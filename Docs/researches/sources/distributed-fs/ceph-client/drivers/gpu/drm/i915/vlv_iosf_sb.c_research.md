# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.c

Purpose: implements Valleyview/Cherryview IOSF sideband register access for BUNIT, CCK, CCU, DPIO, FLISDSI, NC, and PUNIT units.

Important APIs/functions: `vlv_iosf_sb_get()`/`vlv_iosf_sb_put()` acquire/release unit access and maintain `locked_unit_mask`. `vlv_iosf_sb_read()` and `vlv_iosf_sb_write()` translate unit to devfn/port/opcode and call `vlv_sideband_rw()`. `vlv_iosf_sb_init()` initializes the mutex and Valleyview CPU latency QoS request; `vlv_iosf_sb_fini()` removes them. Internal `__vlv_punit_get()` acquires the global IOSF MBI PUNIT lock and applies a CPU latency workaround for Valleyview.

Control flow and state: all sideband reads/writes require the caller to hold the appropriate unit via `get()`. `vlv_sideband_rw()` waits for the doorbell to become idle, disables preemption, writes address/data/doorbell fields, waits for completion, then reads data for reads. PUNIT access has extra locking and QoS state.

Dependencies and integration: depends on i915 uncore register access, `i915_iosf_mbi`, CPU latency QoS, DRM warnings, and platform predicates. Used by VLV/CHV display, power, and clock code that must access sideband registers.

Risks: invalid unit mapping returns zero or `-EINVAL`; callers that ignore `write()` return values can miss sideband timeouts. The lock mask warning in `put()` expects balanced unit masks. PUNIT access can hang hardware without the CPU latency workaround.

Test signals: platform tests should show no doorbell timeouts, no unbalanced lock-mask warnings, and correct sideband register effects on VLV/CHV hardware.
