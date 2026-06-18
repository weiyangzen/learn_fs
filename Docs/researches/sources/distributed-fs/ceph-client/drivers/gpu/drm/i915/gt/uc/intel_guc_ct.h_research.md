## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.h

Purpose: defines the public Command Transport structures, flags, and entry points used by GuC subsystems to initialize CT, send actions, receive events, and print transport state.

Important APIs, types, and functions:
- `struct intel_guc_ct_buffer` models one CT buffer descriptor and circular command area, including lock, descriptor pointer, command pointer, dword size, reserved space, local head/tail/space shadows, and broken flag.
- `struct intel_guc_ct` owns the GuC VMA blob, enabled flag, send/receive buffers, receive tasklet, waitqueue, pending/incoming request lists, worker, stall time, and optional debug tracking.
- `INTEL_GUC_CT_SEND_NB` marks fast/nonblocking sends; `INTEL_GUC_CT_SEND_G2H_DW_MASK` encodes expected G2H payload length; `MAKE_SEND_FLAGS(len)` builds checked nonblocking flags.
- Public APIs include `intel_guc_ct_init_early()`, `intel_guc_ct_init()`, `intel_guc_ct_enable()`, `intel_guc_ct_disable()`, `intel_guc_ct_fini()`, `intel_guc_ct_send()`, `intel_guc_ct_event_handler()`, `intel_guc_ct_print_info()`, and `intel_guc_ct_max_queue_time_jiffies()`.

Control flow:
- Subsystems call init early before hardware access, full init after GuC allocation support is available, enable when GuC is ready, send actions while enabled, handle GuC interrupts through `intel_guc_ct_event_handler()`, then disable/fini during teardown/reset.

State and persistence:
- CT buffer state persists inside `struct intel_guc`. The header exposes enough state for inline enabled/sanitize checks but keeps message parsing and request internals in the C file.

Dependencies and integration points:
- Includes Linux interrupt/spinlock/stackdepot/workqueue/time/wait headers and `intel_guc_fwif.h` for CT descriptor ABI.
- Used by GuC action send wrappers and debugfs status paths.

Risks:
- Direct field access by external code should remain limited; misusing `enabled`, local head/tail, or send flags can break CT invariants.
- `MAKE_SEND_FLAGS()` relies on callers supplying payload dwords without the HXG header length; mismatches affect G2H credit accounting.

Test signals:
- Compile coverage with debug and non-debug configurations.
- Send-flag users should be audited or tested for correct expected G2H length.
