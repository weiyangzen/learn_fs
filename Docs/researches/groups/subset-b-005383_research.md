# subset-b-005383 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-geni-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-geni-qcom.c

## Purpose

`spi-geni-qcom.c` is the Qualcomm GENI/QUP SPI controller driver. It registers either a SPI host or target controller depending on firmware properties, programs GENI SPI protocol state, and moves SPI transfers through FIFO, SE DMA, or GPI DMA paths. The driver is tightly coupled to the Qualcomm GENI serial engine, interconnect bandwidth voting, runtime PM, OPP clock selection, and the SPI core transfer lifecycle.

## Important APIs, Types, and Functions

The central runtime object is `struct spi_geni_master`, which embeds `struct geni_se`, device and IRQ references, FIFO geometry, cached mode/CS/speed/bits-per-word, active transfer counters, completions for command cancellation/abort/DMA reset, DMA channels, and the current transfer mode. Probe wires `spi_geni_prepare_message()`, `spi_geni_transfer_one()`, `geni_can_dma()`, `spi_geni_handle_err()`, and optional `spi_geni_target_abort()` into `struct spi_controller`.

Key setup helpers are `spi_geni_init()`, `spi_slv_setup()`, `get_spi_clk_cfg()`, `geni_spi_set_clock_and_bw()`, `setup_fifo_params()`, `spi_setup_word_len()`, and `spi_geni_grab_gpi_chan()`. Transfer helpers split into `setup_se_xfer()` plus `geni_spi_handle_tx()`/`geni_spi_handle_rx()` for FIFO/SE DMA, and `setup_gsi_xfer()` with `spi_gsi_callback_result()` for GPI DMA. Error handling is in `handle_se_timeout()`, `handle_gpi_timeout()`, and `spi_geni_is_abort_still_pending()`. Interrupt completion is centralized in `geni_spi_isr()`.

## Control Flow

Probe maps the SE resource, gets the `se` clock, allocates a host or target controller, configures OPP/interconnect/runtime PM, initializes completions and the lock, calls `spi_geni_init()`, requests the IRQ, and registers the controller. `spi_geni_init()` validates or loads GENI SPI firmware, reads FIFO depth/width, initializes GENI FIFO thresholds, selects oversampling from QUP hardware version, and chooses GPI DMA if the FIFO interface is disabled and DMA channels are available, otherwise FIFO mode.

For each message, `spi_geni_prepare_message()` verifies no abort IRQ is still pending and, for SE modes, updates cached CS, loopback, CPHA, CPOL, CS polarity, and demux registers. `spi_geni_transfer_one()` rejects new work after a failed abort, completes zero-length transfers immediately, and dispatches to `setup_se_xfer()` or `setup_gsi_xfer()`. The SE path programs word packing, clock/divider, transfer lengths, M command parameters, mode selection, DMA descriptors or initial FIFO fill, then returns positive so the SPI core waits for interrupt completion. The GPI path configures DMA peripheral metadata, prepares RX if needed and TX always, submits descriptors, and finalizes in the DMA callback.

The ISR handles FIFO RX watermarks, FIFO TX watermarks, command done, SE DMA done/reset interrupts, cancel/abort completions, and interrupt acknowledgement under `mas->lock`. FIFO command done finalizes the current transfer and logs premature completion if byte counters remain. Error callbacks cancel then abort M commands, reset DMA FSMs when needed, and prevent new transfers while enabled pending IRQs indicate the abort path has not drained.

## State and Persistence Behavior

State is volatile per controller. `spi_geni_master` persists cached mode/clock/CS settings, active byte counters, current transfer pointer, DMA channel ownership, and abort health. Hardware state persists in GENI registers while the device is runtime-active and is reconstructed by message/transfer setup. No file-backed state exists.

Runtime PM saves power by disabling GENI resources and ICC paths on suspend, dropping OPP votes, and restoring resources plus the last source clock vote on resume. A failed abort sets `abort_failed`; later prepares poll pending IRQ state to avoid starting transfers while stale GENI interrupts could collide with a new transaction.

## Dependencies and Integration Points

The driver depends on the SPI core, Qualcomm GENI SE helpers, QCOM GPI DMA metadata, Linux DMAengine, OPP, interconnect bandwidth APIs, runtime/system PM, platform resources, and firmware/device properties. It consumes `qcom,geni-spi` compatibles and `spi-slave` to select target mode. The SPI core supplies DMA-mapped scatterlists and finalization callbacks; GENI hardware supplies M IRQ and DMA IRQ status bits.

## Risks and Edge Cases

The GPI path requires a TX descriptor even for RX-only transfers; failure to provide mapped TX SG data would break GPI semantics, hence `SPI_CONTROLLER_MUST_TX`. SE DMA only supports single-entry SG lists and silently falls back to FIFO for multi-entry lists. Length calculations for non-byte-aligned words depend on consistent word-count programming; premature done logging explicitly points at risks when `bits_per_word != 8`. Abort timeout paths must handle races where an ISR completed the transfer while error handling waited for the lock. Runtime resume restores `cur_sclk_hz`, so clock state must be initialized before suspend.

## Test Signals

Useful tests include host and target probe, FIFO-disabled systems with working and missing GPI DMA channels, loopback/CPOL/CPHA/CS-high mode changes across devices, 4 to 32 bit words, zero-length transfers, RX-only/TX-only/full-duplex transfers, multi-transfer messages with and without `cs_change`, SE DMA single-entry SG, forced FIFO fallback for multi-entry SG, timeout-induced cancel/abort and DMA FSM reset, runtime suspend/resume during idle, and pending-interrupt recovery after an abort failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-geni-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-gpio.c

## Purpose

`spi-gpio.c` implements a generic GPIO-backed bitbanged SPI host. It is intended for systems without a native SPI controller, systems where the native controller driver is unavailable, or boards that need arbitrary GPIO pins for SCK/MOSI/MISO/CS. It delegates transfer timing and word shifting to the SPI bitbang framework while providing GPIO-specific line operations, chip-select handling, 3-wire turnaround handling, and descriptor/platform-data resource discovery.

## Important APIs, Types, and Functions

`struct spi_gpio` stores the embedded `spi_bitbang`, SCK/MISO/MOSI GPIO descriptors, and optional CS GPIO array. GPIO line callbacks are `setsck()`, `setmosi()`, and `getmiso()`, with `getmiso()` reading MOSI for 3-wire mode. The four `spi_gpio_txrx_word_mode*()` callbacks handle normal full-duplex modes, while `spi_gpio_spec_txrx_word_mode*()` pass controller flags into bitbang helpers so missing MOSI/MISO paths are respected.

SPI-core callbacks are `spi_gpio_chipselect()`, `spi_gpio_set_mosi_idle()`, `spi_gpio_setup()`, `spi_gpio_set_direction()`, and `spi_gpio_cleanup()`. Resource setup is split between `spi_gpio_request()` for GPIO descriptors, `spi_gpio_probe_pdata()` for legacy platform data CS GPIOs, and `spi_gpio_probe()` for controller allocation and bitbang registration.

## Control Flow

Probe allocates a SPI host, chooses descriptor mode when a firmware node exists or legacy platform-data CS setup otherwise, requests optional MOSI/MISO plus required SCK, and configures controller mode bits for 3-wire, CPHA/CPOL, CS-high, LSB-first, and MOSI idle levels. Missing MOSI sets `SPI_CONTROLLER_NO_TX`; CS handling always uses `SPI_CONTROLLER_GPIO_SS` so the local chip-select callback runs.

The bitbang framework calls the selected mode-specific word function for each word. Those functions call generated helpers from `spi-bitbang-txrx.h`, which in turn call `setsck()`, `setmosi()`, and `getmiso()`. Chip selection sets SCK to idle polarity before asserting and drives CS according to `SPI_CS_HIGH`. Direction changes switch MOSI to input only in 3-wire mode and optionally add a high-impedance turnaround clock for `SPI_3WIRE_HIZ`.

## State and Persistence Behavior

The driver keeps only volatile GPIO descriptor state and bitbang framework state. `spi->controller_state` remains reserved for bitbang internals. No hardware FIFO, DMA, IRQ, runtime PM, or persistent storage is involved. GPIO output state persists electrically until changed by later transfers or driver removal.

## Dependencies and Integration Points

The driver depends on gpiolib descriptors, platform devices, firmware nodes or legacy `spi_gpio_platform_data`, the SPI core, and `spi_bitbang`. It matches `spi-gpio` device-tree compatibles and platform alias `spi_gpio`. It integrates with normal SPI child devices through the generic controller registration path.

## Risks and Edge Cases

There is no real delay implementation: `spidelay()` is empty because software overhead dominates, so requested high precision timing is not honored. Transfer speed is CPU/scheduler/GPIO-controller dependent and usually far below hardware SPI. Missing MOSI is explicitly supported, but missing MISO relies on bitbang flags and device expectations. 3-wire direction changes can leave MOSI high unless the code avoids input mode outside 3-wire, a behavior called out in comments. Legacy platform data and descriptor firmware paths differ, so CS GPIO indexing needs board-level validation.

## Test Signals

Tests should cover all four SPI modes, LSB-first, CS-high, no-MOSI TX-disabled operation, optional MISO, 3-wire and 3-wire high-impedance turnaround, MOSI idle low/high, descriptor-based DT probe, legacy platform-data CS setup, multi-CS devices, and slow devices that rely on CPOL idle state before CS assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-gxp.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-gxp.c

## Purpose

`spi-gxp.c` is the HPE GXP SPI flash interface driver. It registers a SPI host with `spi_mem` operations and uses the GXP SPIFI controller in manual/direct modes to perform SPI NOR register, read, and page-program style operations against up to two chip selects.

## Important APIs, Types, and Functions

`struct gxp_spi` stores matched SoC data, three MMIO windows (`reg_base`, `dat_base`, `dir_base`), a device pointer, and per-CS `struct gxp_spi_chip` records. `gxp_spi_set_mode()` switches the controller between manual and direct mode. Register-like spi-mem operations are implemented by `gxp_spi_read_reg()` and `gxp_spi_write_reg()`. Addressed memory operations use `gxp_spi_read()` through the direct memory window and `gxp_spi_write()` through command/data registers. `do_gxp_exec_mem_op()` chooses the helper based on data direction and whether an address is present.

## Control Flow

Probe allocates a host, maps the register, data, and direct windows, stores match data, sets `mem_ops`, `setup`, and `num_chipselect`, then registers the controller. Per-device setup initializes the chip record and enters manual mode. A spi-mem operation with no address is treated as a command/register transaction: the driver programs chip select, opcode, length, direction, starts the controller, polls `SPIMCTRL_BUSY`, and copies data to or from `dat_base`. Addressed reads copy directly from `dir_base + op->addr.val`, with CS0 offset by `0x4000000`. Addressed writes program command/address/length, write up to the 256-byte data buffer, start, and poll completion.

## State and Persistence Behavior

The driver state is limited to mapped MMIO pointers and per-CS chip records. Persistent effects are flash-side effects from write and erase-related opcodes issued by the SPI NOR layer. The controller mode persists in hardware until changed by setup or another owner, but the driver does not maintain cached configuration beyond chip select.

## Dependencies and Integration Points

The driver integrates with the SPI memory API and platform/OF probing for `hpe,gxp-spifi`. It uses `readb_poll_timeout()`, MMIO byte/word/dword accessors, and SPI NOR-style `spi_mem_op` contracts. It does not expose generic `transfer_one`; it is intended for spi-mem flash users.

## Risks and Edge Cases

`gxp_spi_write()` truncates addressed writes to `SPILDAT_LEN` bytes and returns success for that chunk; correctness depends on spi-mem/NOR upper layers splitting writes appropriately or accepting short controller limits through other means. `gxp_spi_read()` returns `0` rather than byte count because `exec_op` status semantics use zero for success. There is no explicit `supports_op` or `adjust_op_size`, so invalid bus widths, dummy cycles, or too-large operations are not filtered locally. Timeout is a polling loop derived from `GXP_SPI_TIMEOUT`, and direct-window CS0 offset is a hardware-specific mapping that needs validation against flash layout.

## Test Signals

Validate probe with all three resources, both chip selects, RDID/RDSR/WRSR style no-address operations, direct reads across offsets and CS0 offset translation, page program sizes at and above 256 bytes, busy timeout injection, unsupported op shapes from spi-nor, and regression tests that ensure manual mode is entered before command-register accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-gxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-kunpeng.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-kunpeng.c

## Purpose

`spi-hisi-kunpeng.c` is the HiSilicon Kunpeng SPI host controller driver. It is an interrupt-driven FIFO controller derived conceptually from DesignWare SPI code, supporting configurable clock dividers, 4 to 32 bits per word, loopback, CPOL/CPHA, CS-high, debugfs register visibility, ACPI probing, and per-device cached control register state.

## Important APIs, Types, and Functions

`struct hisi_spi` contains device/MMIO/IRQ/FIFO state plus current transfer pointers and byte width. `struct hisi_chip_data` is per-SPI-device cached state for CR mode bits and calculated divider fields. Core helpers include `hisi_calc_effective_speed()`, `__hisi_calc_div_reg()`, `hisi_spi_prepare_cr()`, `hisi_spi_reader()`, `hisi_spi_writer()`, `hisi_spi_flush_fifo()`, and `hisi_spi_disable()`. SPI callbacks are `hisi_spi_setup()`, `hisi_spi_cleanup()`, `hisi_spi_transfer_one()`, `hisi_spi_handle_err()`, and ISR `hisi_spi_irq()`.

## Control Flow

Probe allocates a host, maps registers, reads `spi-max-frequency` and optional `num-cs`, sets controller capability masks, initializes FIFO thresholds and interrupt masks, requests IRQ, registers the controller, and creates a debugfs register set. Setup allocates per-device chip data and caches loopback, CPOL, and CPHA bits. Each transfer recalculates effective speed and divider fields, writes the CR including bits per word, flushes stale RX data, sets current TX/RX pointers and word counts, enables interrupts and the controller, and returns positive for asynchronous completion.

The ISR checks masked interrupt status, handles RX overflow as `-EIO`, drains RX every interrupt, finalizes when expected RX words are consumed, and writes more TX data when TX IRQ fires. Finalization disables controller/interrupts and calls `spi_finalize_current_transfer()`.

## State and Persistence Behavior

Per-device `hisi_chip_data` persists between setups until cleanup, caching mode bits and the last effective speed. `hisi_spi` transfer pointers are volatile active-transfer state. Hardware FIFOs and registers are reset/disabled between transfers and on error. There is no storage persistence; writes affect attached devices only.

## Dependencies and Integration Points

The driver depends on ACPI match `HISI03E1`, platform MMIO/IRQ resources, debugfs, the SPI core, and firmware properties for max frequency and chip-select count. It uses bitfield helpers for register composition and standard SPI GPIO descriptor support for CS lines.

## Risks and Edge Cases

`hisi_spi_transfer_one()` derives transfer word count as `transfer->len / n_bytes`, so unaligned lengths relative to bits-per-word would silently ignore trailing bytes; the SPI core should constrain such transfers, but tests should cover them. Error handling sleeps 10 ms after disabling to let an in-flight ISR finish rather than using stronger synchronization. The divider calculation forces even dividers and clamps to hardware limits, so actual speed can be lower than requested. Debugfs creation failure is nonfatal.

## Test Signals

Test ACPI probe, missing/zero `spi-max-frequency`, optional `num-cs`, all supported bits-per-word classes, loopback/CPOL/CPHA/CS-high, TX-only/RX-only/full-duplex, RX overflow IRQ injection, timeout/error path, divider edge speeds near min/max, cleanup of per-device chip data, and debugfs register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-kunpeng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-sfc-v3xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-sfc-v3xx.c

## Purpose

`spi-hisi-sfc-v3xx.c` is a HiSilicon V3XX SPI NOR flash controller driver for hi16xx-class chipsets. It exposes a `spi_mem` controller that executes command/address/dummy/data flash operations through controller command registers and a small DATABUF window, using either IRQ completion or polling.

## Important APIs, Types, and Functions

`struct hisi_sfc_v3xx_host` stores device, MMIO base, max command dwords, optional IRQ/completion, and fixed address mode. `hisi_sfc_v3xx_mem_ops` provides `adjust_op_size`, `supports_op`, and `exec_op`. Data buffer helpers `hisi_sfc_v3xx_read_databuf()` and `hisi_sfc_v3xx_write_databuf()` enforce 32-bit MMIO accesses with byte handling for tails and unaligned host buffers. `hisi_sfc_v3xx_start_bus()` composes command config, bus width mode, dummy count, chip select, direction, and start bit. `hisi_sfc_v3xx_handle_completion()` decodes completion, protected-address, and page-program errors.

## Control Flow

Module init first applies DMI quirks that force quad buswidth override on selected Huawei systems. Probe allocates a host, maps MMIO, optionally requests IRQ, disables interrupts, configures a single-chipselect spi-mem controller, reads global configuration to determine 3-byte versus 4-byte address mode, selects command-buffer size from hardware version, and registers the controller.

For each spi-mem op, `supports_op()` rejects bus widths above quad and address lengths that do not match the controller's read-only address mode. `adjust_op_size()` limits data to the DATABUF size and, for unaligned buffers with at least four bytes, trims the operation to reach alignment. `exec_op()` optionally enables interrupts and stores an on-stack completion, writes outgoing data, starts the bus command, waits by IRQ or by polling the start bit clear, decodes raw interrupt status, and reads incoming data.

## State and Persistence Behavior

The host structure persists only controller configuration: IRQ availability, command-buffer size, and address mode. `host->completion` is transient during one IRQ-backed operation. Flash contents are the only persistent state affected by write/program/erase commands. Interrupt masks are enabled only during a command and disabled afterward.

## Dependencies and Integration Points

The driver integrates with ACPI id `HISI0341`, DMI board quirks, platform MMIO/IRQ resources, and the SPI memory layer used by SPI NOR. It relies on `spi_mem_default_supports_op()` after its own buswidth/address checks. It uses raw 32-bit IO copy helpers because the hardware data registers require 32-bit accesses.

## Risks and Edge Cases

IRQ mode uses an on-stack completion pointer in the host; it disables interrupts, synchronizes the IRQ, and clears the pointer after each command, so tests should stress timeout/IRQ races. `hisi_sfc_v3xx_generic_exec_op()` collapses either wait failure or completion-status failure to `-EIO`, losing `-ETIMEDOUT` detail. Dummy count and data count are programmed directly from op fields and must fit hardware bitfields. Address mode is global and read-only, so devices needing mixed 3-byte/4-byte operations are not supported unless the controller is configured accordingly.

## Test Signals

Test IRQ and polling operation, hardware versions below/above `0x351`, 3-byte and 4-byte address modes, DMI quad override systems, unaligned read/write buffers, operations at 16-dword and 64-dword limits, unsupported buswidth matrices, protected address errors, page program errors, completion timeouts, and SPI NOR probe/read/program/erase paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-sfc-v3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-img-spfi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-img-spfi.c

## Purpose

`spi-img-spfi.c` is the Imagination Technologies SPFI controller driver. It supports PIO and DMA transfers, CPOL/CPHA, dual and optional quad modes, runtime PM, system sleep, configurable maximum frequency, and per-chipselect clock/mode programming.

## Important APIs, Types, and Functions

`struct img_spfi` stores the SPI controller, lock, MMIO base/physical address, IRQ, clocks, DMA channels, and DMA busy flags. PIO helpers are `spfi_pio_write32()`, `spfi_pio_write8()`, `spfi_pio_read32()`, `spfi_pio_read8()`, and `img_spfi_start_pio()`. DMA helpers are `img_spfi_start_dma()`, `img_spfi_dma_rx_cb()`, and `img_spfi_dma_tx_cb()`. Controller callbacks are `img_spfi_prepare()`, `img_spfi_unprepare()`, `img_spfi_config()`, `img_spfi_transfer_one()`, `img_spfi_can_dma()`, and `img_spfi_handle_err()`.

## Control Flow

Probe allocates a controller, maps MMIO, requests an IRQ for illegal-access reporting, enables `sys` and `spfi` clocks, resets the controller, enables only the IACCESS interrupt, configures SPI mode and speed limits, optionally requests TX/RX DMA channels, enables runtime PM, and registers the controller. Message prepare programs chip select, CPOL, and CPHA in `SPFI_PORT_STATE`; unprepare resets the controller after a message.

For each transfer, `img_spfi_config()` calculates the bit clock divider, programs transaction size, selects DMA directions, selects single/dual/quad transfer mode, and enables the serial engine bit. Small transfers use PIO polling: start SPFI, write/read FIFO windows until buffers drain, then wait for ALLDONE. Larger transfers use DMA if both channels exist: configure bus widths based on transfer length alignment, submit RX before starting the controller, start SPFI, submit TX, and finalize when both DMA callbacks have run.

## State and Persistence Behavior

Persistent driver state is limited to clock handles, DMA channel handles, and busy flags. Hardware registers are reset after each message and after PIO timeout. Runtime suspend disables both clocks; runtime resume re-enables them. DMA callbacks update volatile busy flags under a spinlock. No persistent storage is maintained.

## Dependencies and Integration Points

The driver depends on platform resources, OF compatible `img,spfi`, optional DT property `img,supports-quad-mode`, optional `spfi-max-frequency`, Linux clock APIs, DMAengine, IRQ handling, runtime PM, and the SPI core. It uses GPIO descriptors for chip selects.

## Risks and Edge Cases

PIO pointer arithmetic is performed on `void *` buffers, relying on GNU C behavior. DMA completion callbacks call `spfi_wait_all_done()`, so both RX and TX callbacks may poll ALLDONE; races are moderated by busy flags but timing should be tested. DMA is selected solely by length greater than 64 bytes and requires both channels; partial DMA availability falls back to PIO. `img_spfi_handle_err()` terminates DMA but does not reset the controller itself. Transfer length is limited to 16 bits.

## Test Signals

Test PIO lengths below/equal/above FIFO size, DMA with aligned and unaligned lengths, RX-only/TX-only/full-duplex, illegal access IRQ, timeout reset, dual and quad transfers, `spfi-max-frequency` clamping, missing DMA channel fallback, runtime suspend/resume, system suspend/resume reset, and transfer length rejection above `0xffff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-img-spfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-imx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-imx.c

## Purpose

`spi-imx.c` is the Freescale/NXP i.MX SPI controller driver covering multiple CSPI and ECSPI generations from i.MX1 through i.MX6UL-era variants. It supports host and, where hardware allows, target mode; PIO, polling, interrupt-driven, and SDMA-backed transfers; dynamic burst programming; word delays; GPIO and native chip selects; runtime PM; and SoC-specific register layouts through callback tables.

## Important APIs, Types, and Functions

`struct spi_imx_devtype_data` abstracts SoC generation differences with callbacks for interrupt control, message/transfer preparation, trigger, RX availability, reset, DMA watermark setup, disable, and capability flags. `struct spi_imx_data` stores controller/device resources, clocks, active transfer buffers/counters, target state, DMA completions/package data, FIFO watermarks, and selected devtype data.

The driver contains register programming families for MX51/ECSPI (`mx51_ecspi_*`), MX31/MX35, MX21/MX27, and MX1. Transfer setup is handled by `spi_imx_setupxfer()`, transfer execution by `spi_imx_transfer_one()`, `spi_imx_pio_transfer()`, `spi_imx_poll_transfer()`, `spi_imx_pio_transfer_target()`, and `spi_imx_dma_transfer()`. DMA packaging uses `struct dma_data_package` plus helpers for bounce buffers, endian/order adjustment, burst splitting, DMA mapping, watermark calculation, DMA submission, and RX copyback.

## Control Flow

Probe matches the OF compatible to a devtype table, selects host or target allocation based on `spi-slave`, reads optional SPI-ready control and `num-cs`, sets controller mode bits according to hardware generation, maps MMIO, requests IRQ, obtains and enables clocks, initializes runtime PM, optionally requests SDMA channels, resets the controller, disables interrupts, registers the SPI controller, and autosuspends.

Before each message, runtime PM resumes the device and the devtype `prepare_message()` programs mode, CS selection, loopback, SPI_READY, CPOL/CPHA, CS polarity, and for ECSPI waits for configuration propagation at low SCLK rates. `spi_imx_setupxfer()` resolves speed, bits-per-word, buffer accessors, dynamic burst eligibility, DMA eligibility, RX-only CPHA flip state, and target burst size, then calls the devtype transfer-preparation callback.

Transfer execution flushes RX FIFO, then chooses target PIO, DMA, short-transfer polling, or interrupt PIO. PIO fills TX FIFO, triggers hardware, drains RX in ISR or polling loop, and completes when FIFO counters reach zero. DMA builds one or two packages when ECSPI burst length constraints require splitting, prepares aligned bounce buffers, configures DMA widths/watermarks, submits RX before TX, triggers hardware, waits for completions or target abort, copies valid RX bytes back, and falls back to PIO only when failure happened before start.

## State and Persistence Behavior

Driver state persists for the controller lifetime: devtype callbacks, clocks, mapped registers, DMA channel ownership, runtime PM configuration, default bus clock, and target-mode flags. Per-transfer state includes buffer pointers, counters, dynamic burst state, `usedma`, completions, bounce buffers, and target abort flag. Hardware state is reprogrammed per message and per transfer; runtime suspend disables clocks, while prepare/unprepare message brackets runtime PM usage.

## Dependencies and Integration Points

The driver depends on OF matching, platform MMIO/IRQ, Linux clock and pinctrl APIs, runtime PM, DMAengine and i.MX SDMA bindings, SPI core host/target APIs, GPIO descriptor CS support, and module parameters `use_dma` and `polling_limit_us`. It integrates with many `fsl,*-cspi` and `fsl,*-ecspi` compatibles.

## Risks and Edge Cases

This file carries high complexity around DMA byte ordering, unaligned lengths, dynamic burst, and word delay. DMA bounce-buffer allocation is per transfer and can fall back only before start. `spi_imx_dma_map()` checks `dma_mapping_error()` with `ret < 0`, but that API returns nonzero error status; this deserves static-analysis attention. Target mode has hardware errata requiring maximum 512-byte transfers and disabling ECSPI after completion. Runtime PM must be balanced if devtype preparation fails. Polling mode can fall back to interrupt mode after a timeout threshold.

## Test Signals

Test every supported compatible/devtype, host and target mode, native and GPIO CS, SPI_READY, loopback, CPOL/CPHA/CS-high/CS-word/RX_CPHA_FLIP/MOSI idle, 1 to 32 bits-per-word, dynamic burst aligned and unaligned lengths, word delay, PIO/polling/IRQ/DMA paths, DMA split at 512-byte burst boundaries, DMA map/allocation failure fallback, target abort, runtime PM, suspend/resume pinctrl states, and module parameter combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ingenic.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ingenic.c

## Purpose

`spi-ingenic.c` is the SPI bus driver for Ingenic JZ/X-series SoCs. It uses regmap over MMIO, supports several SoC variants with different frame-length and endian controls, provides PIO and optional DMA transfer paths, handles native chip select framing, and gates the controller clock around transfer hardware use.

## Important APIs, Types, and Functions

`struct jz_soc_info` describes bits-per-word mask, frame-length register field, endian-control style, max speed, and native CS count. `struct ingenic_spi` stores SoC info, clock, MMIO resource, regmap, and frame-length field. Core helpers include `spi_ingenic_wait()`, `spi_ingenic_set_cs()`, `spi_ingenic_prepare_transfer()`, `spi_ingenic_prepare_message()`, `spi_ingenic_prepare_hardware()`, and `spi_ingenic_unprepare_hardware()`. PIO transfers are generated by `SPI_INGENIC_TX(8/16/32)`, while DMA uses `spi_ingenic_prepare_dma()` and `spi_ingenic_dma_tx()`.

## Control Flow

Probe obtains matched SoC data, allocates a host, gets the clock, maps/registers regmap and the frame-length field, reads optional `num-cs`, assigns controller callbacks/capabilities, optionally requests TX/RX DMA channels, adds a cleanup action, and registers the controller. Hardware prepare enables the clock, clears and initializes control/status registers, and sets the enable bit; unprepare disables the controller and clock.

Message prepare programs loopback, endian/LSB-first, FIFO select, CPOL, CPHA, CS polarity, and chip-select framing bits. `set_cs()` sets `UNFIN` when asserting and clears it plus status under/overflow bits and waits for END when deasserting, then flushes RX/TX FIFOs. Each transfer programs clock divider and frame length, then either submits RX/TX DMA or uses PIO by prefilling the TX FIFO, reading RX words, and refilling TX until the transfer is complete.

## State and Persistence Behavior

Persistent controller state is SoC metadata, clock handle, regmap, and optional DMA channels. Hardware configuration is rewritten per message and per transfer. There is no persistent storage; attached device writes are the only durable effects. DMA channels are devm-cleaned through `spi_ingenic_release_dma()`.

## Dependencies and Integration Points

The driver integrates with OF compatibles for `ingenic,jz4750-spi`, `jz4775`, `jz4780`, `x1000`, and `x2000`; Linux clocks; regmap and regmap fields; DMAengine; SPI internals; and GPIO descriptor chip selects. It sets `SPI_CONTROLLER_MUST_RX | SPI_CONTROLLER_MUST_TX`, so dummy buffers can be used for one-sided transfers.

## Risks and Edge Cases

If TX DMA request succeeds and RX DMA request fails, `spi_ingenic_request_dma()` returns without clearing `ctlr->dma_tx`; the later devm cleanup action releases any allocated channel, but probe continues without `can_dma`. PIO transfer sizes are `len / word_size`, so transfer lengths must be aligned to selected word width. DMA can only be used when max SG burst constraints are satisfied. CS deassert waits for END and could timeout if hardware fails to finish.

## Test Signals

Test each compatible's bits-per-word and endian behavior, native CS counts, CPOL/CPHA/CS-high/loopback/LSB-first, PIO for 8/16/32-bit words, unaligned transfer rejection by SPI core, DMA success and partial-channel failure, DMA capability limits, clock enable/disable balancing, CS assert/deassert timing, FIFO flush, underflow/overflow status clearing, and low/high speed divider programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel-pci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-intel-pci.c

## Purpose

`spi-intel-pci.c` is the PCI front-end for the Intel PCH/PCU SPI flash controller. It matches Intel PCI IDs, maps BAR 0, provides board-specific controller type data, optionally exposes a PCI config-space write-protect override, and delegates all real SPI flash behavior to `intel_spi_probe()` in `spi-intel.c`.

## Important APIs, Types, and Functions

`intel_spi_pci_set_writeable()` toggles the BIOS Control Register write-protect-disable bit (`BCR_WPD`) when the core requests write access. `bxt_info` and `cnl_info` are `struct intel_spi_boardinfo` instances carrying controller type and the set-writeable callback. `intel_spi_pci_probe()` enables the PCI device, duplicates matched boardinfo, stores the PCI device in `info->data`, maps BAR 0 with `pcim_iomap_region()`, and calls `intel_spi_probe()`.

## Control Flow

The PCI ID table maps many Intel device IDs to BXT or CNL-style controller info. On probe, pcim/devm management handles device and mapping lifetime. The shared core then initializes registers, registers a spi-mem controller, and creates SPI NOR child devices. PCI driver `dev_groups` points at `intel_spi_groups`, so sysfs attributes from the core appear on PCI devices.

## State and Persistence Behavior

This file has no independent long-lived state beyond devm-duplicated boardinfo and PCI-managed mappings. Persistent effects are possible only through the core's flash writes and through setting `BCR_WPD` in PCI config space, which can make BIOS flash writeable until firmware/platform policy changes it.

## Dependencies and Integration Points

The file depends on PCI core managed APIs, Intel PCI IDs, `spi-intel.h`, and platform data definitions from `linux/platform_data/x86/spi-intel.h`. It exports no SPI callbacks itself; all SPI integration is delegated to `spi-intel.c`.

## Risks and Edge Cases

Writeability depends on platform firmware honoring `BCR_WPD`; if the bit cannot be set, the core reports BIOS lock state. Device ID to controller-type mapping is critical because register offsets differ between BXT and CNL. BAR mapping failures or incorrect resource sizing stop probe before the core sees the device.

## Test Signals

Test representative BXT and CNL PCI IDs, BAR0 mapping failure, `writeable=1` with BCR_WPD settable and locked cases, sysfs attribute presence via `dev_groups`, and smoke tests that `intel_spi_probe()` receives the correct boardinfo type and PCI device data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel-platform.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-intel-platform.c

## Purpose

`spi-intel-platform.c` is the platform-device front-end for the Intel PCH/PCU SPI flash controller. It supports non-PCI enumeration paths by receiving `struct intel_spi_boardinfo` as platform data, mapping the MMIO resource, and delegating controller initialization to the shared Intel SPI core.

## Important APIs, Types, and Functions

The only functional entry point is `intel_spi_platform_probe()`. It retrieves platform data, maps resource 0 with `devm_platform_ioremap_resource()`, and calls `intel_spi_probe()`. The platform driver exposes `intel_spi_groups` through its driver `dev_groups` and declares the `platform:intel-spi` alias.

## Control Flow

When a platform device named `intel-spi` probes, the front-end validates that platform data exists, maps MMIO, and invokes the common core. The core then configures sequencers, registers spi-mem operations, and creates SPI NOR child devices.

## State and Persistence Behavior

This wrapper owns no independent state. All persistent state and flash side effects are handled by `spi-intel.c`; platform data remains owned by the enumerating platform code.

## Dependencies and Integration Points

It depends on platform devices, `spi-intel.h`, and boardinfo supplied by x86 platform code. It is an integration shim for systems where the SPI controller is described by platform resources instead of a PCI function.

## Risks and Edge Cases

Missing platform data returns `-EINVAL`; incorrect boardinfo type will make the core use wrong register offsets or sequencer capabilities. Resource mapping errors are propagated directly. There is no front-end write-protect callback unless boardinfo supplies one.

## Test Signals

Test probe with valid and missing platform data, invalid MMIO resource, each supported boardinfo type supplied by platform code, sysfs group presence, and common-core SPI NOR discovery through the platform path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-intel.c

## Purpose

`spi-intel.c` is the shared Intel PCH/PCU SPI flash controller core. It exposes the controller as a `spi_mem` host for SPI NOR, supports hardware and software sequencer operations, enforces or reports flash protection state, reads the Intel flash descriptor to size components and partitions, creates SPI NOR child devices, and exports sysfs status attributes for protected, locked, and BIOS-locked state.

## Important APIs, Types, and Functions

`struct intel_spi` holds device, boardinfo, MMIO bases, protection/software-sequencer register offsets, host pointer, region/protection counts, flash chip size, lock/protection flags, software-sequencer flags, atomic preopcode state, BIOS-programmed opcodes, and selected memory-operation table. `struct intel_spi_mem_op` maps a `spi_mem_op` shape to an execution helper and optional hardware replacement cycle.

Core execution helpers include `intel_spi_hw_cycle()`, `intel_spi_sw_cycle()`, `intel_spi_read_reg()`, `intel_spi_write_reg()`, `intel_spi_read()`, `intel_spi_write()`, and `intel_spi_erase()`. spi-mem callbacks are `intel_spi_adjust_op_size()`, `intel_spi_supports_mem_op()`, `intel_spi_exec_mem_op()`, direct-map create/read/write, and `intel_spi_get_name()`. Initialization and discovery are handled by `intel_spi_init()`, `intel_spi_read_desc()`, `intel_spi_fill_partition()`, `intel_spi_populate_chip()`, and exported `intel_spi_probe()`.

## Control Flow

`intel_spi_probe()` allocates a SPI host, stores MMIO and boardinfo, runs `intel_spi_init()`, registers the controller, stores driver data, and populates SPI NOR child devices. Init selects register offsets and capabilities by boardinfo type, optionally asks the front-end to disable BIOS write protection when `writeable=1`, disables sequencer SMI generation, decides whether erase must use software sequencing based on LVSCC/UVSCC opcodes, verifies software sequencer availability, reads lock state and BIOS opmenu opcodes, chooses generic or 64K-erase operation tables, and dumps debug registers.

spi-mem support matches incoming ops against static operation tables. Register ops use hardware replacement cycles when possible or software sequencer cycles for programmable opcodes. Write-enable is represented as an atomic preopcode for the following software-sequencer write. Bulk reads/writes use the hardware sequencer in chunks no larger than the 64-byte FIFO and not crossing 4 KiB boundaries. Erase uses hardware or software sequencing depending on init decisions. Direct-map operations reuse the matched operation helper.

Flash population reads descriptor signature and component-density data, sets one or two chip selects, creates a `spi-nor` board info for chip 0 with a `BIOS` partition covering enabled regions, marks it read-only if writeable was not requested or protected regions exist, and optionally creates chip 1 with a full-size `BIOS1` partition.

## State and Persistence Behavior

Driver state persists in `struct intel_spi` for the controller lifetime. `protected`, `locked`, and `bios_locked` are exposed read-only through sysfs. The module parameters `writeable` and `ignore_protection_status` affect whether the MTD partition is writeable and whether protected-region status blocks writes. Flash writes/erases persist in SPI NOR storage; BIOS control register changes can alter platform flash writeability. The driver itself stores no file-backed state.

## Dependencies and Integration Points

The core depends on SPI memory APIs, SPI NOR opcodes, MTD partition data, Intel boardinfo from x86 platform data, MMIO accessors, polling helpers, and the PCI/platform wrappers. It exports `intel_spi_probe()` and `intel_spi_groups` for those wrappers. It integrates with SPI NOR by creating `spi-nor` devices programmatically instead of relying on firmware child nodes.

## Risks and Edge Cases

This is security-sensitive firmware flash access. The `writeable` and `ignore_protection_status` parameters can expose BIOS regions for modification. Software sequencer support depends on BIOS-programmed locked opmenus; unsupported opcodes must be rejected. `intel_spi_is_protected()` returns true only when a protected range is contained within a flash region, so range-overlap semantics deserve review. Hardware cycles must not cross 4 KiB boundaries, and FIFO chunks are limited to 64 bytes. Descriptor parsing failure prevents child creation. Atomic preopcode state must be cleared after each relevant operation to avoid applying WREN to the wrong command.

## Test Signals

Test BYT/LPT/BXT/CNL boardinfo paths, locked and unlocked opmenus, hardware versus software sequencer register access, 4K and 64K erase selection, descriptor read failures, one-chip and two-chip descriptors, protected range sysfs, BIOS lock sysfs, `writeable` and `ignore_protection_status` combinations, 64-byte FIFO chunking, 4 KiB boundary splitting, WREN atomic sequence behavior, direct-map reads/writes, and SPI NOR probe/read/program/erase flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h

## Purpose

`spi-intel.h` is the private interface between the Intel SPI flash core and its PCI/platform front-ends. It keeps the front-ends small by exposing the shared probe function and sysfs attribute groups while importing the boardinfo type definition used to describe controller variants and write-protect callbacks.

## Important APIs, Types, and Functions

The header includes `linux/platform_data/x86/spi-intel.h`, declares `extern const struct attribute_group *intel_spi_groups[]`, and declares `int intel_spi_probe(struct device *dev, void __iomem *base, const struct intel_spi_boardinfo *info)`.

## Control Flow

PCI and platform wrappers include this header, map their MMIO resources, prepare or retrieve `struct intel_spi_boardinfo`, and call `intel_spi_probe()`. They also reference `intel_spi_groups` in their driver definitions so sysfs attributes exported by the core are attached to front-end devices.

## State and Persistence Behavior

The header defines no state. It exposes hooks through which front-ends hand persistent MMIO mappings and boardinfo into the core. Any flash or BIOS-lock side effects happen inside `spi-intel.c`.

## Dependencies and Integration Points

It depends on Linux device/MMIO types through including C files and on the x86 Intel SPI platform-data header. It integrates the core with PCI and platform modules without exposing internal `struct intel_spi`.

## Risks and Edge Cases

The ABI between wrappers and core is intentionally narrow; incorrect boardinfo passed through this function can still select wrong register offsets. Header changes can break both wrappers and any other in-tree user of `intel_spi_probe()` or `intel_spi_groups`.

## Test Signals

Build tests should compile both PCI and platform wrappers with this header. Link tests should verify `intel_spi_probe` and `intel_spi_groups` exports resolve when modules are built separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-iproc-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-iproc-qspi.c

## Purpose

`spi-iproc-qspi.c` is the Broadcom iProc integration layer for the shared Broadcom QSPI controller. It adapts iProc-specific level-2 interrupt registers to the common `spi-bcm-qspi` core by providing interrupt status, acknowledge, and mask callbacks, then delegates probing/removal and PM to the common core.

## Important APIs, Types, and Functions

`struct bcm_iproc_intc` wraps `struct bcm_qspi_soc_intc` with platform device, interrupt mask/status MMIO windows, a spinlock, and endian flag. The callback implementations are `bcm_iproc_qspi_get_l2_int_status()`, `bcm_iproc_qspi_int_ack()`, and `bcm_iproc_qspi_int_set()`. `bcm_iproc_probe()` allocates the wrapper, maps named resources, detects big-endian mode, initializes and disables interrupts, installs callbacks, and calls `bcm_qspi_probe()`.

## Control Flow

On probe, the driver maps `intr_regs` and `intr_status_reg`, acknowledges pending MSPI/BSPI done bits, masks done interrupts, fills the common interrupt callback table, and hands control to the shared Broadcom QSPI probe. The status callback reads seven status registers and translates raw bit positions into common `MSPI_DONE`, `BSPI_DONE`, and `BSPI_ERR` flags. Ack writes `1` to each status register selected by a common interrupt mask. Set updates the iProc interrupt-enable register under a spinlock, shifting the common mask by `INTR_BASE_BIT_SHIFT`.

## State and Persistence Behavior

State is volatile interrupt-controller adapter state. The QSPI flash/device state is owned by `spi-bcm-qspi`. Interrupt mask bits persist in hardware while the device is active and are modified by common-core calls.

## Dependencies and Integration Points

The driver depends on OF compatibles `brcm,spi-nsp-qspi` and `brcm,spi-ns2-qspi`, named platform MMIO resources, endian-aware Broadcom QSPI accessors, common interrupt masks from `spi-bcm-qspi.h`, and the shared `bcm_qspi_probe/remove/pm_ops`.

## Risks and Edge Cases

Correct named resources are mandatory. Interrupt translation depends on the common mask definitions matching the seven iProc status registers. The mask update is locked, but status/ack loops are not; this matches typical interrupt-controller usage but should be validated under high IRQ load. Big-endian access must match DT, or interrupt bits will be misread.

## Test Signals

Test both compatibles, big- and little-endian MMIO access, missing named resources, pending IRQ ack at probe, interrupt enable/disable races, MSPI done, BSPI done, BSPI error status translation, and integration smoke tests through the common Broadcom QSPI flash read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-iproc-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-jcore.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-jcore.c

## Purpose

`spi-jcore.c` is a simple J-Core SPI controller driver. It implements byte-at-a-time polling transfers over two MMIO registers, supports three chip selects, CPOL/CPHA/CS-high, a programmable clock divider, and optional reference-clock discovery.

## Important APIs, Types, and Functions

`struct jcore_spi` stores the SPI host, MMIO base, cached CS and speed register bits, current speed, and reference clock frequency. `jcore_spi_wait()` polls the busy bit. `jcore_spi_program()` writes cached CS/speed state to the control register. `jcore_spi_chipsel()` updates active-low/high CS bits through `set_cs`. `jcore_spi_baudrate()` calculates divider bits. `jcore_spi_txrx()` performs the transfer and finalizes it.

## Control Flow

Probe allocates a host, sets fixed capabilities, manually requests and maps MMIO, reads optional `ref_clk` rate with a 50 MHz default, initializes all CS bits high, programs a default 400 kHz speed, and registers the controller. For each transfer, the driver updates baudrate if needed, then for every byte waits idle, writes TX data or zero, starts transfer by writing control with `XMIT`, waits idle again, reads RX data if requested, and finalizes the current transfer.

## State and Persistence Behavior

Cached CS and speed bits persist in `struct jcore_spi` and are reprogrammed whenever CS or speed changes. There is no DMA, IRQ, runtime PM, or persistent storage. Attached devices see persistent effects only from SPI commands sent over the bus.

## Dependencies and Integration Points

The driver depends on platform/OF compatible `jcore,spi2`, MMIO resources, optional clock provider `ref_clk`, and the SPI core. It uses devm resource helpers for mapping and controller registration after manual memory-region request.

## Risks and Edge Cases

Transfers are purely polling and byte-at-a-time, so throughput is low and CPU-bound. `jcore_spi_txrx()` calls `spi_finalize_current_transfer()` and returns `0` on success, which is unusual because many synchronous `transfer_one` implementations either return 0 without finalizing or return 1 for async; this should be checked against SPI core expectations for this code version. Timeout is a fixed loop count rather than time-based, so it varies with CPU speed. Probe error paths use `-EBUSY` for several mapping/resource failures.

## Test Signals

Test probe with and without `ref_clk`, all three chip selects, CPOL/CPHA/CS-high, speed divider extremes, TX-only/RX-only/full-duplex byte streams, busy timeout injection before command and after command, and SPI core completion semantics for synchronous versus explicitly finalized transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-jcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-kspi2.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-kspi2.c

## Purpose

`spi-kspi2.c` is the KEBA SPI host controller type 2 driver for an FPGA IP core exposed as an auxiliary device. It implements byte-oriented polling transfers, a hardware semaphore for sharing the controller with non-Linux processors, automatic registration of board-provided SPI devices, and basic CPOL/CPHA plus clock divider support.

## Important APIs, Types, and Functions

`struct kspi2` stores the KEBA auxiliary device, MMIO base, SPI host, base clock frequency, control-register shadow, and created SPI child devices. Hardware sharing is implemented by `kspi2_inuse_lock()` and `kspi2_inuse_unlock()`, wired to `prepare_transfer_hardware` and `unprepare_transfer_hardware`. Transfer helpers are `kspi2_calc_minimal_divider()`, `kspi2_write_control_reg()`, `kspi2_txrx_byte()`, `kspi2_process_transfer()`, `kspi2_setup_transfer()`, and `kspi2_transfer_one()`. Child management uses `kspi2_register_devices()` and `kspi2_unregister_devices()`.

## Control Flow

Probe allocates a host, retrieves the containing `keba_spi_auxdev`, allocates child-device tracking, maps the auxiliary IO resource, reads the base clock selector, initializes control and CS registers, assigns controller callbacks, registers the controller, and creates each `spi_board_info` child device supplied by the auxiliary device. Before a transfer sequence, the SPI core calls prepare hardware, which polls the IN_USE bit until the hardware semaphore is acquired. Per message, CPOL/CPHA bits are updated through the shadowed control register. Per transfer, the driver validates byte-multiple word widths, selects a divider at or below requested speed, then writes and polls one byte at a time. Unprepare releases the hardware semaphore by writing IN_USE.

## State and Persistence Behavior

The driver keeps a shadow of the control register to avoid redundant writes, an array of child devices to unregister on removal, and base clock state read from hardware. The hardware semaphore state persists in the FPGA register and coordinates with external processors. No filesystem persistence exists; SPI commands may persistently modify attached devices.

## Dependencies and Integration Points

The driver depends on the KEBA auxiliary bus structures from `linux/misc/keba.h`, SPI core, MMIO polling helpers, and auxiliary-driver registration. It matches auxiliary device name `keba.spi`. Child SPI devices come from `keba_spi_auxdev->info`, not from DT child nodes.

## Risks and Edge Cases

Only 8-bit-multiple word widths are supported, but transfers are still processed byte-by-byte, so higher word widths do not change bus packing beyond validation. The hardware semaphore can block for up to 10 seconds and only warns on timeout. `num_chipselect` is 255 and CS register uses `0xff` as none, so chip-select numbering must avoid ambiguity with no-CS semantics. Throughput is limited by per-byte polling. Child device registration failure unwinds previously created devices.

## Test Signals

Test all base clock selector values and invalid selector, semaphore acquisition/release and timeout, CPOL/CPHA mode setup, speed clamping to min/max, byte and multi-byte transfers, RX-only/TX-only/full-duplex, unsupported mode bits, non-byte-multiple word width rejection, chip selects including high values near 255, automatic child creation and unwind, and removal unregistering all children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-kspi2.c -->
