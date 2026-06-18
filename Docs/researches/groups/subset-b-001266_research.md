# Research: subset-b-001266

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-glue.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-glue.c

## Purpose
`k3-udma-glue.c` is the exported glue layer for non-DMAengine clients that need direct packet-oriented access to TI K3 NAVSS UDMA or PKTDMA resources. It wraps low-level UDMA resources, ring accelerator rings, TISCI resource-manager calls, PSI-L thread pairing, and CPPI5 host descriptor sizing behind `k3_udma_glue_*` APIs. Typical users are peripheral drivers that manage descriptors themselves but still need the UDMA driver to allocate channels, flows, rings, interrupts, and address-space conversion consistently with the platform DMA controller.

## Important APIs, Types, And Functions
The central state is split into a shared `struct k3_udma_glue_common` and TX/RX specific containers. `k3_udma_glue_common` tracks the owning Linux device, an auxiliary channel device, `struct udma_dev`, TISCI RM handles, ringacc handle, PSI-L source and destination threads, descriptor metadata sizing, endpoint config, and PKTDMA ASEL. `struct k3_udma_glue_tx_channel` adds a reserved tchan, TX and completion rings, free-packet accounting, TISCI TX flags, a tflow id, and cached IRQ. `struct k3_udma_glue_rx_channel` adds an rchan, remote-channel mode, flow range, and an array of `struct k3_udma_glue_rx_flow`, each with an rflow, RX ring, FDQ ring, and IRQ.

The main exported TX API consists of `k3_udma_glue_request_tx_chn()`, `k3_udma_glue_request_tx_chn_for_thread_id()`, `k3_udma_glue_release_tx_chn()`, `k3_udma_glue_push_tx_chn()`, `k3_udma_glue_pop_tx_chn()`, `k3_udma_glue_enable_tx_chn()`, `k3_udma_glue_disable_tx_chn()`, `k3_udma_glue_tdown_tx_chn()`, `k3_udma_glue_reset_tx_chn()`, TX size/IRQ accessors, DMA device access, and DMA-to-CPPI5 address conversions. The RX API mirrors this with `k3_udma_glue_request_rx_chn()`, `k3_udma_glue_request_remote_rx_chn_for_thread_id()`, `k3_udma_glue_rx_flow_init()`, flow/ring accessors, flow enable/disable for remote RX, channel enable/disable/teardown/reset, push/pop, IRQ, DMA-device, and address conversion helpers.

Key internal helpers include `of_k3_udma_glue_parse*()` for device-tree and direct thread-id setup, `k3_udma_glue_cfg_tx_chn()` and `k3_udma_glue_cfg_rx_chn()` for TISCI channel config, `k3_udma_glue_cfg_rx_flow()` for RX flow and ring configuration, and `k3_udma_glue_allocate_rx_flows()` for general-purpose RX flow range ownership.

## Control Flow
TX allocation parses the `dmas` phandle or an explicit UDMA node/thread id, validates that the thread is a destination PSI-L thread, resolves endpoint metadata, computes host descriptor size, reserves a tchan through `xudma_tchan_get()`, registers an auxiliary channel device, optionally marks it coherent for PKTDMA ASEL 14/15 use, requests TX and completion rings, configures those rings, derives the UDMA source thread, and asks TISCI to program the TX channel. Enabling pairs source and destination PSI-L threads, enables peer runtime, then enables the tchan. Submission decrements `free_pkts`, writes the return policy to the descriptor, and pushes the descriptor DMA address to the TX ring. Completion pops from TXCQ and restores the free-packet count.

RX allocation validates flow-count rules, parses the source PSI-L thread, computes descriptor size, reserves an rchan for local RX unless the channel is remote, creates the channel device, validates or allocates a flow-id range, fills the flow array, derives the destination PSI-L thread, configures the RX channel, and optionally configures the default flow. `k3_udma_glue_cfg_rx_flow()` reserves the rflow, requests RX and FDQ rings, configures ring DMA attributes, and programs the TISCI flow with destination and free-descriptor queue ids. Local RX enable requires every flow to be ready, pairs PSI-L, and enables rchan/peer runtime. Remote RX deliberately does not control the rchan or PSI-L pair; it only owns flows and can enable or disable those flow queue destinations.

Reset paths account for hardware-cached ring state. TX reset drains the TX ring with a client cleanup callback, resets TXCQ normally, and resets TX by DMA-aware ring reset with the saved occupancy. RX reset similarly drains the FDQ unless a shared single FDQ is in use, then resets the completion ring.

## State And Persistence
All allocations are runtime kernel state owned by the caller's device via devm allocations plus explicit ring/resource release. Hardware state persists in UDMA channel runtime registers, ringacc rings, PSI-L pairings, and TISCI channel/flow configuration until disabled or released. `psil_paired`, `flows_ready`, ring pointers, and bitmap-owned `xudma_*` resources are the main software ownership guards. There is no on-disk persistence.

## Dependencies And Integration Points
This file depends on the private K3 UDMA exports from `k3-udma-private.c`, register definitions in `k3-udma.h`, endpoint metadata from `k3-psil-priv.h`, TI SCI RM/PSI-L operations, K3 ring accelerator APIs, CPPI5 descriptor helpers, Linux device-tree DMA spec parsing, and DMA mapping/coherency helpers. It is integrated as a module-init registered class for per-channel DMA devices and exports GPL symbols to other kernel drivers.

## Risks And Edge Cases
Error paths rely on `k3_udma_glue_release_*()` being safe for partially initialized channels. TX allocation after channel-device registration can return early on ring or TISCI failures, so release correctness is important. `k3_udma_glue_rx_flow_get_fdq_id()` returns `-EINVAL` through a `u32`, which callers must not treat as a valid ring id. Flow index bounds are checked in some APIs but not all push/pop/IRQ paths, so callers must pass valid flow ids. Teardown polling uses a fixed 1000 microsecond timeout and logs but does not fail hard. Remote RX intentionally rewrites only flow queue bindings, so misuse against a locally controlled channel returns `-EINVAL`.

## Test Signals
Useful validation signals are successful channel request/release cycles, correct TISCI request parameters for UDMA versus PKTDMA, PSI-L pair/unpair balance, ring occupancy and reset behavior under queued descriptors, IRQ number resolution for ring versus PKTDMA flow MSI events, ASEL address conversion round trips, remote RX flow enable/disable queue ids changing to and from `TI_SCI_RESOURCE_NULL`, and fault injection for partial allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-private.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-private.c

## Purpose
`k3-udma-private.c` exposes a narrow private ABI from the main K3 UDMA DMAengine provider to the glue layer and other closely related K3 DMA code. The file is included at the end of `k3-udma.c`, so it has access to internal static helpers and structures while still exporting symbols with stable `xudma_*` names. It avoids duplicating resource management, PSI-L pairing, ringacc lookup, and register access in glue clients.

## Important APIs, Types, And Functions
The exported PSI-L wrappers are `xudma_navss_psil_pair()` and `xudma_navss_psil_unpair()`, delegating to `navss_psil_pair()` and `navss_psil_unpair()`. Device lookup and property access helpers include `of_xudma_dev_get()`, `xudma_get_device()`, `xudma_get_ringacc()`, `xudma_dev_get_psil_base()`, and `xudma_dev_get_tisci_rm()`. Resource helpers include `xudma_alloc_gp_rflow_range()`, `xudma_free_gp_rflow_range()`, `xudma_rflow_is_gp()`, generated `xudma_tchan_get()/put()`, `xudma_rchan_get()/put()`, `xudma_rflow_get()/put()`, and generated id accessors. Runtime register access is exported through generated `xudma_tchanrt_read()/write()` and `xudma_rchanrt_read()/write()`. PKTDMA helpers are `xudma_is_pktdma()`, `xudma_pktdma_tflow_get_irq()`, and `xudma_pktdma_rflow_get_irq()`.

## Control Flow
`of_xudma_dev_get()` optionally follows a phandle property, finds the platform device by node, drops references appropriately, and returns the probed `struct udma_dev` or `-EPROBE_DEFER` if the DMA provider is not ready. Resource get functions reserve bits in the owning `udma_dev` bitmaps through internal helpers, and put functions clear those bits. RX flow get/put uses the dedicated flow in-use map and enforces GP-flow allocation rules through `__udma_get_rflow()`. Runtime register read/write helpers guard null resource pointers, then access the mapped channel runtime region.

## State And Persistence
This file does not create independent persistent state. It mutates the parent `struct udma_dev` resource bitmaps and accesses its TISCI, ringacc, MSI, and MMIO state. The resource put macros clear bitmap bits directly, so callers must pair get/put calls carefully and avoid double puts. Device-node and platform-device references are transient and released before returning.

## Dependencies And Integration Points
The implementation depends on static symbols and struct definitions from `k3-udma.c` because it is textually included there. Its public declarations live in `k3-udma.h`, and its consumers include `k3-udma-glue.c`. It integrates with device tree, platform device probing, K3 ringacc, TI SCI RM/PSI-L, MSI event offsets in `udma_soc_data`, and the UDMA resource bitmaps initialized by the main provider.

## Risks And Edge Cases
Because this is a private exported shim, ABI drift between `k3-udma.h`, this file, and `k3-udma.c` can break glue users at build or runtime. `xudma_tchan_put()` and `xudma_rchan_put()` clear allocation bits without validating that the pointer belongs to the device or is currently allocated, unlike `__udma_put_rflow()` which logs an unused-flow put. `of_xudma_dev_get()` returns a raw `udma_dev` pointer after dropping the platform-device reference, so normal device lifetime assumptions depend on provider-driver binding and probe ordering. Register helpers silently ignore null resources, which is convenient for cleanup but can mask invalid call paths.

## Test Signals
Useful tests include provider-probe deferral via `of_xudma_dev_get()`, resource get/put bitmap accounting, explicit-id reservation conflicts, RX flow GP allocation enforcement, PSI-L pair/unpair calls receiving the correct NAVSS device id and destination thread encoding, PKTDMA flow IRQ offsets, and null-resource runtime-register access returning or doing nothing without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma-private.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.c

## Purpose
`k3-udma.c` is the Linux DMAengine provider for TI K3 UDMA, BCDMA, and PKTDMA controllers. It discovers SoC-specific channel and flow resources, registers DMAengine channels, translates device-tree DMA requests into endpoint-specific channel configuration, programs hardware through TI SCI RM and PSI-L APIs, builds CPPI5 packet or TR descriptors, drives K3 ring accelerator queues, handles ring and data interrupts, reports residue/status, and manages teardown, pause/resume, PM suspend/resume, and debugfs summaries.

## Important APIs, Types, And Functions
The main device model is `struct udma_dev`, containing `struct dma_device`, MMIO windows, match and SoC data, TISCI handles, ringacc handle, resource bitmaps, hardware resource arrays, RX flush descriptors, purge work, and all `struct udma_chan` instances. `struct udma_chan` embeds `struct virt_dma_chan` and carries the allocated bchan/tchan/rchan/rflow, current and terminated descriptors, IRQs, channel state, DMA pool, endpoint config, and teardown completion. `struct udma_desc` wraps `virt_dma_desc` plus CPPI5 descriptor memory, metadata, residue, TR index, and static PDMA TR parameters.

Major provider entry points are `udma_probe()`, `udma_alloc_chan_resources()`, `bcdma_alloc_chan_resources()`, `pktdma_alloc_chan_resources()`, `udma_free_chan_resources()`, `udma_slave_config()`, `udma_prep_slave_sg()`, `udma_prep_dma_cyclic()`, `udma_prep_dma_memcpy()`, `udma_issue_pending()`, `udma_tx_status()`, `udma_pause()`, `udma_resume()`, `udma_terminate_all()`, and `udma_synchronize()`. Hardware setup is split across `udma_get_mmrs()`, `setup_resources()`, `udma_setup_resources()`, `bcdma_setup_resources()`, `pktdma_setup_resources()`, `udma_setup_rx_flush()`, and the TISCI channel config helpers. Completion is handled by `udma_ring_irq_handler()`, `udma_udma_irq_handler()`, `udma_vchan_complete()`, and `udma_check_tx_completion()`.

## Control Flow
Probe selects match data from compatible strings, derives SoC event offsets from match or `soc_device_match()`, maps global and runtime MMRs, obtains TI SCI handles and device ids, reads UDMA `ti,udma-atype` or BCDMA/PKTDMA `ti,asel`, initializes ringacc or DMA rings, obtains the TI SCI INTA MSI domain, sets DMAengine capabilities, initializes resource maps from TISCI resource ranges, allocates channel objects, initializes RX flush descriptors, fills hardware resource ids and runtime register bases, initializes virt-dma channels, registers the DMAengine device, and registers the OF DMA controller.

OF translation uses `udma_of_xlate()` and `udma_dma_filter_fn()`. UDMA/PKTDMA specs carry a remote thread plus optional atype/asel; BCDMA specs carry trigger type, remote thread, and asel. The filter determines direction from the PSI-L destination bit unless the request is a triggered BCDMA channel, fetches endpoint config from `psil_get_ep_config()`, rejects unsupported BCDMA packet mode, stores packet/TR mode, PDMA attributes, metadata sizing, throughput level, mapped PKTDMA channel and default flow, and address-space attributes.

Resource allocation depends on controller type and direction. UDMA MEM_TO_MEM reserves a matched tchan/rchan pair and rings, configures TISCI TX/RX, pairs PSI-L internally, and uses ring IRQ completion. UDMA slave TX or RX reserves a tchan or rchan/rflow, configures rings and TISCI, pairs the peripheral PSI-L thread, and may request both ring and UDMA data IRQs for TR mode. BCDMA uses bchan for memcpy, tchan/rchan for slave paths, different OES offsets, and optional router trigger events. PKTDMA supports only slave packet paths, uses tflow/rflow event offsets, mapped endpoint channels where provided, and DMA pools for host descriptors.

Descriptor preparation chooses among CPPI5 host packet descriptors, type1 TR descriptors, and type15 TR descriptors. Packet-mode slave transfers allocate one or more host descriptors from a DMA pool, attach SG buffers, link host buffer descriptors, set packet length, return policy, and optional metadata operations. TR-mode slave transfers build type1 TRs; triggered BCDMA and memcpy use type15 TRs. Large segments are split into at most two TRs by `udma_get_tr_counters()`. Cyclic paths build reloadable TR descriptors or per-period host descriptors. `udma_configure_statictr()` programs PDMA static TR fields and validates the Z/burst-count limit.

Submission moves prepared descriptors from virt-dma pending state to hardware rings. `udma_start()` resets stale teardown state, pushes descriptor addresses, programs PDMA static TR registers if needed, enables channel runtime registers, and sets `UDMA_CHAN_IS_ACTIVE`. Ring IRQs pop completion queue entries, detect teardown completion messages, handle cyclic callbacks, check delayed TX drain for PDMA TX, complete cookies, and start the next queued descriptor. Data IRQs handle TR event progress for slave TR mode. `udma_vchan_complete()` invokes callbacks after fetching packet metadata and building a `dmaengine_result`.

Termination marks the channel terminating, writes teardown or flush bits, moves the active descriptor to `terminated_desc`, cancels delayed TX drain work, and frees pending descriptors. `udma_synchronize()` waits up to one second for teardown completion, dumps channel state on timeout, optionally hard-resets by freeing and reallocating channel resources, resets runtime registers, cancels work, and resets rings.

## State And Persistence
Software state is entirely runtime kernel state. Resource availability is represented by bitmaps for bchan, tchan, rchan, GP rflows, in-use rflows, and tflows. Channel state moves through idle, active, and terminating, with `psil_paired`, current descriptor, terminated descriptor, `cyclic`, `paused`, and DMA-pool flags describing the active lifecycle. Hardware state lives in TISCI-managed channel/flow configuration, PSI-L pairings, ringacc rings, MSI allocations, and UDMA runtime registers. Descriptor memory is coherent or DMA-pooled and is freed either immediately or through `udma_purge_desc_work()` to avoid freeing non-pool descriptors in interrupt-sensitive paths. Suspend backs up configs for client-owned channels, frees resources, and resume restores configs and reallocates.

## Dependencies And Integration Points
The driver integrates with Linux DMAengine and virt-dma, OF DMA controller registration, TI SCI RM and PSI-L protocols, TI SCI INTA MSI, K3 ringacc, CPPI5 descriptor helpers, K3 event router for BCDMA triggered channels, `k3-psil-priv.h` endpoint tables, DMA mapping/coherency APIs, debugfs DMA summaries, and system sleep PM. It exposes private internals by including `k3-udma-private.c`, which in turn supports `k3-udma-glue.c`.

## Risks And Edge Cases
The code has multiple hardware-specific branches, so regressions often hide in one controller type or direction. Teardown is delicate: RX may need flush descriptors, TX toward PDMA may need delayed drain polling after completion ring arrival, and timeout recovery performs a hard reset. Descriptor size and TR counter limits reject unsupported large or poorly aligned transfers. BCDMA linked or triggered operation depends on event-router configuration and correct OES offsets. PKTDMA ASEL/coherency handling is limited to expected ASEL values and mapped endpoint metadata. Error paths must unwind IRQs, PSI-L pairs, rings, DMA pools, and bitmaps in the right order. Resource maps are derived from TISCI ranges, so missing or wrong firmware resource descriptions can hide channels or expose invalid ones.

## Test Signals
Strong test signals include probe on each compatible family, resource counts matching capability registers and TISCI ranges, OF DMA request filtering for UDMA/BCDMA/PKTDMA specs, slave SG in packet and TR mode, memcpy on supported controllers, cyclic on UDMA/BCDMA but not PKTDMA, BCDMA triggered-router setup, metadata attach/get/set behavior, residue and in-flight-byte reporting during active transfers, pause/resume restrictions, teardown timeout recovery, suspend/resume with active client channels, MSI/ring IRQ completion, and fault-injection coverage for every allocation stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.h

## Purpose
`k3-udma.h` is the local private header shared by the K3 UDMA provider, its private-export shim, and the glue layer. It defines hardware register offsets, capability-field decoders, runtime control bits, PDMA static TR bitfield helpers, the K3 address-space-select shift, the TISCI resource-manager wrapper structure, resource range identifiers, forward declarations, and the `xudma_*` private API declarations.

## Important APIs, Types, And Constants
The header defines global MMR offsets such as `UDMA_REV_REG`, `UDMA_CAP_REG()`, and RX flow event registers; channel runtime offsets such as `UDMA_CHAN_RT_CTL_REG`, `UDMA_CHAN_RT_PEER_STATIC_TR_XY_REG`, `UDMA_CHAN_RT_PEER_BCNT_REG`, and byte/packet counters; and capability decoders for UDMA, BCDMA, and PKTDMA counts. Runtime control bits include `UDMA_CHAN_RT_CTL_EN`, teardown, pause, flush teardown, error, and peer enable/teardown/pause/flush/idle bits. PDMA helpers define static TR X/Y/Z masks and the ACC32/BURST flags. `K3_ADDRESS_ASEL_SHIFT` defines where PKTDMA/BCDMA ASEL bits are inserted into DMA addresses.

`enum udma_rm_range` names TISCI resource ranges for bchan, tchan, rchan, rflow, and tflow. `struct udma_tisci_rm` groups the TI SCI handle, UDMAP RM ops, DMA controller device id, PSI-L ops, NAVSS device id, and resource range pointers. The declared API covers PSI-L pair/unpair, provider lookup from OF, device/ringacc/TISCI/PSI-L-base accessors, GP RX flow range allocation, tchan/rchan/rflow get/put/id helpers, runtime register read/write helpers, GP-flow classification, PKTDMA detection, and PKTDMA flow IRQ lookup.

## Control Flow
This header does not implement control flow, but it defines the contract used by the implementation. `k3-udma.c` uses the register offsets and bit definitions for runtime channel control, setup, status, and debug. `k3-udma-private.c` implements the declared `xudma_*` functions by delegating into provider internals. `k3-udma-glue.c` consumes those declarations to request resources, program runtime registers, pair PSI-L threads, and convert PKTDMA CPPI5 addresses.

## State And Persistence
The header stores no state. Its declarations describe runtime resources owned by `struct udma_dev`, `struct udma_tchan`, `struct udma_rchan`, and `struct udma_rflow`, all forward-declared here and defined in the provider implementation. The bit definitions directly affect persistent hardware register state when used by callers.

## Dependencies And Integration Points
It includes `linux/soc/ti/ti_sci_protocol.h` for TI SCI types and is consumed by K3 UDMA C files in this directory. It is part of the private source-level boundary between the DMAengine provider and the exported glue API, not a public UAPI header.

## Risks And Edge Cases
Incorrect register offsets or bit masks would affect all K3 UDMA paths. Capability decoders are SoC-specific, so adding new controller variants requires validating the bit layout. ASEL insertion at bit 48 assumes DMA addresses and masks are consistent with the 48-bit coherent mask used in the provider and glue paths. Because private API declarations expose opaque resource types, mismatches between declarations and included implementation can cause subtle ownership bugs.

## Test Signals
Validation comes from build coverage of all C files using the header, probe-time resource counts decoded from capability registers, runtime register writes producing expected channel state, PDMA static TR programming for supported endpoints, ASEL address conversion tests, and private API consumers linking against the expected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/omap-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ti/omap-dma.c

## Purpose
`omap-dma.c` is the DMAengine provider for legacy TI OMAP system DMA controllers. It exposes slave, cyclic, memcpy, and interleaved DMA operations through virt-dma, allocates logical DMA channels, programs OMAP channel registers, optionally uses OMAP linked-list type2 descriptors for multi-SG slave transfers, services global L1 DMA interrupts or legacy callbacks, and handles OMAP-specific errata, idle-state constraints, and context save/restore.

## Important APIs, Types, And Functions
`struct omap_dmadev` owns the DMAengine device, MMIO base, register map, platform data, SoC config, logical-channel bitmap, interrupt mask, descriptor pool, logical-channel map, and optional CPU PM notifier/context. `struct omap_chan` embeds `virt_dma_chan` and stores per-channel register base, cached CCR, slave config, DMA request signal, cyclic/paused/running state, assigned logical channel, active descriptor, and SG index. `struct omap_desc` represents a virt-dma descriptor with direction, device address, element size, CCR/CICR/CSDP/CLNK register values, optional polled completion, and a flexible array of `struct omap_sg`. `struct omap_type2_desc` mirrors hardware linked-list descriptor layout.

Provider entry points include `omap_dma_probe()`, `omap_dma_remove()`, `omap_dma_alloc_chan_resources()`, `omap_dma_free_chan_resources()`, `omap_dma_slave_config()`, `omap_dma_prep_slave_sg()`, `omap_dma_prep_dma_cyclic()`, `omap_dma_prep_dma_memcpy()`, `omap_dma_prep_dma_interleaved()`, `omap_dma_issue_pending()`, `omap_dma_tx_status()`, `omap_dma_pause()`, `omap_dma_resume()`, `omap_dma_terminate_all()`, and `omap_dma_synchronize()`. Low-level helpers include register read/write wrappers for 16-bit, split 2x16-bit, and 32-bit layouts, logical-channel allocation/free, descriptor start/stop, IRQ handling, residue helpers, linked-list descriptor fill, busy checks, and context save/restore.

## Control Flow
Probe maps the controller registers, chooses OF match or OMAP1 platform configuration, initializes DMAengine capabilities and callbacks, determines request and logical-channel counts from platform data or DT, applies any logical-channel mask/reserved channels, allocates one virt-dma channel per DMA request, installs the shared L1 IRQ when available or marks legacy mode, detects LL123 linked-list support, creates a descriptor pool for type2 descriptors, registers the DMAengine device, optionally registers an OF DMA controller, initializes global arbitration/fifo settings, and registers a CPU PM notifier when the SoC needs busy checks or context restore.

Channel allocation either calls legacy `omap_request_dma()` or assigns a free logical channel from `lch_bitmap`, maps that logical channel to the virt channel, enables only L1 interrupts for the assigned channel, disables L0, computes the channel CCR sync/request bits, and applies buffering-disable errata. Freeing disables the L1 bit, clears the map, frees virt descriptors, and releases the legacy or bitmap logical channel.

Descriptor preparation programs register values rather than CPPI5 descriptors. Slave SG validates bus width, determines device address and burst/window parameters, builds `CCR`, `CSDP`, and `CICR`, computes EN/FN frame counts for each SG, and optionally allocates type2 linked-list descriptors when supported and sglen is at least two. Cyclic setup creates one repeating descriptor with frame interrupts when requested and configures auto-init or channel linking depending on OMAP generation. Memcpy and interleaved paths create single-descriptor memory-to-memory transfers, with memcpy optionally using polled completion when interrupts are suppressed.

Issuing pending descriptors calls `omap_dma_start_desc()` when idle. Start writes the static channel registers, source/destination address and index registers, CSDP, link control, current SG address/counts, interrupt enable, and finally enables CCR. IRQ handling reads global L1 status, masks enabled channels, clears per-channel CSR and global status, then calls `omap_dma_callback()`. The callback invokes cyclic callbacks, completes linked-list or final SG descriptors, starts the next descriptor, or advances to the next SG. `omap_dma_tx_status()` computes residue from current source or destination address registers and handles polled memcpy completion by observing CCR enable clearing.

Pause is intentionally restricted. Cyclic transfers can pause, and non-cyclic DEV_TO_MEM can pause because disabling destination-synchronized MEM_TO_DEV can abort and lose FIFO data. Resume restores link control and restarts the active descriptor. Terminate stops the active descriptor unless already paused, clears cyclic/paused flags, and frees queued descriptors.

## State And Persistence
Runtime state is held in logical-channel bitmaps, `lch_map`, per-channel `desc`, `sgidx`, `paused`, `cyclic`, and `running`, and global IRQ masks. Hardware state is in OMAP DMA global and channel registers. Context persistence is SoC-dependent: OMAP3-like controllers may lose context across CPU cluster idle, so `omap_dma_context_save()` stores IRQ enable, OCP sysconfig, and GCR, while restore rewrites them and clears channels. Busy-check notifiers can block deeper idle states while channels are enabled. There is no filesystem persistence.

## Dependencies And Integration Points
The driver integrates with DMAengine and virt-dma, OMAP platform data and register maps from `linux/omap-dma.h`, OF DMA simple xlate/filter mapping, optional legacy OMAP DMA APIs, CPU PM notifiers, DMA pools for hardware linked lists, and platform IRQ/resource management. It uses SoC match data for OMAP2420/2430/3430/3630/4430 variants and runtime `dma_omap1()`/`__dma_omap*()` helpers for generation differences.

## Risks And Edge Cases
The driver carries many generation and errata paths. Stopping a channel must drain FIFO unless buffering is disabled, and erratum i541 temporarily changes idle mode. Pause forbids MEM_TO_DEV to avoid abort/data loss. Linked-list allocation can partially fail; the code falls back to non-linked SG and frees any allocated descriptors. Residue depends on reading current-address registers and has OMAP3.2/3.3 double-read handling. `omap_dma_filter_fn()` accepts `req <= dma_requests`, so request numbering expectations must match platform mapping. Context restore clears all logical channels, which is appropriate only when active channels were blocked before idle.

## Test Signals
Useful validation includes probe on each compatible and OMAP1 platform-data mode, DMA request filtering and slave map coverage, logical-channel mask/reservation behavior, IRQ enable/disable for L1, slave SG with and without linked-list support, cyclic frame callbacks, memcpy with interrupt and polled completion modes, interleaved stride validation, residue reporting during active transfers, pause/resume restrictions, terminate while active or paused, CPU PM busy/context notifier behavior, and errata paths for drain and address-register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ti/omap-dma.c -->
