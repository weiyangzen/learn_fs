# sources/distributed-fs/ceph-client/drivers/reset/reset-simple.c

Purpose: generic MMIO bit-per-reset controller used by many simple SoC blocks and exported for early/simple platform-specific drivers.

Important APIs/types/functions: `reset_simple_update()` computes 32-bit bank/bit and writes assert/deassert with `active_low`; `reset_simple_reset()` pulses using optional `reset_us`; `reset_simple_status()` interprets readback using `status_active_low`; exported `reset_simple_ops` is shared. `reset_simple_devdata` supplies register offset, fixed reset count, and polarity for OF compatibles.

Control flow: probe maps one MMIO resource, initializes `reset_simple_data`, applies match data such as SoCFPGA offset or active-low variants, offsets the membase, and registers the controller. Consumers invoke standard reset ops.

State and persistence: software holds membase, spinlock, polarity flags, and pulse width. Hardware register bits persist until changed.

Dependencies and integration: integrates platform device probing, OF match table, `linux/reset/reset-simple.h`, spinlocks, and the reset-controller framework.

Risks and test signals: no local ID guard in ops; reset core must enforce `nr_resets`. `reset_us == 0` makes `.reset` unsupported. Test each compatible’s polarity/offset, concurrent RMW locking, resource-size-derived reset count, and pulse timing.
