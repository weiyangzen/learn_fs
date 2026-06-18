# sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.h

Purpose: declares RGW bucket logging configuration, enums, record buffers, constants, and operational helpers for S3 server access logging.

Important APIs/types/functions: enums `KeyFormat`, `LoggingType`, `PartitionDateSource`; struct `configuration`; `service_principal`; `source_buckets`; `MAX_BUCKET_LOGGING_BUFFER`; `bucket_logging_records`; template `to_string(records)`; and declarations for logging, rollover, source bookkeeping, cleanup, verification, and target loading helpers.

Control flow: `configuration::encode()` serializes target bucket, key format, prefix, roll time, logging type, batch size, date source, and only encodes `key_filter` for journal logging. Decode mirrors this conditional layout.

State/persistence: `configuration` is the buffer-encoded bucket logging attr. `source_buckets` is the encoded set on target buckets. Record buffers are in-memory batching primitives.

Dependencies/integration: SAL forward declarations, bucket types, buffer encoding, async yield, S3 key filters, and ARN. Used by REST bucket logging handlers and operation completion logging.

Risks: conditional encoding of `key_filter` depends on `logging_type` being decoded correctly. `records_batch_size` is documented for batching, while actual write behavior is in SAL/logging implementation. `LoggingType::Any` is a selector, not valid user config.

Test signals: configuration encode/decode for Standard and Journal, XML/JSON output, source-bucket set encoding, `Any` selector behavior, partitioned/simple key-format serialization, and batch limit boundaries.
