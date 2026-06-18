# sources/distributed-fs/ceph-client/drivers/media/rc/ir-hix5hd2.c

Purpose: platform raw-IR receiver driver for Hisilicon hix5hd2/hi3796cv300 controllers. It configures SoC IR hardware in raw symbol mode, drains hardware symbol FIFOs on interrupts, converts symbol low/high widths into rc-core raw pulse/space events, and registers an `RC_DRIVER_IR_RAW` device.

Important APIs, types, and functions: register and bit macros cover enable/config/data/interrupt/start registers. `struct hix5hd2_soc_data` supplies SoC clock register and extra-enable flag. `struct hix5hd2_ir_priv` stores MMIO base, IRQ, rc device, optional syscon regmap, clock, rate, and SoC data. `hix5hd2_ir_clk_enable()` toggles clock through syscon or common clock API. `hix5hd2_ir_enable()` writes enable bits. `hix5hd2_ir_config()` waits for not busy, programs raw mode, interrupt threshold, frequency divisor, unmasks interrupts, and starts capture. `hix5hd2_ir_rx_interrupt()` handles overflow, receive, and timeout interrupts, drains symbols, stores pulse/space events, sets idle on long symbols, clears interrupt causes, and handles raw events. Probe registers rc-core and IRQ; PM hooks disable/re-enable clocks and restart hardware.

Control flow: probe maps resources, gets IRQ/clock, enables the clock to sample rate, allocates rc-core raw device, registers it, requests the IRQ, and stores private data. rc-core open enables the clock and configures hardware; close disables clock. Interrupts read `IR_INTS`, handle overflow by flushing FIFO and reporting overflow, then read `IR_DATAH` count and `IR_DATAL` symbols for receive/timeout, converting packed low/high counts to 10 us raw durations. Suspend disables clocks; resume enables clocks, clears interrupts, and restarts capture.

State and persistence behavior: state is per-platform-device kernel memory. The hardware remains configured only while the rc device is open or resumed. No scancode state is kept; rc-core raw decoders own protocol state.

Dependencies and integration points: depends on platform device resources, device tree match data, optional `hisilicon,power-syscon` regmap, common clock, IRQ APIs, and rc-core raw event APIs. Device tree can provide `linux,rc-map-name`; otherwise the driver uses `RC_MAP_EMPTY`.

Risks and edge cases: bitwise expression precedence in config register construction must be read carefully; fields rely on masks/shifts. `hix5hd2_ir_config()` busy-waits up to 10 ms. Overflow handling requires reading `IR_DATAL` before clearing overflow because hardware does not clear FIFO. Probe enables the clock before registration and open enables it again, so clock state assumptions should be validated. PM resume uses both hardware clock helper and `clk_prepare_enable()`.

Test signals: test device tree match for both compatibles, raw decoding through rc-core, overflow behavior under heavy IR input, open/close clock gating, suspend/resume, and `linux,rc-map-name` propagation.
