# sources/distributed-fs/ceph-client/drivers/media/rc/meson-ir-tx.c

Purpose: implements the Amlogic Meson IR blaster transmitter as an rc-core raw-TX platform driver for `amlogic,meson-g12a-ir-tx` devices.

Important APIs and types: `struct meson_irtx` stores the MMIO base, current encoded TX buffer/head/length, carrier, duty cycle, spinlock, completion, and modulator clock rate. Probe entry is `meson_irtx_probe()`. rc-core callbacks are `meson_irtx_transmit()`, `meson_irtx_set_carrier()`, and `meson_irtx_set_duty_cycle()`. Hardware helpers include `meson_irtx_setup()`, `meson_irtx_set_mod()`, `meson_irtx_prepare_pulse()`, `meson_irtx_prepare_space()`, and FIFO draining through `meson_irtx_send_buffer()`.

Control flow: probe maps registers, gets the IRQ, initializes defaults and synchronization, chooses the modulator clock from the `xtal` clock or fallback 1 MHz mode, programs the transmitter, requests the FIFO-threshold IRQ, allocates an `RC_DRIVER_IR_RAW_TX` device, and registers it with devm rc-core. Transmit validates each pulse/space duration against hardware timebase limits, allocates a u32 hardware command buffer, encodes pulses with carrier modulation and spaces with the smallest usable timebase, loads the first FIFO batch under lock, waits for IRQ-driven completion up to `IR_MAX_DURATION`, then frees the buffer and clears state.

State and persistence: TX state is transient and protected by `ir->lock`; `buf`, `buf_len`, and `buf_head` describe the active transmission until completion or timeout. Carrier and duty-cycle settings persist in the driver structure and hardware modulator registers while the platform device is active. The completion object serializes caller wait against FIFO-threshold interrupts.

Dependencies and integration points: depends on platform device resources, OF match data, MMIO accessors, clk framework, IRQs, completions, spinlocks, and rc-core raw-TX APIs. Userspace reaches it through LIRC/rc-core transmit interfaces, including carrier and duty-cycle controls.

Risks: only one active transmission is represented in `struct meson_irtx`; concurrent callers rely on upper rc-core serialization. Duration validation rejects values that cannot fit hardware delay fields, but rounding can still alter exact waveform timing. The timeout is based on `IR_MAX_DURATION`, not the exact waveform length. Clock acquisition enables `xtal` but uses devm lifetime without an explicit disable in this file. IRQ handling assumes FIFO threshold interrupts continue until the buffer is drained.

Test signals: device-tree probe on compatible Meson hardware, rc-core registration as TX-only, carrier and duty-cycle setting, short and long transmit waveform validation, FIFO interrupt completion, timeout handling when IRQs do not arrive, and waveform inspection with an IR receiver or oscilloscope.
