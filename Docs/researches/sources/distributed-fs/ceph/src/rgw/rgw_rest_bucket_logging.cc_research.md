# sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.cc

## Purpose

Implements S3-compatible bucket logging REST operations for reading, configuring, disabling, and manually flushing bucket access logging.

## Important APIs, Types, and Functions

Utility helpers verify the `?logging` subresource and update the logging mtime attribute. `RGWGetBucketLoggingOp` reads and returns logging configuration. `RGWPutBucketLoggingOp` parses XML configuration, validates target bucket and policy, writes source bucket logging attributes, updates target logging source lists, and rolls over old pending log objects when configuration changes. `RGWPostBucketLoggingOp` flushes pending logging objects. Factory methods on `RGWHandler_REST_BucketLogging_S3` create GET/PUT/POST operations.

## Control Flow and Data Flow

GET validates the request, loads the source bucket, decodes `RGW_ATTR_BUCKET_LOGGING` and optional mtime attr, and returns XML `BucketLoggingStatus`. PUT validates query/body, parses XML into `rgw::bucketlogging::configuration`, loads the target bucket when enabled, checks requester ownership and IAM permission, verifies target bucket policy and attributes, then uses `retry_raced_bucket_write()` to atomically add/update/remove logging attributes on the source bucket. If a previous config changed, it may roll over the old pending logging object and update logging source attributes on old/new target buckets. POST loads source/target config, verifies permission/policy, ensures target source metadata is current, gets the pending logging object name, and calls `rollover_logging_object()`.

## State and Persistence Behavior

Source bucket attrs store `RGW_ATTR_BUCKET_LOGGING` and `RGW_ATTR_BUCKET_LOGGING_MTIME`. Target bucket attrs track logging source buckets via bucketlogging helpers. Pending logging objects are committed/rolled over into the target bucket. Updates are protected with bucket-attribute merge/retry logic to handle racing writers.

## Dependencies and Integration Points

Depends on RGW op/rest/S3 auth, ARN parsing, URL helpers, `rgw_bucket_logging` configuration and rollover helpers, IAM condition checks, SAL bucket loading/attrs, and XML formatter/decoder. Integrated with S3 `GET/PUT/POST Bucket logging`.

## Risks and Edge Cases

The helper requires `logging` to exist with no value and bucket name to be present. PUT permission uses `configuration` and `target_bucket` prepared during init processing, so operation ordering matters. Target bucket must differ from source and share the zonegroup. Failures updating logging source lists are warnings after source config may already be changed. Decode failures of existing config can still overwrite unknown old state. POST response always writes `FlushedLoggingObject`, which may be empty if no pending object existed or rollover behavior changes.

## Test Signals

Cover missing/valued `logging` param, non-bucket requests, GET with no config, corrupt config, mtime absent/corrupt, PUT malformed XML, disabling logging cleanup, target bucket parse/load failures, same-bucket and cross-zonegroup rejection, IAM owner/policy failures, raced attribute writes, old target source removal, rollover failures, POST no pending object, POST successful flush, and factory method selection.
