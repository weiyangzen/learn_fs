# sources/distributed-fs/ceph-client/drivers/media/rc/st_rc.c

Purpose: platform raw IR/UHF receiver driver for STMicroelectronics communication IRB hardware. It converts hardware mark and symbol-period FIFO values into standard rc-core pulse/space raw events.

Important APIs and functions: `struct st_rc_device` stores device, IRQ/wake state, clock, MMIO bases, rc device, overclock correction factors, UHF mode, and reset control. Main functions are `st_rc_hardware_init`, `st_rc_rx_interrupt`, `st_rc_send_lirc_timeout`, `st_rc_open`, `st_rc_close`, `st_rc_probe`, `st_rc_remove`, and PM suspend/resume handlers.

Control flow: probe requires DT `rx-mode` of `uhf` or `infrared`, obtains clock/reset/MMIO/IRQ resources, initializes hardware, registers a raw rc device, requests IRQ, enables wake IRQ, and sends an initial timeout for LIRC synchronization. Open enables RX interrupts and receiver; close disables them. The ISR drains FIFO/status for up to about 10 ms, handles overrun by reporting overflow and clearing status, reads symbol and mark, computes space as symbol minus mark, applies clock correction if needed, stores pulse and space events, and emits a timeout for the last symbol.

State and persistence: runtime state is in `st_rc_device` and volatile IRB registers. Clock divisor and max-symbol-period settings are reprogrammed on resume when not using wake-only suspend. No persistent storage exists.

Dependencies and integration points: depends on platform/OF, clocks, reset controls, pinctrl PM states, wakeirq helpers, MMIO, interrupts, and rc-core raw decoding. It integrates with system wake through `device_init_wakeup` and `dev_pm_set_wake_irq`.

Risks and edge cases: probe fails if `rx-mode` is absent or unexpected. Overclock correction uses integer scaling and may skew durations. The ISR ignores marks <=2 or symbols <=1 as noise and drains only until a jiffies timeout, so bursts under heavy interrupt load may leave FIFO data. Suspend wake path leaves hardware configured differently from full suspend. Remove disables the clock but does not assert reset.

Test signals: DT probe for IR and UHF modes, clock divisor correctness, IRQ FIFO drain under remote input, overrun handling, LIRC initial timeout, wake-from-suspend behavior, pinctrl sleep/default transitions, and raw decoder output against known protocols.
