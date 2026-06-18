# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.c

## Purpose
Manages the GuC log buffer, captures host snapshots, prints them as ASCII85 debug dumps or binary LFD streams, and tracks GuC log buffer overflow counters.

## Important APIs, Types, And Functions
Exports `xe_guc_log_init`, `xe_guc_log_print`, `xe_guc_log_print_lfd`, `xe_guc_log_print_dmesg`, `xe_guc_log_snapshot_capture`, `xe_guc_log_snapshot_print`, `xe_guc_log_snapshot_free`, and `xe_guc_check_log_buf_overflow`. Internal LFD helpers parse log-init configuration, find buffer markers, emit typed payloads, and stream wrapped event/crash buffers.

## Control Flow
Initialization allocates a managed pinned/mapped system GGTT BO of `GUC_LOG_SIZE`, zeros it, and stores the module log level. Snapshot capture refuses missing BOs, allocates a snapshot object and 2 MiB chunks, copies the mapped BO into those chunks, samples GuC timestamp under forcewake if possible, and records kernel time and firmware version metadata. Printing emits metadata plus an ASCII85 blob. LFD printing loads LIC/config data from the state header, emits required FW and OS payloads, then emits event and crash dump payloads when present. Overflow checking compares a sampled full counter to the previous sample and compensates for 4-bit wrap.

## State And Persistence
Persistent log state is `log->bo`, `log->level`, and per-log-type overflow stats. Snapshots are independent heap allocations that persist until explicitly freed and can be produced from atomic or non-atomic contexts using chunked allocation.

## Dependencies And Integration Points
Depends on GuC log and LFD ABI headers, Xe BO/map/MMIO/forcewake helpers, firmware version state, module parameters, DRM printers, and devcoredump/debugfs users. Debugfs exposes text, LFD, and dmesg dump entry points.

## Risks And Test Signals
Snapshot allocation can fail partially and must free all chunks. LFD parsing trusts marker/header layout in the GuC log buffer; malformed pointers could produce bad output if firmware layout changes. Overflow tracking assumes a 4-bit full counter. Test signals include debugfs log dump readability, LFD decoder acceptance, fault-injected init failures, and overflow notices when GuC reports full-count changes.
