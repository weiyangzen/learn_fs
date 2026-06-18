# subset-b-005385 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c

## Purpose

`spi-mt7621.c` is a compact SPI controller driver for the Ralink/MediaTek MT7621 SoC. The hardware is treated as a half-duplex, flash-oriented controller with a small command/data window and native chip select polarity register. The driver deliberately disables claimed full-duplex behavior because the silicon shifts unintended opcode data in that mode.

## Important APIs, Types, and Functions

`struct mt7621_spi` stores the controller pointer, MMIO base, system clock frequency, last programmed speed, and `pending_write` byte count. Register helpers `mt7621_spi_read()` and `mt7621_spi_write()` wrap MMIO accesses. `mt7621_spi_set_native_cs()` selects the hardware slave, forces more-buffer mode, disables full-duplex, and controls active chip-select polarity.

The message and transfer path is implemented by `mt7621_spi_prepare_message()`, `mt7621_spi_prepare()`, `mt7621_spi_wait_till_ready()`, `mt7621_spi_write_half_duplex()`, `mt7621_spi_read_half_duplex()`, `mt7621_spi_flush()`, and `mt7621_spi_transfer_one()`. `mt7621_spi_setup()` clamps and validates requested device speed. Probe maps registers, gets the system clock, allocates/registers the controller, issues `device_reset()`, and advertises two native chip selects.

## Control Flow

Before a message, the driver waits for the transfer register to become idle, scans all transfers to find the lowest requested speed, and programs the controller clock divider. The divider must fit the hardware's 12-bit-ish range, with rates below 2 clamped to 2. The mode programming honors LSB-first but clears CPHA/CPOL because only mode 0 is considered reliable on this controller.

Write transfers accumulate bytes into the opcode/data registers using the hardware's unusual opcode byte ordering. Once the buffer reaches 36 bytes or the transfer ends, `mt7621_spi_flush()` triggers a half-duplex operation with no RX bytes. Read transfers combine any pending write prefix with the read transaction, program `MOREBUF` with TX and RX bit counts, start the transaction, wait for completion, and copy up to 32 RX bytes per iteration from the DATA registers.

`transfer_one` rejects simultaneous TX and RX buffers with `-EIO`, otherwise dispatches to the read or write half-duplex helper and returns synchronously.

## State and Persistence Behavior

The only persistent driver state is per-controller runtime state in `struct mt7621_spi`. `pending_write` is a transient batching mechanism that lets a write prefix be combined with a subsequent read, which matches flash command/address/read patterns. `speed` records the last requested speed but is not used as a skip cache in the current path.

There is no host-side persistence; persistent side effects are operations performed by attached SPI devices.

## Dependencies and Integration Points

The driver depends on the platform bus, device tree compatible `ralink,mt7621-spi`, clock framework, reset framework, MMIO helpers, and the SPI core. It exposes `SPI_CONTROLLER_HALF_DUPLEX`, `SPI_LSB_FIRST`, 8-bit words, GPIO descriptor support, and two native chip selects.

## Risks and Edge Cases

The driver intentionally forces mode 0 despite advertising only `SPI_LSB_FIRST` mode bits; devices requiring other modes are not supported. `mt7621_spi_wait_till_ready()` uses a fixed 2000 microsecond polling loop, so unusually slow hardware or long operations may timeout. The pending-write batching and opcode swizzling are fragile because the first four bytes are written with different byte order than later data registers. Full-duplex requests fail by design.

`mt7621_spi_prepare_message()` uses each transfer's `speed_hz` directly; if a transfer has zero speed, it can become the selected minimum and later cause invalid divider behavior unless upper layers normalize it.

## Test Signals

Tests should cover mode-0 flash transactions, command/address write followed by read, TX-only transfers over 36 bytes, reads over 32 bytes, native CS0/CS1 polarity behavior, GPIO chip select fallback, divider bounds for max and minimum speeds, reset failure, busy timeout, and explicit rejection of full-duplex transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c

## Purpose

`spi-mtk-nor.c` is a MediaTek SPI NOR controller driver focused on SPI-MEM flash operations. It supports optimized memory reads through controller DMA, small generic program/register-style transactions through the PRGDATA/SHIFT register windows, page program using buffered or unbuffered paths, optional IRQ-driven DMA completion, and runtime PM around controller clocks.

## Important APIs, Types, and Functions

`struct mtk_nor_caps` describes SoC DMA address width and an extra dummy bit needed by newer IP. `struct mtk_nor` stores controller, device, MMIO base, coherent bounce buffer, clocks, current SPI frequency, write-buffer state, IRQ/completion state, high-DMA flag, and caps.

Operation selection is driven by `mtk_nor_supports_op()`, `mtk_nor_adjust_op_size()`, `mtk_nor_match_read()`, and `mtk_nor_match_prg()`. Execution helpers include `mtk_nor_cmd_exec()`, `mtk_nor_reset()`, `mtk_nor_set_addr()`, `mtk_nor_setup_bus()`, `mtk_nor_dma_exec()`, `mtk_nor_read_dma()`, `mtk_nor_read_bounce()`, `mtk_nor_read_pio()`, `mtk_nor_pp_buffered()`, `mtk_nor_pp_unbuffered()`, and `mtk_nor_spi_mem_prg()`. The SPI core fallback message path uses `mtk_nor_transfer_one_message()` with a six-byte maximum message size.

## Control Flow

Probe maps the controller, gets required and optional clocks, loads SoC caps, sets the DMA mask, allocates a host controller, allocates an aligned coherent bounce buffer, enables clocks, initializes registers, optionally requests an IRQ, enables runtime PM, and registers the controller.

For SPI-MEM operations, the driver first validates that command bus width is single-bit and that the address/data/dummy combination maps to either optimized read, page program, or small PRG mode. `adjust_op_size` constrains DMA reads to alignment and timeout-safe sizes, constrains page program to 128-byte buffered chunks or one byte for unbuffered writes, and constrains fallback PRG transactions to the small register windows.

`exec_op` sends no-address or nonstandard operations through `mtk_nor_spi_mem_prg()`. Data-out with 3- or 4-byte addresses uses buffered page program for 128 bytes or unbuffered single-byte write. Matching reads set the address and bus mode, use PIO for one byte, otherwise use DMA directly into the caller buffer or through the coherent bounce buffer if the destination is not 16-byte aligned. DMA read failures trigger a controller reset and one retry.

## State and Persistence Behavior

Runtime state includes the cached write-buffer enable state (`wbuf_en`), high-DMA support, optional IRQ completion, and the coherent bounce buffer. Register state includes bus-width mode, four-byte address mode, write-buffer enable, write-enable/status-poll disable bits, and DMA address registers. Runtime PM disables and re-enables all clocks but does not persist user data.

Persistent effects occur on the external NOR flash when upper layers issue program/erase/status commands; the driver itself stores no file-backed state.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, SPI controller registration, platform devices, OF compatible strings `mediatek,mt8173-nor`, `mt8186-nor`, and `mt8192-nor`, DMA mapping/coherent allocation, interrupts, completions, clocks, and runtime/system PM. It is intended to be consumed by SPI NOR and MTD layers through `spi_mem`.

## Risks and Edge Cases

The coherent bounce buffer allocation is checked for 16-byte virtual alignment even though DMA alignment also matters to hardware; the allocation size includes extra alignment slack but the code does not adjust to an aligned offset. `mtk_nor_pp_buffered()` writes data four bytes at a time and assumes adjusted page-program lengths are compatible with that loop. DMA timeout calculations depend on `spi_freq`; incorrect clock rates can produce too-short polling timeouts. IRQ is optional, so both interrupt and polling completion paths need coverage.

The fallback message path has a small maximum size and manually packs all transfer bytes into PRGDATA in reverse register order; it is useful for simple SPI messages but not a full general-purpose controller.

## Test Signals

Validation should cover supported read opcodes and dummy cycles, single/dual/quad reads, 3-byte and 4-byte addresses, one-byte PIO reads, aligned DMA reads, unaligned bounce reads, DMA retry after reset, 128-byte buffered page program, one-byte unbuffered writes, small command/status reads through PRG mode, IRQ and polling completion paths, runtime suspend/resume, and probe failures for DMA mask, clocks, IRQ request, and controller registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c

## Purpose

`spi-mtk-snfi.c` drives the SPI-NAND mode of the MediaTek NAND Flash Interface. It is a SPI-MEM controller with a pipelined on-host NAND ECC engine. The core job is translating Linux SPI-NAND page-plus-OOB expectations into the controller's sector/FDM/ECC interleaved layout, including SoC-specific bad-block-marker swaps and ECC/FDM handling.

## Important APIs, Types, and Functions

`struct mtk_snand_caps` captures sector size, maximum sectors, FDM and FDM-ECC sizes, FIFO size, BBM swap behavior, empty-page checking, status masks, and supported spare sizes. `struct mtk_snand_conf` caches selected page and OOB format. `struct mtk_snand` stores the SPI controller, clocks, NFI MMIO base, IRQ completion, caps, ECC engine/configuration, current page format, ECC stats, autofmt flag, and bounce buffer.

Core hardware helpers are `mtk_nfi_reset()`, `mtk_snand_mac_reset()`, `mtk_snand_mac_trigger()`, `mtk_snand_mac_io()`, and `mtk_snand_setup_pagefmt()`. ECC integration uses `mtk_snand_ecc_init_ctx()`, `mtk_snand_ecc_prepare_io_req()`, `mtk_snand_ecc_finish_io_req()`, and cleanup. Page operations are implemented by `mtk_snand_read_page_cache()` and `mtk_snand_write_page_cache()`. Data layout helpers include `mtk_snand_read_fdm()`, `mtk_snand_write_fdm()`, `mtk_snand_bm_swap()`, and `mtk_snand_fdm_bm_swap()`.

## Control Flow

Probe matches SoC caps, gets the external MediaTek ECC engine, maps NFI registers, enables clocks, requests the IRQ, sets a 32-bit DMA mask, switches the block to SNFI mode, applies optional sample/latch delays, sets an initial 2 KiB plus 64-byte page format, registers the pipelined ECC engine, and registers a single-chipselect SPI-MEM controller.

`supports_op` accepts standard one-byte command SPI-MEM operations, optimized page-cache operations with two-byte addresses, and smaller MAC/GPRAM operations. `adjust_op_size` keeps page operations within the configured sector-plus-spare size when not in ECC autofmt mode and keeps generic operations within the 0xa0-byte GPRAM window.

ECC prepare configures page format, sets `autofmt`, and stores ECC config. A matching page read resets MAC/NFI, programs read command/address/dummy/mode, maps DMA memory, enables decode ECC when requested, starts custom-read DMA, waits for IRQ and counters, gathers ECC stats, reads FDM registers, applies BBM swaps, handles empty-page status, and copies deinterleaved data/OOB to the caller. Page write mirrors this path: it copies caller data into the bounce buffer, performs BBM/FDM swaps, writes FDM registers, enables encode ECC when requested, starts program-load DMA, waits for completion and sector count, then disables ECC and custom mode.

Non-page operations go through MAC mode by writing command/address/dummy/data into SNF GPRAM, triggering the MAC engine, and reading back response bytes.

## State and Persistence Behavior

`nfi_cfg` persists the current hardware page format and avoids unnecessary reprogramming. `autofmt`, `ecc_cfg`, and `ecc_stats` are scoped to NAND page I/O request windows. The bounce buffer persists and is resized to fit page plus OOB. No host files are persisted; writes and erases affect the attached SPI-NAND flash, and ECC configuration influences how data and OOB are encoded on media.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, MTD NAND, the NAND ECC engine API, MediaTek ECC helpers, platform/OF matching, clocks, interrupts, DMA mapping, and Linux MTD OOB layout. It advertises SPI dual/quad modes and SPI-MEM ECC capability.

## Risks and Edge Cases

The layout transformation is subtle: autofmt DMA omits ECC parity and places FDM in registers, while Linux expects contiguous page then OOB. Bad-block-marker swaps differ by SoC, so regressions can make flash incompatible with BootROM. ECC parity is intentionally inaccessible, so raw parity inspection is not supported. Page offset masking derives from `fls(page_size + oob_size)`; unexpected memory geometries should be tested carefully.

DMA cleanup paths split normal and error unmapping; missed error handling can leak mappings or copy stale data. The code assumes page operations between ECC prepare and finish are true page cache operations.

## Test Signals

Tests should cover mt7622, mt7629, and mt7986 caps; page sizes 512 through 16 KiB where supported; OOB/spare-size selection; ECC strength negotiation; raw and ECC reads/writes; empty-page reads; FDM free OOB layout; BBM swap behavior; dual/quad read and program-load templates; generic MAC commands; DMA timeout/error paths; IRQ filtering; ECC corrected/failed stats propagation; and remove/probe cleanup of ECC engine, bounce buffer, clocks, and IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c

## Purpose

`spi-mux.c` implements a generic SPI bus multiplexer. It binds as a child SPI device on a parent controller and registers a new downstream `spi_controller`; child devices on the downstream bus use mux states as logical chip selects, allowing boards to expand available SPI chip selects with a mux controller.

## Important APIs, Types, and Functions

`struct spi_mux_priv` stores the parent `spi_device`, current selected mux state, saved child message callback/context/device pointers, and the `mux_control`. `spi_mux_select()` selects the mux state, mirrors the child device's mode, speed, and bits-per-word into the parent SPI device, and calls `spi_setup()` on the parent. `spi_mux_setup()` defers meaningful setup to transfer time. `spi_mux_transfer_one_message()` rewrites the child message to target the parent device and submits it with `spi_async()`. `spi_mux_complete_cb()` restores message fields, finalizes the child controller message, and deselects the mux.

Probe allocates a controller, raises lockdep subclasses because parent bus locks nest under child bus locks, obtains the mux control, copies capability fields from the parent controller, sets `must_async` and `defer_optimize_message`, uses `mux_control_states()` as chip-select count, and registers the downstream controller.

## Control Flow

When a child message is submitted, the driver selects the mux state matching the child's chip select. If the selected child differs from the current state, parent SPI setup is updated to match the child's speed/mode/word size. The message callback, context, and `spi` pointer are saved, then replaced with mux-owned values and the parent device. The parent controller executes the message asynchronously. On completion, the mux callback restores the original child message metadata, finalizes the downstream controller's current message, and deselects the mux.

## State and Persistence Behavior

The only persistent state is `current_cs`, which caches the mux state last programmed, and the saved callback/context/device fields while one message is in flight. No data is persisted across boots or to disk. Mux hardware state persists only until deselected or reselected by later operations.

## Dependencies and Integration Points

The driver depends on the SPI core, mux consumer API, lockdep, device tree compatible `spi-mux`, and the parent SPI controller. It intentionally mirrors parent capabilities instead of implementing transfer logic itself.

## Risks and Edge Cases

Message field rewriting is delicate: callback, context, and `m->spi` must be restored exactly once on completion. If `spi_async()` fails after fields are replaced, the current code returns the error without restoring fields or deselecting the mux, which is a risk path to review. The comment states selection should not happen while the parent is already transferring; nested or shared parent use depends on SPI core locking and `must_async`.

The parent device is repeatedly reconfigured to child settings, so child configurations that the parent accepts in isolation but not across rapid switching need coverage.

## Test Signals

Tests should cover multiple downstream chip selects, repeated transfers to the same CS, switching between children with different modes/speeds/bits-per-word, parent `spi_async()` failure, mux select/deselect failure injection, lockdep under nested SPI controllers, unregister while transfers are inactive, and child device probing through device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c

## Purpose

`spi-mxic.c` is the Macronix MX25F0A SPI controller driver. It supports ordinary SPI transfers, SPI-MEM operations, direct-mapped linear read/write windows, octal/DDR features, swap16 data handling, per-operation frequency changes, and optional pipelined NAND ECC integration through the Macronix ECC engine.

## Important APIs, Types, and Functions

`struct mxic_spi` stores device, clocks, register base, current speed, optional linear mapping, and ECC wrapper state. Clock helpers are `mxic_spi_clk_enable()`, `mxic_spi_clk_disable()`, `mxic_spi_clk_setup()`, and `mxic_spi_set_freq()`. Hardware setup is performed by `mxic_spi_hw_init()`, while operation encoding uses `mxic_spi_prep_hc_cfg()` and `mxic_spi_mem_prep_op_cfg()`.

Manual FIFO exchange is in `mxic_spi_data_xfer()`. SPI-MEM callbacks are `mxic_spi_mem_supports_op()`, `mxic_spi_mem_exec_op()`, `mxic_spi_mem_dirmap_create()`, `mxic_spi_mem_dirmap_read()`, and `mxic_spi_mem_dirmap_write()`. Standard SPI callbacks are `mxic_spi_set_cs()` and `mxic_spi_transfer_one()`. ECC wrappers register a pipelined on-host engine using `mxic_spi_mem_ecc_probe()` and delegate NAND ECC operations to `mxic_ecc_get_pipelined_ops()`.

## Control Flow

Probe obtains clocks and MMIO resources, maps an optional direct-map resource, enables runtime PM, fills controller callbacks and mode bits, initializes the hardware, optionally registers the pipelined ECC engine unless probe defers, and registers the SPI controller.

For ordinary transfers, `transfer_one` sets frequency, derives bus width from device mode and transfer direction, programs the slave control register, exchanges bytes through the TX/RX data registers, and finalizes the transfer.

For SPI-MEM `exec_op`, the driver sets per-operation clock, configures host control for manual chip select, enables the controller, programs the operation descriptor for the selected chip, asserts CS, writes command and address bytes, clocks dummy bytes, transfers data in the requested direction, deasserts CS, and disables the controller. Direct-map reads/writes configure linear-read or linear-write registers, map the requested range into the controller's linear aperture, optionally invoke pipelined ECC processing, otherwise copy to/from IO memory, then disable linear mode and wait for disable status.

## State and Persistence Behavior

`cur_speed_hz` caches clock programming to avoid redundant clock-rate changes. The optional `linear` mapping stores IO and bus addresses for direct-map operations. ECC state records whether a pipelined configuration is active and holds the registered engine. Hardware registers retain mode, linear, interrupt, and host-control settings only while the device is active; runtime suspend disables clocks.

No host persistence is used. External flash state is modified by upper-layer SPI-MEM operations.

## Dependencies and Integration Points

The driver integrates with SPI, SPI-MEM, runtime PM, platform resources named `regs` and optional `dirmap`, clocks `ps_clk`, `send_clk`, and `send_dly_clk`, MTD NAND ECC APIs, and Macronix ECC helpers. It advertises DTR, ECC, swap16, per-op frequency, dual/quad/octal modes, and one chip select.

## Risks and Edge Cases

Direct-map read/write clamps `len` to the linear aperture after programming the requested address and range; callers must handle short returns correctly. `mxic_spi_data_xfer()` polls FIFO bits for every 1-4 byte chunk, so timeout behavior is central. The ordinary transfer path has limited full-duplex support and rejects certain asymmetric dual/quad combinations. ECC registration ignores non-deferral errors and continues without ECC, which is acceptable only if upper layers can operate without it.

Runtime PM enables `auto_runtime_pm`, but hardware initialization is done before registration and clocks must be valid when registers are accessed.

## Test Signals

Tests should include STR and DTR SPI-MEM commands, single/dual/quad/octal widths, command/address/dummy/data combinations, manual CS behavior, direct-map read and write with short aperture clamping, per-op frequency changes, runtime suspend/resume, ECC-pipelined NAND read/write requests, operation timeout injection, and probe paths with absent direct-map resource and deferred ECC engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c

## Purpose

`spi-mxs.c` is the Freescale/NXP MXS SSP-based SPI host driver for i.MX23 and i.MX28. It exposes a half-duplex SPI controller backed by the shared MXS SSP block, using PIO for small transfers and DMAengine with MXS-specific PIO descriptors for larger transfers.

## Important APIs, Types, and Functions

`struct mxs_spi` embeds `struct mxs_ssp`, a completion, and the last requested SCK rate. `mxs_spi_setup_transfer()` programs clock, SSP SPI mode, word length, CPOL/CPHA, and command registers. `mxs_spi_cs_to_reg()` maps chip-select index to SSP control bits. `mxs_ssp_wait()` polls register bits with a 10-second timeout.

Data paths are `mxs_spi_txrx_pio()` and `mxs_spi_txrx_dma()`. DMA completion is signaled by `mxs_ssp_dma_irq_callback()`, while `mxs_ssp_irq_handler()` logs unexpected SSP IRQ state. `mxs_spi_transfer_one()` implements the message loop. Probe allocates the controller, maps MMIO, obtains clock and DMA channel, enables runtime PM, resets the SSP block, and registers the controller. Remove unregisters, disables PM, releases DMA, and drops the controller reference.

## Control Flow

For each message, the driver programs chip-select bits into `HW_SSP_CTRL0` and iterates transfers. Each transfer sets up clock and mode, records effective speed, computes whether CS should deassert at the end using last-transfer and `cs_change` state, then chooses PIO for transfers under 32 bytes and DMA otherwise.

PIO sends or receives one byte at a time by programming transfer count, READ direction, RUN, DATA_XFER, and optionally IGNORE_CRC as a CS-deassert signal. DMA allocates an array of per-segment PIO/scatterlist descriptors, splits vmalloc buffers by page or linear buffers by 0xff00 bytes, maps each segment, queues SSP PIO register writes and data moves to the MXS DMA channel, adds a callback to the last descriptor, starts DMA, waits for completion, and unmaps all mapped segments.

On transfer failure, the SSP block is reset and the message ends with error status. On success, `actual_length` is incremented and the message is finalized.

## State and Persistence Behavior

`spi->sck` caches the requested speed to reduce redundant clock programming. The embedded SSP state holds device, clock, base, DMA channel, and SoC id. Transfer descriptors and mappings are temporary. There is no host persistence; external SPI devices may be modified by writes.

Runtime PM and system sleep move pinctrl states and clock state. The SSP hardware is reset during probe and after failed messages.

## Dependencies and Integration Points

The driver integrates with the SPI core, device tree compatibles `fsl,imx23-spi` and `fsl,imx28-spi`, MXS SSP register definitions, STMP reset helpers, DMAengine, MXS DMA flags, clock framework, pinctrl PM, runtime/system PM, tracepoints, and optional regulator headers inherited from platform context.

## Risks and Edge Cases

The controller is half-duplex; if both TX and RX buffers are present, the code may run TX then RX sequentially for the same transfer rather than true simultaneous exchange. DMA error cleanup uses labels inside an unwind loop and must preserve correct `sg_count` semantics for all partial-queue failures. Vmalloc handling maps one page per segment and depends on `offset_in_page()` plus `PAGE_SIZE` segmentation. Very long fixed 10-second timeouts hide hangs but slow failure recovery.

CS handling uses SSP WAIT_FOR_CMD/WAIT_FOR_IRQ bits in SPI mode, which is hardware-specific and easy to regress when changing control-word setup.

## Test Signals

Tests should cover i.MX23 and i.MX28, all three chip selects, mode 0-3, sub-32-byte PIO TX/RX, DMA TX/RX for linear and vmalloc buffers, segment boundaries at page and 0xff00 sizes, `cs_change` on multi-transfer messages, DMA timeout and descriptor-prep failures, runtime/system suspend-resume, and block reset after failed transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c

## Purpose

`spi-npcm-fiu.c` is the Nuvoton NPCM Flash Interface Unit SPI-MEM controller driver. It supports FIU instances with multiple chip selects, direct memory-mapped reads and writes through reserved flash windows, and UMA register transactions for commands that cannot use direct mapping. It handles both standard FIU and SPIX mode.

## Important APIs, Types, and Functions

`struct npcm_fiu_info` describes FIU instance name, id, maximum mapping size, and chip-select count. `struct fiu_data` groups per-SoC FIU arrays for NPCM7xx and NPCM8xx. `struct npcm_fiu_chip` stores per-CS mapped flash pointer and clock rate. `struct npcm_fiu_spi` stores chips, selected info, cached direct-read op, memory resource, regmap, clock, and SPIX mode flag.

Direct-map helpers are `npcm_fiu_set_drd()`, `npcm_fiu_direct_read()`, `npcm_fiu_direct_write()`, `npcm_fiux_set_direct_rd()`, `npcm_fiux_set_direct_wr()`, and `npcm_fiu_dirmap_create()`. UMA helpers are `npcm_fiu_uma_read()`, `npcm_fiu_uma_write()`, `npcm_fiu_manualwrite()`, `npcm_fiu_read()`, and `npcm_fiu_exec_op()`. `npcm_fiu_setup()` records per-device clock rate and chip-select metadata.

## Control Flow

Probe allocates a SPI controller, reads SoC match data, derives FIU id from the `fiu` OF alias, selects FIU instance limits, maps the control resource through regmap, records optional memory resource, enables the FIU clock, reads SPIX mode, fills SPI-MEM callbacks, and registers the controller with the instance-specific chip-select count.

`dirmap_create` verifies that reserved memory exists and that the operation is suitable for direct mapping. It maps the per-chipselect aperture at `memory.start + max_map_size * cs`, applies an NPCM750 GCR FIU fix or local FIU fix bit, and programs direct read/write configuration. Direct reads either copy from IO memory or byte-read in SPIX mode; direct writes copy to IO memory or byte-write in SPIX mode.

`exec_op` rejects SPIX mode and addresses over four bytes, updates the FIU clock to the selected chip rate, then dispatches to UMA read/write variants. Reads with an address are chunked in 16-byte UMA reads. Writes without data, address-only writes, data-only writes, and address-plus-data writes use different UMA command sequences; manual writes hold software CS across command/address setup and 16-byte data chunks.

## State and Persistence Behavior

Cached direct-read operation fields avoid reprogramming DRD registers when direct-map reads repeat the same opcode/address width/dummy configuration. Per-chip `flash_region_mapped_ptr` persists once a direct-map aperture is mapped. Per-chip `clkrate` is learned from `spi->max_speed_hz` and applied in `exec_op`.

The driver stores no host data persistently. Direct and UMA writes modify attached flash devices.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, platform/OF matching for `nuvoton,npcm750-fiu` and `nuvoton,npcm845-fiu`, regmap MMIO, optional syscon GCR fixups, clock framework, IO memory resources named `control` and optional `memory`, and device-tree aliases.

## Risks and Edge Cases

No `supports_op` callback is provided, so unsupported operations fail from `exec_op` rather than being rejected earlier. UMA read/write data registers are limited to 16 bytes, making chunking essential. `npcm_fiu_read()` subtracts 16 from `currlen` even when the last `readlen` is smaller; the loop still terminates but the bookkeeping is non-intuitive. Direct mapping silently disables itself by setting `nodirmap` when resources or fixups are unavailable.

SPIX mode bypasses UMA `exec_op` entirely and uses byte-wise direct IO, so coverage must include both modes.

## Test Signals

Tests should cover FIU0/FIU1/FIU3/FIUX instance selection, invalid aliases, per-chipselect mapping offsets, direct read opcode/dummy/address-width changes, direct writes in SPIX mode, UMA command-only/address-only/data-only/address-plus-data operations, 16-byte chunk boundaries, clock-rate switching, absent memory resource fallback, NPCM750 GCR fixup absence, and regmap polling timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-fiu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c

## Purpose

`spi-npcm-pspi.c` is the Nuvoton NPCM peripheral SPI controller driver. It implements an interrupt-driven, register-FIFO style SPI host for normal SPI devices, supporting 8- and 16-bit words, modes 0-3, GPIO descriptors for chip select, and reset/clock setup.

## Important APIs, Types, and Functions

`struct npcm_pspi` stores completion, reset control, controller, remaining TX/RX byte counts, MMIO base, cached mode/word/speed parameters, TX/RX pointers, clock, and id. Small helpers enable/disable IRQ bits and the SPI engine. `npcm_pspi_set_mode()`, `npcm_pspi_set_transfer_size()`, and `npcm_pspi_set_baudrate()` program control register fields.

`npcm_pspi_setup_transfer()` caches buffers and transfer parameters, optionally upgrades even-length 8-bit transfers to 16-bit hardware words, and updates hardware only when mode/word/speed changed. `npcm_pspi_send()` and `npcm_pspi_recv()` move one hardware word. `npcm_pspi_handler()` drives the interrupt state machine. `npcm_pspi_transfer_one()` starts the engine and waits for completion. Probe maps registers, enables the clock, gets reset and IRQ, resets hardware, requests IRQ, initializes the controller, and registers it.

## Control Flow

Before transfer, the driver records TX/RX buffers and sets both byte counters to transfer length. It programs SPI mode, transfer size, and divider if cached values differ. Transfer execution reinitializes completion, enables the SPI engine, and waits up to two seconds.

The interrupt handler reads status. For TX transfers, it drains receive-buffer-full by reading dummy data, completes when no TX bytes remain, and sends the next word whenever the controller is not busy. For RX transfers, it reads data when receive-buffer-full is set, completes when RX bytes reach zero, and writes dummy zero bytes when the controller is idle and no TX buffer exists, causing clocks for further RX data. Prepare/unprepare hardware enables or disables read/write interrupts around message processing.

## State and Persistence Behavior

Cached `mode`, `bits_per_word`, `speed_hz`, and `is_save_param` reduce repeated register writes. TX/RX byte counters and buffer pointers are active-transfer state only. The driver has no file persistence; writes affect only external SPI devices.

The hardware is reset at probe and remove. The clock is enabled for the lifetime of the registered controller; no runtime PM path is implemented.

## Dependencies and Integration Points

The driver integrates with SPI core, platform devices, OF compatibles `nuvoton,npcm750-pspi` and `nuvoton,npcm845-pspi`, clock framework, reset framework, MMIO helpers, interrupts, completions, and GPIO descriptor chip selects.

## Risks and Edge Cases

`npcm_pspi_setup_transfer()` mutates `t->bits_per_word` from 8 to 16 for even-length transfers, which is efficient but surprising and assumes byte order handling remains correct. The baud-rate divider is not clamped in `npcm_pspi_set_baudrate()` even though min/max divider constants exist; the SPI core's min/max speed fields should prevent invalid rates. The switch in `npcm_pspi_set_mode()` has no default assignment, relying on `SPI_MODE_X_MASK` to produce one of four cases.

Completion depends entirely on interrupts; lost interrupts lead to a two-second timeout and engine disable.

## Test Signals

Tests should cover modes 0-3, 8-bit odd length, 8-bit even length upgraded to 16-bit, explicit 16-bit transfers, TX-only, RX-only dummy-clock generation, timeout when IRQ is missing, min/max speed bounds, reset failure, IRQ request failure, remove reset behavior, and repeated transfers that reuse cached mode/speed/word settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c

## Purpose

`spi-nxp-fspi.c` is the NXP FlexSPI controller driver. It exposes a SPI-MEM-only controller for NOR-like memories connected through single, dual, quad, or octal lines. FlexSPI executes operations through runtime-generated LUT sequences, uses IP bus FIFO access for small operations, uses AHB memory mapping for larger reads when safe, supports selected DTR operation, and handles SoC quirks and endianness differences.

## Important APIs, Types, and Functions

`struct nxp_fspi_devtype_data` describes FIFO sizes, AHB buffer size, quirks, LUT count, and register endianness. `struct nxp_fspi` stores controller registers, AHB mapping, physical memory window, clocks, device, completion, devtype data, mutex, selected chip state, flags, prior operation rate, and max output rate.

Register access is wrapped by `fspi_writel()` and `fspi_readl()` for big/little-endian controllers. SPI-MEM callbacks are `nxp_fspi_supports_op()`, `nxp_fspi_adjust_op_size()`, `nxp_fspi_exec_op()`, and `nxp_fspi_get_name()`. Execution helpers include `nxp_fspi_select_mem()`, `nxp_fspi_prepare_lut()`, `nxp_fspi_fill_txfifo()`, `nxp_fspi_read_rxfifo()`, `nxp_fspi_do_op()`, `nxp_fspi_read_ahb()`, and `nxp_fspi_invalid()`. Setup and PM helpers include `nxp_fspi_default_setup()`, `nxp_fspi_select_rx_sample_clk_source()`, `nxp_fspi_dll_calibration()`, `nxp_fspi_dll_override()`, runtime suspend/resume, and system suspend.

## Control Flow

Probe allocates the controller, loads devtype data, maps register and memory resources, obtains clocks for OF systems, enables runtime PM, powers the device, clears stale interrupts, runs default setup, powers down, requests IRQ, initializes a mutex, assigns SPI-MEM ops/caps, registers cleanup, and registers the controller. ACPI systems skip Linux clock operations.

`supports_op` validates bus widths, address size, address range within the memory-mapped aperture, dummy cycles, and FIFO/AHB size/alignment constraints. `adjust_op_size` constrains writes to TX FIFO size, reads to AHB buffer size, aligns reads that exceed RX FIFO minus four bytes, and further limits reads on IP-only quirked SoCs.

`exec_op` serializes with a mutex, resumes runtime PM, waits for arbitration idle, selects the target chip and clock mode, writes a LUT sequence for command/address/dummy/data, and chooses AHB or IP execution. Larger reads use `ioremap` of the AHB flash window and `memcpy_fromio()` unless an IP-only quirk is set. Writes preload TX FIFO. IP execution programs IPCR address, sequence id, and data size, triggers the command, waits for interrupt completion, and reads RX FIFO for read operations. Every operation invalidates AHB buffers by software-resetting the controller before autosuspend.

## State and Persistence Behavior

`selected`, `FSPI_DTR_MODE`, and `pre_op_rate` cache chip-select and clock/DTR configuration to avoid redundant reprogramming. `ahb_addr`, `memmap_start`, and `memmap_len` cache the currently mapped AHB window and are replaced when a read falls outside it. `FSPI_NEED_INIT` forces full hardware setup after system suspend.

The driver has no file persistence. Flash contents are changed only through upper-layer SPI-MEM program/erase commands.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, platform/OF/ACPI matching, runtime/system PM, pinctrl PM, clocks, interrupts, completions, mutexes, IO remapping, syscon/regmap for LS1028A erratum detection, SoC matching, and device-tree memory resources `fspi_base` and `fspi_mmap`.

## Risks and Edge Cases

The driver uses the last LUT slot dynamically for every operation; concurrent execution is protected by a mutex and must remain so. AHB reads are invalidated after all operations, but write/erase data coherency still depends on correct reset timing. DTR support is limited to full 8D-8D-8D style operation, and some devtypes disable DTR entirely. Clock switching disables clocks, changes rate, re-enables clocks, and recalibrates DLL above 100 MHz; failures can leave previous selections stale.

`nxp_fspi_cleanup()` calls `pm_runtime_get_sync()` but does not check failure before register access. Probe error paths after runtime PM enable need careful coverage.

## Test Signals

Tests should cover each devtype, little- and big-endian register access where applicable, command/address/dummy/data LUT generation, single/dual/quad/octal widths, DTR enable/disable caps, IP reads and writes at FIFO limits, AHB reads and ioremap window reuse/replacement, IP-only quirk behavior, LS1028A erratum detection, clock-rate switching and DLL paths above/below 100 MHz, runtime autosuspend, system suspend with reinit, IRQ timeout, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c -->
