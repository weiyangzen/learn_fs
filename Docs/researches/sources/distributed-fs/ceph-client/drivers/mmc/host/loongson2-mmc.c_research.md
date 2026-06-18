# sources/distributed-fs/ceph-client/drivers/mmc/host/loongson2-mmc.c

## Purpose

`loongson2-mmc.c` implements a platform MMC/SD/SDIO/eMMC host driver for Loongson-2K controllers. It supports multiple SoC variants (`ls2k0300`, `ls2k0500`, `ls2k1000`, `ls2k2000`) through per-platform data covering register range, DMA type, command-data byte reordering, timeout workarounds, and quirks.

## Important APIs, Types, And Functions

- Register macros define the command, response, data, interrupt, DLL, bus-selection, and internal DMA register maps.
- `enum loongson2_mmc_state` models interrupt progress: none, finalize, command sent, response finished, transfer finished, or combined transfer/response wait.
- `struct loongson2_dma_desc` describes internal DMA hardware descriptors with low/high next descriptor and memory address fields.
- `struct loongson2_mmc_host` holds current request, regmap, resource, clock, current clock rate, coherent descriptor memory, DMA completion flag, external DMA channel, stop-command flag, bus width, IRQ lock, current state, and platform data.
- `struct loongson2_mmc_pdata` supplies variant hooks: `reorder_cmd_data`, `fix_data_timeout`, `setting_dma`, `prepare_dma`, and `release_dma`.
- `loongson2_mmc_send_request()` prepares data/DMA, applies variant timeout fixes, sends command, and handles select-card deselect as a special immediate success.
- `loongson2_mmc_irq()` is the hard IRQ state machine for command sent, response timeout/CRC, data CRC/timeout, data finished, and SDIO IRQs.
- `loongson2_mmc_irq_worker()` finalizes responses, unmaps DMA, sends stop commands, sets bytes transferred, clears host state, and completes the request.
- `loongson2_mmc_set_ios()` controls vmmc, reset, interrupt enables, prescaler, DLL mode for DDR timing, and bus width.
- External DMA support is in `loongson2_mmc_prepare_external_dma()`, `ls2k0500_mmc_set_external_dma()`, and `ls2k1000_mmc_set_external_dma()`.
- Internal descriptor DMA support is in `loongson2_mmc_prepare_internal_dma()`, `ls2k2000_mmc_set_internal_dma()`, and `loongson2_mmc_release_internal_dma()`.

## Control Flow And State

`loongson2_mmc_request()` rejects CMD48 on the `ls2k0300` quirk path by completing immediately, then stores the request and calls `loongson2_mmc_send_request()`. Sending configures data registers, maps and starts DMA via the platform hook, optionally waits for TX FIFO full on affected write commands, and programs command argument/control. The command state is selected based on whether data and/or response is expected.

The hard IRQ reads interrupt and data status registers. SDIO IRQs are handled separately by acknowledging and calling `sdio_signal_irq()`. For active requests it transitions state on command-sent and data-finished events, records timeout/CRC errors, and on close invokes `reorder_cmd_data()` before waking the threaded IRQ. The threaded IRQ unmaps data SGs, waits for DMA completion when necessary, reads four response registers, clears command registers, optionally sends the request stop command, calculates `bytes_xfered`, resets host state, and calls `mmc_request_done()`.

Persistent hardware state includes current clock, prescaler, bus width, enabled interrupts, DLL delay programming for DDR modes, variant DMA routing registers, and coherent descriptor memory for internal DMA variants.

## Dependencies And Integration Points

The driver integrates with platform/OF match data, regmap MMIO, optional clocks or `clock-frequency` firmware property, threaded IRQs, DMAEngine for external DMA variants, coherent DMA descriptors for internal DMA variants, MMC slot GPIO helpers, regulators, and SDIO IRQ infrastructure. It uses `bitrev8x4()` and endian conversion to repair protocol data ordering for specific commands.

## Risks And Edge Cases

- `loongson2_mmc_prepare_dma()` sets `cmd->data->error` on failure in `loongson2_mmc_send_request()`; that path assumes `cmd->data` exists when DMA preparation fails.
- Internal DMA allocates one page of descriptors while `mmc->max_segs` is set to 1, keeping descriptor use bounded. Raising `max_segs` would require descriptor memory review.
- Variant reorder hooks mutate mapped scatterlist virtual data using `sg_virt()`, so data buffers must be CPU-addressable as expected.
- The `ls2k0300` CMD48 quirk completes without setting an explicit error, effectively hiding the unsupported operation from upper layers.
- SDIO IRQ enable uses `regmap_update_bits()` with raw `enable` as value rather than a masked bit value; enable values are expected to be 0/1.
- DLL mode silently returns if lock polling fails; no error is propagated to `set_ios`.

## Test Signals

Coverage should include each compatible, external and internal DMA paths, read/write data transfers, stop-command sequencing, data/response CRC and timeout IRQs, SDIO IRQ enable/ack, DDR timing DLL setup, CMD48 quirk behavior, byte-order fixups for ACMD13/22/51/CMD30/SD_SWITCH, TX FIFO full timeout workaround on writes, regulator power cycling, ACPI-style `clock-frequency`, and suspend/resume clock transitions.
