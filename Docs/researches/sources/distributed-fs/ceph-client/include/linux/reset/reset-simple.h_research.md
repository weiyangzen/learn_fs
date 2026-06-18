# sources/distributed-fs/ceph-client/include/linux/reset/reset-simple.h

Purpose: this header defines shared data for simple memory-mapped reset controllers using bit operations over reset registers.

Important APIs/types/functions: `struct reset_simple_data` contains a spinlock, MMIO base, embedded `reset_controller_dev`, polarity flags `active_low` and `status_active_low`, and `reset_us` minimum assert-to-deassert delay. It declares `extern const struct reset_control_ops reset_simple_ops`.

Control flow: simple reset-controller drivers embed/populate `reset_simple_data`, register `rcdev`, and use `reset_simple_ops` for assert, deassert, status, and pulse reset behavior. The spinlock protects read-modify-write register updates.

State and persistence: driver state persists in the data structure. Hardware state is represented by bits in reset controller registers. `reset_us` controls whether the generic reset pulse operation is supported and how long it waits.

Dependencies and integration points: includes MMIO, reset-controller provider API, and spinlocks. It is shared by reset controller drivers with simple active-high or active-low bit layouts.

Risks: polarity flags must match hardware electrical/logical semantics; the comment notes they describe register assertion behavior, not physical voltage level. `reset_us == 0` means reset pulse is unsupported. Test signals include assert/deassert/status readback, active-low/status-active-low variants, reset pulse delay tests, and concurrent reset line updates under lockdep.
