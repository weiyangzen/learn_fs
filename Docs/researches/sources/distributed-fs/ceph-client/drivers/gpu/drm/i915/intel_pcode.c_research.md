# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.c

Purpose: implements i915 PCODE mailbox access for power/firmware commands and exposes a display-facing pcode interface.

Important APIs/functions: exports `snb_pcode_read`, `snb_pcode_write_timeout`, `skl_pcode_request`, `intel_pcode_init`, `snb_pcode_read_p`, `snb_pcode_write_p`, and `i915_display_pcode_interface`. Internal helpers decode gen6/gen7 mailbox status, perform locked mailbox read/write, retry SKL-style requests, and wait for dGPU pcode initialization.

Control flow: mailbox operations serialize on `i915->sb_lock`, check readiness, write data/data1 and mailbox command, wait for ready to clear, optionally read results, and translate status bits. `skl_pcode_request()` sends a request until the reply matches or timeout occurs, first sleep-polling then retrying with preemption disabled. dGPU init waits up to 10 seconds, then extends to 180 seconds with a notice.

State and persistence: no long-lived software state besides lock serialization. Hardware state is in PCODE mailbox/data registers and firmware initialization status.

Dependencies and integration: depends on uncore forcewake-aware register helpers, pcode register definitions, wait macros, runtime PM wrappers for parameterized commands, and display parent interface callbacks.

Risks: mailbox access is timeout-sensitive and firmware-dependent. Busy/locked/rejected statuses must be interpreted correctly. Atomic retry can stall CPUs briefly, so timeout limits are guarded. Missing runtime PM around parameterized commands can access powered-down hardware.

Test signals: pcode read/write users, display pcode interface consumers, dGPU initialization logs, timeout/retry debug messages, and error-code propagation in power/frequency tests.
