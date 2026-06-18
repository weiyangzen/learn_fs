# Group Research: group_577_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__70c6a03c5143

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all requested headers were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64var.h

## Role

`emul64var.h` is the private kernel header for the `emul64` emulated SCSI host bus adapter. It defines driver-local constants, packet/transport accessor macros, soft-state layout, target backing-store bookkeeping, hotplug state, reset notification state, and external support routines.

## Main Definitions

- Provides shorthand constants and request helpers such as `TRUE`, `FALSE`, `UNDEFINED`, `CNUM()`, `TGT()`, `LUN()`, `REQ_TGT_LUN()`, packet state/stat extraction, and SCSI packet flag translation through `EMUL64_SET_PKT_FLAGS()`.
- Defines driver timing and queue constants: retry delay, initial soft-state slots, reset waits, non-interrupt polling delay, timeout margin, `EMUL64_NDATASEGS`, `SHUTDOWN_THROTTLE`, and `CLEAR_THROTTLE`.
- Sets default SCSI options to parity, disconnect/reconnect, sync, tagged, fast, and wide operation.
- Defines hotplug soft-state bits: `EMUL64_SS_OPEN`, `EMUL64_SS_DRAINING`, `EMUL64_SS_QUIESCED`, and `EMUL64_SS_DRAIN_ERROR`.
- Defines `emul64_rng_overlap_t` for checking whether requested disk block ranges overlap no-write ranges.
- Defines sparse backing storage with `blklist_t`, storing only non-zero written blocks in an AVL tree, and `emul64_nowrite_t`, a linked list of disk ranges where writes are ignored.
- Defines `emul64_tgt_t`, the per-target state: SCSI address, target list link, no-write ranges, geometry, inquiry data, data block AVL tree and locks, and error injection fields.
- Defines `struct emul64_slot` for timeout deadlines and `struct emul64_reset_notify_entry` for registered reset callbacks.
- Defines the main `struct emul64` soft state: SCSI HBA transport and devinfo, interrupt cookie, revision fields, timeout id, SCSI option arrays, reset delay, initiator id, suspend flag, per-target capability/sync data, register pointer, request/response/hotplug locks, max LUN/sector arrays, reset notification list, backoff, hotplug state, condition variable, taskq, and target list.

## Locking And Contracts

The header centralizes mutex access with `EMUL64_REQ_MUTEX()`, `EMUL64_RESP_MUTEX()`, `EMUL64_HOTPLUG_MUTEX()`, `EMUL64_MUTEX_ENTER()`, and `EMUL64_MUTEX_EXIT()`. It also includes `_NOTE()` annotations documenting request and response mutex protection for queue, mailbox, slot, and response fields that are expected by implementation files.

## External Interfaces

The file declares BSD/backing-store setup routines (`emul64_bsd_init()`, `emul64_bsd_fini()`, `emul64_bsd_get_props()`), block-range helpers (`emul64_overlap()`, `emul64_bsd_blkcompare()`), and global tunables/statistics such as `emul64debug`, `emul64_nowrite_count`, `emul64_collect_stats`, and taskq limits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epm.h

## Role

`epm.h` is an internal kernel power-management header. It defines the device power-management state carried in `dev_info_t`, PM component metadata, PM dependency work, platform power request payloads, scan/threshold state, debug controls, locking macros, and the internal PM function surface used by kernel PM implementation files and private DDI code.

## Device And Component State

- Declares `e_pm_props()` and `e_new_pm_props()` for parsing PM-related device properties.
- Defines special power-level request values `PM_LEVEL_UPONLY`, `PM_LEVEL_DOWNONLY`, and `PM_LEVEL_EXACT`.
- Defines `devi_pm_flags` bits such as `PMC_NEEDS_SR`, `PMC_NO_SR`, `PMC_PARENTAL_SR`, `PMC_WANTS_NOTIFY`, `PMC_BC`, component parse state bits, threshold source bits, `PMC_NOPMKID`, `PMC_NO_INVOL`, `PMC_VOLPMD`, `PMC_SKIP_BRINGUP`, `PMC_CONSOLE_FB`, `PMC_DRIVER_REMOVED`, `PMC_CPU_DEVICE`, and `PMC_CPU_THRESH`.
- Defines scan bookkeeping with `pm_scan_t`, scan flags (`PM_SCANNING`, `PM_SCAN_AGAIN`, `PM_SCAN_STOP`, `PM_SCAN_DISPATCHED`), and default/CPU scan intervals.
- Defines `pm_comp_t` for parsed `pm-components` property data and `pm_component_t` for live component power/busy/timestamp/normal-current-level state.
- Defines `pm_info_t`, stored on devices that participate in PM, carrying PM state bits, direct-PM clone owner, inline power-level storage, optional level pointer, and direct-PM condition variable.

## Dependencies And Platform Requests

- Defines `pm_dep_wk_t` and dependency work types for power-on/off, attach/detach, dependency removal, bringup, keeper/kept processing, and CPR suspend/resume.
- Defines `pm_canblock_t` to distinguish blocking, failing, or bypassing when user/controller action might be needed.
- Defines `pm_cpupm_t` CPU PM modes: not set, polling, event-driven, and disabled.
- Defines the binary-compatibility-sensitive `pm_request_type` enum and `power_req_t` union used for parent/PPM power requests. Request variants cover set power, suspend/resume, pre/post notifications, PPM configuration, all-lowest notifications, lock/unlock/try-lock, power lock owner queries, ACPI S-state entry, and list search.
- Defines S3/S4 support constants, `s3a_t`, and test-point values for suspend-to-RAM paths.
- Defines bus power operation payloads for child power changes, nexus power-up, `power_has_changed`, and no-involuntary-power bookkeeping.

## PM Records, Macros, And Debugging

- Defines dependency records (`pm_pdr_t`), threshold records (`pm_thresh_rec_t`/`pm_pte_t`), PM direct/detaching state bits, and many access macros such as `PM_GET_PM_INFO()`, `PM_GET_PM_SCAN()`, `PM_CP()`, `PM_ISDIRECT()`, `PM_ISBC()`, `PM_ISCPU()`, and CPU PM mode predicates.
- Defines `PM_SCANABLE()` to express the combined autopm/CPU-PM scan policy.
- Provides PM device name formatting macros and extensive DEBUG-only `PMD_*` bit flags with `PMD()` logging through `pm_log()`.
- Provides POST/debug progress codes `PT_*` for suspend/resume paths.
- Defines power and devinfo locking wrappers: `PM_LOCK_DIP()`, `PM_UNLOCK_DIP()`, `PM_LOCK_BUSY()`, `PM_LOCK_POWER()`, `PM_TRY_LOCK_POWER()`, and related helpers.

## Internal Function Surface

The header declares the internal PM implementation API: detach/failure handling, `pm_power()`, `pm_unmanage()`, normal-power queries, threshold setting, power locking, bus ctlops, child init/uninit, all-to-normal, set-power, scan setup/stop/rescan, config/probe/attach/detach notifications, bus power dispatch, hold/release, driver removal, CPR no-invol reattach, direct-level save/restore, dependency-thread dispatch, PPM registration, and console-framebuffer helpers.

## Filesystem/OS Relevance

Although not filesystem-specific, this header affects VFS and device behavior through suspend/resume, direct PM, dependency bringup, devinfo state, and bus power operations for storage and display devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epoll.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epoll.h

## Role

`epoll.h` exposes the illumos epoll compatibility ABI. It defines the Linux-compatible `epoll_data_t` union, packed `struct epoll_event`, event constants, control operation constants, close-on-exec flag, and userland prototypes.

## ABI Details

- `epoll_data_t` can carry a pointer, file descriptor, 32-bit value, or 64-bit value.
- `epoll_event_t` contains a 32-bit event mask plus user data. Conditional `#pragma pack(4)` preserves 32-bit ABI layout on platforms where native long-long alignment differs.
- Event constants intentionally match Linux values and map to poll equivalents where applicable: `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLRDNORM`, `EPOLLRDBAND`, `EPOLLWRNORM`, `EPOLLWRBAND`, `EPOLLERR`, `EPOLLHUP`, `EPOLLRDHUP`, plus `EPOLLMSG`.
- High-bit flags are defined for `EPOLLEXCLUSIVE`, ignored `EPOLLWAKEUP`, `EPOLLONESHOT`, and edge-triggered `EPOLLET`.
- Defines `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, and Linux-compatible `EPOLL_CLOEXEC`.

## Userland Surface

Outside the kernel, it declares `epoll_create()`, `epoll_create1()`, `epoll_ctl()`, `epoll_wait()`, and `epoll_pwait()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epoll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errno.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errno.h

## Role

`errno.h` defines the illumos system error number ABI. It is a public kernel/user header assigning stable integer values to traditional UNIX, System V, robust-lock, STREAMS, shared-library, filesystem, and networking errors.

## Error Ranges

- Core UNIX errors run from `EPERM` 1 through standard filesystem/process errors such as `ENOENT`, `EINTR`, `EIO`, `EBADF`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `ENOSPC`, `EROFS`, and `EPIPE`.
- Adds math errors `EDOM`/`ERANGE`, System V IPC errors `ENOMSG`/`EIDRM`, channel/link/CSI errors, `EDEADLK`, `ENOLCK`, `ECANCELED`, and `ENOTSUP`.
- Defines filesystem quota error `EDQUOT`.
- Includes convergent and legacy errors such as `EBADE`, `EBADR`, `EXFULL`, `ENOANO`, `EBADRQC`, `EBADSLT`, and `EDEADLOCK`.
- Robust-lock errors include `EOWNERDEAD`, `ENOTRECOVERABLE`, and `ELOCKUNMAPPED`.
- STREAMS errors include `ENOSTR`, `ENODATA`, `ETIME`, and `ENOSR`.
- Shared-library and exec-related errors include `ELIBACC`, `ELIBBAD`, `ELIBSCN`, `ELIBMAX`, `ELIBEXEC`, `EILSEQ`, `ENOSYS`, `ELOOP`, `ERESTART`, `ESTRPIPE`, `ENOTEMPTY`, and `EUSERS`.
- BSD networking errors occupy the higher range, including socket type/address/protocol errors, network/connection errors, timeout/refusal/host errors, `EWOULDBLOCK` as `EAGAIN`, `EALREADY`, `EINPROGRESS`, and NFS `ESTALE`.

## Contract Notes

The numeric values are ABI. Consumers should treat aliases such as `EWOULDBLOCK` and historical duplicates such as `EDEADLK`/`EDEADLOCK` carefully, because applications and kernel compatibility code may depend on exact values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq.h

## Role

`errorq.h` defines the public kernel interface for the illumos error queue facility. Error queues collect fixed-size error records, optionally nvlist-backed, and drain them through callbacks, either asynchronously by soft interrupt or synchronously by the caller.

## Main Interfaces

- Forward-declares `errorq_t` and `errorq_elem_t`.
- Defines `errorq_func_t`, the callback type invoked to drain an element with private data, payload, and element metadata.
- Defines public create flag `ERRORQ_VITAL`, indicating the queue should be automatically drained on system reset.
- Defines dispatch modes `ERRORQ_ASYNC` and `ERRORQ_SYNC`.

## Kernel API

Under `_KERNEL`, the header declares:

- Creation/destruction: `errorq_create()`, `errorq_nvcreate()`, `errorq_destroy()`.
- Submission/drain: `errorq_dispatch()`, `errorq_drain()`, `errorq_init()`, `errorq_panic()`, `errorq_dump()`.
- Reservation path: `errorq_reserve()`, `errorq_commit()`, and `errorq_cancel()`.
- Nvlist element helpers: `errorq_elem_nvl()`, `errorq_elem_nva()`, and `errorq_elem_dup()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq_impl.h

## Role

`errorq_impl.h` is the private implementation header for `errorq`. It expands the opaque public types with queue element, nvlist element, kstat, and queue state layouts.

## Data Structures

- `errorq_nvelem_t` binds an nvlist element to its fixed buffer and `nv_alloc_t`.
- `struct errorq_elem` contains links for processing/free/pending lists, crash-dump list linkage, and the element payload pointer.
- `errorq_kstat_t` tracks dispatched, dropped, logged, reserved, reservation failures, committed, commit failures, and cancelled counts.
- Defines implementation flags `ERRORQ_ACTIVE` and `ERRORQ_NVLIST`, deliberately in the private bit range 16-31.
- Defines `ERRORQ_NAMELEN` as 31.
- `struct errorq` contains the queue name, kstats and installed kstat pointer, drain callback/private data, backing data buffer, queue length and element size, soft interrupt priority and id, flags, consumer lock, element array, processing head/tail, pending list, free bitmap, crash-dump list, global list linkage, and bitmap rotor.

## Contract Notes

This file must agree with `errorq.h` opaque type declarations. Its list and bitmap fields describe a fixed-size queue with both normal dispatch and crash-dump retention paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errorq_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/esunddi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/esunddi.h

## Role

`esunddi.h` declares private kernel DDI functions. It extends public `sunddi.h` with internal property manipulation, suspend/resume, memory locking, devinfo lookup/hold, branch dynamic reconfiguration, and driver-list compatibility routines.

## Property And Suspend/Resume Interfaces

- Declares property creation/modification/update functions for int, int64, arrays, strings, string arrays, and byte arrays.
- Declares property removal/undefine and property lookup functions (`e_ddi_getprop()`, `e_ddi_getprop_int64()`, `e_ddi_getproplen()`, `e_ddi_getlongprop()`, `e_ddi_getlongprop_buf()`).
- Declares `e_ddi_parental_suspend_resume()`, `e_ddi_resume()`, `e_ddi_suspend()`, and `pm_init()`.
- Exposes `pm_platform_power` as the platform power callback pointer.

## Device Reference And Memory Interfaces

- Defines `DEVI_REFERENCED` and `DEVI_NOT_REFERENCED` for `devi_stillreferenced()`.
- Declares `umem_lockmemory()`, a consolidation-private extended form of `ddi_umem_lock()` that can take callback ops and a process pointer.
- Defines `DDI_UMEMLOCK_LONGTERM`, used to reject long-term locks of shared regular-file mappings to avoid pvn deadlocks on truncation.
- Declares hold helpers by dev, path, and dip, including `E_DDI_HOLD_DEVI_NOATTACH`, plus a hold-count query.
- Declares major-instance path reconstruction and driver devinfo walking helpers.

## Branch And Callback Interfaces

- Defines branch flags such as `DEVI_BRANCH_CHILD`, `DEVI_BRANCH_CONFIGURE`, `DEVI_BRANCH_DESTROY`, `DEVI_BRANCH_EVENT`, `DEVI_BRANCH_PROM`, `DEVI_BRANCH_SID`, and `DEVI_BRANCH_ROOT`.
- Defines `devi_branch_t`, which carries an argument, callback, branch type, and PROM/SID creation function pointer.
- Declares branch create/configure/unconfigure/destroy/hold/release/reference operations.
- Keeps obsolete driver-list enter/tryenter/exit functions for compatibility.
- Defines `ddi_unbind_callback_t` and declares `e_ddi_register_unbind_callback()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/esunddi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ethernet.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ethernet.h

## Role

`ethernet.h` provides common Ethernet address, header, EtherType, frame-size, comparison/copy, and address conversion declarations used by kernel and userland.

## Packet And Address Structures

- Defines `ETHERADDRL`, `ETHERFCSL`, and `ETHERADDRSTRL`.
- Defines `ether_addr_t`, `struct ether_addr`, `struct ether_header`, `struct ether_vlan_header`, and `struct ether_vlan_extinfo`.
- Defines VLAN CFI and common EtherTypes: PUP, IP, ARP, REVARP, AppleTalk/AARP, VLAN, IPv6, slow protocols, PPPoE, EAPOL, RSN preauth, TRILL, FCoE, and max type.
- Defines trailer packet type range, MTU/min/max frame size constants.

## Helpers And APIs

- `ether_cmp()` and `ether_copy()` use short-sized loads/stores on SPARC/x86/x64 and fall back to `bcmp()`/`bcopy()` elsewhere.
- Kernel declarations include `ETHER_IS_MULTICAST()`, `localetheraddr()`, `ether_sprintf()`, and kernel `ether_aton()`.
- Userland declarations include `ether_ntoa()`, `ether_ntoa_r()`, `ether_aton()`, `ether_aton_r()`, `ether_ntohost()`, `ether_hostton()`, and `ether_line()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ethernet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/euc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/euc.h

## Role

`euc.h` defines EUC character-set width helpers and the `eucwidth_t` structure used by older multibyte locale and line-discipline code.

## Definitions

- Defines EUC shift bytes `SS2` and `SS3`.
- Defines byte classification macros `ISASCII()`, `NOTASCII()`, `ISSET2()`, `ISSET3()`, and `ISPRINT()`.
- Defines `eucwidth_t` with EUC byte widths for codesets 1-3, screen widths for codesets 1-3, process-code width, and a `_multibyte` flag.

## Contract Notes

The header is guarded so `NOTASCII` and `_EUCWIDTH_T` are not redefined if already supplied. `ISPRINT()` depends on an `eucwidth_t` value and `isprint()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/euc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eucioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eucioctl.h

## Role

`eucioctl.h` defines ioctl commands and small payloads for passing EUC width and mode state to line-discipline STREAMS modules.

## Ioctl Contract

- Defines `EUC_IOC` and ioctl commands `EUC_WSET`, `EUC_WGET`, `EUC_MSAVE`, `EUC_MREST`, `EUC_IXLOFF`, `EUC_IXLON`, `EUC_OXLOFF`, and `EUC_OXLON`.
- Defines compact `struct eucioc`/`eucioc_t` containing four EUC byte widths and four screen widths as unsigned chars. The comments explain this intentionally differs from `eucwidth_t` to keep downstream messages small.
- Defines `EUC_BCAST` for line-discipline broadcast messages and one-byte broadcast states `EUC_B_CANON` and nonzero `EUC_B_RAW`.

## STREAMS Notes

The broadcast protocol is an `M_CTL` message with an `iocblk` containing `EUC_BCAST`, followed by an `M_DATA` block carrying raw/canonical state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eucioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eventfd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eventfd.h

## Role

`eventfd.h` defines illumos support for Linux-compatible `eventfd`. It fixes flag values to Linux ABI values and declares the userland helpers.

## Definitions

- Defines `eventfd_t` as `uint64_t`.
- Defines Linux-compatible flags `EFD_CLOEXEC`, `EFD_NONBLOCK`, and `EFD_SEMAPHORE`.
- Defines native-private ioctl base `EVENTFDIOC` and `EVENTFDIOC_SEMAPHORE`, used to toggle semaphore mode internally.
- Userland declarations are `eventfd()`, `eventfd_read()`, and `eventfd_write()`.
- Kernel-only definitions include minor node constants `EVENTFDMNRN_EVENTFD`, `EVENTFDMNRN_CLONE`, and max counter value `EVENTFD_VALMAX` as `ULLONG_MAX - 1`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eventfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct.h

## Role

`exacct.h` is the main extended accounting API header. It defines exacct versioning, syscall options, libexacct error codes, object model types, object manipulation functions, and kernel accounting assembly/commit hooks.

## Public ABI

- Defines `EXACCT_VERSION` 1.
- Defines unpack allocation modes `EUP_ALLOC` and `EUP_NOALLOC`, coordinated with `ea_free_object()`.
- Defines record type options `EW_PARTIAL`, `EW_INTERVAL`, and kernel-only `EW_FINAL`.
- Defines `EP_RAW` and `EP_EXACCT_OBJECT` to distinguish raw buffers from packed exacct objects.
- Limits accounting buffers with `EXACCT_MAX_BUFSIZE` at 64 KiB.
- Userland syscall prototypes are `getacct()`, `putacct()`, and `wracct()`.
- Defines libexacct result codes from `EXR_OK` through `EXR_INVALID_OBJ`.

## Object Model

- `ea_size_t` is 64-bit; `ea_catalog_t` is 32-bit.
- `ea_object_type_t` distinguishes errors, empty objects, groups, and items.
- `ea_item_t` stores scalar, string, embedded object, or raw payload plus payload size.
- `ea_group_t` stores object count and pointer to child object list.
- `ea_object_t` combines type, group/item union, sibling link, and catalog tag.
- Accessor macros expose item union fields (`ei_uint64`, `ei_string`, etc.) and object union fields (`eo_group`, `eo_item`).

## Functions

The public object API includes `ea_set_item()`, `ea_set_group()`, attachment functions, `ea_free_item()`, `ea_free_object()`, `ea_pack_object()`, and allocation/string helpers.

Under `_KERNEL`, the header declares allocation helpers, process/task/flow/net accounting commit and assembly routines, header creation/write functions, task mstate movement, the `exacct_queue` taskq, and `exacct_object_cache`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_catalog.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_catalog.h

## Role

`exacct_catalog.h` defines the default SunOS extended-accounting catalog tag layout and default data IDs. Each exacct object begins with a 32-bit catalog tag partitioned into type, catalog, and id fields.

## Tag Layout

- Type occupies bits 31-28 and is masked by `EXT_TYPE_MASK`.
- Types include `EXT_NONE`, unsigned integers of 8/16/32/64 bits, `EXT_DOUBLE`, `EXT_STRING`, `EXT_EXACCT_OBJECT`, `EXT_RAW`, and `EXT_GROUP`.
- Catalog occupies bits 27-24 and is masked by `EXC_CATALOG_MASK`.
- `EXC_NONE`/`EXC_DEFAULT` identify default catalog entries, while `EXC_LOCAL` reserves ids for application-defined local use.
- Data id occupies the low 24 bits and is masked by `EXD_DATA_MASK`.

## Default Data IDs

- Global header ids cover version, file type, creator, hostname, and group header.
- Group ids cover process, task, LWP, tags, partial records, task intervals, flow, RFMA/FMA, and network link/flow descriptors and stats.
- Process ids cover pid, uid/gid, task/project, host/command, start/finish times, CPU times, tty, faults, messages, blocks, chars, context switches, signals, swaps, syscalls, flags, tag, ancestor pid, wait status, zone name, and RSS average/max.
- Task ids cover task/project, host, timing, CPU, resource counters, tag, ancestor task, and zone name.
- Flow ids cover IPv4/IPv6 source/destination, ports, protocol, DS field, byte/packet counts, create/last-seen time, project, uid, and action name.
- FMA ids cover label/version, OS/platform, time, nvlist, device major/minor, inode, offset, and UUID.
- Network descriptor/stat ids cover link/flow identity, Ethernet endpoints, VLAN, SAP, priority, bandwidth, IP/ports/protocol/DS field, current time, bytes, packets, and error packets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_catalog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_impl.h

## Role

`exacct_impl.h` contains private extended-accounting implementation structures used by libexacct and the kernel to assemble process, task, flow, and network accounting records.

## Error And Usage Structures

- `EXACCT_SET_ERR()` is a no-op in kernel builds and calls `exacct_seterr()` in userland builds.
- `task_usage_t` records task CPU time, fault/message/block/char/context/signal/swap/syscall counts, start/finish times, and ancestor task id.
- `proc_usage_t` records process resource counters, CPU/start/finish times, RSS average/max, pid/user/group/project/task ids, accounting flags, command, controlling tty major/minor, wait status, ancestor pid, zone name, and node name.
- `flow_usage_t` records IPv4/IPv6 addresses, protocol, ports, DS field, byte/packet counts, creation/last-seen times, project, user, address-family flag, and action name.

## Network Records

- Defines network record types `EX_NET_LNDESC_REC`, `EX_NET_FLDESC_REC`, `EX_NET_LNSTAT_REC`, and `EX_NET_FLSTAT_REC`.
- `net_stat_t` holds name, input/output bytes, input/output packets, error counts, and reference flag.
- `net_desc_t` holds names, Ethernet addresses, VLAN/SAP/priority, bandwidth, IP addresses, IPv4 flag, ports, protocol, DS field, and descriptor type.

## Byte Ordering

Declares `exacct_order16()`, `exacct_order32()`, and `exacct_order64()` for exacct record byte-order conversion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exec.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exec.h

## Role

`exec.h` defines kernel exec subsystem interfaces and shared exec data structures. It covers executable magic probing, exec argument state, interpreter recursion, aux-vector construction, exec module registration, ELF/brand helpers, and core dump helper prototypes.

## Public And Kernel Structures

- Defines `MAGIC_BYTES` and `getexmag()` for executable magic inspection.
- Defines `execa_t` for filename/argv/envp syscall arguments.
- Defines `execenv_t` for bss/brk bases, brk size, executable vnode, and magic.
- Kernel-only `uarg_t` carries exec argument counts/sizes, pathnames, aux vector size, stack layout/alignment/protection, model conversion info, pointer sizes, `execsw` entry, entry point, thread pointer, executable vnode, emulator/brand data, auxv stack addresses, credential state, environment scrubbing flag, and commpage address.
- Defines brand actions `EBA_NONE`, `EBA_NATIVE`, and `EBA_BRAND`.
- Defines stack helper macros `execpoststack()` and `stackaddress()`.
- `ADDAUX()` writes aux vector entries and clears padding where ABI alignment creates possible padding.
- Defines interpreter path size and recursion depth with `INTPSZ` and `INTP_MAXDEPTH`, and `intpdata_t` for nested interpreter names/args.
- Defines set-id classification bits `EXECSETID_SETID`, `EXECSETID_UGIDS`, and `EXECSETID_PRIVS`.

## Exec Switch

`struct execsw` stores magic string, magic offset/length, exec callback, core callback, and module lock pointer. The header declares `nexectype`, `execsw[]`, `execsw_lock`, standard magic values/strings, exec argument parsing, common exec entry points, exec switch allocation/lookup, permission checks, segment mapping, exec environment setup, executable open/close, register setup, and stack pointer sizing.

## ELF, Brands, And Core Dumps

Declares ELF exec and map/read helpers for native and LP64/ELF32 cases, including brand-aware `mapexec_brand()` and `mapexec32_brand()`. Also declares `core_seg()` and `core_write()` for exec module core dump routines.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exechdr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exechdr.h

## Role

`exechdr.h` defines the historical Sun/UNIX `struct exec` a.out-style executable header and related magic and machine-type constants known by kernel and user programs.

## Definitions

- `struct exec` stores dynamic flag, tool version, machine type, magic, text/data/bss/symbol sizes, entry point, and relocation sizes.
- Defines magic values `OMAGIC`, `NMAGIC`, and `ZMAGIC`.
- Defines legacy machine types for old Sun-2, 68010, 68020, and SPARC executables.
- Defines tool-version constants `TV_SUN2_SUN3` and `TV_SUN4`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exechdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/execx.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/execx.h

## Role

`execx.h` defines the public extension for `execvex()`, an exec variant that can take flags.

## Definitions

- Defines `EXEC_DESCRIPTOR`, meaning the first `execvex()` argument is interpreted as an already-open file descriptor in the calling process rather than a pathname.
- Outside the kernel, declares `execvex(uintptr_t, char *const *, char *const *, int)`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/execx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/extdirent.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/extdirent.h

## Role

`extdirent.h` defines a kernel-only extended directory entry format used when `VOP_READDIR()` requests per-entry flags through `V_RDDIR_ENTFLAGS` and the filesystem supports them.

## Definitions

- `edirent_t` contains inode number, disk directory offset, per-entry flags, record length, and variable-length name.
- `EDIRENT_RECLEN()` computes 8-byte-aligned record length for a name length.
- `EDIRENT_NAMELEN()` derives name storage length from record length.
- Defines `ED_CASE_CONFLICT`, indicating that disregarding case, the entry is not unique.
- `ED_CASE_CONFLICTS()` tests the case-conflict flag.

## Filesystem Relevance

This is a VFS/filesystem ABI extension for case-insensitive or case-preserving filesystems that need to report directory-entry metadata beyond standard `dirent64`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/extdirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap.h

## Role

`fasttrap.h` defines the user/kernel ioctl-facing ABI for DTrace fasttrap probes, including probe creation specs, instruction queries, and PT_SUNWDTRACE size linkage.

## Definitions

- Includes ISA-specific fasttrap definitions, DTrace definitions, and base types.
- Defines ioctl base `FASTTRAPIOC` and commands `FASTTRAPIOC_MAKEPROBE` and `FASTTRAPIOC_GETINSTR`.
- Defines `fasttrap_probe_type_t` with entry, return, offsets, post-offsets, and is-enabled probe types.
- `fasttrap_probe_spec_t` carries pid, probe type, function and module names, PC, function/probe size, offset count, and variable offset list.
- `fasttrap_instr_query_t` carries PC, pid, and returned instruction.
- Defines `PT_SUNWDTRACE_SIZE` from `FASTTRAP_SUNWDTRACE_SIZE`, tying kernel exec handling to the runtime linker/libc early-process tracing data object.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap_impl.h

## Role

`fasttrap_impl.h` is the private kernel implementation header for the DTrace fasttrap provider. It defines provider/process/probe/tracepoint state and ISA hooks used to instrument user processes.

## Model

The file documents the fasttrap object model:

- A process can have multiple providers, including pid and USDT providers.
- Providers for one process share a `fasttrap_proc_t`, whose active-provider count determines whether it is active or defunct.
- Probes contain tuples of fasttrap ids and tracepoints.
- Tracepoints represent actual instrumented PCs and hold pre/post probe id lists.
- Tracepoints can be shared and ownership can move between probes when probes are disabled.

## Structures

- `fasttrap_proc_t` stores pid, active and extant provider counts, lock, and hash-chain link.
- `fasttrap_provider_t` stores pid, provider name, DTrace provider id, removal/retirement marks, locks, enabled probe/create/meta counts, shared process pointer, and hash-chain link.
- `fasttrap_id_t` links enabled probe ids to tracepoints and records probe type.
- `fasttrap_id_tp_t` combines an id and tracepoint pointer.
- `fasttrap_probe_t` stores DTrace id, pid, provider, function address/size, generation, tracepoint count, argument type/translation data, enabled flag, and flexible tracepoint tuple array.
- `fasttrap_tracepoint_t` stores associated process, PC, pid, ISA-specific tracepoint state, pre/post id lists, and hash link.
- `fasttrap_bucket_t` pads each hash bucket to 64 bytes around the lock and data pointer.
- `fasttrap_hash_t` stores power-of-two bucket count, mask, and table.

## Hooks

The header maps internal copy/userword operations to kernel primitives, declares `fasttrap_sigtrap()`, global `fasttrap_probe_id` and `fasttrap_tpoints`, hash index macro, ISA-required tracepoint init/install/remove, pid/return probe entry points, and pid/USDT argument fetchers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fasttrap_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fault.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fault.h

## Role

`fault.h` defines process fault numbers used by `/proc` tracing. Faults are analogous to signals but correspond to hardware or low-level execution faults that debuggers can request to stop on.

## Definitions

Fault enumeration starts at 1 and includes illegal instruction, privileged instruction, breakpoint, trace trap, memory access/alignment, bounds, integer overflow, integer divide by zero, floating-point exception, stack fault, recoverable page fault, watchpoint trap, and CPU performance counter overflow.

`fltset_t` is a four-word bitset used to represent traced fault sets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fault.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbio.h

## Role

`fbio.h` defines the historical Sun framebuffer ioctl ABI. It covers framebuffer type discovery, pixrect access, colormap operations, attributes, video control, double buffering, hardware cursors, window IDs, monitor/device information, and framebuffer type codes.

## Core Ioctls And Structures

- `struct fbtype` is returned by `FBIOGTYPE` and reports type, height, width, depth, colormap size, and total size.
- Kernel-only `struct fbpixrect` and `FBIOGPIXRECT` expose pixrect state.
- `struct fbinfo` and `FBIOGINFO` provide physical/kernel-mapped framebuffer information for older devices.
- `struct fbcmap` plus 32-bit `fbcmap32` support `FBIOPUTCMAP` and `FBIOGETCMAP`.
- Attribute structures `fbsattr` and `fbgattr` support `FBIOSATTR` and `FBIOGATTR`, including emulation type, device-specific fields, owner, and possible emulations.
- `FBIOSVIDEO`/`FBIOGVIDEO` control video on/off. Other early ioctls include vertical retrace and window-grabber operations.

## Cursor, Window ID, And Device Info

- Defines double-buffering flags, planes (`FBDBL_A`, `FBDBL_B`, `FBDBL_BOTH`, `FBDBL_NONE`), and `struct fbdblinfo`.
- Defines hardware cursor structures `fbcurpos`, `fbcursor`, and 32-bit `fbcursor32`, plus cursor set bits and cursor ioctls.
- Defines window-id allocation/list/double-buffer structures, including 32-bit list variant, and WID ioctls.
- Defines miscellaneous graphics/device structures: `gfxfb_info`, `cg6_info`, `s3_info`, `p9000_info`, `p9100_info`, `wd90c24a2_info`, and `mon_info`.
- Defines indexed colormap structure `fbcmap_i`, 32-bit `fbcmap_i32`, flags `FB_CMAP_BLOCK` and `FB_CMAP_KERNEL`, and indexed colormap ioctls.

## Framebuffer Type ABI

Defines framebuffer type codes from `FBTYPE_NOTYPE` and early Sun mono/color devices through accelerator/video/plasma/cg14 types, ending with `FBTYPE_LASTPLUSONE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbuf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbuf.h

## Role

`fbuf.h` defines the kernel `fbuf` interface for mapping a region of a vnode-backed file through segkmap/segmap-style facilities.

## API

- `struct fbuf` contains mapped address and byte count.
- `fbread()` maps file data for read/write-style access.
- `fbzero()` maps/zeros file data.
- `fbwrite()` synchronously writes a mapped buffer using file mapping information.
- `fbdwrite()` performs delayed write handling.
- `fbiwrite()` synchronously writes indirectly to a specified block number without using file mapping information.
- `fbrelse()` releases a mapped `fbuf` with a `seg_rw` release code.

## Filesystem Relevance

Filesystem code can use this interface to access directory blocks or metadata through kernel mappings while retaining explicit control over release/writeback behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc.h

## Role

`fc.h` defines Fibre Channel Physical and Signaling Interface constants and payload structures for common FC frame handling. It is a protocol-level header used by FC drivers and FC-4 consumers.

## Frame Header And Control Bits

- Defines `FC_PH_VERSION` and `MAX_FRAME_SIZE`.
- Defines `fc_frame_header_t` with FC-2 frame fields: routing/control, destination/source ids, type, frame control, sequence ids/count, exchange ids, and relative offset/parameter.
- Provides header predicate macros for originator context, unsolicited frame, first/last sequence, last frame, and sequence initiative.
- Defines `r_ctl` routing and info masks plus device-data, extended service, FC-4 service, video, basic service, and link-control routing values.
- Defines device data categories, BLS codes, ELS request/response codes, ELS command opcodes, link-control codes, type values, and `F_CTL_*` bits.

## Addresses And Error Codes

Defines well-known FC addresses for multicast, management/time/name/fabric services, fabric F-port, and broadcast. It also defines busy/reject reason codes for fabric/N-port busy, frame reject, BA_RJT, and LS_RJT.

## Payload Structures

Defines reject parameters, transfer-ready payload, link-error-status reply, login payload, generic ELS payload, and `fc_dataseg_t` data segments with 32-bit base/count.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc_transport.h

## Role

`fc_transport.h` defines a generic Fibre Channel adapter transport interface for child FC protocol drivers. It wraps FC packets, completion callbacks, transport status codes, unsolicited command handling, state change registration, and function vectors exposed by FC adapters.

## Packet And Status Model

- Defines `fc_devdata_t`, `fc_ioclass_t`, `fc_iotype_t`, `fc_sleep_t`, and `fc_statec_t`.
- `fc_packet_t` carries adapter cookie, completion/private data, flags, timeout, I/O class/device data, command/response/data segments, completion status/statistics, command/response frame headers, and packet-chain links.
- Packet flags include `FCFLAG_NOINTR` and `FCFLAG_COMPLETE`.
- Transport return values include success, failure, timeout, queue full, and unavailable.
- `fc_pkt_status` values include OK, P_RJT/F_RJT, P_BSY/F_BSY, offline, timeout, overrun, queue/exchange/resource errors, and pseudo-status values for login timeout, CQ full, transport failure, and reset failure.

## Transport Vectors

`fc_transport_t` exposes adapter cookie, DMA limits/attributes, interrupt cookie, lock/cv, and operations:

- Submit/reset packets.
- Allocate/free packets.
- Register/unregister state change callbacks.
- Poll the interface for error recovery when interrupts are disabled.
- Register/unregister unsolicited command callbacks.
- Fetch unsolicited command payload into a caller-provided packet.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal.h

## Role

`fcal.h` is a Fibre Channel Arbitrated Loop variant of the FC-PH definitions. It largely mirrors `fc.h` with fixed-width integer types for FC-AL/SOCAL use.

## Definitions

- Defines FC version and max payload size.
- Defines `fc_frame_header_t` with FC-2 bitfields and fixed-width exchange/offset fields.
- Provides same frame predicates for originator, unsolicited, first/last sequence, last frame, and initiative.
- Defines `r_ctl`, device-data, BLS/ELS/link-control, type, and `F_CTL_*` constants.
- Defines well-known addresses and busy/reject reason codes.
- Defines `aFC2_RJT_PARAM`, transfer-ready payload `aXFER_RDY`, generic ELS payload, and `fc_dataseg_t`.

## Relationship To `fc.h`

The file duplicates much of `fc.h` for FC-AL-era drivers. Differences are mostly type-width choices and a narrower payload set.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_linkapp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_linkapp.h

## Role

`fcal_linkapp.h` defines FC-AL link application opcodes, events, well-known addresses, service parameter formats, World Wide Name formats, and ELS payload structures.

## Link Application ABI

- Defines `MAX_FCODE_SIZE`, well-known fabric addresses, and many ELS opcodes such as reject, accept, PLOGI/FLOGI/LOGO, RLS, ECHO, RRQ, PRLI/PRLO, SCN, TPLS, GPRLO, GAID/FACT/FDACT, QoSR, PDISC/FDISC/ADISC, plus SMCC-specific display/identify values.
- Defines sysevent strings for FCAL device insertion and removal.
- Defines BA_ACC and BA_RJT payloads and reason/explanation codes.
- Defines common service parameters, 16-byte service parameter blocks, `la_wwn_t`, WWN size, and NAA id values.
- Defines ELS login payload/reply, RLS request/reply, LOGO request/reply, RRQ request/reply, PRLI/PRLO request/reply, PDISC request/reply, ADISC request/reply, identify request/reply, and link application reject payload.

## Notes

The header contains a historical malformed macro line `#define LA_RJT_ INVALID_SEQ_ID 0x21`; consumers likely avoid it or rely on compiler parsing behavior. It should be treated as part of the source as-is, not silently normalized.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_linkapp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_transport.h

## Role

`fcal_transport.h` defines FC-AL transport packet and operation vectors used by FC-AL upper-layer protocol drivers and SOCAL-style adapters.

## Packet And Transport Structures

- Defines `fc_devdata_t`, `fc_ioclass_t`, `fcal_sleep_t`, `fc_iotype_t`, and `fc_uc_cookie_t`.
- `fcal_packet_t` stores adapter cookie, next pointer, completion/private data, flags, command state, transport/diagnostic status, SOC request union, response header, magic, and command count.
- Packet flags include no-interrupt, complete, response-header-valid, aborting, and aborted.
- Command state bits include in-transport, complete, and completion-called.
- `fcal_transport_t` carries adapter handle, DMA limits/attributes, access attributes, login parameters, node/port WWNs, port number, command maximum, lock/cv, and operation table.

## Operations And Status

`fcal_transport_ops_t` includes submit, poll submit, LILP map, force LIP, abort command, ELS request, bypass device, force reset, add/remove upper-layer protocol, and take-core hooks.

Return/status constants cover success, timeout, allocation failure, old port, link error, offline, aborted, abort failure, bad abort/params, overrun, no transport, transport failure/unavailable/queue-full/timeout, login pseudo-statuses, and generic `FCAL_FAILURE`.

Defines FC-AL state reset value, LILP map magic/bad-magic, LIP request constants, and `fcal_lilp_map_t` with AL_PA list.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcio.h

## Role

`fcio.h` defines FC/FC-AL ioctl payloads, maps, link-status structures, firmware/microcode version buffers, and kstat/statistics structures for SOCAL and IFP-style Fibre Channel adapters.

## Ioctls And Maps

- Defines `FIOC`, `SF_IOC`, `SFIOCGMAP`, `SF_NUM_ENTRIES_IN_MAP`, and FC ioctls for limited map, force LIP, link status, and FCode/microcode/prom versions.
- Provides IFP compatibility aliases for map, force LIP, and link status commands.
- `sf_al_addr_pair_t` stores AL_PA, hard address, inquiry dtype, node WWN, and port WWN.
- `sf_al_map_t` stores device count, 127 address pairs, and HBA address.
- Defines `rls_payload`, `lilpmap`, and `socal_fm_version`.

## Statistics And Status Codes

- Defines target stats for ELS failures, timeouts, ABTS failures, task management failures, RO/length mismatches, and received LOGOs.
- Defines `sf_stats_t`, `fc_pstats`, `socal_stats_t`, IFP target stats, and `ifp_stats_t`.
- Defines FCAL response status codes for OK, rejects/busies, online/offline/timeout/overrun, loop state, old/al port, queue/exchange errors, abort/diagnostic/DMA/CRC/open failures, generic error, online timeout, and max status.
- Defines QLA21xx/IFP command completion status codes such as complete, incomplete, DMA error, transport error, reset, aborted, timeout, overrun/underrun, abort/reset rejected, queue full, port unavailable/logged out, and port config changed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcp.h

## Role

`fcp.h` defines Fibre Channel Protocol frame payloads for carrying SCSI commands, data, transfer-ready, and responses over FC.

## Command And Response Payloads

- Defines frame categories `FCP_SCSI_DATA`, `FCP_SCSI_CMD`, `FCP_SCSI_RSP`, and `FCP_SCSI_XFER_RDY`.
- `fcp_cntl_t` encodes tagged-queueing type, task management flags, and read/write data direction bits.
- Defines FCP queue types: simple, head-of-queue, ordered, ACA, and untagged.
- `fcp_ent_addr_t` provides four 16-bit entity-address layers.
- Defines `FCP_CDB_SIZE` 16 and `FCP_LUN_SIZE` 8.
- `fcp_cmd_t` combines entity address, control, 16-byte SCSI CDB, and data length.
- `fcp_status_t` encodes residual under/over, sense-length present, response-length present, and SCSI status.
- `fcp_rsp_t` includes status, residual, sense length, and response length, followed by variable response and sense data.
- Defines `FCP_MAX_RSP_IU_SIZE`.

## PRLI And Transfer Ready

- `struct fcp_rsp_info` and response codes describe no failure, data length mismatch, invalid command, data RO mismatch, unsupported task management, and task management failure.
- `fcp_xfer_rdy_t` carries sequence offset and burst length.
- `fcp_prli` and `fcp_prli_acc` define process login/accept service parameter bitfields including initiator/target functions, image pair, overlay, mixed command/data, and xfer-rdy-disable flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/linkapp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/linkapp.h

## Role

`linkapp.h` is an older Fibre Channel link application payload header. It defines a smaller set of well-known addresses, link application opcodes, basic accept/reject payloads, service parameters, WWN representation, login/RLS/LOGO/reject payloads, and reject reason/explanation codes.

## Definitions

- Defines well-known fabric addresses for multicast, management, time, name, fabric controller/F-port, and broadcast.
- Defines opcodes `LA_RJT`, `LA_ACC`, `LA_LOGI`, `LA_LOGO`, `LA_RLS`, and `LA_IDENT`.
- Defines `ba_acc_t` and `ba_rjt_t`, with BA_RJT reason/explanation constants.
- Defines common service parameters, service parameter block, `la_wwn_t`, and NAA id constants.
- Defines `la_logi_t`, `la_rls_t`, `la_rls_reply_t`, `la_logo_t`, `la_logo_reply_t`, and `la_rjt_t`.
- Defines LA_RJT reason and explanation constants, including options, initiator/recipient, data field size, concurrent, credit, invalid port/node WWN, invalid common service, and insufficient resources.

## Relationship To `fcal_linkapp.h`

This is a smaller predecessor/variant of the FC-AL link application header. Newer FC-AL payloads and ELS opcodes are in `fcal_linkapp.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/linkapp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcntl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcntl.h

## Role

`fcntl.h` defines illumos file open flags, `fcntl()` command numbers, file-lock structures, lock/share constants, openat-style flags, and file-advice constants. It is a core filesystem and file-descriptor ABI header.

## Open Flags And Fcntl Commands

- Access modes include `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_SEARCH`, and `O_EXEC`.
- Defines common open flags such as `O_NDELAY`, `O_APPEND`, `O_SYNC`, `O_DSYNC`, `O_RSYNC`, `O_NONBLOCK`, `O_LARGEFILE`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_XATTR`, `O_NOFOLLOW`, `O_NOLINKS`, `O_CLOEXEC`, `O_DIRECTORY`, `O_DIRECT`, and `O_CLOFORK`, gated by feature-test macros where required.
- Defines descriptor/file commands: duplicate/get/set FD flags, get/set file flags, get extended flags, stream/private/quota/blocksize commands, socket owner commands, revoke, remote-lock query, share/unshare, poison FD, and close-on-exec/close-on-fork duplicate variants including `F_DUP3FD`.
- Kernel/KMEMUSER exposes old SVR3 `F_O_GETLK` and sysid/node-id extraction macros for clustering/remote locks.

## Locking ABI

- Defines command numbers for native and ILP32 large-file lock/space commands. Values differ based on `_LP64`, `_FILE_OFFSET_BITS`, and `_LARGEFILE64_SOURCE`.
- Supports classic POSIX locks, NBMAND private variants, open-file-description locks, and private flock-owned locks.
- Defines `flock_t`, 32-bit `flock32_t`, large-file `flock64_t`, 32-bit packed `flock64_32_t`, LP64 kernel view `flock64_64_t`, and old SVR3 `o_flock_t`.
- Lock types are `F_RDLCK`, `F_WRLCK`, `F_UNLCK`, and `F_UNLKSYS`.

## Share, At, And Advice Constants

- Defines `O_ACCMODE`, `FD_CLOEXEC`, and `FD_CLOFORK`.
- Defines direct I/O toggles `DIRECTIO_OFF` and `DIRECTIO_ON`.
- Defines `fshare_t` and share access/deny masks including private delete/metadata/mandatory enforcement flags.
- Defines `AT_FDCWD`, symlink follow/no-follow flags, `AT_REMOVEDIR`, `_AT_TRIGGER`, and `AT_EACCESS`.
- Defines `POSIX_FADV_*` constants for `posix_fadvise()`.

## Filesystem Relevance

This header is central to VFS/open/lock/share behavior. The conditional command numbering and structure packing are especially important for 32-bit, large-file, and kernel compatibility paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoe_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoe_common.h

## Role

`fcoe_common.h` defines the in-kernel common interface between the Fibre Channel over Ethernet core and its initiator/target clients. It covers FCoE status, FC frame layout as byte arrays, frame and port objects, client registration, byte-order helpers, FC header accessors, and FCP command/response payloads.

## FCoE Core Types

- Defines FCoE return values, 1G/10G port speeds, FC frame header size, FLOGI payload sizes, minimum MTU, and maximum FC frame size.
- Defines `fcoe_fc_frame_header_t` as byte arrays for all FC frame header fields to avoid endian-sensitive bitfield layout.
- `fcoe_frame_t` stores flags, network buffer, FC header and optional headers, FC frame and payload pointers, size/allocation fields, owning port, private client/core pointers, and timestamp.
- `fcoe_port_t` stores flags, private pointers, port/node WWNs, maximum FC frame size, MTU, link speed, Ethernet destination, and function vectors for transmit, frame allocation/release, netb allocation/free, client deregistration, control, and MAC address change.
- Port flags distinguish direct P2P, target mode, initiator mode, and MAC-in-use state.
- Notifications cover link up/down and address change. Port control commands cover online/offline.
- Defines FCoE version enum, current version `FCOE_VER_NOW`, and `fcoe_client_t` registration structure with client callbacks.

## Byte Order And Header Access

The header provides `FCOE_V2B_*` and `FCOE_B2V_*` macros for 1/2/3/4/8-byte big-endian value conversion, plus `FRM_*` getters and `FFM_*` setters for FC header fields. `FRM_IS_LAST_FRAME()` and `FRM_SENDER_IS_XCH_RESPONDER()` test F_CTL bits.

## FCP And Utility Definitions

- Declares `fcoe_register_client()`.
- Defines `EPORT_CLT_TYPE()`, default FCoE OUI/fabric-port MAC helpers, default/min FCP payload sizes, and `fcoe_fcp_cmnd_t`, `fcoe_fcp_rsp_t`, and `fcoe_fcp_xfer_rdy_t`.
- Defines `CURRENT_CLOCK`, seconds-to-ticks conversion, mod-hash key conversion helpers for exchange ids, taskq function pointer type, and `fcoe_trace()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoe_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoeio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoeio.h

## Role

`fcoeio.h` defines the user/kernel ioctl ABI for managing FCoE ports.

## Ioctl Envelope

- Defines top-level ioctl command `FCOEIO_CMD` and sub-command base `FCOEIO_SUB_CMD`.
- Subcommands create a port, delete a port, and get the FCoE port list.
- Defines transfer direction flags `FCOEIO_XFER_NONE`, `FCOEIO_XFER_READ`, `FCOEIO_XFER_WRITE`, and `FCOEIO_XFER_RW`.
- Defines `fcoeio_stat_t` error/status values for invalid argument, busy, already exists, PWWN/NWWN conflicts, MAC create/open failures, port creation failure, jumbo-frame requirement, MAC not found, offline failure, and more-data.
- `fcoeio_t` is the ioctl envelope with transfer direction, command, flags, command flags, input/output/aux lengths, status, and 64-bit user buffer addresses.

## Port Payloads

- Defines client port types `FCOE_CLIENT_INITIATOR` and `FCOE_CLIENT_TARGET`.
- `fcoeio_create_port_param_t` carries port/node WWNs, provided flags, force-promiscuous flag, port type, and datalink id.
- `fcoeio_delete_port_param_t` carries datalink id.
- `fcoe_port_instance_t` reports port WWN, datalink id, factory/current MACs, promiscuous state, port type, and MTU.
- `fcoe_port_list_t` is a variable-length list headed by `numPorts`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoeio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct.h

## Role

`fct.h` defines the common Fibre Channel Target framework interface between STMF/FCT and Fibre Channel adapter drivers. It covers target port, remote port, command, ELS/CT/ABTS, data buffer store, link info, port attributes/statistics, control commands, and FCT service functions.

## Core Objects

- Defines `fct_struct_id_t` values for allocating local ports, remote ports, received/solicited ELS, solicited CT, received ABTS, FCP exchanges, and data-buffer stores.
- `fct_remote_port_t` stores FCT/FCA private data, local port pointer, node/port WWN strings and bytes, remote id, hard address, and handle.
- `fct_cmd_t` stores FCT/FCA/private command data, local/remote port, link pointer, command type, remote-port handle, command handle, local/remote port ids, exchange ids, and completion status. Helper macros extract slot index and validity from command handles.
- Defines command type bits for FCP exchange, received ELS, solicited ELS, received ABTS, solicited CT, and all types.
- `fct_els_t`, `fct_sol_ct_t`, and `fct_rcvd_abts_t` define payload buffers and ABTS response state.

## Ports, Buffers, And Link State

- Defines FC-HBA string lengths, FCT info/taskq lengths, and `FC_TGT_PORT_RLS`.
- `fct_port_attrs_t` contains manufacturer, serial, model, model description, hardware/driver/option ROM/firmware versions, driver name, vendor-specific id, supported class/speed, and max frame size.
- `fct_port_link_status_t` and `fct_port_stat_t` track link failure/sync/signal/protocol/invalid word/CRC counters.
- `fct_dbuf_store_t` wraps STMF data buffer storage callbacks for allocation, free, setup, teardown, max SGL transfer, and copy threshold.
- `fct_local_port_t` stores private data, STMF local port, WWNs and symbolic names, provider, address/login/exchange limits, FCA private sizes, abort timeout, data buffer store, and FCA operation callbacks for link info, remote port registration, command send/data/response/abort, control, FLOGI exchange, HBA details, and port info.
- `fct_flogi_xchg_t` and `fct_link_info_t` describe FLOGI exchanges and link topology/speed/FLOGI ownership state.

## Control And API

Defines port topology/speed constants, port states, FCT control commands for online/offline/force LIP and completion acknowledgement, and I/O flags for FCA-done handling. `FCT_FILL_CTIU_PREAMBLE()` initializes common CT IU bytes.

Exports conversion, allocation/free, SCSI task allocation, local port registration/deregistration, event handling, command posting/termination, handle lookup, control dispatch, completion paths, port initialize/shutdown, received FLOGI handling, event logging, and WWN string conversion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct_defines.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct_defines.h

## Role

`fct_defines.h` supplies constants shared by the Fibre Channel Target framework. It maps FCT statuses to STMF statuses, defines FCT events, ELS/BLS/name-service opcodes, PRLI bits, FCP control/status bits, well-known addresses, WWN lengths, and forward declarations.

## Status And Events

- `fct_status_t` aliases `stmf_status_t`.
- Defines success/failure/busy/abort/not-found/timeout statuses and FCA-specific failure space.
- Defines FCT-specific failure codes for stuck worker, allocation failure, local port offline, no exchange resources, not logged in, ABTS received, and remote-port reject.
- `FCT_REJECT_STATUS()` embeds reject reason and explanation into a status value.
- Event codes cover link up, link down, link reset, and adapter fatal.

## FC Protocol Constants

- Defines ELS opcodes for LSRJT, ACC, PLOGI/FLOGI/LOGO, ABTX, RLS, ECHO, REC, SRR, PRLI/PRLO, SCN, TPRLO, PDISC, ADISC, RSCN, SCR, and RNID.
- Defines BLS reply opcodes BA_ACC and BA_RJT.
- Defines name server command codes for get/register/deregister operations and CT accept/reject.
- Defines PRLI bits for read/write xfer-rdy disable, initiator/target function, data overlay, FCP confirmation, retry, task retry id, and REC support.
- Defines FC name server class bits and SCR registration function codes.
- Defines FCP control bit helpers for task attributes, task management, reset, task set control, and read/write data direction.
- Defines FCP SCSI status bits for bidirectional response/residual, confirmation requested, residual under/over, sense length valid, and response length valid.

## Address And WWN Helpers

Defines domain controller and well-known address ranges, `FC_WELL_KNOWN_ADDR()`, WWN byte/string buffer lengths, and forward declarations for core FCT structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct_defines.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fctio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fctio.h

## Role

`fctio.h` defines the FC target ioctl ABI used to query target HBA/port information, statistics, link status, and force LIP.

## Ioctl Envelope And Commands

- Defines `FCT_IOCTL`, `FCTIO_CMD`, and `FCTIO_SUB_CMD`.
- Subcommands include adapter list, adapter attributes, adapter port attributes, discovered port attributes, port attributes, adapter port stats, link status, and force LIP.
- Defines transfer direction flags `FCTIO_XFER_NONE`, `FCTIO_XFER_READ`, `FCTIO_XFER_WRITE`, and `FCTIO_XFER_RW`.
- `fctio_t` is the ioctl envelope with transfer, command, flags, command flags, input/output/aux lengths, error code, and 64-bit user buffer addresses.

## HBA And Port Structures

- `fc_tgt_hba_list_t` is a variable-length list of port WWNs.
- `fc_tgt_hba_adapter_attributes_t` reports manufacturer, serial, model, model description, node WWN, node symbolic name, hardware/driver/option ROM/firmware versions, vendor id, number of ports, and driver name.
- `fc_tgt_hba_port_attributes_t` reports last change, node/port WWNs, FC id, type/state, supported class, supported/active FC-4 types, symbolic name, supported/current speed, max frame size, discovered-port count, and fabric name.
- `fc_tgt_hba_adapter_port_stats_t` reports reset age, Tx/Rx frames and words, LIP/NOS, error/dumped frames, and link/sync/signal/protocol/invalid word/CRC counts.

## Constants

Defines T11 FC-HBA port type, port state, and port speed constants, including 1/2/4/8/10/16/32 Gbit and not-negotiated. Defines ioctl result codes and sysevent class/subclass strings for sunfc port attach/detach/online/offline/RSCN and target add/remove.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fctio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fd_debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fd_debug.h

## Role

`fd_debug.h` defines DEBUG-build error printing controls for floppy disk (`fd`) and controller/FC-style code paths.

## Debug Controls

- Defines severity levels `FDEP_L0` through `FDEP_L4` and `FDEP_LMAX`, where L0 is most verbose and L4 is catastrophic.
- In DEBUG builds, `FDERRPRINT()` and `FCERRPRINT()` call `cmn_err` only when the message level is at least the configured level and the function mask matches `fderrmask` or `fcerrmask`.
- In non-DEBUG builds, both macros compile to empty blocks.

## Function Masks

Defines `FDEM_*` mask bits for floppy driver functions and phases including identify/attach, size, open, label, close, strategy/start, read/write, command, execution, recovery, interrupt, watch, ioctls, raw ioctls, property operation, command-state block get/return, reset, recalibrate/seek, format, checkdisk, select, eject, change sense, packlabel, module init/info/fini, and `FDEM_ALL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fd_debug.h -->