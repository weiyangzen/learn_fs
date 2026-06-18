# sources/distributed-fs/ceph-client/drivers/char/hw_random/st-rng.c

Purpose: STMicroelectronics platform RNG driver for a FIFO-based 16-bit sample generator.

Important APIs, types, and functions: `struct st_rng_data`, `st_rng_read()`, `st_rng_probe()`, OF match `st,rng`, and platform driver registration.

Control flow: probe maps MMIO, enables clock, initializes per-device hwrng ops, and registers. Read polls the status register until FIFO full or a calibrated timeout, then reads up to four 16-bit samples from the data register into the caller buffer and returns the byte count.

State and persistence: per-device state stores base and hwrng ops. Hardware FIFO readiness is transient; no persistent state.

Dependencies and integration: platform/OF, clock framework, MMIO, delays, and hwrng core.

Risks and test signals: read does not distinguish error status bits from FIFO readiness and ignores `wait`; pointer arithmetic on `void *` follows kernel extension expectations. Tests should cover timeout returning 0, partial reads for small `max`, clock/map failures, and FIFO-full read count.
