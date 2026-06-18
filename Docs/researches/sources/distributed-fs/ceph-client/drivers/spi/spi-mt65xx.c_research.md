<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt65xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mt65xx.c

## Purpose

`spi-mt65xx.c` is the generic MediaTek SPI controller driver for many MTK SoCs. It exposes a `spi_controller` for ordinary SPI messages, supports GPIO and native chip select handling, handles FIFO and DMA transfer paths, and adds `spi-mem` support for IPM-design controllers that can run memory-like command/address/dummy/data transactions with dual/quad bus widths.

## Important APIs, Types, and Functions

The main runtime state is `struct mtk_spi`, which stores MMIO base, clocks, compatible-data flags, current transfer state, DMA scatterlist cursors, SPI-MEM completion, DMA addresses, pad-select data, and a CPU latency QoS request. `struct mtk_spi_compatible` captures per-SoC behavior such as `need_pad_sel`, `must_tx`, `enhance_timing`, `dma_ext`, `no_need_unprepare`, and `ipm_design`.

Probe binds compatible entries such as `mediatek,mt2701-spi`, `mt6765-spi`, `mt6893-spi`, `mt6991-spi`, and `mediatek,spi-ipm` to controller capabilities. Core SPI callbacks are `mtk_spi_setup()`, `mtk_spi_set_cs()`, `mtk_spi_prepare_message()`, `mtk_spi_unprepare_message()`, `mtk_spi_transfer_one()`, and `mtk_spi_can_dma()`. Transfer helpers include `mtk_spi_prepare_transfer()`, `mtk_spi_setup_packet()`, `mtk_spi_fifo_transfer()`, `mtk_spi_dma_transfer()`, `mtk_spi_update_mdata_len()`, and `mtk_spi_setup_dma_addr()`. Interrupt handling is split between `mtk_spi_interrupt()` and threaded `mtk_spi_interrupt_thread()`.

SPI-MEM integration is through `mtk_spi_mem_adjust_op_size()`, `mtk_spi_mem_supports_op()`, and `mtk_spi_mem_exec_op()`, exposed through `mtk_spi_mem_ops` and `mtk_spi_mem_caps`.

## Control Flow

Probe allocates a host controller, selects SoC match data, parses optional `mediatek,pad-select`, maps registers, obtains clocks, programs DMA segment and mask limits, registers a threaded IRQ, enables runtime PM, and registers the SPI controller. The controller advertises mode bits and flags based on match data; IPM controllers additionally advertise SPI-MEM dual/quad support and per-operation frequency.

For normal messages, `prepare_message` programs mode, endian, clock phase/polarity, bit order, interrupt enables, pad select, tick delay, and chip-select timing. `transfer_one` chooses IPM half-duplex direction when needed, then uses DMA if the transfer is longer than the 32-byte FIFO and both buffer pointers are 4-byte aligned; otherwise it writes or reads the FIFO in chunks. Interrupt completion either drains/fills the next FIFO chunk or advances DMA scatterlist segments and packet loops until all data is transferred, then finalizes the current transfer.

For SPI-MEM, `exec_op` resets and initializes hardware, encodes command/address/dummy/data byte counts into IPM registers, builds a temporary TX buffer containing opcode, address, dummy bytes, and optional data-out payload, maps TX and optional RX buffers, starts DMA, waits for completion, copies back from an aligned bounce buffer when needed, disables DMA bits, and frees temporary state.

## State and Persistence Behavior

The driver keeps only volatile kernel and hardware-register state. `mdata->state` tracks idle versus paused transfer state; `cur_transfer`, `xfer_len`, `num_xfered`, scatterlist pointers, and DMA lengths track an active message. `use_spimem` steers the IRQ top half toward completing a SPI-MEM operation instead of waking the threaded normal-transfer handler. `spi_clk_hz` caches the peripheral clock rate for timing calculations.

There is no file-backed persistence. Persistent effects are only the external SPI device side effects caused by transfers, such as flash reads/writes issued by upper layers.

## Dependencies and Integration Points

The file integrates with the Linux SPI core, SPI-MEM, platform devices, device tree, runtime PM, interrupts, DMA mapping, clock framework, GPIO descriptors, pinctrl PM, and CPU latency QoS. The MediaTek platform-data header supplies `struct mtk_chip_config` fields for sample selection and tick delay.

## Risks and Edge Cases

`mtk_spi_can_dma()` tests both `tx_buf` and `rx_buf` pointer alignment even when one direction is absent; null pointers are aligned, so this works but is subtle. DMA transfer splitting depends on packet-size multiples and scatterlist lengths; off-by-one or zero-length residual handling would stall completion. SPI-MEM allocates temporary DMA buffers with `GFP_DMA`, so memory pressure can fail command execution. IPM setup assumes command, address, and dummy byte counts fit the encoded register fields; `supports_op` and `adjust_op_size` must remain consistent with `exec_op`.

Clock handling has two lifetime models: regular `prepare_enable` and `no_need_unprepare` enable/disable-only behavior. Probe, runtime PM, remove, and system sleep paths must stay paired or register access can occur with clocks off.

## Test Signals

Useful tests include build coverage for all compatible-data variants, probe with and without pad-select and GPIO chip selects, mode 0-3 plus LSB-first transfers, FIFO transfers with unaligned and sub-32-byte buffers, DMA transfers across multiple scatterlist segments, TX-only/RX-only/full-duplex cases, pause/resume interrupt handling, runtime suspend/resume, and SPI-MEM read/write operations with aligned and unaligned buffers, dual/quad widths, no-data commands, and timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt65xx.c -->
