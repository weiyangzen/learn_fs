# sources/distributed-fs/ceph-client/drivers/input/touchscreen/fsl-imx25-tcq.c

Purpose: `fsl-imx25-tcq.c` is a platform input driver for the Freescale i.MX25 Touchscreen Conversion Queue connected to the i.MX25 ADC. It programs ADC queue items for a 4-wire resistive touchscreen, handles pen-detect/FIFO interrupts, averages samples, and reports single-touch X/Y.

Important APIs, types, and functions: `struct mx25_tcq_priv` holds queue and core regmaps, input device, mode, thresholds/timings, clock, IRQ, and device pointer. `imx25_setup_queue_cfgs()` programs ADC configurations for precharge, touch detect, X measurement, and Y measurement. `imx25_setup_queue_4wire()` lays out the queue and computes expected sample count. IRQ control helpers mask/unmask pen and FIFO IRQs, force queue start/stop, and reset FIFO. `mx25_tcq_create_event_for_4wire()` interprets FIFO samples and reports down/up/bounce. `mx25_tcq_irq()` is the top half and `mx25_tcq_irq_thread()` drains FIFO samples. `mx25_tcq_init()` computes debounce/settling counts from the ADC clock and programs queue control.

Control flow: probe maps the queue registers, parses DT (`fsl,wires` plus optional threshold/debounce/settling), creates a regmap, gets IRQ, allocates input, obtains parent TSADC core registers and clock, requests a threaded IRQ, and registers input. Input open enables the clock, initializes the queue, and arms touch detection. On pen detect, the top half masks pen IRQ, starts the queue, and enables FIFO IRQ. On FIFO ready, the thread reads aligned sample groups, validates pre/post touch measurements against the threshold, reports averaged coordinates or release, and either continues sampling or re-enables touch detection.

State and persistence: runtime state is programmed into memory-mapped ADC/TS registers and the clock enable state. No persistent configuration exists beyond DT defaults. Open/close gates the hardware clock and IRQ masks.

Dependencies and integration points: it depends on the i.MX25 TSADC MFD parent for `regs` and `clk`, MMIO regmap, OF compatible `fsl,imx25-tcq`, Linux input single-touch APIs, and platform resources.

Risks: only 4-wire mode is supported. FIFO sample grouping assumes counts are multiples of `sample_count` and drops partial groups. Invalid FIFO item IDs discard the whole event. Timing calculations depend on clock rate and can clamp silently at hardware limits. Parent TSADC data must be present and valid.

Test signals: validate DT parsing, unsupported wire count rejection, clock enable/disable, queue register programming, pen detect to FIFO interrupt transition, averaged coordinate reporting, release threshold behavior, bounce sampling continuation, FIFO overflow/underrun recovery, and close while queue is active.
