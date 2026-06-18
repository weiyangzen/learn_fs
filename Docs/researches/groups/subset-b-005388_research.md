# subset-b-005388 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip-sfc.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip-sfc.c

## Purpose

`spi-rockchip-sfc.c` is a Linux `spi-mem` controller driver for the Rockchip Serial Flash Controller. It is specialized for SPI NOR/NAND-style memory transactions rather than generic full-duplex SPI. The driver programs SFC command, address, dummy, data-width, length, chip-select, FIFO, DMA, interrupt, clock, and runtime-PM registers and exposes the controller through `struct spi_controller_mem_ops`.

## Important APIs, Types, and Functions

`struct rockchip_sfc` stores MMIO base, bus/interface clocks, per-chip-select cached speeds, a coherent-ish DMA bounce buffer, a DMA completion, controller version, maximum I/O size, and the registered SPI host. Register helpers include `rockchip_sfc_reset()`, `rockchip_sfc_get_version()`, `rockchip_sfc_clk_set_rate()`, `rockchip_sfc_irq_mask()`, and `rockchip_sfc_init()`.

The transfer path is split into `rockchip_sfc_adjust_op_work()`, `rockchip_sfc_xfer_setup()`, FIFO helpers `rockchip_sfc_write_fifo()` and `rockchip_sfc_read_fifo()`, DMA helpers `rockchip_sfc_fifo_transfer_dma()` and `rockchip_sfc_xfer_data_dma()`, and completion wait `rockchip_sfc_xfer_done()`. The exported memory hooks are `rockchip_sfc_exec_mem_op()` and `rockchip_sfc_adjust_op_size()` in `rockchip_sfc_mem_ops`. Probe/remove and PM are handled by `rockchip_sfc_probe()`, `rockchip_sfc_remove()`, runtime suspend/resume, and system suspend/resume.

## Control Flow

Probe allocates a SPI host, maps registers, gets clocks or ACPI `clock-frequency`, decides whether DMA is enabled from `rockchip,sfc-no-dma`, enables clocks, requests the IRQ, initializes the controller, records hardware version and max I/O size, enables runtime PM, optionally allocates and maps a DMA bounce buffer, then registers the controller. `exec_op` takes a runtime-PM reference, adjusts the interface clock when `per_op_freq` changes, rewrites dummy-without-address operations into address cycles, programs command/address/dummy/data registers, transfers data via DMA for aligned large buffers or PIO FIFO loops otherwise, waits for the controller to go idle, and drops the PM reference.

DMA transfer starts by unmasking the DMA interrupt, writing the bounce-buffer DMA address, and triggering the SFC DMA engine. The IRQ handler clears raw interrupt status and completes `sfc->cp` on `SFC_RISR_DMA`. PIO transfer polls FIFO fill levels before each repeated MMIO read/write. Resume reinitializes the controller after clocks and pinctrl state are restored.

## State and Persistence Behavior

The driver has no file-backed persistence. Runtime state is the controller register image, per-CS speed cache, runtime-PM clock state, DMA buffer mapping, and transfer completion. Persistent external effects are flash-memory operations initiated by upper-layer spi-mem clients; this file only transports those operations.

`rockchip_sfc_adjust_op_size()` clamps each operation to `max_iosize`. Versions 4+ use `SFC_LEN_EXT` and `SFC_LEN_CTRL_TRB_SEL`; older versions encode length in `SFC_CMD`. Version 8 doubles the configured source clock relative to the observed SFC bus rate.

## Dependencies and Integration Points

The driver integrates with Linux platform devices, OF/ACPI properties, clocks, runtime PM, pinctrl sleep/default states, interrupts, DMA mapping, and the `spi-mem` framework. It supports dual/quad TX/RX mode bits, two native chip selects, half-duplex transfers, and per-operation frequency selection. Flash protocol semantics are supplied by spi-mem consumers.

## Risks and Edge Cases

`rockchip_sfc_get_max_iosize()` always returns the version-3 limit even though version-4 constants exist; if newer hardware can safely transfer larger chunks this underuses it, while if version-specific limits differ in the other direction it could be wrong. DMA uses a single bounce buffer allocated with `GFP_DMA32` and writes only the low 32 bits of the DMA address, so the mapping must be 32-bit-addressable. `rockchip_sfc_exec_mem_op()` casts away `const` to adjust the op, which relies on spi-mem callers tolerating mutation. Removal unmaps/frees the DMA buffer unconditionally; this is benign only if the fields are zero/NULL when DMA was disabled. Error paths must keep runtime-PM and clock state balanced after partial probe failures.

## Test Signals

Useful tests include spi-nor probe/read/write/erase on both chip selects, odd-length PIO transfers, aligned and unaligned large reads/writes crossing the DMA threshold, dummy-cycle-only operations, 3-byte and 4-byte addressing, per-op frequency switching, DMA timeout injection, FIFO timeout injection, runtime suspend/resume during idle, and system suspend/resume followed by flash reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip-sfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip.c

## Purpose

`spi-rockchip.c` is a generic Rockchip SPI controller driver supporting host and target modes, PIO and DMA transfer paths, native/GPIO chip selects, active-high support on newer IP, runtime PM, and common SPI modes. It targets the Rockchip DesignWare-like SPI register block used across many Rockchip SoCs.

## Important APIs, Types, and Functions

`struct rockchip_spi` stores clocks, MMIO registers, DMA port addresses, current TX/RX pointers and word counts, DMA state bits, FIFO depth, source frequency, bytes-per-word, RX sample delay, target-abort state, CS-inactive detection support, and the active transfer pointer. Core helpers are `spi_enable_chip()`, `wait_for_tx_idle()`, `get_fifo_len()`, `rockchip_spi_set_cs()`, `rockchip_spi_config()`, `rockchip_spi_prepare_irq()`, `rockchip_spi_prepare_dma()`, `rockchip_spi_isr()`, and DMA callbacks.

The controller hooks are `rockchip_spi_setup()`, `rockchip_spi_transfer_one()`, `rockchip_spi_can_dma()`, `rockchip_spi_target_abort()`, `rockchip_spi_handle_err()`, and `rockchip_spi_max_transfer_size()`. Probe/remove and power management are implemented by `rockchip_spi_probe()`, `rockchip_spi_remove()`, system suspend/resume, and runtime suspend/resume.

## Control Flow

Probe chooses `devm_spi_alloc_target()` when the DT node has `spi-slave`, otherwise `devm_spi_alloc_host()`. It maps registers, enables `apb_pclk` and `spiclk`, requests the IRQ, computes RX sample delay, detects FIFO depth from the version register, enables runtime PM, configures controller capabilities, optionally requests TX/RX DMA channels, derives DMA port addresses, detects newer active-high/CS-inactive behavior, and registers the controller.

Each transfer validates length and buffers, derives one or two bytes per word, decides DMA eligibility from FIFO depth, writes CTRLR0/CTRLR1/RX threshold/DMA thresholds/BAUDR, then starts either PIO IRQ or DMA. PIO preloads TX FIFO, enables RX-full and optional CS-inactive interrupts, and finalizes when RX words drain to zero. DMA starts RX before TX, sets state bits atomically, enables CS-inactive interrupt in target mode when supported, and finalizes from the last DMA callback. Target abort pauses/terminates DMA, drains RX FIFO, adjusts the transfer length to the actual received bytes, disables the chip, and finalizes.

## State and Persistence Behavior

Driver state is volatile: current transfer pointers, residual word counts, DMA state bits, FIFO length, cached clock rate, RX sample delay, and runtime-PM references held while native CS is asserted. There is no persistent storage. Hardware state is reprogrammed for each transfer, and clocks are gated by runtime PM when idle.

## Dependencies and Integration Points

The driver depends on platform/OF, clock, DMAengine, interrupt, scatterlist, pinctrl, PM runtime, and the SPI core. It integrates with GPIO descriptors for external CS lines, native chip-select registers for internal CS, SPI target abort handling, and optional DMA channels named `tx` and `rx`.

## Risks and Edge Cases

Native CS handling takes a runtime-PM reference on assertion and drops it on deassertion; any missed deassertion would keep clocks on. DMA callbacks use atomic state to wait for both directions, so callback ordering and abort races are important. Target abort depends on DMA residue being meaningful and on the active `rs->xfer` pointer remaining valid. Zero-length transfers are finalized manually because hardware will not interrupt. Transfer length is capped at `0xffff` because `0x10000` can hang the controller. Active-high native CS is rejected unless the IP version advertises support.

## Test Signals

Exercise PIO and DMA thresholds, 4/8/16-bit words, TX-only/RX-only/full-duplex transfers, target mode with CS-inactive abort, GPIO and native chip selects, active-high rejection/acceptance, RX sample delay DT settings, DMA callback order, `handle_err()` during active DMA, runtime suspend around CS assertion, and suspend/resume with queued transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rpc-if.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rpc-if.c

## Purpose

`spi-rpc-if.c` adapts the Renesas RPC-IF memory controller core to the Linux `spi-mem` API. It does not implement low-level register access itself; instead it translates `spi_mem_op` and direct-map requests into `struct rpcif_op` operations and delegates hardware work to `memory/renesas-rpc-if.h` helpers.

## Important APIs, Types, and Functions

`rpcif_spi_mem_prepare()` is the central translator from `struct spi_mem_op` to RPC-IF command, address, dummy, and data fields. `rpcif_spi_mem_supports_op()` filters operations through default spi-mem support plus RPC-IF limits of <=4-bit bus widths and <=4 address bytes. Direct-map hooks are `rpcif_spi_mem_dirmap_create()`, `rpcif_spi_mem_dirmap_read()`, and `xspi_spi_mem_dirmap_write()`. Manual operations use `rpcif_spi_mem_exec_op()`.

Probe/remove and PM hooks are `rpcif_spi_probe()`, `rpcif_spi_remove()`, `rpcif_spi_suspend()`, and `rpcif_spi_resume()`. The registered `spi_controller_mem_ops` exposes supports-op, exec-op, dirmap-create, dirmap-read, and dirmap-write.

## Control Flow

Probe allocates a SPI host with embedded `struct rpcif`, initializes RPC-IF software state from the parent device, points the SPI controller OF node at the parent, enables runtime PM on `rpc->dev`, declares one chip select and half-duplex 8-bit SPI with dual/quad mode bits, initializes hardware in SPI mode, and registers the controller. `exec_op` prepares the operation and calls `rpcif_manual_xfer()`. Direct-map reads/writes verify that offset plus length stays within 32-bit RPC address space, prepare the template with adjusted offsets/lengths, then call `rpcif_dirmap_read()` or `xspi_dirmap_write()`.

## State and Persistence Behavior

This file keeps little state of its own. `struct rpcif` owned by the common RPC-IF layer stores the device, direct-map capability, XSPI capability, and hardware state. Persistent effects are flash-memory reads/writes/erases performed by spi-mem clients; the adapter has no filesystem persistence.

## Dependencies and Integration Points

The driver is tightly coupled to the Renesas RPC-IF core API: `rpcif_sw_init()`, `rpcif_hw_init()`, `rpcif_prepare()`, `rpcif_manual_xfer()`, `rpcif_dirmap_read()`, and `xspi_dirmap_write()`. It integrates with platform devices by using the parent hardware device as the real RPC-IF device and registers a child SPI controller named `rpc-if-spi`.

## Risks and Edge Cases

Address-range checks reject direct-map accesses beyond `U32_MAX`, but manual `exec_op` does not perform the same explicit bound check in this file. Direct-map writes require `rpc->xspi`; non-XSPI hardware only supports direct-map reads. The resume path calls `rpcif_hw_init(dev, false)` using the SPI device pointer rather than `rpc->dev`; correctness depends on the PM callback device matching what the RPC-IF core expects. Operation support is deliberately conservative: octal or >4-byte-address operations are rejected here.

## Test Signals

Test normal spi-nor probe, manual register reads/writes, direct-map reads, XSPI direct-map writes, operations at the 32-bit address boundary, dual/quad bus-width combinations, suspend/resume reinitialization, and absence of direct-map support when `rpc->dirmap` or `rpc->xspi` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rpc-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rspi.c

## Purpose

`spi-rspi.c` is the Renesas RSPI/QSPI controller driver for legacy SH RSPI, RZ RSPI, and R-Car Gen2 QSPI variants. It handles register-layout differences through `struct spi_ops`, supports PIO and optional DMA, can use multiplexed or split RX/TX IRQs, and exposes dual/quad transfer modes for QSPI.

## Important APIs, Types, and Functions

`struct rspi_data` stores MMIO base, current speed, controller and platform device, waitqueue, lock for `RSPI_SSLP`, clock, cached command/status/pin-control fields, IRQ numbers, variant ops, DMA completion flag, and byte-access mode. `struct spi_ops` supplies variant-specific configuration and transfer methods plus clock divisors, flags, FIFO size, and native-SS count.

Configuration helpers include `rspi_set_rate()`, `rspi_set_config_register()`, `rspi_rz_set_config_register()`, `qspi_set_config_register()`, and `qspi_setup_sequencer()`. Transfer helpers include interrupt waits, byte PIO, `rspi_dma_transfer()`, RSPI/RZ/QSPI transfer functions, and QSPI trigger programming. Lifecycle code includes DT parsing, reset control deassert/assert action, IRQ setup, DMA channel setup, probe/remove, and PM suspend/resume.

## Control Flow

Probe selects variant ops from OF or platform id, parses chip-select count and optional reset, maps registers, gets the clock, enables runtime PM, initializes waitqueue/lock, sets SPI controller mode bits and speed bounds, requests either a mux IRQ or separate RX/TX IRQs, optionally requests DMA channels, and registers the controller.

For each message, `rspi_prepare_message()` selects the minimum transfer speed, builds `spcmd` from SPI mode/CS/bit order, configures polarity through `RSPI_SSLP`, programs variant configuration registers, optionally programs the QSPI sequencer for multiple single/dual/quad modes, and enables the SPI function. Transfer uses DMA when available and length exceeds variant FIFO size; `-EAGAIN` falls back to PIO. PIO waits for TX empty and RX full via IRQ-backed waitqueues. QSPI reads and writes program FIFO trigger thresholds and sequence modes. Unprepare disables the SPI function and resets the sequencer.

## State and Persistence Behavior

State is runtime-only: current speed, `spcmd`, `spsr`, `sppcr`, IRQ wait state, DMA completion flag, byte-access selection, and SSL polarity. No persistent storage is used. Reset controls are deasserted during probe and asserted automatically by devm action on teardown when present.

## Dependencies and Integration Points

The file depends on platform/OF, clocks, reset controls, PM runtime, DMAengine, SH DMA compatibility filters, waitqueues, spinlocks, interrupts, and SPI core message hooks. It supports `renesas,rspi`, `renesas,rspi-rz`, and `renesas,qspi` compatibles and legacy `"rspi"` platform IDs.

## Risks and Edge Cases

DMA temporarily disables the normal RX/TX IRQ lines because hardware needs SPxIE bits set for DMA; IRQ balance must be restored on every failure path. `rspi_wait_for_interrupt()` uses cached `rspi->spsr` updated by IRQ handlers, so lost interrupts cause HZ timeouts. `qspi_setup_sequencer()` supports only four distinct mode runs per message. Clock calculations round divisors and then overwrite `speed_hz` with the effective value; boundary speeds need validation. PIO transfer ignores the return from the final `rspi_wait_for_tx_empty()` in `rspi_common_transfer()`.

## Test Signals

Run RSPI SH, RSPI RZ, and QSPI variants with PIO and DMA, mux and split IRQs, active-high CS through native and GPIO CS, loopback, dual/quad QSPI read/write sequences, more-than-four QSPI mode changes, DMA fallback, timeout injection on TX/RX waits, reset-control probe failures, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2h-rspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2h-rspi.c

## Purpose

`spi-rzv2h-rspi.c` is a newer Renesas RSPI controller driver for RZ/V2H(P), RZ/G3L/G3E, RZ/T2H, and RZ/N2H-style hardware. It supports host-mode SPI with 4 to 32 bits per word, PIO and DMA, multiple clock-source selection algorithms, hardware resets, and four chip selects.

## Important APIs, Types, and Functions

`struct rzv2h_rspi_info` describes SoC-specific clock search functions, TCLK name, FIFO size, and clock count. `struct rzv2h_rspi_priv` stores the SPI controller, matched info, MMIO base, TCLK/PCLK, waitqueue, bytes-per-word, RX IRQ, cached requested/effective frequency, selected SPR/BRDV divisors, PCLK use flag, and DMA completion flag.

Important functions include register RMW helpers, FIFO clear and IRQ clear helpers, `rzv2h_rx_irq_handler()`, PIO send/receive helpers, `rzv2h_rspi_transfer_dma()`, `rzv2h_rspi_transfer_one()`, clock calculators `rzv2h_rspi_find_rate_fixed()` and `rzv2h_rspi_find_rate_variable()`, `rzv2h_rspi_setup_clock()`, message prepare/unprepare, and probe.

## Control Flow

Probe allocates a host controller, maps registers, gets all clocks and identifies TCLK plus optional PCLK by name, deasserts `presetn` and `tresetn`, requests the RX IRQ, declares mode and bits-per-word capabilities, computes minimum speed from the rounded TCLK, optionally requests DMA channels, and registers the controller.

`prepare_message()` disables SPE before changing configuration, scans message transfers for the minimum speed and bits-per-word, computes `bytes_per_word`, recalculates divisors only when requested speed changes, writes SPBR, SPCR, SPPCR, SPCMD, SSLP, and FIFO thresholds, clears FIFOs, then enables SPE. `transfer_one()` sets the effective speed, computes word count, uses DMA when the SPI core mapped the transfer for DMA, otherwise loops through PIO send/receive with IRQ waits, clears IRQ state, and requests a PIO retry when DMA setup returns `-EAGAIN`. `unprepare_message()` disables SPE.

## State and Persistence Behavior

State is volatile: selected clock source/rate/divisors, cached last requested speed, interrupt status, DMA completion, and bytes-per-word. The reset lines and clocks are device resources. There is no persistent host-side storage; persistent effects belong to attached SPI devices.

## Dependencies and Integration Points

The driver integrates with OF match data, clock bulk APIs, reset controls, DMAengine, waitqueues, interrupts, and SPI core DMA mapping. SoC-specific match data selects fixed or variable TCLK/PCLK search behavior and FIFO thresholds.

## Risks and Edge Cases

`prepare_message()` derives `bits_per_word` from the last transfer examined; mixed bits-per-word messages may not be represented correctly. The generated `rzv2h_rspi_rx_u8()` helper uses `readl` for an 8-bit destination, which is suspicious even if the register tolerates 32-bit reads. DMA requires both TX and RX channels and always prepares both directions, matching the controller's `MUST_RX|MUST_TX` flags. PIO waits rely on RX IRQ setting `rspi->status`; stale status is cleared around transfers but IRQ loss produces HZ timeouts. Fixed-rate search rejects SPR=0/BRDV=0 due to hardware restrictions.

## Test Signals

Test all matched SoCs, fixed and variable clock selection, PCLK fallback, speed-boundary requests around 50 MHz and prohibited divisors, 4/8/16/24/32-bit words, mixed transfer messages, PIO vs DMA fallback, missing one DMA channel, RX IRQ timeout, reset acquisition failures, active-high CS, loopback, and transfer after repeated prepare/unprepare cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2h-rspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2m-csi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2m-csi.c

## Purpose

`spi-rzv2m-csi.c` is a Renesas RZ/V2M Clocked Serial Interface driver exposing CSI as a SPI controller. It supports host and target modes, 8- and 16-bit words, interrupt-driven PIO transfers, optional SS pin handling in target mode, software reset, and CSI clock divisor programming.

## Important APIs, Types, and Functions

`struct rzv2m_csi_priv` holds MMIO base, CSI and peripheral clocks, device/controller pointers, active TX/RX buffers, transfer counters, bytes-per-word, waitqueue, error/status bits, target-abort flag, and SS-pin policy. Register helpers include `rzv2m_csi_reg_write_bit()`, `rzv2m_csi_sw_reset()`, and `rzv2m_csi_start_stop_operation()`.

Transfer functions include FIFO fill/read/empty helpers, current chunk calculation, RX trigger setup, IRQ enable/disable/clear helpers, wait helpers, `rzv2m_csi_irq_handler()`, clock and operating-mode setup, device `setup()`, `rzv2m_csi_pio_transfer()`, `rzv2m_csi_transfer_one()`, and `rzv2m_csi_target_abort()`.

## Control Flow

Probe chooses host or target allocation based on `spi-slave`, decides whether to use the SS pin for target mode from `renesas,csi-no-ss`, maps registers, gets IRQ, clocks, and shared reset, initializes the waitqueue, assigns SPI hooks, requests IRQ, deasserts reset without asserting it for shared-reset safety, puts the IP into software reset, enables `csiclk`, and registers the controller.

Device setup deasserts reset, writes base mode, programs CPOL/CPHA, bit order, host/target role, SS polarity/enable, performs a software reset pulse, then briefly enables/disables communication so the clock line settles. Each transfer records buffers/length, programs transmit-receive or receive-only mode and word length, sets host clock divisor, then runs chunked PIO. The PIO loop clears FIFOs/status, enables RX triggers and error IRQs, computes a power-of-two chunk no larger than FIFO capacity, fills TX FIFO or dummy clocks, starts operation, waits for RX trigger or target abort, stops in host mode, drains/copies RX FIFO, and repeats until done.

## State and Persistence Behavior

All state is runtime-only: buffer pointers, bytes sent/received, current chunk sizing, error bits, IRQ status, target abort flag, and clock divisor. The driver has no persistence. Because reset is shared with hardware outside Linux control, probe only deasserts it and later uses CSI software reset for local cleanup.

## Dependencies and Integration Points

The driver uses platform/OF, clocks, reset controls, waitqueues, interrupts, polling helpers, and SPI core host/target APIs. It uses GPIO descriptors through the SPI core and exposes active-high CS support. It does not use DMA.

## Risks and Edge Cases

`rzv2m_csi_calc_current_transfer()` rounds chunk size down to a power of two; zero-length or badly aligned lengths would be problematic, though normal SPI transfers have positive lengths and supported 8/16-bit words. Target-mode waits are interruptible and return `-EINTR` on abort. FIFO level checks are strict; unexpected hardware levels produce `-EIO`. `rzv2m_csi_setup_clock()` may change `csiclk` up or down to satisfy the PCLK/2 restriction, so shared clock consumers need consideration. Only `csiclk` is explicitly enabled, while `pclk` is used for rate decisions after acquisition.

## Test Signals

Test host and target modes, with and without SS pin, 8- and 16-bit transfers, RX-only and TX/RX transfers, non-FIFO-multiple lengths, overflow/underrun IRQ injection, target abort during wait, clock requests above 8 MHz and near divisor limits, setup polarity/phase combinations, shared-reset behavior, and remove after active/failed transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2m-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-s3c64xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-s3c64xx.c

## Purpose

`spi-s3c64xx.c` is the Samsung S3C64xx/Exynos/FSD/GS101 SPI controller driver. It supports many SoC variants through port-configuration tables, native or automatic chip select, GPIO descriptors, PIO, IRQ-assisted PIO, DMA, runtime PM, clock/prescaler programming, loopback on capable variants, and per-target feedback delay.

## Important APIs, Types, and Functions

`struct s3c64xx_spi_port_config` describes FIFO masks/depth, TX-done bit, clock divider, quirks, high-speed mode, CMU clocking, optional IO clock, loopback, and 32-bit-only MMIO. `struct s3c64xx_spi_driver_data` stores MMIO/clocks/platform/controller pointers, platform info, spinlock, register bus address, completion, state flags, current mode/bits/speed, DMA channel descriptors, port config, port id, FIFO depth, and FIFO masks.

Core functions include `s3c64xx_flush_fifo()`, DMA callback/preparation, `s3c64xx_spi_set_cs()`, transfer-hardware prepare/unprepare, `s3c64xx_spi_can_dma()`, width-specific FIFO I/O helpers, `s3c64xx_enable_datapath()`, DMA and PIO wait functions, `s3c64xx_spi_config()`, `s3c64xx_spi_prepare_message()`, `s3c64xx_spi_transfer_one()`, target controller-data parsing, setup/cleanup, IRQ handling, hardware init, DT parsing, probe/remove, and PM hooks.

## Control Flow

Probe obtains platform/DT controller info, IRQ, host allocation, SoC port config, port id, FIFO depth/masks, DMA directions, SPI hooks/capabilities, MMIO resource, optional GPIO config, clocks, runtime PM, initial hardware state, spinlock/completion, IRQ, error interrupts, then registers the controller. DMA channels are requested during `prepare_transfer_hardware()` unless the DT lacks `dmas`, in which case polling is used.

Setup parses optional per-target `controller-data` and feedback delay, clamps the requested max speed to what the clock/prescaler can provide, stores controller data, and leaves CS inactive. `transfer_one()` reconfigures hardware if speed or bits-per-word changed, chooses DMA for transfers at least FIFO-sized when channels exist, otherwise slices large polling transfers into `fifo_len - 1` pieces, optionally enables RX FIFO-ready IRQ for larger PIO transfers, asserts CS, enables TX/RX datapaths and DMA or writes FIFO data, waits for DMA completion or PIO FIFO fill, handles errors and DMA termination, flushes FIFO, advances sliced buffers, restores original transfer fields, and returns status.

## State and Persistence Behavior

State is volatile: current speed/mode/bpw cache, busy flags, completions, DMA channels/cookies, feedback-delay controller data, FIFO masks/depth, and clock runtime state. Persistent effects are only on attached SPI devices. Runtime resume reinitializes hardware and re-enables error interrupts.

## Dependencies and Integration Points

The driver integrates with Samsung platform data and OF compatibles, clock framework, runtime PM, DMAengine, interrupts, SPI core, GPIO descriptors, and optional SoC-specific GPIO setup callbacks. The variant table maps many compatibles including S3C6410, S5PV210, Exynos generations, Tesla FSD, and Google GS101.

## Risks and Edge Cases

Transfer slicing mutates `xfer->tx_buf`, `rx_buf`, and `len` and restores them at the end; early returns must preserve restoration. DMA TX completion only means FIFO fill, so TX-only DMA requires an extra TX-done poll. PIO receive loops depend on FIFO-level masks and can misbehave if DT FIFO depth or deprecated masks are wrong. Controller-data is allocated in setup for DT devices and freed in cleanup; repeated setup paths must avoid leaks. Polling mode is selected by absence of `dmas`, so malformed DT can silently change behavior. SoCs with 32-bit-only MMIO need the custom 8/16-bit write helpers.

## Test Signals

Test every major port config, FIFO depths 64/128/256, polling/IRQ-assisted PIO/DMA, TX-only/RX-only/full-duplex, 8/16/32-bit words, loopback-capable variants, auto-CS and manual-CS quirks, feedback delay parsing, DMA timeout and residue logging, speed clamping with CMU and prescaler paths, runtime suspend/resume, and DT without `dmas`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sc18is602.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sc18is602.c

## Purpose

`spi-sc18is602.c` is an SPI host driver for NXP SC18IS602/602B/603 I2C-to-SPI bridge chips. It registers a SPI controller behind an I2C client and translates each SPI message into one or more I2C command/data transactions.

## Important APIs, Types, and Functions

`struct sc18is602` stores the SPI host, device, cached control byte, oscillator frequency, selected SPI speed, I2C client, chip id, a 201-byte command/data buffer, queued transmit length, receive index, and optional reset GPIO. `sc18is602_wait_ready()` polls the bridge by trying an I2C read after a transfer-time-based sleep. `sc18is602_setup_transfer()` encodes CPHA/CPOL/LSB-first and selects one of four clock divisors. `sc18is602_txrx()` coalesces SPI transfers into bridge-sized I2C messages and performs readback when needed.

SPI hooks are `sc18is602_transfer_one()` as `transfer_one_message`, `sc18is602_setup()`, and `sc18is602_max_transfer_size()`. Probe validates I2C functionality, resets the bridge, determines chip-select count and clock, assigns SPI capabilities, and registers the controller.

## Control Flow

On each SPI message, `transfer_one_message()` resets the queued length, iterates transfers, checks aggregate buffer size, programs bridge control if mode/speed changed, decides whether this transfer must flush based on `cs_change` or message end, and calls `sc18is602_txrx()` for nonzero lengths. TX-only transfers are buffered until a read, CS change, or message end because one I2C message corresponds to one complete SPI CS assertion. RX-only transfers append dummy bytes and force a bridge transaction, then read back enough bytes to copy the RX segment.

## State and Persistence Behavior

The driver caches only the bridge control byte, selected speed, transfer staging buffer, and optional reset GPIO state. There is no persistent storage. The bridge's own mode register persists until changed or reset, so redundant control writes are skipped.

## Dependencies and Integration Points

The driver depends on I2C master transfers, SMBus byte-data write, optional platform data for SC18IS603 clock frequency, firmware property `clock-frequency`, optional reset GPIO, and SPI core message handling. It exposes 8-bit words, CPHA/CPOL/LSB-first, four chip selects for SC18IS602/602B, and two for SC18IS603.

## Risks and Edge Cases

Maximum message staging is 200 payload bytes plus the CS command byte. `sc18is602_check_transfer()` rejects only the current staged aggregate; clients must respect max message size. Readiness polling treats any successful one-byte I2C receive as ready and retries only ten times. Timing is based on selected SPI speed, so wrong clock-frequency data can make waits too short. SC18IS602 rejects CS2 explicitly despite advertising four chip selects for the family. Coalescing behavior means `cs_change` boundaries are semantically important.

## Test Signals

Test all chip ids, reset GPIO, clock-frequency override for SC18IS603, all four mode combinations, LSB-first, all divisor ranges, TX-only coalescing, RX-only dummy writes, full-duplex readback, `cs_change` flushing, buffer-limit rejection, I2C short write/read, and bridge-not-ready timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sc18is602.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sg2044-nor.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sg2044-nor.c

## Purpose

`spi-sg2044-nor.c` is a Sophgo SG2044/SG2042 SPI NOR flash memory-controller driver using the `spi-mem` API. It implements command/register operations and memory reads/writes through a small FIFO, chunking reads at 64 KiB, and selecting SoC-specific FIFO interrupt behavior.

## Important APIs, Types, and Functions

`struct sg204x_spifmc_chip_info` records whether the optional `SPIFMC_OPT` register exists and which read FIFO trigger level to use. `struct sg2044_spifmc` stores the SPI controller, MMIO base, device, mutex, clock, and chip info. Helpers include interrupt and FIFO-pointer pollers, `sg2044_spifmc_init_reg()`, read/write/command paths, register-operation path, `sg2044_spifmc_exec_op()`, hardware init, and probe.

The spi-mem hook table exposes only `.exec_op`. Match data distinguishes `"sophgo,sg2044-spifmc-nor"` from `"sophgo,sg2042-spifmc-nor"`.

## Control Flow

Probe allocates a host, enables the AHB clock, maps registers, sets one chip select and 8-bit spi-mem capabilities, initializes a mutex, gets match data, performs controller init/reset, clears transfer CSR, and registers the controller. `exec_op()` serializes with the mutex and routes address-less operations to `sg2044_spifmc_trans_reg()` and addressed operations to read, write, or command helpers.

Read writes opcode, address bytes, dummy bytes, length, clears interrupts, starts the transfer, waits for read-FIFO interrupt, drains up to 8 bytes at a time after polling FIFO pointer size, waits for transfer done, and clears FIFO pointer. Large reads are split into `SPIFMC_MAX_READ_SIZE` chunks. Write similarly writes opcode/address/dummy, starts transfer, waits for FIFO empty, pushes data in up-to-8-byte batches, waits for done, and clears FIFO pointer. Register reads use dummy writes and optional FIFO-flush suppression.

## State and Persistence Behavior

The driver maintains only the mutex, clock, and controller register state. It does not persist data itself; flash contents and status/configuration registers are persistent in the attached NOR device. Hardware init disables direct memory mapping, resets controller state, sets a conservative clock divider, clears CE control, and seeds transfer CSR defaults.

## Dependencies and Integration Points

The file depends on platform/OF, clocks, MMIO polling, mutexes, and `spi-mem`. It is intended for SPI NOR clients and advertises dual/quad mode bits, though the transfer code currently programs mostly 1-bit bus-width constants and does not implement a supports-op filter.

## Risks and Edge Cases

`sg2044_spifmc_exec_op()` ignores return values from the routed operation helpers and always returns 0, so timeout or I/O errors can be hidden from spi-mem clients. `sg2044_spifmc_trans()` also discards helper return values. The driver advertises dual/quad mode bits but does not clearly program bus width from `op->cmd/addr/dummy/data.buswidth` in normal read/write paths. Address and dummy byte counts are combined into one hardware field, so unsupported combinations need validation. Poll loops use one-second timeouts and no IRQ handler. Register write status opcode `0x01` has special bidirectional configuration that should be checked against NOR behavior.

## Test Signals

Test JEDEC ID/status reads, write-enable/status writes, page program, erase, large reads spanning 64 KiB chunks, timeouts from FIFO and transfer-done waits, SG2042 vs SG2044 match data, dual/quad operations advertised by spi-nor, error propagation from helpers, and concurrent spi-mem access serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sg2044-nor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-hspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-hspi.c

## Purpose

`spi-sh-hspi.c` is a simple SuperH HSPI SPI host driver. It uses programmed I/O only, manually controls hardware chip select, computes the closest clock divisor for each transfer, and completes whole SPI messages synchronously through `transfer_one_message`.

## Important APIs, Types, and Functions

`struct hspi_priv` stores MMIO base, controller, device, and clock. Register helpers are `hspi_write()`, `hspi_read()`, and `hspi_bit_set()`. `hspi_status_check_timeout()` polls status bits with a fixed retry loop. `hspi_hw_setup()` programs clock divisor and CPOL/CPHA. `hspi_transfer_one_message()` performs byte-by-byte transfers with CS handling. Probe/remove handle resource mapping, clock acquisition, runtime PM enable, controller registration, and cleanup.

## Control Flow

Probe obtains the memory resource, allocates a SPI host, gets the clock, maps registers, enables runtime PM, sets mode and 8-bit word capabilities, installs `transfer_one_message`, and registers. For each message, the transfer loop sets up hardware and asserts CS when starting a CS segment, writes one byte to SPTBR after waiting for TX space, waits for RX ready, reads SPRBR into the RX buffer when present, applies transfer delay, and deasserts CS when `cs_change` or message end requires it.

## State and Persistence Behavior

State is minimal and runtime-only: MMIO register contents, clock, and CS level. There is no persistent state and no DMA/IRQ state. Attached SPI devices own any persistent side effects.

## Dependencies and Integration Points

The driver uses platform resources, clocks, runtime PM, MMIO, and the SPI core. It supports only 8-bit words and CPOL/CPHA mode bits. OF matching recognizes `renesas,hspi`.

## Risks and Edge Cases

`msg->actual_length` is incremented by `t->len` even if an inner byte loop breaks early after a timeout, so partial failures may overreport transferred bytes. Clock selection brute-forces 64 divisor settings but does not reject large frequency error. `spi_transfer_delay_exec()` runs after the byte loop even if a timeout occurred in that transfer. There is no DMA or interrupt support, so long messages burn CPU and depend on fixed polling delays.

## Test Signals

Test all four modes, CS hold and `cs_change`, TX-only/RX-only/full-duplex messages, timeout paths for TX and RX status bits, requested speeds across divisor boundaries, probe/remove clock cleanup, runtime PM, and actual_length on injected mid-transfer failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-hspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-msiof.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-msiof.c

## Purpose

`spi-sh-msiof.c` is the SuperH/R-Car MSIOF SPI controller driver. It supports host and target modes, native and GPIO chip selects, 3-wire, LSB-first, many bits-per-word combinations, PIO and DMA, SoC-specific FIFO sizes and controller flags, optional DTDL/SYNCDL timing properties, and detection of MSIOF instances used for I2S rather than SPI.

## Important APIs, Types, and Functions

`struct sh_msiof_chipdata` carries bits-per-word masks, FIFO sizes, controller flags, minimum divider power, and quirks. `struct sh_msiof_spi_priv` stores controller, MMIO base, clock, platform device, parsed info, completions, FIFO sizes, DMA bounce pages and addresses, native CS state, and target-abort state.

Important functions include register read/write and CTR polling, IRQ handler, reset, clock and pin-mode register setup, DTDL/SYNCDL encoding, mode-register programming, FIFO read/write variants for aligned/unaligned and swapped 8/16/32-bit data, native-CS setup, message prepare, hardware start/stop, target abort, completion wait, PIO chunk transfer, DMA transfer, byte/word swap copy helpers, `sh_msiof_transfer_one()`, DT parsing, DMA channel allocation/release, probe/remove, and PM.

## Control Flow

Probe rejects nodes with graph ports because they represent MSIOF-I2S usage, selects chipdata and platform/DT info, applies fixed DTDL for R8A7795, allocates host or target controller, gets clock/IRQ/MMIO, requests IRQ, enables runtime PM, applies FIFO overrides, sets SPI capabilities and hooks, optionally allocates DMA channels plus one-page TX/RX DMA bounce buffers, and registers the controller.

Message prepare configures pin and CS polarity before assertion. Each transfer resets registers, sets the clock in host mode, limits word count by FIFO size, attempts DMA for chunks over 15 bytes when DMA exists, packing 8/16-bit data into 32-bit DMA words with byte/halfword swaps, and falls back to PIO on `-EAGAIN`. PIO chooses width-specific FIFO functions, programs mode registers and watermarks, fills TX FIFO, starts hardware, waits for interrupt completion or target abort, drains RX FIFO, clears status, stops hardware, and repeats for remaining words including odd trailing bytes.

## State and Persistence Behavior

State is runtime-only: completions, target-abort flag, FIFO sizing, native CS polarity cache, DMA bounce pages, and controller registers. There is no persistent storage. Timing properties from DT/platform data are parsed at probe and then used for each pin-mode setup.

## Dependencies and Integration Points

The driver integrates with platform/OF, OF graph, clock framework, PM runtime, interrupts, DMAengine plus SH DMA compatibility filters, SPI core host/target APIs, and `linux/spi/sh_msiof.h` register definitions/platform data. Match data covers SH Mobile and R-Car generations 2 through 4.

## Risks and Edge Cases

DMA uses single-page bounce buffers and chunks capped by mode-register word-length fields; large transfers rely on repeated packing/unpacking. Both source and destination cannot be unaligned for copy helpers, as noted in comments. Target abort completes both normal and TX-DMA completions, so abort races with real completions require careful testing. DTDL/SYNCDL values outside limited encodings are ignored with warnings. If DMA setup partially fails, release paths must unmap/free pages and channels exactly once. Clock setup reports too-low requested rates but still programs maximum divisor.

## Test Signals

Test SH/R-Car generation match data, host and target mode, native and GPIO CS, active-high CS, 3-wire TX high-Z, DTDL/SYNCDL DT values, 8/16/24/32-bit transfers, unaligned buffers, odd trailing bytes, DMA and PIO paths, DMA fallback, target abort during PIO and DMA, low-speed requests, suspend/resume, and probe rejection for I2S graph nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-msiof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-sci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-sci.c

## Purpose

`spi-sh-sci.c` is a bitbanged SPI driver using SuperH SCI pin-control register bits as GPIO-like SCK, MOSI, and MISO signals. It wraps the generic `spi_bitbang` framework and delegates chip-select control to platform data.

## Important APIs, Types, and Functions

`struct sh_sci_spi` embeds `struct spi_bitbang`, MMIO base, cached SCSPTR output value, platform `struct sh_spi_info`, and platform device. Low-level helpers are `setbits()`, `setsck()`, `setmosi()`, and `getmiso()`. The included `spi-bitbang-txrx.h` uses these helpers through four mode-specific wrappers: `sh_sci_spi_txrx_mode0()` through mode3. `sh_sci_spi_chipselect()` calls the platform chip-select callback.

Probe/remove allocate/release the SPI host, map/unmap SCI registers, initialize pins, start/stop bitbang, and restore pin state.

## Control Flow

Probe requires platform data for bus number, chip-select count, and optional chip-select callback. It configures the bitbang controller and txrx functions, maps the SCI resource, caches the current SCSPTR value, sets initial SCK/TXD/output-enable bits, and starts the bitbang engine. Runtime transfers are handled by the SPI bitbang core, which calls the mode-specific txrx function, toggles SCK/MOSI via `setbits()`, samples MISO from SCSPTR, delays with `ndelay()`, and invokes the platform CS callback.

## State and Persistence Behavior

The only driver state is the cached SCSPTR byte and platform data pointer. There is no persistence. The driver assumes it is the sole user of SCSPTR bits and therefore avoids locking around the cached read-modify-write model.

## Dependencies and Integration Points

The file depends on legacy SuperH platform data in `<asm/spi.h>`, MMIO helpers, `spi_bitbang`, and platform devices. It does not use OF, DMA, interrupts, clocks, or runtime PM.

## Risks and Edge Cases

Correctness depends on exclusive ownership of SCSPTR; any other user changing those bits will desynchronize `sp->val`. Speed and delays are governed by spi-bitbang timing rather than hardware clocks, so performance is low and CPU-bound. Missing platform data prevents probe. Chip-select semantics are entirely platform-callback-defined. Because MISO and MOSI share `PIN_TXD` definitions for this SCI mode, board wiring assumptions are critical.

## Test Signals

Test all four SPI modes, platform chip-select callback polarity, initialization and cleanup pin values, transfers with no RX or no TX, concurrent SCSPTR users if any exist on target boards, and behavior when platform data or memory resources are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh-sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-sh.c

## Purpose

`spi-sh.c` is an older SuperH SPI controller driver using FIFO registers, one IRQ, waitqueues, and whole-message transfer callbacks. It supports two chip selects, 8-bit or 32-bit register access depending on resource flags, TX and RX transfers, and simple setup/cleanup.

## Important APIs, Types, and Functions

`struct spi_sh_data` stores MMIO base, IRQ, SPI host, cached CR1 interrupt/status bits, waitqueue, and register width. Register helpers abstract 8-bit resources using shifted offsets versus 32-bit resources. Core helpers are bit set/clear, `clear_fifo()`, `spi_sh_wait_receive_buffer()`, `spi_sh_wait_write_buffer_empty()`, `spi_sh_send()`, `spi_sh_receive()`, `spi_sh_transfer_one_message()`, setup/cleanup, IRQ handler, probe, and remove.

## Control Flow

Probe validates memory resource and IRQ, allocates a devm SPI host, determines 8-bit or 32-bit MMIO access from resource flags, maps registers, initializes the waitqueue, requests the IRQ, sets two chip selects, installs setup/transfer/cleanup hooks, and registers the controller. Setup stops the cycle, clears CR1/CR3, resets FIFO, and programs a fixed 1/8 clock setting.

Message transfer clears SSA, then for each transfer calls `spi_sh_send()` when TX data exists and `spi_sh_receive()` when RX data exists. TX asserts SSA, fills up to 32 FIFO bytes, waits for TX buffer empty IRQ when more remains, handles write-protect abort, and on final transfer waits for TX completion before deasserting. RX programs byte count, asserts receive mode, waits for TX empty, waits for RX FIFO-full interrupts for large chunks, reads FIFO bytes, and resets CR3/FIFO for long transfers. The IRQ handler mirrors CR1 status bits into `ss->cr1`, clears enabled interrupt bits in CR4, and wakes the waitqueue.

## State and Persistence Behavior

State is volatile: MMIO register values, waitqueue status bits, FIFO contents, IRQ registration, and fixed setup clock bits. There is no persistence. Attached devices own any nonvolatile side effects.

## Dependencies and Integration Points

The driver depends on platform resources with `IORESOURCE_MEM_8BIT` or `IORESOURCE_MEM_32BIT`, IRQs, MMIO, waitqueues, and SPI core legacy `transfer_one_message`. It does not use DMA, runtime PM, OF match data, or clock framework.

## Risks and Edge Cases

The error path in `spi_sh_transfer_one_message()` calls `spi_finalize_current_message()` and then calls `mesg->complete` manually if present, which risks double completion depending on SPI core behavior. TX final wait checks `if (ret == 0 && (ss->cr1 & SPI_SH_TBE))`, which appears inverted relative to the earlier timeout pattern and may miss timeout reporting. `msg->actual_length` is incremented by full transfer length after send/receive success but partial progress inside helpers is not reported. Fixed clock setup ignores requested transfer speed and mode beyond the hard-coded divisor. Remove unregisters the controller then frees the manually requested IRQ.

## Test Signals

Test 8-bit and 32-bit resource widths, TX-only/RX-only/sequential TX+RX messages, long transfers above FIFO size and `SPI_SH_MAX_BYTE`, write-protect abort, timeout paths for TX and RX waits, final-transfer CS deassertion, cleanup state, double-completion behavior under injected errors, and registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-sh.c -->
