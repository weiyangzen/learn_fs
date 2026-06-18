# Group Research: group_574_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__afe90785e5bb

Scope: `Docs/research_subset_a.md`, source tree `sources/os/illumos/illumos-gate`. All listed files were read completely. This group is mostly illumos DDI/DKI device-driver interface headers, plus public ABI headers for disk ioctls, devinfo snapshots, FMA, UFM, `/dev/poll`, directory entries, and legacy DES.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_impldefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_impldefs.h

This is the central private implementation definition header for illumos DDI device tree internals. It includes the core DDI property, devops, autoconf, mutex, page, DACF, fault-management, DMA, interrupt, hotplug, ISA, id-space, modhash, and bitset headers, which reflects its role as the connective tissue for devinfo-node state.

The dominant structure is `struct dev_info`, the in-kernel representation of a device tree node. It records tree relationships (`devi_parent`, child, sibling), binding/name/address data, nodeid/instance, driver ops, parent-private data, minor nodes, per-driver instance links, inherited bus operation provider pointers, power-management state, callback lists, fault-management handle, interrupt state, contracts, hotplug handles, property dynamic caches, bus-private data, and nexus-specific data. Code touching this file is usually operating below public DDI and must preserve assumptions made by autoconfiguration, devfs, hotplug, PM, FMA, and interrupt subsystems.

The file defines device state and transition flag families for online/offline/down/degraded/removed device state, bus quiesced/down state, and reconfiguration transitions such as attaching, detaching, onlining, offlining, DACF invocation, devfs event add/remove, and reset-needed. The `DEVI_*` macros both test and mutate those bitfields and are used throughout device configuration logic.

It also defines ancillary structures: `ddi_cb` callback list entries, `devi_port`, `devi_bus_priv`, `regspec`, `regspec64`, `rangespec`, attach/detach specs, `ddi_minor`, `ddi_minor_data`, `ddi_parent_private_data`, soft-state tables (`i_ddi_soft_state`, string-keyed soft state, string-id records), DMA implementation handles, callback queues, dynamic-property caches, encoded device-id implementation data, and saved PCI config/capability descriptors.

Architecture-specific DMA internals are present. SPARC and non-SPARC forms of `ddi_dma_impl_t` differ, and public-looking DMA handles ultimately depend on these private layouts. The flag families `DMP_*`, `_DMCM*`, DMA physical mapping callbacks, and shadow/lock/cache/bypass/no-sync flags are private implementation controls.

The device-id section defines the raw encoded `impl_devid` layout, magic/revision constants, length/type conversion macros, ASCII/binary device-id type conversion helpers, SCSI VPD type checks, and the `devid` property name. These support compatibility with libdevinfo’s device-id representation even though the implementation is property-based.

Research notes:
- This header is private ABI for the illumos kernel, not a stable driver-facing surface.
- `struct dev_info` field order and bit meanings are high-risk compatibility points for kernel modules.
- Device-state macros have side effects and often imply devfs event/report state changes.
- Includes many cross-subsystem dependencies, so small changes can affect autoconf, devfs, PM, hotplug, FMA, interrupts, and DMA.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_impldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_implfuncs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_implfuncs.h

This header declares private implementation entry points for the DDI framework. It is included only for kernel implementation code and pulls in OBP, vnode, task, and project/resource-control types.

The declarations cover bus mapping and fault handling (`i_ddi_bus_map`, `i_ddi_apply_range`, `i_ddi_rnumber_to_regspec`, `i_ddi_map_fault`), DMA and device memory allocation (`i_ddi_mem_alloc`, `i_ddi_mem_free`), device access attribute translation to HAT attributes, cache attribute validation, and fault state set/clear routines for access and DMA handles.

It exposes root nexus event helpers, property operation helpers, PROM property integer extraction, Sun bus child initialization/removal, access-handle allocation and initialization, access/DMA fault protection setup, peek/poke trampoline support, boot-device name conversion, and nodeid allocation/free/take routines.

The file also declares device tree and driver-binding helpers: minor name/devt/spectype conversion, property-list duplication/search/refcounting, driver conf load/unload, node state getters/setters, driver detach, binding name update, bulk bind/unbind, pathname-to-devinfo resolution, prom-path to devfs-path conversion, pseudo/hardware node attach, attached-device checks, and PCI dip detection.

Cache and persistence-related declarations include `/etc/devices` cache initialization/read/cleanup, devid cache init/read/cleanup, devid discovery/register/unregister/devt-list conversion, and retire-store persistence operations.

Resource-control hooks are declared for locked memory accounting, and `preroot_walk_block_devices()` supports early filesystem/block-device discovery before root is mounted. Its callback uses `PREROOT_WALK_BLOCK_DEVICES_NEXT` and `PREROOT_WALK_BLOCK_DEVICES_CANCEL`.

Research notes:
- This is a declaration hub for DDI implementation internals rather than a standalone subsystem.
- Functions are mostly `i_ddi_*`, `impl_*`, or `e_*` private interfaces.
- Several routines are boot/autoconfiguration sensitive; callers likely depend on ordering around root nexus initialization and `/etc/devices` cache reads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_implfuncs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr.h

This is the public DDI interrupt interface header for kernel drivers. It defines interrupt return conventions, interrupt types, priorities, capability flags, opaque interrupt handles, handler typedefs, allocation behavior flags, and both modern and legacy interrupt APIs.

The modern interrupt model supports fixed, MSI, and MSI-X interrupts through `DDI_INTR_TYPE_FIXED`, `DDI_INTR_TYPE_MSI`, and `DDI_INTR_TYPE_MSIX`. Drivers query supported types, number of interrupts, available interrupts, allocate/free handle arrays, query/set capabilities, query/set priority, add/duplicate/remove handlers, enable/disable individual or block interrupts, mask/unmask interrupts, query pending state, and set requested interrupt count.

Soft interrupt support uses `ddi_softint_handle_t` plus `ddi_intr_add_softint`, remove, trigger, and priority get/set calls. Priority constants distinguish hardware priority ranges from soft interrupt preferences.

The file includes `ddi_intr_impl.h` when `_KERNEL` is set, so public handle declarations are paired with private implementation layout for kernel consumers. Legacy APIs are retained for older drivers: `ddi_intr_hilevel`, `ddi_get_iblock_cookie`, `ddi_dev_nintrs`, `ddi_add_intr`, `ddi_add_fastintr`, `ddi_remove_intr`, and older softintr routines.

Research notes:
- Return values `DDI_INTR_CLAIMED` and `DDI_INTR_UNCLAIMED` are the ISR contract.
- New code should prefer the `ddi_intr_*` handle-based APIs over legacy `ddi_add_intr`/`ddi_add_fastintr`.
- MSI-X handler duplication and block enable behavior are backed by private state in `ddi_intr_impl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr_impl.h

This is the private implementation header for the DDI interrupt framework. It defines interrupt bus operation opcodes, handle internals, soft interrupt internals, MSI-X state, interrupt resource management pools and requests, per-devinfo interrupt state, private helper prototypes, and legacy intrspec support.

`ddi_intr_op_t` enumerates nexus interrupt operations: supported types, interrupt counts, allocation/free, priority get/set, ISR add/remove, duplicate vector, enable/disable, block enable/disable, capability get/set, mask/unmask, pending query, available count, resource pool access, and target get/set.

`ddi_intr_handle_impl_t` is the in-core representation of a `ddi_intr_handle_t`. It records dip, interrupt type, inum, vector, version, state, capabilities, priority, per-handle rwlock, callback function/args, MSI-X duplication flags and main handle pointer, platform-private data, scratch fields used by framework/nexus handoff, and a target processor snapshot.

The internal state flags track allocated, handler-added, and enabled states. Validation macros check interrupt type and allocation behavior. MSI-X allocation constants set default/min/max allocation behavior. `ddi_intr_msix_t` stores MSI-X table and PBA access handles, addresses, offsets, and device access attributes.

Interrupt Resource Management is represented by `ddi_irm_pool_t`, `ddi_irm_req_t`, and `ddi_irm_params_t`. Pools track interrupt vector supply, policy, requested/reserved counts, locks, condition variables, balancing thread, owner dip, and request lists. Requests attach a device to a pool with type, requested/available counts, scratch state, and list linkage.

`devinfo_intr_t` is the per-device interrupt cache used from `struct dev_info`. It stores supported types, MSI-X data, current type/count/enabled count, legacy handle array, x86 PCI config handle/capability pointer, and optional IRM request.

The bottom section preserves `struct intrspec` for old DDI interrupt interfaces and declares obsolete intrspec operations. It also declares affinity helpers, `i_ddi_intr_ops`, softint helpers, devinfo interrupt init/fini, state getters/setters, IRM operations, handle lookup, MSI-X getter/setter, x86 PCI config helper accessors, interrupt weight accessors, and platform handle allocation/free.

Research notes:
- This file is private and tightly coupled to `devops.h` bus operation revisioning.
- `NEXUS_HAS_INTR_OP()` requires busops revision at least 9 and a `bus_intr_op`.
- IRM introduces asynchronous balancing/threading state; pool locks and flags are important for correctness.
- Legacy intrspec APIs coexist for old driver compatibility but are explicitly obsolete.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_obsolete.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_obsolete.h

This header collects obsolete DDI interfaces that remain available when `_DDI_STRICT` is not defined. It includes basic types, DDI opaque types, and LDI event types.

It declares legacy `strtol`/`strtoul` and obsolete memory and I/O accessor functions. The `ddi_mem_get*`, `ddi_mem_put*`, `ddi_mem_rep_get*`, and `ddi_mem_rep_put*` families operate through access handles on memory mappings. The `ddi_io_get*`, `ddi_io_put*`, `ddi_io_rep_get*`, and `ddi_io_rep_put*` families provide older I/O-space accessors.

The file also declares obsolete LDI event interfaces: `ldi_get_eventcookie`, `ldi_add_event_handler`, and `ldi_remove_event_handler`.

Research notes:
- The entire functional surface is hidden under `#ifndef _DDI_STRICT`.
- New code should avoid these symbols in favor of current DDI access and LDI event APIs.
- This file exists for compatibility and source migration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_obsolete.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_periodic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_periodic.h

This private kernel header defines the implementation backing the DDI periodic handler interface. It includes list, taskq, and cyclic infrastructure.

It defines an opaque `timeout_t` for `i_timeout()` and `i_untimeout()`, periodic state flags (`DPF_DISPATCHED`, `DPF_EXECUTING`, `DPF_CANCELLED`), and `ddi_periodic_impl_t`, the in-core record for a registered periodic handler.

`ddi_periodic_impl_t` stores global and softint list links, an id, interval, lock/cv, state flags, interrupt/taskq dispatch level, taskq entry for level zero work, fire count, current executing thread, cyclic id, callback function, and callback argument.

Private lifecycle and dispatch functions are declared: `ddi_periodic_init`, `ddi_periodic_fini`, `ddi_periodic_softintr`, `i_timeout`, and `i_untimeout`.

Research notes:
- This is kernel-only implementation state, not the public `ddi_periodic_add`/remove surface.
- It bridges cyclic timers, taskq dispatch, soft interrupts, and cancellation synchronization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_periodic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm.h

This header defines the public user/kernel ABI and kernel driver interface for DDI UFM, the Unified Firmware Management facility. It exposes `/dev/ufm`, UFM interface versioning, UFM ioctls, packed nvlist schema keys, capability bits, slot attributes, ioctl payload structures, and kernel driver callbacks.

The ioctl family is based on `UFM_IOC`: `UFM_IOC_GETCAPS`, `UFM_IOC_REPORTSZ`, `UFM_IOC_REPORT`, and `UFM_IOC_READIMG`. The current version is `1`. Capabilities include reporting UFM information and reading firmware images.

User ABI structures include `ufm_ioc_getcaps_t`, `ufm_ioc_bufsz_t`, `ufm_ioc_report_t`, and `ufm_ioc_readimg_t`, each carrying version and device path fields. Kernel-only 32-bit forms are provided for buffer size, report, and read-image payloads. The read-image 32-bit form is packed to preserve ABI layout.

The report format is a packed nvlist. Top-level data contains `ufm-images`; each image can contain description, optional image misc nvlist, and an array of slot nvlists. Slot data includes version, attributes, optional misc nvlist, and optional image size. Attributes include readable, writeable, active, and empty, with `DDI_UFM_ATTR_MAX` as the valid mask.

Kernel driver-facing declarations define opaque handle/image/slot types and `ddi_ufm_ops_t`: callbacks for image count, filling image metadata, filling slot metadata, getting capabilities, and reading an image. Drivers call `ddi_ufm_init`, `ddi_ufm_update`, and `ddi_ufm_fini`, and use setters in fill callbacks to populate images and slots.

Research notes:
- This header is both user ABI and kernel DDI interface.
- Packed nvlist key names are ABI-visible and must be preserved.
- `UFM_IOC_MAX` is currently set to `UFM_IOC_REPORT`, even though `UFM_IOC_READIMG` exists; consumers should verify ioctl range logic in implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm_impl.h

This is the private kernel implementation header for DDI UFM. It includes AVL tree, public UFM definitions, mutex, nvpair, and base types.

It defines `ddi_ufm_state_t` flags for initialized, ready, and shutting-down handle states. Private functions include `ufm_init()` for DDI startup, `ufm_find()` for the `/dev/ufm` driver to locate a registered handle by path, `ufm_cache_fill()` to build cached report state, and `ufm_read_img()` to service firmware image reads with model-aware copy semantics.

Private structures mirror the public report model. `struct ddi_ufm_slot` stores slot number, version string, attributes, image size, and misc nvlist. `struct ddi_ufm_image` stores image number, description, misc nvlist, slot array, and slot count. `struct ddi_ufm_handle` stores lock, device path, ops vector, driver argument, state, version, lazily cached images/count/capabilities/report nvlist, and AVL linkage.

Research notes:
- The handle explicitly separates driver-provided state from lazily cached report state.
- Correct locking around `ufmh_state` and cached report fields is central to avoiding detach/update races.
- This file is implementation-private and should not be consumed by ordinary drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidevmap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidevmap.h

This header defines kernel devmap and user-memory mapping implementation types and public devmap-related flags. It includes `sys/mman.h` under `_KERNEL`.

Kernel-private structures include `devmap_info`, `ddi_umem_cookie`, `devmap_callback_ctl`, `devmap_softlock`, `devmap_ctx`, devmap fault/read-write enums, and `devmap_handle_t`. These represent driver mappings into user address spaces, umem-backed mappings, soft locking, CPU-context tracking, and callback operations for map/access/dup/unmap.

`ddi_umem_cookie_t`, `ddi_as_handle_t`, `devmap_pmem_cookie_t`, and `devmap_cookie_t` are opaque or semi-opaque mapping handles. `struct ddi_umem_cookie` records allocation size, virtual address, lock, type, page array, owning process/address space, segment flags, lock count, cleanup callbacks, reference count, unlock-list linkage, and locked-memory resource-control tracking.

Devmap callback versioning is `DEVMAP_OPS_REV`. Driver setup flags include defaults, invalid mapping, allow remap, and use page size. Internal handle flags include setup done, lock initialized, locked, and large-page mapping.

Umem allocation and lock flags include sleep/nosleep, pageable, trash mappings, and read/write expected access for `ddi_umem_lock`. The comments warn that VM read/write meaning can be opposite to I/O `B_READ`/`B_WRITE`.

Research notes:
- This header is closely tied to `segdev`, `segkp`, page locking, HAT attributes, and mmap/devmap callbacks.
- Locking and callback lifetime are sensitive: long-term umem cleanup callbacks can occur after a lock call.
- Public drivers mostly see flags and opaque handles, while the kernel implementation sees full structure layouts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidevmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidmareq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidmareq.h

This header defines DMA object descriptions, DMA limits/attributes, DMA request structures, mapping flags, return codes, synchronization flags, legacy DMA control ops, and I/O memory cache attributes.

DMA source/destination objects can be virtual addresses, page lists, physical addresses, buffer virtual addresses, or DVMA addresses. The object model is represented by `v_address`, `pp_address`, `phy_address`, `dvma_address`, `ddi_dma_aobj_t`, `ddi_dma_atyp_t`, and `ddi_dma_obj_t`.

DMA limits are architecture-specific. SPARC `ddi_dma_lim_t` describes low/high DMA address range, counter maximum, burst sizes, minimum transfer, and expected DMA speed. x86 extends this with versioning, address register max, count register max, granularity, scatter/gather length, and request size, with `DMA_UNIT_8/16/32` and `DMALIM_VER0`.

Modern `ddi_dma_attr_t` describes DMA address range, counter limit, alignment, burst sizes, minimum and maximum transfer, segment boundary, scatter/gather length, granularity, and bus-specific flags. Attribute flags include forced physical DMA, error flagging, relaxed ordering, and a private bounce-on-segment flag.

`ddi_dma_req_t` packages optional limits, allocation flags, callback/sleep behavior, callback argument, and the DMA object. Callback constants distinguish no-wait, sleep, and callback-based resource wait; callback return values indicate runout or done.

DMA mapping flags include read/write direction, redzone, partial mapping, consistent mapping, exclusive mapping, streaming, and SBus 64-bit support. Return codes distinguish mapped, partial, done, no resources, no mapping, too big/small, locked, bad limits, stale, bad attributes, in use, and physical-DMA fallback.

Synchronization flags specify consistency for device, CPU, or kernel view. The `ddi_dma_ctlops` enum preserves many obsolete bus nexus control operations plus resource reserve/release, SBus64, remap, and motherboard DMA engine operations. Cache attribute flags define cached, write-combining, and uncached I/O memory behavior with helper macros.

Research notes:
- This file is foundational for both old and newer DDI DMA APIs.
- ABI varies by architecture, especially `ddi_dma_lim_t`.
- Many enum members are explicitly obsolete but remain required by bus ops and legacy callers.
- Cache-attribute flags are mutually exclusive and used to override HAT attributes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidmareq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm.h

This header defines the public kernel DDI fault-management interface for drivers. It includes DDI types and varargs support, and declares `ddi_system_fmcap`.

It defines FMA return statuses (`DDI_FM_OK`, fatal, nonfatal, unknown), driver capability flags for ereport generation, access-handle checking, DMA-handle checking, and error callbacks, plus convenience macros to test capabilities.

Error expectation values distinguish unexpected errors, expected errors, poke, and peek. Kernel-only `ddi_fm_error_t` carries structure version, status, expectation flag, ENA, optional access and DMA handles, bus-specific error data, and bus type. Bus types include default and PCI.

The file declares driver-facing FMA calls: `ddi_fm_ereport_post`, `ndi_fm_ereport_post`, `ddi_fm_service_impact`, handler register/unregister, `ddi_fm_init`, `ddi_fm_fini`, capability query, and access/DMA error get/clear calls.

Research notes:
- Drivers use this to harden device access and DMA paths and report service impact.
- Capabilities are negotiated through `ddi_fm_init` and can be influenced by system-wide FMA capability.
- Access/DMA error handling integrates with private caches in `ddifm_impl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm_impl.h

This is the private implementation header for DDI fault management. It includes DDI types and error queue support.

It defines internal FMA kstats, maximum ereport class size, stack depth, and symbol size. `i_ddi_errhdl` stores an error-handler callback and implementation argument. Fault-management resource cache structures track active access or DMA handles and bus-specific state.

`i_ddi_fmhdl` is the per-devinfo fault-management handle. It stores lock and owner, DMA/access caches, owning dip, kstat pointer, capability level, kstats, error queue, optional FMRI nvlist, interrupt block cookie, registered child targets, and bus-specific FM state.

PCI error table entries are represented by `pci_fm_err_t`, and `pci_err_tbl[]` is declared. Kernel-private declarations include global initialization, driver defect ereport posting, handler enter/exit/ownership checks, access/DMA error set and comparison-function getters, busop access enter/exit, busop FM init/fini, and FMA cache create/destroy.

Research notes:
- This header backs `ddifm.h` and is not driver-facing.
- `i_ddi_fmhdl` is referenced from `struct dev_info` in `ddi_impldefs.h`.
- Cache and handler ownership tracking are central to avoiding recursive or misattributed FMA handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddimapreq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddimapreq.h

This header defines the private DDI bus mapping request structure and related return codes. It includes mmap protections and DDI types.

Kernel-only `ddi_map_obj_t` can hold either an rnumber or a `regspec *`; `ddi_map_type_t` distinguishes those forms. `ddi_map_op_t` covers unlocked map, locked map, handle-only map, unmap, and unlock-without-unmap operations. `ddi_map_req_t` packages the operation, object type/value, mapping flags, protection bits, access-handle pointer, and version.

Mapping version is `DDI_MAP_VERSION`. Mapping flags distinguish user mapping, kernel mapping, device mapping, and a platform-reserved high-bit x86 extended regspec flag.

The public error codes are negative values for generic errors, unimplemented operator, no resources, unsupported operation, regspec/rnumber range errors, and invalid input.

Research notes:
- This is a bus nexus/private framework contract, not a typical driver API.
- The x86 extended regspec bit is reserved for children of the x86 root nexus.
- Mapping semantics depend on `regspec` layout from `ddi_impldefs.h` and mmap protection flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddimapreq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddipropdefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddipropdefs.h

This header defines DDI property implementation types, property operation enums, property flags, encoded property handle operations, return codes, common property names, and debugging hooks.

`ddi_prop_op_t` describes property operation mode: length only, length plus caller buffer, length plus allocated buffer, or existence check. `ddi_prop_t` is the in-kernel software property node, storing next pointer, matching dev_t, property name, flags, length, and value pointer. `ddi_prop_list_t` wraps a reference-counted list.

Encoded property access is represented by `prop_handle_t` and `prop_handle_ops_t`, with ops for int, string, byte, and int64 data. Command enum values request encoded size, decoded size, decode, encode, or skip. Result values distinguish encoding/decoding error, end of data, and success/positive size.

The file defines IEEE 1275 property cell helpers, property handle flags, property return codes, and a large set of property flags: don't pass to parent, can sleep, system-defined, not PROM, don't sleep, stack create, undefine, hardware-defined, typed int/string/byte/composite/int64, LDI dev_t wildcard, unbound DLPI2 lookup, typed consumer expansion, dynamic driver prop_op lookup, and rootnex global lookup.

Common dev_t/major constants include `DDI_DEV_T_NONE`, `DDI_DEV_T_ANY`, `DDI_MAJOR_T_UNKNOWN`, and `DDI_MAJOR_T_NONE`. Common root properties include `relative-addressing` and `generic-addressing`.

It declares `ddi_prop_search_common()` and optional property debugging support under `DDI_PROP_DEBUG`.

Research notes:
- This is private to property implementation, despite being included by public-adjacent DDI code.
- Typed property flags and older untyped lookup compatibility are intertwined.
- Property values are stored by reference, so allocation/free ownership matters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddipropdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dditypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dditypes.h

This header defines fundamental DDI opaque types and small ABI-visible DDI structures. It includes ISA definitions and base types outside assembly.

It declares opaque DMA handles, DMA window and segment handles, DMA cookies, interrupt cookie types, register and interrupt spec handles, soft interrupt IDs, devinfo handles, devmap data handles, device IDs, event cookies, callback IDs, and periodic handles. `ddi_dma_cookie_t` provides a 64-bit DMA address view plus 32-bit address aliases that respect data-model byte order.

Device-id constants enumerate SCSI WWN/serial, fabric, encapsulated, ATA serial, SCSI VPD T10/EUI/NAA, NVMe namespace id/EUI64/NGUID, and max type. It also defines encode-version constants and minor-name wildcard constants for devid lookup.

`ddi_node_state_t` defines the device node lifecycle state sequence from invalid/proto through linked, bound, initialized, probed, attached, and ready. Comments warn that `DS_ATTACHED` and `DS_READY` should generally not be used outside devcfg state model code.

Kernel-only access definitions include `ddi_device_acc_attr_t`, device attribute versions, endian flags, data ordering modes, data-size constants, `ddi_acc_handle_t`, full `ddi_acc_hdl_t`, `peekpoke_ctlops_t`, and access protection mode constants (`DDI_DEFAULT_ACC`, `DDI_FLAGERR_ACC`, `DDI_CAUTIOUS_ACC`).

Research notes:
- This is a low-level type foundation used by many other headers in this group.
- Several types are intentionally opaque to keep public ABI separated from private implementation.
- `ddi_acc_hdl_t` is kernel-private full state for data access mappings and is referenced by mapping and access routines.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dditypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/debug.h

This header defines illumos assertion, verification, and compile-time assertion macros. It includes ISA definitions outside standalone builds, base types, and note annotations.

`VERIFY()` always evaluates and calls `assfail()` on false. `ASSERT()` does so only in debug builds and is a no-op otherwise. `ASSERT32` and `ASSERT64` select assertions based on data model.

`IMPLY()` and `EQUIV()` are debug-only logical assertion helpers. The `VERIFY3*` and `ASSERT3*` families compare two values and report the left value, operator, and right value through `assfail3()`. Variants cover boolean, signed, unsigned, pointer, and zero comparisons. `CTASSERT()` maps to C11 `_Static_assert`.

Kernel/fake-kernel declarations include `abort_sequence_enter()` and `debug_enter()`. The `STATIC` macro becomes empty for non-Sun DEBUG builds, otherwise `static`, supporting debug visibility during non-Sun builds.

Research notes:
- `VERIFY*` macros keep side effects in both debug and non-debug builds; `ASSERT*` macros do not.
- `ASSERT3*` macros evaluate arguments once into typed temporaries.
- This is a foundational header frequently used across kernel code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/des.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/des.h

This header defines the generic, hardware-independent DES driver ioctl interface. It includes `sys/ioccom.h`.

It defines maximum block operation length (`DES_MAXLEN`) and quick inline data length (`DES_QUICKLEN`). Direction enum values are encrypt and decrypt; mode enum values are CBC and ECB.

`struct desparams` contains the 8-byte key, direction, mode, 8-byte initialization vector, data length, and a union that either embeds quick data or points to a larger buffer. Macros alias the union members as `des_data` and `des_buf`.

Two ioctls are defined: `DESIOCBLOCK` for arbitrary-sized buffers and `DESIOCQUICK` for small data passed directly in the structure.

Research notes:
- This is a legacy crypto ioctl ABI, not modern kernel crypto framework API.
- Structure layout and ioctl numbers are user-visible.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/des.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache.h

This kernel header defines the client-facing interface for cached `/etc/devices` nvlist-backed files. It includes list support.

`nvf_handle_t` is an opaque handle returned to clients that register a cache file. `nvf_ops_t` describes a cache file: path, unpack callback, pack callback, list-free callback, and write-complete callback.

Client interfaces include `nvf_register_file`, `nvf_read_file`, `nvf_wake_daemon`, `nvf_error`, `nvf_cache_name`, `nvf_lock`, `nvf_list`, `nvf_mark_dirty`, and `nvf_is_dirty`.

Research notes:
- This is kernel-only and supports clients such as devid cache and other device-state persistence.
- Clients own logical list contents but use the devcache framework for nvlist file persistence and daemon wakeups.
- Implementation details live in `devcache_impl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache_impl.h

This private implementation header defines the on-disk packed nvlist file header and in-kernel descriptors for `/etc/devices` cache persistence.

The file format header uses magic `NVPF_HDR_MAGIC`, version `NVPF_HDR_VERSION`, fixed header size `NVPF_HDR_SIZE`, and `nvpf_hdr_t` with size, header checksum, and payload checksum fields plus padding for future extension.

Kernel-only `kfile_t` wraps vnode-based kernel file I/O state: vnode pointer, flags, filename, file position, and state. `nvfd_t`/`struct nvfiledesc` is the registered cache file descriptor, storing client ops, state flags, data list, rwlock, and global list linkage.

`NVF_F_*` flags track dirty, flushing, error, read-only, create-message, and rebuild-message states. Helper macros test/mark/clear dirty state and mark read-only state. Shorthand macros access the client ops vector.

The file declares `kfio_report_error`, defines temporary filename suffix constants, and debug macros for the nvpacked daemon and kernel file I/O under `DEBUG`.

Research notes:
- File header format is persistent and should be treated as ABI for existing `/etc/devices` cache files.
- The dirty/flushing/read-only flags coordinate asynchronous flush behavior.
- This header depends on `nvf_ops_t` from `devcache.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devctl.h

This header defines the devctl ioctl ABI used by libdevice, nexus drivers, attachment-point management, power-management tests/controls, and LED controls. It includes base types and nvpair.

`struct devctl_iocdata` is the ioctl payload shared between libdevice interfaces and nexus driver devctl handling. It stores command, flags, copyout buffer, packed user nvlist pointer/size, child node name, and unit address. A 32-bit version exists for syscall32. `DEVCTL_MAX_NVL_USERSZ` limits packed user attributes to 64 KiB.

Attachment point state enums describe receptacle state, occupant state, and condition. `devctl_ap_state_t` and its 32-bit form report AP state, condition, last-change time, error code, and transition flag.

The ioctl namespace is `DEVCTL_IOC`. Commands cover bus quiesce/unquiesce/reset/getstate/configure/unconfigure/device-create, device online/offline/getstate/reset/remove, AP connect/disconnect/insert/remove/configure/unconfigure/getstate/control, PM busy/idle/power transitions/test controls, PROM printf, suspend failure simulation, resume power-change markers, and LED set/get/count.

State bit definitions report device online/busy/offline/down and bus active/quiesced/shutdown. `IS_DEVCTL()` checks the ioctl range. `DC_DEVI_NODENAME`, construction/offline flags, and LED control structures/constants round out the ABI.

Research notes:
- This header is user/kernel ABI and should be changed cautiously.
- Applications are expected to use libdevice rather than direct structure access.
- Several PM ioctls are diagnostic/test hooks and not generic hotplug controls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devfm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devfm.h

This header defines `/dev/fm` ioctl interfaces and packed nvlist schemas for FMA consumers. It includes base types and nvpair.

It sets maximum input/output buffer sizes, driver version, version-key strings, and ioctl commands under `FM_IOC`. Generic commands include versions, page retire/status/unretire, and cache info. x86-specific commands include physical CPU info, CPU retire/status/unretire, legacy topology generation, and CPU PCI data.

`fm_ioc_data_t` carries interface version, input packed nvlist size/buffer, output packed nvlist size/buffer, and has a kernel-only 32-bit form. Most operation data is encoded as packed nvlist keys defined in this file.

The schema includes keys for page retire FMRI, CPU lists, chip/core/strand IDs, old status, topology legacy data, cache CPU count, physical CPU vendor/family/model/stepping/chip/core/strand/APIC/SMBIOS/root/revision/socket/cpuid/identifier string fields, cache metadata, and PCI data fabric records.

`fm_cache_info_type_t` describes data, instruction, and unified caches. Cache info keys include level, type, sets, ways, line size, total size, fully-associative boolean, synthetic cache id, and x86 APIC shift.

Research notes:
- The ioctl payload is a packed nvlist ABI; key names are as important as structs.
- Some operations are architecture-gated under `__x86`.
- Buffer-size constants constrain user/kernel copy behavior for FMA management data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devfm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devid_cache.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devid_cache.h

This private kernel header defines the devid cache nvlist identifiers, in-memory cache records, tunables, and debug logging macros.

The persistent `/etc/devices/devid_cache` top-level nvpair identifier is `DP_DEVID_ID`. Kernel record `nvp_devid` stores a list node, device id, registered path, devinfo pointer, and flags. Flags distinguish registered entries and entries with a current dip.

Tunables control boot/postboot devid discovery, always-discover behavior, discovery interval, and cache read/write disable flags. `devid_report_error` enables more verbose error reporting even in non-debug kernels.

Under `DEBUG`, logging macros gate registration, find, lookup, match, path, error, discovery, hold, unregister, remove, stale, and detach messages. Helpers print debug path and devid information. Non-debug builds compile these away except `DEVIDERR`, which remains controlled by `devid_report_error`.

Research notes:
- This header supports the private devid persistence machinery declared in `ddi_implfuncs.h`.
- Cache entries bridge persistent device IDs, paths, and live devinfo nodes.
- Logging knobs are intentionally granular because devid discovery can be noisy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devid_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devinfo_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devinfo_impl.h

This private/public-adjacent header defines the devinfo driver ioctl flags and the snapshot data structures copied to userland/libdevinfo. It is separate from `libdevinfo.h` because the devinfo driver must know copy sizes before libdevinfo is built.

The ioctl namespace is `DIIOC`. Snapshot flags request subtree, minor data, properties, I/O pathing, private data, force-load all drivers, cached data, cleanup, layering, and hotplug data. Straight ioctl commands include userland copyout, load driver, and identify. `DI_MAGIC` is returned by identify.

Snapshot format constants include operation kind bits, property list kinds, max tree depth, private pointer count, snapshot version, private-data version, endian constants, cache magic, cache permissions, and cache snapshot flags. Cast macros convert offsets/pointers to snapshot structure types.

The snapshot structures include `di_all`, `di_devnm`, layered link endpoint/linkage structures, `di_node`, `di_minor`, `di_path`, `di_hp`, `di_path_prop`, `di_prop`, private data formatting records, aliases, and `dinfo_io`. These encode exported node metadata, minor nodes, properties, pathing/multipath state, hotplug state, layering, and private prtconf support.

`di_path_state_t` defines unknown, offline, standby, online, and fault path states. Path snapshot flags indicate missing endpoints, endpoint postprocessing, missing client/phci links, and link postprocessing. Removed-device path flags mirror device removal state.

Research notes:
- This is an ABI-sensitive snapshot format for libdevinfo/devinfo driver coordination.
- Many fields are offsets into a copied snapshot rather than live kernel pointers.
- Version constants and structure sizes must be preserved for cached snapshots and mixed user/kernel consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devinfo_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devops.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devops.h

This header defines the core illumos driver operation vectors: `cb_ops`, `bus_ops`, legacy `bus_ops_rev1`, and `dev_ops`. It is the main contract between device drivers/nexus drivers and the kernel DDI framework.

`cb_ops` describes character/block/STREAMS leaf operations such as open, close, strategy, print, dump, read, write, ioctl, devmap, mmap, segmap, chpoll, prop_op, STREAMS tab pointer, flags, revision, aread, and awrite. Comments identify which entries correspond to DDI/DKI and obsolete interfaces.

`bus_ops` describes nexus operations: map, get/add/remove intrspec legacy hooks, DMA map/allochdl/freehdl/bind/unbind/flush/window/control, prop_op, ctl, DMA control legacy op, bus quiesce/unquiesce/bus reset/device reset, FMA init/fini/access enter/access exit/error handler, power, configure/unconfigure, and interrupt operations. Revision constants run through `BUSO_REV_10`.

`bus_ops_rev1` is retained for old busops layout compatibility. `dev_ops` stores revision, refcount, getinfo, identify, probe, attach, detach, reset, cb_ops pointer, bus_ops pointer, power, and quiesce.

Enums define getinfo command, attach commands, detach commands, and reset commands. Probe result constants map to familiar `ENXIO`/`nulldev` behavior. `DDI_DEFINE_STREAM_OPS` builds a `dev_ops`/`cb_ops` pair for STREAMS drivers.

Research notes:
- This file is one of the most ABI-sensitive headers in the DDI.
- Bus operation revision gates availability of newer callbacks such as `bus_intr_op`.
- Legacy fields remain in structure layout even when comments say obsolete.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpolicy.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpolicy.h

This header defines device policy data structures and kernel APIs for privilege-gated device access. It includes types, privilege sets, param, and vnode.

`devplcysys_t` is the system-call interface structure, carrying major number, minor name, wildcard flags, and variable privilege set data. Macros compute its size and read/write privilege-set pointer locations.

`devplcy_t` is the kernel policy object with reference count, generation, flags, read and write privilege sets, and optional minor name. The file declares `nullpolicy`, global generation counter, refcount helpers, lookup by vnode, initialization, load/get/get-by-name syscalls, and privilege lookup by name.

Token names identify read and write privilege-set fields. Limits include `MAXDEVPOLICY` and default-major marker `DEVPOLICY_DFLT_MAJ`.

Research notes:
- Device policy ties device special files to privilege requirements.
- The system-call payload is variable-sized due to embedded privilege sets.
- Generation count supports cache invalidation or policy freshness checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpolicy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpoll.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpoll.h

This header defines `/dev/poll` ioctl ABI and kernel entry bookkeeping. It includes poll implementation and 32-bit type support.

Ioctls under `DPIOC` include `DP_POLL`, `DP_ISPOLLED`, `DP_PPOLL`, and `DP_EPOLLCOMPAT`. `DEVPOLLSIZE` is the table growth increment.

`dvpoll_t` is the user ioctl payload with pollfd array pointer, fd count, timeout in milliseconds, and optional signal set pointer. `dvpoll32_t` is the 32-bit ABI version. `dvpoll_epollfd_t` places `pollfd_t` first and adds a 64-bit epoll-compatible payload.

Kernel-only `dp_entry_t` stores a lock, pollcache pointer, reference count, writer wait count, flags, and cv. Flags track writer presence and epoll compatibility mode. `DP_REFRELE` decrements entry references with an assertion.

Research notes:
- This is a user-visible ABI for `/dev/poll`, including syscall32 layouts.
- The epoll compatibility structure depends on `pollfd_t` being the first member.
- Kernel entry locking protects concurrent ioctl and write/update paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpoll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dirent.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dirent.h

This header defines filesystem-independent directory entry structures and `getdents` large-file interface mapping. It includes feature-test definitions.

`dirent_t` contains inode number, directory offset, record length, and variable-length name. A kernel syscall32 `dirent32_t` form uses 32-bit inode/off_t fields. Under `_LARGEFILE64_SOURCE`, `dirent64_t` uses 64-bit inode and offset fields.

Kernel/fake-kernel helpers compute aligned record length and name length for 64-bit and 32-bit dirent layouts. `MAXGETDENTS_SIZE` caps bytes stored by `getdents(2)` in user buffers at 64 KiB.

For userland, large-file compilation mappings redirect `getdents` to `getdents64` on ILP32 with `_FILE_OFFSET_BITS=64`, and map `getdents64`/`dirent64` back to native on LP64. The file declares `getdents(int, struct dirent *, size_t)` and deliberately does not provide a transitional large-file function declaration.

Research notes:
- This is user ABI and kernel ABI for directory entry record layout.
- Alignment macros are important for filesystem `getdents` implementations.
- Feature-test macros control visible names and large-file symbol mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/disp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/disp.h

This header defines dispatcher queue structures, scheduler priority bounds, kernel preemption helpers, and dispatcher function declarations. It includes priocntl, thread, and scheduling class definitions.

`dispq_t` represents one dispatcher queue entry with first/last thread pointers and runnable count. `disp_t` is the per-CPU dispatcher state: queue pointer, lock, runnable count, current max run priority, max unbound priority, queue limit, last rundown time, steal counters, kernel-preemption queue data, owning CPU pointer, and related state.

Priority constants define system class priority bounds. `DISP_MAXRUNPRI()` reads a thread’s dispatcher queue max priority. Kernel globals include swapped thread count, no-steal timing, idle/preemption hooks, and dispatcher enqueue hooks.

Function declarations cover queue allocation/free, dequeue, initialization, class registration, interrupt state checks, preemption/switch/resume paths, run queue enqueue variants, CPU rechoose/surrender, kernel preemption, CPU selection, bound-thread checks, CPU dispatcher lifecycle, priority adjustment, swapped enqueue, and work detection. `KPREEMPT_SYNC`, `kpreempt_disable`, `kpreempt_enable`, and `CPU_IDLE_PRI` define preemption controls.

Research notes:
- This header belongs to the scheduler/dispatcher rather than DDI, but appears in the same sys header group.
- Several functions are low-level context-switch paths and include `__NORETURN` declarations.
- Dispatcher structure layout is kernel-private and CPU/scheduler sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/disp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkbad.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkbad.h

This legacy disk header defines structures for DEC STD 144-style bad sector forwarding. It has no includes.

The comments describe bad-sector information stored in the first five even-numbered sectors of the last track of the disk pack, with up to 126 bad sectors supported. The alternate sectors are located in the last track of the `c` filesystem partition.

`NDKBAD` is 126. `struct dkbad` stores cartridge serial number, bad-sector table size, and an array of bad track/sector entries. Nested `struct bt_bad` stores cylinder, track, and sector.

Research notes:
- This is legacy disk metadata support retained for compatibility.
- The structure layout is disk-format/user-visible for old tools or drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkbad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkio.h

This header defines the disk ioctl ABI, disk geometry/info structures, media metadata, write-cache controls, partition queries, firmware update structures, directed read structures, disk ID structures, and free/discard ioctls. It includes `sys/dklabel.h`.

`dk_cinfo` reports controller name/type/flags, controller and unit numbers, partition, max transfer, and slave number. Controller type constants include old controller classes, SCSI, IDE/direct, PCMCIA, virtual block device, and generic block device. Controller flags describe formatting and bad-sector behavior.

Geometry and partition structures include `dk_allmap`, 32-bit map form, and `dk_geom`. The ioctl namespace is `DKIOC`, with commands for geometry, info, eject, VTOC/extVTOC get/set, write-cache flush/get/set, physical/virtual geometry, lock/unlock, media state/removable/hotpluggable/solid-state, defect lists, partition info, erase-bypass controls, media info, mboot get/set, temperature, read-only state, EFI get/set, and historical partition query aliases.

`dk_callback` supports asynchronous write-cache flushing in kernel `FKIOCTL` mode. `dkio_state` reports inserted/ejected/gone state. `dk_temperature`, `dk_minfo`, `dk_minfo_ext`, and 32-bit media info forms describe media type, block size, capacity, and logical/physical block geometry. Media type constants cover optical, fixed disk, floppy, ZIP, and JAZ classes.

Volume capability and directed mirror read support use `volcap_t`, `vol_directed_rd_t`, and 32-bit form, with ABR/DMR capability bits and directed-read status bits. Disk identity support uses `dk_disk_id_t` with ATA/SCSI strings and type flags. Firmware update support uses `dk_updatefw_t` and 32-bit form plus temporary/permanent firmware type constants.

Free/discard support defines `DKIOCFREE`, `DF_WAIT_SYNC`, extent and list structures (`dkioc_free_list_ext_t`, `dkioc_free_list_t`), size macro `DFL_SZ`, and `DKIOC_CANFREE`.

Research notes:
- This is a large user/kernel ABI header; structure layout and ioctl numbers are externally visible.
- Some ioctl numbers overlap by design/history: `DKIOCSETEXTPART` and `DKIOC_GETDISKID` both use `DKIOC|46`.
- Several older commands are obsolete but retained for compatibility.
- `dkioc_free_util.h` provides kernel copyin/iteration helpers for `DKIOCFREE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkioc_free_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkioc_free_util.h

This kernel helper header supports safe handling of the `DKIOCFREE` discard/free ioctl payload defined in `dkio.h`.

It defines `DFL_COPYIN_MAX_EXTS` as the maximum number of extents accepted during copyin and `DFL_ISSYNC()` to test whether a copied free list requested synchronous completion through `DF_WAIT_SYNC`.

`dkioc_free_info_t` stores normalized information needed to validate or translate a free-list request: flags, number of extents, structure sizes, extent offset fields, extent length fields, and total request size. This allows one implementation to handle native and model-specific layouts.

`dfl_iter_fn_t` is the callback type used when iterating normalized free-list extents. The declared helpers are `dfl_copyin()` to copy and validate user input, `dfl_free()` to release it, and `dfl_iter()` to iterate extents with a caller-supplied function.

Research notes:
- This file is kernel-only and exists to avoid open-coded `DKIOCFREE` copyin/parsing.
- The maximum extent count protects the kernel from excessive allocation.
- It depends directly on `dkioc_free_list_t` from `dkio.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkioc_free_util.h -->