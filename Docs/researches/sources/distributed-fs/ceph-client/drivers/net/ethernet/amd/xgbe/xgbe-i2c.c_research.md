# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-i2c.c

## Purpose
`xgbe-i2c.c` implements the driver's private I2C master used mainly by the v2 PHY path for SFP EEPROM/GPIO access, SFP PHY-over-I2C access, and I2C-attached redrivers. It wraps the DesignWare-style I2C register interface behind `struct xgbe_i2c_if`.

## Important APIs, Types, And Functions
- `xgbe_i2c_abort`, `xgbe_i2c_set_enable`, `xgbe_i2c_enable`, and `xgbe_i2c_disable` control the I2C master and recover from disable failures.
- `xgbe_i2c_write` and `xgbe_i2c_read` drive FIFO fill/drain for the current `xgbe_i2c_op_state`.
- `xgbe_i2c_isr_bh_work`, `xgbe_i2c_isr`, and `xgbe_i2c_combined_isr` handle I2C interrupts and support both separate and combined IRQ routing.
- `xgbe_i2c_xfer` is the synchronous transfer API exposed through `i2c_if->i2c_xfer`.
- `xgbe_i2c_start`, `xgbe_i2c_stop`, and `xgbe_i2c_init` manage IRQ registration and controller setup.
- `xgbe_init_function_ptrs_i2c` fills `struct xgbe_i2c_if`.

## Control Flow
The PHY v2 start path starts I2C before SFP detection. Each transfer takes `pdata->i2c_mutex`, disables the controller, programs the target address and operation state, clears interrupts, enables the controller, and unmasks I2C interrupts. The TX-empty interrupt seeds read or write commands into the FIFO; RX-full drains read data; STOP or TX-abort completes `pdata->i2c_complete`. The caller waits up to one second and maps abort causes to `-ENOTCONN` or `-EAGAIN`.

## State And Persistence
Runtime state is in `pdata->i2c`: controller feature sizes, `started`, and a single active `op_state`. `pdata->i2c_complete` synchronizes interrupt completion with callers, and `pdata->i2c_mutex` serializes transfers. No state is persistent across device teardown.

## Dependencies And Integration Points
This file depends on XI2C register macros, Linux IRQ/workqueue/completion/mutex APIs, `system_bh_wq`, and `pdata->vdata->irq_reissue_support`. The primary consumers are `xgbe-phy-v2.c` SFP, external PHY, and redriver code. Platform and PCI probing supply `xi2c_regs` and the I2C IRQ.

## Risks
All transfers are serialized and use a fixed one-second timeout, which can delay link handling if hardware is wedged. Transfer completion relies on interrupts; incorrect IRQ routing or reissue behavior can stall operations. The FIFO logic assumes the controller is configured to avoid RX overflow. Error handling disables interrupts and controller state, but callers must tolerate `-ETIMEDOUT`, `-ENOTCONN`, `-EAGAIN`, and `-EIO` during SFP probing.

## Test Signals
Exercise SFP insertion/removal, EEPROM reads via `ethtool -m`, SFP GPIO signal changes, and redriver configuration on hardware using separate and combined IRQs. Kernel logs for "i2c operation timed out", TX abort diagnostics, and controller enable/disable failures are important regression signals.
