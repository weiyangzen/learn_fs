# subset-b-005387 SPI Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pl022.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pl022.c

## Purpose
`spi-pl022.c` is the AMBA/PrimeCell SPI controller driver for ARM PL022 SSP and related vendor variants. It exposes the PL022 block as a Linux `spi_controller`, supports interrupt, polling, and optional DMA-engine transfers, and adapts register programming for ARM, ST, ST PL023, and LSI variants with different FIFO depths, control register layouts, loopback support, and internal chip-select handling.

## Important APIs, Types, And Functions
- `struct vendor_data` captures per-IP differences: FIFO depth, max bits-per-word, ST extended control registers, PL023 restrictions, loopback, and internal CS control.
- `struct pl022` is controller runtime state: AMBA device, mapped registers, clock, SPI controller, platform data, current transfer/chip, TX/RX cursors, FIFO accounting, DMA channels/tables, dummy DMA page, and current chip select.
- `struct chip_data` is per-SPI-device state stored with `spi_set_ctldata()`: CR0/CR1/DMACR/CPSR register images, bytes-per-word, read/write access width, DMA enablement, and transfer type.
- `pl022_probe()` allocates/registers the SPI controller, maps AMBA resources, enables the clock, initializes hardware defaults, requests IRQ, probes DMA, and enables runtime PM.
- `pl022_setup()` validates per-device controller data or DT properties, computes clock divisors, derives word-size read/write modes, and precomputes register images for later transfer use.
- `pl022_transfer_one()` restores chip state, flushes the FIFO, and dispatches to polling or interrupt/DMA paths.
- `readwriter()` is the core PIO pump, draining RX FIFO and filling TX FIFO while maintaining `exp_fifo_level` to avoid RX FIFO overrun.
- DMA support is built around `pl022_dma_autoprobe()`, `pl022_dma_probe()`, `configure_dma()`, `dma_callback()`, `terminate_dma()`, and `pl022_dma_remove()`.
- PM hooks are `pl022_suspend()`, `pl022_resume()`, `pl022_runtime_suspend()`, and `pl022_runtime_resume()`.

## Control Flow
Probe begins from the AMBA match table, selects a `vendor_data` entry, derives platform data from board data or DT, allocates `spi_controller`, maps registers, gets the SSP clock, writes default register values, installs `pl022_interrupt_handler()`, optionally discovers DMA channels, then registers the controller. Device setup runs lazily per SPI device; it builds a `chip_data` register image based on SPI mode, bits-per-word, max speed, PL022-specific controller data, and vendor layout.

Transfers start in `pl022_transfer_one()`. The driver restores the per-device register image, flushes stale FIFO data, and sets transfer cursors. Polling mode enables SSP and repeatedly calls `readwriter()` until TX/RX are complete or a 1000 ms timeout fires. Interrupt mode enables TX and error interrupts; the IRQ handler handles overrun as fatal, otherwise pumps FIFO via `readwriter()`, disables TX interrupt after TX completion, and finalizes when RX reaches `rx_end`. DMA mode configures RX/TX DMA channels and scatterlists, enables the hardware DMA bits already present in the chip register image, suppresses PL022 data interrupts, and finalizes from the RX DMA callback.

## State And Persistence Behavior
The driver keeps no persistent storage outside kernel runtime state. Hardware configuration is represented as cached register images in `chip_data` and reloaded on every transfer, which limits cross-device register leakage. Transfer state is transient in `struct pl022`: buffer cursors, current chip, FIFO expected level, and DMA mapping state. Runtime PM disables/enables the SSP clock and selects pinctrl idle/default states; system suspend delegates to SPI core suspend and forced runtime PM. DMA scatterlists and the dummy page are allocated at transfer or probe time and freed on completion, error, remove, or DMA termination.

## Dependencies And Integration Points
This driver integrates with AMBA device matching, the SPI core, DT/board `struct pl022_ssp_controller` data, optional DMA engine slave channels named `rx` and `tx`, the common clock framework, runtime/system PM, pinctrl, and GPIO-descriptor chip selects through `host->use_gpio_descriptors`. It imports PL022-specific public definitions from `<linux/amba/pl022.h>`. It registers early via `subsys_initcall()` so SPI devices needed early in boot can bind.

## Risks
- DMA mapping assumes both RX and TX channels are available; partial DMA availability falls back to PIO/interrupt only at setup/probe boundaries.
- `BUG_ON()` is used in DMA helper paths for unexpected scatterlist and bus-width conditions, so invalid internal state can become a kernel panic.
- Polling transfers have a fixed timeout and only diagnose by dumping selected registers.
- Odd transfer lengths with 16/32-bit word widths are rejected, but surplus RX bytes can still be observed and warned about if hardware delivers more than expected.
- The DT controller-data path accepts many PL022-specific properties; invalid combinations are caught by `verify_controller_parameters()`, but board descriptions remain a major compatibility surface.
- Runtime PM relies on balanced probe/remove behavior around `pm_runtime_put()` and `pm_runtime_get_noresume()`.

## Test Signals
- Probe success/failure with each AMBA ID variant and DT/platform-data path.
- SPI loopback and mode 0-3 transfers across 4-16 bit ARM variant and 4-32 bit ST variants.
- DMA and non-DMA transfers, including missing DMA channel fallback and RX overrun handling.
- Polling timeout behavior under stalled hardware.
- Runtime suspend/resume and system suspend/resume with active SPI clients.
- Internal CS register operation on the LSI variant and GPIO descriptor CS operation on other variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pl022.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ppc4xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-ppc4xx.c

## Purpose
`spi-ppc4xx.c` is a simple Open Firmware platform driver for IBM PPC4xx SPI controllers. The hardware has no FIFO, so the driver sends one byte at a time and waits for an interrupt for each received byte. It uses the legacy `spi_bitbang` helper to provide SPI controller services while still driving native controller registers.

## Important APIs, Types, And Functions
- `struct spi_ppc4xx_regs` describes the byte-wide mode, RX, TX, control, status, and clock divisor registers.
- `struct ppc4xx_spi` stores the bitbang controller, completion, register mapping, IRQ, OPB clock frequency, active transfer length/counter, current TX/RX buffers, and SPI controller pointer.
- `struct spi_ppc4xx_cs` stores the precomputed mode register value for each SPI device.
- `spi_ppc4xx_setup()` validates `max_speed_hz` and builds mode bits from SPI mode and `SPI_LSB_FIRST`.
- `spi_ppc4xx_setupxfer()` programs mode and clock divisor for a transfer.
- `spi_ppc4xx_txrx()` starts byte zero and sleeps on a completion until the IRQ handler finishes the buffer.
- `spi_ppc4xx_int()` handles byte completion, reads RX, writes the next TX byte, and completes the transfer when all bytes are done.
- `spi_ppc4xx_of_probe()` performs OF resource lookup, OPB clock discovery, mapping, IRQ request, controller setup, and `spi_bitbang_start()`.

## Control Flow
Probe allocates a SPI controller with `struct ppc4xx_spi`, configures `spi_bitbang` callbacks, reads the OPB `clock-frequency`, maps the SPI register block, requests the IRQ, enables the shared SPI/I2C pinmux via DCR, and starts the bitbang controller. Per-device setup caches the static mode register value. Per-transfer setup programs the cached mode and computes the CDM prescaler from the requested speed.

During a transfer, `spi_ppc4xx_txrx()` stores buffer pointers and length, writes the first byte to `txd`, sets `SPI_PPC4XX_CR_STR`, and waits. Each IRQ reads status, busy-waits briefly if `BSY` is still set, reads `rxd`, stores it if RX is present, writes the next byte if any, or completes the transfer.

## State And Persistence Behavior
There is no persistent on-disk state. Per-device `controller_state` holds only the cached mode byte. Active transfer state in `struct ppc4xx_spi` is overwritten for each transfer and synchronized by completion. The register mapping and IRQ live from probe to remove. Remove stops bitbang, releases memory/IRQ resources, unmaps registers, and releases the SPI controller.

## Dependencies And Integration Points
The file depends on OF platform probing, PowerPC DCR access for pinmux enablement, `spi_bitbang`, and standard SPI core setup/cleanup callbacks. Chip selects are expected to be represented by GPIO descriptors; `num_chipselect` is set to zero so SPI core derives the count from GPIO descriptors.

## Risks
- One interrupt per byte can produce high CPU load; the header comment explicitly points to `max_speed_hz` throttling via DT as mitigation.
- The IRQ handler has a fixed short busy-wait loop for undocumented BSY/RBR timing; if the hardware remains busy it completes with a partial count rather than a rich error path.
- Clock divisor calculation clamps to 8 bits and can only approximate requested speeds.
- No DMA or FIFO path exists, so large transfers are inherently expensive.

## Test Signals
- OF probe with `ibm,ppc4xx-spi`, valid OPB node, clock property, memory resource, and IRQ.
- SPI mode 0-3 and `SPI_LSB_FIRST` setup.
- Transfers with TX-only, RX-only, and full-duplex buffers.
- Slow device operation where status remains busy at IRQ entry.
- Removal after active controller registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-ppc4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-dma.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-dma.c

## Purpose
`spi-pxa2xx-dma.c` provides DMA-engine support for the PXA2xx SSP SPI core. It prepares RX/TX DMA slave descriptors against the SSP data register, starts/stops paired DMA transfers, handles DMA completion versus FIFO-overrun races, and acquires/releases DMA channels for the shared core driver.

## Important APIs, Types, And Functions
- `pxa2xx_spi_dma_setup()` requests compatible TX/RX slave DMA channels using platform/glue-provided filter data.
- `pxa2xx_spi_dma_prepare()` prepares both TX and RX descriptors for a `spi_transfer`, registering the completion callback on RX.
- `pxa2xx_spi_dma_start()` issues pending RX then TX channels and marks `dma_running`.
- `pxa2xx_spi_dma_transfer()` is the IRQ-side DMA transfer handler used by the core to catch SSP FIFO overrun.
- `pxa2xx_spi_dma_transfer_complete()` serializes completion/error handling using `atomic_t dma_running`, clears interrupts/status, disables timeout on newer SSPs, sets message status on error, and finalizes the SPI transfer.
- `pxa2xx_spi_dma_stop()` terminates both DMA channels synchronously.
- `pxa2xx_spi_dma_release()` terminates and releases allocated DMA channels.

## Control Flow
The PXA2xx core calls `pxa2xx_spi_dma_setup()` during probe when platform data requests DMA. For each DMA-mapped transfer, the core sets `drv_data->transfer_handler` to `pxa2xx_spi_dma_transfer()`, calls `pxa2xx_spi_dma_prepare()`, clears SSP status, starts DMA, configures SSCR registers, and enables SSP service. RX completion calls `pxa2xx_spi_dma_callback()`, which delegates to `pxa2xx_spi_dma_transfer_complete(false)`. If the SSP IRQ reports RX overrun first, `pxa2xx_spi_dma_transfer()` terminates channels and completes with error.

## State And Persistence Behavior
The file relies on shared `struct driver_data` from `spi-pxa2xx.h`. DMA state is held in `controller->dma_tx`, `controller->dma_rx`, `xfer->tx_sg`, `xfer->rx_sg`, and `atomic_t dma_running`. It persists only for the controller lifetime. The atomic prevents double finalization when DMA completion and ROR IRQ arrive on different CPUs.

## Dependencies And Integration Points
This file is tightly coupled to `spi-pxa2xx.c` and `spi-pxa2xx.h`, the SPI core's DMA-mapped transfer helpers, DMA engine slave API, PXA SSP register helpers, and platform/PIC glue that supplies DMA filter parameters. It uses `DEFAULT_DMA_CR1`, `MAX_DMA_LEN`, `pxa25x_ssp_comp()`, `read_SSSR_bits()`, `write_SSSR_CS()`, and `clear_SSCR1_bits()` from the shared header.

## Risks
- Both RX and TX channels are mandatory; failure to request RX after TX unwinds TX, but no half-DMA mode exists.
- DMA descriptors are prepared separately; TX descriptor preparation failure after RX success terminates TX only because RX was not submitted yet.
- Error detection depends on SSP overrun status recheck at completion to cover races.
- Burst size and DMA filter correctness come entirely from platform/glue data.

## Test Signals
- DMA setup success and fallback when one channel is missing.
- RX/TX DMA transfers for 8/16/32-bit frames and multiple burst sizes.
- Concurrent DMA completion and FIFO-overrun IRQ races.
- Termination paths from SPI core error handling and controller remove.
- Scatterlist DMA-mapped transfers near `MAX_DMA_LEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-pci.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-pci.c

## Purpose
`spi-pxa2xx-pci.c` is PCI glue for PXA2xx-compatible Intel SPI/SSP controllers, including Quark X1000, Bay Trail, Merrifield, Braswell, CE4100, and Lynx Point. It maps PCI resources, creates fixed-rate clocks, fills `pxa2xx_spi_controller` and `ssp_device` platform data, wires platform-specific DMA filter parameters, and delegates the actual SPI controller implementation to `pxa2xx_spi_probe()`.

## Important APIs, Types, And Functions
- `struct pxa_spi_info` holds a setup callback selected from the PCI ID table.
- Static `dw_dma_slave` structures encode source/destination request IDs for each LPSS/Merrifield/Braswell/LPT instance.
- `pxa2xx_spi_pci_clk_register()` creates a fixed-rate clock named from the SSP port ID.
- `lpss_dma_filter()` binds DesignWare DMA channels by `dma_dev` and stores the slave config in `chan->private`.
- `lpss_spi_setup()`, `mrfld_spi_setup()`, `ce4100_spi_setup()`, and `qrk_spi_setup()` fill SSP type, port ID, chip select count, clock rate, DMA parameters, and DMA burst size.
- `pxa2xx_spi_pci_probe()` enables the PCI function, maps BAR0, runs the selected setup, allocates IRQ vectors, calls the PXA2xx core probe, and enables runtime PM.
- `pxa2xx_spi_pci_remove()` disables runtime PM and calls `pxa2xx_spi_remove()`.

## Control Flow
The PCI ID table associates each supported device with a setup profile. Probe uses managed PCI enablement and BAR mapping, allocates a controller data object, initializes `ssp_device` physical/MMIO fields, applies the selected profile, marks the device bus-master capable, allocates one IRQ vector, stores `ssp->irq`, and calls the shared PXA2xx core. Runtime PM autosuspend is configured only after the core probe succeeds.

## State And Persistence Behavior
This file creates only runtime kernel state. Fixed-rate clocks are registered with a managed cleanup action. DMA device references from `pci_get_slot()` are released via managed cleanup. `pxa2xx_spi_controller` and embedded `ssp_device` persist for the PCI device lifetime and are consumed by `spi-pxa2xx.c`.

## Dependencies And Integration Points
The file integrates PCI, runtime PM, fixed-rate clock provider, DesignWare DMA platform data, and the exported `"SPI_PXA2xx"` namespace from the core driver. Hardware identity and per-function port numbering are encoded in the PCI ID table and setup switch statements.

## Risks
- Correct DMA operation depends on hard-coded DMA request IDs and DMA-device slot lookup for each Intel platform.
- `pci_get_slot()` returning NULL is not explicitly checked before storing `dma_dev->dev`, so unusual PCI topology could be fragile.
- CE4100 sets `num_chipselect` to `devfn`, which is legacy-specific and should be tested with actual firmware descriptions.
- Runtime PM is enabled after core probe; failures before that rely on managed cleanup plus PCI core cleanup.

## Test Signals
- Probe/remove for every PCI ID table entry.
- DMA channel matching on BYT, BSW, LPT, and MRFLD devices.
- Fixed-rate clock registration names and rates: 50 MHz LPSS/Quark, 25 MHz MRFLD, 3.6864 MHz CE4100.
- IRQ vector allocation and transfer IRQ delivery.
- Runtime autosuspend/resume after transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-platform.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-platform.c

## Purpose
`spi-pxa2xx-platform.c` is platform/ACPI/OF glue for the shared PXA2xx SSP SPI core. It discovers or requests an `ssp_device`, initializes platform data from firmware properties, configures optional Intel LPSS private DMA matching, enables runtime PM, and delegates controller registration to `pxa2xx_spi_probe()`.

## Important APIs, Types, And Functions
- `pxa2xx_spi_idma_filter()` matches iDMA channels by parent device pointer.
- `pxa2xx_spi_init_ssp()` maps MMIO resources, gets the SSP clock and IRQ, sets SSP type and ACPI UID-derived port ID.
- `pxa2xx_spi_ssp_request()` requests an already-registered PXA SSP device and installs managed release.
- `pxa2xx_spi_init_pdata()` builds `struct pxa2xx_spi_controller` from platform data, match data, or firmware property `intel,spi-pxa2xx-type`.
- `pxa2xx_spi_platform_probe()` initializes runtime PM and calls `pxa2xx_spi_probe()`.
- `pxa2xx_spi_platform_remove()` resumes the device, calls core remove, and disables runtime PM.
- ACPI and OF match tables enumerate Intel ACPI IDs and `marvell,mmp2-ssp`.

## Control Flow
Probe first uses explicit platform data if present; otherwise it builds it. `pxa2xx_spi_init_pdata()` prefers an existing SSP registry entry from `pxa_ssp_request()`, then match data, then the Intel type property. It sets `num_chipselect`, target/slave mode, DMA defaults, and initializes an embedded `ssp_device` if no external SSP object exists. The platform probe enables runtime PM with a 50 ms autosuspend delay and calls the common core.

## State And Persistence Behavior
The platform data and embedded `ssp_device` are managed allocations tied to the platform device. Runtime PM state is enabled at probe and disabled on remove. No persistent storage is used. If an external SSP device is requested, a managed release action returns it to the PXA SSP subsystem.

## Dependencies And Integration Points
The file integrates ACPI, OF match data, generic device properties, platform resources, clock lookup, `pxa_ssp_request()/pxa_ssp_free()`, runtime PM, optional iDMA filtering, and the exported PXA2xx SPI core API. It imports the `"SPI_PXA2xx"` namespace and has a soft dependency on `dw_dmac`.

## Risks
- Firmware must provide either an existing SSP, match data, or a valid `intel,spi-pxa2xx-type`; otherwise probe fails as missing platform data.
- DMA is enabled by default and may later be disabled by the core if channels are unavailable; this fallback should be expected.
- ACPI UID parsing controls bus numbering; missing UID maps to `-1`.
- Remove uses `pm_runtime_get_sync()` without checking a negative return before core remove.

## Test Signals
- ACPI IDs `80860F0E`, `8086228E`, `INT33C0`, `INT33C1`, `INT3430`, and `INT3431`.
- OF `marvell,mmp2-ssp` match data.
- Existing PXA SSP registry path versus embedded SSP initialization path.
- `spi-slave`, `num-cs`, and Intel type firmware properties.
- Runtime PM autosuspend and remove sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.c

## Purpose
`spi-pxa2xx.c` is the shared PXA2xx SSP SPI controller core. It supports PXA/CE4100/Quark/Merrifield/Intel LPSS/MMP2 SSP variants, SPI host and target modes, interrupt-driven PIO transfers, DMA transfers through `spi-pxa2xx-dma.c`, LPSS private chip-select handling, runtime/system PM, and exported probe/remove/PM APIs for PCI and platform glue.

## Important APIs, Types, And Functions
- `struct chip_data` stores per-SPI-device CR1 mode bits, Quark DDS rate, FIFO thresholds, and LPSS/MRFLD thresholds.
- `struct lpss_config` describes LPSS private register offsets, thresholds, chip-select select fields, and clock-gating quirks.
- `pxa2xx_spi_probe()` and `pxa2xx_spi_remove()` are exported in namespace `"SPI_PXA2xx"` for glue drivers.
- `pxa2xx_spi_transfer_one()` is the central transfer path, selecting PIO/DMA, programming clocks and frame size, configuring FIFO thresholds, enabling SSP, and returning asynchronous completion.
- `ssp_int()` is the shared IRQ top-level handler; it filters shared/powered-off IRQs and dispatches to `interrupt_transfer()` or `pxa2xx_spi_dma_transfer()`.
- `interrupt_transfer()` drains RX, fills TX, handles overrun/underrun/timeout, and finalizes PIO transfers.
- `setup()` and `cleanup()` allocate/free per-device `chip_data`.
- LPSS helpers `lpss_ssp_setup()`, `lpss_ssp_select_cs()`, and `lpss_ssp_cs_control()` configure private registers and software CS.
- PM operations are exported through `pxa2xx_spi_pm_ops`.

## Control Flow
Glue code constructs `struct pxa2xx_spi_controller` and `struct ssp_device`, then calls `pxa2xx_spi_probe()`. The core allocates host or target controller, initializes mode/bpw masks and callbacks, requests a shared IRQ, attempts DMA setup if requested, enables the SSP clock, programs default SSCR registers per SSP type, initializes LPSS private registers and CS count where applicable, optionally gets target ready GPIO, and registers the SPI controller.

Per-device `setup()` computes thresholds and CR1 mode bits from SSP type, SPI mode, and target/host role. On each transfer, `pxa2xx_spi_transfer_one()` flushes the FIFO, sets TX/RX cursors, computes clock divider including Quark DDS handling, selects reader/writer functions based on bits-per-word, prepares DMA if the SPI core DMA-mapped the transfer, programs SSCR0/SSCR1 and variant threshold registers, enables SSP, primes target-mode TX data and ready GPIO, then enables service/interrupt bits. Completion happens in the IRQ handler for PIO or DMA callback/overrun handling for DMA.

## State And Persistence Behavior
The driver maintains controller lifetime state in `struct driver_data`: SSP pointer/type, controller pointer, masks, DMA running flag, active transfer cursors, active reader/writer callbacks, transfer handler, LPSS base, and optional ready GPIO. Per-device state persists in `chip_data`. Hardware registers are reprogrammed per transfer when relevant. Runtime PM only gates the SSP clock; system suspend stops the SPI queue, disables SSP, and conditionally disables the clock depending on runtime state.

## Dependencies And Integration Points
The core depends on PXA SSP register definitions/helpers, SPI core asynchronous transfer API, DMA support from `spi-pxa2xx-dma.c`, platform data/glue in `spi-pxa2xx-platform.c` and `spi-pxa2xx-pci.c`, clocks, GPIO descriptors, runtime PM, firmware CS translation, and target-mode SPI support. It exports its APIs under `"SPI_PXA2xx"`.

## Risks
- Variant-specific masks and thresholds are complex; regressions can affect only one SSP generation.
- Transfer length is assumed to align with bits-per-word because `n_words = len / w_size`; odd lengths with wide words need SPI core validation coverage.
- MMP2 has special behavior where disabling SSE corrupts RX FIFO, and code works around possible garbage in TX FIFO.
- DMA is limited to `MAX_DMA_LEN` and transfers larger than that are forced to PIO with a ratelimited warning.
- LPSS CS switching uses a delay derived from `max_speed_hz` and toggles private clock-gating registers for some variants.
- Shared IRQ filtering must correctly handle runtime-suspended or powered-off devices.

## Test Signals
- PIO transfers for 4-32 bpw, TX-only, RX-only, and full-duplex paths.
- DMA transfer setup, completion, overrun race, and fallback when channels are absent.
- Quark DDS clock divisor accuracy and CE4100/PXA25x clock paths.
- LPSS chip-select selection, CS-high behavior, and clock-gating workaround.
- Target mode with `ready` GPIO.
- Runtime PM, system suspend/resume, and shared IRQ noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.h -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.h

## Purpose
`spi-pxa2xx.h` is the private shared header for the PXA2xx SPI core, DMA helper, and glue drivers. It defines the controller platform-data contract, the shared runtime `driver_data`, register access helpers, DMA constants, and exported core/DMA/PM entry points.

## Important APIs, Types, And Functions
- `struct pxa2xx_spi_controller` is the glue-to-core configuration: chip-select count, DMA enable/burst size/filter parameters, target/slave mode, and embedded `ssp_device` for non-PXA enumeration.
- `struct driver_data` is the central runtime state used by core and DMA code: SSP, type, SPI controller, masks, `atomic_t dma_running`, transfer cursors, bytes-per-word, reader/writer callbacks, transfer handler, LPSS base, and optional ready GPIO.
- `pxa2xx_spi_read()` and `pxa2xx_spi_write()` wrap PXA SSP register access.
- `pxa25x_ssp_comp()`, `clear_SSCR1_bits()`, `read_SSSR_bits()`, and `write_SSSR_CS()` encode common variant-specific register handling.
- Constants `DMA_ALIGNMENT`, `MAX_DMA_LEN`, and `DEFAULT_DMA_CR1` define DMA constraints and service bits.
- Declarations expose DMA helper functions, `pxa2xx_spi_probe()`, `pxa2xx_spi_remove()`, and `pxa2xx_spi_pm_ops`.

## Control Flow
The header itself has no runtime control flow, but it defines the shared call graph: platform/PCI glue fills `pxa2xx_spi_controller` and calls `pxa2xx_spi_probe()`, the core fills `driver_data`, transfer code optionally calls DMA helpers, and remove/PM callbacks are shared back to glue modules.

## State And Persistence Behavior
All state described here is in-memory kernel runtime state. The embedded `ssp_device` allows glue drivers without legacy PXA SSP registration to still pass MMIO/IRQ/clock/type data to the core. The `atomic_t dma_running` field is a cross-file synchronization point between DMA callbacks and IRQ error handling.

## Dependencies And Integration Points
This header depends on Linux DMA engine, IRQ return types, size constants, `linux/pxa2xx_ssp.h`, SPI forward declarations, and GPIO descriptors. It is the integration boundary between `spi-pxa2xx.c`, `spi-pxa2xx-dma.c`, `spi-pxa2xx-platform.c`, and `spi-pxa2xx-pci.c`.

## Risks
- Any change to `struct driver_data` affects both core and DMA code.
- `write_SSSR_CS()` preserves alternate frame bits only for CE4100 and Quark; adding variants requires revisiting this helper.
- `MAX_DMA_LEN` and `DMA_ALIGNMENT` are exported policy for all glue users.
- The platform-data structure mixes firmware-derived config, DMA filter state, and embedded hardware object, so initialization ownership must remain clear.

## Test Signals
- Compile coverage with and without each PXA2xx glue module.
- DMA and non-DMA builds using all declared helper functions.
- Variant behavior in `pxa25x_ssp_comp()` and `write_SSSR_CS()`.
- Namespace imports from PCI/platform modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qcom-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-qcom-qspi.c

## Purpose
`spi-qcom-qspi.c` is a Qualcomm QSPI controller driver for standard half-duplex SPI and SPI memory users. It supports PIO transfers through read/write FIFOs and optional descriptor-based DMA for larger transfers, manages core/interface clocks, OPP clock rates, interconnect bandwidth votes, runtime PM, and SPI memory transfer size adjustment.

## Important APIs, Types, And Functions
- `struct qcom_qspi` stores MMIO base, device, clocks, active transfer state, DMA descriptor pool/arrays, interconnect path, last speed, and an IRQ-protected spinlock.
- `struct qspi_xfer` tracks active buffer, remaining bytes, bus width, transfer direction, and fragment/last-transfer state.
- `struct qspi_cmd_desc` is the hardware DMA command descriptor.
- `qcom_qspi_transfer_one()` sets speed, records transfer direction/bus width, chooses DMA or PIO, and starts the hardware.
- `qcom_qspi_setup_dma_desc()` validates SG limits/alignment/read length and builds command descriptor chains.
- `qcom_qspi_irq()` handles PIO FIFO service, hardware errors, DMA-chain completion, descriptor freeing, and SPI transfer finalization.
- `qcom_qspi_prepare_message()` configures chip select, SPI mode, pin hold/wp, feedback clock, SBL mode, and timing delay fields.
- `qcom_qspi_adjust_op_size()` shrinks unaligned large SPI memory reads to a 4-byte multiple for DMA safety.
- Runtime/system PM hooks manage clocks, OPP rates, interconnect enablement, and pinctrl states.

## Control Flow
Probe maps registers, obtains core/interface clocks, gets the `qspi-config` interconnect path, initializes a minimal bandwidth vote for register access, requests IRQ, sets a 32-bit DMA mask, configures SPI controller capabilities, attaches optional DMA only when an IOMMU is present, sets up OPP support, creates a DMA descriptor pool, enables runtime PM, and registers the controller.

For each message, `prepare_message()` writes master config and clears DMA mode. For each transfer, `transfer_one()` updates OPP/interconnect bandwidth based on speed, records active transfer state under lock, uses DMA if the SPI core supplied SG lists, and falls back to PIO on descriptor alignment/size constraints. PIO writes are fed by `WR_FIFO_EMPTY`; PIO reads drain `RESP_FIFO_RDY`. DMA starts by writing `NEXT_DMA_DESC_ADDR`; `DMA_CHAIN_DONE` frees descriptors and finalizes.

## State And Persistence Behavior
Runtime state includes `last_speed`, interconnect bandwidth vote, active `xfer`, and outstanding DMA descriptors. The driver stores descriptor virtual and DMA addresses until IRQ completion or error handling frees them. Runtime suspend drops OPP rate, disables clocks, disables ICC, and selects sleep pinctrl; runtime resume reverses that and restores the last OPP-derived core rate.

## Dependencies And Integration Points
The driver integrates platform/OF probing, SPI core, `spi_mem` adjustment, DMA pools, DMA mapping constraints, interconnect framework, OPP, clock bulk API, pinctrl, runtime/system PM, and an optional IOMMU-aware DMA path. It advertises dual/quad TX/RX and `SPI_CONTROLLER_HALF_DUPLEX`.

## Risks
- DMA supports at most `QSPI_MAX_SG` entries and requires 32-byte aligned DMA addresses; otherwise it falls back to PIO.
- DMA reads with non-4-byte lengths are unsafe because hardware writes whole words, so `spi_mem` adjustment and fallback paths are critical.
- Error IRQs log FIFO/NOC faults but completion status propagation is limited because the IRQ finalizes through SPI core without storing a rich error in active state.
- Descriptor cleanup must occur on all error and completion paths to avoid DMA pool leaks.
- Speed changes affect both OPP and ICC; runtime resume uses `last_speed * 4`, so zero/initial-speed behavior depends on transfer ordering.

## Test Signals
- PIO reads/writes for 1/2/4 bus widths and short transfers.
- DMA transfers with aligned SG, too many SG entries, unaligned DMA address, and non-word-multiple reads.
- `spi_mem` large read adjustment and follow-up residual transfer.
- IRQ error bits: response FIFO underrun, write FIFO overrun, and NOC response error.
- Runtime PM suspend/resume with clock, OPP, ICC, and pinctrl transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qcom-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qpic-snand.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-qpic-snand.c

## Purpose
`spi-qpic-snand.c` is a Qualcomm QPIC SPI-NAND controller driver for IPQ9574-class hardware. It exposes a `spi_controller` with `spi_mem` operations, maps SPI-NAND opcodes to QPIC NAND controller commands, integrates a pipelined on-host NAND ECC engine, and uses the common Qualcomm NAND controller BAM/DMA helper layer for register/data transactions.

## Important APIs, Types, And Functions
- `struct qpic_spi_nand` links the QPIC NAND controller, SPI controller, MTD, ECC engine/config, buffers, cached command/address values, codeword count, and current IO mode flags.
- `struct qpic_ecc` stores ECC geometry and precomputed raw/ECC register configurations.
- `qcom_spi_probe()` allocates QPIC/SPI/NAND state, maps resources, maps controller registers for DMA, allocates common NAND resources, initializes SPI config, registers the ECC engine, and registers the SPI controller.
- `qcom_spi_mem_ops` provides `supports_op` and `exec_op`; `qcom_spi_mem_caps` advertises ECC support.
- ECC engine callbacks `qcom_spi_ecc_init_ctx_pipelined()`, `cleanup_ctx`, `prepare_io_req`, and `finish_io_req` configure BCH ECC and record per-request flags/statistics.
- Page read/write paths include `qcom_spi_read_page_raw()`, `qcom_spi_read_page_ecc()`, `qcom_spi_read_page_oob()`, `qcom_spi_program_raw()`, `qcom_spi_program_ecc()`, and `qcom_spi_program_oob()`.
- `qcom_spi_cmd_mapping()`, `qcom_spi_send_cmdaddr()`, and `qcom_spi_io_op()` implement opcode-level SPI-NAND command handling.

## Control Flow
Probe sets up clocks (`core`, `aon`, `iom`), maps the NAND register resource, maps it for DMA, allocates common BAM/NAND structures, writes SPI config/address/busy-wait registers through descriptors, registers the pipelined ECC engine, and exposes a one-CS SPI memory controller with dual/quad mode bits.

ECC initialization derives codewords per page, validates step size and strength, allocates OOB buffer, re-allocates BAM transaction capacity for the page geometry, fills raw and ECC register configs, installs OOB layout, and initializes erased-page status registers. `prepare_io_req` sets `page_rw`, `oob_rw`, and `raw_rw` for later `spi_mem` operations; `finish_io_req` updates MTD ECC statistics.

For `spi_mem` execution, page operations are detected from bus widths/address shape. Page read paths build BAM descriptors for raw/ECC/OOB codeword reads, submit them, and inspect flash/ECC status. Program paths cache page data at `PROGRAM_LOAD`, then execute raw/ECC/OOB writes on `PROGRAM_EXECUTE`. Non-page commands handle reset, read ID, get/set feature, write-enable, erase, and read command/address sequencing.

## State And Persistence Behavior
The driver uses in-memory QPIC NAND controller state, BAM transaction state, ECC context stored in `nand->ecc.ctx.priv`, and buffers allocated for data/OOB. Current operation flags and cached command/address/data pointers in `qpic_spi_nand` persist only across the SPI-NAND multi-op sequence needed to load data then execute program/read. ECC statistics are accumulated into MTD stats after read requests.

## Dependencies And Integration Points
This driver depends on `linux/mtd/nand-qpic-common.h`, SPI memory, SPI-NAND/MTD NAND ECC APIs, DMA mapping, QCOM BAM/ADM DMA helpers, clocks, OF match data, and platform resources. It is not a generic SPI controller in practice; it is a SPI-NAND memory controller with ECC-aware `spi_mem` operations.

## Risks
- ECC support is limited to 512-byte step size and 4-bit or 8-bit strength.
- OOB/bad-block-marker handling includes a TODO workaround duplicating the bad block marker until SPI-NAND supports a single-byte marker.
- The code casts feature data through `u32 *` and copies fixed 4-byte buffers for feature/read-id paths; endianness and size assumptions need hardware coverage.
- BAM transaction allocation is resized during ECC init; failure paths must avoid leaving stale transaction state.
- Page operation detection is specialized and may reject valid future SPI-NAND op shapes.
- `qcom_spi_write_page()` currently caches data for `PROGRAM_LOAD` but otherwise returns after command mapping; sequencing depends on later `PROGRAM_EXECUTE`.

## Test Signals
- Probe on `qcom,ipq9574-snand` with all three clocks and BAM-capable resources.
- SPI-NAND reset, read ID, get/set feature, write-enable, erase, read, program-load, and program-execute operations.
- ECC init with default/user/required 4-bit and 8-bit strengths, plus unsupported strengths/step sizes.
- Raw, ECC, and OOB read/write modes and MTD ECC statistic updates.
- Bad block marker placement and erased-page detection.
- BAM descriptor submission failures and cleanup/unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qpic-snand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qup.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-qup.c

## Purpose
`spi-qup.c` is the Qualcomm QUP SPI controller driver for QUP v1/v2 hardware. It supports FIFO, block, and BAM/DMOV-style DMA transfer modes, programs QUP/SPI state machines, handles native chip select for newer QUP versions, manages clocks/OPP/interconnect bandwidth, and provides runtime/system PM.

## Important APIs, Types, And Functions
- `struct spi_qup` stores register base, clocks, interconnect path, IRQ, FIFO/block sizes, active transfer state, completion/error state, word size/count, TX/RX buffer cursors, QUP version flag, DMA mode, DMA configs, and current bandwidth vote.
- `spi_qup_set_state()` transitions QUP among RESET/RUN/PAUSE with validity polling and special PAUSE-to-RESET handling.
- `spi_qup_io_prep()` chooses FIFO, block, or DMA mode based on transfer size, DMA mapping, and loopback constraints.
- `spi_qup_io_config()` resets/configures counters, IO modes, pack/unpack, SPI clock polarity/phase/loopback/high-speed mode, QUP config, and IRQ masks for a transfer.
- `spi_qup_do_pio()` runs FIFO/block transfers and waits for IRQ completion.
- `spi_qup_do_dma()` chunks SG lists to `SPI_MAX_XFER`, prepares DMA descriptors, starts QUP RUN state, issues DMA, and waits for completion.
- `spi_qup_qup_irq()` handles QUP/SPI error flags, FIFO/block service flags, DMA operational acks, and transfer completion.
- `spi_qup_probe()` maps resources, gets clocks/ICC/OPP, initializes DMA if available, discovers FIFO/block sizes, resets hardware, requests IRQ, enables PM, and registers the controller.

## Control Flow
Probe reads `spi-max-frequency` and `num-cs`, creates a SPI host, optionally acquires DMA channels, determines QUP version from OF match data, enables clocks, derives FIFO and block sizes from `QUP_IO_M_MODES`, resets the hardware, enables error interrupts, configures baseline SPI IO control, requests IRQ, enables runtime PM, and registers.

For each transfer, `spi_qup_transfer_one()` prepares mode and timeout, resets byte counters and error state, then runs DMA or PIO. PIO mode may split large transfers into `SPI_MAX_XFER` iterations and falls back to FIFO for small chunks; it sequences RESET, RUN, PAUSE, optional initial FIFO write, RUN, then waits for completion. DMA mode walks RX/TX SG lists in bounded chunks, configures IO for each chunk, starts QUP RUN, submits DMA descriptors, and waits for the DMA callback completion. Both paths reset QUP after completion and terminate DMA on errors.

## State And Persistence Behavior
Active transfer state is stored in `struct spi_qup` and protected by a spinlock where shared with IRQ. Completion state is per transfer via `struct completion done`. Bandwidth votes persist as `bw_speed_hz` and are changed on DMA transfer speed changes and PM suspend. Runtime suspend enables QUP clock auto-gating, disables clocks, votes ICC bandwidth to zero, and runtime resume reenables clocks and disables auto-gating.

## Dependencies And Integration Points
The driver integrates platform/OF probing for `qcom,spi-qup-v1.1.1`, `qcom,spi-qup-v2.1.1`, and `qcom,spi-qup-v2.2.1`; SPI core; DMA engine; OPP; interconnect; runtime/system PM; clock framework; and optional GPIO descriptors. It includes SPI internals for DMA mapping helpers and advertises 4-32 bpw, mode 0-3, loopback, and up to four native chip selects.

## Risks
- QUP state transitions are timing-sensitive and return `-EIO` after short polling loops.
- DMA eligibility depends on cache alignment, channel availability, QUP version block alignment, and transfer size; boundary coverage is important.
- Timeout is computed from speed and length with a 100x multiplier; extremely low or unusual speeds may stress the calculation.
- IRQ error handling stores only the first error and still services flags; races with completion need coverage.
- Runtime/system PM sequencing touches clocks and ICC in different orders; suspend while runtime-suspended has an explicit resume path.
- QUP v1 lacks native CS handling and masks input overrun differently from newer hardware.

## Test Signals
- FIFO, block, and DMA transfers with TX-only, RX-only, and full-duplex buffers.
- QUP v1 and v2 OF matches, native CS behavior, and GPIO CS fallback.
- DMA alignment and block-size rejection cases.
- QUP/SPI error flags: overrun, underrun, clock over/underrun.
- Loopback size limit and high-speed mode threshold.
- Runtime PM autosuspend/resume and system suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-qup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rb4xx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-rb4xx.c

## Purpose
`spi-rb4xx.c` is a minimal SPI controller driver for MikroTik RB4xx boards using AR71xx-style GPIO-mode SPI registers. It bit-bangs bytes through a memory-mapped IOC register, supports a board-specific dual-bit transmit mode for the CPLD, and exposes three chip selects.

## Important APIs, Types, And Functions
- `struct rb4xx_spi` stores the MMIO base and AHB clock.
- `rb4xx_read()` and `rb4xx_write()` access raw registers.
- `do_spi_clk()` clocks one output bit through DO and CLK fields.
- `do_spi_byte()` sends one byte MSB-first in single-bit mode.
- `do_spi_clk_two()` and `do_spi_byte_two()` send two bits per clock using CS2 as the second data line.
- `rb4xx_transfer_one()` selects board-specific CS mask, bit-bangs each byte, optionally reads `RDS`, and finalizes the transfer.
- `rb4xx_spi_probe()` maps resources, enables AHB clock, configures SPI controller capabilities, registers it, and switches hardware to GPIO/SPI function mode.

## Control Flow
Probe maps the MMIO resource, allocates a SPI host, enables the AHB clock, sets `num_chipselect = 3`, advertises `SPI_TX_DUAL`, requires TX buffers, registers `transfer_one` and `set_cs`, then writes the function-select register to enable GPIO SPI mode. Transfers compute the IOC chip-select baseline: CS2 devices use CS0 for MMC, while boot flash/CPLD use CS1 due to board wiring. Each TX byte is clocked as single-bit or dual-bit based on `t->tx_nbits`; RX reads capture the read-data-shift register after each byte.

## State And Persistence Behavior
The driver has no persistent storage and minimal runtime state. It does not maintain per-device state. Chip select is encoded directly in each IOC write during bit-banging. Probe-managed resources handle lifetime cleanup.

## Dependencies And Integration Points
It depends on platform/OF matching (`mikrotik,rb4xx-spi`), the common clock framework, SPI core, and board-specific AR71xx register semantics. It marks `SPI_CONTROLLER_MUST_TX`, so the SPI core should provide dummy TX when clients request reads.

## Risks
- Board-specific CS sharing between boot flash and CPLD is encoded in the transfer path and relies on non-clashing command sets.
- Dual-bit mode abuses CS2 as a second data output, so generic dual-SPI assumptions do not apply.
- There is no speed control, delay tuning, error reporting, or runtime PM.
- Raw MMIO access and bit-banging depend on CPU timing and AHB clock behavior.

## Test Signals
- Boot flash, CPLD, and MMC chip-select behavior on RB4xx hardware.
- Single-bit and `SPI_NBITS_DUAL` TX transfers.
- RX sampling from `RDS` with controller-provided dummy TX.
- Probe with AHB clock and function-select register write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-rb4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl-snand.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl-snand.c

## Purpose
`spi-realtek-rtl-snand.c` is a SPI memory controller driver for Realtek RTL930x SPI-NAND controllers. It implements `spi_mem` operations using command/address/dummy/data phases, supports dual/quad bus widths, switches between small PIO-style register transfers and DMA for larger data phases, and uses IRQ completion for DMA.

## Important APIs, Types, And Functions
- `struct rtl_snand` stores device, regmap, and DMA completion.
- `rtl_snand_supports_op()` accepts default-supported `spi_mem` ops with one-byte single-lane commands.
- `rtl_snand_xfer_head()` asserts CS and emits command, address, and dummy phases with appropriate bus-width register fields.
- `rtl_snand_xfer()` handles small data phases in up-to-4-byte chunks through read/write command/data registers.
- `rtl_snand_dma_xfer()` maps the data buffer, enables DMA IRQ, chunks DMA lengths, starts DMA direction triggers, waits for completion, and unmaps.
- `rtl_snand_irq()` acknowledges DMA interrupt and completes the wait unless status indicates controller/data read/write busy bits.
- `rtl_snand_exec_op()` chooses DMA for data phases larger than 32 bytes.
- `rtl_snand_probe()` maps registers through regmap, sets 32-bit DMA mask, requests IRQ, configures SPI memory capabilities, and registers the controller.

## Control Flow
Probe allocates a SPI host, initializes MMIO regmap, completion, IRQ, and DMA mask, then registers a two-chip-select controller with `spi_mem` ops and dual/quad mode bits. Execution starts in `rtl_snand_exec_op()`, logs the operation, chooses PIO or DMA, and wraps all operations with explicit CS assert/deassert. The head function sends command/address/dummy phases and waits for controller idle between each. PIO loops over data chunks; DMA maps the full buffer, then runs one or more controller DMA chunks with max read length 2080 bytes and max write length 520 bytes.

## State And Persistence Behavior
Runtime state is limited to regmap and the DMA completion. No per-device state is stored. DMA transfers use a transient DMA mapping and temporarily enable `SNAFCFR_DMA_IE`; it is disabled on exit. CS state is written directly through `SNAFCCR`.

## Dependencies And Integration Points
The driver integrates platform/OF matching for RTL9301/RTL9302/RTL9303 SNAND compatibles, SPI memory, regmap MMIO, DMA mapping, IRQ completions, and the SPI core. It is specialized for SPI-NAND-style memory operations rather than full-duplex SPI messages.

## Risks
- `rtl_snand_irq()` returns `IRQ_NONE` when busy/status bits are set; incorrect status interpretation could lead to DMA timeouts.
- DMA maps `op->data.buf.in` even for output direction through the union field; this works only if the union pointer layout is valid and should be tested carefully.
- DMA chunk sizes are hard-coded and asymmetric for reads/writes.
- PIO copies raw register-endian `u32` values into buffers for partial chunks, so endianness must match hardware expectations.
- DMA timeout is fixed at 20 ms per chunk.

## Test Signals
- PIO operations for command-only, address, dummy, small read, and small write phases.
- DMA reads over 2080 bytes and writes over 520 bytes to exercise chunking.
- Dual/quad address/data bus-width operations.
- IRQ completion, timeout path, and DMA interrupt disable/unmap cleanup.
- Probe on each RTL930x compatible with 32-bit DMA mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl-snand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl.c

## Purpose
`spi-realtek-rtl.c` is a simple half-duplex SPI controller driver for Realtek RTL838x/RTL839x SoC SPI flash blocks. It sends or receives data through 1-byte and 4-byte register accesses, controls CS0, initializes byte ordering, and registers a basic SPI controller.

## Important APIs, Types, And Functions
- `struct rtspi` stores the MMIO base.
- `rt_set_cs()` toggles CS0 through `RTL_SPI_SFCSR`.
- `set_size()` selects 1-byte or 4-byte transfer length in the status/control register.
- `wait_ready()` busy-waits for `RTL_SPI_SFCSR_RDY`.
- `send4()`, `send1()`, `rcv4()`, and `rcv1()` perform blocking register transfers.
- `transfer_one()` handles TX-only or RX-only transfers in 4-byte chunks followed by 1-byte residue.
- `init_hw()` enables read/write big-endian byte ordering, disables CS1, and selects CS0.
- `realtek_rtl_spi_probe()` maps registers, initializes hardware, configures half-duplex callbacks, and registers the controller.

## Control Flow
Probe allocates a SPI host, maps the register resource, calls `init_hw()`, sets `SPI_CONTROLLER_HALF_DUPLEX`, assigns `set_cs` and `transfer_one`, and registers. Transfer execution checks whether TX or RX is present, then loops over 4-byte operations and remaining bytes. Each operation waits for hardware ready, sets transfer size, and writes or reads `SFDR`; completion is signaled immediately after the loop.

## State And Persistence Behavior
The driver holds only the register base as runtime state. There is no per-device state, no DMA, no IRQ, and no PM logic. Hardware byte-order and CS1-disabled state are initialized at probe and remain until reset/remove.

## Dependencies And Integration Points
It integrates with platform/OF matching for RTL8380/RTL8382/RTL8391/RTL8392/RTL8393 SPI blocks, the SPI core, and MMIO resource mapping. It exposes only half-duplex transfer behavior and does not advertise mode/bpw constraints beyond defaults.

## Risks
- `wait_ready()` has no timeout, so hardware lockup can spin forever.
- No explicit mode bits, speed programming, IRQ, DMA, or runtime PM are implemented.
- `init_hw()` uses `value &= RTL_SPI_SFCSR_CS`, which preserves only the CS select bit and clears other fields before writing; this depends on hardware reset/default expectations.
- TX and RX are mutually exclusive; full-duplex clients rely on SPI core half-duplex constraints.

## Test Signals
- Probe on each listed Realtek compatible.
- TX-only and RX-only transfers with lengths divisible by 4 and with 1-3 byte residues.
- CS0 assert/deassert polarity.
- Hardware-ready wait behavior under slow flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl.c -->
