# subset-b-001252 Research

Grouped report for subset-b-001252. Each section preserves the source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bcm-sba-raid.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bcm-sba-raid.c

Purpose: Broadcom SBA RAID DMAengine provider. It exposes one DMA channel backed by a Broadcom mailbox/ring-manager channel and offloads interrupt, memcpy, XOR, and RAID6 PQ operations by emitting `brcm_sba_command` sequences instead of programming local registers directly.

Important APIs/types/functions: `struct sba_device` owns DT-derived hardware limits, mailbox client/channel, DMA device/channel, preallocated coherent response/command pools, request lists, and debugfs. `struct sba_request` wraps a `dma_async_tx_descriptor`, a `brcm_message`, command array, and chained-request bookkeeping. Key callbacks are `sba_prep_dma_interrupt`, `sba_prep_dma_memcpy`, `sba_prep_dma_xor`, `sba_prep_dma_pq`, `sba_tx_submit`, `sba_issue_pending`, `sba_tx_status`, and `sba_device_terminate_all`.

Control flow: probe identifies `brcm,iproc-sba` versus `brcm,iproc-sba-v2`, derives buffer/PQ command limits, requests mailbox channel 0, resolves the mailbox device, preallocates 8192 request slots plus coherent command/response pools, registers debugfs stats, and registers a DMA device. Prep paths split large operations at `hw_buf_size` boundaries and chain requests through `first`, `next`, and `next_pending_count`. Submit assigns a cookie and moves all chain members to pending. Issue-pending sends up to eight mailbox messages per pass, respecting `SBA_REQUEST_FENCE`. Mailbox receive completes the first descriptor only after all chained messages have returned, invokes callbacks, unmaps, frees the chain, and drains more pending work.

State and persistence: Runtime state is in protected request lists: free, allocated, pending, active, aborted. It also stores `reqs_fence` to serialize fenced work. There is no persistent disk state; device state is reconstructed on probe. Coherent pools persist for the device lifetime.

Dependencies/integration: Linux DMAengine/async_tx, RAID6 GF tables, Broadcom mailbox message ABI, OF platform data, coherent DMA mapping, and debugfs. The DMA device is anchored to the mailbox device because memory access is performed by the ring-manager/SBA path.

Risks: mailbox send errors leave the request pending; aborted active requests rely on eventual receive callbacks for cleanup. PQ slow-path chaining and `DMA_PREP_CONTINUE` ordering are delicate. Request exhaustion depends on `mbox_client_peek_data()` progressing completions. Coherent pool sizing scales with fixed `SBA_MAX_REQ_PER_MBOX_CHANNEL`.

Test signals: boot/probe logs, DMAengine capability registration, debugfs `stats` counts returning to free after work, async_tx memcpy/xor/pq validation, RAID6 parity checks, fence ordering tests, terminate-all while active, mailbox error injection, and module remove with no leaked requests or coherent mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bcm-sba-raid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bcm2835-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bcm2835-dma.c

Purpose: DMAengine driver for the BCM2835/Raspberry Pi DMA controller. It supports private slave, cyclic audio-style, and memcpy transfers over hardware control-block chains and uses `virt-dma` for descriptor queuing.

Important APIs/types/functions: `struct bcm2835_dmadev` holds the DMA device, MMIO base, and mapped zero page. `struct bcm2835_chan` stores `virt_dma_chan`, slave config, DREQ, channel MMIO, IRQ, lite-channel flag, and control-block pool. `struct bcm2835_desc` contains direction, frame count, cyclic flag, total size, and a flexible control-block array. Main callbacks are `bcm2835_dma_prep_dma_memcpy`, `bcm2835_dma_prep_slave_sg`, `bcm2835_dma_prep_dma_cyclic`, `bcm2835_dma_issue_pending`, `bcm2835_dma_tx_status`, `bcm2835_dma_terminate_all`, and `bcm2835_dma_xlate`.

Control flow: probe maps registers, maps a zero page, reads `brcm,dma-channel-mask`, resolves per-channel IRQs including legacy shared IRQ handling, initializes channels, registers an OF DMA controller, then registers the DMAengine device. Each channel allocates a DMA pool for 32-byte aligned control blocks when resources are requested. Prep routines calculate frame counts, allocate one CB per frame, fill source/destination/length/info fields, chain CBs via `next`, and use `vchan_tx_prep`. Issue-pending starts the next queued descriptor if idle by writing first CB address and `ACTIVE`. IRQ clears INT while keeping ACTIVE, completes non-cyclic descriptors only when the current CB address becomes zero, and calls cyclic callbacks for cyclic descriptors.

State and persistence: Active state is per-channel: `desc`, queued virt-dma descriptors, DMA pool, slave config, DREQ, IRQ flags, and hardware registers. The zero-page DMA mapping lives for the device lifetime. No persistent state survives driver unload.

Dependencies/integration: DMAengine, OF DMA translation, `virt-dma`, DMA pools, IRQ framework, BCM2835 DT properties and interrupts. The xlate callback takes a DREQ ID from the DMA spec and returns an exclusive slave channel.

Risks: lite channels have a 64 KiB minus 4 limit, so frame splitting must be correct. Cyclic period lengths not dividing buffer length are allowed with a warning but may create latency artifacts. Shared IRQ filtering depends on the INT bit. The zero-page optimization is disabled for lite channels. Suspend fails with `-EBUSY` if any DMA address register remains nonzero.

Test signals: DT probe with named and legacy interrupts, slave SG and cyclic audio transfers with period callbacks, memcpy validation across lite and full channels, residue checks while active, terminate-all abort path, suspend-busy behavior, and IRQ sharing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bcm2835-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Kconfig

Purpose: Kconfig menu entries for the Freescale MPC5200 BestComm communication coprocessor support and its optional task families. Important symbols: `PPC_BESTCOMM` is a tristate gated by `PPC_MPC52xx`, selects `PPC_LIB_RHEAP`, and represents the core BestComm engine/SRAM allocator. `PPC_BESTCOMM_ATA`, `PPC_BESTCOMM_FEC`, and `PPC_BESTCOMM_GEN_BD` are tristate task-library symbols that depend on the core.

Control flow/state: This file controls build-time configuration rather than runtime behavior. Choices persist in `.config` and drive which objects the Makefile includes. The task symbols are hidden and normally selected by dependent drivers or platform configuration.

Dependencies/integration: PowerPC MPC52xx platform support, reusable heap allocator, and downstream ATA/FEC/PSC users of BestComm APIs.

Risks and test signals: Hidden task symbols can be missed if users fail to select them. Test with Kconfig dependency validation, `make olddefconfig`, module/built-in combinations, and link coverage for dependent users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Makefile

Purpose: Kbuild description for BestComm core and task helper modules. It groups `bestcomm.o` and `sram.o` into `bestcomm-core`, ATA wrapper plus ATA microcode into `bestcomm-ata`, FEC wrapper plus RX/TX microcode into `bestcomm-fec`, and generic BD wrapper plus RX/TX microcode into `bestcomm-gen-bd`.

Control flow/state: No runtime code. Kbuild includes each composite object according to `CONFIG_PPC_BESTCOMM*` symbols; build artifacts and module composition are its only state.

Dependencies/integration: Sibling Kconfig and wrapper references to generated task arrays. Grouping ensures each wrapper links with its microcode image.

Risks and test signals: Missing image objects would surface as link failures. Test by building each config combination and checking module composition/undefined symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/ata.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/ata.c

Purpose: BestComm ATA task wrapper. It allocates a task, loads ATA microcode, initializes variables/increments, and exports helpers to prepare RX or TX direction.

Important APIs/types/functions: `bcom_ata_init`, `bcom_ata_rx_prepare`, `bcom_ata_tx_prepare`, `bcom_ata_reset_bd`, and `bcom_ata_release`; microcode variable/increment structs cover enable register, BD ring bounds, buffer size, and signed transfer increments.

Control flow/state: init disables prefetch, allocates a BD-backed task, resets BDs, loads `bcom_ata_task`, patches SDMA/BD variables, configures pragma/auto-start and ATA initiator priorities, and clears pending interrupts. RX/TX prepare changes increments and initiator. State lives in the `bcom_task`, SRAM BD ring, task var/inc areas, and indices; reset clears BDs and rewinds indices.

Dependencies/integration: BestComm core APIs, ATA microcode image, MPC52xx SDMA registers, and ATA BestComm headers. Risks include the required prefetch disable, assuming `bcom_eng` is initialized, and direction setup ordering. Test with ATA DMA read/write, ring reset, interrupt clear, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/ata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_ata_task.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_ata_task.c

Purpose: Static BestComm ATA microcode image as `u32 bcom_ata_task[]`. It contains the BestComm header, descriptor words, default VAR words, and INC words decoded in comments.

Control flow/state: No C control flow. `bcom_load_image()` validates the header, copies descriptors/variables/increments to SRAM, and `ata.c` patches runtime variables. The array is immutable module data; active state exists only after loading.

Dependencies/integration: External symbol consumed by `bcom_ata_init()` and the BestComm task image ABI.

Risks and test signals: Header size fields and payload layout must match; edits are firmware-like. Validate by successful load, ATA DMA integrity, expected interrupts, and no invalid-microcode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_ata_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_rx_task.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_rx_task.c

Purpose: Static BestComm FEC receive microcode image exposed as `u32 bcom_fec_rx_task[]`.

Control flow/state: The array has a standard task header, descriptor stream, default variables, and increments. `bcom_fec_rx_reset()` loads it and patches enable register, FEC FIFO, BD ring addresses, and max receive size. The array is read-only module data; runtime state lives in SRAM and caller-managed BDs.

Dependencies/integration: `fec.c`, `bcom_load_image()`, BestComm SRAM layout, and MPC52xx FEC RX expectations.

Risks and test signals: Opaque image must match wrapper var/inc structs. Test RX packets under load, BD updates, interrupts, reset/reload, and loader diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_rx_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_tx_task.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_tx_task.c

Purpose: Static BestComm FEC transmit microcode image exposed as `u32 bcom_fec_tx_task[]`.

Control flow/state: No C path. `bcom_fec_tx_reset()` loads this image, locates a self-modified DRD in the copied descriptor stream, and patches FIFO, enable register, BD ring bounds/start, and DRD physical address. Mutable state exists only in SRAM after loading.

Dependencies/integration: FEC task wrapper, BestComm loader, and MPC52xx FEC networking transmit path.

Risks and test signals: TX depends on descriptor order expected by `self_modified_drd()`. Test packet TX, completion interrupts, reset after activity, and DRD location validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_fec_tx_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_rx_task.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_rx_task.c

Purpose: Static BestComm generic buffer-descriptor receive microcode image for PSC and other generic BD consumers.

Control flow/state: `gen_bd.c` loads `bcom_gen_bd_rx_task[]` during RX reset and patches enable, FIFO, BD ring, buffer size, and increments. The compiled array is immutable; copied SRAM image plus BD ring are runtime state.

Dependencies/integration: Generic BD RX wrappers, PSC helpers, BestComm loader, and MPC52xx initiator/IPR constants.

Risks and test signals: Layout-sensitive firmware-like data. Test PSC/generic RX DMA, ring wrap, interrupts, reset, and boundary-sized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_rx_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_tx_task.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_tx_task.c

Purpose: Static BestComm generic buffer-descriptor transmit microcode image for generic and PSC transmit paths.

Control flow/state: `bcom_gen_bd_tx_reset()` loads the array and patches enable, FIFO, BD ring, source increments, pragma, initiator, and priority. The source array is read-only; runtime mutation occurs in SRAM.

Dependencies/integration: `gen_bd.c`, PSC helper APIs, BestComm image ABI, and MPC52xx SDMA/FIFO addressing.

Risks and test signals: Wrapper/image variable offsets must agree. Test generic/PSC TX DMA, ring wrap, interrupt-on-completion, FIFO integrity, and reset after transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bcom_gen_bd_tx_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bestcomm.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bestcomm.c

Purpose: Core MPC52xx BestComm/SDMA coprocessor driver. It initializes shared SRAM structures, maps SDMA registers, exports task allocation/loading/control APIs, and registers early with `subsys_initcall`.

Important APIs/types/functions: exported `bcom_eng`, `bcom_task_alloc`, `bcom_task_free`, `bcom_load_image`, `bcom_set_initiator`, `bcom_enable`, and `bcom_disable`; lifecycle functions `bcom_engine_init`, `bcom_engine_cleanup`, `mpc52xx_bcom_probe`, and remove.

Control flow/state: probe locates SRAM, initializes allocator, allocates engine state, maps registers, and creates SRAM TDT/context/var/FDT regions. Task allocation reserves a task via TDT `stop`, maps IRQ, and optionally allocates BD SRAM. Image loading validates magic, allocates or validates descriptor area, clears var/inc areas, and copies image sections. State is the singleton engine, registers, SRAM heaps, task tables, contexts, vars, and BDs.

Dependencies/integration: OF platform matching, MPC52xx register definitions, BestComm headers, SRAM allocator, IRQ mapping, and exported symbols consumed by task wrappers.

Risks and test signals: Singleton initialization and task reservation are central. Test boot logs, SRAM allocation, all task families, microcode reload validation, initiator patching, IRQ mapping, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/bestcomm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/fec.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/fec.c

Purpose: BestComm wrapper for MPC52xx FEC Ethernet RX/TX DMA.

Important APIs/types/functions: `bcom_fec_rx_init/reset/release`, `bcom_fec_tx_init/reset/release`, RX/TX var/inc structs, private FIFO/maxbuf data, and `self_modified_drd()`.

Control flow/state: RX/TX init allocate tasks with FEC BD rings and private data, then reset. Reset disables the task, loads the matching image, patches enable/FIFO/BD variables and increments, clears BDs and indices, configures pragma/auto-start/IPR, and clears interrupts. TX additionally records a self-modified DRD physical address. State lives in task private data, SRAM var/inc areas, and BD rings.

Dependencies/integration: BestComm core, FEC RX/TX microcode arrays, MPC52xx SDMA/FEC constants, and the network FEC driver.

Risks and test signals: TX descriptor search is sensitive to microcode layout; reset must be externally synchronized with network BD ownership. Test FEC traffic, ring wrap, packet-size boundaries, link-cycle resets, and unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/fec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/gen_bd.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/gen_bd.c

Purpose: Generic BestComm buffer-descriptor wrapper for peripherals such as MPC52xx PSC, with RX/TX task allocation, reset, release, and PSC-specific constructors.

Important APIs/types/functions: `bcom_gen_bd_rx_init/reset/release`, `bcom_gen_bd_tx_init/reset/release`, `bcom_psc_gen_bd_rx_init`, `bcom_psc_gen_bd_tx_init`, generic var/inc layouts, and `bcom_psc_params`.

Control flow/state: init stores FIFO/initiator/IPR/maxbuf private data and calls reset. Reset disables the task, loads microcode, patches enable/FIFO/BD variables, sets increments, clears BDs/indices, programs pragmas/auto-start and initiator priority, and clears interrupts. State is task private data, SRAM var/inc areas, and BD rings.

Dependencies/integration: BestComm core, generic BD microcode, MPC52xx PSC constants, and PSC/generic FIFO drivers.

Risks and test signals: TX PSC helper lacks the RX bounds check for `psc_num`; callers must validate. Test PSC RX/TX across valid ports, invalid RX index, caller-side TX validation, ring wrap, reset, interrupts, and FIFO integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/gen_bd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/sram.c -->
# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/sram.c

Purpose: Simple BestComm on-board SRAM allocator backed by PowerPC `rheap`.

Important APIs/types/functions: exported `bcom_sram`, `bcom_sram_init`, `bcom_sram_cleanup`, `bcom_sram_alloc`, and `bcom_sram_free`.

Control flow/state: init prevents double initialization, resolves SRAM OF resource, requests and maps it, creates an rheap, attaches the whole region, and initializes a spinlock. Alloc/free lock around `rh_alloc_align`/`rh_free` and translate between offset, virtual pointer, and physical address. Cleanup destroys heap, unmaps, releases region, and clears singleton state.

Dependencies/integration: OF address/resource handling, IO mapping, PowerPC rheap, and BestComm task/core allocations.

Risks and test signals: Allocator is not IRQ-safe per comment. The partial-zone code is inactive, so the full SRAM region is always attached. Test init, alignment, exhaustion, cleanup, and mixed BestComm allocation sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/bestcomm/sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/cv1800b-dmamux.c -->
# sources/distributed-fs/ceph-client/drivers/dma/cv1800b-dmamux.c

Purpose: DMA router/DMAMUX driver for Sophgo CV1800/SG2000 SoCs. It maps peripheral request IDs and CPU interrupt targets onto physical DMA channels before delegating to a master DMA controller.

Important APIs/types/functions: `struct cv1800_dmamux_data`, `struct cv1800_dmamux_map`, `cv1800_dmamux_route_allocate`, `cv1800_dmamux_free`, probe, and remove.

Control flow/state: probe gets the parent syscon regmap, preallocates map objects for channels 0..7, and registers an OF DMA router. Allocation validates two spec cells, rewrites the downstream spec to one channel cell, parses `dma-masters`, reuses a reserved map or consumes a free map, programs channel remap and interrupt mux registers, and returns route data. Free clears/remaps register state. State is in free/reserved lists, a peripheral bitmap, map records, and syscon registers.

Dependencies/integration: OF DMA router API, regmap/syscon parent, platform lookup, spinlock guard helpers, and downstream DMA master.

Risks and test signals: `devid > MAX_DMA_MAPPING_ID` may allow an out-of-range bitmap index when ID equals 42. Reserved maps are kept for reuse rather than returned to free. Test valid/invalid route cells, repeated requests, channel exhaustion, free register state, interrupt CPU selection, and bitmap boundary IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/cv1800b-dmamux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dma-axi-dmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/dma-axi-dmac.c

Purpose: DMAengine driver for Analog Devices AXI-DMAC soft IP. It supports one configured channel with slave SG, peripheral vectors, cyclic/repeated transfers, interleaved 2D transfers, optional hardware SG, partial-transfer reporting, and capability discovery.

Important APIs/types/functions: `struct axi_dmac`, `struct axi_dmac_chan`, `struct axi_dmac_desc`, `axi_dmac_start_transfer`, `axi_dmac_transfer_done`, IRQ handler, prep callbacks, `axi_dmac_detect_caps`, and probe.

Control flow/state: probe maps MMIO, enables clock, reads version, discovers interface config from registers or DT, detects feature bits by register probing, validates coherency if requested, registers DMAengine and OF controller, and requests IRQ. Prep allocates coherent hardware descriptors, validates direction/address/length, fills linear/2D/cyclic SGs, and queues via virt-dma. IRQ acknowledges SOT/EOT, records partial lengths, completes or cycles descriptors, and starts queued work. State includes active descriptors, `next_desc`, IDs, partial lengths, and MMIO registers.

Dependencies/integration: DMAengine, virt-dma, OF DMA helpers, ADI version macros, DT bus-type bindings, clk, IRQ, coherent DMA, and regmap.

Risks and test signals: Cyclic termination differs by SG/non-SG; old non-SG cores need a hotfix. Capability probing writes registers. Test old/new IP, SG/non-SG, cyclic EOT, partial residue, interleaved limits, coherent DT validation, terminate-all, and IRQ sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dma-axi-dmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dma-jz4780.c -->
# sources/distributed-fs/ceph-client/drivers/dma/dma-jz4780.c

Purpose: DMAengine driver for Ingenic JZ47xx/X1000/X1830 DMA controllers, supporting memcpy, slave SG, and cyclic transfers through hardware descriptor blocks.

Important APIs/types/functions: `struct jz4780_dma_dev`, `struct jz4780_dma_chan`, `struct jz4780_dma_desc`, prep callbacks, `jz4780_dma_begin`, IRQ handler, OF xlate, probe, and SoC match data.

Control flow/state: probe validates OF match data, maps channel/control registers, enables clock, reads reserved channels, configures DMAengine callbacks, enables controller bits, initializes virt channels, applies a channel-enable workaround, requests IRQ, registers DMAengine, and registers OF DMA. Prep allocates descriptor blocks, computes transfer size/shift, fills SG/cyclic/memcpy descriptors, and queues them. IRQ scans pending channels, handles DCS errors/completion, cycles periodic descriptors, and restarts work. State is per-channel active descriptor, current descriptor index, descriptor pool, slave config, transfer types, and registers.

Dependencies/integration: DMAengine/virt-dma, OF DMA, clk, IRQ, DMA pools, Ingenic compatibles, and reserved-channel DT property.

Risks and test signals: Break-links SoC mode changes completion sequencing. Cyclic callbacks may require unlinking descriptors. Status path assumes active descriptor for active cookie cases. Test all compatibles, reserved xlate, SG/cyclic/memcpy, residue, address/halt errors, break-links behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dma-jz4780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmaengine.c -->
# sources/distributed-fs/ceph-client/drivers/dma/dmaengine.c

Purpose: Core Linux DMAengine subsystem implementation. It manages provider registration, channel allocation/release, public channel rebalancing, OF/ACPI/filter-map requests, sysfs/debugfs exposure, unmap pools, metadata helpers, and dependency submission.

Important APIs/types/functions: global provider list/mutex/IDA/ref count/per-CPU channel table; exported request/release, registration, async wait, unmap, metadata, and dependency helpers.

Control flow/state: init creates channel tables, unmap pools, DMA class, and debugfs. Provider registration validates callbacks, assigns IDs, creates channel devices, takes references for existing async clients, adds the provider to the global list, and rebalances. Request paths resolve firmware mappings or filters, mark exclusive channels private, allocate provider resources, and create sysfs links. Release and unregister unwind links, router mappings, resources, references, debugfs, channel devices, and krefs. State is all in kernel memory: provider list, counts, krefs, sysfs/debugfs objects, per-CPU stats, and mempools.

Dependencies/integration: DMA providers, async_tx clients, OF/ACPI DMA helpers, sysfs, debugfs, modules, RCU/kref/IDA, mempool/slab, and DMA mapping.

Risks and test signals: Locking and private-channel accounting are critical; providers without `device_release` are unsafe to unbind while referenced. Metadata modes cannot mix. Test registration/unregistration under clients, devm release, firmware/filter requests, sysfs counters, rebalancing, metadata errors, unmap pools, and dependency chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmaengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmaengine.h -->
# sources/distributed-fs/ceph-client/drivers/dma/dmaengine.h

Purpose: Private helper header for DMAengine provider drivers, supplying cookie helpers, callback helpers, private slave-channel declarations, and debugfs root access.

Important APIs/types/functions: `dma_cookie_init`, `dma_cookie_assign`, `dma_cookie_complete`, `dma_cookie_status`, residue/in-flight setters, `struct dmaengine_desc_callback`, callback get/invoke helpers, `dma_get_slave_channel`, `dma_get_any_slave_channel`, and `dmaengine_get_debugfs_root`.

Control flow/state: Providers initialize cookies, assign monotonically increasing nonzero cookies under their own lock, complete descriptors by updating `completed_cookie`, and report lockless snapshot status. Callback helpers invoke result-aware or legacy callbacks with a default success result. State touched is in `dma_chan`, descriptors, and optional tx state.

Dependencies/integration: DMAengine providers and `dmaengine.c`, public DMAengine types, and optional debugfs.

Risks and test signals: Cookie helpers rely on driver serialization and `dma_cookie_complete` BUGs on invalid cookies. Callback locking is driver-defined. Test cookie ordering/wrap, status/residue reporting, both callback styles, and debugfs behavior with/without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dmaengine.h -->
