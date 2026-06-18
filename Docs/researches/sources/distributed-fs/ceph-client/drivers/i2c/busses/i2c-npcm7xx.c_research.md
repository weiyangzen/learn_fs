# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-npcm7xx.c

## Purpose
Provides the Nuvoton NPCM7xx/NPCM8xx I2C/SMBus controller driver. It supports master transfers, optional slave mode, FIFO and non-FIFO operation, SMBus block/PEC behavior, timing-table clock programming, debugfs counters, and bus recovery using the controller's SCL toggle capability.

## Important APIs, Types, And Functions
`struct npcm_i2c` is the central state container: adapter, MMIO registers, chip data, spinlock, completion, active messages, indices, FIFO flags, master/slave state, PEC/block flags, recovery info, and diagnostic counters. `npcm_i2c_master_xfer()` implements `.xfer`; `npcm_i2c_bus_irq()` dispatches master or slave IRQ handling. Master control is split across `npcm_i2c_master_start_xmit()`, `npcm_i2c_int_master_handler()`, `npcm_i2c_irq_handle_sda()`, read/write subhandlers, and error handlers. Slave support is behind `CONFIG_I2C_SLAVE` through `.reg_slave` and `.unreg_slave`.

## Control Flow
Probe obtains match data, clock rate, sys-manager regmap, MMIO, IRQ, initializes adapter fields, requests the IRQ, initializes timing and hardware, installs recovery callbacks, registers a numbered adapter, and creates debugfs counters. Master transfer normalizes one-message reads/writes and two-message write-read pairs into write/read buffer sizes, waits briefly for bus free, stores the destination address for recovery, resets/recovers on busy or BER state, arms completion and interrupts, starts the transaction, then waits with an adaptive timeout. IRQs move the state machine through address stall, write FIFO fill, repeated-start read, block-length handling, STOP/EOB completion, NACK, BER, and recovery.

## State And Persistence
The driver keeps rich in-memory state for active transfer progress and diagnostics. Debugfs exposes monotonically increasing counters for bus error, NACK, recovery success/failure, timeout, and completion counts. Hardware state includes two register banks, FIFO threshold/configuration, own slave addresses, PEC/block flags, and module timing. There is no durable storage.

## Dependencies And Integration Points
Depends on platform device/OF matching for `nuvoton,npcm750-i2c` and `nuvoton,npcm845-i2c`, clocks, syscon regmap, I2C core, optional I2C slave framework, debugfs, completions, and generic bus recovery. `npcm_i2c_data` supplies generation-specific FIFO masks and segment-control initialization.

## Risks
This is a highly stateful IRQ machine; race boundaries around `bus->msgs`, completion, master/slave mode switching, and slave-address masking are sensitive. FIFO `LAST`/PEC/block-read handling has hardware workaround comments and can require module reset after errors. Recovery relies on toggling SCL rather than direct line driving. Long transfer limits are large, so timeout estimation and FIFO index arithmetic need stress coverage. Warm-reset stale interrupt status is explicitly guarded in probe.

## Test Signals
Coverage should include standard/fast/fast-plus clock configurations, write-only, read-only, write-read, SMBus block read with `I2C_M_RECV_LEN`, PEC reads, NACK and bus-error injection, busy-bus recovery, FIFO-capable and FIFO-disabled hardware, multi-master contention, debugfs counter increments, slave read/write callbacks when enabled, and repeated module remove/probe or warm reset scenarios.
