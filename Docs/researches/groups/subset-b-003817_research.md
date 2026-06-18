# subset-b-003817 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hyperv_vmbus.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hyperv_vmbus.h

## Purpose

`hyperv_vmbus.h` is the private VMBus/SynIC coordination header for the Hyper-V guest bus. It defines monitor-page layouts, per-CPU SynIC state, global Hyper-V context, connection/channel bookkeeping, ring-buffer APIs, message dispatch metadata, utility-device states, debug hooks, and helpers used by VMBus channel and utility drivers.

## Important APIs, Types, and Functions

- `struct hv_per_cpu_context` stores host/paravisor SynIC message/event pages, a decrypted `post_msg_page` for TDX/paravisor `HVCALL_POST_MESSAGE`, and per-CPU message tasklet state.
- `struct hv_context` carries the guest ID, per-CPU contexts, and NUMA CPU allocation map.
- `struct vmbus_connection` is the central VMBus state object: connection state, interrupt pages, monitor pages, channel lists/maps, workqueues, suspend counters, and offer-delivery completions.
- Ring-buffer API declarations include `hv_ringbuffer_init`, `hv_ringbuffer_write`, `hv_ringbuffer_read`, and cleanup/preinit helpers.
- Message/connection APIs include `hv_init`, `hv_post_message`, `hv_synic_init`, `vmbus_connect`, `vmbus_post_msg`, `vmbus_on_event`, and `vmbus_on_msg_dpc`.
- `vmbus_signal_eom()` safely clears a SynIC message slot and writes the EOM MSR if another message is pending.
- CPU allocation helpers (`hv_is_allocated_cpu`, `hv_set_allocated_cpu`, `hv_clear_allocated_cpu`, `hv_update_allocated_cpus`) manage NUMA affinity for performance channels.

## Control Flow

VMBus initialization allocates SynIC pages per CPU, connects to the host using `vmbus_connect`, receives channel offers through message handlers, and tracks channels by relid in `vmbus_connection.channels`. Channel interrupts are represented by bits in the send/receive interrupt pages; `vmbus_send_interrupt()` sets the relid bit for host notification. Incoming events and messages are dispatched via per-CPU tasklets/workqueues according to `channel_message_table` entries, where handlers are explicitly marked blocking or non-blocking.

## State and Persistence Behavior

`hv_context` and `vmbus_connection` are long-lived global state. Per-channel state persists through the channel list and relid map until unmap/free. Suspend behavior is represented by `ignore_any_offer_msg`, close-on-suspend counters, and completions. SynIC and monitor pages are memory shared with Hyper-V or the paravisor and must be treated as externally mutable.

## Dependencies and Integration Points

The header depends on Linux list, atomic, tasklet, interrupt, bit operation, Hyper-V UAPI/internal definitions, `hvhdk.h`, and `hv_trace.h`. It integrates with VMBus channel management, Hyper-V utility services (`kvp`, `vss`), ring-buffer sysfs/debugfs, and confidential-computing paths that distinguish host-accessible and paravisor-only SynIC pages.

## Risks and Edge Cases

Shared SynIC pages are host/hypervisor visible in non-CoCo configurations, so consumers must validate data read from them. `vmbus_signal_eom()` has crash-path races and uses `try_cmpxchg` to avoid clearing a newly delivered message. CPU allocation helpers assume `channel_mutex` is held. Channel count limits depend on Hyper-V page size and event-flag counts.

## Test Signals

Useful signals include VMBus connect/disconnect tests, channel offer/rescind handling, relid map/unmap correctness, ring-buffer read/write coverage, suspend/resume channel cleanup, confidential VM post-message behavior, EOM pending-message delivery, debugfs/sysfs creation, and lockdep coverage around channel mutex and tasklet/workqueue dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hyperv_vmbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv.h -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv.h

## Purpose

`mshv.h` is the small shared public-internal header for Microsoft Hyper-V partition management helpers. It provides a reserved-field validation macro and declares common hypercall wrappers used by MSHV root, VTL, and related modules.

## Important APIs, Types, and Functions

- `mshv_field_nonzero(STRUCT, MEMBER)` uses `memchr_inv` and `sizeof_field` to detect non-zero reserved fields in copied user ABI structures.
- `hv_call_get_vp_registers()` and `hv_call_set_vp_registers()` batch Hyper-V VP register get/set operations for a target partition and VP.
- `hv_call_get_partition_property()` reads a scalar Hyper-V partition property.

## Control Flow

Consumers copy user or internal request structures, validate reserved fields with `mshv_field_nonzero`, then call the wrapper functions rather than directly formatting Hyper-V input pages. The concrete implementations in `mshv_common.c` serialize per-CPU hypercall input/output page usage by disabling local interrupts.

## State and Persistence Behavior

The header owns no persistent state. Its APIs operate on caller-supplied register arrays and output pointers. State lives in Hyper-V, the per-CPU hypercall pages, and higher-level partition/VP objects.

## Dependencies and Integration Points

It includes standard Linux string/field helpers and `hyperv/hvhdk.h`. The prototypes are consumed by `mshv_root_main.c`, `mshv_synic.c`, and VTL code paths that need partition properties or VP registers.

## Risks and Edge Cases

The reserved-field macro evaluates the passed structure expression for address computation and is intended for real objects, not side-effect expressions. Wrapper callers must provide arrays sized for `count`; batching is handled internally but not allocation. Property values are raw Hyper-V semantics and require caller-specific interpretation.

## Test Signals

Compile coverage should catch prototype drift against `mshv_common.c`. ABI tests should verify reserved fields reject non-zero bytes. Hypercall wrapper tests should cover multi-batch register get/set, failures converted with `hv_result_to_errno`, and property reads for valid and invalid property codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_common.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_common.c

## Purpose

`mshv_common.c` implements common Hyper-V helper calls shared across MSHV modules, plus x86 power-off integration. It wraps VP register and partition-property hypercalls behind safer batching and per-CPU page handling.

## Important APIs, Types, and Functions

- `hv_call_get_vp_registers()` fills caller-provided `struct hv_register_assoc` values by issuing repeated `HVCALL_GET_VP_REGISTERS` batches.
- `hv_call_set_vp_registers()` copies register associations into the per-CPU input page and issues repeated `HVCALL_SET_VP_REGISTERS` batches.
- `hv_call_get_partition_property()` issues `HVCALL_GET_PARTITION_PROPERTY` and returns the scalar property value.
- On x86, `hv_sleep_notifiers_register()` registers a reboot notifier that initializes S5 sleep-state system properties, and `hv_machine_power_off()` enters S5 through `HVCALL_ENTER_SLEEP_STATE`.

## Control Flow

The get/set register wrappers disable local interrupts, take the current CPU's Hyper-V input/output pages, initialize common fields once, and loop until all requested registers have been processed or a hypercall fails. Batch size is derived from `HV_HYP_PAGE_SIZE`. Partition-property reads similarly use current CPU pages, zero input, issue one hypercall, copy output on success, and return an errno-mapped Hyper-V status.

For power off, the reboot notifier validates ACPI S5 support, reads PM sleep type data, writes `HV_SYSTEM_PROPERTY_SLEEP_STATE`, and later `hv_machine_power_off()` asks Hyper-V to enter S5.

## State and Persistence Behavior

Register calls do not persist kernel state beyond modifying caller arrays; persistent effects occur inside Hyper-V. The sleep-state notifier persists registration in the reboot notifier chain. Local IRQ masking protects per-CPU hypercall pages from same-CPU reentrancy while formatting inputs.

## Dependencies and Integration Points

The file depends on `asm/mshyperv.h`, ACPI, reboot notifiers, exports, and `mshv.h`. Its exported wrappers are used by root partition management, SynIC setup, VTL paths, and any module that needs VP registers or partition properties.

## Risks and Edge Cases

The loops rely on `hv_repcomp(status)` making progress after successful rep hypercalls. If Hyper-V returns success with zero completions, callers could spin. Sleep-state initialization is x86-only and depends on ACPI S5 being available. Local IRQ disabling means wrappers should avoid long or blocking work while using per-CPU pages.

## Test Signals

Tests should cover single and multi-batch register operations, partial completion on failures, property read success/failure, IRQ-context safety assumptions, reboot notifier registration failure logging, ACPI S5 unsupported paths, and power-off hypercall invocation on x86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs.c

## Purpose

`mshv_debugfs.c` builds `/sys/kernel/debug/mshv` and exposes Hyper-V statistics pages for the hypervisor, logical processors, the parent partition, child partitions, and VPs. It also maps/unmaps the backing Hyper-V stats pages.

## Important APIs, Types, and Functions

- `mshv_debugfs_init()` creates the top-level tree, root-only hypervisor/LP stats, and parent partition stats.
- `mshv_debugfs_exit()` removes debugfs dentries and unmaps all stats pages.
- `mshv_debugfs_partition_create/remove()` create/remove per-partition directories and partition stats.
- `mshv_debugfs_vp_create/remove()` create/remove VP `stats` files under a partition's `vp` directory.
- `lp_stats_show`, `hv_stats_show`, `partition_stats_show`, and `vp_stats_show` print named counters from `hv_stats_page`.
- Mapping helpers call `hv_map_stats_page()` and `hv_unmap_stats_page()` for `HV_STATS_OBJECT_*` identities.

## Control Flow

Initialization creates `mshv`, optionally maps hypervisor stats and uses the logical processor count counter to size LP mappings, creates `lp/<index>/stats`, then creates `partition/self` for the current partition and per-online-CPU VP stats. Dynamic child partitions and VPs call the exported create/remove helpers during their own lifecycle.

Stats reads are simple seq-file show callbacks. Partition and VP stats can have both SELF and PARENT areas; display prefers PARENT values and falls back to SELF when the PARENT value is zero. L1VH parent partitions cannot access PARENT stats and alias PARENT to SELF.

## State and Persistence Behavior

Global dentries track the debugfs tree. `mshv_lps_stats`, `parent_vp_stats`, and partition/VP object fields hold mapped stats-page pointers until removal. Stats page mappings are persistent Hyper-V mappings and must be explicitly unmapped.

## Dependencies and Integration Points

The file includes `mshv_debugfs_counters.c` directly for counter names, depends on debugfs and Hyper-V stats hypercalls from `mshv_root_hv_call.c`, and is invoked by module init/exit plus partition/VP creation and destruction in `mshv_root_main.c`.

## Risks and Edge Cases

Debugfs creation is optional at runtime but mapping failures abort module init for parent stats. CPU hotplug after init is not reflected in `parent_vp_stats` because it iterates online CPUs during creation/removal. The direct include of counter data is guarded by `MSHV_DEBUGFS_C` to prevent accidental separate use. Removal paths assume dentries/private pointers were successfully initialized.

## Test Signals

Test by mounting debugfs and checking `mshv/stats`, `mshv/lp/*/stats`, `mshv/partition/self/stats`, child partition directories, VP directories, and clean teardown. Fault-injection should cover map failures at each stage, PARENT stats unsupported fallback, L1VH aliasing, and module exit without leaks or stale mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs_counters.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs_counters.c

## Purpose

`mshv_debugfs_counters.c` is data-only support for `mshv_debugfs.c`. It maps Hyper-V stats-page counter indices to printable names for hypervisor, logical processor, partition, and VP counters.

## Important APIs, Types, and Functions

- `hv_hypervisor_counters[]` names hypervisor-wide counters such as logical processors, partitions, pages, and startup cost.
- `hv_lp_counters[]` names logical processor counters, with architecture-specific x86_64 and arm64 suffix ranges.
- `hv_partition_counters[]` names partition counters including GPA/device pages, TLBs, attached devices, auto suspend, and active child partitions.
- `hv_vp_counters[]` names VP counters including runtime, intercepts, hypercalls, interrupts, nested virtualization, dispatch, waiting, VTL, and architecture-specific events.

## Control Flow

There is no executable control flow beyond static array initialization. `mshv_debugfs.c` includes this file after defining `MSHV_DEBUGFS_C`, then iterates the arrays and skips NULL entries when printing stats.

## State and Persistence Behavior

The arrays are static and immutable after load. Sparse indices intentionally preserve the Hyper-V counter numbering so `stats->data[idx]` lines up with the name.

## Dependencies and Integration Points

The file must be included only from `mshv_debugfs.c`; it emits a preprocessor error otherwise. Architecture guards tailor counter names to x86_64 or arm64 Hyper-V layouts.

## Risks and Edge Cases

Counter names must stay synchronized with Hyper-V `hv_stats_page` layouts. Sparse arrays make missing indices silent in output, which is useful for reserved slots but can hide newly added counters. Architecture-specific index drift would produce misleading debugfs labels without compile errors.

## Test Signals

Build both x86_64 and arm64 configurations, verify debugfs output names match known Hyper-V counters, check sparse NULL entries are skipped, and add review checks when `hvhdk.h` counter definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.c

## Purpose

`mshv_eventfd.c` implements KVM-style `irqfd` and `ioeventfd` support for MSHV partitions. It lets userspace signal an eventfd to inject a guest interrupt and lets guest MMIO doorbells signal userspace eventfds.

## Important APIs, Types, and Functions

- IRQ ack notifier APIs register/unregister callbacks and notify matching GSIs.
- `mshv_set_unset_irqfd()` assigns or deassigns an eventfd/GSI binding.
- `mshv_irqfd_wakeup()` drains eventfd counters, updates routing, and asserts interrupts through a fast root-scheduler vector path or `hv_call_assert_virtual_interrupt()`.
- Resampler support groups irqfds by GSI and signals resample eventfds on EOI/ack.
- `mshv_set_unset_ioeventfd()` assigns/deassigns MMIO doorbell eventfds using `mshv_register_doorbell()`.
- `mshv_eventfd_init()` initializes partition lists/locks, and `mshv_eventfd_release()` tears down ioeventfds and irqfds.

## Control Flow

Assigning an irqfd resolves the eventfd, optionally resolves a resamplefd, joins or creates a resampler, installs a priority wait-queue callback through poll, checks duplicate eventfd use, snapshots routing under SRCU, links the irqfd, and handles already-pending events. On wakeup, EPOLLIN reads the counter and injects an interrupt; EPOLLHUP deactivates the binding and queues cleanup work. Deassign unlinks matching bindings and flushes the cleanup workqueue before returning.

Assigning an ioeventfd validates MMIO-only flags, length and overflow, checks collisions under the partition mutex, registers a Hyper-V doorbell port for address/value matching, and links the object into an RCU list. Doorbell ISR callbacks find the matching doorbell ID and signal the eventfd.

## State and Persistence Behavior

Per-partition hlist state stores active irqfds, resamplers, ack notifiers, and ioeventfds. `seqcount_spinlock_t` protects routing snapshots in irqfds. Cleanup is deferred through `irqfd_cleanup_wq`, but deassign/release flushes it to prevent late interrupts after teardown.

## Dependencies and Integration Points

The file depends on eventfd, poll, wait queues, workqueues, SRCU/RCU, APIC definitions on x86, MSHV IRQ routing, and SynIC doorbell APIs. It integrates with partition ioctls, `mshv_irq.c` routing updates, `mshv_synic.c` EOI and doorbell handling, and Hyper-V interrupt hypercalls.

## Risks and Edge Cases

Fast injection only supports x86_64 root scheduler, direct APIC destination mode, available VP register pages, and spare vector slots. A validation bug risk exists in `mshv_irqfd_assign()`: it checks resample/level-triggered before `mshv_irqfd_update()` fills `irqfd_lapic_irq`, so the level-triggered test may see zeroed routing data. Resampler shutdown must synchronize with SRCU readers. Duplicate detection forbids the same eventfd for another IRQ but not all possible semantic collisions. `ioeventfd_check_collision()` is annotated with `pt->mutex`, but the actual field is `pt_mutex`.

## Test Signals

Cover irqfd assign/deassign, duplicate fd rejection, pending event delivery after assign, EPOLLHUP cleanup, routing-table updates, resample signaling after EOI, fast-path fallback, ioeventfd collision rules, wildcard/datamatch behavior, doorbell unregister on release, and lockdep/RCU/SRCU teardown under concurrent signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.h -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.h

## Purpose

`mshv_eventfd.h` declares the MSHV irqfd/ioeventfd data structures and APIs used by partition ioctl handling, IRQ routing, and SynIC interrupt acknowledgment.

## Important APIs, Types, and Functions

- `struct mshv_irqfd_resampler` tracks a GSI-level resample group and its ack notifier.
- `struct mshv_irqfd` stores one userspace eventfd-to-GSI binding, routing snapshot, wait entry, shutdown work, and optional resamplefd linkage.
- `struct mshv_ioeventfd` stores one MMIO doorbell-to-eventfd binding, including address, length, datamatch, wildcard flag, and Hyper-V doorbell ID.
- Public APIs initialize/release partition eventfd state, manage ack notifiers, set/unset irqfd/ioeventfd bindings, and manage the irqfd cleanup workqueue.

## Control Flow

Partition creation calls `mshv_eventfd_init()`. Partition ioctls copy user arguments and call `mshv_set_unset_irqfd()` or `mshv_set_unset_ioeventfd()`. Routing updates call `mshv_irqfd_routing_update()` via the root header declaration. EOI handling calls `mshv_notify_acked_gsi()` to drive resamplers. Partition release calls `mshv_eventfd_release()`.

## State and Persistence Behavior

The structures are heap allocated by `mshv_eventfd.c` and linked into per-partition hlist heads. Eventfd contexts are reference-counted. Shutdown work separates wait-queue detachment from object freeing.

## Dependencies and Integration Points

The header includes poll/eventfd-facing Linux types, `mshv.h`, and `mshv_root.h`. It is consumed by IRQ routing, root partition ioctl logic, and eventfd implementation.

## Risks and Edge Cases

The structs expose internal lock-sensitive fields; callers outside `mshv_eventfd.c` should not mutate list nodes, seqcounts, or contexts. Lifetime depends on cleanup workqueue initialization at module load and flushing during deassign/release.

## Test Signals

Build tests should catch type drift with `mshv_eventfd.c`. Runtime tests should verify partition init/release initializes all hlist heads and locks, irqfd workqueue lifecycle wraps module init/exit, and ack notifiers fire only for matching GSIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_irq.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_irq.c

## Purpose

`mshv_irq.c` manages userspace-provided guest IRQ routing tables for MSHV partitions and translates routing entries into Hyper-V virtual interrupt descriptors.

## Important APIs, Types, and Functions

- `mshv_update_routing_table()` validates and installs a new RCU-protected `mshv_girq_routing_table`.
- `mshv_free_routing_table()` frees the current table at partition teardown.
- `mshv_ret_girq_entry()` returns a routing entry for an IRQ number under SRCU/lock protection.
- `mshv_copy_girq_info()` converts a `mshv_guest_irq_ent` MSI-style entry into `struct mshv_lapic_irq`.

## Control Flow

The set-MSI-routing ioctl copies user entries and calls `mshv_update_routing_table()`. The function validates GSI bounds and rejects non-zero high MSI address, sizes the table to the maximum GSI plus one, rejects duplicate GSI mappings, fills entries, swaps the table under `pt_irq_lock`, notifies irqfds to refresh cached routes, then waits for SRCU readers before freeing the old table.

## State and Persistence Behavior

`partition->pt_girq_tbl` is an RCU pointer to the active flexible-array routing table. IRQFDs cache translated entries and are refreshed on each route swap. Route entries persist until replaced or the partition is destroyed.

## Dependencies and Integration Points

The file depends on slab allocation, RCU/SRCU, `mshv_eventfd.h`, `mshv_root.h`, and tracepoints. It feeds `mshv_eventfd.c` interrupt injection and is driven by `MSHV_SET_MSI_ROUTING`.

## Risks and Edge Cases

GSI zero is ambiguous because duplicate detection tests `guest_irq_num != 0`, so duplicate GSI 0 entries may not be rejected as intended. Only one-to-one GSI/MSI routing is supported. x86 and arm64 fill different `hv_interrupt_control` fields. Premature irqfd registration before routes exist yields an invalid entry that is intentionally ignored.

## Test Signals

Test empty table swaps, maximum GSI bounds, duplicate GSI handling including GSI 0, non-zero `address_hi` rejection, irqfd route refresh after swaps, SRCU readers during replacement, and architecture-specific conversion of vector/APIC/interrupt control fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_portid_table.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_portid_table.c

## Purpose

`mshv_portid_table.c` provides an IDR-backed global table for Hyper-V port IDs, primarily used to map SynIC doorbell port IDs back to kernel callback metadata.

## Important APIs, Types, and Functions

- `mshv_portid_alloc()` allocates an ID in `[1, INT_MAX)` for a caller-provided `port_table_info`.
- `mshv_portid_lookup()` copies table info for a port ID under RCU read locking.
- `mshv_portid_free()` removes an ID, waits for RCU readers, and frees the entry.
- `mshv_port_table_fini()` removes and RCU-frees all remaining entries during module exit.

## Control Flow

Doorbell registration allocates and fills `port_table_info`, obtains an ID, then uses that ID as the Hyper-V port/connection ID. SynIC doorbell ISR lookup copies the table entry and invokes the callback if the port type is `HV_PORT_TYPE_DOORBELL`. Unregistration disconnects/deletes the Hyper-V port and frees the ID.

## State and Persistence Behavior

The static `DEFINE_IDR(port_table_idr)` is global module state. Entries persist until explicit free or module finalization. Lookup returns a by-value copy so callbacks can be invoked after dropping RCU, but pointer fields inside the copy remain owned by the original subsystem.

## Dependencies and Integration Points

The file depends on Linux IDR, RCU freeing, Hyper-V definitions, and `mshv_root.h`. It integrates with `mshv_synic.c` doorbell registration and ISR dispatch.

## Risks and Edge Cases

`mshv_portid_lookup()` drops RCU before copying `_info`, so the entry can be freed between `idr_find()` and `*_info = *_info`; this is a use-after-free risk unless external ordering prevents concurrent free. The finalizer uses `kfree_rcu`, while normal free synchronizes then `kfree`s. IDR allocation uses `GFP_KERNEL` while holding the IDR lock via `idr_lock`, which should be reviewed for allocation constraints.

## Test Signals

Exercise concurrent lookup/free under KCSAN/KASAN, repeated allocate/free, module finalization with live entries, lookup of missing IDs, and doorbell callback dispatch while unregistering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_portid_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_regions.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_regions.c

## Purpose

`mshv_regions.c` implements guest memory-region backing for MSHV root partitions. It supports pinned RAM, movable/HMM-backed RAM faulted on GPA intercepts, MMIO mappings, huge-page chunking, encrypted-partition host-access transitions, and mmu interval invalidation.

## Important APIs, Types, and Functions

- `mshv_region_create()` allocates a flexible-array region and derives Hyper-V map flags from user flags.
- `mshv_region_pin()`, `mshv_region_map()`, `mshv_region_share()`, `mshv_region_unshare()`, and invalidation helpers manage page pinning and Hyper-V mappings.
- `mshv_region_handle_gfn_fault()` faults and maps a batch around an intercepted GFN for movable memory.
- `mshv_region_movable_init/fini()` register/remove an `mmu_interval_notifier`.
- Internal range/chunk walkers coalesce contiguous present pages and use 2 MiB large-page mappings when aligned and supported.

## Control Flow

Pinned regions pin all user pages in batches with `FOLL_LONGTERM`, optionally release host access for SNP partitions, then map GPA pages. Movable regions initially map GPA as no-access; when Hyper-V reports a GPA intercept, the root run loop locates the region and calls `mshv_region_handle_gfn_fault()`, which uses HMM to fault pages, verifies the notifier sequence, locks the region, stores `struct page *` pointers, and remaps the affected range with normal access. MMU invalidation remaps affected pages to no-access and clears page pointers, unpinning if needed.

## State and Persistence Behavior

Each `mshv_mem_region` stores guest PFN range, userspace start, map flags, type, partition pointer, refcount, optional interval notifier, mutex, and page array. Regions are linked from `partition->pt_mem_regions` and destroyed by refcount, which unmaps GPA pages, restores host access for encrypted partitions, invalidates pages, removes movable notifiers, and frees memory.

## Dependencies and Integration Points

The file depends on HMM, mmu interval notifiers, page pinning, Hyper-V mapping/host-access hypercalls, and partition state from `mshv_root.h`. It is called from memory ioctls and GPA intercept handling in `mshv_root_main.c`.

## Risks and Edge Cases

Invalidation failure is explicitly dangerous because Hyper-V could retain mappings to freed pages. Huge-page support only accepts compound head pages with PMD order and aligned GFN/count. `page_count = HVPFN_DOWN(mend - mstart)` can become zero for sub-page invalidation ranges. Encrypted-region destroy refuses to unpin if sharing back to host fails, intentionally avoiding host crash but leaking inaccessible pages. Long-term pinning has memory-management impact.

## Test Signals

Test pinned map/unmap, movable no-access initial mapping, GPA intercept fault batching, mmu invalidation during guest execution, huge-page and misaligned fallback, SNP share/unshare error paths, overlapping region rejection at callers, and KASAN/lockdep under concurrent unmap and fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_regions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root.h -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_root.h

## Purpose

`mshv_root.h` is the private root-partition interface for `/dev/mshv`. It defines partition, VP, memory-region, IRQ routing, SynIC, doorbell, and root global state plus the internal APIs shared by root implementation files.

## Important APIs, Types, and Functions

- `struct mshv_vp` stores VP index, partition backpointer, mapped state pages, run flags, signal count, wait queue, and debugfs state.
- `struct mshv_partition` stores partition ID, refcount, mutexes, memory regions, VPs, IRQ/SRCU state, eventfd lists, routing table, async hypercall state, isolation type, init state, and debugfs dentries.
- `struct mshv_mem_region` tracks guest/user ranges, Hyper-V flags, type, page array, refcount, notifier, and mutex.
- IRQ structs model ack notifiers, LAPIC interrupt data, and routing table entries.
- `struct mshv_root` holds the partition hash table and VMM capabilities.
- Function declarations cover routing, port IDs, SynIC, partition refs/lookups, stats mapping, region operations, hypercall wrappers, and debugfs hooks.

## Control Flow

The header connects the module's implementation units. `mshv_root_main.c` owns lifecycle and ioctls; `mshv_root_hv_call.c` owns Hyper-V calls; `mshv_regions.c` owns memory; `mshv_irq.c` owns routing; `mshv_eventfd.c` owns eventfd bridges; `mshv_synic.c` owns interrupts and doorbells; `mshv_debugfs.c` owns stats exposure.

## State and Persistence Behavior

Partition objects are refcounted and RCU-hashed. VP objects live inside partitions and are exposed through anon inode fds. Memory regions are kref-managed. IRQ routing uses RCU/SRCU. Async hypercall state is one-per-partition because the implementation permits only one in-flight async hypercall per partition.

## Dependencies and Integration Points

The header depends on kernel locking, SRCU, hash tables, mmu notifiers, UAPI `linux/mshv.h`, Hyper-V HVDK types, and trace declarations. It defines the internal contract for all MSHV root files.

## Risks and Edge Cases

The structures expose many lock-protected fields; misuse can race with ISR, fd release, or RCU teardown. `MSHV_MAX_VPS` is fixed at 256. Version constants define the validated Hyper-V build range but module init logs rather than hard-fails on mismatch. `mshv_partition_encrypted()` currently recognizes SNP isolation only.

## Test Signals

Compile all MSHV configurations, validate lockdep annotations and partition reference behavior, stress create/destroy with live VP fds, verify RCU lookup safety from ISR paths, and test stats/debugfs fields under `CONFIG_DEBUG_FS` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root_hv_call.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_root_hv_call.c

## Purpose

`mshv_root_hv_call.c` is the Hyper-V hypercall adapter for the root MSHV driver. It formats input/output pages, handles repeated hypercalls and memory-deposit retries, maps/unmaps GPA and state pages, manages ports, stats pages, and sparse SPA host access.

## Important APIs, Types, and Functions

- Partition lifecycle: `hv_call_create_partition`, `initialize`, `finalize`, `delete`, `withdraw_memory`.
- GPA mapping: `hv_call_map_gpa_pages`, `hv_call_map_mmio_pages`, `hv_call_unmap_gpa_pages`, and access-state reads.
- VP state: `hv_call_get_vp_state`, `hv_call_set_vp_state`, `hv_map_vp_state_page`, `hv_unmap_vp_state_page`, and `hv_call_delete_vp`.
- Interrupts: `hv_call_assert_virtual_interrupt()` and `hv_call_clear_virtual_interrupt()`.
- Ports and doorbells: create/delete/connect/disconnect port and notify ring empty.
- Stats: `hv_map_stats_page()` and `hv_unmap_stats_page()` support old hypervisor-provided mappings and L1VH overlay-GPFN mappings.
- `hv_call_modify_spa_host_access()` acquires/releases sparse SPA host access for encrypted memory transitions.

## Control Flow

Most calls disable local interrupts while using current CPU hypercall pages, zero and fill the input structure, invoke a fast, normal, or repeated hypercall, restore interrupts, and translate Hyper-V status to errno. Calls that can return `HV_STATUS_INSUFFICIENT_MEMORY` or equivalent loop through `hv_deposit_memory()` or `hv_call_deposit_pages()` until success or deposit failure. Repeated mapping/unmapping walks batches sized by the hypercall page.

## State and Persistence Behavior

The file does not own high-level objects but mutates persistent Hyper-V partition state. GPA/state/stats mappings persist until corresponding unmap/finalize calls. Overlay-GPFN mode allocates Linux pages for VP state and stats mappings and frees them on unmap. Withdraw-memory returns deposited pages to the kernel.

## Dependencies and Integration Points

It depends on `asm/mshyperv.h`, `hvhdk.h` structures, global `mshv_root.vmm_caps`, and tracepoints. It is called throughout partition lifecycle, memory mapping, debugfs stats, SynIC doorbells, eventfd interrupts, and VP ioctls.

## Risks and Edge Cases

Large-page mapping requires 2 MiB aligned page counts and indexes into the original page array with shifted offsets. Error rollback after partial map uses `done`, which is counted in large-page units when large mappings are active and should be reviewed against `hv_call_unmap_gpa_pages()` expectations. Old stats-page mapping returns success with NULL for unsupported PARENT area; callers must handle NULL. Local IRQ masking assumes hypercalls are bounded. `hv_call_modify_spa_host_access()` returns early on index overflow before restoring IRQs if that path is hit inside the IRQ-disabled loop, which should be reviewed.

## Test Signals

Fault-inject Hyper-V statuses for memory-deposit loops, partial completions, GPA map rollback, MMIO RAM rejection, large-page alignment, VP state page overlay allocation/free, PARENT stats unsupported fallback, port create/connect cleanup, sparse SPA host access for encrypted partitions, and tracepoint emission for lifecycle calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root_hv_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root_main.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_root_main.c

## Purpose

`mshv_root_main.c` implements the `/dev/mshv` misc device and core root-partition VMM ABI. It creates partitions and VPs, runs VPs under Hyper-V or root scheduling, maps guest memory, handles VP state ioctls, passes audited hypercalls through to Hyper-V, and tears everything down.

## Important APIs, Types, and Functions

- File operations for the device, partition fds, and VP fds implement `MSHV_CREATE_PARTITION`, partition ioctls, VP ioctls, mmap, and release.
- `mshv_ioctl_create_partition()` validates feature/isolation flags, creates a Hyper-V partition, initializes locks/lists/SRCU/eventfd state, hashes the partition, and returns an anon fd.
- `mshv_partition_ioctl_create_vp()` creates a VP, maps intercept/register/GHCB pages, maps stats pages, creates debugfs, and returns an anon VP fd.
- `mshv_vp_ioctl_run_vp()` runs a VP, handles GPA intercepts internally for movable memory, and returns intercept messages to userspace.
- Memory ioctls map/unmap pinned RAM, movable RAM, or MMIO through `mshv_regions.c` and Hyper-V calls.
- Partition release drains eventfds/SRCU, drops refs, and `destroy_partition()` finalizes Hyper-V state, unmaps VPs/regions, withdraws deposited memory, deletes the partition, and frees routing tables.
- Module init registers `/dev/mshv`, initializes SynIC, VMM caps, scheduler buffers, debugfs, irqfd workqueue, partition hash, and the MSHV ISR handler.

## Control Flow

Users open `/dev/mshv`, create a partition fd, initialize the partition, register guest memory, create VPs, set routing/eventfds, and call `MSHV_RUN_VP` on VP fds. Hypervisor-scheduler mode resumes VP execution by clearing suspend registers and waits for SynIC kicks. Root-scheduler mode dispatches VPs directly with per-CPU input/output pages, handles guest-mode pending work, blocked dispatch state, explicit/intercept suspend, and injected vectors. GPA intercepts for movable regions are resolved in-kernel and the run loop continues; unhandled intercepts are copied to userspace.

## State and Persistence Behavior

`mshv_root` holds global VMM caps and partition hash. Partitions are refcounted and persist while fds/VPs reference them. VPs store mapped Hyper-V state pages and wait queues. Memory regions persist in a partition hlist. Async hypercall completion is per partition. Root scheduler buffers are per CPU. Module init state persists until module exit.

## Dependencies and Integration Points

The file integrates all MSHV subsystems: common register/property calls, root hypercall wrappers, regions, IRQ routing, eventfd, SynIC, debugfs, tracepoints, Linux anon inodes, miscdevice, cpuhp, reboot/panic context, guest-mode work, and UAPI `linux/mshv.h`.

## Risks and Edge Cases

The async hypercall guard appears inverted: `mshv_init_async_handler()` rejects when `completion_done()` is true, but a newly initialized completion starts done, so this path deserves review. VP creation error handling can jump to `free_vp` without setting `ret = -ENOMEM` after `kzalloc_obj(*vp)` failure. Root scheduler paths depend on stats counters to detect blocked dispatch threads. Partition teardown must drain root-scheduler VP signals before removing the RCU hash. Passthrough hypercalls are limited by allowlists but still copy arbitrary one-page input/output buffers from userspace.

## Test Signals

End-to-end tests should cover create/init/destroy partition, VP create/run/mmap/state get/set, memory map/unmap for pinned/movable/MMIO, GPA intercept resolution, irqfd/ioeventfd ioctls, MSI routing, passthrough hypercall allow/deny, root and non-root scheduler paths, debugfs lifecycle, module init failure unwinding, and concurrent fd release while SynIC messages arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_root_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_synic.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_synic.c

## Purpose

`mshv_synic.c` manages MSHV SynIC interrupt setup, message dispatch, scheduler/intercept kicks, async hypercall completions, and doorbell port integration for root partitions.

## Important APIs, Types, and Functions

- `mshv_isr()` is the main MSHV SynIC interrupt handler.
- Doorbell helpers read queued ports from SynIC event rings and invoke registered port-table callbacks.
- Scheduler message handlers kick VPs from bitset or pair messages.
- Async completion handler completes a partition's async hypercall.
- Intercept handler routes opaque intercept and APIC EOI messages to VP wait queues or irq ack notifiers.
- `mshv_synic_init/exit()` configure per-CPU SynIC pages, SINT vector/IRQ, CPU hotplug, and reboot cleanup.
- `mshv_register_doorbell()` and `mshv_unregister_doorbell()` create/connect/disconnect Hyper-V doorbell ports.

## Control Flow

CPU online setup maps SIMP, SIEFP, and SIRBP pages from MSR-provided GPAs, enables percpu IRQs if needed, programs interception and doorbell SINTs, and enables SynIC globally. `mshv_isr()` reads the interception SINT message slot, tries doorbell, scheduler, async completion, then intercept handling, clears the message, memory barriers, and writes EOM if pending.

Doorbell messages drain the doorbell event ring, look up each port ID, and call the registered callback in interrupt context. Scheduler messages find partitions through the RCU hash and wake target VPs. Intercept messages either notify irqfd resamplers on APIC EOI or kick the VP whose intercept message page has been filled by Hyper-V.

## State and Persistence Behavior

Per-CPU `synic_pages` stores mapped SynIC pages. SINT vector and Linux IRQ are module globals. Doorbell port table entries persist until unregister. VP run state is updated by interrupt context through `kicked_by_hv`, `vp_signaled_count`, and wait queues.

## Dependencies and Integration Points

The file depends on Hyper-V MSRs, ACPI GSI setup on platforms without `HYPERVISOR_CALLBACK_VECTOR`, CPU hotplug, reboot notifiers, port ID table, eventfd ack notifications, partition lookup, and root hypercall wrappers for ports and ring-empty notifications.

## Risks and Edge Cases

Callbacks run in interrupt context and must not sleep. Doorbell event-ring tail storage comes from Hyper-V per-CPU state and missing pages are tolerated with debug logs. Partition/VP lookup occurs under RCU but VP array entries are used without extra locking based on lifecycle assumptions. Reboot notifier removes CPU hotplug state for root partitions. Incorrect EOM ordering can lose messages.

## Test Signals

Test CPU online/offline SynIC setup, SINT IRQ allocation paths, doorbell registration and MMIO-triggered callback, async hypercall completion, scheduler bitset/pair messages, APIC EOI resampler notification, opaque intercept VP wakeups, message-pending EOM behavior, and module exit/reboot cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_synic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.c -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.c

## Purpose

`mshv_trace.c` instantiates the MSHV tracepoints declared in `mshv_trace.h` by defining `CREATE_TRACE_POINTS` and including the header.

## Important APIs, Types, and Functions

There are no functions or data structures beyond tracepoint definition generation. The inclusion emits the tracepoint objects for events such as partition/VP lifecycle, hypercalls, memory mapping, ioeventfd assignment, dispatch, and GPA intercept handling.

## Control Flow

Build-time control flow is the important behavior: exactly one C file must define `CREATE_TRACE_POINTS` before including the trace header so the tracepoint storage is emitted once. Other files include `mshv_trace.h` normally and call `trace_mshv_*()`.

## State and Persistence Behavior

Tracepoint state is managed by the kernel tracing subsystem. This file contributes static tracepoint definitions that persist while the module is loaded.

## Dependencies and Integration Points

It depends directly on `mshv_trace.h` and indirectly on Linux tracepoint infrastructure and Hyper-V types used in event prototypes.

## Risks and Edge Cases

Adding another `CREATE_TRACE_POINTS` inclusion would cause duplicate definitions. Removing this file would leave callers with declarations but no tracepoint storage. It has no runtime error handling.

## Test Signals

Build and load the module with tracing enabled, confirm `/sys/kernel/tracing/events/mshv/*` entries exist, enable representative events, and verify lifecycle/ioctl paths emit records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.h -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.h

## Purpose

`mshv_trace.h` declares the Linux tracepoints for the MSHV root driver. The events provide low-overhead observability for partition/VP lifecycle, hypercalls, VP dispatch, IRQ routing, memory mapping, eventfd registration, wait states, and GPA intercept handling.

## Important APIs, Types, and Functions

- Lifecycle events: `mshv_create_partition`, `mshv_partition_release`, `mshv_destroy_partition`, `mshv_create_vp`, `mshv_vp_release`.
- Hypercall events: create/initialize/finalize/delete partition, withdraw memory, map VP state page, dispatch VP.
- Run-loop events: `mshv_run_vp_entry`, `mshv_run_vp_exit`, explicit suspend clear, guest-mode work, wait-for-kick.
- Configuration events: routing table update, user memory map, ioeventfd assign/deassign.
- Fault event: `mshv_handle_gpa_intercept` logs partition, VP, GFN, access type, and handled status.

## Control Flow

Implementation files call generated `trace_mshv_*()` helpers at important transitions. The header sets `TRACE_SYSTEM mshv`, defines include path/file metadata, and ends with `trace/define_trace.h` outside the include guard as required by kernel tracepoint conventions.

## State and Persistence Behavior

Tracepoints do not alter MSHV state. They snapshot scalar fields and pointers into ring buffers when enabled. Pointer fields such as routing table or eventfd addresses are diagnostic only and should not be treated as stable identifiers after object teardown.

## Dependencies and Integration Points

The header depends on `linux/tracepoint.h` and Hyper-V HVDK types. It is included by MSHV implementation files and instantiated by `mshv_trace.c`.

## Risks and Edge Cases

Trace format is a user-visible diagnostics contract; changing field names or print formats can affect tooling. Some events log raw pointers, which may be restricted by kernel pointer formatting policy. The GPA intercept event stores access type as a character in a `u8` field, which is intentional but easy to misread.

## Test Signals

Build with tracing, enable each event, exercise matching code paths, verify field decoding through `trace_pipe` or perf, and ensure tracepoint prototypes remain synchronized with call sites after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_vtl.h -->
# sources/distributed-fs/ceph-client/drivers/hv/mshv_vtl.h

## Purpose

`mshv_vtl.h` defines the userspace-visible run structure for MSHV VTL support. It packages cancellation state, return-action sizing, exit messages, CPU context, and return actions for VTL run operations.

## Important APIs, Types, and Functions

- `struct mshv_vtl_run` contains `cancel`, `vtl_ret_action_size`, padding, `exit_message[MSHV_MAX_RUN_MSG_SIZE]`, a union containing `struct mshv_vtl_cpu_context` or a 1024-byte reserved area, and `vtl_ret_actions[MSHV_MAX_RUN_MSG_SIZE]`.

## Control Flow

This header has no executable logic. VTL device code maps or copies this structure between kernel and userspace so userspace can observe exits, provide CPU context, request cancellation, and receive VTL return actions.

## State and Persistence Behavior

Instances are per run/mapping and are ABI state shared with userspace. The reserved 1024-byte union member preserves layout room for future CPU-context growth.

## Dependencies and Integration Points

It includes UAPI `linux/mshv.h` for `MSHV_MAX_RUN_MSG_SIZE` and `mshv_vtl_cpu_context`, plus Linux integer types. It is consumed by VTL implementation files outside this subset.

## Risks and Edge Cases

Because this is syscall-note ABI layout, field order and sizes must remain stable. Padding/reserved fields should be zeroed/validated by implementation code. Consumers must honor `vtl_ret_action_size` bounds against `vtl_ret_actions`.

## Test Signals

ABI tests should assert `sizeof(struct mshv_vtl_run)`, field offsets, zero/reserved handling, max message/action bounds, and compatibility with existing userspace VTL tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/mshv_vtl.h -->
