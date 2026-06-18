# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h` declares the public AWS cloud sync module and the small encoded state records used by the implementation to track source object identity and multipart upload progress.

## Important APIs, Types, and Functions

`rgw_sync_aws_multipart_part_info` records a multipart part number, source offset, part size, and destination ETag. `rgw_sync_aws_src_obj_properties` captures source mtime, ETag, source zone short id, pg version, and versioned epoch. `rgw_sync_aws_multipart_upload_info` records the upload id, source object size/properties, chosen part size/count, current part/offset, and a map of completed part records. All three define Ceph encoders. `RGWAWSSyncModule` derives from `RGWSyncModule`, reports no data export support, and exposes `create_instance()`.

## Control Flow

The header has no runtime flow. The sync module registry instantiates `RGWAWSSyncModule`, calls `create_instance()`, and the implementation returns an `RGWSyncModuleInstance` with a data handler. The encoded multipart structs are read and written by AWS multipart sync coroutines.

## State and Persistence Behavior

The structs are persisted through Ceph `bufferlist` encoding in the zone log pool for resumable multipart sync. Versioned encoders currently start at version 1, so future format changes must preserve backward decode behavior. The module class itself owns no state in the header.

## Dependencies and Integration Points

The header depends on `rgw_sync_module.h`, Ceph `bufferlist` encoding macros, and the RGW sync module interface. The implementation uses these declarations with RADOS status objects and S3 REST sync coroutines.

## Risks and Edge Cases

The persistence layout is part of the on-disk recovery contract for in-flight multipart uploads. Field changes, default value changes, or non-compatible encoder updates can break resume/abort behavior after upgrade.

## Test Signals

Test signals include encode/decode round trips for empty and populated multipart records, compatibility tests for persisted status objects across versions, and module registration tests that instantiate the AWS sync module from JSON config.
