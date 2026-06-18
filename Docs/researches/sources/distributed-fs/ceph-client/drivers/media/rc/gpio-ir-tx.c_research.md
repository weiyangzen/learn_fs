<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c

Purpose: platform raw IR transmitter that bit-bangs a GPIO, either unmodulated or modulated at a configured carrier and duty cycle.

Important APIs and functions: `struct gpio_ir` stores the GPIO, carrier, and duty cycle. rc-core callbacks are `gpio_ir_tx`, `gpio_ir_tx_set_carrier`, and `gpio_ir_tx_set_duty_cycle`. Timing helpers are `delay_until`, `gpio_ir_tx_unmodulated`, and `gpio_ir_tx_modulated`. Probe is `gpio_ir_tx_probe`.

Control flow: probe allocates state and an `RC_DRIVER_IR_RAW_TX` device, gets an output-low GPIO, assigns transmit and carrier/duty callbacks, defaults to 38 kHz and 50 percent duty cycle, and registers rc-core. Transmit disables local IRQs, then either toggles the GPIO for each pulse/space or generates carrier cycles during pulse intervals using `ndelay`, `udelay`, and `mdelay` until the requested waveform is complete.

State and persistence: only carrier and duty-cycle settings persist in driver memory while bound. GPIO is driven low after unmodulated transmit and naturally ends low after modulated pulse loops.

Dependencies and integration points: depends on OF, GPIO descriptors, platform bus, delay/timing helpers, and rc-core raw TX. Device-tree compatible is `gpio-ir-tx`; Kconfig excludes PREEMPT_RT because transmit disables local IRQs and busy-waits.

Risks: bit-banged timing blocks the CPU with local interrupts disabled and can affect latency. Carrier is limited to 500 kHz but duty cycle is not range-checked in this file. Long buffers can monopolize CPU time. Timing accuracy depends on GPIO latency and busy-wait calibration.

Test signals: waveform capture with a logic analyzer for default and custom carriers/duty cycles, unmodulated mode with carrier set to zero, invalid high carrier rejection, rc-core TX API tests, and latency testing on target SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c -->
