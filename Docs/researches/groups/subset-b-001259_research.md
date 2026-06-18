# Research Report: subset-b-001259

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor_v2.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mv_xor_v2.c

## Purpose
`mv_xor_v2.c` is a Linux dmaengine provider for Marvell's version 2 XOR engine. It exposes one DMA channel with `DMA_MEMCPY`, `DMA_XOR`, and `DMA_INTERRUPT` capabilities, programs a fixed-size hardware descriptor queue, and completes async_tx requests from MSI-driven interrupts.

## Important APIs, Types, and Functions
- `struct mv_xor_v2_descriptor` is the 128-byte hardware descriptor. It stores operation mode, source/destination addresses, buffer size, XOR data-buffer address packing, and a software descriptor id.
- `struct mv_xor_v2_device` holds MMIO bases, clocks, the single `dma_chan`, descriptor queue DMA address, software descriptor array, free list, queue index, pending count, lock, MSI irq, and tasklet.
- `struct mv_xor_v2_sw_desc` wraps `dma_async_tx_descriptor` and a prepared hardware descriptor.
- `mv_xor_v2_prep_dma_memcpy()`, `mv_xor_v2_prep_dma_xor()`, and `mv_xor_v2_prep_dma_interrupt()` build software descriptors for dmaengine clients.
- `mv_xor_v2_tx_submit()` assigns cookies and copies the prepared descriptor into the coherent hardware descriptor ring.
- `mv_xor_v2_issue_pending()` notifies hardware how many descriptors were submitted since the last issue.
- `mv_xor_v2_interrupt_handler()` reads completion count and schedules `mv_xor_v2_tasklet()`, which completes cookies, invokes callbacks, runs dependencies, and returns descriptors to the free list.
- `mv_xor_v2_probe()` maps DMA/global register resources, enables clocks, allocates MSI, allocates coherent descriptor queue memory, initializes dmaengine callbacks, and registers the DMA device.

## Control Flow
Probe sets a 40-bit DMA mask, enables optional register and core clocks, allocates one MSI vector, initializes a 1024-entry coherent descriptor queue, initializes all software descriptors on `free_sw_desc`, registers one channel, configures interrupt message thresholds, and enables the descriptor queue. A client prepare call removes an acknowledged descriptor from the free list and fills the in-memory hardware descriptor. `tx_submit` assigns the cookie, copies the descriptor to `hw_desq_virt[hw_queue_idx]`, increments `npendings`, and wraps the ring index. `issue_pending` writes `npendings` to `DESQ_ADD`, then resets it to zero. Completion IRQs report pending completed descriptors; the tasklet reads the completion pointer and count, maps descriptor ids back to software descriptors, completes cookies, unmaps/invokes callbacks, returns descriptors to the free list, and deallocates completed descriptors from hardware.

## State and Persistence
All runtime state is in kernel memory and hardware registers. Persistent state is not written. Important volatile state includes `free_sw_desc`, `npendings`, `hw_queue_idx`, descriptor cookies, MSI message registers, descriptor queue base/size registers, and global bandwidth/cacheability settings. Suspend writes `DESQ_STOP`; resume restores descriptor size, interrupt thresholds, and descriptor queue configuration.

## Dependencies and Integration Points
The driver integrates with platform devices using `compatible = "marvell,xor-v2"`, the Linux dmaengine and async_tx APIs, MSI allocation through `platform_device_msi_init_and_alloc_irqs()`, clocks, coherent DMA memory, and memory-mapped IO resources. It uses `dma_cookie_*`, `dma_descriptor_unmap()`, `dmaengine_desc_get_callback_invoke()`, and `dma_run_dependencies()` for dmaengine semantics.

## Risks and Edge Cases
- The ring has a fixed 1024 descriptors and no explicit check that `npendings` plus in-flight descriptors cannot overrun hardware if clients submit faster than completions.
- Free descriptor selection depends on `async_tx_test_ack()`; unacknowledged descriptors can make prepare return `NULL` even if descriptors are physically present.
- `DESC_IOD` is set only when `DMA_PREP_INTERRUPT` is requested for memcpy/XOR; clients that depend on callbacks without this flag may not get per-request interrupt behavior.
- Address high parts are masked to 16 bits, matching the configured 40-bit mask; a future wider DMA mask would require descriptor format review.
- Error/status flags in completed hardware descriptors are not inspected, so data-movement faults may be reported as successful completions unless hardware reports them elsewhere.

## Test Signals
Useful checks are successful build under `CONFIG_MV_XOR_V2`, device-tree probe with two MMIO resources and MSI support, `dmatest` memcpy coverage, async_tx XOR/RAID-style tests with one to eight sources, suspend/resume smoke tests, and interrupt coalescing validation around `MV_XOR_V2_DONE_IMSG_THRD` and timer threshold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mxs-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mxs-dma.c

## Purpose
`mxs-dma.c` is a Freescale/NXP MXS APBH/APBX dmaengine slave and cyclic DMA controller driver for i.MX23 and i.MX28 style SoCs. It programs command-chain words (CCWs) in coherent memory and exposes channels through device tree DMA translation.

## Important APIs, Types, and Functions
- `struct mxs_dma_ccw` is the hardware command descriptor: next pointer, command bits, transfer byte count, buffer address, and optional PIO words.
- `struct mxs_dma_chan` stores one dmaengine channel, its tasklet, IRQ, coherent CCW block, status, flags for SG loop/semaphore mode, and reset state.
- `struct mxs_dma_engine` stores controller type/id, base registers, clock, `dma_device`, channel array, platform device, and number of channels.
- `mxs_dma_reset_chan()`, `mxs_dma_enable_chan()`, `mxs_dma_pause_chan()`, and `mxs_dma_resume_chan()` perform per-channel hardware control.
- `mxs_dma_prep_slave_sg()` emits linear or appended CCW chains and supports a special `DMA_TRANS_NONE` PIO-register programming mode.
- `mxs_dma_prep_dma_cyclic()` creates a circular CCW list with semaphore handling for audio-like cyclic transfers.
- `mxs_dma_int_handler()` handles completion and error interrupts, updates status, replenishes cyclic semaphores, completes cookies, and schedules callbacks.
- `mxs_dma_xlate()` maps a one-cell DT specifier to a DMA channel and records the per-channel IRQ.

## Control Flow
Probe reads `dma-channels`, selects APBH/APBX and i.MX23/i.MX28 behavior from OF match data, maps registers, gets a clock, initializes all 16 possible channel objects, resets/enables the controller block, registers dmaengine callbacks, and registers an OF DMA controller. Channel resource allocation allocates one 4-page coherent CCW block, requests the channel IRQ, enables the clock, resets the channel, and initializes a single reusable async descriptor. Prepare calls fill the CCW array and set channel status to `DMA_IN_PROGRESS`. `device_issue_pending` points hardware at the CCW block and increments the channel semaphore to start execution. IRQ handling clears completion/error bits, resets on real errors, keeps cyclic loops running by adding semaphore credits, completes cookies for non-reset complete transfers, and schedules the tasklet callback.

## State and Persistence
The driver keeps no persistent storage. Runtime state is split between the coherent CCW block, APBH/APBX channel registers, channel status, `desc_count`, flags, and cookies. Cyclic transfers maintain a circular command chain and depend on semaphore credits instead of resetting the channel. Controller initialization resets the block, enables APBH burst modes, and enables interrupts for all channels.

## Dependencies and Integration Points
The driver depends on platform resources, clocks, `stmp_reset_block()`, device tree compatibles (`fsl,imx23-dma-apbh`, `fsl,imx23-dma-apbx`, `fsl,imx28-dma-apbh`, `fsl,imx28-dma-apbx`), `linux/dma/mxs-dma.h` flag definitions, and the dmaengine slave/cyclic APIs. It registers an OF xlate function that expects one argument: channel id.

## Risks and Edge Cases
- This local source calls `dmaenginem_async_device_register(&mxs_dma->dma_device)`, which appears to be a misspelling of the normal `dma_async_device_register()` API and is a compile-time risk unless the tree carries a compatibility macro.
- The driver uses one reusable `dma_async_tx_descriptor` per channel, so overlapping independent submissions are constrained and rely on the intended MXS command-chain usage.
- `DMA_TRANS_NONE` treats `sgl` as a raw `u32 *` PIO-word source, so callers must obey the private contract exactly.
- i.MX28 APBX reset avoids READ_FLUSH for up to 50 ms; timeout only logs and proceeds with reset, which can still be risky on affected hardware.
- The cyclic residue calculation uses the last CCW address plus length minus the BAR register and is specific to the circular layout.

## Test Signals
Build coverage with the target config should catch the registration-name issue. Runtime signals include OF channel requests for valid and invalid channel ids, slave SG transfers at `MAX_XFER_BYTES` boundaries, cyclic audio-style transfers with semaphore replenishment, pause/resume behavior, termination during cyclic mode, and error IRQ paths that distinguish termination-with-completion from real bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mxs-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/nbpfaxi.c -->
# sources/distributed-fs/ceph-client/drivers/dma/nbpfaxi.c

## Purpose
`nbpfaxi.c` is a dmaengine driver for Renesas NBPFAXI64 DMA controllers. It supports memory copy and slave DMA using hardware link descriptors, per-channel completion interrupts, and a separate error interrupt.

## Important APIs, Types, and Functions
- `struct nbpf_config` identifies model-specific channel count and buffer size.
- `struct nbpf_link_reg` is the packed hardware link descriptor loaded by the DMAC.
- `struct nbpf_link_desc`, `struct nbpf_desc`, and `struct nbpf_desc_page` implement a page-sized descriptor allocator containing high-level dmaengine descriptors, software link wrappers, and DMA-mapped link registers.
- `struct nbpf_channel` contains one dmaengine channel, MMIO base, IRQ, terminal/request-line configuration, slave bus settings, descriptor lists (`free_links`, `free`, `queued`, `active`, `done`), `running`, and paused state.
- `nbpf_prep_one()` programs one hardware link for memcpy or slave direction, including bus-width, burst, request-line, link-mode, interrupt-mask, and sweep-buffer bits.
- `nbpf_prep_sg()`, `nbpf_prep_memcpy()`, and `nbpf_prep_slave_sg()` allocate descriptors and generate link chains.
- `nbpf_issue_pending()`, `nbpf_chan_irq()`, `nbpf_chan_tasklet()`, and `nbpf_err_irq()` drive queueing, normal completion, callback invocation, and error abort.
- `nbpf_of_xlate()` accepts two OF cells: terminal id and request-line flags.

## Control Flow
Probe requires a device tree node, chooses controller geometry from compatible data, maps MMIO, gets a clock, reads optional max memory burst properties, discovers one of three supported IRQ layouts, requests the error IRQ and channel IRQs, initializes channel objects, registers `DMA_MEMCPY`, `DMA_SLAVE`, and `DMA_PRIVATE`, enables the clock, configures global level interrupts, registers dmaengine, and registers the OF controller. Channel allocation initializes descriptor lists, allocates an initial descriptor page, and writes channel link-mode configuration. Prepare allocates enough link descriptors for each SG segment, fills hardware descriptors, syncs them for device access, and returns a dmaengine descriptor. Submit moves descriptors to `queued`; issue splices them to `active` and starts the first descriptor if idle. Completion IRQ acknowledges the channel, moves `running` to `done`, starts the next active descriptor, and schedules the tasklet. The tasklet completes cookies and invokes callbacks, recycling descriptors immediately if acknowledged or marking them `user_wait` until acked. Error IRQs clear hardware errors, idle the affected channel, and abort queued/active/done descriptors without callbacks.

## State and Persistence
No persistent storage is used. Runtime state lives in per-channel descriptor lists, DMA mappings for link descriptors, slave configuration fields, terminal/request flags, `running`, and `paused`. Hardware state includes channel control/configuration registers, link descriptor pointers, current transaction byte count, global interrupt style, and error/end status registers. Runtime PM only toggles the controller clock.

## Dependencies and Integration Points
The driver integrates with platform devices, OF matching for `renesas,nbpfaxi64dmac*` compatibles, `dt-bindings/dma/nbpfaxi.h` request flags, dmaengine memcpy/slave APIs, `of_dma_controller_register()`, clk APIs, IRQ APIs, and streaming DMA mapping for hardware descriptors. It supports platform id-table names as well as OF matches.

## Risks and Edge Cases
- `nbpf_desc_page_alloc()` uses `GFP_DMA` page allocation and maps each link register separately; mapping failures must unwind correctly, and the local unwind uses `sizeof(hwdesc)` instead of `sizeof(*hwdesc)` in the unmap-error path.
- Hardware descriptor `next` fields are cast to 32 bits, so effective descriptor addressing assumes reachable DMA addresses despite the wider system DMA API.
- Error handling intentionally drops callbacks for aborted descriptors; clients must tolerate silent completion loss after hardware errors.
- `nbpf_pause()` sets suspend and then clears enable to terminate sweep-buffer style reception, which is tailored to variable-length receive clients.
- Descriptor allocation can expand dynamically under memory pressure but prepare paths return `NULL` if new descriptor pages cannot be allocated.

## Test Signals
Good validation includes build coverage for each model table entry, OF xlate with valid/invalid two-cell specs, memcpy dmatest, slave SG with narrow and wide bus widths, optional max burst properties, shared and per-channel IRQ layouts, pause-on-receive residue behavior, descriptor recycling after delayed async ack, and forced error IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/nbpfaxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/of-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/of-dma.c

## Purpose
`of-dma.c` provides the generic device-tree helper layer for DMA controllers, routers, and slave-channel requests. It maintains a global list of registered OF DMA providers and exports common translation helpers used by controller drivers.

## Important APIs, Types, and Functions
- `of_dma_list` and `of_dma_lock` store and protect registered `struct of_dma` providers.
- `of_dma_controller_register()` allocates and registers a DMA controller node with its `of_dma_xlate` callback and private data.
- `of_dma_controller_free()` removes and frees a controller registration for a device node.
- `of_dma_router_register()` registers a DMA router as an OF DMA provider using `of_dma_router_xlate()`.
- `of_dma_request_slave_channel()` resolves a client node's `dmas` and `dma-names` entries by name and calls the provider xlate callback.
- `of_dma_simple_xlate()` maps one-cell DMA specifiers to `__dma_request_channel()` filter parameters.
- `of_dma_xlate_by_chan_id()` maps a one-cell DMA specifier directly to a channel id in a `dma_device`.

## Control Flow
Controller drivers register their OF node and translation callback. Client drivers call `of_dma_request_slave_channel(np, name)`. The helper validates inputs and the `dmas`/`dma-names` properties, rotates the starting index using a static atomic to distribute duplicate names, parses each matching phandle, locks the provider list, finds the provider by node, calls its xlate callback, unlocks, drops the parsed node reference, and returns the first channel found. If a provider is missing, it returns `-EPROBE_DEFER`; if no matching channel exists, it returns `-ENODEV`. Router translation first asks the router to allocate/modify a target specifier, resolves the target provider, requests a real channel, stores router metadata on the channel, optionally calls `device_router_config`, and frees route data on failures.

## State and Persistence
State is an in-memory global linked list of OF DMA registrations plus one static `last_index` atomic used for approximate load distribution. No persistent storage is used. Router allocations store `chan->router` and `chan->route_data` until channel release.

## Dependencies and Integration Points
The file exports GPL symbols to DMA controller drivers and clients. It depends on Open Firmware helpers (`of_parse_phandle_with_args()`, property readers, node references), dmaengine request/release APIs, router callbacks, and `struct of_dma`/`struct dma_router` definitions from `linux/of_dma.h` and dmaengine internals.

## Risks and Edge Cases
- Provider lookup matches only `device_node *` identity; stale or duplicate registrations would affect all DMA clients for that node.
- `of_dma_request_slave_channel()` treats missing providers as probe deferral, so controller registration ordering directly affects client probe behavior.
- Router translation must balance the node reference taken by route allocation; this function explicitly calls `of_node_put()` on the translated spec node.
- `of_dma_xlate_by_chan_id()` returns `dma_get_slave_channel(candidate)`, so candidate existence does not guarantee availability.
- The local code uses `kzalloc_obj(*ofdma)`, which is tree-specific or macro-dependent; without that helper macro, this is a build risk.

## Test Signals
Validation should cover controller registration/free lifetime, duplicate `dma-names` distribution, missing provider deferral, simple one-cell filter translation, channel-id xlate behavior for unavailable channels, router allocate/config/free success and failure paths, and module builds for providers that include `linux/of_dma.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/of-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/owl-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/owl-dma.c

## Purpose
`owl-dma.c` is the Actions Semi Owl SoC dmaengine driver. It uses `virt-dma` to multiplex device-tree-visible virtual channels/request lines over a smaller set of physical DMA channels and supports memcpy, slave SG, and cyclic transfers through hardware linked-list descriptors.

## Important APIs, Types, and Functions
- `struct owl_dma_lli` represents a DMA-pool-allocated hardware linked-list item.
- `struct owl_dma_txd` wraps `virt_dma_desc`, owns an LLI list, and marks cyclic transfers.
- `struct owl_dma_pchan` models a hardware physical channel and its current virtual channel.
- `struct owl_dma_vchan` wraps `virt_dma_chan`, tracks assigned physical channel, active transaction, slave config, and DRQ id.
- `struct owl_dma` stores the controller-level dmaengine device, MMIO base, clock, global lock, LLI pool, IRQ, physical/virtual channel arrays, and SoC id.
- `owl_dma_cfg_lli()` converts dmaengine direction and slave config into Owl descriptor mode/control words.
- `owl_dma_start_next_txd()`, `owl_dma_phy_alloc_and_start()`, and `owl_dma_issue_pending()` allocate physical channels and launch queued virtual descriptors.
- `owl_dma_interrupt()` clears global/channel interrupt state, completes active virtual descriptors, starts queued work, or releases physical channels.
- `owl_dma_prep_memcpy()`, `owl_dma_prep_slave_sg()`, and `owl_prep_dma_cyclic()` construct LLI chains.

## Control Flow
Probe reads `dma-channels` and `dma-requests`, selects S700/S900 descriptor layout behavior from OF match data, initializes dmaengine callbacks and channel lists, maps physical channel register windows, creates virtual channels with `vchan_init()`, creates a DMA pool for LLIs, enables the clock, registers dmaengine, and registers the OF xlate callback. OF xlate assigns a DRQ id to an arbitrary slave channel. Prepare paths allocate an `owl_dma_txd`, build one or more LLIs, and return a `virt-dma` prepared descriptor. `issue_pending` queues descriptors through `vchan_issue_pending()` and, if no physical channel is assigned, grabs a free pchan and starts the next txd. Interrupt handling clears pending bits, checks for missed channel-level status, completes the active `virt_dma_desc`, and either starts the next queued descriptor on the same pchan or terminates/releases the pchan.

## State and Persistence
The driver maintains only runtime state: virtual-channel queues from `virt-dma`, current `vchan->txd`, physical-channel ownership, slave config, DRQ assignment, LLI pool contents, and controller interrupt masks. Hardware descriptors differ between S700 and S900 in frame length/frame count/control packing. No persistent storage is used.

## Dependencies and Integration Points
Dependencies include platform/OF resources, `of_dma_controller_register()`, `virt-dma`, DMA pools, clocks, MMIO, and a single shared controller IRQ. Compatible strings include `actions,s500-dma`, `actions,s700-dma`, and `actions,s900-dma`. The driver uses `subsys_initcall()` rather than `module_platform_driver()`.

## Risks and Edge Cases
- `owl_dma_pause()` dereferences `vchan->pchan` without a null check, unlike resume, so pause before physical assignment would be unsafe.
- `owl_dma_of_xlate()` rejects `drq > od->nr_vchans`; since valid DRQs are zero-based, `drq == nr_vchans` should also be invalid and may index beyond the virtual request range semantically.
- `od->dma.directions` is set only to `BIT(DMA_MEM_TO_MEM)` even though slave SG/cyclic callbacks and capabilities are registered; this may under-advertise slave directions.
- `owl_dma_get_pchan()` returns the last pchan pointer even if all pchans are busy because the loop leaves `pchan` non-NULL; this can lead to assigning a busy physical channel.
- Busy waits on channel idle use `cpu_relax()` without timeout in `owl_dma_start_next_txd()`.

## Test Signals
Tests should include build/probe for S700 and S900 compatibles, OF DRQ boundary tests, memcpy over lengths greater than `OWL_DMA_FRAME_MAX_LENGTH`, slave SG with 1-byte and 4-byte widths, cyclic callback repetition, pchan exhaustion with more virtual requests than hardware channels, pause/resume before and during active transfers, residue reporting, and missed global-vs-channel IRQ status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/owl-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pch_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/pch_dma.c

## Purpose
`pch_dma.c` is a PCI dmaengine slave driver for Intel EG20T PCH and LAPIS/ROHM ML7213, ML7223, and ML7831 IOH DMA controllers. It manages up to 12 hardware channels using DMA-pool descriptors and supports private slave SG transfers.

## Important APIs, Types, and Functions
- `struct pch_dma_desc_regs` mirrors per-descriptor hardware fields: device address, memory address, size/width, and next pointer/control.
- `struct pch_dma_desc` wraps descriptor registers, `dma_async_tx_descriptor`, and list nodes for chained descriptors.
- `struct pch_dma_chan` stores one channel's MMIO descriptor window, direction, tasklet, error bit, lock, active/queued/free lists, and allocation count.
- `struct pch_dma` contains the dmaengine device, PCI MMIO base, descriptor pool, saved registers, and channel array.
- `pdc_set_dir()`, `pdc_set_mode()`, `pdc_dostart()`, and `pdc_advance_work()` program channel control and dispatch queued descriptors.
- `pd_prep_slave_sg()` builds one-shot or scatter-gather chains from a `struct pch_dma_slave` supplied through `chan->private`.
- `pd_irq()` reads/clears status registers and schedules per-channel tasklets.
- `pch_dma_probe()` owns PCI enablement, BAR mapping, IRQ request, descriptor pool creation, channel initialization, and dmaengine registration.

## Control Flow
PCI probe allocates controller state, enables the PCI device, requests regions, sets a 32-bit DMA mask, maps BAR 1, requests the shared IRQ, creates a descriptor DMA pool, initializes channel lists/tasklets, registers private slave dmaengine capabilities, and returns. Channel allocation checks the hardware channel is idle, preallocates `init_nr_desc_per_channel` descriptors, initializes cookies, and enables channel IRQ. `pd_prep_slave_sg()` chooses the peripheral register from `pch_dma_slave`, sets channel direction, obtains descriptors, fills hardware size/width/next fields, chains descriptors through physical addresses, and returns the first descriptor. Submission immediately starts the descriptor if no active work exists, otherwise queues it. IRQ status schedules the tasklet; the tasklet handles errors or advances/completes work, invoking callbacks and returning descriptors to the free list.

## State and Persistence
Runtime state is held in active/queued/free descriptor lists, DMA-pool allocations, channel direction, error bit, saved suspend registers, and hardware control/status registers. Suspend saves controller and channel registers; resume restores them. No disk persistence exists.

## Dependencies and Integration Points
The driver integrates with PCI IDs for Intel and ROHM devices, `linux/pch_dma.h` slave metadata, dmaengine private slave APIs, PCI BAR/IRQ management, DMA pools, and simple PM ops. Clients are expected to provide `struct pch_dma_slave` through the channel private pointer.

## Risks and Edge Cases
- `pd_tx_submit()` returns `0` and does not call `dma_cookie_assign()`, which breaks normal dmaengine cookie semantics unless this tree intentionally bypasses cookies for this legacy private driver.
- The control-register mask logic in `pdc_set_dir()`/`pdc_set_mode()` is delicate and appears to use masks in a way that can preserve or clear unintended channel bits.
- Error handling logs a bad descriptor but still calls the normal callback path rather than a result-aware error callback.
- `pd_device_terminate_all()` invokes callbacks while holding the channel lock through `pdc_chain_complete()`, which may be risky if callbacks call back into dmaengine.
- Descriptor size limits are strict and width-dependent; oversized SG entries fail at prepare time after some descriptors may have been allocated and must be returned correctly.

## Test Signals
Validation should include compilation for PCI PCH/ROHM configs, probe for each channel-count PCI id, slave SG with each supported width and boundary sizes, cookie tracking tests, shared IRQ status for channels above and below 8, terminate-all during active and queued transfers, suspend/resume register restoration, and descriptor pool exhaustion/reuse behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pch_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pl330.c -->
# sources/distributed-fs/ceph-client/drivers/dma/pl330.c

## Purpose
`pl330.c` is the ARM PrimeCell PL330 DMAC dmaengine driver. It contains both a low-level PL330 microcode generator/executor and a dmaengine-facing provider for memcpy, slave SG, and cyclic DMA using AMBA devices and optional OF DMA registration.

## Important APIs, Types, and Functions
- `struct pl330_config` captures hardware configuration read from PL330 registers: bus width/depth, channel count, peripheral count, event count, security mode, and non-secure masks.
- `struct pl330_reqcfg`, `struct pl330_xfer`, and `struct dma_pl330_desc` describe one dmaengine transfer and the request configuration used to generate PL330 microcode.
- `struct pl330_thread` models a PL330 channel or manager thread, with two request slots, assigned event, and running index.
- `struct dma_pl330_chan` is the dmaengine channel wrapper with submitted/work/completed lists, channel lock, assigned PL330 thread, FIFO mapping, cyclic flag, and runtime-PM active state.
- `struct pl330_dmac` stores the dmaengine device, descriptor pool, microcode buffers, MMIO base, hardware config, event map, channel threads, manager thread, fault tasklet, reset state, peripheral channel array, quirks, and reset controls.
- `_emit_*()` helpers generate PL330 instructions such as `DMAMOV`, `DMALD`, `DMAST`, `DMAWFP`, `DMASEV`, `DMAEND`, and `DMAKILL`.
- `_setup_req()`, `_setup_xfer()`, `_setup_loops()`, `_loop()`, `_bursts()`, and `_dregs()` compile transfer requests into bounded per-channel microcode buffers.
- `pl330_submit_req()`, `pl330_start_thread()`, `_trigger()`, `_stop()`, `pl330_update()`, and `pl330_dotask()` submit microcode, start/stop threads, process events, and recover faults.
- `pl330_prep_dma_memcpy()`, `pl330_prep_slave_sg()`, `pl330_prep_dma_cyclic()`, `pl330_tx_submit()`, `pl330_issue_pending()`, and `pl330_tx_status()` implement the dmaengine API.

## Control Flow
AMBA probe sets a 32-bit DMA mask, maps registers, deasserts optional resets, requests AMBA IRQs, validates the peripheral id, reads hardware configuration, allocates privileged coherent microcode buffers sized per hardware channel, creates PL330 channel/manager thread objects, initializes a descriptor pool, creates dmaengine channels, registers capabilities, optionally registers OF xlate, configures runtime PM, and reports hardware geometry. A prepare call obtains one or more descriptors from the DMAC pool, fills transfer addresses/lengths, burst settings, increment flags, request type, and bytes requested. `tx_submit()` assigns cookies to all descriptors in a chain and moves them to the submitted list. `issue_pending()` moves submitted descriptors to the work list, gets runtime PM, and directly runs the channel tasklet. The tasklet completes DONE descriptors, calls `fill_queue()` to compile and enqueue up to two PL330 requests into the hardware thread slots, starts the thread, and invokes callbacks for completed descriptors. IRQ handling calls `pl330_update()`, which checks manager/channel faults, clears event interrupts, detaches completed request slots, restarts threads, and schedules callbacks or reset work. Fault tasklet stops affected threads, reports abort/fail completions internally, clears request slots, and resets state.

## State and Persistence
All state is volatile. Key state includes descriptor-pool membership, submitted/work/completed lists, descriptor status (`FREE`, `PREP`, `BUSY`, `PAUSED`, `DONE`), per-thread request slots, event-to-channel mapping, microcode buffers, FIFO DMA mappings, reset flags, and runtime PM active accounting. Hardware state includes PL330 channel states, SAR/DAR/CCR, event status, interrupt enable/clear, fault status, and debug instruction registers. Suspend/resume delegates clock/runtime-PM handling through AMBA bus PM.

## Dependencies and Integration Points
The driver depends on AMBA/PrimeCell matching, dmaengine APIs, OF DMA helpers, scatterlist, runtime PM, reset controls, debugfs, coherent DMA allocation with `DMA_ATTR_PRIVILEGED`, and optional OF quirks `arm,pl330-broken-no-flushp` and `arm,pl330-periph-burst`. OF xlate maps one cell to a peripheral channel. Debugfs can expose physical-thread to channel mapping.

## Risks and Edge Cases
- The driver relies on bounded generated microcode; requests that exceed half of `mcbufsz` fail with `-ENOMEM`, so very large or poorly aligned transfers depend on segment limits and platform buffer sizing.
- Pause is not resumable by design; paused descriptors must be terminated and recreated.
- Runtime PM accounting is subtle: `issue_pending()`, tasklet completion, terminate, and free-resource paths must balance autosuspend references.
- Fault recovery calls callbacks via internal status transitions but dmaengine client-visible error reporting is limited.
- FIFO mapping uses `dma_map_resource()` and must be remapped when direction/config changes; stale direction state would corrupt peripheral transfers.
- Security mode and non-secure channel/event masks can prevent channel allocation or cause aborts when secure/non-secure assumptions mismatch.

## Test Signals
Important coverage includes AMBA probe/remove with reset controls, OF xlate for valid/invalid peripheral ids, memcpy dmatest across alignments and large segment sizes, slave SG in both directions, cyclic period callback behavior, residue reporting during running and paused transfers, fault injection for channel/manager faults, runtime PM autosuspend balance, debugfs output, and builds with/without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pl330.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/plx_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/plx_dma.c

## Purpose
`plx_dma.c` is a dmaengine memcpy provider for PLX/Microsemi ExpressLane PEX PCIe switch DMA hardware. It exposes one DMA channel backed by a coherent off-chip descriptor ring.

## Important APIs, Types, and Functions
- `struct plx_dma_hw_std_desc` is the hardware descriptor containing size/flags and 48-bit source/destination addresses split into low/high fields.
- `struct plx_dma_desc` wraps one dmaengine descriptor, points at its hardware ring entry, and stores original transfer size for residue/result calculation.
- `struct plx_dma_dev` owns the dmaengine device/channel, RCU-protected PCI device pointer, BAR mapping, completion tasklet, ring lock, active flag, head/tail indices, coherent hardware ring, and software descriptor ring.
- `plx_dma_prep_memcpy()` reserves a ring slot under lock, fills hardware address/size fields, and returns with the ring lock held for `tx_submit()`.
- `plx_dma_tx_submit()` assigns a cookie, uses a write barrier, sets the hardware valid bit, and releases the lock.
- `plx_dma_issue_pending()` starts the hardware ring after a barrier.
- `plx_dma_process_desc()` consumes completed write-back descriptors, computes residue/result, completes cookies, unmaps, and invokes result callbacks.
- `plx_dma_stop()`/`__plx_dma_stop()` gracefully pause and clear ring registers; `plx_dma_abort_desc()` reports queued work as aborted.

## Control Flow
PCI probe enables the device, negotiates 48-bit then 32-bit DMA mask, maps BAR 0, allocates an IRQ vector, sets bus mastering, and creates/registers the dmaengine device. Channel resource allocation allocates the coherent 2048-entry hardware ring, allocates matching software descriptors, programs ring base/count/prefetch registers, resets control, and marks the ring active. Prepare reserves a circular-buffer slot if the ring is active, space exists, and length fits the descriptor size mask. Submit sets the valid bit after descriptor writes are visible. Issue writes the start control value. Interrupt handling checks descriptor-done status and schedules a tasklet, which drains completed descriptors until the tail reaches a still-valid entry. Free/remove paths mark the ring inactive, stop hardware, synchronize IRQ/tasklet, abort remaining descriptors, and free rings.

## State and Persistence
The driver has only volatile ring state: `head`, `tail`, `ring_active`, hardware descriptor write-back flags, software descriptors, and an RCU PCI pointer used to prevent MMIO after removal. No persistent storage exists. Hardware state is the descriptor ring base/count/next registers, control registers, prefetch limit, and interrupt status/control.

## Dependencies and Integration Points
The driver integrates with PCI matching for vendor PLX device `0x87D0` with system-other class, dmaengine memcpy APIs, coherent DMA allocation, PCI IRQ vectors, RCU for removal synchronization, tasklets, and result-aware dmaengine callbacks. It uses `DMAENGINE_ALIGN_1_BYTE`.

## Risks and Edge Cases
- `plx_dma_prep_memcpy()` intentionally returns with `ring_lock` held and relies on `tx_submit()` to release it; any dmaengine API misuse that drops the descriptor without submitting would deadlock later users.
- Ring size is a power-of-two 2048 entries, and `CIRC_SPACE()` protects against full-ring overwrite, but no dynamic expansion exists.
- Completion depends on hardware clearing `PLX_DESC_FLAG_VALID` and writing result bits; malformed write-back can misclassify failures.
- Remove/free paths mix tasklet killing, IRQ synchronization, RCU pointer clearing, and abort completion; ordering is critical to avoid MMIO after device removal.
- Length is limited by `PLX_DESC_SIZE_MASK`, and addresses rely on the negotiated DMA mask fitting descriptor high fields.

## Test Signals
Test with PCI probe/remove, DMA mask fallback, dmatest memcpy with 1-byte alignment and max-size boundaries, ring-full prepare failures, interrupt-driven completion, read/write failure write-back bits, resource-free aborts, and hot-remove/unregister races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/plx_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/Makefile

## Purpose
This Makefile connects the PPC4xx DMA subdirectory to Kbuild. It builds the `adma.o` object when `CONFIG_AMCC_PPC440SPE_ADMA` is enabled.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_AMCC_PPC440SPE_ADMA) += adma.o` is the only build rule and expresses a direct config-to-object dependency.
- The SPDX header declares GPL-2.0-only licensing for the build metadata.

## Control Flow
There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_AMCC_PPC440SPE_ADMA`; when it is `y` or `m`, `adma.o` is included in the directory's built-in or module object list according to standard Kbuild semantics.

## State and Persistence
No runtime state exists. The only persistent behavior is build graph selection derived from kernel configuration.

## Dependencies and Integration Points
The file depends on the surrounding Linux Kbuild system and on a sibling `adma.c`/`adma.o` implementation in the same `ppc4xx` directory. It integrates with the architecture/platform DMA configuration symbol `CONFIG_AMCC_PPC440SPE_ADMA`.

## Risks and Edge Cases
- If `CONFIG_AMCC_PPC440SPE_ADMA` is selectable but `adma.c` or its dependencies are missing, the build will fail.
- No additional objects are listed, so any helper source introduced for PPC4xx ADMA would need this Makefile updated.
- The file does not declare module-specific flags or composite objects; all complexity is expected to live in `adma.o`.

## Test Signals
Build testing should cover `CONFIG_AMCC_PPC440SPE_ADMA=y`, `m`, and unset where applicable, and confirm the resulting object is included or omitted as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/Makefile -->
