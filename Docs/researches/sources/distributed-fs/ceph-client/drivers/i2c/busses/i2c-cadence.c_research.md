# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cadence.c

## Purpose
Cadence/Xilinx I2C controller driver with master, atomic master, optional slave mode, runtime PM, bus recovery, reset control, and input-clock rate change handling.

## APIs, Control Flow, and State
`struct cdns_i2c` holds MMIO, adapter, current message, completions, send/receive counters, clock/reset handles, notifier, cached control/divider state, recovery info, FIFO depth, detected transfer-size limit, atomic flag, and optional slave role state. Master transfer uses `cdns_i2c_master_common_xfer()` to wait for bus idle, set HOLD for repeated starts, reject receive-then-more sequences on broken HOLD hardware, and process each message through `cdns_i2c_process_msg()`. `cdns_i2c_msend()` and `cdns_i2c_mrecv()` program direction, FIFO, transfer-size, HOLD, address, and interrupts; large receives use a transfer-size/HOLD workaround so the controller does not prematurely NACK. Atomic variants poll ISR/status rather than sleeping. Slave mode switches controller roles, sets the slave address, and maps DATA/COMP/NACK/overflow interrupts to I2C slave callbacks.

## Dependencies and Integration
Uses OF compatibles `cdns,i2c-r1p10` and `cdns,i2c-r1p14`, clk, reset, runtime PM autosuspend, pinctrl bus recovery, Linux I2C master/slave APIs, clock notifiers, and optional `fifo-depth`/`clock-frequency` properties.

## Risks and Test Signals
Risks are concentrated in HOLD-bit timing, large receive transfer-size rollover, clock-rate notifier updates while active, slave/master role switching, and PM/reset cleanup. Test r1p10 broken-HOLD paths, repeated starts, large reads over FIFO and transfer-size boundaries, SMBus block reads with PEC length, arbitration loss/retry, atomic transfers, bus recovery on busy bus, slave send/receive/stop, runtime/system suspend, invalid clock rates, and clock rate change abort/post-change cases.
