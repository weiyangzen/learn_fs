## sources/distributed-fs/ceph/src/rgw/rgw_log.h

Purpose: declares the serialized operation log model and the sink abstraction used by RGW request logging.

Important APIs/types: `delete_multi_obj_entry` and `delete_multi_obj_op_meta` capture per-object outcomes for S3 multi-object delete logs. `rgw_log_entry` is the central encoded log record, including owners, bucket/object identifiers, request/response fields, byte counts, elapsed time, headers, auth identity, STS claims, access key, temp URL, account/role ids, and optional Keystone scope. `OpsLogSink` is the sink interface; `OpsLogManifold` fans out to multiple sinks; `JsonOpsLogSink` formats entries; `OpsLogFile`, `OpsLogSocket`, and `OpsLogRados` provide concrete transports.

Control flow: implementations fill `rgw_log_entry`, then call `OpsLogSink::log()`. JSON sinks share formatter handling and delegate the resulting `bufferlist` to `log_json()`. The manifold returns failure when any child sink fails.

State and persistence: `rgw_log_entry::encode()` currently writes version 16 with legacy compatibility down to version 5. Decode has explicit branches for historical bucket id formats, old owner encoding, optional x-headers, token claims, identity fields, multi-delete metadata, account/role ids, and Keystone scope.

Dependencies/integration: includes common RGW request structures, `OutputDataSocket`, versioned owner conversion, SAL forward declarations, and Keystone scope. It is used by request execution, Lua `Request.Log()`, RADOS log storage, and admin/dump tooling.

Risks and test signals: backward-compatible decode branches are high risk because old logs may still be readable after upgrades. `WRITE_CLASS_ENCODER` and `generate_test_instances()` make this file a target for Ceph encoding tests. New fields must bump encode versions and add decode guards without breaking old clusters.
