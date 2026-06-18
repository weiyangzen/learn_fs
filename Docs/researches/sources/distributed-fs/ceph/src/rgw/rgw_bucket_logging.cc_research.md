# sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.cc

Purpose: implements S3 server access logging configuration parsing/output, pending log object naming/rollover, record generation, quota checks, target policy validation, source bookkeeping, and deletion cleanup.

Important APIs/types/functions: `configuration::decode_xml/dump_xml/dump/to_json_str()`, `new_logging_object()`, `commit_logging_object()`, `rollover_logging_object()`, both `log_record()` overloads, `object_name_oid()`, `get_bucket_id()`, `update_bucket_logging_sources()`, `bucket_deletion_cleanup()`, `source_bucket_cleanup()`, `verify_target_bucket_policy()`, `verify_target_bucket_attributes()`, and `get_target_and_conf_from_source()`.

Control flow: XML decode enables config only when `LoggingEnabled` exists, parses target bucket/prefix, Ceph extensions, journal filters, and key format. Logging loads the target bucket, validates policy/attributes, refreshes the source list, gets or creates the pending object name, rolls over by time or full-object error, formats either standard or journal records, checks user/bucket quota, and appends. Cleanup removes source attrs, source list entries, pending-object name objects, and either commits or removes pending log objects depending on whether source or target is deleted.

State/persistence: bucket logging config is stored in `RGW_ATTR_BUCKET_LOGGING`; target source tracking in `RGW_ATTR_BUCKET_LOGGING_SOURCES`; pending object names and pending/committed log objects are manipulated through SAL bucket methods with object version trackers for races.

Dependencies/integration: SAL driver/bucket/object, `req_state`, IAM policy evaluator, ARN, S3 auth helpers, quotas, XML/JSON, filters, Ceph time, and retry-raced bucket writes.

Risks: rollover is race-prone and relies on `-ECANCELED` handling. Cleanup intentionally swallows many post-attr-removal errors to preserve idempotence, which can leak objects. Target policy verification mutates request environment with `aws:SourceArn` and `aws:SourceAccount`. `EventTime` partition format is not fully implemented. Logging target cannot itself have logging, requester pays, or encryption.

Test signals: XML round-trips, standard/journal record formats, journal filters, target policy allow/deny, requester-pays/encryption/logging rejection, quota failures, object rollover by time and `-EFBIG`, source/target bucket deletion cleanup, races on pending object name, and tenant-qualified target bucket parsing.
