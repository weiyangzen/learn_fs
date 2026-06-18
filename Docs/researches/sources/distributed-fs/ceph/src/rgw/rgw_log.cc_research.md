## sources/distributed-fs/ceph/src/rgw/rgw_log.cc

Purpose: implements RGW usage logging and operation logging. It turns `req_state` plus optional `RGWOp` data into usage accounting batches, JSON/file/socket records, and encoded RADOS log objects.

Important APIs/functions: `render_log_object_name()` expands time and bucket tokens for RADOS log object names; `rgw_log_usage_init()`/`rgw_log_usage_finalize()` own the global `UsageLogger`; `rgw_format_ops_log_entry()` formats `rgw_log_entry` for JSON output; `rgw_log_op()` is the main request logging entry point. Concrete sink methods implement `OpsLogManifold`, `OpsLogFile`, `JsonOpsLogSink`, `OpsLogSocket`, and `OpsLogRados`.

Control flow: `rgw_log_op()` first calls `log_usage()` when enabled, then exits if ops logging is disabled. It validates bucket existence and UTF-8 bucket names, extracts object identity, request environment fields, URI, auth identity, token claims, optional x-headers, ownership, byte counters, timestamps, status, and transaction id, then sends the completed entry to the configured `OpsLogSink`. File logging is asynchronous: `OpsLogFile::log_json()` appends to an in-memory queue and wakes a thread that calls `flush()`.

State and persistence: `UsageLogger` keeps a mutex-protected `usage_map` keyed by user/bucket and flushes by timer or threshold through `driver->log_usage()`. `OpsLogFile` buffers `bufferlist` entries until flush to an append-only file. `OpsLogRados` encodes `rgw_log_entry` and writes it via `driver->log_op()` to an object name derived from configuration.

Dependencies/integration: depends on request state, SAL driver, REST logging filters, ACL owners, auth identity writers, `ACCOUNTING_IO`, Ceph timers, `OutputDataSocket`, and RADOS SAL. Main RGW setup wires these sinks in `AppMain::init_opslog()`.

Risks and test signals: file sink drops entries when the configured memory buffer is full; file flush retries with exponential sleep and can block its thread. The global `usage_logger` pointer has lifecycle assumptions around RGW startup/shutdown. `rgw_log_entry::generate_test_instances()` and `dump()` provide encoding/dump coverage signals, while integration tests should verify multi-delete `op_data`, requester-pays usage attribution, x-header filtering, and RADOS object-name rendering.
