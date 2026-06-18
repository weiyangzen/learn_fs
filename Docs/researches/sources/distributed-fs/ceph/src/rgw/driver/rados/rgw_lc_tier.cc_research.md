# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.cc

## Purpose
Implements RGW lifecycle cloud-tier object transition and restore for the RADOS-backed gateway. It copies local RGW objects to an S3-compatible remote endpoint, handles target bucket creation, selects plain versus multipart transfer, records resumable multipart upload state, checks whether a remote copy already represents the current source version, and restores Glacier-style remote objects back through GET after issuing a restore request.

## Important APIs, Types, And Functions
The public entry points are `rgw_cloud_tier_transfer_object()`, `rgw_cloud_tier_get_object()`, `rgw_cloud_tier_restore_object()`, `cloud_tier_restore()`, and `is_restore_in_progress()`. Internal serialized state is `rgw_lc_multipart_upload_info`, which persists `upload_id`, source size, source mtime, and source etag. `rgw_lc_obj_properties` carries source mtime, etag, versioned epoch, ACL mappings, and target storage class into outbound headers.

`RGWLCStreamRead` wraps a SAL object read operation, validates the source mtime to avoid racing with object mutation, builds an `rgw_rest_obj` from local attributes/ACL, and streams either the whole object or a multipart byte range. `RGWLCCloudStreamPut` wraps `RGWRESTStreamS3PutObj`, maps source attributes and ACL grants into S3 headers, tracks returned ETag, and completes the remote request. Helper functions build target names, map RGW attrs to HTTP headers, issue multipart init/part/complete/abort calls, and issue remote RESTORE requests.

## Control Flow
`rgw_cloud_tier_transfer_object()` first checks a caller-provided cache of known target buckets. On miss it sends `HEAD` to the target bucket and creates it with optional location constraint if absent. It then sends a best-effort `HEAD` for the target object and treats a matching `x-amz-meta-rgwx-source-mtime` as already tiered. If the object is not already tiered, the source size is compared with `multipart_sync_threshold`, clamped to at least the S3 minimum multipart part size, to choose plain or multipart transfer.

Plain transfer constructs `RGWLCStreamRead` and `RGWLCCloudStreamPut`, initializes the source read, initializes/sends the destination PUT, streams object bytes from `read_op->iterate()` into the destination callback, and completes the request. Multipart transfer first checks a status object named `lc_multipart_<source_oid>` in the zone log pool. If the status exists but source mtime/size/etag changed, it aborts the remote upload and deletes the status. Otherwise it starts or resumes an upload, computes a part size that respects `MULTIPART_MAX_PARTS` and configured minimums, streams every part, collects returned ETags, completes the multipart upload, and best-effort deletes the status object.

Restore flow sends a remote `POST ?restore` XML request unless the caller already marks restore as in progress, polls `HEAD` up to two times looking for `ongoing-request="true"` in `x-amz-restore`, and only performs the actual GET when the remote reports completion.

## State And Persistence
Remote state is the target bucket/object plus S3 metadata headers: `x-amz-meta-rgwx-source`, `x-rgw-cloud`, `x-rgw-cloud-keep-attrs`, source mtime, source etag, source key/version, versioned epoch, storage class, and mapped ACL grants. Local resumability state for multipart transition is a system object in the zone log pool. The code does not persist per-part completion state, so a crash after uploaded parts but before completion will resume from the upload id but resend all parts. `cloud_targets` is only an in-memory bucket-existence cache passed by the lifecycle caller.

## Dependencies And Integration Points
The file integrates with RGW SAL object reads, `RGWRESTConn` and S3 streaming request classes, RGW attr names from `rgw_common.h`, XML formatting/decoding, zone parameters for the log pool, lifecycle bucket directory entries, and tier configuration types from `rgw_zone.h`. It assumes a RADOS-backed driver when reading/writing multipart status objects through `RGWSI_SysObj`; non-RADOS drivers are rejected for cloud transition state.

## Risks And Edge Cases
Race handling depends on matching source `mtime` during `ReadOp::prepare()`, but multipart only stores source mtime/size/etag at upload start and does not record individual parts. XML error parsing treats `RestoreAlreadyInProgress`, `BucketAlreadyOwnedByYou`, and `BucketAlreadyExists` as acceptable special cases but otherwise returns `-EIO`, so endpoint-specific XML differences are compatibility risks. Header name normalization is mixed between uppercase and lowercase forms; restore/already-tiered checks compensate for common variants but may miss unusual endpoint casing. Plain transfer uses shared pointers due to a noted stack-lifetime/performance issue, which is a signal that callback ownership is subtle. Best-effort abort/status deletion can leave remote uploads or status objects behind on failure.

## Test Signals
Useful tests include lifecycle transition of small objects, multipart threshold boundary cases, object mutation during transfer returning `-ECANCELED`, interrupted multipart uploads with status-object reuse, remote bucket already exists/absent paths, restore in-progress and restore-complete HEAD responses, ACL mapping output, ETag unquoting on get/restore, and endpoints returning transient `-EIO` during remote GET.
