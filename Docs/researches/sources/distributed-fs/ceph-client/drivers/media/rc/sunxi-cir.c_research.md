# sources/distributed-fs/ceph-client/drivers/media/rc/sunxi-cir.c

Purpose: platform raw IR receiver driver for Allwinner sunXi CIR controllers. It configures clocks/resets, reads RX FIFO bytes, converts them to pulse/space durations, and registers an rc-core raw receiver.

Important APIs and functions: `struct sunxi_ir_quirks` captures reset and FIFO-size differences; `struct sunxi_ir` stores rc device, MMIO base, IRQ, clocks, reset, and keymap. Main functions are `sunxi_ir_irq`, timeout conversion helpers, `sunxi_ir_set_timeout`, `sunxi_ir_hw_init`, `sunxi_ir_hw_exit`, probe/remove/shutdown, and PM suspend/resume.

Control flow: probe selects SoC quirks from OF match data, obtains APB and IR clocks, optional reset, sets IR base clock, maps registers, allocates/registers raw rc device, requests IRQ, then initializes hardware. Hardware init deasserts reset, enables clocks, selects CIR mode, programs noise and idle thresholds, inverts input, clears status, enables overflow/packet-end/FIFO interrupts, and enables RX. IRQ reads status, clears pending bits, drains available FIFO bytes up to FIFO size, stores filtered raw events, reports overflow or idle packet end, and wakes raw decoding.

State and persistence: per-device state is devm-managed except the rc device, which is explicitly unregistered/freed. Hardware register state is volatile and reinitialized after resume. Optional DT keymap name is stored as a pointer to DT property memory.

Dependencies and integration points: depends on OF, clocks, reset controls, platform MMIO/IRQ, and rc-core raw APIs. Device compatibles cover sun4i-a10, sun5i-a13, and sun6i-a31 variants.

Risks and edge cases: remove calls `rc_unregister_device` before `sunxi_ir_hw_exit`, so IRQs must be quiesced by managed IRQ teardown/order. Timeout conversion must avoid values outside 8-bit idle threshold; min/max are derived for sysfs validation. FIFO count macro depends on local `ir` variable, which is fragile style. Resume always reinitializes hardware regardless of users count.

Test signals: DT probe for each compatible, clock-rate programming, idle-threshold min/max behavior, FIFO drain under known remotes, overflow and packet-end handling, suspend/resume, shutdown clock/reset cleanup, and custom `linux,rc-map-name`.
