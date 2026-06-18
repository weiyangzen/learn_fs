# Research: subset-b-003952

## Scope

This grouped report covers the requested InfiniBand/RDMA driver files under `sources/distributed-fs/ceph-client/drivers/infiniband`: Cisco usNIC interval/resource helpers, VMware PVRDMA host-facing verbs/device code, and the rdmavt software verbs library pieces for AH, CQ, MAD, multicast, mmap, MR, and PD handling.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c

## Purpose

Implements the mutable interval-set operations used by usNIC UIOM memory tracking. It wraps Linux `INTERVAL_TREE_DEFINE` with higher-level insert, remove, and relative-complement operations that split overlapping intervals, maintain a per-interval `ref_cnt`, and combine flag bits for overlapping registrations.

## Important APIs, Types, And Functions

The file operates on `struct usnic_uiom_interval_node` from the paired header. Important helpers are `usnic_uiom_interval_node_alloc()`, `find_intervals_intersection_sorted()`, `usnic_uiom_get_intervals_diff()`, `usnic_uiom_insert_interval()`, `usnic_uiom_remove_interval()`, and `usnic_uiom_put_interval_set()`. `INTERVAL_TREE_DEFINE(...)` emits the standard insert, remove, subtree-search, first, and next routines declared in the header.

`MAKE_NODE`, `MAKE_NODE_AND_APPEND`, and `MARK_FOR_ADD` centralize allocation and staging of intervals. `FLAGS_EQUAL(flags1, flags2, mask)` lets diff calculation treat matching masked flags as already covered.

## Control Flow

`find_intervals_intersection_sorted()` walks the rb interval tree over a query range, temporarily links matching nodes onto a list, and sorts by start address. `usnic_uiom_get_intervals_diff()` then scans that sorted intersection with a `pivot` and emits new nodes for holes not covered by same-masked flags in the tree.

`usnic_uiom_insert_interval()` first gathers all intersecting intervals. For each overlap, it stages left remnants, newly inserted gaps, overlapped segments with incremented `ref_cnt` and ORed flags, and right remnants. After staging succeeds, it removes and frees the old intersecting nodes and inserts the replacement segments into the rb tree.

`usnic_uiom_remove_interval()` iterates overlapping nodes, decrements `ref_cnt`, adds nodes that reach zero to the caller-supplied `removed` list, then removes those nodes from the rb tree. The caller owns freeing the removed nodes.

## State And Persistence Behavior

State is entirely in caller-owned `struct rb_root_cached` trees and temporary `list_head` collections. Insert mutates the tree by replacing overlapping nodes; remove only removes intervals whose reference count reaches zero. Diff output is allocated as independent nodes and must be freed through `usnic_uiom_put_interval_set()`. Allocations use atomic GFP in this file, implying callers may be in non-sleepable paths.

## Dependencies And Integration Points

Depends on Linux list sorting, slab allocation, rb interval tree generation, and the usNIC interval-node layout. It integrates with UIOM registration code that needs to know which user address ranges are new versus already pinned or tracked.

## Risks And Edge Cases

The implementation temporarily reuses each node's `link` field while it remains in the rb tree, so callers must not expect those list links to carry other concurrent state. Insert error handling frees only staged nodes; the original tree is untouched until all replacements are allocated. Removal only decrements whole intersecting nodes and does not split partially removed ranges, so callers must call it with ranges aligned to prior interval segmentation or rely on the insert-side splitting invariant. Address arithmetic around `last + 1` and `interval->start - 1` must avoid overflow/underflow at boundary values.

## Test Signals

Useful tests insert overlapping ranges with different flags, verify resulting non-overlapping segments and reference counts, compute diffs with selective flag masks, remove ranges until counts reach zero, and inject allocation failures before tree mutation. Concurrency tests should be at the caller layer because this file has no internal tree lock.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h

## Purpose

Declares the usNIC UIOM interval tree node and public interval-set operations. It is the contract for tracking pinned or registered user memory ranges by inclusive start/end address, reference count, and flags.

## Important APIs, Types, And Functions

`struct usnic_uiom_interval_node` embeds an rb node, a list link, inclusive `start`/`last` addresses, `__subtree_last` for interval-tree augmentation, `ref_cnt`, and `flags`. The header exposes generated interval-tree primitives plus `usnic_uiom_insert_interval()`, `usnic_uiom_remove_interval()`, `usnic_uiom_get_intervals_diff()`, and `usnic_uiom_put_interval_set()`.

## Control Flow

Consumers initialize an `rb_root_cached`, insert ranges as they are acquired, ask for diffs before new acquisition, and remove ranges when references are released. Removed and diff nodes are passed through lists so callers can batch follow-up unpin/free work.

## State And Persistence Behavior

The rb tree persists in the caller. Node ownership is explicit: tree nodes are owned by the tree until removed; diff-set nodes are caller-owned and released by `usnic_uiom_put_interval_set()`; remove returns zero-ref nodes for caller cleanup.

## Dependencies And Integration Points

Depends on Linux `rbtree.h` and the interval-tree generated functions from the implementation file. It is expected to be used by usNIC UIOM memory registration code and any code that must compare requested user ranges against existing tracked ranges.

## Risks And Edge Cases

The list link is dual-purpose and should only be used by these helpers while a node is in operation-specific lists. The API uses inclusive `last`, so off-by-one handling is important. No locking is declared; callers must serialize access to the tree and returned lists.

## Test Signals

Compile coverage should confirm generated function declarations match `INTERVAL_TREE_DEFINE`. Behavioral tests should verify insertion, removal, and diff ownership semantics and that callers free all returned lists.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c

## Purpose

Implements Cisco usNIC vNIC discovery and resource allocation. It maps PCI BARs, registers the lower-level `vnic_dev`, discovers WQ/RQ/CQ/interrupt resources, and hands resource chunks to higher usNIC IB queue-pair code with owner tracking.

## Important APIs, Types, And Functions

`struct usnic_vnic` holds the `vnic_dev`, mapped BARs, per-resource chunks, and `res_lock`. Public operations include `usnic_vnic_alloc()`, `usnic_vnic_free()`, `usnic_vnic_get_resources()`, `usnic_vnic_put_resources()`, `usnic_vnic_check_room()`, `usnic_vnic_res_cnt()`, `usnic_vnic_res_free_cnt()`, `usnic_vnic_dump()`, `usnic_vnic_spec_dump()`, `usnic_vnic_res_spec_update()`, and `usnic_vnic_res_spec_satisfied()`.

`_to_vnic_res_type()` maps usNIC resource enums to the common `vnic_resource` enum through the X-macro in the header. `usnic_vnic_alloc_res_chunk()` builds the resource arrays, and `usnic_vnic_discover_resources()` performs BAR mapping, `vnic_dev_register()`, and chunk discovery.

## Control Flow

Allocation requires an already enabled PCI device. `usnic_vnic_alloc()` allocates the wrapper, initializes the resource lock, maps all memory BARs, registers the `vnic_dev`, and builds resource chunks for each real resource type. Higher layers call `usnic_vnic_get_resources()` with a type, count, and non-null owner; it checks free capacity, allocates a returned chunk, then marks free resources as owned under `res_lock`. `usnic_vnic_put_resources()` reverses ownership and increments per-type free counts.

Teardown frees all resource objects, unregisters `vnic_dev`, unmaps BARs, and releases the wrapper. Dump helpers render BAR0 and each resource's owner state for debugfs/sysfs-like diagnostics.

## State And Persistence Behavior

Persistent state is the mapped BAR array, `vnic_dev` registration, and the resource chunks in the `usnic_vnic`. Resource ownership is an in-memory pointer stored in each `struct usnic_vnic_res`; it is not persisted beyond driver lifetime. Free counts are protected by a spinlock. Returned chunks are heap objects owned by the caller until `usnic_vnic_put_resources()`.

## Dependencies And Integration Points

Depends on PCI APIs, Cisco `vnic_dev` and `vnic_resource` helpers, and usNIC logging. It is consumed by usNIC IB queue-pair/group code that reserves WQ/RQ/CQ/interrupt control blocks and programs their MMIO control pointers.

## Risks And Edge Cases

`usnic_vnic_get_resources()` checks free counts before taking `res_lock`, so concurrent callers rely on the later locked scan and `WARN_ON(ret->cnt != cnt)` to detect races rather than returning a clean partial-failure path. `usnic_vnic_res_spec_satisfied()` appears to compare `res_spec->resources[i].type` against `min_spec->resources[i].type` inside the inner loop, which may not express the intended cross-index search. BAR cleanup stops on the first unmapped BAR in error cleanup, assuming BARs were mapped in order. `usnic_vnic_get_index()` derives a VF index from `devfn - 1`, which depends on device layout.

## Test Signals

Test with synthetic or mocked `vnic_dev_get_res_count()` values for zero-resource failure, successful chunk creation, concurrent get/put accounting, dump output, PCI BAR map/unmap failure cleanup, and resource-spec satisfaction across reordered resource descriptors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h

## Purpose

Defines the usNIC vNIC resource model and the public API for allocating, releasing, counting, and dumping vNIC hardware resources.

## Important APIs, Types, And Functions

`USNIC_VNIC_RES_TYPES` is an X-macro list mapping usNIC resources to lower `vnic_resource` types and display strings: EOL, WQ, RQ, CQ, INTR, and MAX. `struct usnic_vnic_res` represents one hardware resource with a control pointer and owner. `struct usnic_vnic_res_chunk` groups resources of one type. `struct usnic_vnic_res_desc` and `struct usnic_vnic_res_spec` describe requested counts. Function declarations expose allocation/free, BAR/pdev access, counting, room checks, resource spec mutation, and diagnostics.

## Control Flow

Users create a `struct usnic_vnic` through `usnic_vnic_alloc()`, construct a resource spec, check availability, acquire chunks with `usnic_vnic_get_resources()`, program the returned `ctrl` pointers, and return them with `usnic_vnic_put_resources()` before `usnic_vnic_free()`.

## State And Persistence Behavior

The header describes in-memory kernel state only. No data is persisted outside the driver. Owner pointers are opaque and let higher layers associate resources with queue-pair groups or other consumers.

## Dependencies And Integration Points

Includes PCI and Cisco `vnic_dev.h`. Resource type mapping must remain in sync with `vnic_resource.h` and `usnic_vnic.c`'s X-macro expansions.

## Risks And Edge Cases

Because the enum and mapping arrays are generated from macros, adding a resource requires updating the X-macro once but verifying all generated arrays still have matching order. The API does not encode locking expectations; callers should not read counts as stable under concurrent allocation.

## Test Signals

Compile tests catch enum/mapping drift. Runtime tests should acquire and release each resource type, verify string conversion for valid/invalid types, and confirm resource specs ending at EOL are handled consistently.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig

## Purpose

Adds the `INFINIBAND_VMWARE_PVRDMA` tristate option for the VMware Paravirtualized RDMA driver.

## Important APIs, Types, And Functions

The option depends on `NETDEVICES`, `ETHERNET`, `PCI`, `INET`, and `VMXNET3`. The help text documents that the driver provides low-level support for the VMware PVRDMA adapter and interacts with VMXNET3 for Ethernet capabilities.

## Control Flow

Kconfig selection controls whether the module is built. The VMXNET3 dependency mirrors runtime pairing in `pvrdma_main.c`, where the PVRDMA PCI function finds its sibling VMXNET3 netdev.

## State And Persistence Behavior

No runtime state exists in this file; it controls build configuration.

## Dependencies And Integration Points

Integrates with the RDMA hardware driver Kconfig hierarchy and the VMXNET3 network driver.

## Risks And Edge Cases

Incorrect dependencies can allow building a driver that cannot bind because paired network support is unavailable. Restricting to VMXNET3 is intentional for this paravirtual device.

## Test Signals

Kconfig tests should verify the symbol appears only when the network, PCI, INET, and VMXNET3 prerequisites are satisfiable and that module builds include all objects from the Makefile.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile

## Purpose

Builds the VMware PVRDMA driver module from its component source files when `CONFIG_INFINIBAND_VMWARE_PVRDMA` is enabled.

## Important APIs, Types, And Functions

The module target is `vmw_pvrdma.o`, composed of `pvrdma_cmd.o`, `pvrdma_cq.o`, `pvrdma_doorbell.o`, `pvrdma_main.o`, `pvrdma_misc.o`, `pvrdma_mr.o`, `pvrdma_qp.o`, `pvrdma_srq.o`, and `pvrdma_verbs.o`.

## Control Flow

The kernel build system compiles each object and links them into the module according to the Kconfig symbol.

## State And Persistence Behavior

No runtime state exists here. The file determines which source files participate in the module.

## Dependencies And Integration Points

Integrates with the kernel kbuild system and the local headers that tie the objects together.

## Risks And Edge Cases

Missing an object here would produce unresolved symbols or silently omit verbs functionality. Adding a new implementation file requires updating this list.

## Test Signals

`make M=drivers/infiniband/hw/vmw_pvrdma` or equivalent kernel builds should compile and link the module with no unresolved symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h

## Purpose

Central private header for the VMware PVRDMA driver. It defines all driver-private object wrappers, core device state, conversion helpers, MMIO accessors, enum translation helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions

Major types include `struct pvrdma_dev`, `pvrdma_page_dir`, `pvrdma_cq`, `pvrdma_ucontext`, `pvrdma_pd`, `pvrdma_user_mr`, `pvrdma_srq`, `pvrdma_qp`, `pvrdma_ah`, `pvrdma_wq`, `pvrdma_uar_map`, and `pvrdma_id_table`. Inline helpers convert generic IB objects to PVRDMA objects, write/read device registers, ring CQ/QP UAR doorbells, convert MTU/port/QP/MR/access/opcode/completion values, and compute page-directory pointers.

Prototypes link together command posting, UAR management, page-directory management, MR/CQ/QP/SRQ helpers, and AH/GID conversion helpers.

## Control Flow

All PVRDMA verbs handlers receive generic RDMA core objects and use the `to_v*()` helpers to reach private state. Most host operations build command structures from `pvrdma_dev_api.h`, post them through `pvrdma_cmd_post()`, then update local tables and counters. Work queues and completion queues share ring state in page directories and notify the device through UAR MMIO writes.

## State And Persistence Behavior

`struct pvrdma_dev` is the persistent per-PCI-device state: register mapping, shared device region, command/response slots, async/CQ rings, QP/CQ/SRQ lookup tables, GID table, UAR allocator, counters, netdev association, and RDMA registration state. Object wrappers persist for the lifetime of their RDMA core object and often hold umem pins or coherent page directories.

## Dependencies And Integration Points

Depends on Linux PCI, interrupts, workqueues, semaphores, RDMA core verbs, RDMA user ABI, PVRDMA device ABI, and the local ring/device/verbs headers. It is included by all PVRDMA implementation files.

## Risks And Edge Cases

Several translation helpers assume 1:1 enum values with RDMA core for many fields, while switch statements handle opcodes and network types explicitly. Table indexing commonly uses handles modulo capability sizes when receiving events, but some destroy paths clear by raw handle; tests should watch for handle semantics across device versions. MMIO writes require ordering barriers in callers where host-visible state is prepared.

## Test Signals

Compile coverage verifies structure layout and cross-file prototypes. Runtime signals include successful probe, ucontext/PD/CQ/QP/MR/SRQ lifecycle, correct work-completion decoding, and stable behavior across PVRDMA version 17 through 20 feature gates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c

## Purpose

Implements the synchronous guest-to-device command path for PVRDMA. Commands are written into a DMA-coherent command slot, signaled through a request register, and optionally completed by copying the response slot after an interrupt-driven completion.

## Important APIs, Types, And Functions

`PVRDMA_CMD_TIMEOUT` is 10 seconds. `pvrdma_cmd_post()` serializes command submissions with `cmd_sema`, copies a `union pvrdma_cmd_req` into `dev->cmd_slot`, writes `PVRDMA_REG_REQUEST`, checks `PVRDMA_REG_ERR`, and receives responses through `pvrdma_cmd_recv()`. `pvrdma_cmd_recv()` waits for `dev->cmd_done`, copies `dev->resp_slot`, and validates the response ack code.

## Control Flow

Callers fill a command union, call `pvrdma_cmd_post()`, and pass a response union plus expected response code when a response is needed. The response interrupt handler in `pvrdma_main.c` completes `cmd_done`. Timeout or interruptible wait interruption is reported as `-ETIMEDOUT`; wrong response ack is `-EFAULT`; device error register nonzero is also reported as `-EFAULT`.

## State And Persistence Behavior

Command state lives in per-device coherent command/response slots and the command completion. `cmd_sema` guarantees only one outstanding command per device. `cmd_lock` protects slot copies.

## Dependencies And Integration Points

Depends on `pvrdma_write_reg()`, `pvrdma_read_reg()`, command/response unions from `pvrdma_dev_api.h`, and the response interrupt path.

## Risks And Edge Cases

The path treats interrupted waits like timeouts. If an interrupt is lost or the device writes a mismatched ack, all higher-level verbs operations fail. The `BUILD_BUG_ON` ties command union sizing to `pvrdma_cmd_modify_qp`; ABI changes must preserve slot sizing.

## Test Signals

Exercise every command with expected response codes, no-response destroy commands, timeout injection, wrong ack injection, and concurrent callers verifying semaphore serialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c

## Purpose

Implements PVRDMA completion queue creation, destruction, notification arming, CQE flushing, and polling.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_cq()`, `pvrdma_destroy_cq()`, `pvrdma_req_notify_cq()`, `pvrdma_poll_cq()`, and `_pvrdma_flush_cqe()`. Helpers include `pvrdma_free_cq()`, `get_cqe()`, and `pvrdma_poll_one()`.

## Control Flow

Create validates flags and CQE count, reserves a device CQ counter, handles user CQs through `ib_umem_get()` or kernel CQs through driver-allocated page directories, posts `PVRDMA_CMD_CREATE_CQ`, stores the returned handle in `dev->cq_tbl`, and returns a CQ number to userspace. Notify writes the CQ handle plus arm bits to the UAR and can report missed events by checking the ring. Poll reads the kernel CQ ring, asks the device to poll once on an empty ring, translates CQEs to `ib_wc`, and advances the consumer head.

Destroy posts `PVRDMA_CMD_DESTROY_CQ`, clears the table entry, waits for event-handler references to drain through `refcnt` and `free`, releases umem/page-directory resources, and decrements counters.

## State And Persistence Behavior

Each CQ keeps a page directory, optional user umem, ring state, CQ handle, kernel/user flag, spinlock, refcount, and completion. Device-level state includes `num_cqs` and `cq_tbl`. CQEs persist in shared ring memory until consumed or flushed.

## Dependencies And Integration Points

Integrates with RDMA core CQ ops, userspace ABI structs, PVRDMA command ABI, page-directory helpers, UAR doorbells, QP table lookups for completions, and async/completion interrupts in `pvrdma_main.c`.

## Risks And Edge Cases

`pvrdma_destroy_cq()` clears `dev->cq_tbl[vcq->cq_handle]` while create indexes by `handle % max_cq`; this is safe only if handles are bounded as table indexes. `_pvrdma_flush_cqe()` only handles kernel CQs and rewrites ring contents; off-by-one errors here would drop or duplicate completions during QP reset/destroy. User CQ ring state is trusted to userspace-provided memory layout but pinned through umem.

## Test Signals

Tests should cover user and kernel CQ creation, max CQ/CQE limits, missed-event reporting, solicited/all notification arming, polling empty and non-empty rings, QP destroy flushing, CQ event refcounting, and destroy after failed userspace copyback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h

## Purpose

Defines the PVRDMA guest-host device ABI: supported versions, PCI resource IDs, MMIO registers, shared region layout, capabilities, command opcodes, command payloads, event queue elements, and response payloads.

## Important APIs, Types, And Functions

Key version constants are `PVRDMA_ROCEV1_VERSION`, `PVRDMA_ROCEV2_VERSION`, `PVRDMA_PPN64_VERSION`, `PVRDMA_QPHANDLE_VERSION`, and `PVRDMA_VERSION`. Page-directory macros define a two-level directory with up to `PVRDMA_PAGE_DIR_MAX_PAGES`. `struct pvrdma_device_shared_region` carries driver version, guest OS info, command/response DMA addresses, async/CQ ring page directories, UAR PFN, and device capabilities. Command structs cover query port/pkey, create/destroy user context, PD, MR, CQ, SRQ, QP, and GID bindings.

## Control Flow

Probe allocates and fills the shared region, writes its physical address to registers, and the device fills capabilities. Verbs code populates command structs and expects matching response ack values. Event interrupt handlers consume `pvrdma_eqe` and `pvrdma_cqne` records from shared rings.

## State And Persistence Behavior

This file defines the memory layout of persistent shared state between guest driver and paravirtual device. The shared region and command slots live for the PCI device lifetime. Command structs are transient but ABI-stable within version gates.

## Dependencies And Integration Points

Includes Linux types and `pvrdma_verbs.h`. All PVRDMA implementation files depend on these definitions, and the hypervisor/device backend must implement the same ABI.

## Risks And Edge Cases

Packed shared-region layout, version gates, and response struct sizes are ABI-sensitive. Any incompatible field reorder or enum renumbering breaks host/guest communication. `PVRDMA_SUPPORTED()` currently accepts RoCE v1 or v2 modes only; future iWARP/IB modes would need explicit expansion.

## Test Signals

ABI tests should assert struct sizes/offsets, command union sizes, version-gated UAR PFN behavior, QP handle v2 response behavior, supported/unsupported device mode detection, and command response ack matching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c

## Purpose

Implements allocation and cleanup of PVRDMA User Access Region indexes used for doorbell pages.

## Important APIs, Types, And Functions

`pvrdma_uar_table_init()` initializes an ID bitmap sized by `dev->dsr->caps.max_uar`, reserves index 0 for the driver/device, and requires a power-of-two table. `pvrdma_uar_alloc()` finds a free bit, sets it, returns an index and PFN. `pvrdma_uar_free()` clears the bit and updates allocation cursors. `pvrdma_uar_table_cleanup()` frees the bitmap.

## Control Flow

Probe initializes the table after capabilities are available. Ucontext allocation obtains a UAR index and passes its PFN to the device through a create-ucontext command. Ucontext deallocation destroys the context and frees the UAR index.

## State And Persistence Behavior

State lives in `dev->uar_table.tbl`: bitmap, `last`, `top`, `max`, `mask`, and lock. UAR allocation persists for the lifetime of a user context. PFNs are derived from the UAR PCI resource start plus allocated index.

## Dependencies And Integration Points

Depends on Linux bitmap helpers, PCI resource addresses, and PVRDMA ucontext code.

## Risks And Edge Cases

`max_uar` must be a power of two. The `top`/mask logic produces wrapped index generations; consumers must agree on how much of `uar->index` is a raw table index versus generation. Index 0 is reserved and must not be handed to userspace.

## Test Signals

Test power-of-two rejection, full-table `-ENOMEM`, reserve index 0, reuse after free, PFN computation, and concurrent allocation/free under the spinlock.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c

## Purpose

Provides PVRDMA module lifecycle, PCI probe/remove, RDMA device registration, interrupt handlers, async event dispatch, GID binding, netdevice pairing, and sysfs attributes.

## Important APIs, Types, And Functions

Key flows are `pvrdma_pci_probe()`, `pvrdma_pci_remove()`, `pvrdma_register_device()`, `pvrdma_alloc_intrs()`, `pvrdma_intr0_handler()`, `pvrdma_intr1_handler()`, `pvrdma_intrx_handler()`, `pvrdma_add_gid()`, `pvrdma_del_gid()`, netdevice notifier/work handlers, `pvrdma_init()`, and `pvrdma_cleanup()`. `pvrdma_dev_ops` wires all RDMA core operations to PVRDMA implementations; `pvrdma_dev_srq_ops` is installed conditionally when the backend supports SRQ.

## Control Flow

Probe allocates `pvrdma_dev`, enables PCI, requests regions, sets 64-bit DMA, maps registers and driver UAR, allocates the DMA-coherent shared region plus command/response slots, creates async and CQ notification rings, writes the DSR address to the device, validates RoCE support, locates the sibling VMXNET3 netdev, allocates interrupts, initializes UAR/GID tables, activates the device, registers the IB device, and registers a netdevice notifier.

Interrupt vector 0 completes command responses. Vector 1 drains async events and dispatches QP/CQ/SRQ/device events with refcount protection. Later vectors drain CQ notification events and invoke CQ completion handlers. Remove unregisters netdevice and IB state, disables interrupts, resets the device, frees coherent/page-directory state, unmaps MMIO, frees tables, and disables PCI.

## State And Persistence Behavior

Persistent module state includes an ordered event workqueue and a global `pvrdma_device_list` protected by a mutex. Per-device persistent state includes mapped MMIO, shared DMA region, rings, command slots, object lookup tables, GID table, UAR table, netdev reference, interrupt vectors, and registered `ib_device`. Runtime GID bindings are mirrored in `sgid_tbl` and in backend state through create/destroy bind commands.

## Dependencies And Integration Points

Integrates PCI, DMA coherent memory, MSI-X/MSI/INTx IRQ allocation, RDMA core registration, netdevice notifiers, VMXNET3 pairing, sysfs device attributes, and all local PVRDMA verbs implementations.

## Risks And Edge Cases

Probe has many staged resources and must unwind in exact reverse order. Netdevice association assumes the VMXNET3 function is same bus/slot/function 0. Event handlers use modulo lookups and refcounts; handle-table mismatch can misdispatch events. On NETDEV_UNREGISTER, `dev->netdev` becomes NULL, so remove must tolerate prior notifier cleanup. Device activation depends on ordered DSR register writes and barriers.

## Test Signals

Test probe failure at each allocation/mapping/command stage, successful attach to paired VMXNET3, interrupt fallback from MSI-X to MSI/INTx, async QP/CQ/SRQ/device events, netdev up/down/register/unregister, GID add/delete, sysfs attributes, and remove after partially initialized or active devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c

## Purpose

Provides PVRDMA page-directory allocation/population/cleanup and conversion helpers between PVRDMA ABI types and RDMA core types.

## Important APIs, Types, And Functions

Page-directory APIs include `pvrdma_page_dir_init()`, `pvrdma_page_dir_cleanup()`, `pvrdma_page_dir_insert_dma()`, `pvrdma_page_dir_insert_umem()`, `pvrdma_page_dir_insert_page_list()`, and `pvrdma_page_dir_get_dma()`. Conversion helpers include QP cap, GID, global route, AH attr, and GID type conversions.

## Control Flow

`pvrdma_page_dir_init()` allocates one coherent directory page, coherent table pages, and optionally coherent data pages; optional pages are inserted into the tables as DMA addresses. User-backed objects call `pvrdma_page_dir_insert_umem()` to populate entries from pinned DMA blocks. Fast-reg MRs call `pvrdma_page_dir_insert_page_list()`.

Cleanup frees optional data pages, table pages, and the directory. Conversion functions copy or translate fields used by query/modify QP and AH handling.

## State And Persistence Behavior

Page directories persist in CQ, QP, SRQ, MR, and device ring objects. They hold DMA addresses visible to the backend. Conversion helpers are stateless.

## Dependencies And Integration Points

Depends on DMA coherent allocation, RDMA umem block iteration, PVRDMA device ABI page-directory macros, and RDMA AH/GID APIs.

## Risks And Edge Cases

`pvrdma_page_dir_init()` returns `-ENOMEM` for all cleanup paths, including oversized `npages` caught before allocation as `-EINVAL`. `npages == 0` would make `PVRDMA_PAGE_DIR_TABLE(npages - 1)` problematic, so callers must avoid zero-page directories unless audited. Umem insertion relies on caller-provided `npages` matching DMA block count.

## Test Signals

Test coherent page-directory creation with and without data pages, max-page rejection, umem insertion, cleanup after partial allocation failure, fast-reg page-list insertion bounds, and AH/GID route conversion round trips.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c

## Purpose

Implements PVRDMA memory-region verbs: DMA MR creation, userspace MR registration, fast-reg MR allocation, deregistration, and scatterlist mapping for fast registration.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_get_dma_mr()`, `pvrdma_reg_user_mr()`, `pvrdma_alloc_mr()`, `pvrdma_dereg_mr()`, and `pvrdma_map_mr_sg()`. Helper `pvrdma_set_page()` appends pages to the fast-reg page list.

## Control Flow

DMA MR creation supports only `IB_ACCESS_LOCAL_WRITE`, posts `PVRDMA_CMD_CREATE_MR` with `PVRDMA_MR_FLAG_DMA`, and stores returned lkey/rkey/handle. User MR registration validates length, pins umem, builds a page directory from DMA blocks, posts create MR with start/length/access/nchunks/pdir, and stores returned keys. Fast-reg allocation creates an empty page list and page directory, creates an FRMR backend object, and later `pvrdma_map_mr_sg()` fills the page list through `ib_sg_to_pages()`.

Deregistration posts destroy MR, logs failures, then frees page directory, umem, fast-reg pages, and wrapper memory regardless of command result.

## State And Persistence Behavior

MRs hold backend handle, keys, IOVA/size, optional umem pins, page directories, and fast-reg page lists. Device backend state persists until destroy command or device teardown.

## Dependencies And Integration Points

Depends on RDMA MR APIs, umem, scatterlist-to-pages helper, PD handles from `pvrdma_verbs.c`, command posting, and page-directory helpers.

## Risks And Edge Cases

Destroy command failures do not prevent local resource release, which avoids leaks but can leave backend state until device reset. Fast-reg page-list length is capped at `PVRDMA_MAX_FAST_REG_PAGES`. User MR registration rejects zero length and lengths above backend max. `pvrdma_map_mr_sg()` records DMA addresses in `mr->pages`; correctness depends on later post-send fast-reg WQE inserting them into the page directory.

## Test Signals

Test unsupported DMA access flags, zero/too-large user MR, umem pin failure, page-directory allocation failure, create/destroy command failures, fast-reg max pages, scatterlist mapping offsets, and key propagation to userspace.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c

## Purpose

Implements PVRDMA queue-pair lifecycle and work request posting: create/destroy/query/modify QPs, reset queue state, flush CQEs, and translate send/receive WRs into backend WQEs.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_qp()`, `pvrdma_destroy_qp()`, `pvrdma_modify_qp()`, `pvrdma_query_qp()`, `pvrdma_post_send()`, and `pvrdma_post_recv()`. Internal helpers cover CQ lock ordering, queue sizing, QP reset, QP free, command destroy, WQE address computation, and fast-reg segment setup.

## Control Flow

Create validates flags, QP type, SRQ support, and port, reserves a QP counter, sets up user umems or kernel queue pages, builds a page directory, posts `PVRDMA_CMD_CREATE_QP`, stores returned qpn/handle based on device version, registers the QP in `dev->qp_tbl`, and returns handles to userspace. Modify validates standard state transitions through `ib_modify_qp_is_ok()`, copies attributes to the PVRDMA command, posts modify, and resets local rings/CQEs if moving to RESET. Query either returns RESET locally or asks the backend.

Send posting requires at least RTS, checks SQ space and SGE counts, validates opcode/type compatibility, fills UD or RC WQE fields, handles fast-reg WRs, writes SGEs, uses a write barrier, advances the producer tail, and rings the QP send doorbell after a successful batch. Receive posting rejects RESET and SRQ-associated QPs, fills RQ WQEs, advances the producer tail, and rings the receive doorbell.

## State And Persistence Behavior

Each QP tracks backend handle, qkey, send/receive rings, optional user umems, page directory, optional SRQ, page counts, state, port, mutex, refcount, and completion. Device-level state tracks active QPs in `qp_tbl` and `num_qps`. Kernel rings are coherent memory; user rings are pinned user memory.

## Dependencies And Integration Points

Integrates RDMA core QP state rules, CQ flushing from `pvrdma_cq.c`, SRQ objects, MR fast-reg page directories, PVRDMA command ABI, page-directory helpers, UAR doorbells, and async event handlers.

## Risks And Edge Cases

The destroy/free paths clear table entries by raw handle while create/event paths often use modulo. `pvrdma_post_send()` checks `qp_type != UD && qp_type != RC && wr->opcode != SEND`, which means unsupported non-UD/RC types could pass if opcode is SEND before later switch rejection; the switch still protects correctness. User QP support requires larger output ABI for QP handle on newer devices. CQ lock ordering by handle prevents deadlock during reset/flush.

## Test Signals

Test QP create for RC/UD/GSI, unsupported types/flags, SRQ and non-SRQ paths, user/kernel rings, device-version handle responses, state-transition validation, RESET flushing, send opcode/type matrix, full SQ/RQ rings, fast-reg WRs, bad AHs, receive on SRQ QPs, query after RESET and active states, and destroy with concurrent events/completions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_ring.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_ring.h

## Purpose

Defines the compact ring-index protocol shared by PVRDMA queues and notification rings.

## Important APIs, Types, And Functions

`struct pvrdma_ring` has atomic producer tail and consumer head. `struct pvrdma_ring_state` contains TX and RX rings. Inline helpers are `pvrdma_idx_valid()`, `pvrdma_idx()`, `pvrdma_idx_ring_inc()`, `pvrdma_idx_ring_has_space()`, and `pvrdma_idx_ring_has_data()`. `PVRDMA_INVALID_IDX` marks invalid ring state.

## Control Flow

Producers test space, write an entry, issue ordering barriers in callers, increment producer tail, and ring a doorbell if needed. Consumers test data, read entries, and increment consumer head. Indices wrap over `max_elems << 1` to carry a generation bit.

## State And Persistence Behavior

Ring counters live in shared coherent memory or user-pinned ring state. The helper functions are stateless but enforce ring counter validity.

## Dependencies And Integration Points

Used by PVRDMA QP send/receive rings, CQ rings, async event rings, and CQ notification rings.

## Risks And Edge Cases

`max_elems` must be a power of two for masking to work. Invalid producer or consumer values cause `PVRDMA_INVALID_IDX`; callers vary in whether they log or simply stop. Atomic counters do not themselves provide full data-entry ordering; callers supply read/write barriers.

## Test Signals

Test empty/full transitions, wraparound generation behavior, invalid index detection, power-of-two assumptions, and producer/consumer barrier pairing in queue users.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c

## Purpose

Implements PVRDMA shared receive queue verbs: create, query, modify, destroy, and local resource teardown.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_srq()`, `pvrdma_query_srq()`, `pvrdma_modify_srq()`, and `pvrdma_destroy_srq()`. `pvrdma_free_srq()` clears the device table, waits for references, releases umem and page directories, and decrements counters.

## Control Flow

Create is userspace-only and supports only `IB_SRQT_BASIC`. It validates WR/SGE limits, reserves an SRQ counter, copies user command data, pins the user buffer, builds a page directory from umem, posts `PVRDMA_CMD_CREATE_SRQ`, stores the returned handle in `dev->srq_tbl`, and copies the SRQN back to userspace. Query posts `PVRDMA_CMD_QUERY_SRQ` and returns limit/max fields. Modify supports only `IB_SRQ_LIMIT`. Destroy posts backend destroy and then frees local state regardless of command result.

## State And Persistence Behavior

SRQs hold pinned user memory, page directory, backend handle, lock, refcount, completion, WQE sizing, and the device table entry. There is no kernel-client SRQ support in this implementation.

## Dependencies And Integration Points

Depends on RDMA SRQ APIs, user ABI structs, page-directory helpers, command posting, PD handles, and async SRQ event dispatch from `pvrdma_main.c`.

## Risks And Edge Cases

Create ignores the return value of `pvrdma_page_dir_insert_umem()`, so a failed insertion would be discovered only later by backend behavior. Table clearing uses raw handle indexing while insertion uses modulo. Destroy returns 0 even when backend destroy fails. Only limit modification is accepted, so resize-like semantics are unsupported.

## Test Signals

Test no-udata rejection, unsupported SRQ type, max WR/SGE bounds, umem/page-dir failures, create/destroy command failures, query responses, limit modification, userspace copyback failure cleanup, and SRQ async event refcounting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c

## Purpose

Implements the PVRDMA non-QP/CQ/SRQ verbs surface: device/port/GID/PKey queries, port modification, user context allocation/mmap, protection domains, and address handles.

## Important APIs, Types, And Functions

Public handlers include `pvrdma_query_device()`, `pvrdma_query_port()`, `pvrdma_query_gid()`, `pvrdma_query_pkey()`, `pvrdma_port_link_layer()`, `pvrdma_modify_port()`, `pvrdma_alloc_ucontext()`, `pvrdma_dealloc_ucontext()`, `pvrdma_mmap()`, `pvrdma_alloc_pd()`, `pvrdma_dealloc_pd()`, `pvrdma_create_ah()`, and `pvrdma_destroy_ah()`.

## Control Flow

Device query copies capability fields from the shared region into RDMA core attributes and adds software-capability flags. Port and PKey queries post backend commands. GID query reads the driver's `sgid_tbl`. Ucontext allocation checks `ib_active`, allocates a UAR, posts create-ucontext with version-specific PFN width, stores `ctx_handle`, and returns QP table size. Mmap maps a single UAR page to userspace. PD allocation/deallocation post create/destroy commands and maintain counters. AH creation validates RoCE GRH and non-multicast destination, then builds a PVRDMA AV from AH attrs.

## State And Persistence Behavior

Device and port capabilities persist in `dev->dsr->caps`. User contexts own UAR indexes and backend context handles. PDs own backend PD handles and privileged/user state. AHs are local software objects with an AV and device AH count; no backend create command is used for AHs in this file.

## Dependencies And Integration Points

Depends on RDMA core query/mmap/ucontext/PD/AH APIs, PVRDMA command ABI, UAR allocator, GID table updates from `pvrdma_main.c`, and netdev/RoCE address semantics.

## Risks And Edge Cases

`pvrdma_query_device()` rejects non-empty user input/output buffers. Ucontext copyback failure calls dealloc, which posts destroy and frees UAR. `pvrdma_mmap()` only maps one page and rejects non-page-aligned offsets. AH creation rejects multicast addresses and requires GRH/RoCE attributes; multicast is not implemented through AH creation.

## Test Signals

Test capability reporting across device versions, query-port/pkey command failures, GID bounds, port shutdown state, ucontext allocation when inactive, UAR mmap validation, PD max accounting and copyback failure, AH validation for missing GRH/multicast/non-RoCE, and AH count limits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h

## Purpose

Defines PVRDMA's verb-level ABI enums, attribute structs, and operation prototypes corresponding to RDMA core verbs.

## Important APIs, Types, And Functions

The header defines PVRDMA GIDs, link layers, MTUs, port states/capabilities/width/speed, port attributes, global routes, GRH, AH attributes, CQ notification flags, QP capabilities/types/create flags/attribute masks/states/migration states, SRQ attributes, QP attributes, send flags, access flags, and prototypes for all PVRDMA verbs handlers.

## Control Flow

Implementation files translate between RDMA core structs and these PVRDMA structs before sending commands to the device or interpreting responses. The prototypes are installed into `ib_device_ops` in `pvrdma_main.c`.

## State And Persistence Behavior

The header itself has no runtime state. Its structs define state persisted in command payloads, work queue entries, AVs, and query responses.

## Dependencies And Integration Points

Includes Linux types and is consumed by `pvrdma.h`, `pvrdma_dev_api.h`, and all verbs implementation files. It must stay aligned with the device backend ABI.

## Risks And Edge Cases

Many enums intentionally mirror RDMA core values. Any mismatch requires explicit conversion helpers; assuming 1:1 mapping where it no longer holds would corrupt commands or completions. Attribute masks cap accepted fields through `PVRDMA_QP_ATTR_MASK_MAX`.

## Test Signals

Compile-time size/layout assertions and runtime query/modify/post tests should validate enum translation, QP state/attribute masks, CQ notification flags, and access/send flag masking.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile

## Purpose

Selects software RDMA provider subdirectories for the InfiniBand build.

## Important APIs, Types, And Functions

Builds `rdmavt/` for `CONFIG_INFINIBAND_RDMAVT`, `rxe/` for `CONFIG_RDMA_RXE`, and `siw/` for `CONFIG_RDMA_SIW`.

## Control Flow

The kernel build descends into enabled software provider directories.

## State And Persistence Behavior

No runtime state exists here.

## Dependencies And Integration Points

Integrates rdmavt, RXE, and SIW providers into the RDMA subsystem build.

## Risks And Edge Cases

Wrong symbol-to-directory mapping omits provider code or builds unsupported code.

## Test Signals

Kbuild coverage with each config enabled should compile the expected subdirectory.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig

## Purpose

Defines the `INFINIBAND_RDMAVT` tristate for the RDMA verbs transport library.

## Important APIs, Types, And Functions

The option depends on `INFINIBAND_VIRT_DMA`, `X86_64`, and `PCI`. The help text identifies rdmavt as a common software verbs provider for RDMA networks.

## Control Flow

When enabled, kbuild compiles the rdmavt library module described in the local Makefile.

## State And Persistence Behavior

No runtime state exists in the Kconfig file.

## Dependencies And Integration Points

Exposes rdmavt to drivers that depend on the virtual DMA and PCI environment, historically hfi1/qib-style software verbs support.

## Risks And Edge Cases

The X86_64/PCI restrictions limit portability; relaxing them would require auditing low-level assumptions in the library and consumers.

## Test Signals

Kconfig dependency tests should confirm the symbol is unavailable without virtual DMA, X86_64, or PCI and that enabling it builds the rdmavt object list.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile

## Purpose

Builds the rdmavt library object from its component implementation files.

## Important APIs, Types, And Functions

`rdmavt-y` includes `vt.o`, `ah.o`, `cq.o`, `mad.o`, `mcast.o`, `mmap.o`, `mr.o`, `pd.o`, `qp.o`, `rc.o`, `srq.o`, and `trace.o`. `CFLAGS_trace.o = -I$(src)` ensures trace header lookup.

## Control Flow

When `CONFIG_INFINIBAND_RDMAVT` is enabled, kbuild compiles and links these objects into `rdmavt.o`.

## State And Persistence Behavior

No runtime state exists here.

## Dependencies And Integration Points

Integrates the local rdmavt verbs, queue-pair, RC, SRQ, MR, CQ, mmap, multicast, MAD, AH, PD, and trace files.

## Risks And Edge Cases

Omitting a component breaks exported symbols or driver callbacks. Trace include flags are required for generated trace code to compile.

## Test Signals

Module build tests should confirm all listed objects compile and that tracepoints resolve.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c

## Purpose

Implements rdmavt address-handle validation, creation, modification, query, and destruction.

## Important APIs, Types, And Functions

`rvt_check_ah()` validates port, static rate, GRH SGID index, and delegates to an optional driver callback. `rvt_create_ah()`, `rvt_destroy_ah()`, `rvt_modify_ah()`, and `rvt_query_ah()` implement RDMA core AH ops. `rvt_check_ah` is exported for driver use.

## Control Flow

Create validates AH attrs, checks the per-device max AH count under `n_ahs_lock`, copies attributes into the rdmavt AH object, and notifies the driver if requested. Destroy decrements the count and destroys copied AH attr resources. Modify revalidates and replaces attrs. Query copies stored attrs out.

## State And Persistence Behavior

AH state is local in `struct rvt_ah`, primarily an `rdma_ah_attr` copy. Device state tracks `n_ahs_allocated`. No hardware/backend state is directly programmed here except optional driver callbacks.

## Dependencies And Integration Points

Depends on RDMA AH helpers, `ib_query_port()`, rdmavt device data, and optional driver function table hooks.

## Risks And Edge Cases

`rvt_modify_ah()` assigns `ah->attr = *ah_attr` rather than using deep-copy helper, so embedded resources must be safe for value assignment in this context. Port validity is checked after `ib_query_port()` call using `port_num`, so invalid ports depend on query behavior. Count accounting must match create/destroy paths.

## Test Signals

Test invalid port/rate/SGID index, driver callback rejection, AH max exhaustion, create/destroy count accounting, modify/query round trips, and notify_new_ah invocation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h

## Purpose

Declares rdmavt address-handle operation functions.

## Important APIs, Types, And Functions

Prototypes cover `rvt_create_ah()`, `rvt_destroy_ah()`, `rvt_modify_ah()`, and `rvt_query_ah()`.

## Control Flow

The functions are installed into RDMA device ops by rdmavt core users and implemented in `ah.c`.

## State And Persistence Behavior

No state is defined here; AH state is in rdmavt core structs from `<rdma/rdma_vt.h>`.

## Dependencies And Integration Points

Includes RDMA VT public definitions and is included by rdmavt core registration code.

## Risks And Edge Cases

Prototype changes must match RDMA core operation signatures.

## Test Signals

Compile coverage catches signature drift between header, implementation, and device-op registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c

## Purpose

Implements software completion queues for rdmavt, including creation, mmap-backed userspace queues, completion insertion, notification delivery, resize, poll, and workqueue lifecycle.

## Important APIs, Types, And Functions

Public handlers are `rvt_cq_enter()`, `rvt_create_cq()`, `rvt_destroy_cq()`, `rvt_req_notify_cq()`, `rvt_resize_cq()`, `rvt_poll_cq()`, `rvt_driver_cq_init()`, and `rvt_cq_exit()`. `send_complete()` runs completion callbacks from a per-CPU high-priority workqueue.

## Control Flow

Create validates flags and size, allocates a user `rvt_cq_wc` through `vmalloc_user()` when userspace expects an mmap offset or a kernel `rvt_k_cq_wc` through `vzalloc_node()`, creates mmap info for user queues, reserves a CQ count, sets CPU affinity for the completion vector, and initializes locks/work. `rvt_cq_enter()` writes a completion to the user or kernel ring, validates user-writable head, detects full queues, fires CQ error events, and queues completion work when notification rules match. Poll drains kernel queues. Resize allocates a new ring, validates the existing user-modifiable head/tail, copies pending entries, swaps queues, and updates mmap info for userspace.

## State And Persistence Behavior

CQ state includes ring buffers, head/tail counters, notification mode, full flag, pending mmap info, completion work, selected CPU, and device CQ allocation count. User queues persist as vmalloc memory mapped through `rvt_mmap()` and reference-counted by mmap info.

## Dependencies And Integration Points

Depends on RDMA core CQ APIs, rdmavt mmap helpers, tracepoints, workqueues, vmalloc, uverbs copyout, and optional driver completion-vector CPU lookup.

## Risks And Edge Cases

User queues expose head/tail fields to userspace, so every path must sanitize them. Full CQ handling sets a sticky `cq_full` and reports `IB_EVENT_CQ_ERR`. Completion callbacks are serialized through workqueue semantics but `triggered` is used to catch events queued during callback execution. Resize must not shrink below pending completion count.

## Test Signals

Test kernel/user CQ creation, max limits, mmap offset return, CQ full behavior and event delivery, notification transitions and missed-event reporting, poll order, resize with wrapped head/tail, invalid user head/tail values, destroy flushing pending work, and workqueue init/exit.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h

## Purpose

Declares rdmavt completion-queue operation and lifecycle functions.

## Important APIs, Types, And Functions

Prototypes cover CQ create/destroy, notify, resize, poll, driver CQ init, and CQ exit.

## Control Flow

The header allows rdmavt core and drivers to install the CQ ops and manage the global completion workqueue lifecycle.

## State And Persistence Behavior

No state is defined here; the implementation manages `struct rvt_cq` and a global workqueue.

## Dependencies And Integration Points

Includes RDMA VT and rdmavt CQ public structures.

## Risks And Edge Cases

Signatures must remain aligned with RDMA core object-size and uverbs APIs.

## Test Signals

Compile tests catch mismatches; module init/exit tests should call init/exit exactly once around CQ use.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c

## Purpose

Provides rdmavt MAD agent setup/teardown and a default MAD processing stub.

## Important APIs, Types, And Functions

`rvt_process_mad()` currently returns `IB_MAD_RESULT_FAILURE` because MAD handling is driver-specific. `rvt_create_mad_agents()` registers SMI MAD send agents for each port. `rvt_free_mad_agents()` unregisters agents and destroys stored subnet-manager AHs. `rvt_send_mad_handler()` frees completed send MAD buffers.

## Control Flow

Create loops over all ports, registers an `IB_QPT_SMI` MAD agent, stores it in `rvp->send_agent`, and optionally notifies the driver. On failure it unregisters any agents already created and sends free notifications. Teardown unregisters all agents, destroys `sm_ah`, and calls optional driver free notifications.

## State And Persistence Behavior

Per-port state includes `send_agent` and optional `sm_ah`. These persist while the rdmavt device is active.

## Dependencies And Integration Points

Depends on RDMA MAD core, rdmavt port/device structs, and driver callbacks for MAD agent lifecycle.

## Risks And Edge Cases

Default `rvt_process_mad()` is not functional; drivers that require MAD handling must override or provide their own processing. Failure unwind calls notifications only for agents that were created. Teardown must handle partially initialized ports.

## Test Signals

Test per-port agent registration, failure unwind, send completion freeing, free path destroying `sm_ah`, callback invocation, and driver-provided MAD processing paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h

## Purpose

Declares rdmavt MAD processing and MAD agent lifecycle functions.

## Important APIs, Types, And Functions

Prototypes cover `rvt_process_mad()`, `rvt_create_mad_agents()`, and `rvt_free_mad_agents()`.

## Control Flow

Used by rdmavt core and driver setup to register MAD support for each port.

## State And Persistence Behavior

No state is defined here; per-port agent state is managed in rdmavt port structures.

## Dependencies And Integration Points

Includes RDMA VT public definitions and matches RDMA MAD callback signatures.

## Risks And Edge Cases

Any signature drift from RDMA core MAD APIs breaks registration.

## Test Signals

Compile coverage and per-port setup/teardown tests validate the header contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c

## Purpose

Implements rdmavt multicast group tracking and QP attach/detach operations.

## Important APIs, Types, And Functions

Public functions are `rvt_driver_mcast_init()`, `rvt_mcast_find()`, `rvt_attach_mcast()`, `rvt_detach_mcast()`, and `rvt_mcast_tree_empty()`. Internal helpers allocate/free multicast groups and QP attachments and insert into the rb tree through `rvt_mcast_add()`.

## Control Flow

Multicast groups are keyed by MGID in an rb tree per port, with a required matching MLID. Attach rejects QP0/QP1 and RESET QPs, allocates a candidate group and QP link outside locks, then inserts or attaches under the port lock. Duplicate QP attach is treated as success. Detach finds the MGID/MLID, removes the QP link with RCU list deletion, removes the group if it was the last attachment, waits for readers through `refcount`/waitqueue, then frees structures and decrements global group count.

## State And Persistence Behavior

Per-port multicast state lives in `ibp->mcast_tree`, each `struct rvt_mcast` has a QP list, attach count, refcount, and waitqueue. Device state tracks allocated group count under `n_mcast_grps_lock`. QP refs are held for each attachment.

## Dependencies And Integration Points

Depends on rdmavt QP reference helpers, RDMA multicast attach/detach verbs, rb trees, RCU lists, waitqueues, and per-port locks.

## Risks And Edge Cases

MGID can have only one MLID; conflicting MLID returns `-EINVAL`. Readers using `rvt_mcast_find()` must decrement the reference and wake waiters as expected by broader rdmavt code. Detach waits for refcounts, so missing wakeups can hang teardown. Duplicate attach succeeds without adding state.

## Test Signals

Test attach/detach for valid QPs, duplicate attach, invalid QP0/QP1/RESET QP, max group and max QP attach limits, MGID/MLID conflict, tree-empty reporting, concurrent find/detach readers, and last-QP group deletion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h

## Purpose

Declares rdmavt multicast initialization and attach/detach helpers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_driver_mcast_init()`, `rvt_attach_mcast()`, `rvt_detach_mcast()`, and `rvt_mcast_tree_empty()`.

## Control Flow

Drivers initialize multicast state during rdmavt device setup and expose attach/detach through RDMA core verbs.

## State And Persistence Behavior

No state is defined here; multicast rb trees and counts live in rdmavt device/port structs.

## Dependencies And Integration Points

Includes RDMA VT public definitions.

## Risks And Edge Cases

Header users also need exported `rvt_mcast_find()` from the implementation if they walk multicast groups directly; it is not declared here, so external declarations must come from another public header.

## Test Signals

Compile tests should validate operation signatures and driver integration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mcast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c

## Purpose

Implements rdmavt userspace mmap bookkeeping for vmalloc-backed objects such as CQs, QPs, and SRQs, while reserving a low offset range for driver-specific mmap handlers.

## Important APIs, Types, And Functions

`rvt_mmap_init()` initializes pending mmap lists and offset counters. `rvt_create_mmap_info()` creates a pending map descriptor and allocates a dynamic offset. `rvt_update_mmap_info()` updates an existing descriptor after object resize. `rvt_mmap()` resolves offsets to pending descriptors and maps vmalloc memory with `remap_vmalloc_range()`. `rvt_release_mmap_info()`, `rvt_vma_open()`, and `rvt_vma_close()` manage krefs.

## Control Flow

Objects that need userspace mapping create mmap info and put it on `pending_mmaps`. Userspace receives the offset through udata and calls mmap. `rvt_mmap()` delegates reserved offsets below `MMAP_OFFSET_START` to the driver, otherwise finds a matching context and offset, rejects oversized mappings, removes the pending entry, maps the vmalloc object, and installs VM open/close ops for lifetime tracking.

## State And Persistence Behavior

Per-device state includes `pending_mmaps`, `pending_lock`, `mmap_offset`, and `mmap_offset_lock`. Each `rvt_mmap_info` holds offset, size, context, object pointer, pending list node, and kref. Mapped objects persist until the final VMA close and object ref release.

## Dependencies And Integration Points

Used by rdmavt CQ resize/create and other mmap-capable objects. Depends on RDMA uverbs context, vmalloc remapping, VMA operations, and optional driver mmap callback.

## Risks And Edge Cases

Offsets increment by one page regardless of object size, making offset uniqueness rather than range reservation the key contract. Only the creating context can map an object. `rvt_release_mmap_info()` deletes from the pending list even after `list_del_init()` in mmap; list state must remain valid. Objects resized before mmap must update offset and re-add pending state correctly.

## Test Signals

Test reserved-offset delegation, wrong context rejection, oversized mmap rejection, successful remap, VMA open/close refcounting, resize offset update, wrap/reset of offset counter, and destroy before mmap.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h

## Purpose

Declares rdmavt mmap initialization, mmap handling, and mmap-info creation/update/release helpers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_mmap_init()`, `rvt_release_mmap_info()`, `rvt_mmap()`, `rvt_create_mmap_info()`, and `rvt_update_mmap_info()`.

## Control Flow

rdmavt setup calls init; mmap-capable objects create/update descriptors; RDMA core mmap calls route to `rvt_mmap()`.

## State And Persistence Behavior

No state is declared here; state lives in `struct rvt_dev_info` and `struct rvt_mmap_info`.

## Dependencies And Integration Points

Includes RDMA VT public definitions and exposes helpers used by CQ/QP/SRQ code.

## Risks And Edge Cases

All users must obey the descriptor lifetime rules or VMA close can free an object still in use.

## Test Signals

Compile and mmap lifecycle tests validate function signatures and object lifetime behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c

## Purpose

Implements rdmavt software memory-region management: lkey table initialization, DMA/user/fast-reg MR allocation, MR deregistration with QP cleanup, scatterlist mapping, fast registration, rkey invalidation, and local/remote key validation.

## Important APIs, Types, And Functions

Public APIs include `rvt_driver_mr_init()`, `rvt_mr_exit()`, `rvt_get_dma_mr()`, `rvt_reg_user_mr()`, `rvt_dereg_mr()`, `rvt_alloc_mr()`, `rvt_map_mr_sg()`, `rvt_fast_reg_mr()`, `rvt_invalidate_rkey()`, `rvt_lkey_ok()`, and `rvt_rkey_ok()`. Core helpers include `rvt_init_mregion()`, `rvt_alloc_lkey()`, `rvt_free_lkey()`, `rvt_check_refs()`, and SGE/MR reference utilities.

## Control Flow

Initialization allocates an RCU-protected lkey table sized from driver parameters, with high bits indexing the table and lower bits carrying user/generation information. MR allocation initializes segment maps and publishes an lkey under the table lock. User MR registration pins umem, builds segment maps from pages, and stores user base/iova/length/access. DMA MR uses lkey 0 and is restricted to kernel PDs. Deregistration unpublishes the lkey, drops references, cleans matching QPs, synchronizes RCU, waits up to five seconds for MR refs to drain, and frees maps/umem.

Fast-reg and map-SG paths build or update page segments and key/access state. `rvt_lkey_ok()` validates local SGEs, compresses adjacent SGEs, checks PD/access/range/lkey generation, and takes MR refs. `rvt_rkey_ok()` performs equivalent remote-key validation for QP operations.

## State And Persistence Behavior

Persistent state includes the per-device lkey table, optional DMA MR pointer, generation counter, and each MR's segment maps, percpu refcount, completion, lkey publication flag, invalidation flag, PD, access flags, iova/user-base/offset/length, and optional umem. MR refs persist through in-flight QP SGEs and must drain before deregistration completes.

## Dependencies And Integration Points

Depends on RDMA umem, scatterlist page iteration, rdmavt QP iteration/cleanup, RCU, percpu refs, tracepoints, and driver device parameters. Exported functions are used by QP send/receive/RC paths to validate SGEs and remote access.

## Risks And Edge Cases

Deregistration can return `-EBUSY` after timeout and intentionally re-takes a reference, leaving cleanup to later handling. Lkey generation sizing must leave enough bits to avoid stale-key reuse. `rvt_lkey_ok()` and `rvt_rkey_ok()` must correctly handle lkey/rkey zero for kernel DMA MR while rejecting user PDs. Adjacent SGE compression must not hide overruns. User MR segment construction requires `page_address()` to succeed.

## Test Signals

Test lkey table sizing and generation wrap, DMA MR user rejection, user MR zero length and umem failures, deregistration with active QP refs, fast-reg key checks, invalidated rkey rejection, local and remote access flag enforcement, SGE boundary/offset calculations, adjacent SGE compression, scatterlist mapping, and RCU publication/unpublication races.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h

## Purpose

Declares rdmavt memory-region wrappers and MR operation prototypes.

## Important APIs, Types, And Functions

`struct rvt_mr` wraps `struct ib_mr`, optional `struct ib_umem`, and trailing `struct rvt_mregion`. `to_imr()` converts an `ib_mr` to the wrapper. Prototypes expose driver MR init/exit, DMA MR, user MR registration, deregistration, fast-reg MR allocation, and scatterlist mapping.

## Control Flow

RDMA core calls the declared MR handlers through rdmavt device ops; QP paths use the resulting `rvt_mregion` state for SGE validation.

## State And Persistence Behavior

The wrapper persists for the MR lifetime. The `rvt_mregion` must be last, matching allocation patterns that include flexible map storage.

## Dependencies And Integration Points

Includes RDMA VT definitions and is paired with `mr.c`.

## Risks And Edge Cases

Changing struct layout can break assumptions in allocation and `container_of()` conversions. The header does not expose key-validation exports; those are declared in broader rdmavt public headers.

## Test Signals

Compile tests catch layout and signature drift; MR lifecycle tests validate wrapper conversion and cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c

## Purpose

Implements rdmavt protection-domain allocation and deallocation accounting.

## Important APIs, Types, And Functions

`rvt_alloc_pd()` increments the device PD count if below `max_pd` and records whether the PD belongs to userspace. `rvt_dealloc_pd()` decrements the count.

## Control Flow

Allocation is called by RDMA core after object allocation. It locks `n_pds_lock`, checks `n_pds_allocated` against `dparms.props.max_pd`, increments, unlocks, and sets `pd->user = !!udata`. Deallocation decrements under the same lock and returns success.

## State And Persistence Behavior

Persistent state is the per-device allocated PD count and each `struct rvt_pd`'s `user` flag. No hardware state is programmed.

## Dependencies And Integration Points

Depends on RDMA VT public structs. MR logic uses `pd->user` to reject user DMA MRs and lkey zero access.

## Risks And Edge Cases

PD count underflow is possible if deallocation is called without a matching successful allocation; RDMA core lifecycle should prevent that. The implementation does not track per-PD resources beyond the user flag.

## Test Signals

Test max-PD exhaustion, user versus kernel PD flag, balanced count increment/decrement, and MR behavior differences for user/kernel PDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h

## Purpose

Declares rdmavt protection-domain allocation and deallocation handlers.

## Important APIs, Types, And Functions

Prototypes cover `rvt_alloc_pd()` and `rvt_dealloc_pd()`.

## Control Flow

The functions are installed in rdmavt RDMA device ops and called by RDMA core during PD lifecycle.

## State And Persistence Behavior

No state is declared here; count and PD flags are managed in `pd.c`.

## Dependencies And Integration Points

Includes RDMA VT public definitions.

## Risks And Edge Cases

Signatures must match RDMA core PD op expectations.

## Test Signals

Compile coverage and PD lifecycle tests validate the contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/pd.h -->
