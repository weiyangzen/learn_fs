# sources/distributed-fs/ceph-client/drivers/leds/leds-expresswire.c

Purpose: shared helper library for Kinetic ExpressWire LED-control protocol used by devices such as KTD2692 and KTD2801. It exports GPIO pulse primitives rather than registering LED class devices.

Important APIs/types/functions: public namespace exports are `expresswire_power_off()`, `expresswire_enable()`, and `expresswire_write_u8()`. Internal helpers `expresswire_start()`, `expresswire_end()`, and `expresswire_set_bit()` generate timing-specific GPIO pulses from `struct expresswire_common_props`.

Control flow: power-off drives the control GPIO low with a sleepable setter and waits `poweroff_us`. Enable disables local IRQs, emits the ExpressWire detect sequence using non-sleeping GPIO writes and `udelay()`, then restores IRQs. `write_u8()` similarly masks local IRQs, emits start timing, shifts bits MSB first using short/long low-high pulses, then emits end timing.

State and persistence: no internal state. The caller owns the GPIO descriptor and timing table. Hardware state persists in the target ExpressWire IC after commands.

Dependencies/integration: depends on GPIO descriptor API, delay APIs, local IRQ masking, and exported symbol namespace `"EXPRESSWIRE"`. Callers must ensure `ctrl_gpio` is usable with non-sleeping `gpiod_set_value()` during timing-critical sections.

Risks: IRQ-off sections protect pulse timing but can add latency if timings are long. Passing a sleep-capable GPIO to enable/write paths is unsafe. Timing data must match the target IC. There is no locking; callers must serialize accesses.

Test signals: scope GPIO waveforms for enable and byte writes, validate MSB-first bit order, ensure namespace exports resolve for dependent drivers, and test power-off with sleepable GPIOs.
