# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-davinci.c

## Purpose
TI DaVinci/Keystone I2C master adapter. It programs SoC I2C registers, exposes standard and SMBus-emulated transfers, handles runtime PM, CPU frequency changes, and optional GPIO-style SCL bus recovery through the controller pin function registers.

## Important APIs, Types, And Functions
`struct davinci_i2c_dev` holds MMIO base, completion, clock, active buffer, IRQ, adapter, bus frequency, CPU frequency notifier, and `has_pfunc`. Core functions include `i2c_davinci_calc_clk_dividers()`, `i2c_davinci_init()`, `i2c_davinci_xfer_msg()`, `i2c_davinci_xfer()`, and `i2c_davinci_isr()`. Recovery is via `davinci_i2c_scl_recovery_info`. Probe/remove are `davinci_i2c_probe()` and `davinci_i2c_remove()`.

## Control Flow
Probe gets IRQ, clock, MMIO, bus frequency, enables runtime PM, initializes hardware, requests IRQ, registers CPU frequency notifier, configures the adapter, optionally attaches recovery info, and registers a numbered adapter. Transfers resume runtime PM, wait for bus idle, perform each message, and autosuspend. Each message programs SAR, buffer state, count, mode bits, first transmit byte when needed, starts transfer, and waits on a completion signaled by the ISR. The ISR loops through IVR events for arbitration lost, NACK, register ready, RX ready, TX ready, and stop.

## State And Persistence
Runtime state includes `buf`, `buf_len`, `cmd_err`, `stop`, and `terminate`, all consumed by the IRQ handler. Hardware state is reinitialized after arbitration loss, recovery, CPU frequency transitions, suspend/resume, and probe. There is no disk persistence.

## Dependencies And Integration Points
Integrates with platform/OF IDs `ti,davinci-i2c` and `ti,keystone-i2c`, clocks, runtime PM, interrupt handling, cpufreq notifiers, device properties, and I2C generic SCL recovery.

## Risks
The reserved own address `0x08` cannot be targeted. Transfer completion relies on IRQ ordering and completion state; abnormal leftover `buf_len` triggers termination. CPU frequency updates lock the root adapter and reprogram dividers. Recovery requires `ti,has-pfunc`. Runtime PM errors must avoid leaving clocks or autosuspend state inconsistent.

## Test Signals
Exercise standard and fast-mode divider calculation, read/write/zero-length transfers, NACK with and without `I2C_M_IGNORE_NAK`, arbitration loss reset, bus-busy recovery, CPU frequency transition handling, runtime suspend/resume, and probe cleanup on IRQ/notifier/adapter registration failure.
