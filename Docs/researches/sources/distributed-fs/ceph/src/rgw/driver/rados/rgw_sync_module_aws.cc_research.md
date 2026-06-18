# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc` implements the RGW cloud sync module that exports multisite data changes to an S3-compatible AWS target. It parses sync-module JSON configuration, chooses per-bucket target profiles, translates source RGW object metadata/ACLs into S3 headers, creates destination buckets as needed, streams normal objects, handles resumable multipart uploads, and issues delete requests for removed objects.

## Important APIs, Types, and Functions

The central configuration types are `ACLMapping`, `ACLMappings`, `AWSSyncConfig_Connection`, `AWSSyncConfig_S3`, `AWSSyncConfig_Profile`, and `AWSSyncConfig`. `AWSSyncConfig::init()` parses the default profile, named connections, ACL profiles, S3 multipart tuning, root target, and explicit bucket/prefix profiles. `find_profile()`, `get_path()`, and `get_target()` map RGW source buckets and keys into destination bucket/object names.

The streaming path uses `RGWRESTStreamGetCRF` to fetch source objects from the source zone, `RGWAWSStreamPutCRF` to PUT to the destination S3 service, and `RGWStreamSpliceCR` to copy data between them. `RGWAWSStreamObjToCloudPlainCR` handles small objects. Large objects are coordinated by `RGWAWSStreamObjToCloudMultipartCR`, with helper coroutines for initiate, part upload, complete, and abort. `RGWAWSHandleRemoteObjCBCR` is the object stat callback that chooses plain versus multipart sync. `RGWAWSDataSyncModule` exposes the sync-module interface, and `RGWAWSSyncModule::create_instance()` builds the module instance.

## Control Flow

Initialization parses config, expands target-path variables such as `${sid}`, `${zonegroup}`, `${zone}`, `${bucket}`, and `${owner}`, then builds `S3RESTConn` objects for the root and explicit profiles. During data sync, `sync_object()` allocates `RGWAWSHandleRemoteObjCR`, which stats the remote object through `RGWCallStatRemoteObjCR`, decodes source zone/pg version attributes, picks a target profile, derives the destination path, creates the destination bucket if this coroutine has not seen it before, and starts either the plain or multipart upload flow.

The plain path creates a source GET stream and destination PUT stream and splices them. The multipart path first tries to read persisted multipart state, aborts stale state if source size/mtime/etag changed, initiates a new upload if needed, uploads each ranged part while recording ETags, writes progress after each part, completes the multipart upload, and removes the status object. `remove_object()` maps the source key to the destination path and issues a REST DELETE. Delete marker creation is logged as not implemented.

## State and Persistence Behavior

Configuration state is held in `AWSSyncInstanceEnv` and profile objects for the lifetime of the sync module instance. Multipart progress persists in a RADOS status object under the zone log pool using `RGWBucketPipeSyncStatusManager::obj_status_oid()`, encoded as `rgw_sync_aws_multipart_upload_info`. The status includes upload id, source mtime/etag/zone/pg/versioned epoch, part size, current part/offset, and uploaded part ETags. Destination buckets and objects are external S3 state. The file also injects source metadata into destination user metadata headers such as source mtime, source etag, source key, source version id, and versioned epoch.

## Dependencies and Integration Points

This module sits on RGW multisite data sync (`RGWDataSyncModule`, `RGWDataSyncCtx`, `rgw_bucket_sync_pipe`), RGW coroutine infrastructure, REST connection/coroutine helpers, source-zone connections from `svc_zone`, RGW ACL structures, and RADOS coroutine helpers for the multipart status object. It integrates with S3 signing via `S3RESTConn`, destination host style/region config, and RGW object attributes such as `RGW_ATTR_ACL`, `RGW_ATTR_PG_VER`, and `RGW_ATTR_SOURCE_ZONE`.

## Risks and Edge Cases

Multipart recovery depends on correctly detecting stale state; mismatched source metadata can leave an abandoned upload that is only best-effort aborted. ACL mapping silently ignores grants without configured mappings. Bucket creation treats `BucketAlreadyOwnedByYou` as success but relies on parsing an S3 XML error body. `bucket_created` is per callback object, so repeated create attempts may occur across objects or workers. Target path splitting assumes a slash exists after expansion. Delete marker sync is unimplemented, which is important for versioned bucket semantics. Errors while removing multipart status are ignored after successful complete, so stale status may trigger unnecessary future cleanup.

## Test Signals

High-value tests include config parsing with default, inline, referenced, duplicate, and missing profiles; target-path expansion for tenants and owners; ACL mapping coverage for id/email/uri grants; plain object sync preserving metadata; multipart sync across interruption and resume; stale multipart state abort when source changes; destination bucket already exists/owned behavior; delete object mapping; and negative REST/XML/JSON decode paths.
