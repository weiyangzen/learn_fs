# subset-b-005922 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h

## Purpose

`controller.h` is the public SSAM controller API for Microsoft Surface Aggregator Module clients. It sits above the raw Surface Serial Hub protocol and defines event payloads, request/response descriptors, synchronous request helpers, retry wrappers, and event notifier registration. Its main consumers are Surface platform drivers that need to issue EC commands or subscribe to EC-generated events without owning the packet transport implementation.

## Important APIs, types, and functions

Key types are `struct ssam_event`, `struct ssam_request`, `struct ssam_response`, `struct ssam_request_sync`, `struct ssam_request_spec`, `struct ssam_request_spec_md`, `struct ssam_notifier_block`, `struct ssam_event_registry`, `struct ssam_event_id`, and `struct ssam_event_notifier`. The API exports controller lookup/lifetime helpers (`ssam_get_controller()`, `ssam_client_bind()`, `ssam_controller_get()`/`put()`), synchronous request allocation/submission/waiting (`ssam_request_sync_alloc()`, `ssam_request_sync_submit()`, `ssam_request_do_sync*()`), request definition macros (`SSAM_DEFINE_SYNC_REQUEST_*` and `_MD_*`), retry macros, notifier registration, and direct event enable/disable calls.

## Control flow

Typical command flow builds an `ssam_request`, writes SSH command data with `ssam_request_write_data()`, submits through the controller, waits on `struct completion`, and validates the response length when a return value is expected. The generated macros produce small static wrapper functions for no-argument, write-only, read-only, and write/read commands; multi-device variants take `tid` and `iid` at call time. Event flow registers `ssam_event_notifier` objects; the controller enables EC events on first active registration, dispatches matching `ssam_event` instances by category/target/instance mask, and disables events on the last unregister.

## State and persistence behavior

The header itself holds no state, but it defines stateful contracts: request buffers must remain valid until completion/release, `ssam_request_sync.status` becomes authoritative after `ssam_request_sync_wait()`, response length is written by the transport, notifier lists and event usage counts live in the controller, and event enablement persists in the EC until disabled or reset. `ssam_controller_statelock()`/`stateunlock()` expose controller state serialization to clients that need coordinated setup/teardown.

## Dependencies and integration points

It depends on completions, device model types, `linux/types.h`, and `serial_hub.h` for `ssh_request`, `ssam_span`, target IDs, and categories. Integration points are Surface client drivers, the SSAM bus in `device.h`, the lower packet/request transport, and EC command registries (`SSAM_EVENT_REGISTRY_SAM`, `KIP`, and `REG`).

## Risks and test signals

Risks center on lifetime and protocol shape: using stack request buffers after failed submission can deadlock in `ssam_request_sync_wait()`, response-size mismatches are treated as `-EIO`, unsequenced requests must not request responses, notifier callbacks can stop traversal, and hotplug/removal races can make EC communication time out. Tests should compile macro-generated wrappers, exercise sync success/error/timeout paths, verify response-length rejection, register multiple observers and active notifiers, and validate event enable/disable reference counting against controller traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h

## Purpose

`device.h` defines the SSAM bus and client-device interface. It lets non-ACPI/non-platform Surface Aggregator clients appear as Linux driver-model devices with stable SSAM UIDs, match tables, driver callbacks, child-device registration, request helper macros, and notifier wrappers. It is the main bridge between the controller-level command API and individual Surface subsystem drivers.

## Important APIs, types, and functions

Core identifiers are `enum ssam_device_domain`, `enum ssam_virtual_tc`, and `struct ssam_device_uid`. `SSAM_DEVICE()`, `SSAM_VDEV()`, and `SSAM_SDEV()` build match table entries with `SSAM_MATCH_TARGET`, `SSAM_MATCH_INSTANCE`, and `SSAM_MATCH_FUNCTION` derived from wildcard values. `struct ssam_device` embeds `struct device`, controller pointer, UID, and flags. `struct ssam_device_driver` wraps `device_driver`, a match table, `probe`, and `remove`. Helpers cover type conversion, matching, allocation/add/remove, refcounting, driver data, driver registration, firmware-node child registration, client-device request macros (`SSAM_DEFINE_SYNC_REQUEST_CL_*`), and device-scoped notifier register/unregister.

## Control flow

Firmware-described or virtual clients are allocated with a controller and UID, added to the SSAM bus, matched against driver tables, then probed via `ssam_device_driver`. Client request macros reuse controller multi-device request wrappers but fill target and instance IDs from `sdev->uid`. Child registration walks firmware nodes below a parent and instantiates SSAM children. Notifier registration first checks whether the device is hot-removed and then delegates to controller notifier registration.

## State and persistence behavior

Device lifetime follows the embedded `struct device` refcount. The `ctrl` pointer binds all client communication to one controller. The `flags` word stores hot-removal state; once `SSAM_DEVICE_HOT_REMOVED_BIT` is set, drivers should avoid EC traffic because it may time out. Driver data persists in the normal `dev_get_drvdata()` slot.

## Dependencies and integration points

The header depends on the Linux device model, module tables, firmware properties, and `controller.h`. It integrates with `CONFIG_SURFACE_AGGREGATOR_BUS`, module driver registration, firmware-node child enumeration, controller request APIs, and controller notifiers.

## Risks and test signals

Risks include invalid wildcard use in `SSAM_DEVICE()` arguments, stale controller references, assuming `is_ssam_device()` works when the bus is disabled, communication after hot removal, and mismatched target/category/function IDs that silently prevent binding. Tests should cover match-table wildcard behavior, bus-disabled stubs, device add/remove and refcount lifetimes, child enumeration from firmware nodes, client request macro expansion, and notifier behavior before and after `ssam_device_mark_hot_removed()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h

## Purpose

`serial_hub.h` defines the low-level Surface Serial Hub protocol used below SSAM controller requests. It describes SSH frame and command wire formats, payload sizing and offsets, CRC calculation, request/event ID encoding, known target IDs/categories, packet transport state, and request transport state.

## Important APIs, types, and functions

Important wire types are `struct ssh_frame` and `struct ssh_command`, both packed and size-asserted. Sizing macros include `SSH_FRAME_MAX_PAYLOAD_SIZE`, `SSH_COMMAND_MAX_PAYLOAD_SIZE`, `SSH_MSG_LEN_BASE`, `SSH_MESSAGE_LENGTH()`, and `SSH_COMMAND_MESSAGE_LENGTH()`. Offset helpers locate fields in raw messages. `ssh_crc()` wraps `crc_itu_t()`. Request ID helpers classify event IDs and skip reserved event IDs. Transport state is represented by `struct ssam_span`, `struct ssh_packet`, `struct ssh_packet_ops`, `struct ssh_request`, and `struct ssh_request_ops`; helpers manage references and attach caller-owned buffers.

## Control flow

Outbound control starts with a raw message buffer containing SYN, frame, frame CRC, optional command payload, and payload CRC. A packet is queued with priority derived from base class and retry count. Sequenced data packets require ACK tracking; request transport wraps packets and waits for matching command responses by request ID. Inbound command frames can be classified as responses or EC events via reserved request IDs, then delivered to request completion or notifier logic above.

## State and persistence behavior

The header defines volatile transport state rather than persistent storage. `ssh_packet.state` and `ssh_request.state` track locked, queued, pending, transmitting, transmitted, acknowledged/response-received, canceled, and completed phases. Timestamps support timeout handling. Buffers are non-owned spans; callers must preserve raw data until release callbacks fire. References are managed by `kref` through packet/request get/put helpers.

## Dependencies and integration points

It depends on CRC-ITU-T, krefs, ktime, lists, and core integer types. It feeds `controller.h` request construction, the SSAM serial transport driver, Surface EC event dispatch, and target/category constants used by Surface client drivers.

## Risks and test signals

Protocol layout mistakes are high impact because structures are packed hardware/firmware ABI. Risks include stale caller-owned buffers, incorrect CRC coverage, event/request ID overlap, invalid target IDs, retry priority overflow beyond four low bits, and missing barriers around transport state. Tests should validate exact wire sizes/offsets, CRC generation, request ID rollover around reserved event IDs, target ID validity, packet reference release ordering, ACK/NAK handling, timeout paths, and event versus response dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/suspend.h -->
# sources/distributed-fs/ceph-client/include/linux/suspend.h

## Purpose

`suspend.h` is the central kernel header for system sleep, suspend-to-idle, and hibernation interfaces. It defines sleep-state constants, platform callback contracts, PM notification IDs, wakeup helpers, hibernation image helpers, and config-dependent stubs so callers can compile across PM configurations.

## Important APIs, types, and functions

Key types are `suspend_state_t`, `struct platform_suspend_ops`, `struct platform_s2idle_ops`, `struct pbe`, and `struct platform_hibernation_ops`. Public APIs include `suspend_set_ops()`, `pm_suspend()`, `s2idle_set_ops()`, `s2idle_wake()`, `hibernate()`, `hibernation_set_ops()`, `register_nosave_region()`, `swsusp_arch_suspend()`/`resume()`, PM notifier registration, wakeup event helpers, `lock_system_sleep()`, `pm_sleep_transition_in_progress()`, debug printing macros, autosleep work queuing, and suspend failure recording.

## Control flow

Suspend flow validates a target state, calls platform `begin`, suspends devices, invokes `prepare`/`prepare_late`, disables nonboot CPUs and IRQs as required, enters the platform state, then unwinds through `wake`, `finish`, device resume, and `end` or `recover`. S2idle uses a smaller callback set and a global `s2idle_state` checked by idle code. Hibernation flow shrinks/freezes, snapshots memory, writes or restores an image, and calls architecture/platform hooks across snapshot, enter, leave, and restore phases.

## State and persistence behavior

Global PM state includes `pm_suspend_target_state`, current/default mem sleep state, `pm_suspend_global_flags`, `s2idle_state`, wakeup counters, debug flags, hibernation hardware signature, and `restore_pblist`. Flags record whether firmware participates or platform power state remains under kernel control. Hibernation persists a memory image to storage; suspend state is mostly transient but hardware sleep state outlives CPU execution.

## Dependencies and integration points

The header depends on swap, notifiers, init, PM, MM, freezer, and arch errno. It integrates with device power management, freezer, CPU hotplug, wakeup source tracking, sysfs `/sys/power`, hibernation snapshot code, architecture suspend/resume code, consoles, VT, and PM debug.

## Risks and test signals

Risks include callback ordering violations, missing unwind callbacks after partial failures, using PM helpers when their config stubs return success/no-op, wakeup races, storage I/O under restricted GFP masks, and firmware/kernel ownership confusion. Tests should exercise suspend success and failure injection at each stage, s2idle wake behavior, hibernation snapshot/restore, PM notifier ordering, wakeup-count races, debug output gating, and builds with `CONFIG_SUSPEND`, `CONFIG_HIBERNATION`, and `CONFIG_PM_SLEEP` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/svga.h -->
# sources/distributed-fs/ceph-client/include/linux/svga.h

## Purpose

`svga.h` provides helper structures and routines for legacy Super VGA framebuffer drivers. It abstracts VGA register bitfield programming, default register sets, tiled text-mode operations, PLL computation, mode timing validation/programming, and framebuffer format matching.

## Important APIs, types, and functions

`struct vga_regset` describes a register number and bit range; `VGA_REGSET_END` terminates register lists. `struct svga_fb_format` maps `fb_var_screeninfo` color fields to fixed framebuffer properties. `struct svga_timing_regs` groups horizontal and vertical timing register sets. `struct svga_pll` constrains clock synthesis parameters. Inline helpers are `svga_wattr()`, `svga_wseq_mask()`, `svga_wcrt_mask()`, and `svga_primary_device()`. External helpers cover multi-register writes, default VGA text/graphics setup, tile acceleration, capabilities, PLL search, timing checks, timing programming, and format matching.

## Control flow

Drivers select an fb mode, call format and timing validators, compute PLL values, write sequencer/CRT/attribute register bitfields through the helper lists, and then expose tile operations where hardware supports text acceleration. `svga_primary_device()` uses PCI command I/O enablement to infer whether the VGA device is primary.

## State and persistence behavior

The header itself is stateless; state is VGA register state and framebuffer configuration programmed into hardware. Register helpers perform read-modify-write operations, so callers must serialize concurrent register access.

## Dependencies and integration points

It depends on PCI, VGA I/O helpers, and framebuffer types. It integrates with legacy fbdev drivers, PCI VGA probing, and `video/vga.h` register access.

## Risks and test signals

Risks include off-by-one bit ranges in register sets, wrong sentinel placement, unsafe concurrent register writes, PLL values outside hardware limits, and format mismatches between var/fix screen info. Tests should validate register-list programming on emulated/real VGA hardware, mode timing acceptance/rejection, PLL results around boundary frequencies, primary-device detection, and tile operation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/svga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sw842.h -->
# sources/distributed-fs/ceph-client/include/linux/sw842.h

## Purpose

`sw842.h` declares the kernel software implementation interface for IBM 842 compression. It exposes compression and decompression functions plus the compressor work-memory size needed by callers.

## Important APIs, types, and functions

`SW842_MEM_COMPRESS` defines required compression workspace size. `sw842_compress()` takes source bytes, source length, destination buffer, in/out destination length, and caller-provided work memory. `sw842_decompress()` takes source compressed bytes, source length, destination buffer, and in/out destination length.

## Control flow

Callers allocate destination storage and compression workspace, pass maximum destination length by pointer, and receive actual output length or an errno. Decompression similarly consumes a bounded compressed stream and reports actual restored byte count.

## State and persistence behavior

No state is owned by this header. Compression state is temporary caller-owned workspace, and output persistence is limited to caller buffers.

## Dependencies and integration points

It relies on kernel integer typedefs and integrates with the software 842 compressor implementation and any subsystem selecting 842 as a compression backend, such as zram/powernv-related paths in kernels that enable it.

## Risks and test signals

Risks include undersized workspace, incorrect destination length handling, corrupt compressed input, and callers assuming in-place operation without implementation support. Tests should cover round trips for boundary sizes, insufficient destination buffers, malformed streams, zero-length input, and workspace allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sw842.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swab.h -->
# sources/distributed-fs/ceph-client/include/linux/swab.h

## Purpose

`swab.h` is the kernel-facing byte-swap convenience header. It re-exports UAPI byte/halfword swap primitives under shorter kernel names and adds array helpers for 16-, 32-, and 64-bit buffers.

## Important APIs, types, and functions

Macros map `swab16`, `swab32`, `swab64`, `swab`, `swahw32`, `swahb32`, pointer variants, and in-place variants to `__swab*` UAPI definitions. `swab16_array()`, `swab32_array()`, and `swab64_array()` walk word counts and call in-place swap helpers.

## Control flow

Array helpers perform a simple decrementing loop over typed pointers, swapping one element at a time. Scalar macros defer to compile-time or architecture-optimized implementations in `uapi/linux/swab.h`.

## State and persistence behavior

The array helpers mutate caller-provided buffers in place. There is no global state.

## Dependencies and integration points

It depends on UAPI swab definitions and kernel integer types. It integrates broadly with endian conversion code, binary parsers, filesystems, drivers, and protocol implementations that need explicit byte swapping.

## Risks and test signals

Risks are primarily caller-side: passing byte counts instead of word counts, unaligned typed pointers on strict architectures, double-swapping data, or using in-place helpers on read-only memory. Tests should validate scalar and array swaps for representative patterns, odd word counts, alignment-sensitive callers, and compile-time constant folding where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait.h -->
# sources/distributed-fs/ceph-client/include/linux/swait.h

## Purpose

`swait.h` defines simple wait queues, a restricted waitqueue variant designed for deterministic lock and IRQ behavior, especially under realtime constraints. It intentionally removes many regular waitqueue features to keep wakeups bounded and simple.

## Important APIs, types, and functions

`struct swait_queue_head` contains a raw spinlock and waiter list. `struct swait_queue` stores the task and list node. Initializer macros create queue heads and waiters, including lockdep-aware on-stack initialization. Core APIs include `swait_active()`, `swq_has_sleeper()`, `swake_up_one()`, `swake_up_all()`, `swake_up_locked()`, `prepare_to_swait_exclusive()`, `prepare_to_swait_event()`, `__finish_swait()`, and `finish_swait()`. Wait macros provide uninterruptible, interruptible, idle, and timeout-exclusive waits.

## Control flow

Waiters initialize a local `swait_queue`, call `prepare_to_swait_event()` in a loop, check the condition, schedule if unmet, and finish with `finish_swait()`. Wakers call one/all wake helpers. All sleepers are exclusive and wakeups target `TASK_NORMAL` semantics, avoiding mixed-state scans and custom callbacks.

## State and persistence behavior

Queue state is the protected task list plus each waiter's current task pointer. `swait_active()` is lockless and only safe with the documented locking or memory-barrier pairing. Timeout macros return remaining jiffies or interrupt status.

## Dependencies and integration points

It depends on lists, raw spinlocks, regular wait macros, current task access, and scheduler state constants. It integrates with RT-sensitive kernel subsystems that need bounded wakeup behavior.

## Risks and test signals

Risks include missed wakeups when using `swait_active()` without barriers, misuse where nonexclusive or custom wake behavior is required, calling `swake_up_all()` from IRQ-disabled contexts contrary to design, and condition expressions with side effects. Tests should cover one/all wakeups, interruptible return paths, timeout return values, idle waits not contributing to load, lockdep initialization, and memory-order patterns around lockless active checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait_api.h -->
# sources/distributed-fs/ceph-client/include/linux/swait_api.h

## Purpose

`swait_api.h` is a one-line compatibility or layering header that includes `linux/swait.h`. It provides an alternate include name for code that wants the simple waitqueue API without depending directly on the main header name.

## Important APIs, types, and functions

It exports no independent symbols. All visible API comes from `swait.h`: simple waitqueue heads, wait entries, wake functions, prepare/finish helpers, and wait-event macros.

## Control flow

There is no local control flow. Inclusion delegates preprocessing entirely to `swait.h`.

## State and persistence behavior

There is no local state. State behavior is exactly that of `swait.h` consumers.

## Dependencies and integration points

It depends solely on `linux/swait.h` and integrates as an include shim for kernel files that use simple wait queues.

## Risks and test signals

Risk is minimal, but duplicate or inconsistent include paths can hide dependency mistakes. Tests are compile-time only: ensure consumers including `swait_api.h` receive the same declarations as `swait.h` and do not rely on this header for any extra definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap.h -->
# sources/distributed-fs/ceph-client/include/linux/swap.h

## Purpose

`swap.h` is the central VM header for swap space, reclaim, LRU handling, swapcache accounting, and memory-cgroup swap charging. It defines swap flags, special swap entry type allocation, swap area metadata, reclaim helpers, and configuration stubs.

## Important APIs, types, and functions

The header defines user-visible swap flags, `MAX_SWAPFILES` layout with reserved pseudo-types for hwpoison, migration, device-private memory, and PTE markers, `union swap_header`, `struct reclaim_state`, `struct swap_extent`, `struct swap_sequential_cluster`, and `struct swap_info_struct`. APIs include reclaimed-page accounting, workingset hooks, LRU add/drain and access helpers, reclaim entry points, swap extent activation, swapcache freeing, swap device lookup/refcounting, swap counts, hibernation swap slots, memcg swappiness/charging/uncharge helpers, swap throttling, and managed-zone iteration.

## Control flow

Swap activation parses headers and extents into `swap_info_struct`, then allocation uses cluster lists, sequential cluster hints, and per-device locks. Reclaim paths isolate folios, may allocate swap entries, add to swapcache, write pages, free swapcache later, and account reclaimed pages through `current->reclaim_state`. Memcg paths charge and uncharge swap entries when swap is enabled and memory cgroups are active.

## State and persistence behavior

Persistent disk state is the swap header and swap area contents. In-memory state lives in `swap_info_struct`: flags, priority, extent tree, cluster lists, zeromap, total/free page counters, locks, discard/reclaim work, and percpu user references. Global counters include `nr_swap_pages`, `total_swap_pages`, `nr_rotate_swap`, and `lru_disable_count`.

## Dependencies and integration points

It depends on spinlocks, MM zones, memcg, scheduler, filesystem/pagemap, page flags, mempolicy UAPI, and architecture page definitions. It integrates with vmscan, swapfile, shmem, hibernation, HMM/device-private memory, memory failure, cgroups, block discard, LRU generation, and sysinfo reporting.

## Risks and test signals

Risks include special swap type overlap, lock ordering between `swap_lock` and per-device locks, races during swapoff, bad cluster accounting, THP swap order handling, memcg disabled stubs masking behavior, and accidental I/O under no-IO reclaim contexts. Tests should cover swapon/swapoff, full-swap behavior, discard modes, swapcache counts, migration/device-private/hwpoison entries, memcg charging, hibernation slots, CONFIG_SWAP disabled builds, and stress with concurrent reclaim and swapoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h

## Purpose

`swap_cgroup.h` declares the swap-cgroup metadata interface used to associate swap entries with memory cgroup IDs. It provides real declarations when both memory cgroups and swap are enabled and no-op stubs otherwise.

## Important APIs, types, and functions

The active API includes `swap_cgroup_record()`, `swap_cgroup_clear()`, `lookup_swap_cgroup_id()`, `swap_cgroup_swapon()`, and `swap_cgroup_swapoff()`. These functions record cgroup ownership for folio swap entries, clear ownership for ranges, query stored IDs, and allocate/free per-swap-type metadata during swapon/swapoff.

## Control flow

During swapout, VM/memcg code records the cgroup ID for the allocated swap entry. During swapin or swap freeing, the entry can be looked up or cleared. Swapon allocates metadata sized by max pages; swapoff tears it down.

## State and persistence behavior

The state is in-memory metadata keyed by swap type and offset. It does not persist on disk; after reboot or swapoff, ownership records disappear. Stub builds drop all accounting and return zero/success.

## Dependencies and integration points

It depends on `swap.h` and, when enabled, memcg and swap internals. It integrates with memcg charging/uncharging, swap activation/deactivation, and reclaim paths.

## Risks and test signals

Risks include losing accounting when CONFIG combinations disable the implementation, stale IDs after swapoff races, clearing too few or too many entries, and mismatches between folio size and entry count. Tests should cover swapon metadata allocation, record/lookup/clear for multi-page folios, memcg disabled stubs, swapoff cleanup, and concurrent reclaim/swapin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapfile.h -->
# sources/distributed-fs/ceph-client/include/linux/swapfile.h

## Purpose

`swapfile.h` exposes architecture and generic limits for swapfile sizing and a flag describing whether migration swap entries can preserve accessed/dirty bits. It is a narrow interface between generic swap code and architecture-specific swap encoding limits.

## Important APIs, types, and functions

It declares `generic_max_swapfile_size()`, `arch_max_swapfile_size()`, global `swapfile_maximum_size`, and global `swap_migration_ad_supported`.

## Control flow

Swap activation consults generic and architecture maximum size calculations to cap usable swap offsets. Migration-entry helpers in `swapops.h` query `swap_migration_ad_supported` to decide whether to encode A/D bits in swap offsets.

## State and persistence behavior

`swapfile_maximum_size` and `swap_migration_ad_supported` are global kernel state initialized by swap/architecture setup. They persist for the boot lifetime and govern later swapon and migration-entry behavior.

## Dependencies and integration points

It integrates with `swap.h`, `swapops.h`, architecture page-table/swap encoding, and `mm/swapfile.c`.

## Risks and test signals

Risks include overestimating maximum offsets on architectures with small PTE swap fields, inconsistent A/D-bit support versus actual encoding capacity, and regressions for 32-bit pgoff architectures. Tests should validate maximum swapfile sizes across page sizes and architectures, migration entries with and without A/D preservation, and swapon rejection/truncation around limit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapops.h -->
# sources/distributed-fs/ceph-client/include/linux/swapops.h

## Purpose

`swapops.h` defines architecture-independent manipulation of `swp_entry_t` values and conversion to page-table entries. It also builds special swap entries for device-private memory, migration, hardware poison, and PTE markers.

## Important APIs, types, and functions

Core macros are `SWP_TYPE_SHIFT`, `SWP_OFFSET_MASK`, `SWP_PFN_BITS`, `SWP_PFN_MASK`, migration A/D bit masks, and PTE marker bits. Functions include `pte_swp_clear_flags()`, `swp_entry()`, `swp_type()`, `swp_offset()`, `swp_entry_to_pte()`, radix/XArray conversions, device-private entry builders, migration entry builders and A/D marking, `migration_entry_wait*()`, `make_hwpoison_entry()`, `is_hwpoison_entry()`, `make_pte_marker_entry()`, `make_poisoned_swp_entry()`, `make_guard_swp_entry()`, THP PMD migration helpers, and `swp_entry_to_pmd()`.

## Control flow

VM code creates swap entries from type/offset, converts them into architecture PTE/PMD encodings, and later extracts type/offset for fault handling. Migration and device-private faults recognize special types and wait, migrate back, signal poison, or enforce userfault/guard semantics.

## State and persistence behavior

Swap entries persist inside page tables, swapcache XArrays, and shadow entries while mappings are absent. PTE markers intentionally persist metadata in otherwise-none PTE slots. No global state is owned here, except reading `swap_migration_ad_supported`.

## Dependencies and integration points

It depends on MMU builds, radix/XArray value storage, architecture `__swp_entry` conversion helpers, `swapfile.h`, migration, memory failure, device-private memory, userfaultfd write-protect, and THP migration.

## Risks and test signals

Risks include type/offset bit overlap, insufficient PFN bits, losing soft-dirty/UFFD/exclusive flags incorrectly, migration A/D encoding on unsupported architectures, and special entries escaping paths that expect real swap. Tests should cover encode/decode round trips, radix conversion, all special entry types, migration waits, PTE marker faults, THP migration stubs, and builds with `CONFIG_MMU`, `CONFIG_SWAP`, `CONFIG_MIGRATION`, and `CONFIG_MEMORY_FAILURE` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swiotlb.h -->
# sources/distributed-fs/ceph-client/include/linux/swiotlb.h

## Purpose

`swiotlb.h` declares the Software I/O TLB bounce-buffer interface used by DMA mapping code when devices cannot directly address memory or when restricted/encrypted DMA pools are required. It describes pool layout, initialization, mapping, unmapping, sync, and restricted allocation helpers.

## Important APIs, types, and functions

Constants define flags, segment size, slab size, and default pool size. `struct io_tlb_pool` describes one pool, including physical range, virtual address, slots, areas, dynamic list membership, and transient status. `struct io_tlb_mem` describes per-device/default allocator state, dynamic growth, limits, locks, work, and debug counters. APIs include early/late initialization, memory attribute updates, device init, pool lookup, force-bounce checks, map/unmap/sync helpers, allocation-state queries, default range queries, info printing, and restricted-pool `swiotlb_alloc()`/`free()`.

## Control flow

DMA mapping code maps a physical buffer through `swiotlb_tbl_map_single()`/`swiotlb_map()` when bouncing is needed. Later unmap and sync helpers first call `swiotlb_find_pool()`; if the address is a bounce buffer, they copy/sync and free slots. Dynamic configurations can find pools through `__swiotlb_find_pool()` after checking `dev->dma_uses_io_tlb` with a read barrier.

## State and persistence behavior

Pool state persists for the boot lifetime or until dynamic pool teardown. Slot and area metadata track allocation. Device state lives in `dev->dma_io_tlb_mem` and `dev->dma_uses_io_tlb`. Debug counters track current and high-water usage. Bounce buffers contain transient copies of DMA data.

## Dependencies and integration points

It depends on device DMA metadata, DMA direction enums, init, spinlocks, workqueues, RCU/list support for dynamic pools, and optional debugfs/restricted DMA pool configs. It integrates with DMA direct/IOMMU paths, memory encryption, confidential computing, and restricted DMA pool allocation.

## Risks and test signals

Risks include missing syncs causing data corruption, pool lookup races without barriers, wrong direction handling, insufficient pool size, dynamic pool lifetime bugs, restricted-pool null dereferences, and assuming SWIOTLB is active in stub builds. Tests should cover mapping/unmapping in all DMA directions, forced bounce, addressing-limited devices, dynamic pool growth/free, encrypted memory remapping, restricted pool allocation, debugfs counters, and CONFIG_SWIOTLB disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swiotlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/switchtec.h -->
# sources/distributed-fs/ceph-client/include/linux/switchtec.h

## Purpose

`switchtec.h` defines register layouts and core device state for the Microsemi/Microchip Switchtec PCIe switch driver. It covers management RPC registers, software events, system/flash information, NTB registers, partition config, PFF CSR windows, DMA MRPC output, and the driver’s top-level `switchtec_dev`.

## Important APIs, types, and functions

Important constants include MRPC payload size, GAS region offsets, event bits, DMA MRPC enable, MRPC command IDs, NTB control bits, and event masks. Register structs include `mrpc_regs`, `sw_event_regs`, generation-specific `sys_info_regs_*`, `flash_info_regs_*`, `ntb_info_regs`, `part_cfg_regs`, `ntb_ctrl_regs`, `ntb_dbmsg_regs`, and `pff_csr_regs`, mostly packed to match MMIO layouts. `struct switchtec_dev` binds the PCI device, character device, generation, partition state, MMIO pointers, MRPC queue/work/timer state, event waitqueue/counters, link notifier, NTB state, and DMA MRPC buffer. `to_stdev()` converts from embedded `struct device`.

## Control flow

The driver maps GAS regions, initializes typed MMIO pointers, queues MRPC commands under `mrpc_mutex`, drives command work and timeout handling, receives event/interrupt indications from software or partition event registers, wakes waiters, and exposes management through a character device and optional NTB integration.

## State and persistence behavior

Hardware state persists in PCIe switch MMIO registers and flash partitions. Software state includes queue membership, `mrpc_busy`, delayed timeout work, `alive`, event counters, link event counts, and DMA buffer ownership. Flash/sys-info structs represent persistent firmware/configuration partitions.

## Dependencies and integration points

It depends on PCI and character-device infrastructure. It integrates with the Switchtec PCI driver, userspace management char device, DMA MRPC support, interrupt/event handling, and Switchtec NTB support.

## Risks and test signals

Risks include packed layout drift from hardware documentation, endian/MMIO access mistakes, MRPC queue races, timeout cleanup while device removal is in progress, generation-specific sys/flash layout confusion, and event bit clearing mistakes. Tests should validate structure offsets/sizes, MRPC success/error/timeout/interrupted paths, event masking/clearing, Gen3/Gen4/Gen5 identification, DMA MRPC, char-device lifetime, hot removal, and NTB register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/switchtec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h

## Purpose

`sxgbe_platform.h` declares platform data for Samsung SXGBE Ethernet MAC support. It lets board or firmware glue describe PHY, bus, checksum, DMA, queue, and clock-related capabilities to the SXGBE driver.

## Important APIs, types, and functions

The file defines `struct sxgbe_mdio_bus_data` for MDIO IRQ/mask/probe behavior, `struct sxgbe_dma_cfg` for programmable burst and fixed/mixed burst settings, and `struct sxgbe_plat_data` for common MAC platform configuration: bus ID, PHY address/interface, MDIO bus data, DMA config, checksum offload, enhanced descriptor selection, force threshold/store-forward flags, maximum MTU, multicast/unicast filter counts, queue counts, and clock pointers.

## Control flow

Platform setup fills the data structure before driver probe. The driver reads it to create the MDIO bus, bind the PHY, configure DMA burst behavior, enable descriptor/checksum features, size queues and filters, and manage clocks.

## State and persistence behavior

The structures are caller-owned static or probe-time configuration. Runtime persistence is in the SXGBE driver state and hardware registers programmed from these fields. Clock pointers must remain valid according to device-driver lifetime rules.

## Dependencies and integration points

It depends on PHY interface definitions, netdevice/MDIO concepts, and common clock framework types. It integrates with platform/OF board code and the SXGBE network driver.

## Risks and test signals

Risks include mismatched PHY interface/address, bad queue counts, invalid MTU, enabling unsupported offloads, and clock lifetime/enable sequencing issues. Tests should cover probe with platform data and DT-derived data, PHY link up/down, DMA under load, checksum offload validation, multiple queue configurations, MTU limits, and suspend/resume clock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_core.h -->
# sources/distributed-fs/ceph-client/include/linux/sync_core.h

## Purpose

`sync_core.h` declares `sync_core_before_usermode()`, an architecture-sensitive helper used to ensure core instruction synchronization before returning to user mode after code or execution-context changes.

## Important APIs, types, and functions

The single exported API is `sync_core_before_usermode()`. Implementations are architecture-specific or generic depending on the kernel tree.

## Control flow

Kernel code calls the helper before user return when it needs guarantees that subsequent user execution observes updated instruction stream or CPU context state. The actual synchronization sequence is supplied elsewhere.

## State and persistence behavior

The header owns no state. The effect is transient CPU pipeline/core synchronization; it does not persist except by ordering execution.

## Dependencies and integration points

It integrates with architecture entry/exit paths, text patching or instruction-modifying mechanisms, signal/return-to-user flows, and CPU synchronization barriers.

## Risks and test signals

Risks include missing calls after modifying executable user-visible state, overuse on hot paths, and architecture implementations that do not provide sufficient serialization. Tests should cover architecture build coverage, self-modifying/JIT code scenarios where applicable, signal/return paths, and tracing or static analysis that confirms required callers invoke the helper before usermode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_file.h -->
# sources/distributed-fs/ceph-client/include/linux/sync_file.h

## Purpose

`sync_file.h` defines the userspace file descriptor wrapper for DMA fences. It lets drivers export one or merged fences as pollable files and lets userspace import a fence from an fd.

## Important APIs, types, and functions

`struct sync_file` contains the backing `struct file`, optional debugfs list node, waitqueue, flags, a `struct dma_fence *`, callback storage, and a user-provided merged-fence name buffer. `POLL_ENABLED` marks active polling. APIs are `sync_file_create()`, `sync_file_get_fence()`, and `sync_file_get_name()`.

## Control flow

A driver creates a sync file from a DMA fence, returns its fd to userspace, and userspace polls or passes it elsewhere. Poll setup attaches a fence callback that wakes the waitqueue when signaled. Importers call `sync_file_get_fence()` to resolve an fd back to a referenced fence.

## State and persistence behavior

The sync file persists as long as the file descriptor/reference exists. The fence reference tracks asynchronous GPU/display/DMA completion. Debug builds can list active sync files. Poll state is stored in `flags` and callback fields.

## Dependencies and integration points

It depends on file descriptors, waitqueues, debugfs optionally, and `dma_fence`. It integrates with DRM, DMA-BUF, display, GPU, camera, and media synchronization APIs.

## Risks and test signals

Risks include fence reference leaks, use-after-free around callbacks, polling after fence signal, incorrect merged names, and accepting unrelated fds. Tests should create/signaled/unsignaled fences, poll and wake behavior, fd import/export, release races, debugfs listing, and invalid fd handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sync_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/synclink.h -->
# sources/distributed-fs/ceph-client/include/linux/synclink.h

## Purpose

`synclink.h` is the kernel-side wrapper for SyncLink multiprotocol serial adapter ioctl definitions. It includes the UAPI header and adds 32-bit compatibility structures/ioctls on 64-bit kernels.

## Important APIs, types, and functions

When `CONFIG_COMPAT` is enabled, `struct MGSL_PARAMS32` mirrors UAPI `MGSL_PARAMS` with `compat_ulong_t` for fields whose size differs between 32-bit userspace and 64-bit kernel. `MGSL_IOCSPARAMS32` and `MGSL_IOCGPARAMS32` define compat ioctl numbers for setting and getting parameters.

## Control flow

Compat ioctl handlers can receive the 32-bit structure, translate it to the native structure, and call the normal SyncLink configuration path. Without compat, this header only re-exports UAPI definitions.

## State and persistence behavior

The header owns no state. Adapter state is changed by driver ioctl handling based on translated parameters.

## Dependencies and integration points

It depends on `uapi/linux/synclink.h` and, under compat, `linux/compat.h`. It integrates with SyncLink serial drivers and compat ioctl dispatch.

## Risks and test signals

Risks include structure layout drift versus UAPI, missing translation of widened fields, and ioctl number mismatch. Tests should validate 32-bit userspace ioctl set/get on 64-bit kernels, native ioctl compatibility, field round trips, and builds with `CONFIG_COMPAT` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/synclink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys.h -->
# sources/distributed-fs/ceph-client/include/linux/sys.h

## Purpose

`sys.h` is a legacy placeholder header. Its comments state it is no longer used or needed, retaining only disabled historical syscall alias notes.

## Important APIs, types, and functions

There are no active exported APIs. A `#ifdef notdef` block documents obsolete syscall aliases such as old wait, uname, stat, signal, and signal-mask variants, but they are not compiled.

## Control flow

There is no runtime or compile-time control flow beyond the include guard and inactive block.

## State and persistence behavior

No state exists.

## Dependencies and integration points

It has no includes and should not be a dependency for new code. Its only integration value is preserving a historical include path.

## Risks and test signals

Risk is accidental reliance by new code on an empty legacy header or re-enabling obsolete aliases. Tests are limited to compile checks that removing includes from consumers has no effect and that no active symbols are expected from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_info.h -->
# sources/distributed-fs/ceph-client/include/linux/sys_info.h

## Purpose

`sys_info.h` declares a kernel diagnostic interface for dumping selected system information, with bitmask flags for tasks, memory, timers, locks, ftrace, panic console replay, all backtraces, and blocked tasks.

## Important APIs, types, and functions

Flags are `SYS_INFO_TASKS`, `SYS_INFO_MEM`, `SYS_INFO_TIMERS`, `SYS_INFO_LOCKS`, `SYS_INFO_FTRACE`, `SYS_INFO_PANIC_CONSOLE_REPLAY`, `SYS_INFO_ALL_BT`, and `SYS_INFO_BLOCKED_TASKS`. APIs are `sys_info()`, `sys_info_parse_param()`, and, with sysctl enabled, `sysctl_sys_info_handler()`.

## Control flow

Callers pass a mask to `sys_info()` to emit selected diagnostic sections. Boot/sysctl parsing can convert string parameters into masks, and sysctl handling can trigger or configure dumps through `/proc/sys` plumbing.

## State and persistence behavior

The header owns no state. State is diagnostic output and any sysctl-side configuration stored elsewhere. Panic console replay is explicitly panic-only because it requires special handling.

## Dependencies and integration points

It depends on `sysctl.h` and integrates with kernel diagnostics, panic paths, sysctl, task/memory/timer/lock/ftrace subsystems, and blocked-task reporting.

## Risks and test signals

Risks include excessive output in panic contexts, unsafe diagnostics while locks are compromised, parsing invalid masks, and triggering console replay outside panic. Tests should validate mask parsing, individual section output, sysctl handler read/write behavior, panic-only constraints, and builds without CONFIG_SYSCTL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_soc.h -->
# sources/distributed-fs/ceph-client/include/linux/sys_soc.h

## Purpose

`sys_soc.h` declares the SoC bus registration and matching API. It lets platform code register SoC identity attributes as a device and lets drivers match against machine/family/revision/SoC IDs.

## Important APIs, types, and functions

`struct soc_device_attribute` stores machine, family, revision, serial number, SoC ID, opaque data, and an optional custom attribute group. APIs include `soc_device_register()`, `soc_device_unregister()`, `soc_device_to_device()`, `soc_attr_read_machine()`, and `soc_device_match()` when `CONFIG_SOC_BUS` is enabled.

## Control flow

Platform code allocates and fills attributes, registers a SoC device, and exposes attributes through the driver model/sysfs. Consumers call `soc_device_match()` with a table of desired attributes and receive the matching entry or NULL. Unregister tears down the device.

## State and persistence behavior

Registered SoC devices persist in the device model until explicitly unregistered. Attribute strings must remain valid for that lifetime. Match data is static caller-owned data.

## Dependencies and integration points

It depends on the Linux device model and integrates with platform/SoC initialization, sysfs SoC identification, DMI/firmware model reads, and drivers needing SoC-specific quirks.

## Risks and test signals

Risks include attribute lifetime bugs, overly broad matches, missing CONFIG_SOC_BUS stubs returning NULL, and custom attribute group misuse. Tests should register/unregister SoC devices, verify sysfs attributes, match exact and wildcard-like tables, read machine attributes, and build with SOC_BUS disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h -->
# sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h

## Purpose

`syscall_user_dispatch.h` declares the kernel control interface for syscall user dispatch, a generic-entry feature that can redirect selected syscalls to userspace emulation based on configured address ranges and a userspace selector byte.

## Important APIs, types, and functions

When `CONFIG_GENERIC_ENTRY` is enabled, APIs are `set_syscall_user_dispatch()`, `clear_syscall_work_syscall_user_dispatch()`, `syscall_user_dispatch_get_config()`, and `syscall_user_dispatch_set_config()`. Disabled builds return `-EINVAL` or no-op. It includes `struct syscall_user_dispatch` from the companion types header.

## Control flow

Configuration paths set mode, allowed offset/length, and selector address on a task. Entry code checks syscall work flags and dispatch configuration before executing a syscall; clearing the work bit disables checks for the task. Get/set config functions support ptrace/prctl-style inspection and update.

## State and persistence behavior

Per-task state lives in thread/task structures through `struct syscall_user_dispatch`. The selector is a userspace pointer and must be accessed carefully. Configuration persists until changed, cleared, exec/reset by owning logic, or task exit.

## Dependencies and integration points

It depends on thread-info syscall work helpers, task structs, user pointers, and `syscall_user_dispatch_types.h`. It integrates with generic syscall entry, prctl/ptrace config paths, compatibility layers, and userspace emulators such as Wine-like runtimes.

## Risks and test signals

Risks include unsafe selector access, wrong allowed-region boundaries, failing to clear syscall work, ptrace size validation errors, and inconsistent behavior on architectures without generic entry. Tests should cover enable/disable, allowed and dispatched address ranges, selector toggling, get/set config ABI sizes, fork/exec semantics, signal/syscall restart interactions, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h -->
# sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h

## Purpose

`syscall_user_dispatch_types.h` defines the per-task storage shape for syscall user dispatch. It is separated from the API header so low-level task/thread structures can include the type without pulling in the full control API.

## Important APIs, types, and functions

With `CONFIG_GENERIC_ENTRY`, `struct syscall_user_dispatch` contains a userspace `selector`, an allowed `offset`, allowed `len`, and `on_dispatch` recursion/dispatch-state flag. Without generic entry, the struct is empty.

## Control flow

The type is read by syscall entry code and written by configuration code declared in `syscall_user_dispatch.h`. `on_dispatch` helps distinguish active dispatch handling from normal syscall execution.

## State and persistence behavior

The struct is per-task state. The selector pointer targets userspace memory and the offset/length range defines a persistent allowed syscall region until reconfigured.

## Dependencies and integration points

It depends on `linux/types.h` and integrates with task structs, generic syscall entry, and syscall user dispatch configuration APIs.

## Risks and test signals

Risks include empty-struct layout assumptions when generic entry is disabled, invalid userspace selector pointers, offset/length overflow, and recursion state leaks. Tests should cover structure availability in both config modes, range boundary checks, selector fault handling, and dispatch recursion state clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls.h -->
# sources/distributed-fs/ceph-client/include/linux/syscalls.h

## Purpose

`syscalls.h` is the non-architecture-specific syscall declaration and definition-macro header. It provides `SYSCALL_DEFINE*` machinery, syscall tracing metadata generation, argument casting/sign-extension wrappers, compat aliases, split-64-bit helpers, and prototypes for generic, architecture-specific, and deprecated syscalls.

## Important APIs, types, and functions

Macro layers include `__MAP*`, `__SC_DECL`, `__SC_LONG`, `__SC_CAST`, `__SC_TEST`, `SYSCALL_METADATA`, `SYSCALL_TRACE_ENTER_EVENT`, `SYSCALL_TRACE_EXIT_EVENT`, `SYSCALL_DEFINE0`, `SYSCALL_DEFINE1` through `SYSCALL_DEFINE6`, `SYSCALL_DEFINEx`, `__SYSCALL_DEFINEx`, `SC_ARG64`, `SC_VAL64`, and `SYSCALL32_DEFINE*`. With tracing, each syscall can emit `struct syscall_metadata` and trace event calls. The prototype block lists kernel entry points for I/O, xattrs, fs, fd, process, time, scheduler, signal, IPC, networking, memory management, namespaces, security, BPF, Landlock, LSM, mount API, and legacy syscalls, guarded by architecture/config conditions.

## Control flow

For a normal syscall definition, `SYSCALL_DEFINE<n>` emits metadata, a public `sys_*` alias, a `__se_sys_*` sign-extension wrapper taking long-sized arguments, and an inline `__do_sys_*` implementation body. Entry code or syscall tables call the exported `sys_*` symbol. Tracing metadata is collected into special sections for ftrace syscall events. Architectures with custom wrappers can replace this machinery.

## State and persistence behavior

The header owns no runtime mutable state, but tracing metadata and event call descriptors are static kernel objects. Syscall prototypes are ABI contracts and must remain stable in calling convention and argument order.

## Dependencies and integration points

It depends on many UAPI and kernel types, `linux/unistd.h`, quota/key/personality headers, trace syscall support, and architecture syscall-wrapper headers. It integrates with syscall tables, entry code, ftrace, error injection, compat syscall definitions, static analysis, and virtually every syscall implementation file.

## Risks and test signals

Risks include ABI breakage from prototype changes, wrapper mismatches on 32-bit/64-bit or compat builds, sign-extension bugs, tracing metadata argument drift, split 64-bit argument ordering errors, and adding prototypes when `CONFIG_ARCH_HAS_SYSCALL_WRAPPER` expects arch ownership. Tests should include all-arch build coverage, syscall selftests, compat syscall tests, ftrace syscall event validation, BPF/seccomp interaction tests, error-injection builds, and static checks that syscall table entries match prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls_api.h -->
# sources/distributed-fs/ceph-client/include/linux/syscalls_api.h

## Purpose

`syscalls_api.h` is a one-line include shim for `linux/syscalls.h`. It offers an alternate API-facing include path without defining independent syscall symbols.

## Important APIs, types, and functions

All visible APIs come from `syscalls.h`: syscall definition macros, tracing metadata macros, compat aliases, and syscall prototypes.

## Control flow

There is no local control flow. Preprocessing immediately includes `syscalls.h`.

## State and persistence behavior

No state is owned here. Static metadata and ABI behavior are inherited from `syscalls.h`.

## Dependencies and integration points

It depends directly on `linux/syscalls.h` and integrates as a compatibility or layering header for code that wants syscall declarations.

## Risks and test signals

Risks are limited to include layering ambiguity and accidental assumptions that this header narrows the syscall API. Tests are compile-time: consumers including `syscalls_api.h` should see the same declarations as `syscalls.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscore_ops.h -->
# sources/distributed-fs/ceph-client/include/linux/syscore_ops.h

## Purpose

`syscore_ops.h` defines system-core operation registration for devices or subsystems that need very late suspend, early resume, or shutdown callbacks outside normal device PM ordering.

## Important APIs, types, and functions

`struct syscore_ops` provides `suspend`, `resume`, and `shutdown` callbacks taking opaque data. `struct syscore` stores list node, ops pointer, and data pointer. APIs are `register_syscore()`, `unregister_syscore()`, `syscore_suspend()`, `syscore_resume()` under `CONFIG_PM_SLEEP`, and `syscore_shutdown()`.

## Control flow

Subsystems register a `struct syscore`. During system sleep, PM core walks registered syscore objects after normal device suspend and invokes `suspend`; on resume it invokes `resume` early. Shutdown walks callbacks to quiesce core hardware. Unregister removes the object from the global list.

## State and persistence behavior

Registered syscore objects persist in a global list until unregister. Callback data is caller-owned and must outlive registration. Suspend failures affect PM unwind.

## Dependencies and integration points

It depends on lists and integrates with PM sleep core, shutdown paths, clocks/timers/interrupt controllers, and other fundamental subsystems that cannot rely solely on device PM.

## Risks and test signals

Risks include registering stack objects, wrong ordering assumptions, sleeping in late callbacks when not allowed, missing resume after failed suspend, and callbacks touching devices already suspended. Tests should cover registration/unregistration, suspend failure unwind, callback ordering, shutdown invocation, and builds without CONFIG_PM_SLEEP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscore_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysctl.h -->
# sources/distributed-fs/ceph-client/include/linux/sysctl.h

## Purpose

`sysctl.h` declares the kernel `/proc/sys` sysctl table infrastructure and standard proc handlers for text, integer, unsigned, boolean, bitmap, static key, and bounded numeric values. It also preserves warnings about legacy binary sysctl numbering exported through UAPI.

## Important APIs, types, and functions

It defines constant value pointers such as `SYSCTL_ZERO`, `SYSCTL_ONE`, `SYSCTL_INT_MAX`, long equivalents, direction helpers `SYSCTL_USER_TO_KERN()`/`SYSCTL_KERN_TO_USER()`, `proc_handler`, many `proc_do*` conversion handlers, `struct ctl_table_poll`, `DEFINE_CTL_TABLE_POLL`, `struct ctl_table`, `struct ctl_node`, `struct ctl_table_header`, `struct ctl_dir`, `struct ctl_table_set`, and `struct ctl_table_root`. Registration APIs include `register_sysctl()`, `register_sysctl_sz()`, `register_sysctl_init()`, `__register_sysctl_table()`, `unregister_sysctl_table()`, `register_sysctl_mount_point()`, and namespace/set setup/retire helpers, with stubs when sysctl is disabled.

## Control flow

Subsystems define arrays of `ctl_table`, register them at a path, and procfs mirrors leaf entries as files. Reads and writes call the table’s `proc_handler`, which copies between kernel variables and user buffers with optional range/conversion constraints. Pollable entries increment an event counter and wake waiters through `proc_sys_poll_notify()`. Namespaced roots can choose visible sets and ownership/permission behavior.

## State and persistence behavior

Registered table headers persist until unregistered. Header fields track use counts, registration counts, RCU lifetime, parent directory, inodes, and table type. Poll state stores an atomic event counter and waitqueue. Sysctl data pointers refer to caller-owned variables.

## Dependencies and integration points

It depends on lists, RCU, waitqueues, rbtrees, uid/gid types, and UAPI sysctl constants. It integrates with procfs, kernel parameter parsing, namespaces, permissions, and subsystem tunables across VM, networking, kernel, fs, and drivers.

## Risks and test signals

Risks include changing exported numeric IDs, registering transient table memory, bad maxlen/mode/handler combinations, min/max pointer type mismatches, unregister races with proc inodes, namespace visibility bugs, and stubs hiding missing sysctl support. Tests should cover handler conversion/range checks, read/write direction, poll notifications, registration/unregistration under concurrent access, mount points, namespace permissions, boot-time init tables, and CONFIG_SYSCTL disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfb.h -->
# sources/distributed-fs/ceph-client/include/linux/sysfb.h

## Purpose

`sysfb.h` declares generic system-framebuffer support, primarily for firmware-provided framebuffers on x86/EFI systems. It carries display info, DMI EFI framebuffer quirks, simplefb creation, and helpers to disable firmware framebuffers when native drivers take over.

## Important APIs, types, and functions

It defines Mac model enum IDs for EFI quirks, `struct efifb_dmi_info`, and `struct sysfb_display_info` containing `screen_info` plus optional firmware EDID. It declares global `sysfb_primary_display`. APIs include `sysfb_disable()`, `sysfb_handles_screen_info()`, EFI-specific `sysfb_apply_efi_quirks()` and `sysfb_set_efifb_fwnode()`, and simplefb helpers `sysfb_parse_mode()` and `sysfb_create_simplefb()`, with config-dependent stubs.

## Control flow

Early boot records firmware framebuffer details in `screen_info`/`sysfb_primary_display`. Sysfb code applies EFI/DMI quirks, parses mode data into `simplefb_platform_data`, creates a platform device for simplefb/simpledrm-style binding, and later native graphics drivers call `sysfb_disable()` to prevent overlapping firmware framebuffer use.

## State and persistence behavior

Primary display information persists globally after boot. Created platform devices persist in the device model until removed. EFI DMI quirks adjust screen info before device creation. Disabled sysfb state is maintained by implementation code outside this header.

## Dependencies and integration points

It depends on error pointers, simplefb platform data, `screen_info`, EDID, device and platform-device types, EFI, firmware EDID, and SYSFB/SYSFB_SIMPLEFB configs. It integrates with x86 boot graphics, EFI framebuffer, simplefb/simpledrm, and native GPU handoff.

## Risks and test signals

Risks include incorrect DMI quirks, bogus firmware mode parsing, overlapping native and firmware drivers, missing EDID, stubs returning false/`-EINVAL` in unsupported configs, and lifetime issues for fwnodes/platform devices. Tests should cover EFI framebuffer quirks, simplefb creation for common pixel formats, native driver disable handoff, no-SYSFB builds, EDID propagation, and boot on systems with invalid screen_info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfb.h -->
