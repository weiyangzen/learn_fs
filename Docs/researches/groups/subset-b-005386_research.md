# Research: subset-b-005386

Grouped research for SPI driver sources under `sources/distributed-fs/ceph-client/drivers/spi/`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-xspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-xspi.c

Purpose: NXP xSPI SPI-mem host driver for `nxp,imx94-xspi`. It supports single/dual/quad/octal bus widths, SDR and the controller's 8D-8D-8D DTR path, dynamically programs one LUT slot per `spi_mem_op`, and chooses AHB mapped reads when possible versus IP-triggered FIFO operations for writes and out-of-range reads.

Important APIs, types, and functions: `struct nxp_xspi` stores register mappings, memory window, clock, completion, mutex, selected chip select, DTR flag, previous operation rate, and device capability data. `struct nxp_xspi_devtype_data` carries RX/TX FIFO and AHB buffer sizes plus quirks. The driver registers `spi_controller_mem_ops` through `nxp_xspi_mem_ops`: `supports_op`, `adjust_op_size`, `exec_op`, and `get_name`; capabilities include DTR, per-op frequency, and `swap16`. Core helpers are `nxp_xspi_prepare_lut()`, `nxp_xspi_select_mem()`, `nxp_xspi_ahb_read()`, `nxp_xspi_do_op()`, FIFO helpers, DDR/DLL setup, reset, default setup, runtime/system PM, and IRQ completion on `XSPI_FR_TFF`.

Control flow: probe allocates a devm SPI host, maps the `"base"` registers and `"mmap"` resource, enables runtime PM, clears flags, runs `nxp_xspi_default_setup()`, requests the IRQ, initializes the mutex and cleanup action, then registers a SPI-mem controller. Each operation takes the driver mutex, resumes runtime PM, waits for not busy, reselects/reclocks/configures DDR state if CS, DTR state, or op rate changed, rewrites the LUT, chooses AHB read for in-range reads, otherwise triggers an IP command and waits for completion. After every op it software-resets controller logic.

State and persistence: persistent state is hardware register configuration, current memory mapping cache (`ahb_addr`, `memmap_start`, `memmap_len`), selected CS, DTR flag, and `pre_op_rate`. Runtime suspend disables the module and clock; resume re-enables them; system resume reruns default setup and pinctrl restore. Cleanup disables interrupts, clears flags, disables hardware, and unmaps cached AHB memory.

Dependencies and integration points: integrates with `spi-mem`, platform resources, device tree match data, runtime PM, pinctrl sleep/default states, Linux clock framework, MMIO, completions, and `readl_poll_timeout`. It is optimized for memory devices rather than generic `transfer_one`.

Risks: LUT construction is central and must match SDR/DTR opcode/address/dummy/data encoding. `nxp_xspi_select_mem()` changes the clock while choosing DDR/STR and depends on successful clock programming; failures return early after the clock may have been disabled. FIFO code has alignment-sensitive casts and appends `0xff` for unaligned writes. AHB remapping changes per read range and must not exceed `memmap_phy_size`; IP reads are capped by RX FIFO when quirks require it. Several timeouts use warnings but leave recovery to the reset after op.

Test signals: useful coverage includes SPI NOR read/write/erase through spi-mem, octal DTR transactions, per-op frequency changes, crossing the AHB memory-map boundary to exercise `adjust_op_size()`, unaligned write lengths, runtime suspend/resume and system suspend/resume, IRQ timeout paths, and multi-chip-select naming/selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-xspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-oc-tiny.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-oc-tiny.c

Purpose: OpenCores tiny SPI host driver using `spi_bitbang`. It supports a simple MMIO controller with TX/RX data, status, control, and baud registers, optionally interrupt-driven transfers, and platform data or device tree properties for base clock and baud register width.

Important APIs, types, and functions: `struct tiny_spi` embeds `struct spi_bitbang` first and tracks MMIO base, optional IRQ, frequency, baud width/current baud, mode, transfer counters, and current buffers. `tiny_spi_baud()` calculates a divider from controller frequency. `tiny_spi_setup()` caches mode and default baud; `tiny_spi_setup_transfer()` writes the selected baud and mode. `tiny_spi_txrx_bufs()` implements either IRQ or polling transfers; `tiny_spi_irq()` advances byte-at-a-time interrupt state. Probe allocates a host, maps resource 0, optionally requests IRQ, reads platform/OF timing data, and starts the bitbang engine.

Control flow: SPI core calls bitbang setup and transfer callbacks. In IRQ mode the driver primes one or two bytes, enables status interrupts by writing TXR/TXE status bits, then waits on a completion completed by `tiny_spi_irq()`. In polling mode it writes each byte, waits for TX ready or TX empty, and reads returned bytes when an RX buffer exists.

State and persistence: state is volatile per-controller and per-transfer counters in `struct tiny_spi`; no persistent storage. `speed_hz`, `baud`, and `mode` are cached to avoid repeated divider calculation. Remove stops bitbang and drops the host reference.

Dependencies and integration points: depends on `spi_bitbang`, platform resources, optional OF properties `clock-frequency` and `baud-width`, optional IRQ, and GPIO descriptors for chip select. It accepts SPI CPOL/CPHA/CS_HIGH mode bits.

Risks: there is no timeout in polling waits, so wedged hardware can spin forever. If neither platform data nor OF properties provide sane `freq` and `baudwidth`, baud calculation can be wrong. IRQ mode uses shared mutable transfer fields and assumes one active transfer through bitbang serialization. The hardware is byte-oriented only and does not advertise bits-per-word flexibility.

Test signals: verify polling and IRQ transfer paths, RX-only/TX-only/full-duplex byte streams, mode changes, divider selection at min/max speeds, GPIO chip select behavior, missing optional IRQ, and DT/platform-data initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-oc-tiny.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-adi-util-sigma-delta.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-adi-util-sigma-delta.c

Purpose: Minimal Analog Devices util-sigma-delta SPI offload trigger provider. It models the hardware block as a data-ready trigger source for SPI offload consumers and registers it with the generic SPI offload trigger registry.

Important APIs, types, and functions: `adi_util_sigma_delta_match()` accepts only `SPI_OFFLOAD_TRIGGER_DATA_READY` with zero fwnode arguments. `adi_util_sigma_delta_ops` supplies that match callback. `adi_util_sigma_delta_probe()` gets and enables the device clock with `devm_clk_get_enabled()` and registers a `spi_offload_trigger_info` using `devm_spi_offload_trigger_register()`. The platform driver matches `adi,util-sigma-delta-spi`.

Control flow: probe obtains the functional clock first so the trigger hardware is live, then registers the trigger against the device fwnode. Later, SPI offload consumers resolving a `trigger-sources` reference can match this provider only for data-ready trigger requests. There are no validate, enable, disable, request, or release callbacks, so the core registry handles lifetime while the provider exposes only identity matching.

State and persistence: no private state is stored. The enabled devm clock and registered trigger are tied to device lifetime. On removal or probe failure, devm unwinds the clock and unregisters the trigger.

Dependencies and integration points: integrates with the SPI offload provider API, fwnode references, platform bus, module OF matching, and clock framework. It relies on `spi-offload.c` to manage references and reject consumers after provider unregister.

Risks: because there are no enable/disable/validate hooks, any hardware configuration is presumed external or static once the clock is enabled. If the underlying block needs acknowledgement or edge selection, this driver does not expose it. The match callback ignores the trigger object and only validates type/nargs.

Test signals: probe with/without clock, fwnode trigger lookup from a consumer, rejection of periodic or argument-bearing trigger requests, module unload while a consumer holds a reference, and deferred clock/provider probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-adi-util-sigma-delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-pwm.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-pwm.c

Purpose: Generic PWM-backed SPI offload trigger provider. It exposes a PWM output as a periodic trigger source for offloaded SPI transfers, rounding requested frequency/offset to what the PWM controller can produce and driving a 50 percent duty waveform while enabled.

Important APIs, types, and functions: `struct spi_offload_trigger_pwm_state` stores device and PWM handles. `spi_offload_trigger_pwm_match()` accepts `SPI_OFFLOAD_TRIGGER_PERIODIC` with no fwnode args. `spi_offload_trigger_pwm_validate()` computes a `pwm_waveform`, calls `pwm_round_waveform_might_sleep()`, and writes rounded frequency/offset back to config. `spi_offload_trigger_pwm_enable()` programs the waveform. `spi_offload_trigger_pwm_disable()` reads the current waveform and sets duty to zero. Probe gets the PWM, applies an enabled zero-duty initial state, registers a devm release action that disables the PWM, and registers trigger ops.

Control flow: during probe the PWM is initialized enabled but inactive. A consumer validates a periodic config, possibly getting adjusted values. On trigger enable the offload core first enables the offload instance, then this driver sets waveform timing. Disable is called through the offload core and zeros duty to stop triggering while preserving period/offset.

State and persistence: private state is just the PWM handle and device pointer. Runtime waveform state lives in the PWM provider hardware. Devm cleanup disables the PWM at device teardown. There is no internal active flag, so disable errors are logged but not persisted.

Dependencies and integration points: integrates with the generic SPI offload trigger registry, PWM waveform API, fwnode matching through compatible `"pwm-trigger"`, and platform device probing. It expects `trigger-sources` references from offload providers/consumers to resolve to this fwnode.

Risks: duty cycle is fixed at 50 percent and has a `REVISIT`, so hardware needing pulse-width control cannot express it. Validation mutates frequency using rounded period length; consumers must re-check the returned values. `disable()` depends on reading the current waveform and logs errors without forcing state otherwise. Zero frequency is rejected.

Test signals: validate/enable/disable periodic triggers at supported and unsupported rates, offset rounding, zero-frequency rejection, PWM provider probe deferral, cleanup disabling PWM on driver removal, and interaction with offload trigger enable rollback when PWM programming fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload-trigger-pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-offload.c

Purpose: Generic SPI offload support library. It provides devm allocation/get helpers for offload providers and consumers, a global fwnode-keyed trigger registry, trigger validation/enable/disable wrappers, and DMA channel request helpers for offloaded TX/RX streams.

Important APIs, types, and functions: exported provider/consumer APIs include `devm_spi_offload_alloc()`, `devm_spi_offload_get()`, `devm_spi_offload_trigger_get()`, `spi_offload_trigger_validate()`, `spi_offload_trigger_enable()`, `spi_offload_trigger_disable()`, `devm_spi_offload_tx_stream_request_dma_chan()`, `devm_spi_offload_rx_stream_request_dma_chan()`, `devm_spi_offload_trigger_register()`, and `spi_offload_trigger_get_priv()`. Internal `struct spi_offload_trigger` has list linkage, `kref`, fwnode, lock, ops, and private pointer. A `spi_controller_and_offload` resource pairs `get_offload()` with balanced `put_offload()`.

Control flow: consumers call `devm_spi_offload_get()` on a `spi_device`; the controller's `get_offload()` supplies an instance and devm cleanup calls `put_offload()`. Trigger consumers read the provider device fwnode's `trigger-sources` reference, search the global list by fwnode and provider-specific `match()`, optionally call `request()`, then hold a kref until devm release. Enable first calls optional offload `trigger_enable()`, then trigger `enable()`, rolling back offload enable if trigger enable fails. Disable calls offload `trigger_disable()` and then trigger `disable()`.

State and persistence: global trigger list is protected by `spi_offload_triggers_lock`; each trigger has its own lock protecting ops/priv during calls and unregister. Unregister removes the list entry, nulls ops/priv, and drops the provider reference; outstanding consumers see `-ENODEV` through wrappers.

Dependencies and integration points: depends on SPI controller offload hooks, `linux/spi/offload/*` public types, fwnode reference args, devm actions, DMAEngine, mutexes, krefs, and exported namespace `SPI_OFFLOAD`.

Risks: `spi_offload_trigger_get()` calls provider `match()` while holding the global list lock and before taking the per-trigger lock, so provider unregister ordering depends on list removal and devm lifetimes. Enable/disable ordering is asymmetric: disable invokes offload disable before checking trigger ops. Consumers must balance trigger enable/disable and validate any mutated trigger config. DMA helpers assume provider returns channels that can be released with `dma_release_channel()`.

Test signals: controller without `get_offload`, invalid null args, provider probe deferral via unresolved trigger, request/release callbacks, provider unregister while consumer reference remains, enable rollback when trigger enable fails, unsupported DMA stream callbacks, and concurrent trigger lookup/register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-omap-uwire.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-omap-uwire.c

Purpose: Legacy OMAP1 MicroWire SPI interface driver using `spi_bitbang`. It maps fixed UWIRE registers, exposes four chip selects on bus 2, supports half-duplex transfers up to 16 bits per word, and computes hardware-specific two-stage clock divisors.

Important APIs, types, and functions: `struct uwire_spi` embeds bitbang and functional clock; `struct uwire_state` stores the per-device `div1_idx` needed because divider 1 is global. Register helpers operate through global `uwire_base`. Key functions are `omap_uwire_configure_mode()`, `wait_uwire_csr_flag()`, `uwire_set_clk1_div()`, `uwire_chipselect()`, `uwire_txrx()`, `uwire_setup_transfer()`, `uwire_setup()`, `uwire_cleanup()`, probe/remove, and init/exit registration.

Control flow: setup allocates per-device controller state and programs mode/dividers. Chip-select waits for controller idle, deselects old CS, restores the device's global divider, sets CPOL in SR4, and asserts `CS_CMD`. Transfers are TX-only or RX-only; TX writes one or two bytes shifted to MSB position, starts a write in CSR, waits for start and final idle. RX starts reads, waits for data-ready, masks received bits, and writes bytes back to the buffer.

State and persistence: per-device state holds only `div1_idx`; hardware state is in UWIRE SR/CSR registers. The global register base and `uwire_idx_shift` reflect platform-specific layout. Remove stops bitbang, clears SR3, disables the clock, and drops the controller.

Dependencies and integration points: depends on OMAP1 SoC headers, fixed physical address `UWIRE_BASE_PHYS`, clock `"fck"`, `spi_bitbang`, and platform device registration via `subsys_initcall`. It advertises `SPI_CONTROLLER_HALF_DUPLEX`, CPOL/CPHA/CS_HIGH, and bits-per-word 1..16.

Risks: fixed physical mapping and global base limit portability and concurrency assumptions. `BUG_ON(wait_uwire_csr_flag(...))` can crash on chipselect timeout. Polling timeouts use one second and return `-EIO` on failure. Comments note DMA and overlap opportunities are not implemented. The code assumes TX and RX are not simultaneous.

Test signals: 1/8/16-bit TX and RX, each SPI mode, CS high/low behavior, divider calculation at boundary rates, timeout behavior with nonresponsive hardware, remove clock cleanup, and multiple devices changing dividers between chip selects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-omap-uwire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-omap2-mcspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-omap2-mcspi.c

Purpose: OMAP2/OMAP4/AM654 McSPI controller driver supporting host and target mode, PIO and DMA transfers, FIFO setup, 3-wire operation, GPIO/native chip-select handling, runtime PM context restore, and SoC-specific register offsets/transfer limits.

Important APIs, types, and functions: `struct omap2_mcspi` stores controller, base/phys, DMA channels, context shadow, ref clock, FIFO state, target abort flag, pin direction, max transfer length, multi-mode flags, and last-CS state. `struct omap2_mcspi_cs` stores per-CS register base, word length, mode, and shadowed `CHCONF0/CHCTRL0`. Important functions include register/shadow helpers, DMA request/release and callbacks, `omap2_mcspi_txrx_dma()`, `omap2_mcspi_txrx_pio()`, `omap2_mcspi_setup_transfer()`, `omap2_mcspi_transfer_one()`, `prepare_message()`, runtime suspend/resume, target abort, and probe/remove.

Control flow: probe allocates host or target based on `spi-slave`, maps registers with optional offset, allocates one DMA pair per chipselect, requests IRQ, gets optional ref clock, enables runtime PM, sets wake and mode, then registers the controller. Setup allocates a per-CS state node and programs default clock/mode. `prepare_message()` decides whether multi-mode CS handling is valid for one-word transfers and clears stale FORCE bits. `transfer_one()` disables the channel, optionally overrides setup for transfer speed/bits/3-wire direction, sets TRM mode and turbo, enables FIFO for DMA-mapped transfers, enables the channel, performs DMA or PIO, checks byte count, disables channel/FIFO, restores defaults, and toggles GPIO CS if needed.

State and persistence: register context is shadowed in `ctx` and per-CS objects for runtime resume, including FORCE bit repair after off-mode wake. DMA completions and `txdone` completion synchronize interrupts. `last_msg_kept_cs` affects later multi-mode eligibility. Runtime PM switches pinctrl states and restores MODULCTRL, WAKEUPENABLE, and each CS CHCONF0.

Dependencies and integration points: integrates with SPI core host/target APIs, DMAEngine, scatterlist splitting, GPIO descriptors, pinctrl, runtime/system PM, device tree compatibles, OMAP platform data, and internal SPI helpers such as `spi_xfer_is_dma_mapped()`.

Risks: DMA RX has documented transfer length reductions and manual tail reads, with special turbo handling. FIFO enable is constrained by word alignment and max word count. Multi-mode CS logic is strict and depends on `cs_change` semantics. Target abort must unblock all completions. Runtime resume toggles FORCE to repair CS state after off-mode. PIO paths poll with one-second timeouts.

Test signals: PIO and DMA TX/RX/full-duplex across 4..32 bits, turbo RX-only, FIFO and non-FIFO DMA, 3-wire direction changes, GPIO and native CS including `cs_change`, target-mode abort/EOW IRQ, runtime/system suspend resume with active per-CS contexts, AM654 max transfer size, and missing/deferred DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-omap2-mcspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-orion.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-orion.c

Purpose: Marvell Orion/Armada SPI controller driver. It supports 8- and 16-bit PIO transfers, optional direct mapped TX window for suitable writes, runtime PM, GPIO chip selects, LSB-first mode, and SoC-specific clock divisor/erratum behavior.

Important APIs, types, and functions: `struct orion_spi_dev` describes SoC type, max/min divisors, prescale mask, max Hz, and 50 MHz erratum flag. `struct orion_spi` stores host, MMIO base, clocks, devdata, device, and per-CS direct access mapping. Key functions are `orion_spi_baudrate_set()`, `orion_spi_mode_set()`, `orion_spi_50mhz_ac_timing_erratum()`, `orion_spi_setup_transfer()`, `orion_spi_set_cs()`, 8/16-bit write-read helpers, `orion_spi_write_read()`, `orion_spi_transfer_one()`, probe/remove, reset, and runtime PM callbacks.

Control flow: probe allocates a host, resolves bus number, applies match data, enables clocks, calculates max/min speed, maps controller registers, scans child nodes for direct-access address windows, enables runtime PM, resets the controller, and registers. Each transfer programs mode, bitrate, erratum timing, and 8/16-bit mode, then either writes through a direct mapped CS window for 8-bit TX-only non-`SPI_CS_WORD` transfers or loops word-by-word through data out/in registers, clearing interrupt cause and polling ready each word.

State and persistence: hardware configuration is in IF control/config/timing registers. Per-CS direct access virtual address/size is cached at probe. Runtime suspend disables clocks; resume re-enables them. Remove unregisters controller and tears down runtime PM/clocks.

Dependencies and integration points: uses platform resources, OF match data and child address resources, optional AXI clock, runtime PM autosuspend, GPIO descriptors, SPI core transfer_one, unaligned helpers for 16-bit words, and device tree compatibles for several Marvell SoCs.

Risks: ready polling is microsecond-loop based and returns partial byte count on timeout. `SPI_CS_WORD` is only valid for 8-bit words. Direct mapped writes only map one page and only handle TX writes; future NOR/NAND direct support would need broader semantics. Clock divisor logic differs by SoC and old Armada 370 DT compatibility. AXI clock error handling must tolerate optional absence.

Test signals: mode 0..3 and LSB-first, 8/16-bit TX/RX/full-duplex, `SPI_CS_WORD`, direct-access child mapping and fallback, timeout handling, Armada 380 50 MHz CPOL/CPHA erratum, GPIO CS, runtime PM autosuspend, and old/new compatible max-speed calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pci1xxxx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pci1xxxx.c

Purpose: Microchip PCI1xxxx PCI SPI controller driver. It supports one or two hardware SPI instances exposed by PCI subsystem IDs, 7 chip selects per instance, 8-bit transfers, PIO through command/response windows, optional DMA through a separate BAR on newer PF0 devices, MSI/INTx interrupts, and suspend/resume register preservation.

Important APIs, types, and functions: `struct pci1xxxx_spi` stores PCI device, instance count, revision, MMIO bases, DMA locks, DMA availability, and per-instance pointers. `struct pci1xxxx_spi_internal` stores instance id, IRQs, mode/divider, in-progress flag, DMA SG state, abort flags, completion, host pointer, transfer pointer, and saved config. Core functions include syslock helpers, DMA capability/init/config, `pci1xxxx_spi_set_cs()`, `pci1xxxx_get_clock_div()`, DMA setup helpers, `pci1xxxx_spi_transfer_with_io()`, `pci1xxxx_spi_transfer_with_dma()`, SPI/DMA ISR handlers, probe, suspend/resume, and config store/restore.

Control flow: probe decodes instance count/start from `driver_data`, allocates parent and per-instance hosts, enables PCI and regions once, maps BAR0, allocates interrupt vectors, unmasks SPI interrupts, configures instance selection, registers each SPI controller, then attempts DMA init. PIO transfer splits TX into 320-byte chunks, copies to command buffer, configures mode/length/clock, starts GO, waits for completion, and copies response if RX exists. DMA transfer primes SG state, programs read DMA from memory to SPI command window, starts DMA doorbell, and waits; SPI and DMA interrupts chain subsequent SG segments and response DMA.

State and persistence: per-instance state tracks active transfer, SG progression, abort flags, completion, previous chip select and MSI vector selection for suspend. Parent state tracks DMA BAR, revision, and locks for interrupt register clearing. Suspend waits for transfers to finish, stores config, suspends SPI hosts, and masks events; resume resumes hosts, unmasks, and restores saved config.

Dependencies and integration points: PCI core, MSI/INTx allocation, DMA mapping, scatterlists, SPI core, spinlocks, completions, MMIO, `readx_poll_timeout`, and internal SPI helper `spi_xfer_is_dma_mapped()`. DMA is only enabled for revision >= C0 mapped to PF0 and when vector layout matches expectations.

Risks: `can_dma()` returns parent `can_dma` without checking transfer shape; DMA transfer itself rejects missing TX buffer/SG. DMA completion sequencing uses `atomic_t dma_completion_count` across RD/WR and SPI interrupts; races or abort paths can lead to timeout recovery. PIO requires TX because host has `SPI_CONTROLLER_MUST_TX`. Suspend spins while transfer is in progress with sleep polling. There is no remove callback beyond devm/PCI cleanup.

Test signals: subsystem IDs for one/two instances and secondary-only start, PIO chunking at 320-byte boundaries, DMA SG multi-segment TX/RX, DMA abort and engine reset, INTx shared ISR versus MSI vectors, chip-select force/devsel transitions, suspend/resume during idle and after transfer, revision/PF gating of DMA, and mode 0/3 clock divider boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pci1xxxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pic32-sqi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pic32-sqi.c

Purpose: Microchip PIC32 SQI quad SPI controller driver. It is a half-duplex DMA/descriptor-ring SPI host for SQI hardware, supporting two chip selects, single/dual/quad transfer lanes, 8..32 bits per word, and hardware-owned buffer descriptors for DMA transactions.

Important APIs, types, and functions: `struct pic32_sqi` stores MMIO, clocks, host, IRQ, completion, descriptor ring memory, free/used descriptor lists, current SPI device, speed, and mode. `struct buf_desc` mirrors hardware descriptors; `struct ring_desc` wraps descriptor metadata and DMA address. Important functions are clock programming, interrupt enable/disable and ISR, ring get/put/allocation/free, `pic32_sqi_one_transfer()`, `pic32_sqi_one_message()`, hardware prepare/unprepare, hardware init, probe, and remove.

Control flow: probe maps registers, gets IRQ and clocks, initializes completion, soft-resets hardware, sets DMA mode/quad lanes/burst/thresholds, allocates coherent descriptor memory and software ring descriptors, requests IRQ, configures host DMA limits and callbacks, then registers. For each SPI message the driver updates speed/mode when the SPI device changes, converts each transfer's DMA SG entries into BDs with direction/lane/CS/LSB flags, marks the last descriptor with LAST/CS_DEASSERT/LIFM/PKT_INT, writes the BD base, enables interrupts and DMA processor, waits up to 5 seconds, disables DMA/interrupts, returns descriptors to free list, updates actual length, and finalizes the message.

State and persistence: descriptor memory and ring lists persist for device lifetime. `cur_spi`, `cur_speed`, and `cur_mode` cache hardware programming. Used descriptors represent the current message only and are returned in reverse order after completion/error. Hardware state includes DMA mode, lanes, CS enables, thresholds, and clock divider.

Dependencies and integration points: platform device/OF compatible `microchip,pic32mzda-sqi`, clock framework (`reg_ck`, `spi_ck`), coherent DMA allocation, SPI core `transfer_one_message`, DMA-mapped SGs, and Linux list/completion/IRQ APIs. Host flags require half-duplex and DMA alignment/length constraints.

Risks: `pic32_sqi_one_transfer()` breaks if free descriptors run out but returns 0, so messages exceeding descriptor capacity may be silently truncated before last descriptor marking. The code assumes DMA SGs are prepared by the core because `can_dma` always returns true. Transfer-specific speed, bits-per-word, and delays are explicitly unsupported. Timeout still counts used descriptor lengths into `actual_length`. Hardware reset masks CPU interrupts locally due to reset-generated interrupt.

Test signals: descriptor exhaustion with >256 SG entries, 1/2/4-lane TX and RX, half-duplex enforcement, CS deassert on final descriptor, clock divider stability timeout, DMA error interrupt, packet completion, 5-second timeout handling, current-device speed/mode cache, and probe/remove ring/IRQ cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pic32-sqi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pic32.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-pic32.c

Purpose: Microchip PIC32 SPI controller driver for standard SPI hardware. It supports one chip select through GPIO, 8/16/32-bit words, interrupt-driven PIO transfers, optional DMA for larger transfers, explicit prepare/unprepare hardware hooks, and error IRQ handling for overflow/underrun/frame errors.

Important APIs, types, and functions: `struct pic32_spi` stores register base and DMA physical base, fault/RX/TX IRQs, FIFO size, clock, host, cached speed/mode/bits, DMA flag, transfer completion, PIO buffer pointers, transfer length, and word-size-specific FIFO callbacks generated by `BUILD_SPI_FIFO_RW`. Key functions include enable/disable, clock setting, FIFO level/max helpers, error and RX/TX IRQs, DMA transfer/config/prep/unprep, `pic32_spi_set_word_size()`, prepare message/hardware, `pic32_spi_one_transfer()`, setup/cleanup, hardware init/probe, platform probe/remove.

Control flow: probe allocates a host, maps registers and IRQs, enables the clock, initializes hardware, configures host operations and flags, optionally requests DMA channels, installs disabled IRQ handlers with `IRQ_NOAUTOEN`, initializes completion and mode cache, then registers. Prepare hardware enables the controller; prepare message applies device word size, speed, and CPOL/CPHA. Each transfer applies transfer-specific overrides, reinitializes completion, starts DMA if both RX/TX SGs exist, otherwise initializes PIO pointers and enables fault/RX/TX IRQs. Completion comes from RX DMA callback or RX IRQ; timeout terminates DMA if issued. Unprepare disables the controller.

State and persistence: cached speed/mode/bits and FIFO callbacks persist across transfers. DMA channel ownership is persistent while prepared and released on remove or failure. PIO transfer state lives in pointer fields until completion. Setup requires a CS GPIO and cleanup drives it inactive.

Dependencies and integration points: platform resources, named IRQs `fault`, `rx`, `tx`, clock `mck0`, DMAEngine channels `spi-rx`/`spi-tx`, GPIO descriptors, SPI core transfer/prepare hooks, and MMIO set/clear registers. Host flags require both TX and RX buffers, matching the controller's full-duplex behavior.

Risks: setup rejects devices without CS GPIO because native CS can glitch when TX FIFO empties. DMA prep failure other than defer degrades to PIO, but DMA config errors during word-size changes are not propagated. IRQ handlers disable lines with `disable_irq_nosync`; missed re-enable or error completion can stall later transfers. FIFO pointer arithmetic uses `void *` extensions and dummy all-ones TX/RX behavior for missing buffers. Transfer timeout is fixed at 2 seconds.

Test signals: PIO for 8/16/32-bit transfers, DMA threshold at 64 bytes, DMA channel absence and defer, fault IRQs for RX overflow/TX underrun/frame error, CS GPIO requirement/inactive cleanup, speed and mode changes across messages and transfers, timeout with DMA termination, and remove-time DMA/channel cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-pic32.c -->
