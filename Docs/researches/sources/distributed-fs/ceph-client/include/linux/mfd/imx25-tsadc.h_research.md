# sources/distributed-fs/ceph-client/include/linux/mfd/imx25-tsadc.h

Purpose: This header defines the Freescale i.MX25 touchscreen/ADC MFD shared register map. It describes the parent TSADC state, global control/status registers, queue register layout, FIFO/result extraction, interrupt/DMA masks, and per-item ADC configuration fields.

Important APIs, types, and constants: `struct mx25_tsadc` stores the regmap, IRQ domain, and clock. Register macros cover `MX25_TSC_TGCR`, `MX25_TSC_TGSR`, `MX25_TSC_TICR`, queue FIFO/control/status/mask/item/config registers, and channel-stride addressing. Bit macros configure power, reset, clock, sleep, ADC clock, internal reference, queue reset, watermark, repeat/fixed queue modes, FIFO status, DMA/IRQ enables, settling time, number of samples, touch-panel switch states, positive/negative references, input selection, and FIFO data/id extraction.

Control flow, state, and persistence: Parent code enables clocks and regmap, creates an IRQ domain, and child touchscreen/IIO ADC drivers program queue items and consume FIFO events. Runtime state includes queue configuration, FIFO contents, pending interrupts, ADC power mode, sampling references, and clock divider setup. Persistence is limited to hardware register state while powered.

Dependencies and integration points: It integrates with regmap, clk, IRQ domain, touchscreen input drivers, and IIO ADC consumers.

Risks and test signals: Risks include invalid `MX25_ADCQ_ITEM()` indexes, off-by-one sample count via `NOS(x)`, incorrect reference/input combinations damaging touch readings, and failing to clear FIFO errors. Test signals include pen/touch input tests, ADC channel readback, FIFO overrun/underrun handling, IRQ domain mapping, clock rate/divider validation, and suspend/resume power-mode checks.
