# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.h

Purpose: defines the timer synchronization context and lifecycle functions.

Important types and API: `struct adf_timer` stores `accel_dev`, delayed work, and initial timestamp. Declares `adf_timer_start` and `adf_timer_stop`.

Control flow and state: header only. Runtime state is owned per device at `accel_dev->timer`.

Dependencies and integration: includes ktime and workqueue types. Used by platform hardware hooks and heartbeat logic.

Risks and test signals: callers must only stop timers that were successfully started. Test exported symbol availability, repeated start/stop, and null-safe stop behavior.
