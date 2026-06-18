# sources/distributed-fs/lustre-release/lustre/ptlrpc/lproc_ptlrpc.c

## Purpose
`lproc_ptlrpc.c` provides PTLRPC observability and tunables through debugfs/sysfs/lprocfs-style interfaces. It maps opcodes to names, registers service and OBD statistics, exposes request-buffer/thread/NRS controls, prints request history and timeouts, implements ping/import recovery controls, and publishes PTLRPC PM-QoS tunables.

## Important APIs, types, and functions
Opcode translation is handled by `ll_opcode2str()`, `ll_str2opcode()`, and `ll_eopcode2str()` over `ll_rpc_opcode_table` and `ll_eopcode_table`. Registration helpers include `ptlrpc_ldebugfs_register()`, `ptlrpc_sysfs_register_service()`, `ptlrpc_sysfs_unregister_service()`, `ptlrpc_ldebugfs_register_service()`, `ptlrpc_lprocfs_register_obd()`, `ptlrpc_lprocfs_unregister_service()`, `ptlrpc_lprocfs_unregister_obd()`, `ptlrpc_lproc_init()`, and `ptlrpc_lproc_fini()`.

Service tunable handlers expose `req_buffer_history_len`, `req_buffer_history_max`, `req_buffers_max`, `threads_min`, `threads_started`, `threads_max`, and `high_priority_ratio`. NRS visibility and control use `ptlrpc_lprocfs_nrs_policies_seq_show()` and `ptlrpc_lprocfs_nrs_policies_seq_write()`. Request history uses `struct ptlrpc_srh_iterator`, sequence/position conversion macros, and seq-file callbacks. Runtime actions include `ping_show()`, legacy `ping_store()`, `ldebugfs_import_seq_write()`, `pinger_recov_show()`, and `pinger_recov_store()`. PM-QoS module attributes mirror global variables defined in `niobuf.c`.

## Control flow
Stats registration allocates a counter array sized for extra counters plus Lustre opcodes, initializes global request counters, initializes extra counters for enqueue subtypes and BRW byte totals, then initializes one latency counter per opcode name. Service debugfs registration creates per-service directories with `timeouts`, `nrs_policies`, and `req_history`; sysfs registration attaches a kobject with tunable attributes.

Write-side tunables parse user input, validate ranges, and update service fields under `srv_lock` or import locks. History size is capped by either half of max request buffers or a total-RAM-derived bound. Thread minimum/maximum values are normalized per CPT and constrained against `PTLRPC_NTHRS_INIT`, current limits, and current init counts.

NRS policy show serializes against core registration with `nrs_core.nrs_mutex`, aggregates policy state from all service partitions under `nrs_lock`, verifies policy name/argument/fallback consistency across partitions, sums queued/active counters, and emits YAML-like regular and high-priority sections. NRS writes parse a bounded command buffer, optional `reg`/`hp` queue token, and arguments, then call `ptlrpc_nrs_policy_control()` under the same mutex.

Request history uses a 64-bit seq-file position that rotates CPT bits into the high bits so seq-file incrementing does not corrupt the CPT portion of Lustre history sequence numbers. Start/next iterate service partitions, lock each partition mutex and spinlock, seek the next request by history sequence, and show prints stable fields that were set before handler parsing, then calls the service-specific request printer if present.

Ping obtains the import under `with_imp_locked()`, prepares a ping request, forces full import send state, waits, and drops the request. Import writes accept `connection=<nid>@...::instance`, compare optional instance numbers to avoid obsolete-target reconnects, and call `ptlrpc_recover_import()` when needed. Module init creates `/sys/.../ptlrpc` attributes for PM-QoS controls; fini removes them.

## State and persistence behavior
The file does not persist configuration across reboots. It mutates live in-memory service configuration (`srv_hist_nrqbds_cpt_max`, `srv_nrqbds_max`, `srv_nthrs_cpt_init`, `srv_nthrs_cpt_limit`, `srv_hpreq_ratio`), import flags (`IMPF_NO_PINGER_RECOVER`), recovery targets, and PM-QoS globals. It maintains registered debugfs/sysfs dentries, kobjects, statistics objects, and counters that are cleaned up by unregister/fini paths.

## Dependencies and integration points
It depends on Lustre lprocfs/debugfs helpers, PTLRPC service and import internals, NRS scheduler internals, OBD stats, kobject/sysfs APIs, seq-file APIs, and opcode definitions from Lustre protocol headers. `niobuf.c` reads OBD service stats for PM-QoS duration decisions and exports PM-QoS globals that this file tunes. `llog_*` opcodes from this subset are mapped in the opcode table for stats and history output.

## Risks and edge cases
Several reads intentionally race with live request processing and therefore only print fields considered initialized before parsing. The static `unknown_opcode` buffer in `ll_opcode2str()` is shared and not reentrant. Write handlers must keep range checks strict; bad history or thread limits can cause memory pressure or starve services. NRS policy aggregation assumes all service partitions have the same policy set and can return `-EINVAL` if registration changes are inconsistent despite mutex serialization. Request-history iteration depends on `sizeof(loff_t) == sizeof(__u64)` and on CPT-bit encoding remaining stable. Import write parsing is strict and user-facing; malformed connection strings return `-EINVAL`.

## Test signals
Useful tests include opcode/name round trips and unknown opcode formatting, service sysfs registration/unregistration lifetime, each tunable's range checks, NRS show/write with regular-only and high-priority services, concurrent policy registration while reading, request-history reads across multiple CPTs and culled entries, ping success/failure, import reconnect parsing with matching and obsolete instances, pinger recovery toggling, stats increments for normal RPCs and BRW byte counters, and PM-QoS attribute updates being reflected in `niobuf.c` behavior.
