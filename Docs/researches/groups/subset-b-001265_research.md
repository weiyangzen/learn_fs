# Research: subset-b-001265

This grouped report covers the DMA controller, DMA router, and K3 PSI-L endpoint map files assigned to `subset-b-001265`. Each file section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra20-apb-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/tegra20-apb-dma.c

## Purpose
This is the DMAengine provider for NVIDIA Tegra20-family APB DMA controllers. It exposes slave SG and cyclic DMA channels for APB peripherals, registers an OF DMA controller, and abstracts SoC differences for Tegra20, Tegra30, Tegra114, and Tegra148.

## Important APIs, Types, and Functions
Key state types are `struct tegra_dma`, `struct tegra_dma_channel`, `struct tegra_dma_desc`, and `struct tegra_dma_sg_req`. `struct tegra_dma_chip_data` captures per-SoC channel count, register stride, maximum count, pause support, and separate word-count support. DMAengine entry points include `tegra_dma_slave_config()`, `tegra_dma_prep_slave_sg()`, `tegra_dma_prep_dma_cyclic()`, `tegra_dma_issue_pending()`, `tegra_dma_terminate_all()`, `tegra_dma_synchronize()`, and `tegra_dma_tx_status()`. Hardware access is isolated through `tdma_write()`, `tdc_write()`, and `tdc_read()`.

## Control Flow
Probe obtains the memory resource, clock, reset, per-channel IRQs, initializes channel lists/tasklets, registers the DMAengine device, and registers OF translation through `tegra_dma_of_xlate()`. A client configures slave properties, prepares either SG or cyclic descriptors, submits them through `tegra_dma_tx_submit()`, and starts work with `issue_pending()`. `tdc_start_head_req()` programs channel registers and enables the channel. Interrupts clear EOC status, call the active ISR handler (`handle_once_dma_done()` or `handle_cont_sngl_cycle_dma_done()`), wake synchronizers, and schedule the tasklet for callbacks.

## State and Persistence
Per-channel state is held in pending SG requests, reusable SG request and descriptor freelists, callback descriptors, `busy`, `cyclic`, `config_init`, and the current slave ID. Transfer progress is tracked by descriptor byte counters and per-SG `words_xferred`. Runtime PM gates the DMA clock while active transfers take references. System suspend kills tasklets and refuses suspend if any channel is busy. Resume reinitializes hardware through reset and global enable.

## Dependencies and Integration Points
The driver depends on Linux DMAengine, runtime PM, clocks, resets, OF DMA, IRQs, tasklets, and Tegra tracepoints. Device tree supplies compatible strings and DMA request IDs. Clients receive private slave channels via `dma_get_any_slave_channel()` and the OF xlate path sets `tdc->slave_id`.

## Risks
The driver has delicate races around pausing, EOC status, and programming the next cyclic segment. Older SoCs use a global pause counter, so one channel pause can affect global controller state. Transfer lengths and addresses must be 4-byte aligned and within `max_dma_count`; callers that violate this fail at prepare time. Cyclic residue is approximate around counter wrap and EOC timing. Suspend during active DMA returns `-EBUSY`.

## Test Signals
Useful checks include DMAengine slave SG loopback/peripheral tests, ALSA cyclic audio playback/capture, DT xlate with valid and invalid request IDs, suspend/resume with idle and busy channels, runtime PM clock toggling, and tracepoint/callback ordering under multi-period cyclic load. Error tests should cover unaligned buffers, overlarge SG segments, termination while EOC is pending, and callback synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra20-apb-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra210-adma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/tegra210-adma.c

## Purpose
This driver provides DMAengine support for NVIDIA Tegra ADMA audio DMA controllers on Tegra210, Tegra186, and Tegra264. It is cyclic-oriented and intended for AHUB/audio peripheral transfers between memory and ADMAIF-style request lines.

## Important APIs, Types, and Functions
The central structures are `struct tegra_adma`, `struct tegra_adma_chan`, `struct tegra_adma_desc`, and `struct tegra_adma_chip_data`. The chip data table provides register offsets, bit shifts, request masks, channel counts, page programming callbacks, and burst encoding callbacks. DMAengine operations include `tegra_adma_prep_dma_cyclic()`, `tegra_adma_issue_pending()`, `tegra_adma_tx_status()`, `tegra_adma_pause()`, `tegra_adma_resume()`, `tegra_adma_terminate_all()`, and `tegra_adma_synchronize()`. It uses virt-dma helpers for queueing and callbacks.

## Control Flow
Probe maps either legacy single-region resources or newer page/global resources, derives the ADMA page number, initializes enabled channels from `dma-channel-mask`, initializes global hardware, registers the DMAengine device, and registers `tegra_dma_of_xlate()`. OF xlate assigns a nonzero slave request index to a free channel. Preparation validates cyclic buffer and period sizes, allocates a descriptor, calculates channel control/config/FIFO/TC registers, and reserves the request line for the transfer direction. `issue_pending()` starts the next virt-dma descriptor, programming channel registers and asserting `ADMA_CH_CMD`. Interrupts clear transfer-done status and call `vchan_cyclic_callback()`.

## State and Persistence
The controller tracks reserved RX/TX request lines in bitmaps, enabled channel masks, channel request metadata, the active descriptor pointer, transfer-position counters, and saved register images for runtime PM. Runtime suspend saves global command and active channel registers before disabling `d_audio`; runtime resume restores the clock, page configuration, and active channel state.

## Dependencies and Integration Points
The driver depends on DMAengine, virt-dma, OF DMA, OF IRQ mapping, runtime PM, clocks, and MMIO polling. It integrates with Tegra AHUB clients through one-cell DMA specifiers that name the request index. Tegra186 and Tegra264 page/global-register layouts are selected by compatible string.

## Risks
Only cyclic transfers are implemented, so SG or memcpy clients are unsupported. `tegra_adma_pause()` and `resume()` assume `tdc->desc` exists; callers must not pause an idle channel. Request-line reservation prevents RX/TX sharing conflicts, but stale reservations would block future users until termination/free. Page resource math can fail if DT resource order or offsets are wrong. Residue uses a hardware position counter with wrap handling and must be tested over long-running cyclic streams.

## Test Signals
Exercise audio capture/playback on each supported SoC data variant, valid and invalid `dma-channel-mask` values, one-cell OF request mapping, concurrent RX/TX reservation conflicts, pause/resume, runtime suspend/resume during active cyclic DMA, and removal/IRQ disposal. Negative tests should include zero request index, unaligned buffers, too many periods, and invalid page/global resource layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra210-adma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/Kconfig

## Purpose
This Kconfig file declares the Texas Instruments DMA driver options for CPPI 4.1, EDMA, OMAP sDMA, K3 UDMA, the K3 UDMA glue layer, the internal K3 PSI-L endpoint library, and the internal TI DMA crossbar router.

## Important APIs, Types, and Functions
There are no runtime functions; the important interface is the Kconfig symbols. `TI_CPPI41` builds the CPPI USB DMA engine on OMAP/DA8xx. `TI_EDMA` selects `DMA_ENGINE`, `DMA_VIRTUAL_CHANNELS`, and conditionally `TI_DMA_CROSSBAR`. `DMA_OMAP` does the same for OMAP sDMA. `TI_K3_UDMA` depends on K3 architecture or compile testing, TI SCI protocol, and TI SCI INTA irqchip support, and selects `SOC_TI`, ring accelerator support, and `TI_K3_PSIL`. `TI_K3_PSIL` is a hidden tristate defaulting to `TI_K3_UDMA`; `TI_DMA_CROSSBAR` is an internal bool.

## Control Flow
Build-time dependency resolution controls which source files in the TI DMA directory are compiled. Enabling UDMA automatically brings in the PSI-L library needed by K3 UDMA endpoint lookup. EDMA and OMAP sDMA select the crossbar on relevant OMAP/compile-test configurations.

## State and Persistence
The file has no runtime state. Its persistent effect is the kernel build configuration and selected object graph.

## Dependencies and Integration Points
It integrates with architecture symbols (`ARCH_OMAP`, `ARCH_DAVINCI`, `ARCH_KEYSTONE`, `ARCH_K3`, `SOC_DRA7XX`), compile-test builds, DMAengine core, virtual channels, TI SCI firmware interfaces, TI INTA interrupt controller support, TI ring accelerator support, and the Makefile in the same directory.

## Risks
Incorrect dependencies can silently omit needed support or build drivers on unsupported platforms. `TI_K3_PSIL` is hidden and defaulted from UDMA, so any UDMA split or modularization must preserve that selection. Whitespace inconsistency in the `help` blocks is cosmetic but can obscure Kconfig review.

## Test Signals
Build matrix checks should cover `allmodconfig`, `allyesconfig`, K3-only configs, OMAP/DRA7 configs, DaVinci configs, Keystone configs, and `COMPILE_TEST`. Verify that enabling `TI_K3_UDMA` links `k3-psil-lib.o`, and that EDMA/OMAP builds include crossbar support where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/Makefile

## Purpose
This Makefile maps the TI DMA Kconfig symbols to object files and defines the multi-object K3 PSI-L endpoint library.

## Important APIs, Types, and Functions
There are no C APIs. The important build targets are `cppi41.o`, `edma.o`, `omap-dma.o`, `k3-udma.o`, `k3-udma-glue.o`, `dma-crossbar.o`, and `k3-psil-lib.o`. `k3-psil-lib-objs` combines the generic `k3-psil.o` lookup code with SoC maps for AM654, J721E, J7200, AM64, J721S2, AM62, AM62A, J784S4, and AM62P.

## Control Flow
Kbuild includes objects according to the corresponding `CONFIG_*` values. When `CONFIG_TI_K3_PSIL` is enabled, Kbuild links the generic PSI-L implementation and every listed SoC table into one module/object library so runtime `soc_device_match()` can select the correct map.

## State and Persistence
The Makefile has no runtime state. Its persistent effect is object composition and symbol availability, especially the exported `psil_get_ep_config()` and `psil_set_new_ep_config()` functions from the PSI-L library.

## Dependencies and Integration Points
It is paired with `drivers/dma/ti/Kconfig` and the source files in this directory. It integrates with Kbuild's `obj-$(CONFIG_...)` and `*-objs` multi-object module conventions.

## Risks
Adding a new K3 SoC endpoint map requires both an extern in `k3-psil-priv.h`, a match entry in `k3-psil.c`, and an object entry here. Missing any one of those causes either link failure or runtime `-ENOTSUPP`/`-ENOENT` lookups. Object ordering is not functionally complex but must include `k3-psil.o` and all maps under the same library.

## Test Signals
Run Kbuild with `CONFIG_TI_K3_PSIL=y` and `=m`, verify all endpoint-map objects are linked, and check module symbol exports. Build configurations toggling each top-level TI DMA symbol should include only expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/cppi41.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/cppi41.c

## Purpose
This driver provides DMAengine support for TI CPPI 4.1 DMA, primarily used by USB on AM335x and DA8xx platforms. It configures the CPPI DMA scheduler, queue manager, packet descriptors, completion queues, and teardown flow.

## Important APIs, Types, and Functions
Core types are `struct cppi41_dd`, `struct cppi41_channel`, `struct cppi41_desc`, `struct chan_queues`, and `struct cppi_glue_infos`. DMAengine entry points are `cppi41_dma_alloc_chan_resources()`, `cppi41_dma_free_chan_resources()`, `cppi41_dma_prep_slave_sg()`, `cppi41_dma_issue_pending()`, `cppi41_dma_tx_status()`, and `cppi41_stop_chan()`. Hardware setup and teardown are handled by `init_cppi41()`, `init_descs()`, `init_sched()`, `deinit_cppi41()`, and `cppi41_tear_down_chan()`. OF translation uses `cppi41_dma_xlate()` plus `cpp41_dma_filter_fn()`.

## Control Flow
Probe reads platform glue data from the compatible string, maps controller/scheduler/queue-manager resources, enables runtime PM, initializes queue-manager scratch and coherent descriptors, builds RX/TX channel objects, registers the shared IRQ, registers DMAengine, and registers OF DMA translation. A client requests a channel with a two-cell specifier: USB port and RX/TX direction. Preparation fills a host packet descriptor from the first SG entry. `issue_pending()` adds the channel to a controller pending list, and `cppi41_run_queue()` pushes descriptors into hardware queues if not runtime-suspended. The IRQ scans pending completion queues, pops descriptors, maps them back through `chan_busy[]`, computes residue, completes the cookie, and invokes callbacks.

## State and Persistence
Persistent runtime state includes coherent descriptor memory, queue-manager scratch memory, pending software queue, per-channel queue numbers, busy descriptor map, teardown flags, saved `DMA_TDFDQ`, and runtime suspend flag. Runtime PM references are deliberately held while descriptors are in `chan_busy[]` to prevent autosuspend during long USB transfers. System suspend saves teardown queue configuration and disables the scheduler; resume restores queue-manager memory base, scheduler, RX completion queue routing, scratch, and teardown queue.

## Dependencies and Integration Points
The driver depends on DMAengine, OF DMA, platform resources, IRQs, coherent DMA memory, runtime PM, raw MMIO, and USB/MUSB-style clients. Platform glue supplies queue numbering differences between AM335x and DA8xx. Device tree must provide `reg-names`, `dma-channels` or deprecated `#dma-channels`, and an interrupt.

## Risks
The implementation supports only one descriptor per channel despite iterating SG entries; true SG requires client/controller support beyond current use. The queue-manager and teardown paths are timing-sensitive and contain retry logic. Raw MMIO requires explicit barriers before pushing descriptors. Runtime-suspend interactions are subtle: pending transfers are held while suspended and completion IRQs warn if observed during suspend. Queue table bounds currently use AM335x array size in the filter, so platform-specific queue array size assumptions matter.

## Test Signals
Test with USB RX/TX traffic on AM335x and DA8xx, runtime autosuspend during long mass-storage transfers, channel terminate while active and while pending, shared IRQ completion, zero-length packet descriptors, residue reporting, DT xlate/filter selection, and system suspend/resume. Fault injection should cover allocation failure for coherent descriptors/scratch and invalid `dma-channels` or `reg-names`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/cppi41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/dma-crossbar.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/dma-crossbar.c

## Purpose
This file implements TI DMA crossbar routing as an OF DMA router for AM335x/AM437x EDMA crossbars and DRA7-family crossbars. It translates client DMA specifiers into DMA-master specifiers while programming mux registers.

## Important APIs, Types, and Functions
AM335x support uses `struct ti_am335x_xbar_data`, `struct ti_am335x_xbar_map`, `ti_am335x_xbar_route_allocate()`, and `ti_am335x_xbar_free()`. DRA7 support uses `struct ti_dra7_xbar_data`, `struct ti_dra7_xbar_map`, `ti_dra7_xbar_route_allocate()`, and `ti_dra7_xbar_free()`. `ti_dma_xbar_probe()` dispatches by compatible string. `of_dma_router_register()` is the integration API.

## Control Flow
At `arch_initcall`, the platform driver registers. Probe identifies the crossbar type. AM335x probe validates the DMA master, reads request counts, maps the mux resource, resets all request lines to zero, and registers a router. AM335x allocation validates three arguments, sets `dma_spec->np` to the DMA master, rewrites the request spec to two cells, and writes the requested event value to the selected DMA line. DRA7 probe validates the master, reads request counts and safe-map value, reserves configured request ranges, resets free lines to the safe value, and registers a router. DRA7 allocation finds a free output line under a mutex, rewrites the first DMA spec arg to the allocated DMA request plus offset, and writes the selected input to the mux.

## State and Persistence
AM335x state is simple MMIO plus request-count limits; route-free resets the mapped line to zero. DRA7 keeps a `dma_inuse` bitmap protected by a mutex, a safe reset value, request counts, and a master-specific offset for EDMA vs SDMA numbering. Mux register programming persists until route-free or driver/probe reset.

## Dependencies and Integration Points
The driver depends on OF DMA router infrastructure, OF platform device lookup, DMA master phandles, MMIO resource mapping, and device tree properties such as `dma-masters`, `dma-requests`, `ti,dma-safe-map`, and `ti,reserved-dma-request-ranges`. It is selected internally by EDMA/OMAP DMA Kconfig paths.

## Risks
DRA7 dynamic allocation can exhaust DMA request lines. Incorrect reserved ranges or safe-map values can route spurious events. AM335x has a special register layout for events 60-63, so off-by-one errors are hardware-specific. Allocation uses `of_find_device_by_node()` and must always balance `put_device()`. Bad DT arg counts or unsupported DMA master compatibles lead to routing failure.

## Test Signals
Validate DT routing for AM335x and DRA7 with multiple clients, free/reallocate cycles, reserved-range enforcement, request exhaustion, safe-map reset on route free, and EDMA vs SDMA offset handling. Build and boot tests should verify `arch_initcall` registration before DMA clients request channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/dma-crossbar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/edma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/edma.c

## Purpose
This is the TI EDMA3 DMAengine driver. It supports hardware-triggered slave SG, cyclic audio-style transfers, software-triggered memcpy, interleaved memory transfers, PaRAM slot management, interrupt/error handling, DT translation, and legacy platform-data modes.

## Important APIs, Types, and Functions
Important types are `struct edma_cc`, `struct edma_chan`, `struct edma_desc`, `struct edma_pset`, `struct edmacc_param`, and `struct edma_tc`. PaRAM and channel helpers include `edma_alloc_slot()`, `edma_free_slot()`, `edma_link()`, `edma_set_chmap()`, `edma_start()`, `edma_stop()`, `edma_pause()`, `edma_resume()`, and `edma_execute()`. DMAengine operations include `edma_prep_slave_sg()`, `edma_prep_dma_memcpy()`, `edma_prep_dma_interleaved()`, `edma_prep_dma_cyclic()`, `edma_issue_pending()`, `edma_tx_status()`, `edma_terminate_all()`, and `edma_synchronize()`.

## Control Flow
Probe obtains DT or platform data, enables runtime PM, decodes EDMA hardware capabilities from `CCCFG`, allocates channel/slot bitmaps, marks reserved slots/channels, resets unused PaRAM entries, registers completion and error IRQs, allocates a dummy slot, configures TPTC queue priorities, initializes DMAengine channels, assigns default queues, and registers slave and optional memcpy DMA devices. OF xlate maps a DMA specifier to a channel and optional event queue. Prepared descriptors contain one or more PaRAM sets. `edma_execute()` writes a window of up to `MAX_NR_SG` sets to hardware, links them, starts or resumes the channel, and handles missed events. Completion IRQs call `edma_completion_handler()`, which either cycles callbacks, completes descriptors, or pauses at intermediate windows and programs the next window. Error IRQs clear missed event and queue errors and may retrigger safe in-flight transfers.

## State and Persistence
Controller state includes decoded channel/slot/queue counts, channel mask, slot-in-use bitmap, dummy slot, TPTC list, queue priority mapping, DMA devices, and per-channel active descriptor, slots, event queue, missed flag, and slave config. Descriptors persist residue, processed PaRAM count, current SG length, and cyclic/polled flags. Suspend disables interrupts for allocated channels; resume restores dummy slot, queue priorities, shadow-region access, interrupts, and channel-to-slot mappings.

## Dependencies and Integration Points
The driver depends on DMAengine, virt-dma, OF DMA, OF IRQ/address parsing, runtime PM, TI EDMA platform data, and optional TPTC child devices. It integrates with TI DMA crossbar through DT and Kconfig, with legacy `ti,edma3` bindings, newer `ti,edma3-tpcc` bindings, and platform filter-map based channel requests.

## Risks
PaRAM slot allocation is a scarce global resource, and long SG lists are chunked into windows of `MAX_NR_SG`, so missed event handling is essential. Residue computation polls hardware position and may hit a bounded busy-wait on slow devices. Cyclic mode rejects too many periods unless burst equals period length. Legacy memcpy mode without explicit memcpy channels is warned as risky. Error handling intentionally avoids recursion in null-slot cases, using a missed flag for later recovery. DT reservation masks, queue priorities, and channel-map presence must match hardware.

## Test Signals
Run DMAengine memcpy, slave SG, cyclic, and interleaved tests where hardware permits. Cover legacy and TPCC DT bindings, event queue selection, reserved slot/channel masks, `ti,edma-memcpy-channels`, xbar event map programming, TPTC phandles, completion IRQs, CC error IRQs, polled memcpy status, long SG windows exceeding `MAX_NR_SG`, suspend/resume with allocated idle channels, and invalid bus widths or bursts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/edma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62.c

## Purpose
This file declares the AM62 PSI-L endpoint map consumed by the K3 UDMA PSI-L library. It maps source and destination thread IDs to endpoint configuration for SAUL, PDMA SPI/UART/McASP, CPSW3G Ethernet, and CSI2RX.

## Important APIs, Types, and Functions
There are no executable functions. The exported data object is `struct psil_ep_map am62_ep_map`. Macros build `struct psil_ep` entries: `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. These fill `struct psil_endpoint_config` fields such as endpoint type, packet mode, EPIB requirements, PSD size, mapped channel ID, flow range, default flow, and `notdpkt`.

## Control Flow
Runtime lookup happens in `k3-psil.c`, not here. When the detected SoC family is AM62X, `psil_get_ep_config()` searches `am62_src_ep_map` or `am62_dst_ep_map` for the requested thread ID. Source entries are used for RX (`DMA_DEV_TO_MEM`) and destination entries for TX (`DMA_MEM_TO_DEV`).

## State and Persistence
The arrays are static map data compiled into `k3-psil-lib.o`. `psil_set_new_ep_config()` can mutate returned endpoint configs at runtime for named device-tree DMA entries, so these static entries can become process-wide runtime configuration state.

## Dependencies and Integration Points
The file depends on `k3-psil-priv.h` and public `linux/dma/k3-psil.h` endpoint definitions. It is linked by the TI DMA Makefile and selected by `soc_device_match()` for family `AM62X`.

## Risks
Thread IDs, flow ranges, and channel IDs must match SoC integration data. Ethernet and SAUL entries carry explicit flow/channel assignments, so incorrect numbers can break packet DMA. CSI2RX entries are native endpoints with minimal config and rely on consumers/UDMA for the rest. Runtime mutation of static config should be treated carefully because all later lookups observe the changed data.

## Test Signals
Validate AM62 UDMA clients for SAUL RX/TX, SPI/UART PDMA packet mode, McASP 32-bit burst mode, CPSW3G packet DMA flows, and CSI2RX streams. Unit-style checks can call `psil_get_ep_config()` for representative source, destination, and invalid thread IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62a.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62a.c

## Purpose
This file provides the AM62A PSI-L endpoint map for K3 UDMA. It is close to AM62 but uses AM62A-specific CSI2RX thread IDs and includes macros for both TR and packet PDMA endpoints.

## Important APIs, Types, and Functions
The main symbol is `struct psil_ep_map am62a_ep_map`. Endpoint entries are built through `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. These macros configure PDMA XY packet or transfer mode, native packet endpoints with EPIB/PSD metadata, SAUL security accelerator flows, McASP burst/access flags, and native CSI2RX endpoints.

## Control Flow
No code executes in this file. `k3-psil.c` selects `am62a_ep_map` for SoC family `AM62AX`, then performs linear lookup through the source or destination arrays. Destination IDs keep the high destination-thread bit set; fallback symmetric lookup is available in the generic library if a destination-specific entry is absent.

## State and Persistence
The static source/destination arrays persist for the lifetime of the module/kernel image. Because the generic library returns mutable pointers, `psil_set_new_ep_config()` can alter a selected entry based on device-tree `dma-names` and `dmas`.

## Dependencies and Integration Points
The map integrates AM62A peripherals with K3 UDMA and is linked into `k3-psil-lib.o`. It depends on endpoint type constants and `struct psil_endpoint_config` from the public K3 PSI-L header.

## Risks
The AM62A CSI2RX range starts at `0x5000`, unlike AM62's `0x4700` range, so copy/paste between maps is a likely regression vector. SAUL and Ethernet flow assignments must stay coherent with firmware/resource manager allocation. Missing destination entries for PDMA devices would fall back only if symmetric lookup works for that ID.

## Test Signals
Probe UDMA on AM62AX hardware or DT tests and verify endpoint lookup for SAUL, PDMA SPI/UART/McASP, CPSW3G, and CSI2RX IDs. Negative lookup tests should confirm invalid AM62 or AM62A CSI ranges return `-ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62p.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62p.c

## Purpose
This file defines the AM62P PSI-L endpoint map, also reused for the J722S SoC family by the generic selector. It covers SAUL, PDMA SPI/UART/McASP, CPSW3G, and a large CSI2RX source-thread set including J722S-only additional receivers.

## Important APIs, Types, and Functions
The exported data object is `struct psil_ep_map am62p_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, `PSIL_SAUL()`, `PSIL_PDMA_MCASP()`, and `PSIL_CSI2RX()`. Entries populate packet mode, EPIB/PSD metadata, mapped channel IDs, flow windows, default flow IDs, and PDMA burst/access flags.

## Control Flow
The file is declarative. `psil_get_ep_config()` in `k3-psil.c` selects it for `AM62PX` and `J722S`, then searches source and destination arrays. Source entries cover RX endpoints, while destination entries cover TX endpoints.

## State and Persistence
Endpoint arrays are static global data. They are logically read-only configuration, but the generic `psil_set_new_ep_config()` API can overwrite an entry for a device-tree named DMA.

## Dependencies and Integration Points
The map depends on `k3-psil-priv.h` and is part of the `k3-psil-lib.o` object group. It feeds K3 UDMA channel and flow setup for AM62P/J722S peripherals.

## Risks
The source array includes repeated `0x5000`-`0x501f` CSI2RX entries followed by J722S-only `0x5100`-`0x531f` ranges. Duplicate thread IDs mean lookup returns the first matching config; that is harmless only if duplicate configs are intentionally identical. Reusing AM62P for J722S can hide SoC-specific differences if future peripherals diverge. Flow assignments for SAUL and CPSW must match board firmware/resource allocation.

## Test Signals
Verify `psil_get_ep_config()` for AM62P and J722S families, including duplicate CSI2RX IDs, J722S-only CSI IDs, CPSW3G TX/RX channels, SAUL flows, and PDMA endpoints. A static duplicate-ID checker would be useful for this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am62p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am64.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am64.c

## Purpose
This file declares the AM64 PSI-L endpoint map for K3 UDMA. It covers SAUL, ICSSG Ethernet, PDMA SPI/USART/ADC, and CPSW2 endpoints with AM64-specific mapped channel and flow assignments.

## Important APIs, Types, and Functions
The exported data object is `struct psil_ep_map am64_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, and `PSIL_SAUL()`. Unlike older maps, AM64 Ethernet and SAUL macros encode mapped channel IDs and flow ranges directly, including single-flow ICSSG TX entries and wider RX ranges.

## Control Flow
There are no local functions. Generic PSI-L lookup selects this map for the `AM64X` family and linearly searches source or destination arrays based on the requested thread ID. The destination-thread bit distinguishes TX IDs such as `0xc100`/`0xc500` from RX IDs such as `0x4100`/`0x4500`.

## State and Persistence
The arrays are static endpoint configuration tables. They are persistent for the lifetime of the driver and can be modified indirectly through `psil_set_new_ep_config()`.

## Dependencies and Integration Points
This map is linked into `k3-psil-lib.o` and supplies endpoint metadata to TI K3 UDMA. It depends on public K3 PSI-L endpoint config definitions and the generic SoC-family selector.

## Risks
AM64 has explicit channel/flow data for ICSSG, CPSW2, and SAUL; errors here lead to wrong UDMA channel or flow allocation. ADC endpoints use TR mode while SPI/USART use packet mode, so endpoint-type mismatches can break PDMA setup. Destination ICSSG Ethernet entries use one flow each, while CPSW2 uses eight-flow windows.

## Test Signals
Validate AM64 UDMA clients for ICSSG RX/TX, CPSW2 RX/TX, SAUL crypto, SPI/USART PDMA packet mode, and ADC TR mode. Lookup tests should include representative source/destination pairs and verify flow ranges/default flow IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am654.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am654.c

## Purpose
This file provides the AM654 PSI-L endpoint map. It covers SA2UL, PRU_ICSSG Ethernet, PDMA McASP/SPI/USART/ADC, CPSW0, and MCU PDMA endpoints for early K3 AM65x devices.

## Important APIs, Types, and Functions
The exported object is `struct psil_ep_map am654_ep_map`. Endpoint macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_ETHERNET()`, and `PSIL_SA2UL()`. Compared with newer AM62/AM64 maps, Ethernet and SA2UL entries do not encode mapped channel/flow IDs here; they primarily set endpoint type, packet mode, EPIB, PSD size, and `notdpkt` for TX SA2UL.

## Control Flow
The file contributes data only. `k3-psil.c` selects `am654_ep_map` for family `AM65X`; lookups then search source or destination arrays. Source entries correspond to RX threads such as `0x4000`, `0x4100`, `0x4400`, and MCU ranges; destination entries include `0xc000`, ICSSG TX ranges, and CPSW0 `0xf000`-style IDs.

## State and Persistence
The endpoint arrays persist as static module/kernel data and may be overwritten by the generic `psil_set_new_ep_config()` API when a caller supplies replacement config for a named DMA.

## Dependencies and Integration Points
The map is linked through the TI DMA Makefile and depends on `k3-psil-priv.h`. It integrates with K3 UDMA and the AM65x SoC-family match table.

## Risks
Because older entries omit explicit flow/channel mapping, consumers must rely on defaults or other UDMA resource management paths. Thread IDs span main and MCU domains, so accidental removal of MCU ranges breaks low-power/peripheral DMA. SA2UL TX uses `notdpkt`, and incorrect direction flags would affect packet formatting.

## Test Signals
Test AM65x UDMA endpoint lookup for SA2UL RX/TX, PRU_ICSSG, CPSW0, PDMA McASP/SPI/USART, MCU SPI/USART, and ADC TR endpoints. Negative tests should verify unknown thread IDs return `-ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-am654.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j7200.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j7200.c

## Purpose
This file defines the J7200 PSI-L endpoint map for K3 UDMA. It covers McASP, SPI, UART, CPSW5, CPSW0, MCU PDMA, ADC, and SA2UL endpoints.

## Important APIs, Types, and Functions
The main symbol is `struct psil_ep_map j7200_ep_map`. Endpoint macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, and `PSIL_SA2UL()`. McASP endpoints set PDMA 32-bit access and burst flags; packet-mode PDMA covers SPI/UART; Ethernet entries set native packet mode with EPIB and 16-byte PSD; SA2UL entries set 64-byte PSD and TX `notdpkt`.

## Control Flow
The map is selected by `k3-psil.c` for SoC family `J7200`. Source entries are searched for RX threads; destination entries are searched first for destination IDs and can otherwise fall back to symmetric source lookup if an explicit destination is absent.

## State and Persistence
The source and destination arrays are static configuration state. Generic PSI-L APIs return pointers into these arrays, so runtime replacement through `psil_set_new_ep_config()` changes later lookups.

## Dependencies and Integration Points
This file depends on the private PSI-L map header and links into `k3-psil-lib.o`. It integrates J7200 peripheral thread IDs with K3 UDMA endpoint setup.

## Risks
The map contains multiple peripheral groups with similar contiguous IDs, making range omissions easy. CPSW5 and CPSW0 use different RX/TX ranges; incorrect thread IDs would route Ethernet traffic to the wrong endpoint. MCU-domain entries are separate from main-domain entries and need board-level validation. SA2UL appears near `0x7500`/`0xf500`, matching other K3 families but still SoC-specific.

## Test Signals
Validate J7200 lookup and DMA operation for McASP, SPI groups, UART groups, CPSW5, CPSW0, MCU SPI/UART, ADC, and SA2UL. Static table tests should check that each destination group expected by DT has a matching entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j7200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721e.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721e.c

## Purpose
This file provides the J721E PSI-L endpoint map. It is a large declarative map for SA2UL, PRU_ICSSG, multiple PDMA groups, CSI2RX, CPSW9, CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported symbol is `struct psil_ep_map j721e_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. These macros encode endpoint type, packet mode, EPIB/PSD requirements, PDMA burst/access flags, and SA2UL TX packet behavior.

## Control Flow
No functions execute locally. The generic library selects this map for `J721E` and performs linear thread-ID lookup. Source entries are used for RX, including many CSI2RX IDs from `0x4940` through `0x497f`; destination entries cover matching TX-capable groups where applicable.

## State and Persistence
The arrays are static persistent endpoint tables and can be mutated through the generic `psil_set_new_ep_config()` interface. Since lookup returns direct pointers, modifications are global to the selected map.

## Dependencies and Integration Points
The map depends on `k3-psil-priv.h`, the public K3 PSI-L endpoint definitions, and Makefile linkage into `k3-psil-lib.o`. It supplies endpoint metadata to K3 UDMA clients on J721E.

## Risks
This is a dense hardware table with many similar PDMA and CSI2RX IDs. Missing or transposed entries can break a peripheral without compiler signals. CSI2RX is source-only and native with minimal config, so consumers rely on correct thread IDs. Ethernet and SA2UL entries do not include explicit flow/channel mapping in this older style. Runtime mutation can hide table defects if used as a workaround.

## Test Signals
Run endpoint lookup tests for representative IDs in every group: SA2UL, ICSSG, McASP PDMA groups, SPI PDMA groups, UART PDMA groups, CSI2RX, CPSW9, CPSW0, MCU SPI/UART/ADC, and MCU SA2UL. Hardware tests should include camera capture and Ethernet paths because they touch the largest map regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721s2.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721s2.c

## Purpose
This file declares the J721S2 PSI-L endpoint map. It covers main-domain McASP, SPI, CPSW2G, UART, CSI2RX, main SA2UL, MCU CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported object is `struct psil_ep_map j721s2_ep_map`. Macros are `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. These build endpoint configs for PDMA XY TR/packet, McASP burst/access, native packet Ethernet, SA2UL packet endpoints, and native CSI2RX.

## Control Flow
The file is selected by `psil_get_ep_config()` for SoC family `J721S2`. The generic lookup searches destination entries first when the destination bit is set and then source entries after masking the destination bit. Source entries include large CSI2RX ranges and both main and MCU domains.

## State and Persistence
The endpoint arrays are static global data. They can be changed by `psil_set_new_ep_config()` if a caller replaces a config associated with a device-tree DMA name.

## Dependencies and Integration Points
The file is compiled into the K3 PSI-L library and depends on the private map declarations. It integrates J721S2 peripheral endpoints with the K3 UDMA driver.

## Risks
J721S2 destination map is much smaller than its source map, so many TX-capable-looking peripherals may rely on symmetric fallback or may not be TX endpoints. CSI2RX ranges are numerous and easy to truncate. Main SA2UL uses `0x4a40`/`0xca40`, while MCU SA2UL uses `0x7500`/`0xf500`; confusing these would route to the wrong domain.

## Test Signals
Validate lookup and DMA operation for McASP, SPI groups, CPSW2G, UART, CSI2RX, main SA2UL, MCU CPSW0, MCU SPI/UART/ADC, and MCU SA2UL. Table tests should compare expected DT thread IDs against the map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j721s2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j784s4.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j784s4.c

## Purpose
This file defines the J784S4 PSI-L endpoint map. It covers main-domain McASP, SPI, CPSW2G, UART, extensive CSI2RX, CPSW9G, main SA2UL, MCU CPSW0, MCU PDMA, MCU ADC, and MCU SA2UL endpoints.

## Important APIs, Types, and Functions
The exported symbol is `struct psil_ep_map j784s4_ep_map`. Macros include `PSIL_PDMA_XY_TR()`, `PSIL_PDMA_XY_PKT()`, `PSIL_PDMA_MCASP()`, `PSIL_ETHERNET()`, `PSIL_SA2UL()`, and `PSIL_CSI2RX()`. They encode native packet endpoints with EPIB/PSD metadata, PDMA packet/TR modes, McASP PDMA burst/access flags, and SA2UL direction flags.

## Control Flow
Generic lookup in `k3-psil.c` selects this map for the `J784S4` family. Source lookups cover RX endpoints; destination lookups cover explicit TX entries for Ethernet, SA2UL, PDMA SPI, and MCU endpoints. The map itself has no executable control path.

## State and Persistence
The source/destination arrays are persistent static data. They are mutable indirectly through the generic replacement API, which copies new endpoint configuration into the matching map entry.

## Dependencies and Integration Points
The map depends on K3 PSI-L endpoint types and is linked into `k3-psil-lib.o`. K3 UDMA uses the selected endpoint config to determine packet mode, EPIB, PSD, PDMA behavior, and endpoint type.

## Risks
J784S4 has very large CSI2RX source ranges, including `0x4900`-style and `0x4940`-`0x499f` IDs, making duplicate/omitted entries hard to spot manually. Destination groups are ordered differently than source groups. Main and MCU domain IDs must not be confused. Ethernet entries are native packet mode without explicit flow data in this map style.

## Test Signals
Use table validation for all expected J784S4 DT thread IDs, plus hardware tests for CSI capture, CPSW2G/CPSW9G, SA2UL, SPI, McASP, UART, MCU CPSW0, and MCU PDMA/ADC paths. Include invalid ID lookup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-j784s4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-priv.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-priv.h

## Purpose
This private header defines the internal data structures used by the K3 PSI-L endpoint library and declares every SoC endpoint map compiled into the TI DMA PSI-L object.

## Important APIs, Types, and Functions
`struct psil_ep` pairs a 32-bit thread ID with a `struct psil_endpoint_config`. `struct psil_ep_map` names a SoC map and stores source and destination endpoint arrays with counts. `psil_get_ep_config()` is declared for endpoint lookup. The header declares external map objects for AM654, J721E, J7200, AM64, J721S2, AM62, AM62A, J784S4, and AM62P.

## Control Flow
The header has no control flow, but its comment documents generic lookup behavior: if a destination thread has no explicit destination entry, the library masks the destination-thread offset and tries to find a symmetric source entry.

## State and Persistence
It defines the shape of static endpoint-map state. Because maps expose mutable endpoint config objects through pointers, these structures are both configuration tables and runtime state if modified by `psil_set_new_ep_config()`.

## Dependencies and Integration Points
The header depends on `linux/dma/k3-psil.h` for public endpoint configuration definitions. It is included by `k3-psil.c` and all SoC map files. The extern declarations must stay synchronized with the Makefile and SoC match table.

## Risks
Count fields must match array sizes; every map file uses `ARRAY_SIZE()` for this. Adding a new SoC requires coordinated edits here, in the generic selector, and in the Makefile. The symmetric fallback behavior means missing destination entries can be intentional or accidental, so table review must understand endpoint directionality.

## Test Signals
Build tests catch missing extern/object mismatches. Runtime lookup tests should verify explicit destination, symmetric fallback, and not-found behavior for at least one map. Static analysis can ensure every extern map has a Makefile object and a selector entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil.c

## Purpose
This file implements the generic K3 PSI-L endpoint lookup and replacement API used by TI K3 UDMA. It selects the proper SoC endpoint map at runtime and returns endpoint configuration for a PSI-L thread ID.

## Important APIs, Types, and Functions
The exported APIs are `psil_get_ep_config(u32 thread_id)` and `psil_set_new_ep_config(struct device *dev, const char *name, struct psil_endpoint_config *ep_config)`. Internal state is `soc_ep_map`, protected during first selection by `ep_map_mutex`. `k3_soc_devices[]` maps SoC family strings (`AM65X`, `J721E`, `J7200`, `AM64X`, `J721S2`, `AM62X`, `AM62AX`, `J784S4`, `AM62PX`, `J722S`) to endpoint maps.

## Control Flow
`psil_get_ep_config()` lazily matches the running SoC with `soc_device_match()`. If no match exists, it returns `ERR_PTR(-ENOTSUPP)`. For destination thread IDs with a destination map, it first scans the destination array for an exact ID. It then clears `K3_PSIL_DST_THREAD_ID_OFFSET` and scans the source array, enabling symmetric source/destination fallback. If no entry matches, it returns `ERR_PTR(-ENOENT)`. `psil_set_new_ep_config()` finds a named DMA entry in a device tree node, parses the matching `dmas` phandle, obtains the endpoint config by thread ID, and copies the supplied config into the map entry.

## State and Persistence
`soc_ep_map` is cached after first SoC match and persists for the lifetime of the module/kernel image. Endpoint configs are returned as mutable pointers into static SoC arrays. `psil_set_new_ep_config()` persistently mutates the selected static map entry, affecting all later users of that thread ID.

## Dependencies and Integration Points
The file depends on the Linux SoC device matching API, OF phandle parsing, module exports, mutexes, and the SoC maps declared in `k3-psil-priv.h`. It is selected by the TI K3 UDMA Kconfig path and consumed by UDMA/glue code that needs endpoint metadata.

## Risks
The SoC map is selected globally once; systems with unexpected family strings fail with `-ENOTSUPP`. Linear lookup is simple but table duplicates return the first match. Runtime replacement lacks copy-on-write or refcounting, so callers must coordinate if changing configs after users have cached pointers. Device-tree parsing in `psil_set_new_ep_config()` depends on matching `dma-names` and `dmas` indices.

## Test Signals
Test successful map selection for every family string, explicit destination lookup, symmetric fallback lookup, missing thread IDs, and missing SoC match. For `psil_set_new_ep_config()`, test invalid device/no OF node, missing `dma-names`, missing `dmas`, invalid thread ID, and successful mutation visible through a subsequent `psil_get_ep_config()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil.c -->
