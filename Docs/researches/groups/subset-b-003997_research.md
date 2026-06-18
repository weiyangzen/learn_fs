# Research: subset-b-003997

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-sysfs.c

## Purpose
This file provides the common sysfs representation for registered IOMMU hardware devices. It creates the global `iommu` device class, gives every IOMMU instance an initially empty `devices/` attribute group, and lets IOMMU drivers add/remove bidirectional sysfs links between an IOMMU device and the devices it manages.

## Important APIs, Types, And Functions
`iommu_class` is a static `struct class` named `iommu`; its `dev_release` frees the dynamically allocated `struct device`, and its class device groups include a `devices` subdirectory.

`iommu_dev_init()` registers that class through `postcore_initcall`, so other IOMMU core and driver code can add IOMMU sysfs devices later in boot.

`iommu_device_sysfs_add()` allocates `iommu->dev`, initializes it, assigns class, parent, and driver-provided attribute groups, sets the kobject name from a format string, adds the device, and stores the `struct iommu_device` as driver data. It is exported GPL.

`iommu_device_sysfs_remove()` clears driver data, unregisters the device, and nulls `iommu->dev`. It is exported GPL.

`iommu_device_link()` adds `devices/<managed-device-name>` under the IOMMU device and creates a reverse `iommu` symlink under the managed device. `iommu_device_unlink()` removes both links.

## Control Flow
Boot registers the `iommu` class before most device probing. A concrete IOMMU driver calls `iommu_device_sysfs_add()` while registering its `struct iommu_device`; later, when the core probes a managed device, `iommu_init_device()` in `iommu.c` calls `iommu_device_link()` to expose the relationship. Device release paths call `iommu_device_unlink()`, and IOMMU driver teardown calls `iommu_device_sysfs_remove()`.

The add path is failure-safe: if name assignment or `device_add()` fails, it drops the initialized device with `put_device()`, causing the release callback to free it.

## State And Persistence
Persistent kernel state is limited to the `iommu_class` registration, `iommu->dev`, kobject names, sysfs links, and driver data. There is no on-disk persistence. Lifetime is kobject/device-model managed: `device_unregister()` eventually invokes `release_device()`.

## Dependencies And Integration Points
This file depends on the Linux driver core, sysfs kobjects, `struct iommu_device`, and exported IOMMU core APIs used by hardware IOMMU drivers. Its links are consumed by userspace tools inspecting `/sys/class/iommu/...` and by the IOMMU group/device sysfs topology produced in `iommu.c`.

## Risks
`iommu_device_link()` assumes `iommu->dev` has already been added; callers must preserve that ordering. Symlink names use `dev_name(link)`, so name collisions or late device renames would surface as sysfs errors. Error handling for the reverse symlink correctly removes the forward link, but callers still need to unwind device probe if link creation fails.

## Test Signals
Useful signals include booting with an IOMMU driver and verifying `/sys/class/iommu/<name>/devices/` links, reverse `iommu` links on managed devices, and clean removal during driver unbind or hotplug. KASAN/kmemleak should see no leak from failed `iommu_device_sysfs_add()` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-traces.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-traces.c

## Purpose
This file instantiates and exports IOMMU tracepoints declared in `trace/events/iommu.h`. It has no runtime policy of its own; it exists so other core and driver code can emit standardized trace events for group membership, domain attachment, map/unmap, and page faults.

## Important APIs, Types, And Functions
`CREATE_TRACE_POINTS` before including `<trace/events/iommu.h>` materializes the tracepoint definitions.

Exported tracepoints are `add_device_to_group`, `remove_device_from_group`, `attach_device_to_domain`, `map`, `unmap`, and `io_page_fault`.

## Control Flow
There is no explicit function control flow beyond static tracepoint creation. Calls in `iommu.c` such as `trace_add_device_to_group()`, `trace_remove_device_from_group()`, `trace_attach_device_to_domain()`, `trace_map()`, `trace_unmap()`, and `trace_io_page_fault()` reach the generated tracepoint machinery when tracing is enabled.

## State And Persistence
The file contributes tracepoint registration metadata compiled into the kernel. Runtime state is managed by the tracing subsystem and trace buffers, not by this file. Trace output is transient unless userspace captures it.

## Dependencies And Integration Points
It depends on the kernel tracing infrastructure and `trace/events/iommu.h`. The exports let GPL modules hook or use these symbols. It integrates tightly with `iommu.c` map/unmap, group membership, domain attach, and fault paths.

## Risks
The risk surface is low, but tracepoint ABI names matter for observability tools. If tracepoint declarations and exports diverge, builds or module users fail. Since tracepoints may run on hot paths, their generated callbacks must remain efficient when disabled.

## Test Signals
Enable ftrace/perf trace events under the IOMMU event group, then exercise device probe, domain attach, IOVA map/unmap, and fault reporting. Expected events should appear without changing behavior when tracing is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-traces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu.c

## Purpose
This is the central Linux IOMMU core implementation for device probing, IOMMU device registration, group construction, default domain management, DMA ownership, domain attach/detach, IOVA map/unmap helpers, reserved-region handling, PASID attachment, attach handles for IOMMUFD, PCI reset blocking, MSI preparation, and sysfs-visible group attributes.

## Important APIs, Types, And Functions
Core state includes the global `iommu_device_list`, `iommu_group_kset`, `iommu_group_ida`, `iommu_global_pasid_ida`, `iommu_def_domain_type`, `iommu_dma_strict`, and `iommu_cmd_line`.

`struct iommu_group` tracks the group kobject, device list, PASID xarray, mutex, default/blocking/current domains, ownership counters, reset recovery count, and optional driver data. `struct group_device` stores a device in a group plus reset-blocking state.

Registration and probing APIs include `iommu_device_register()`, `iommu_device_unregister()`, selftest-only bus registration helpers, `iommu_probe_device()`, `iommu_release_device()`, `bus_iommu_probe()`, and the bus notifier.

Group APIs include `iommu_group_alloc()`, `iommu_group_add_device()`, `iommu_group_remove_device()`, `iommu_group_for_each_dev()`, `iommu_group_get()`, `iommu_group_put()`, `iommu_group_id()`, `generic_device_group()`, `generic_single_device_group()`, `pci_device_group()`, and `fsl_mc_device_group()`.

Domain APIs include `iommu_paging_domain_alloc_flags()`, `iommu_domain_free()`, `iommu_attach_device()`, `iommu_detach_device()`, `iommu_attach_group()`, `iommu_detach_group()`, `iommu_iova_to_phys()`, `iommu_map_nosync()`, `iommu_map()`, `iommu_unmap()`, `iommu_unmap_fast()`, and `iommu_map_sg()`.

Ownership and default-domain APIs include `iommu_device_use_default_domain()`, `iommu_device_unuse_default_domain()`, `iommu_group_claim_dma_owner()`, `iommu_device_claim_dma_owner()`, `iommu_group_release_dma_owner()`, `iommu_device_release_dma_owner()`, and `iommu_group_dma_owner_claimed()`.

PASID and handle APIs include `iommu_attach_device_pasid()`, `iommu_replace_device_pasid()`, `iommu_detach_device_pasid()`, `iommu_alloc_global_pasid()`, `iommu_free_global_pasid()`, `iommu_attach_handle_get()`, `iommu_attach_group_handle()`, `iommu_detach_group_handle()`, and `iommu_replace_group_handle()`.

Other exports include fault reporting, reserved regions, firmware spec setup, default passthrough selection, page-table quirks, PCI reset IOMMU prepare/done, and optional software MSI preparation.

## Control Flow
Boot first creates `/sys/kernel/iommu_groups` via `iommu_init()` and registers IOMMU bus notifiers in `iommu_subsys_init()`. Default domain policy is selected from Kconfig, memory encryption, and early parameters `iommu.passthrough` and `iommu.strict`.

When an IOMMU driver registers, `iommu_device_register()` stores ops in the global list and probes supported buses. Device probe allocates `dev->iommu`, obtains firmware ops, takes the IOMMU module reference, calls `ops->probe_device()`, creates the sysfs IOMMU-device link, obtains a group from `ops->device_group()`, adds a `group_device`, creates default domains, direct reserved mappings, and DMA ops. Removal reverses sysfs links, driver release hooks, domain cleanup, module refs, and group refs.

Group creation allocates an ID, initializes kobjects/xarrays/mutexes, creates the `devices` kobject, and exposes `reserved_regions` and `type`. Adding a device creates bidirectional group sysfs links and records trace events. PCI grouping walks DMA aliases, ACS isolation boundaries, multifunction aliasing, and existing groups to preserve DMA isolation.

Default domain setup chooses a driver-requested, user-requested, or global domain type; allocates identity or paging domains; installs DMA cookies for DMA domains; maps `IOMMU_RESV_DIRECT` regions before attach; attaches the domain to all group devices; and restores/free old domains on failure. Sysfs `type` changes require admin/rawio privileges and usually require no owner.

Attach/detach flows are group-centric. `__iommu_group_set_domain_internal()` iterates every unblocked group device and calls `attach_dev`; on failure it reverts earlier devices to the old domain unless the caller marked the transition must-succeed. Detach returns the group to default or blocking domain depending on ownership.

Map/unmap flows validate paging domains, page-size bitmaps, alignment, and GFP flags. `iommu_map_nosync()` maps via generic page-table ops when a generic `pt_iommu` is present, otherwise calls domain ops in page-size batches, traces and debug-records mapped bytes, and unwinds partial maps. `iommu_map()` adds sync. Unmap uses gather state and syncs unless `iommu_unmap_fast()` delegates sync to the caller.

DMA ownership blocks ordinary DMA API use for exclusive owners such as VFIO/IOMMUFD. Claiming ownership allocates or reuses a blocking domain, attaches it, records `owner` and `owner_cnt`, and rejects mismatched owners or existing PASID attachments. Release restores the default domain once the last owner leaves.

PASID attach attaches a domain to the same PASID across all PASID-capable devices in a group, stores either a tagged domain pointer or attach handle in `group->pasid_array`, and rolls back partial device configuration. Replace reserves the xarray slot, optionally changes hardware PASID domains, and swaps in a new handle. Detach removes hardware PASID domains and erases the xarray entry.

PCI reset prepare/done temporarily attaches RID and PASID translations to the blocking domain while retaining `group->domain` and `pasid_array`, sets `gdev->blocked`, increments `recovery_cnt`, and restores domains after reset. Concurrent attach attempts are rejected while `recovery_cnt` is nonzero.

## State And Persistence
All state is in kernel memory: global IOMMU device lists, per-device `dev_iommu`, `iommu_fwspec`, groups, kobjects, xarrays, IDAs, domains, owner counters, PASID entries, and reset-blocking flags. Sysfs exposes but does not persist group and device topology. Early parameters affect boot-time default policy only. Map/unmap state lives in driver page tables and optional generic page-table structures.

## Dependencies And Integration Points
This file integrates with the Linux device model, bus notifiers, sysfs, PCI/ACS/PASID/ATS, MSI, DMA-IOMMU, firmware-node parsing, module ownership, tracepoints, debugfs, IOMMUFD internal attach handles, `uapi/linux/iommufd.h`, and low-level `struct iommu_ops`/`struct iommu_domain_ops` supplied by hardware drivers.

It is a major integration point for IOMMUFD: domains can carry `IOMMU_COOKIE_IOMMUFD`, handle-based group attach is exported in the `IOMMUFD_INTERNAL` namespace, PASID replace is exported there, and MSI preparation can dispatch to `iommufd_sw_msi()`.

## Risks
Lock ordering is critical: probe uses `iommu_probe_device_lock`, groups use `group->mutex`, PASID xarrays have their own lock for handle lookup, and some reset/PASID readers intentionally rely on synchronization comments. Races here can lead to use-after-free or stale hardware attachment.

Domain transition failure handling assumes drivers can always reattach known-good domains or blocking domains; a buggy driver can leave inconsistent hardware despite defensive warnings.

Default-domain changes and direct reserved mappings are security-sensitive: devices with firmware-required 1:1 mappings cannot be safely attached to blocking domains, and untrusted PCI devices are forced toward translated DMA.

PASID attach/replace stores lockless-visible attach handles. Callers must provide fresh handles and synchronize lifetime with attach/detach, otherwise PRI/fault paths can dereference invalid memory.

Mapping helpers rely on accurate `pgsize_bitmap`, `map_pages`, and `unmap_pages` behavior. Partial map accounting is essential; tests should check that `mapped` bytes reflect hardware state on errors.

PCI reset blocking warns about DMA-aliased siblings that may be prematurely unblocked; that path is explicitly noted as an unresolved risk in complex alias cases.

## Test Signals
Relevant signals include boot/probe tests across supported buses, sysfs group topology, default-domain selection under `iommu.passthrough` and `iommu.strict`, DMA-FQ transition through group `type`, VFIO/IOMMUFD ownership claim/release, PASID attach/replace/detach with mixed PASID-capable group members, PCI reset with ATS enabled, reserved-region direct mappings, MSI remapping through DMA and IOMMUFD cookies, and tracepoint output for group, attach, map, unmap, and fault events.

Unit or selftest coverage should exercise failure injection in domain allocation, attach, map, reserved region retrieval, xarray reservations, and group removal while ensuring no leaked domains, group refs, PASID entries, or sysfs links remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Kconfig

## Purpose
This Kconfig fragment defines build-time controls for the IOMMUFD userspace API, its shared driver core, VFIO container compatibility, and selftest support.

## Important Symbols
`IOMMUFD_DRIVER_CORE` is a hidden bool selected by either `IOMMUFD_DRIVER` or `IOMMUFD` when IOMMUFD is not disabled. It builds shared driver-facing helpers.

`IOMMUFD` is a tristate "IOMMU Userspace API". It selects interval-tree support and `IOMMU_API`, and provides `/dev/iommu` for userspace-managed IO page tables backed by userspace memory.

`IOMMUFD_VFIO_CONTAINER` allows IOMMUFD to provide `/dev/vfio/vfio` compatibility when `VFIO_GROUP` is enabled and native `VFIO_CONTAINER` is not. Its help warns that it lacks several native VFIO container features and is mainly for testing unmodified VFIO Type1 userspace.

`IOMMUFD_TEST` enables dangerous test support for `tools/testing/selftests/iommu`, depends on debug/fault-injection/runtime-testing options, requires AMDv1 page table support compatibility, selects DMA-BUF and `IOMMUFD_DRIVER`, and defaults off.

## Control Flow
Build selection flows from user-visible `IOMMUFD` to object inclusion in the Makefile. Enabling test support adds selftest objects and dependencies. Enabling VFIO container compatibility changes device-node compatibility behavior in the broader IOMMUFD codebase.

## State And Persistence
Kconfig symbols persist only in the kernel build configuration. They control compiled objects and conditional code paths such as test hooks, DMA-BUF support, and compatibility entry points.

## Dependencies And Integration Points
The fragment integrates with top-level IOMMU configuration, VFIO group/container options, interval tree libraries, DMA-BUF, fault injection, runtime testing, and IOMMUFD Makefile object lists.

## Risks
The compatibility option intentionally lacks feature parity with native VFIO container behavior, so enabling it in production could expose missing peer-to-peer DMA or platform-specific behavior. `IOMMUFD_TEST` is explicitly dangerous and should remain confined to selftest kernels.

## Test Signals
Build matrix signals include `IOMMUFD=n/m/y`, `IOMMUFD_VFIO_CONTAINER` with VFIO group configurations, and `IOMMUFD_TEST=y` selftest kernels. The resulting `.config` should select required dependencies and produce expected object lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Makefile

## Purpose
This Makefile defines the IOMMUFD object composition and conditional build products.

## Important Build Entries
`iommufd-y` contains core objects: `device.o`, `eventq.o`, `hw_pagetable.o`, `io_pagetable.o`, `ioas.o`, `main.o`, `pages.o`, `vfio_compat.o`, and `viommu.o`.

`iommufd-$(CONFIG_IOMMUFD_TEST) += selftest.o` adds selftest-only support.

`obj-$(CONFIG_IOMMUFD) += iommufd.o` builds the main module or built-in object.

`obj-$(CONFIG_IOMMUFD_DRIVER) += iova_bitmap.o` builds the IOVA bitmap helper for driver-facing functionality.

`iommufd_driver-y := driver.o` and `obj-$(CONFIG_IOMMUFD_DRIVER_CORE) += iommufd_driver.o` build the shared driver helper library.

## Control Flow
Kconfig symbols choose whether the main `/dev/iommu` implementation, selftests, IOVA bitmap helper, and shared driver core are included. `driver.o` is separated from `iommufd.o` so builtin or external users can consume shared helper exports when `IOMMUFD_DRIVER_CORE` is selected.

## State And Persistence
There is no runtime state in the Makefile. Its persistent effect is the build artifact layout and symbol availability.

## Dependencies And Integration Points
It integrates with `Kconfig`, `main.c` ioctl dispatch, IOAS/page-table code, VFIO compatibility, vIOMMU support, event queues, and the exported helper namespace from `driver.c`.

## Risks
Misconfigured object inclusion can produce missing exported symbols or include driver helpers without the rest of IOMMUFD. Test-only `selftest.o` must remain conditional. Splitting `driver.o` from the main object means namespace imports and Kconfig dependencies must stay aligned.

## Test Signals
Check `make drivers/iommu/iommufd/` under `IOMMUFD=m/y`, `IOMMUFD_TEST=y`, and driver-core-only configurations. `modinfo`/link output should expose expected `iommufd` and `iommufd_driver` artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/device.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/device.c

## Purpose
This file binds physical devices to an IOMMUFD context, manages per-IOMMU-group IOMMUFD state, attaches/replaces/detaches devices and PASIDs to hardware page tables, handles reserved IOVA/MSI setup, exposes in-kernel IOAS access objects, and reports device hardware information to userspace.

## Important APIs, Types, And Functions
`allow_unsafe_interrupts` is a module parameter allowing device binding without isolated MSI support; it is explicitly a security-weakening override.

`struct iommufd_attach` stores the hwpt for a PASID plus a device xarray. `struct iommufd_group` is defined in private headers and is managed here as per-context state indexed by `iommu_group_id()`.

Group helpers include `iommufd_get_group()`, `iommufd_put_group()`, and `iommufd_group_release()`. They keep a per-context xarray of IOMMU groups, refcount entries, and prevent duplicate state for the same core group.

Device lifecycle exports include `iommufd_device_bind()`, `iommufd_device_unbind()`, `iommufd_ctx_has_group()`, `iommufd_device_to_ictx()`, `iommufd_device_to_id()`, `iommufd_device_attach()`, `iommufd_device_replace()`, and `iommufd_device_detach()`.

Attachment internals include `iommufd_hw_pagetable_attach()`, `iommufd_hw_pagetable_detach()`, `iommufd_device_auto_get_domain()`, `iommufd_device_change_pt()`, `iommufd_hwpt_attach_device()`, `iommufd_hwpt_replace_device()`, and `iommufd_hwpt_detach_device()`.

Access-object exports include `iommufd_access_create()`, `iommufd_access_destroy()`, `iommufd_access_attach()`, `iommufd_access_detach()`, `iommufd_access_replace()`, `iommufd_access_pin_pages()`, `iommufd_access_unpin_pages()`, and `iommufd_access_rw()`.

`iommufd_get_hw_info()` implements the userspace hardware-info ioctl for device-specific IOMMU data, dirty tracking capability, ATS/PASID capability signals, and driver-specific data buffers.

## Control Flow
Binding first checks cache coherency, obtains per-context group state, rejects unsafe MSI unless overridden, claims DMA ownership from the IOMMU core, allocates an IOMMUFD device object, references the context, stores coherency capability, and finalizes the object. Unbind destroys the user object, releasing DMA ownership, group refs, vdevice state, and context refs.

Attachment uses `iommufd_device_change_pt()` to accept an existing HWPT, nested HWPT, or IOAS. For IOAS inputs it searches reusable auto-created paging domains, trying compatible domains and treating `-EINVAL` as a soft incompatibility, otherwise creates an auto domain. Immediate attach supports IOMMU drivers that cannot allocate a complete domain before attach.

`iommufd_hw_pagetable_attach()` serializes on `igroup->lock`, reserves the PASID slot with an xarray zero entry, creates `iommufd_attach` if needed, inserts the device, enforces reserved IOVAs and software MSI pages for no-PASID paging domains, attaches the group/PASID only on the first device for that PASID, stores the hwpt, and refcounts the hwpt per device.

Replacement verifies the device is currently attached, optionally enforces reserved regions for a new paging IOAS, calls IOMMU core replace operations, removes old reserved regions if IOAS changed, swaps the attached hwpt, and moves device-array references from the old hwpt to the new hwpt.

Detach removes the device from the PASID attach array; if it was the last device for that PASID, it detaches from IOMMU core, auto-responds outstanding faults as invalid, removes the PASID attach record, and drops reserved IOVA state. It then puts the hwpt reference outside the group lock.

Access-object control flow uses `access->ioas_lock` to block pin/read operations during attach/detach/replace. On IOAS change it sets `access->ioas` to NULL, optionally registers with the new IO page table, notifies external access users to unmap all old ranges, removes old access registration, updates refcounts, and then publishes the new IOAS. Pin and read/write paths walk contiguous `iopt_area` ranges under `iova_rwsem`, enforce permissions and alignment, and unwind partial pins on failure.

Hardware info flow validates flags/reserved fields, obtains the IOMMUFD device object, calls optional `ops->hw_info()`, copies as much as userspace requested, clears trailing buffer bytes, returns the kernel-supported length and capability bits, and reports enabled PASID properties for PCI devices.

## State And Persistence
State is in the IOMMUFD context: object xarrays, per-group xarrays, `pasid_attach` records, `device_array` entries, hwpt object refs, reserved IOVA entries in IO page tables, software MSI bitmaps, vdevice pointers, access-object IOAS references, and lock-protected page pin/access intervals. No state persists across process or kernel lifetime except hardware/domain state until detached.

## Dependencies And Integration Points
The file depends on IOMMU core ownership, group attach handles, PASID attach APIs, reserved-region APIs, dirty/PASID/ATS capabilities, PCI PRI/PASID helpers, MSI isolation, IOMMUFD object lifecycle, IOAS/page-table code, event queue fault cleanup, vIOMMU/vdevice objects, and pages access helpers.

## Risks
This is a security-sensitive boundary. Binding requires cache coherency and isolated MSI because userspace cannot safely repair cache or interrupt isolation after binding. The override parameter should be tested but avoided in production.

Attach/replace/detach lock ordering across `igroup->lock`, IOAS mutexes, IOMMU core group mutexes, and object refs must remain stable. Fault auto-response relies on attach handles being valid until detach/replace frees them.

Reserved IOVA enforcement must unwind exactly; otherwise userspace could map device-reserved ranges or software MSI windows. Replacement across IOASs is particularly sensitive because old and new reserved regions overlap with group devices.

Access objects require external drivers to honor unmap callbacks and unpin exactly matching ranges. The unmap path in `io_pagetable.c` can return `-EDEADLOCK` if access users fail to respond after repeated notifications.

Hardware-info copy paths must handle short buffers, larger kernel data, and zeroing correctly to avoid leaking kernel memory.

## Test Signals
Exercise bind/unbind with and without MSI isolation, cache-coherent and non-coherent devices, group sharing, repeated bind failures, IOAS auto-domain attach, manual HWPT attach, PASID attach, replace across same and different IOASs, detach of multi-device groups, vdevice destruction races, software MSI reservation/install, page fault auto-response on detach/replace, access pin/unpin/rw permissions, access replacement callbacks, and hardware-info short/long buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/double_span.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/double_span.h

## Purpose
This header declares a double interval-tree span iterator used to compute spans over the union of two interval trees. IOMMUFD uses it for IOVA allocation where both reserved ranges and mapped areas must be considered.

## Important APIs And Types
`struct interval_tree_double_span_iter` stores two input interval tree roots, two regular span iterators, hole/used start and end fields, and an `is_used` state: `0` for hole, `1` for a used span from the first tree, `2` for a used span from the second tree, and `-1` for done.

`interval_tree_double_span_iter_first()`, `interval_tree_double_span_iter_update()`, and `interval_tree_double_span_iter_next()` are implemented in `pages.c`.

`interval_tree_double_span_iter_done()` checks for the terminal state.

`interval_tree_for_each_double_span()` wraps initialization, done testing, and iteration in a `for` loop.

## Control Flow
Callers initialize the iterator with two interval trees and a range. Each iteration reports either a hole or a used span, preferring the first tree when both trees cover the same region. The iterator is greedy and avoids emitting consecutive spans with the same `is_used` class.

## State And Persistence
The iterator is stack/local state only. It references caller-owned interval trees and does not allocate or persist memory.

## Dependencies And Integration Points
It depends on Linux interval tree and span iterator helpers. `io_pagetable.c` uses it in `iopt_alloc_iova()` to search holes that are inside allowed ranges but outside both reserved and already mapped IOVA intervals.

## Risks
The first-tree priority is semantically important; changing it can alter IOVA allocation around reserved ranges. Iterator boundary bugs can create off-by-one allocation holes, overlap existing mappings, or skip valid ranges.

## Test Signals
Tests should cover empty trees, overlapping first/second intervals, adjacent intervals, first-tree priority, full-range coverage, holes at boundaries, and IOVA allocation with reserved plus mapped intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/double_span.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/driver.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/driver.c

## Purpose
This file builds the driver-facing IOMMUFD helper module. It exports object dependency helpers, mmap-offset management for driver-owned MMIO windows, vIOMMU/vdevice lookup helpers, vIOMMU event reporting, and software MSI mapping support shared with builtin modules.

## Important APIs, Types, And Functions
`_iommufd_object_depend()` and `_iommufd_object_undepend()` let drivers create same-type object dependencies by manipulating object user refcounts. They reject self-dependency and cross-type dependencies.

`_iommufd_alloc_mmap()` allocates a page-aligned mmap offset in `ictx->mt_mmap` for an owner object and physical MMIO range. `_iommufd_destroy_mmap()` erases that offset and verifies ownership.

`iommufd_vdevice_to_device()`, `iommufd_viommu_find_dev()`, and `iommufd_viommu_get_vdev_id()` translate virtual devices back to physical devices or virtual IDs under vIOMMU xarray locking.

`iommufd_viommu_report_event()` queues driver-supplied vIOMMU events into a typed event queue, using a lost-events header when the queue is full or allocation fails.

When `CONFIG_IRQ_MSI_IOMMU` is enabled, `iommufd_sw_msi_get_map()`, `iommufd_sw_msi_install()`, and `iommufd_sw_msi()` create fd-global IOVA mappings for physical MSI pages and update MSI descriptors.

## Control Flow
Dependency helpers are direct refcount operations with validation.

MMAP allocation validates page alignment, allocates `struct iommufd_mmap`, reserves a range in the maple tree starting after the first page, stores `vm_pgoff`, and returns a user-visible offset. Destroy erases and frees it.

vIOMMU event reporting takes `viommu->veventqs_rwsem`, finds a queue by type, then under the queue spinlock either appends a newly allocated event or records lost events. It calls the event handler to place the event on the queue and wake readers.

Software MSI handling is invoked from the IOMMU core while the group mutex protects attach-handle lifetime. It finds the IOMMUFD attach handle, skips identity/no-software-MSI cases, allocates or reuses a global MSI-page mapping, maps the physical page into the hwpt if not present, records required MSI bits on the group, and updates the descriptor with the IOVA.

## State And Persistence
State lives in IOMMUFD context maple trees (`mt_mmap`), vIOMMU xarrays/lists, event queue lists and counters, and `sw_msi_list`/bitmaps. These are kernel-memory lifetimes tied to the IOMMUFD file and objects.

## Dependencies And Integration Points
The file depends on IOMMUFD private objects, Linux maple tree, anon event queues from `eventq.c`, vIOMMU objects, MSI descriptors, `iommu_map()`, IOMMU core attach handles, and the `IOMMUFD`/`IOMMUFD_INTERNAL` export namespaces.

## Risks
Object dependencies are low-level refcount operations; misuse can leak objects or deadlock destruction. MMAP offsets must remain owner-checked to avoid one object destroying another object's mapping.

Event reporting runs in contexts such as threaded IRQ handlers, so allocation uses atomic behavior and overflow must be represented through lost-event headers. Queue depth and lost event semantics need careful testing.

Software MSI is security-sensitive: mappings must match reserved SW-MSI windows, be consistent across domains in a context, and only run while attach handles are stable.

## Test Signals
Test same-type dependency/ref release, rejection of self and cross-type dependencies, mmap alignment and duplicate destroy warnings, vIOMMU device lookup under xarray locking, event queue overflow/lost events, and software MSI mapping reuse across devices/domains with IOMMUFD cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/eventq.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/eventq.c

## Purpose
This file implements IOMMUFD event queues backed by anon inodes. It supports page-fault queues for I/O page faults and vIOMMU event queues for driver-reported virtual IOMMU events, including read/write/poll/release file operations and object lifecycle cleanup.

## Important APIs, Types, And Functions
Fault handling includes `iommufd_fault_alloc()`, `iommufd_fault_iopf_handler()`, `iommufd_fault_fops_read()`, `iommufd_fault_fops_write()`, `iommufd_fault_destroy()`, and `iommufd_auto_response_faults()`.

vEVENTQ handling includes `iommufd_veventq_alloc()`, `iommufd_veventq_abort()`, `iommufd_veventq_destroy()`, `iommufd_veventq_fops_read()`, and helper fetch/restore functions.

Common infrastructure includes `iommufd_eventq_init()`, `iommufd_eventq_fops_poll()`, `iommufd_eventq_fops_release()`, and the `INIT_EVENTQ_FOPS` macro.

## Control Flow
Fault allocation validates flags, allocates an IOMMUFD fault object, initializes a response xarray and mutex, creates an anon inode with read/write/poll ops, responds to userspace with object ID and fd, then installs the fd. Hardware page faults arrive through `iommufd_fault_iopf_handler()`, which appends an `iopf_group` to the deliver list and wakes readers.

Fault reads require nonseekable, record-aligned reads. They remove groups from the deliver list, allocate response cookies, compose one `iommu_hwpt_pgfault` per fault, copy to userspace, and restore the group if the buffer is too small or copy fails. Fault writes consume page-response records, validate response codes, erase matching cookies, respond to hardware, and free groups.

`iommufd_auto_response_faults()` is called on detach/replace to find pending groups for a dying attach handle in both deliver and response queues, respond invalid, and free them.

vEVENTQ allocation validates type/depth, locks the vIOMMU event queue list for write, rejects duplicate types, allocates an event queue object, references the vIOMMU, installs it on the vIOMMU list, initializes a lost-events header, creates an anon inode, finalizes the object, and installs the fd.

vEVENTQ reads fetch queued events. For lost-events headers it copies a temporary header so the permanent lost header can be reinserted when needed. Normal events decrement `num_events` after successful copy and are freed.

Poll reports `EPOLLOUT` for fault queues and `EPOLLIN|EPOLLRDNORM` when the deliver list is nonempty. Release drops the eventq object user ref and context ref.

## State And Persistence
State is in event queue objects, anon file references, wait queues, spinlock-protected deliver lists, fault response xarrays, vEVENTQ depths and event counters, and vIOMMU queue lists. No data persists after object/fd destruction.

## Dependencies And Integration Points
This file integrates with IOMMUFD object management, `iopf_group` hardware fault infrastructure, attach handles from IOMMU core/IOMMUFD, anon inodes, file descriptor installation, userspace UAPI records, polling, vIOMMU driver callbacks, and `driver.c` event reporting.

## Risks
Fault delivery is sensitive to cookie lifetime and attach-handle lifetime. If a detach path misses a pending group, userspace could respond to a stale hardware context; if it frees too early, readers can fault.

Record-size validation is strict; userspace must use exact multiples for fault records and responses. Partial copy handling must restore queues without losing groups.

vEVENTQ overflow behavior intentionally collapses events into a lost-events marker. Queue users must treat that marker as lossy state and resynchronize.

Locking mixes mutexes, spinlocks, xarrays, and rwsems; order must prevent races between read/write, destroy, detach auto-response, and driver event reporting.

## Test Signals
Exercise fault fd allocation, polling, multi-fault group reads, too-small reads, invalid response codes, duplicate/late responses, detach auto-invalid responses from deliver and response queues, vEVENTQ duplicate type rejection, queue overflow lost-events markers, read buffer boundaries, fd release refcounts, and destroy while queues hold pending events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/eventq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/hw_pagetable.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/hw_pagetable.c

## Purpose
This file allocates, finalizes, aborts, destroys, configures, and invalidates IOMMUFD hardware page table objects. It supports paging HWPTs tied to IOAS objects, nested HWPTs tied to parent HWPTs or vIOMMUs, dirty tracking, dirty bitmap retrieval, page-fault queue association, and driver-specific cache invalidation.

## Important APIs, Types, And Functions
Lifecycle functions include `iommufd_hwpt_paging_destroy()`, `iommufd_hwpt_paging_abort()`, `iommufd_hwpt_nested_destroy()`, `iommufd_hwpt_nested_abort()`, and private `__iommufd_hwpt_destroy()`.

Allocation functions include `iommufd_hwpt_paging_alloc()`, `iommufd_hwpt_nested_alloc()`, `iommufd_viommu_alloc_hwpt_nested()`, and ioctl entry `iommufd_hwpt_alloc()`.

Dirty/invalidate ioctls include `iommufd_hwpt_set_dirty_tracking()`, `iommufd_hwpt_get_dirty_bitmap()`, and `iommufd_hwpt_invalidate()`.

`iommufd_hwpt_paging_enforce_cc()` asks a domain to enforce cache coherency if a bound device requires it.

## Control Flow
Paging allocation validates flags and driver capabilities, checks dirty tracking capability, rejects conflicting fault/nest-parent flags, allocates an IOMMUFD paging object, references the IOAS, allocates a domain using driver flag-aware ops or generic paging allocation, marks the domain owner and IOMMUFD cookie, enforces cache coherency if required, optionally immediately attaches the domain to support legacy drivers, fills the domain from the IOAS via `iopt_table_add_domain()`, and links it to `ioas->hwpt_list`.

Nested allocation validates user data and driver nested-domain ops, requires a non-auto paging parent marked nest-parent and owned by the same IOMMU ops, allocates a nested object, references the parent, allocates a nested domain, and verifies the domain type is `IOMMU_DOMAIN_NESTED`. vIOMMU nested allocation follows the vIOMMU ops path and references the vIOMMU.

The `iommufd_hwpt_alloc()` ioctl obtains the device and parent PT object, dispatches to paging, nested, or vIOMMU nested allocation, optionally attaches a fault object and IOPF handler, responds with the HWPT ID, and finalizes or aborts the object with proper mutex/object cleanup.

Dirty tracking validates flags, gets a paging HWPT, and delegates to `iopt_set_dirty_tracking()`. Dirty bitmap retrieval validates flags/reserved fields and delegates to `iopt_read_and_clear_dirty_data()`. Invalidate dispatches to nested-domain `cache_invalidate_user()` or vIOMMU `cache_invalidate()` and reports how many entries the driver processed.

## State And Persistence
State includes IOMMUFD HWPT objects, `iommu_domain` pointers, IOAS user refs, parent/vIOMMU refs, IOAS `hwpt_list` membership, domain cookies, fault object refs, and driver-domain dirty tracking state. All state is in kernel memory and hardware IOMMU configuration until destroyed.

## Dependencies And Integration Points
The file depends on IOMMU core domain allocation and free APIs, per-driver `iommu_ops`, nested domain ops, IOAS/page-table fill/remove logic, IOMMUFD object management, fault event queues, vIOMMU ops, and UAPI structs in `linux/iommufd.h`.

## Risks
Allocation has complex unwind paths: IOAS mutex ownership, immediate attach, domain fill, object abort/finalize, and reference counts must stay balanced. Cache coherency is security-critical; a device requiring enforced coherency must not share a non-coherent HWPT.

Nested domains require exact driver ownership compatibility and valid user data. Accepting auto domains as nesting parents or mismatched ops would let userspace construct invalid hardware nesting.

Dirty tracking assumes domain `dirty_ops` are coherent with the IOAS mappings and that enabling starts from a clean snapshot. Invalidation returns partial completion counts, so userspace must handle short processing.

## Test Signals
Test paging allocation with generic and flag-aware driver ops, dirty-tracking-capable and incapable devices, fault queue association, immediate attach failure unwind, IOAS fill failure, nested allocation with invalid parent/auto parent/mismatched ops, vIOMMU nested allocation, dirty tracking enable/disable, dirty bitmap with clear/no-clear, and invalidate dispatch with nested HWPT and vIOMMU objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/hw_pagetable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.c

## Purpose
This file implements the IOMMUFD IO page table (`io_pagetable`) that maps IOVA ranges to `iopt_pages` backing storage, fills/unfills attached IOMMU domains, supports userspace/file/DMA-BUF mappings, tracks allowed and reserved IOVA ranges, handles dirty tracking, supports unmap notifications for access objects, manages IOVA alignment, and controls large-page behavior.

## Important APIs, Types, And Functions
`struct iopt_pages_list` is a temporary map/copy descriptor pairing an `iopt_pages` object, optional `iopt_area`, start byte, length, and list node.

Contiguous-area iteration is implemented by `iopt_area_contig_init()` and `iopt_area_contig_next()`.

Map APIs include `iopt_map_user_pages()`, `iopt_map_file_pages()`, `iopt_map_pages()`, and internal `iopt_map_common()`, `iopt_alloc_area_pages()`, `iopt_insert_area()`, and `iopt_fill_domains_pages()`.

Unmap APIs include `iopt_unmap_iova()`, `iopt_unmap_all()`, and internal `iopt_unmap_iova_range()`.

Domain APIs include `iopt_table_add_domain()`, `iopt_table_remove_domain()`, `iopt_fill_domain()`, and `iopt_unfill_domain()`.

Dirty tracking APIs include `iopt_set_dirty_tracking()`, `iopt_read_and_clear_dirty_data()`, `iommufd_check_iova_range()`, and the bitmap iteration callbacks.

IOVA policy APIs include `iopt_set_allow_iova()`, `iopt_reserve_iova()`, `iopt_remove_reserved_iova()`, and `iopt_table_enforce_dev_resv_regions()`.

Other APIs include `iopt_init_table()`, `iopt_destroy_table()`, `iopt_get_pages()`, `iopt_cut_iova()`, `iopt_enable_large_pages()`, `iopt_disable_large_pages()`, `iopt_add_access()`, and `iopt_remove_access()`.

## Control Flow
Mapping begins by allocating `iopt_pages` from user VA, file, or DMA-BUF. `iopt_alloc_area_pages()` preallocates areas, takes the write side of `iova_rwsem`, validates fixed IOVA or auto-allocates a hole using allowed, reserved, and mapped interval trees, inserts areas with `pages == NULL` to reserve the IOVA space, then releases the lock. `iopt_map_pages()` fills every attached domain under `domains_rwsem`, then publishes `area->pages` under `iova_rwsem`, moving page refs from the temporary list into persistent areas.

Auto IOVA allocation preserves page offset and useful alignment for huge pages, refuses zero IOVA, scans allowed ranges or the full usable space, and uses `interval_tree_for_each_double_span()` over reserved and area trees to find a hole.

Unmap takes `domains_rwsem` read and `iova_rwsem` write. It refuses partial-area unmaps, mappings under construction/destruction, and locked areas. If an area has active access users, it marks `prevent_access`, drops locks, calls `iommufd_access_notify_unmap()`, and retries, aborting after repeated non-response. Once safe, it clears `area->pages`, unmaps/unfills domains, removes the area, drops page refs, and advances the search start to avoid racing new allocations behind it.

Domain add takes domain and IOVA write locks, checks duplicate domains, calculates required IOVA alignment from `pgsize_bitmap`, reserves geometry outside the aperture, reserves an xarray ID, fills the new domain from every existing area, updates alignment, and stores the domain. Domain removal compresses the domains xarray, unmaps/unfills the removed domain, removes its geometry reservations, and recalculates alignment.

When filling domains, a first domain can become the `storage_domain` for each area and insert the area's pages interval into `pages->domains_itree`. Later domains can be filled from page storage. Removing one of many domains may select another storage domain, while removing the last domain fully unpins/unfills from page storage. DMA-BUF areas also track/untrack revocation per domain.

Dirty tracking validates bitmap ranges against IOAS alignment and bitmap page size, iterates only contiguous mapped IOVA areas, calls driver dirty ops, and syncs IOTLB gathers when clearing. Enabling dirty tracking first clears existing dirty data to start from a clean baseline.

Allowed IOVA replacement swaps the allowed interval tree and verifies no reserved range intersects. Reserved IOVA insertion refuses overlap with mapped areas or allowed ranges, records an owner, and removal deletes all owner-matching reservations. Device reserved-region enforcement imports IOMMU reserved regions, skips relaxable direct regions, reserves all other regions, records SW-MSI base when requested, and validates HW/SW MSI combinations.

Area splitting for VFIO compatibility creates left/right areas around a split point, disallows DMA-BUF, active access, huge-page-capable mapped domains unless large pages are disabled, updates `pages->domains_itree`, and shares the same `iopt_pages` via refcounts.

## State And Persistence
Persistent runtime state inside `io_pagetable` includes interval trees for mapped areas, allowed IOVAs, and reserved IOVAs; an xarray of attached domains; an xarray of access users; `iova_alignment`; `next_domain_id`; and large-page mode. Each `iopt_area` stores IOVA range, backing page range, permissions, page offset, storage domain, access counters, lock counters, and access-prevention state. Backing `iopt_pages` objects and domain page tables persist until unmapped or domains are removed.

## Dependencies And Integration Points
This file depends on `pages.c` for pinning, filling domains, xarray page storage, DMA-BUF tracking, access pinning, and rw access; on `ioas.c` for ioctl entry points; on `hw_pagetable.c` for domain add/remove and dirty tracking; on `device.c` for reserved regions and access notifications; on IOMMU core map/unmap/dirty ops; and on interval tree, xarray, DMA-BUF, and UAPI bitmap helpers.

## Risks
Locking is dense: `iova_rwsem` protects IOVA interval structures, `domains_rwsem` prevents domain attach/remove while areas are transient, and `pages->mutex` protects page storage, `storage_domain`, and access counters. Lock order regressions can deadlock or expose NULL `pages` areas to domain attach.

Publishing areas with `pages == NULL` reserves IOVA during setup; any user of `area->pages` must honor the documented lock rules. Unmap must notify and wait for external access users; non-cooperating users can stall unmap or trigger `-EDEADLOCK`.

Alignment changes from domains, access objects, and large-page mode can reject existing mappings. Area splitting is intentionally constrained because huge pages, DMA-BUF revocation, and access intervals are hard to split safely.

Reserved region enforcement must avoid overflow in `start + length - 1`, handle driver-provided regions sanely, and unwind owner reservations on failures. Dirty bitmap code must reject unaligned or overflowing ranges to avoid reading outside mappings.

## Test Signals
Test fixed and auto IOVA map/unmap, overlap rejection, reserved/allowed range interaction, aperture reservations, multiple attached domains, domain add/remove while mappings exist, map failure unwind, DMA-BUF mappings and revocation, dirty tracking enable and bitmap read with no-clear/clear, unmap with active access callbacks, `iopt_get_pages()` contiguous coverage, area splitting with large pages enabled/disabled, access-list alignment changes, and destroy-time empty-tree/xarray warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.h

## Purpose
This header defines the core data structures and helper interfaces for IOMMUFD IO page tables. It describes how IOVA areas map to backing page objects, how allowed/reserved intervals are represented, how access and DMA-BUF tracking interact with mappings, and which functions `io_pagetable.c`, `pages.c`, `ioas.c`, `device.c`, and `hw_pagetable.c` share.

## Important APIs, Types, And Functions
`struct iopt_area` represents one mapped IOVA interval and its slice of an `iopt_pages` backing object. It contains interval-tree nodes for IOVA and pages, the parent `io_pagetable`, backing `iopt_pages`, `storage_domain`, page offset, permissions, `prevent_access`, and access/lock counters.

`struct iopt_allowed` and `struct iopt_reserved` represent allowed and reserved IOVA intervals; reserved intervals carry an owner pointer for owner-scoped removal.

Inline helpers convert between area IOVA, page indexes, lengths, and byte offsets: `iopt_area_index()`, `iopt_area_last_index()`, `iopt_area_iova()`, `iopt_area_last_iova()`, `iopt_area_length()`, `iopt_area_start_byte()`, and `iopt_area_iova_to_index()`.

The `__make_iopt_iter()` macro creates interval-tree iterators for areas, allowed ranges, and reserved ranges.

`struct iopt_area_contig_iter` and `iopt_for_each_contig_area()` define contiguous mapped-area iteration over an IOVA range.

`enum iopt_address_type` distinguishes user memory, file-backed memory, and DMA-BUF memory. `struct iopt_pages_dmabuf_track` and `struct iopt_pages_dmabuf` hold DMA-BUF attachment/tracking state.

`struct iopt_pages` stores backing memory state: kref, mutex, page count, pinned count, source task/mm/user, address type, backing pointer/file/DMA-BUF, writability, accounting mode, pinned PFN xarray, access interval tree, and domains interval tree.

Function declarations cover domain fill/unfill, DMA-BUF tracking, page allocation/release, xarray fill/unfill, access pin/unpin, rw access, and pin accounting.

## Control Flow
Callers build mappings by allocating an `iopt_pages`, inserting one or more `iopt_area` entries, filling attached domains through declared fill functions, and then publishing the area as active. Access and unmap paths use byte/index helpers to translate from IOVA ranges to backing pages. Domain add/remove paths use domain fill/unfill declarations and DMA-BUF tracking declarations. Page pinning and CPU rw access are implemented in `pages.c` behind the prototypes in this header.

The header encodes important lock expectations in comments: `io_pagetable::iova_rwsem` protects interval nodes, `iopt_pages::mutex` protects page nodes and access counters, `iopt` and permissions are immutable, and `storage_domain` is protected by `pages->mutex`.

## State And Persistence
The header defines runtime in-memory state only. `iopt_area` and `iopt_pages` objects persist while IOAS mappings or access pins reference them. Xarray and interval-tree nodes are embedded in those objects rather than stored separately.

## Dependencies And Integration Points
It depends on DMA-BUF, interval tree, kref, mutex, xarray, IOMMU domain declarations, and `iommufd_private.h`. Its structures are shared by `io_pagetable.c` for IOVA layout, `pages.c` for PFN storage and domain map/unmap, `device.c` for access objects, `hw_pagetable.c` for dirty tracking/domain registration, and `ioas.c` for userspace IOAS commands.

## Risks
The structure comments are part of the contract. Misusing `area->pages == NULL`, `storage_domain`, or interval nodes outside the documented locks risks races during map/unmap or domain attach/remove.

Byte/index conversion must preserve page offsets for sub-page-aligned file or user mappings. Incorrect conversions can pin or expose the wrong backing pages.

DMA-BUF revocation is represented by zero-length `phys` state and must be checked while holding `pages->mutex`; otherwise mappings may outlive revoked attachments.

Access intervals act as locks over pinned PFNs. Incorrect access accounting can prevent unmap forever or allow unmap while a driver still uses pages.

## Test Signals
Compile-time signals include lockdep assertions and selftest warnings in helpers. Runtime tests should cover byte/index conversions with offsets, contiguous iteration gaps, access interval add/remove accounting, DMA-BUF revoked checks, page refcount release, domain fill/unfill declarations across multiple domains, and alignment changes caused by domains or access objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.h -->
