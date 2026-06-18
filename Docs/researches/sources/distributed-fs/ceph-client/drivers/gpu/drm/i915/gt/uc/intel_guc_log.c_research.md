## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.c

Purpose: manages the shared GuC log buffer, log-size programming values, log verbosity control, relayfs streaming to debugfs, flush handling, overflow accounting, and raw log dumping.

Important APIs, types, and functions:
- `_guc_log_init_sizes()` calculates crash/debug/capture section sizes, API unit flags/counts, field clipping, and crash/debug unit consistency based on build config defaults.
- `intel_guc_log_section_size_capture()`, `intel_guc_get_log_buffer_size()`, and `intel_guc_get_log_buffer_offset()` expose section sizing/offsets.
- `intel_guc_log_create()` allocates the combined log VMA, pins a WC map for critical reads, and initializes log level from `i915->params.guc_log_level`.
- `intel_guc_log_destroy()` releases the map/VMA.
- `intel_guc_log_set_level()` sends GuC log-control action under `guc_lock`.
- Relay support includes `guc_log_relay_create()`, `intel_guc_log_relay_open()`, `intel_guc_log_relay_start()`, `intel_guc_log_relay_flush()`, `intel_guc_log_relay_close()`, and `intel_guc_log_handle_flush_event()`.
- `_guc_log_copy_debuglogs_for_relay()` snapshots debug/crash log state, handles overflows and wraparound, copies data from WC log memory into relay subbuffers, advances read pointers, and acknowledges flush completion.
- `intel_guc_log_info()` reports relay/log stats. `intel_guc_log_dump()` prints raw log object or saved load-error log.

Control flow:
- Create computes the layout: one page of `guc_log_buffer_state` headers followed by debug, crash, and capture sections. It allocates a GuC VMA and pins WC mapping for direct reads during error paths.
- Log level changes use runtime PM, send `INTEL_GUC_ACTION_UK_LOG_ENABLE_LOGGING`, and update cached level only on success.
- Relay open creates a single global relay file under GuC debugfs, maps the log object for relay bookkeeping, and requires fast WC memcpy support.
- Firmware flush notifications queue high-priority work. The worker copies debug/crash sections, not capture, then sends `INTEL_GUC_ACTION_LOG_BUFFER_FILE_FLUSH_COMPLETE`.
- Forced relay flush waits for pending work, sends force-flush action, and copies the updated data.
- Raw dumping pins the selected log object WC, copies page by page, and emits four dwords per line.

State and persistence:
- `intel_guc_log` stores configured level, size units/counts, log VMA, WC map, relay channel/open/started flags, work item, relay full count, and per-buffer overflow/flush stats.
- Shared `guc_log_buffer_state` fields coordinate producer/consumer state with firmware; host updates read pointers and clears flush flags.

Dependencies and integration points:
- Uses debugfs/relayfs, runtime PM, GuC CT/MMIO action wrappers, i915 GEM VMA mapping, WC memcpy, capture sizing, and GuC print helpers.
- Integrated with CT event handling for `INTEL_GUC_ACTION_NOTIFY_FLUSH_LOG_BUFFER_TO_FILE` and with capture parsing via the capture log section.

Risks:
- Relay no-overwrite mode can drop copying when user space is too slow; `full_count` tracks this.
- Incorrect size/unit programming can misconfigure firmware log buffers; code logs alignment, zero, clipping, and unit mismatch errors.
- Log buffer state can be invalid or overflowed; code falls back to whole-buffer copy but may include stale/garbled data.
- WC mapping and relay lifecycle require careful locking and object refs.

Test signals:
- Verify log allocation sizes under normal, DEBUG_GEM, and DEBUG_GUC builds.
- Exercise debugfs log level changes, relay open/start/flush/close, slow consumer behavior, and firmware flush events.
- Validate raw log dump and saved load-error dump.
- Inject overflow and invalid read/write offsets to observe recovery/warnings.
