# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca9541.c

Purpose: driver for the NXP PCA9541 two-master I2C bus master selector, modeled as a single-channel arbitrating mux.

Important APIs/types: `struct pca9541` stores client, select timeout, and arbitration timeout. Register helpers `pca9541_reg_read()` and `pca9541_reg_write()` use unlocked SMBus transfers. `pca9541_arbitrate()` implements the datasheet state machine. Mux callbacks are `pca9541_select_chan()` and `pca9541_release_chan()`.

Control flow: probe requires SMBus byte-data support, locks the segment to release any stale bus ownership, allocates an `I2C_MUX_ARBITRATOR` mux core, and adds one child adapter. Select sets an arbitration deadline, loops through `pca9541_arbitrate()`, sleeps/udelay according to short or long retry delay, forces ownership after adapter timeout, and fails after twice the timeout. Release clears bus ownership when this master owns the bus.

State and persistence: hardware control/status registers hold bus ownership, bus-on, bus-init, and test bits. Driver state tracks arbitration timing only during selection.

Dependencies and integration: depends on I2C mux core, SMBus byte-data transfers, jiffies timing, and optional OF match `nxp,pca9541`.

Risks: arbitration forcibly takes ownership after timeout, which can disrupt a peer master. Register access must use unlocked helpers to avoid nested locking. The state-table control array is hardware-specific and fragile. Timeouts inherit adapter timeout settings.

Test signals: two-master contention, forced ownership warning, release behavior, timeout paths, stale-ownership cleanup on probe, and child adapter removal.
