# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.h

Purpose: declares PCODE mailbox helpers and the display pcode callback interface exported by i915.

Important APIs/functions: exposes `snb_pcode_read`, `snb_pcode_write_timeout`, convenience macro `snb_pcode_write`, `skl_pcode_request`, `intel_pcode_init`, parameterized dGPU helpers `snb_pcode_read_p/write_p`, and `i915_display_pcode_interface`.

Control flow: callers choose direct mailbox read/write, request-with-ack polling, or command/parameter helpers. The implementation handles locking, wait policy, and runtime PM where needed.

State and persistence: no header state; all state is hardware mailbox registers and implementation-local locks.

Dependencies and integration: includes `linux/types.h`, forward-declares `drm_device` and `intel_uncore`, and bridges display code to i915 pcode operations.

Risks: the one-millisecond `snb_pcode_write` default may be too short for long-running commands; callers needing longer waits must use `snb_pcode_write_timeout`.

Test signals: compile/link coverage from pcode clients, display pcode callbacks, and platform power-management tests.
