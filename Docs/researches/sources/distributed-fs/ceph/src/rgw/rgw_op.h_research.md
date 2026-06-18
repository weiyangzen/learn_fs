# sources/distributed-fs/ceph/src/rgw/rgw_op.h

## Purpose
`rgw_op.h` is the central abstract operation surface for RADOS Gateway requests. It declares `RGWOp`, `RGWHandler`, data filters, metadata helpers, and most concrete operation base classes used by S3, Swift, admin, lifecycle, multipart, tagging, replication, object-lock, bucket policy, public-access, and metadata-search frontends. The file does not implement most behavior; instead it defines the contracts implemented by protocol-specific REST classes and the common execution path in `rgw_process.cc`.

## Important APIs, Types, And Functions
`RGWHandler` owns dialect-specific request initialization, permission setup, retargeting, authorization, and post-auth initialization. `RGWOp` owns request state, driver access, quota initialization, CORS state, return status, request verification hooks, execution hooks, response hooks, op masks, dmclock classification, and operation naming. Derived classes map API verbs/resources to common RGW behavior, including `RGWGetObj`, `RGWPutObj`, `RGWPostObj`, `RGWCopyObj`, multipart operations, bucket metadata operations, ACL/CORS/lifecycle operations, object-lock operations, and bucket public-access block operations.

Helper APIs include `rgw_rest_read_all_input()`, `rgw_rest_get_json_input()`, `retry_raced_bucket_write()`, `get_system_versioning_params()`, `rgw_get_request_metadata()`, `encode_delete_at_attr()`, `encode_obj_tags_attr()`, `encode_dlo_manifest_attr()`, `complete_etag()`, `parse_value_and_bound()`, `rgw_policy_from_attrset()`, and the generic `get_decrypt_filter()`.

## Control Flow
The intended flow is: handler creates an op, `process_request()` authenticates requester, `rgw_process_authenticated()` initializes permissions, optionally retargets, reads ACL/policy state, runs `init_processing()`, checks op masks and permissions, calls `verify_params()`, `pre_exec()`, `execute()`, then `complete()`/`send_response()`. `RGWOp::read_all_input()` and `get_json_input()` complete AWS v4 authentication after reading the body. `RGWGetObj_Filter` chains data transformations; `DataProcessorFilter` bridges get-object streaming into a SAL data processor.

## State And Persistence
Most persistent state is indirect through SAL objects and encoded attrs. The header defines attr serialization helpers for HTTP metadata, delete-at timestamps, object tags, DLO manifests, SLO entries, and SLO manifests. Operation objects keep transient request state such as ranges, encryption/decryption filters, multipart ids, ACLs, CORS configs, object-lock state, checksum state, and response tracking. `retry_raced_bucket_write()` exists because bucket info writes can fail with `-ECANCELED` if bucket metadata changed concurrently.

## Dependencies And Integration Points
This file ties together `req_state`, SAL driver/user/bucket/object abstractions, ACL, CORS, quota, lifecycle, tags, object-lock, bucket encryption, compression, logging, tracing, dmclock scheduling, and RGW-specific attributes. `rgw_process.cc` consumes the virtual hooks. Protocol frontends subclass these base operations to parse parameters and send protocol-specific responses.

## Risks And Test Signals
Risk concentrates in virtual-contract drift, missing `op_mask()` coverage, body-read/AWS4 ordering, attr size/name enforcement, metadata header blocklists, storage-class parsing, and races around bucket attr updates. Useful tests exercise each operation through REST protocol tests, multipart/copy/range/encryption paths, object-lock and public-access block cases, invalid metadata bounds, stale bucket-info retries, and dmclock client classification for data versus metadata operations.
