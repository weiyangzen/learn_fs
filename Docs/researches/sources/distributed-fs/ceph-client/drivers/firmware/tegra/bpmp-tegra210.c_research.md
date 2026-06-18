# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra210.c

Tegra210 BPMP transport implementation. Unlike Tegra186+, it retrieves channel buffers from BPMP atomics registers and uses an arbitration semaphore register block plus legacy interrupt controller retriggering for doorbells.

`struct tegra210_bpmp` stores the mapped atomics and arb-sema regions and cached TX IRQ data. Channel state is encoded as two-bit fields per channel: `SL_SIGL`, `SL_QUED`, `MA_FREE`, and `MA_ACKD`. Readiness/free predicates compare the semaphore state to the expected value. Post/ack operations write masks to semaphore set/clear offsets to move ownership between master and firmware. Doorbell ringing calls `irq_retrigger()` on the TX IRQ chip.

Init maps two platform resources, initializes the TX, RX, and threaded channels by asking BPMP for each channel base address through the atomics trigger/result registers, maps each 0x80-byte channel window, records IRQ data for `"tx"`, and registers an IRQ handler for `"rx"` that invokes `tegra_bpmp_handle_rx()`. It exports `tegra210_bpmp_ops` without deinit/resume callbacks.

State is MMIO-backed in BPMP channel windows and arb-sema registers. Linux stores only mappings, completions, and IRQ data. Dependencies include platform resources, IRQ chip retrigger support, raw MMIO accessors, and the private BPMP op table.

Risks include reliance on `irq_retrigger`; platforms whose TX IRQ chip lacks it cannot ring BPMP. Channel base addresses returned by firmware are trusted and mapped fixed-size. Raw MMIO access is used for semaphore state and requires correct hardware ordering assumptions. Test signals include DT resource/IRQ names, channel address retrieval per index, semaphore state transitions during transfers, RX interrupt delivery, and behavior on IRQ chips without retrigger support.
