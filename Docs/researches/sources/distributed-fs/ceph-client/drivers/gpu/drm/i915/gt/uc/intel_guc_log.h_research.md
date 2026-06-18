## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.h

Purpose: defines the GuC log state structure, log-level conversion macros, section identifiers, and public log/relay/dump APIs.

Important APIs, types, and functions:
- Log level macros map i915 levels to GuC enable/default/verbosity semantics: disabled, non-verbose, verbose, `GUC_LOG_LEVEL_TO_VERBOSITY()`, and `GUC_LOG_LEVEL_MAX`.
- Section enum indexes crash, debug, and capture sections.
- `struct intel_guc_log` stores level, `guc_lock`, per-section size/unit/count/flag data, VMA/map, relay state, and stats.
- Public APIs cover early init, overflow detection, buffer size/offset queries, create/destroy, set/get level, relay create/open/start/flush/close state, flush event handling, info printing, raw dump, and capture section size.

Control flow:
- GuC setup initializes the struct early, creates the backing buffer before firmware configuration, handles firmware flush notifications during runtime, and destroys the VMA during teardown.
- Debugfs routes user operations through set-level, relay, info, and dump APIs.

State and persistence:
- The header documents persistent host-side log state. Shared firmware log state is represented by `guc_log_buffer_state` from `intel_guc_fwif.h`.

Dependencies and integration points:
- Includes Linux mutex/relay/workqueue APIs, `intel_guc_fwif.h` for log buffer types, and GEM declarations.
- Used by GuC logging implementation, capture code, debugfs, and CT event handling.

Risks:
- Exposed state must remain consistent with locking rules: `guc_lock` for `level`, `relay.lock` for relay channel/object ref state.
- Log-level macros must align with GuC firmware control semantics where default logging is separate from enable.

Test signals:
- Build coverage for callers.
- Runtime debugfs tests for log level, relay, dump, and flush notifications.
