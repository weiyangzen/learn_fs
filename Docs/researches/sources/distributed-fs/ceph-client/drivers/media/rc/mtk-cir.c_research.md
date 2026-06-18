# sources/distributed-fs/ceph-client/drivers/media/rc/mtk-cir.c

Purpose: implements the MediaTek MT7622/MT7623 consumer IR receiver as an rc-core raw receiver. It programs sampling periods and interrupt thresholds, reads captured pulse-width registers, and feeds software decoders with raw events.

Important APIs and types: SoC differences are modeled by `struct mtk_ir_data`, register-offset arrays, and field descriptors. `struct mtk_ir` stores device, rc device, MMIO base, IRQ, clocks, and SoC data. Key functions are `mtk_ir_probe()`, `mtk_ir_irq()`, `mtk_ir_remove()`, register helpers (`mtk_w32_mask`, `mtk_w32`, `mtk_r32`), and period calculation in `mtk_chk_period()`.

Control flow: probe gets the IR and optional bus clocks, maps registers, allocates an `RC_DRIVER_IR_RAW` device, applies keymap and input metadata, registers rc-core, gets the IRQ, enables clocks, disables IR interrupts while configuring, requests the IRQ, writes software and hardware sampling periods, sets de-glitch count, enables PWM/IR and OK-count completion, then enables interrupts. On IRQ, the driver reads 17 capture registers, decodes four one-byte pulse/space widths from each, alternates pulse state, scales durations by the sample period, stores raw events, appends a trailing long space if the hardware capture did not end cleanly, runs `ir_raw_event_handle()`, restarts the controller, and clears interrupt status. Remove disables interrupts, synchronizes the IRQ, and disables clocks.

State and persistence: runtime state is devm-managed except for enabled clocks and hardware registers, which are undone in remove. Capture state does not persist across interrupts; each IRQ processes the fixed hardware register bank. The rc device timeout is set to the maximum one-byte sample span.

Dependencies and integration points: depends on OF compatibles `mediatek,mt7623-cir` and `mediatek,mt7622-cir`, clk framework, platform MMIO resources, IRQs, reset-capable hardware state through register writes, and rc-core raw decoders. Device tree may provide `linux,rc-map-name`; otherwise `RC_MAP_EMPTY` is used.

Risks: hardware stores at most 68 pulse/space bytes, so longer frames lose trailing data; the driver mitigates with a trailing long space but cannot recover missing edges. The IRQ parser currently stores all bytes including zero-width tail bytes before relying on decoder filters. Sample period math depends on accurate clock rates and SoC divisor data. Error path after enabling the first clock must disable it if bus-clock enable fails, which this file handles, but runtime PM is not implemented.

Test signals: probe both MT7622 and MT7623 compatibles, validate clock fallback for old device trees without `bus`, measure sample period, receive NEC/RC5/RC6 and long frames through software decoders, exercise overflow/truncation behavior with long captures, remove while IRQs are active, and run suspend-style clock/reset tests at the platform level.
