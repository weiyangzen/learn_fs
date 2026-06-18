
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-platform.c

Purpose: this is the platform/OF wrapper for memory-mapped PCA9564/PCA9665 controllers. Like the ISA variant, it supplies register access, wait, interrupt, and reset callbacks to the shared `i2c-algo-pca` engine, but supports platform resources, MMIO register strides, optional GPIO reset, and numbered adapter registration.

Important APIs, types, and functions: `struct i2c_pca_pf_data` contains MMIO base, optional IRQ, reset GPIO, wait queue, adapter, and `i2c_algo_pca_data`. Separate `readbyte`/`writebyte` helpers handle 8-, 16-, and 32-bit memory resource spacing while still performing byte I/O. `i2c_pca_pf_waitforcompletion()` waits on IRQ or polls `I2C_PCA_CON_SI`. `i2c_pca_pf_handler()` filters interrupts by checking SI before waking waiters. Reset is either GPIO pulse in `i2c_pca_pf_resetchip()` or a warning-only dummy reset.

Control flow: probe obtains an optional IRQ, allocates driver state, maps the first memory resource, initializes adapter fields, gets optional `reset` GPIO, reads `clock-frequency` or defaults to 59000 Hz, lets platform data override timeout and clock, assigns callbacks, selects register spacing from `IORESOURCE_MEM_TYPE_MASK`, requests IRQ if present, and calls `i2c_pca_add_numbered_bus()`. Remove deletes the adapter; devm handles mappings, GPIO, memory, and IRQ.

State and persistence: per-device state is entirely in `i2c_pca_pf_data`. The wait queue and adapter timeout are persistent for device lifetime. Hardware state includes PCA algorithm registers and optional reset GPIO state. No persistent storage is used.

Dependencies and integration points: this file depends on platform resources, OF compatibles `nxp,pca9564` and `nxp,pca9665`, device properties, GPIO descriptors, IRQs, and `i2c-algo-pca`. It can also consume legacy `i2c_pca9564_pf_platform_data`.

Risks: incorrect resource flags select the wrong register stride and break register access. Without a reset GPIO, bus recovery is limited to algorithm-level behavior and the chip may remain stuck. IRQ is optional and polling fallback must be validated on slow systems. Platform data can override DT-derived clock and timeout in ways that produce unexpected bus timing.

Test signals: DT and platform-data probe paths, 8/16/32-bit resource spacing, IRQ and polling completion, reset GPIO pulse on recovery paths, adapter numbering, and transfer behavior against devices that NACK or hold SI low.
