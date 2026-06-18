# subset-b-003928 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pcie.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pcie.c

## Purpose
`pcie.c` contains the HFI1 driver's PCIe bring-up, BAR mapping, PCI configuration preservation, PCIe capability tuning, AER recovery hooks, and ASIC-specific PCIe link speed transition logic. It is the low-level bridge between Linux PCI core state and the device CSR/MMIO layout used by the rest of the HFI1 driver.

## Important APIs, Types, And Functions
`hfi1_pcie_init()` enables the PCI function, requests BAR regions, sets a coherent DMA mask, and marks the endpoint bus-master capable. `hfi1_pcie_ddinit()` maps BAR0 into uncached CSR windows, a write-combining PIO send-buffer aperture, and a write-combining receive-array aperture, then sets `HFI1_PRESENT`. `hfi1_pcie_ddcleanup()` tears those mappings down. `pcie_speeds()` and `update_lbus_info()` derive link speed/width and Gen3 capability. `save_pci_variables()` and `restore_pci_variables()` preserve command, BAR, ROM, DevCtl/LnkCtl/DevCtl2, MSI-X, and optional TPH config across secondary-bus resets. `tune_pcie_caps()` optionally raises MPS/MRRS and enables extended tags. `hfi1_pci_err_handler` wires Linux PCI error recovery to `hfi1_disable_after_error()` and `hfi1_init()`. `do_pcie_gen3_transition()` performs the long firmware-download, SerDes EQ, SBus, gasket, SBR, config-restore, retry, and link-validation sequence.

## Control Flow
Probe first calls the generic PCI setup, then maps device memory once `hfi1_devdata` exists. BAR0 is split because PIO buffers occupy the tail of the chip address space and need WC mapping while CSR regions stay uncached. Gen3 transition is conditional on ASIC silicon, requested module parameters, current speed, upstream bridge access, and Gen3 capability. It acquires the SBus resource, disables thermal polling, loads PCIe firmware, programs port-logic registers and EQ tables, arms gasket logic, forces a secondary bus reset through the parent bridge, restores PCI config, verifies gasket status and per-lane errors, updates cached link info, and retries if speed or width missed the target. AER callbacks request reset for frozen channels, disconnect on permanent failure, and reinitialize asynchronously on resume.

## State And Persistence
PCI state is cached in `dd` fields so device resets can be survived without relying on the PCI core retaining live hardware config. MMIO base pointers and physical address fields persist for the driver's lifetime until cleanup. Link metadata is cached in `lbus_width`, `lbus_speed`, `lbus_info`, and `link_gen3_capable`. Module parameters (`pcie_caps`, `pcie_target`, `pcie_force`, `pcie_retry`, `pcie_pset`, `pcie_ctle`) alter capability tuning and transition behavior only at runtime; no nonvolatile state is written.

## Dependencies And Integration Points
The file depends on Linux PCI/PCIe config helpers, DMA mask APIs, IO mapping APIs, AER recovery infrastructure, HFI1 CSR accessors, generated chip register definitions, ASPM control, SBus firmware loading, chip-resource locking, link bounce/reinit paths, and module parameters. Its mapped `piobase` and CSR windows are consumed by PIO, receive, interrupt, and firmware-management code throughout the driver.

## Risks
The Gen3 transition performs reset-sensitive operations while hoping the kernel and other devices do not access the endpoint during SBR. Error exits inside the SBus critical section must release resources and restore thermal polling; early returns after firmware/config failures are especially important to audit. `tune_pcie_caps()` trusts module-param bit fields and may alter upstream bridge settings. BAR size assumptions are strict. Mapping failures clean up partially initialized state, but later users depend on `HFI1_PRESENT` accurately tracking valid CSR access.

## Test Signals
Useful signals include probe failure at each PCI setup stage, 32-bit DMA fallback, BAR length mismatch, MMIO read-all-ones detection, save/restore PCI config across simulated reset, Gen1/Gen2/Gen3 module-param combinations, invalid `pcie_pset`, firmware download failure, SBR failure, gasket error/status variants, AER frozen/permanent paths, and link-width retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pin_system.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pin_system.c

## Purpose
`pin_system.c` implements system-memory page pinning for HFI1 user SDMA. It caches pinned user virtual-address ranges in the driver's MMU red-black tree so SDMA descriptors can safely reference user pages while also reacting to mmu-notifier invalidation and pin-limit pressure.

## Important APIs, Types, And Functions
`struct sdma_mmu_node` extends `mmu_rb_node` with the owning user SDMA packet queue, an array of pinned `struct page *`, and a page count. `hfi1_init_system_pinning()` registers queue-specific `mmu_rb_ops`; `hfi1_free_system_pinning()` unregisters them. `pin_system_pages()` enforces pin limits through `hfi1_can_pin_pages()`, evicts cached nodes when needed, calls `hfi1_acquire_user_pages()`, and increments `pq->n_locked`. `get_system_cache_entry()` finds, prepends, or creates cache nodes for a request range. `add_mapping_to_sdma_packet()` converts cached pages into SDMA descriptors with node get/put callbacks. `hfi1_add_pages_to_sdma_packet()` is the exported packet-building entry point.

## Control Flow
For each user iovec segment, the code aligns the requested range to page boundaries and searches the mmu-rb cache. If an existing node covers the start, it is returned with an extra safety kref. If the first matching node begins after the requested start, a new prepended node is pinned and inserted. If no node exists, the entire aligned range is pinned and inserted. Packet construction then walks page by page, computing page offsets and byte counts, and attaches the last descriptor for each cache-entry span to the node context so descriptor completion releases the kref. The top-level loop advances `req->iov_idx`, iovec offsets, and remaining packet bytes.

## State And Persistence
Pinned ranges live in per-queue mmu-rb nodes until evicted, invalidated, or queue teardown. `pq->n_locked` tracks the number of pages locked by the queue. Each cache node has a tree reference plus transient safety and descriptor references. There is no disk or firmware persistence; state is tied to the process `mm_struct`, the user SDMA queue, and outstanding descriptors.

## Dependencies And Integration Points
The implementation depends on `mmu_rb`, HFI1 user-page acquire/release helpers, queue pin accounting, user SDMA request/iovec/txreq structures, `sdma_txadd_page()`, krefs, mmu notifier release paths, and trace/debug macros. It is the bridge between user SDMA packet assembly and Linux memory-management invalidation.

## Risks
The code has subtle kref lifetime rules: successful cache lookup and insertion deliberately take a safety reference that must be released after descriptor assignment. A mismatch would leak pinned pages or free nodes still referenced by descriptors. `pin_system_pages()` passes `node->npages` as the start offset when unpinning a partial pin failure, but `node->npages` is still zero for new nodes, which appears intentional but deserves regression coverage. Concurrent insertion races are handled by retrying `-EEXIST`; invalidation during descriptor construction is protected by references but should be stress tested.

## Test Signals
Exercise empty ranges, unaligned iovecs spanning many pages, cache hits, prepended cache nodes, concurrent insertion races, pin-limit eviction, partial pin failures, mmu invalidation while descriptors are being built, descriptor callback release, queue teardown with live nodes, and accounting of `n_locked` after success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pin_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pinning.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pinning.h

## Purpose
`pinning.h` is the small public header for the HFI1 system-memory pinning layer. It exposes the queue lifecycle hooks and packet-population helper used by user SDMA code without leaking the private mmu-rb cache node layout.

## Important APIs, Types, And Functions
The header forward-declares `hfi1_user_sdma_pkt_q`, `user_sdma_request`, `user_sdma_txreq`, and `user_sdma_iovec`. `hfi1_init_system_pinning()` installs per-queue MMU invalidation support, `hfi1_free_system_pinning()` removes it, and `hfi1_add_pages_to_sdma_packet()` pins/maps bytes from user iovecs into an SDMA tx request while updating request progress.

## Control Flow
Callers initialize pinning when a user SDMA packet queue is created, call `hfi1_add_pages_to_sdma_packet()` while building each packet from user iovecs, and free pinning during queue teardown. The header intentionally keeps all cache, kref, and eviction details private to `pin_system.c`.

## State And Persistence
No state is defined in the header. State lives in the queue's hidden handler and private cache nodes created by the implementation. The API implies lifecycle ordering: packet additions are valid only after init and before free.

## Dependencies And Integration Points
This header integrates user SDMA request building with the system pinning implementation and is included by code that needs to submit user-backed pages to SDMA. It depends on `u32` being visible from prior includes or kernel type headers.

## Risks
Because the header only forward declares types, misuse is mostly lifecycle-related: calling the packet helper without a registered handler or after teardown would fail in implementation paths. The `u32 *pkt_data_remaining` output contract must remain synchronized with user SDMA callers.

## Test Signals
Compile coverage should catch prototype drift. Runtime tests should verify queue init/free ordering, packet helper error propagation, and correct progress updates across partial iovec consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pinning.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.c

## Purpose
`pio.c` manages HFI1 Programmed I/O send contexts: memory-pool sizing, hardware/software context allocation, PIO context initialization, enable/disable/restart, credit return, buffer allocation/release, VL-to-context mapping, freeze/link recovery, and diagnostic dumping.

## Important APIs, Types, And Functions
The file centers on `struct send_context` and `struct send_context_info` from `pio.h`. `pio_send_control()` updates global send-control bits and VL arbitration. `init_sc_pools_and_sizes()` computes per-type context counts and credit sizes for kernel, ACK, user, and VL15 contexts. `init_send_contexts()` creates software context tables and hardware-to-software mappings. `sc_alloc()` programs send-context CSRs, credit-return DMA address, partition/opcode/VL checks, thresholds, and shadow rings. `sc_enable()`, `sc_disable()`, `sc_restart()`, `sc_stop()`, `pio_freeze()`, `pio_kernel_unfreeze()`, and `pio_kernel_linkup()` implement lifecycle and recovery. `sc_buffer_alloc()` reserves PIO blocks and `sc_release_update()` reclaims them from hardware credit returns. `pio_map_init()` publishes an RCU-protected VL map used by `pio_select_send_context_vl()` and `pio_select_send_context_sc()`.

## Control Flow
Initialization allocates coherent credit-return memory per NUMA node, builds context records, allocates per-VL kernel contexts plus VL15, initializes hardware contexts, enables them, writes VL checks, and publishes a VL map. Sending code selects a send context by QP selector and VL/SC, allocates blocks from the shadow ring under `alloc_lock`, writes PIO data through copy helpers, and later updates release state from hardware credit counters. On credit-return interrupts, group release updates reclaim completed buffers and wake queued QPs. On halt/freeze, allocation is stopped first, outstanding buffers and waiters are flushed, contexts are disabled, and eligible kernel contexts are re-enabled after restart/unfreeze/link-up.

## State And Persistence
State is volatile hardware/software runtime state: context tables, `hw_to_sw`, coherent credit-return pages, per-context fill/free counters, shadow-ring head/tail, per-CPU outstanding buffer counters, wait lists, thresholds, and RCU VL maps. Context CSR configuration mirrors software state but is reset by context init, disable, or chip reset. No nonvolatile persistence exists.

## Dependencies And Integration Points
The file integrates with generated send-context CSRs, DMA coherent allocation, QP/iowait wakeups, SDMA capability flags, VL/SC mapping helpers, node affinity, link workqueues, tracepoints, and kernel RCU/spinlock/seqlock primitives. `qp.c` and verbs send paths consume the context-selection and wait/wakeup APIs; `pio_copy.c` consumes allocated `pio_buf` metadata.

## Risks
Correctness depends on memory ordering between allocator head publication and release-side reads, plus accurate hardware credit counters. Interrupt enable/disable is refcounted and callers must pair calls. `sc_disable()` flushes callbacks while holding release state and wakes QPs after detaching wait-list entries; missed lock pairing can strand waiters. `pio_map_init()` must handle non-power-of-two VL/context counts and partial allocation failures. Timeouts in egress wait bounce the link, so false positives are disruptive.

## Test Signals
Test pool sizing with SDMA on/off, exhausted context counts, coherent allocation failures, context enable init errors, buffer allocation under no-credit/link-down states, credit return callback codes, interrupt refcount pairing, PIO wait-list wake ordering, freeze/unfreeze/linkdown paths, RCU map replacement, per-VL threshold changes, and debug seqfile output on live contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.h

## Purpose
`pio.h` defines the public structures, constants, and function contracts for HFI1 PIO send-context management and PIO memory copy support.

## Important APIs, Types, And Functions
The header defines send-context type IDs (`SC_KERNEL`, `SC_VL15`, `SC_ACK`, `SC_USER`), PIO release reason bits, `union mix`, `struct pio_buf`, `union pio_shadow_ring`, `struct send_context`, `struct send_context_info`, credit-return DMA structures, context sizing structures, and the RCU VL map types `pio_map_elem` and `pio_vl_map`. It declares lifecycle APIs such as `init_sc_pools_and_sizes()`, `init_send_contexts()`, `sc_alloc()`, `sc_enable()`, `sc_disable()`, `sc_restart()`, `sc_buffer_alloc()`, `sc_release_update()`, `pio_map_init()`, and the segmented/non-segmented copy routines.

## Control Flow
The declarations describe the normal PIO path: initialize credit-return and send contexts, allocate/enable contexts, publish VL mappings, select a context, allocate a `pio_buf`, copy packet bytes, and release/wake based on credit returns. The struct layout separates read-mostly initialization fields, allocation fields, release fields, wait-list state, and credit-control state into cacheline-conscious groups.

## State And Persistence
`struct send_context` is the main in-memory persistent runtime state for a hardware context. It retains CSR identity, PIO base address, credit counters, shadow-ring state, per-CPU outstanding allocation counters, interrupt enable counts, wait queue/list state, and halt work until freed. `struct pio_buf` tracks one allocated PIO buffer and carries partial bytes for segmented copies.

## Dependencies And Integration Points
The header ties together HFI1 device data, QP waiters, DMA credit-return memory, Linux RCU/list/waitqueue/workqueue primitives, PIO copy code, and diagnostic seqfile dumping. It is included by send paths, QP code, user context code, and low-level PIO implementation.

## Risks
Several fields are intentionally touched from different locks or interrupt contexts, so changing struct layout or semantics can introduce cacheline contention or races. `pio_release_cb` codes are bit flags and callback users must tolerate combined reasons. `SC_USER` being the last type is a configuration assumption. The RCU map uses flexible arrays and rounded power-of-two masks, which requires allocation and bounds discipline.

## Test Signals
Compile tests should catch prototype drift. Runtime coverage should validate context selection, callback reason handling, segmented-copy state in `pio_buf`, credit interrupt refcounting, and RCU map replacement/freeing with concurrent readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio_copy.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio_copy.c

## Purpose
`pio_copy.c` contains the low-level routines that write packet data into HFI1 PIO MMIO send-buffer space. It handles SOP versus non-SOP address spaces, block-aligned hardware write requirements, circular context wraparound, dangling bytes, and segmented packet construction.

## Important APIs, Types, And Functions
`pio_copy()` copies a complete aligned packet body after writing the PBC, using QWORD writes and padding the final PIO block. `seg_pio_copy_start()`, `seg_pio_copy_mid()`, and `seg_pio_copy_end()` support packet construction from multiple source fragments. Helpers such as `jcopy()`, `read_low_bytes()`, `read_extra_bytes()`, `merge_write8()`, `mid_copy_mix()`, and `mid_copy_straight()` maintain `pbuf->carry`, `carry_bytes`, and `qw_written` when source fragments are not naturally QWORD aligned.

## Control Flow
The complete-copy path writes the PBC to SOP space, writes QWORD data until the first block ends, switches into non-SOP space, wraps at `pbuf->end` if needed, writes remaining QWORD data, writes a dangling DWORD if present, pads to the next PIO block boundary, and decrements the per-CPU outstanding buffer count. The segmented path writes the PBC and initial aligned data, stores trailing bytes in `carry`, repeatedly merges or writes middle fragments while respecting SOP space and wraparound, then flushes any final carry and pads the block in `seg_pio_copy_end()`.

## State And Persistence
The routines mutate only the supplied `pio_buf`: `qw_written`, `carry`, `carry_bytes`, and implicit outstanding-buffer accounting in the owning send context. The hardware-visible state is the MMIO PIO buffer contents. The functions assume `preempt_disable()` was performed during buffer allocation and finish by decrementing `buffers_allocated` and enabling preemption.

## Dependencies And Integration Points
The code depends on `struct pio_buf` from `pio.h`, `writeq()` MMIO semantics, the HFI1 PIO address layout where SOP space is offset by half the PIO aperture, and send-context size/end metadata. It is called by verbs/PIO send paths after `sc_buffer_alloc()` succeeds.

## Risks
The functions rely on strict alignment and size contracts: `pio_copy()` expects an 8-byte-aligned source and a DWORD count, while segmented helpers tolerate misaligned middle fragments through carry handling. Incorrect `qw_written` or carry accounting would corrupt packet boundaries. Pointer arithmetic on `void *` is a kernel extension. The final preemption enable assumes each buffer allocation has disabled preemption exactly once.

## Test Signals
Test single-block packets, multi-block packets, exact SOP block endings, context wraparound, odd DWORD counts, segmented fragments smaller than 8 bytes, misaligned middle fragments, carry flush at end, padding behavior, and outstanding buffer counter balance under all copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.c

## Purpose
`platform.c` loads platform configuration data, derives port/cable policy, qualifies QSFP modules, and applies link SerDes/QSFP tuning before HFI1 link negotiation. It combines BIOS scratch data, EPROM or firmware platform tables, QSFP memory, and 8051 firmware configuration commands.

## Important APIs, Types, And Functions
`get_platform_config()` obtains config from integrated-platform scratch registers, EPROM, or fallback firmware `hfi1_platform.dat`; `free_platform_config()` releases copied data; `get_port_type()` reads the configured port type. `set_qsfp_tx()` controls QSFP transmitter disable bits. `qual_power()` and `qual_bitrate()` enforce power-class and speed policies. `set_qsfp_high_power()`, `apply_cdr_settings()`, `apply_eq_settings()`, and `apply_rx_amplitude_settings()` program active QSFP modules. `apply_tunings()` sends tuning method, channel loss, external device capability, and TX EQ settings to the 8051. `tune_serdes()` is the top-level link-readiness workflow.

## Control Flow
Integrated systems first validate an ASIC scratch checksum and save prepacked fields; discrete systems try EPROM, then fallback firmware. During link setup, `tune_serdes()` clears link-ready state, handles loopback/simulator bypass, switches on `port_type`, verifies QSFP presence where required, locks the QSFP I2C resource, refreshes cache, tunes active or passive modules, refreshes cache after modifications, releases the resource, applies 8051 tunings if no offline-disabled reason was set, and finally marks `driver_link_ready`.

## State And Persistence
Platform data is kept in `dd->platform_config` or, for integrated scratch configs, decoded into `ppd` fields with `config_from_scratch`. Runtime port state includes `port_type`, attenuation values, preset bitmaps, max power class, QSFP cache flags, `offline_disabled_reason`, `link_enabled`, and `driver_link_ready`. QSFP module memory may be modified for power, CDR, EQ, TX disable, and amplitude settings; these changes are module runtime state and are reset via QSFP reset or cable removal.

## Dependencies And Integration Points
The file depends on EPROM access, firmware loading, platform-table parsing (`get_platform_config_field()`), QSFP read/write/cache helpers, chip resource locking, 8051 host-command config, OPA link speed/width policy constants, loopback/simulator flags, and port link startup code that consumes `driver_link_ready`.

## Risks
Many `get_platform_config_field()` calls in tuning paths log or continue with zero-initialized defaults, so malformed tables can silently lead to suboptimal or wrong tuning. Active QSFP programming changes module memory and relies on `reset_needed` to avoid stale settings across retunes. Power and bitrate failures communicate through `offline_disabled_reason`; ordering matters when multiple policies could apply. Several QSFP writes ignore return values, especially for CDR/EQ helpers.

## Test Signals
Test scratch checksum valid/invalid, EPROM success/failure, fallback firmware absence, each port type, QSFP absent/present/cache invalid, active/passive/unknown module technologies, power-class limits, bitrate rejection, high-power enable classes, CDR/EQ/amplitude support matrices, 8051 command failures, loopback bypass, and final `driver_link_ready`/offline reason transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.h

## Purpose
`platform.h` defines the HFI1 platform configuration table schema, field IDs, packed scratch-register bit layouts, link/cable tuning encodings, masks, and public platform/tuning APIs used by `platform.c` and related link code.

## Important APIs, Types, And Functions
The header enumerates platform table types (system, port, RX preset, TX preset, QSFP attenuation, variable settings) and per-table field IDs. `struct platform_config` stores a raw binary image; `struct platform_config_data` and `struct platform_config_cache` provide parsed table/metadata references. It defines encodings for QSFP power classes, port types, link speed/width support, VL capability, MTU capability, timeout values, and tuning method. It declares `get_platform_config()`, `free_platform_config()`, `get_port_type()`, `set_qsfp_tx()`, and `tune_serdes()`.

## Control Flow
The constants describe how platform-table records and metadata are decoded and how integrated-platform scratch registers pack port type, attenuation, QSFP power, TX presets, RX presets, bitmap version, and checksum. Consumers read fields by table/record/field ID and translate them into link policy and tuning commands.

## State And Persistence
The header does not own state, but it defines the in-memory representations for raw and parsed platform config plus the persistent meaning of BIOS/EPROM/firmware table data. Scratch-register fields act as firmware-provided boot-time platform state for integrated systems.

## Dependencies And Integration Points
It integrates platform parsing with HFI1 device/port data, QSFP policy, 8051 tuning, OPA link capabilities, and firmware/EPROM data sources. The bit masks must match hardware scratch-register and platform binary format definitions.

## Risks
Field IDs and masks are ABI-like contracts with platform firmware and table generators; drift will cause wrong tuning without compiler errors. Some encodings are subsets rather than exhaustive OPA capabilities. The scratch checksum/version constants must remain aligned with BIOS producers.

## Test Signals
Validate table parsing against known binaries, scratch-register decoding for HFI0/HFI1, mask/shift round trips, all enum boundary values, unknown/reserved table types, and compatibility with platform firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.c

## Purpose
`qp.c` supplies HFI1-specific Queue Pair behavior for the RDMAVT core: supported work-request metadata, QP private allocation, send scheduling, SDMA/PIO wait handling, path/MTU validation, migration, error cleanup, and debug iteration.

## Important APIs, Types, And Functions
`hfi1_post_parms` declares supported RDMA, atomic, send, local invalidate, OPFN, and TID RDMA operations by QP type and flags. `hfi1_check_modify_qp()` validates address-vector service class against SDMA engines and PIO send contexts. `hfi1_modify_qp()` updates cached service class, SDMA engine, send context, header type, and OPFN state. `hfi1_setup_wqe()` enforces PMTU/VL15/SL constraints and decides whether immediate send scheduling is needed. `_hfi1_schedule_send()`, `hfi1_schedule_send()`, `hfi1_qp_wakeup()`, and `hfi1_qp_unbusy()` coordinate iowait-driven send progress. `qp_to_sdma_engine()` and `qp_to_send_context()` map QPs to hardware resources. Lifecycle helpers include `qp_priv_alloc()`, `qp_priv_free()`, `flush_qp_waiters()`, `stop_send_queue()`, `quiesce_qp()`, `notify_qp_reset()`, `notify_error_qp()`, and `hfi1_error_port_qps()`.

## Control Flow
When QP attributes change, HFI1 validates the new path, computes SC/VL-backed resources, updates 16B/9B header state, and initializes OPFN as needed. Posting a WQE lets HFI1 enforce length/MTU policy and force direct scheduling for small PIO-threshold packets. Send progress runs through `iowait`; if SDMA descriptors are unavailable, `iowait_sleep()` queues the txreq on the SDMA engine wait list and marks QP wait flags. Credit or DMA availability wakeups clear flags and reschedule IB or TID work. Reset/error/quiesce paths remove waiters, drain SDMA/PIO, flush queued txreqs, clear AHG/TID/OPFN state, and transition matching QPs to error when port SL mappings change.

## State And Persistence
QP-specific HFI1 state lives in `struct hfi1_qp_priv`: owner, AHG state, service class, SDMA engine, send context, iowait work queues, TID state, running packet-size estimate, and header type. Wait flags are split between RDMAVT `s_flags` and HFI1 private high bits. State is runtime-only and rebuilt when QPs are created or modified.

## Dependencies And Integration Points
The file depends on RDMAVT QP APIs, RDMA core verbs types, HFI1 SDMA, PIO send contexts, TID RDMA, OPFN, AH/LID helpers, iowait infrastructure, workqueues, tracepoints, and seq_file diagnostics. It is a major integration point between generic RDMA QP semantics and HFI1 hardware resource selection.

## Risks
Wait-state handling is race-sensitive: QP references are taken when queued and released on wake/removal, and busy flags are mirrored for TID second-leg sends. Incorrect locking around `s_lock`, engine waitlocks, or send-context waitlocks can strand QPs or double-release references. MTU conversion clamps OPA 10K to 8K for verbs compatibility, which can surprise callers. `hfi1_migrate_qp()` updates `priv->s_sde` but relies on later paths for send-context consistency.

## Test Signals
Cover QP modify validation for AV and alternate path, SC 0xf rejection, no-SDMA and no-PIO-resource cases, WQE length checks by QP type, immediate scheduling threshold, SDMA descriptor exhaustion and wakeup, PIO drain wait, reset/error cleanup, path migration event delivery, MTU conversion/clamping, and SL-specific port QP error iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.h

## Purpose
`qp.h` declares HFI1-specific QP flags, scheduling helpers, resource mapping APIs, lifecycle callbacks supplied to RDMAVT, and inline helpers used by send paths.

## Important APIs, Types, And Functions
The header reserves high `s_flags` bits for AHG validity/clear, PIO drain wait, TID space/response wait, and send halt. `hfi1_send_ok()` decides if send progress can run based on busy and wait flags plus pending queued work or response state. `clear_ahg()` resets AHG state and frees the SDMA AHG index. Declarations cover QP wakeup, SDMA/send-context mapping, scheduling, migration, private allocation/free, MTU conversion, waiter flushing, error notification, quiesce, port-QP erroring, and unbusy handling.

## Control Flow
Send paths consult `hfi1_send_ok()` before scheduling, set wait flags when PIO/SDMA/TID resources are unavailable, and later call `hfi1_qp_wakeup()` or `hfi1_qp_unbusy()` to resume progress. RDMAVT calls the declared hooks for QP creation, modification support, reset, error, and teardown.

## State And Persistence
The header defines bit assignments stored in `rvt_qp::s_flags` and manipulates AHG state in `hfi1_qp_priv`. These are runtime QP state only. The `HFI1_S_MIN_BIT_MASK` documents the boundary below which the base RDMAVT layer owns flags.

## Dependencies And Integration Points
It includes RDMAVT QP definitions, HFI1 verbs, SDMA, and verbs txreq headers. It is shared by QP implementation, PIO code, SDMA send paths, TID RDMA, and other verbs code that needs HFI1 wait semantics.

## Risks
Flag-bit collisions with RDMAVT would corrupt send state, so additions must stay above the documented minimum. `clear_ahg()` assumes `priv->s_ahg` exists and that SDMA AHG free is safe when `s_sde` is set and index is nonnegative. Inline scheduling predicates must remain consistent with wakeup paths.

## Test Signals
Compile coverage for flag users, AHG allocation/free cycles, send scheduling under each wait flag, TID wait interactions, and static checks that HFI1 flags do not overlap RDMAVT-defined bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.c

## Purpose
`qsfp.c` implements HFI1 QSFP I2C bus support, paged QSFP memory reads/writes, QSFP cache refresh, cable-info query support, module presence detection, power-class decoding, and human-readable cable dumps.

## Important APIs, Types, And Functions
`set_up_i2c()` creates two bit-banged I2C adapters over ASIC QSFP GPIO CSRs using `hfi1_setsda()`, `hfi1_setscl()`, `hfi1_getsda()`, and `hfi1_getscl()`. `i2c_write()` and `i2c_read()` are resource-checked raw I2C accessors. `qsfp_write()` and `qsfp_read()` handle SFF-8636 page selection and 128-byte boundary limits. `one_qsfp_read()` wraps a single read with QSFP resource acquisition. `refresh_qsfp_cache()` reads lower/upper page 0 and optional upper pages into the 128-byte-chunk cache. `get_cable_info()` serves SMA cable-info reads from cache while refreshing dynamic monitor bytes. `get_qsfp_power_class()`, `qsfp_mod_present()`, and `qsfp_dump()` expose common cable metadata.

## Control Flow
I2C setup allocates adapter objects and registers them with the Linux bit-bang I2C core. Accessors select bus 0 or 1 by target, convert the shifted QSFP address into a 7-bit I2C address and offset-size, and require the caller to hold the matching chip resource except for raw internal helpers. QSFP paged reads/writes repeatedly set byte 127 to the target page, delay after writes, then transfer a chunk that does not cross a 128-byte boundary. Cache refresh clears stale data and `cache_valid`, verifies module presence, reads mandatory page 0, conditionally reads optional pages based on paging/status bits, and marks the cache valid. Cable-info reads validate port/address/cache, copy cached bytes, and live-refresh monitor ranges.

## State And Persistence
I2C adapter objects live in `hfi1_asic_data`. Per-port QSFP state lives in `struct qsfp_data`: cached bytes, lock, validity/refresh flags, reset-needed and limiting-active flags. QSFP module memory writes persist in the module until reset/removal or power state changes, but the driver treats cache as volatile and invalidates it before refresh.

## Dependencies And Integration Points
The file depends on Linux I2C bit-bang APIs, HFI1 CSR access, chip resource locking, QSFP constants from `qsfp.h`, port/device data, and platform/link tuning code. `platform.c` uses the read/write/cache APIs to qualify and tune cables; management query paths use `get_cable_info()` and `qsfp_dump()`.

## Risks
`set_up_i2c()` can leak the first adapter if the second allocation/registration fails unless caller cleanup handles the partial state. Page selection before every chunk adds write delays and can fail mid-transfer, returning short counts. Cache validity is protected by a spinlock, but cache byte array reads are not fully serialized against refresh. `get_cable_info()` zero-fills only `excess_len`, which is usually `len` on early errors but must stay correct for partial overrange copies.

## Test Signals
Test I2C adapter registration failure for bus0/bus1, resource-check rejection, offset sizes 0/1/2, page-boundary splitting, short read/write failures, module absent, optional page combinations, cache invalidation after cable swap, dynamic monitor refresh overlap cases, overrange cable-info zero fill, power-class decoding, and dump formatting with invalid cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.h

## Purpose
`qsfp.h` defines QSFP device constants, SFF-8636 byte offsets, technology/power/attenuation helpers, interrupt flag masks, per-port QSFP cache state, and public QSFP/I2C APIs for the HFI1 driver.

## Important APIs, Types, And Functions
The header defines the QSFP I2C address, power/mod-presence delays, page/cache sizes, 128-byte read/write boundary, page-select offset, required module fields, monitor ranges, power/CDR/TX control offsets, technology classification macros, OUI helpers, alarm/warning masks, and attenuation helpers. `struct qsfp_data` holds the per-port cache, work item, spinlock, and state flags. It declares cache refresh, power-class, presence, cable-info, raw I2C, QSFP paged read/write, one-shot read, and I2C setup/cleanup functions.

## Control Flow
Callers use the constants to interpret cached QSFP bytes and the prototypes to refresh or access module memory. The cache layout stores five logical 128-byte chunks: lower page 0, upper page 0, and optional upper pages 1-3, matching cable-info query mapping rather than raw 256-byte page layout.

## State And Persistence
`struct qsfp_data` is volatile per-port state. `cache_valid` and `cache_refresh_required` indicate whether cached module bytes can be used; `reset_needed` and `limiting_active` coordinate with platform tuning after the driver has modified active modules.

## Dependencies And Integration Points
The header is consumed by QSFP implementation, platform tuning, management query code, and link bring-up. Its offsets and masks are contracts with SFF-8636 module memory and HFI1 ASIC GPIO pin wiring.

## Risks
Incorrect offsets or technology bitmaps directly affect cable qualification and tuning. Cache size and address mapping must match both `refresh_qsfp_cache()` and `get_cable_info()`. State flags are compact `u8`s updated from multiple contexts, requiring the implementation's locking discipline to be preserved.

## Test Signals
Validate power-class mappings, technology classification macros across all 16 high-nibble values, address-to-cache mapping, monitor range constants, alarm bit masks, QSFP state transitions after refresh/reset, and compile coverage for all public API users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.h -->
