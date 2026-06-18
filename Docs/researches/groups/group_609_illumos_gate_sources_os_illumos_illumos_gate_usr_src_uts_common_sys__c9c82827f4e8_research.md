# Group Research: group_609_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__c9c82827f4e8

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All 36 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prsystm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prsystm.h

## Role

`prsystm.h` is a kernel-only procfs integration header. It declares the procfs-side routines used by the core kernel and other modules to expose process, LWP, register, credential, privilege, secflags, address-space, file-descriptor, watchpoint, stepping, and lifecycle state.

## Key Interfaces

The header exports procfs globals `pr_pidlock` and `pr_pid_cv`, then forward-declares procfs-visible structs such as `pstatus`, `lwpstatus`, `psinfo`, `lwpsinfo`, `prcred`, `prpriv`, `prsecflags`, `prfdinfo`, and register-set types.

Important function groups:
- Status and identity collection: `prgetstatus()`, `prgetlwpstatus()`, `prgetpsinfo()`, `prgetlwpsinfo()`.
- Register access: `prgetprfpregs()`, `prgetprxregs()`, `prgetprxregsize()`, plus SPARC/x86 platform-specific routines.
- Credentials/security: `prgetcred()`, `prgetpriv()`, `prgetsecflags()`.
- Lifecycle hooks: `prexit()`, `prfree()`, `prlwpexit()`, `prlwpfree()`, `prexecstart()`, `prexecend()`, `prrelvm()`.
- Debugging and stopping: `prstop()`, `prunstop()`, `prstep()`, `prnostep()`, `prdostep()`, `prundostep()`, `pr_allstopped()`.
- Address-space/watchpoint helpers: `pr_getprot()`, `pr_getsegsize()`, `prnsegs()`, `prmapin()`, `prmapout()`, `pr_watch_emul()`, `pr_free_watched_pages()`.

## Compatibility Notes

Under `_SYSCALL32_IMPL`, the file declares 32-bit procfs status/register conversion and fetch routines. SPARC exposes register-window helpers and optional ASR access; x86 exposes LDT helpers.

## Research Notes

This is not a public user ABI header. It is the contract between procfs implementation code and kernel process/thread/address-space machinery. Audit changes here with procfs lifecycle, ptrace-like stop/step semantics, zone-aware status reporting, and 32-bit procfs ABI conversion in mind.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prsystm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pset.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pset.h

## Role

`pset.h` defines the processor-set user/kernel ABI: the `psetid_t` type, special processor-set identifiers, processor-set types, userland library prototypes, system-call subcodes, and attribute flags.

## Key Interfaces

The special IDs allow callers to express nonliteral targets:
- `PS_NONE`, `PS_QUERY`, `PS_MYID`
- `PS_SOFT`, `PS_HARD`
- `PS_QUERY_TYPE`

Processor-set types are `PS_SYSTEM` and `PS_PRIVATE`.

Outside the kernel, the header declares:
- `pset_create()`, `pset_destroy()`
- `pset_assign()`, `pset_info()`, `pset_list()`
- `pset_bind()`, `pset_bind_lwp()`
- `pset_getloadavg()`
- `pset_setattr()`, `pset_getattr()`

The syscall subcodes map these operations to numeric dispatch values, including forced assignment and LWP binding. The only attribute bit defined here is `PSET_NOESCAPE`.

## Research Notes

This is a compact ABI header. The critical stability surface is the numeric values of special IDs, syscall subcodes, and `PSET_NOESCAPE`, because userland and kernel dispatch logic must agree exactly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pshot.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pshot.h

## Role

`pshot.h` is the private header for the `pshot` pseudo hotplug test driver. It defines user-visible node/property names plus kernel-only soft-state, minor-node, child-device, event, hotplug, power, bus, and debug interfaces.

## Public Surface

The user-accessible constants describe a small device topology:
- Two minor nodes per instance: `devctl` and `testctl`.
- Properties: `dev-name`, `dev-nt`, `dev-compat`.
- Minor-node limits: `PSHOT_MAX_MINOR_PERINST` and `PSHOT_MAX_MINOR_NAMELEN`.

## Kernel Structures

`pshot_minor_t` records a minor node’s owning `pshot_t`, minor number, and name. `pshot_t` carries:
- Instance, `dev_info_t`, lock, state bits.
- NDI event handle/set.
- interrupt block cookie.
- callback caches for normal and test callbacks.
- minor node array.
- power level and busy counters.

The state flags cover open/exclusive-open state, reset pending state, power/fail-suspend behavior, strict-parent/no-involuntary behavior, and power-management support.

## Event and Bus Interfaces

The header declares static prototypes for:
- Driver entry points: open, close, ioctl, probe, attach, detach, info, power.
- `devctl` and `testctl` ioctl handlers.
- Event names/tags for device offline/reset, bus reset/quiesce/unquiesce, debug, sub-reset, and test post.
- NDI event bus ops: get cookie, add/remove callback, post event.
- Bus config/unconfig, child init/uninit, control ops, interrupt ops, power setup, and property helpers.

## Research Notes

This header is effectively a complete private declaration block for a synthetic DDI/hotplug exerciser. It is useful for studying illumos device-tree event plumbing, minor encoding, and test-driver power/hotplug behavior rather than production storage or filesystem paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pshot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptem.h

## Role

`ptem.h` defines the private state used by the pseudo-terminal emulation STREAMS module.

## Data Model

`struct ptem` stores:
- `cflags`: cached terminal control flags.
- `dack_ptr`: preallocated message block used to ACK disconnects.
- `q_ptr`: the ptem read queue.
- `wsz`: terminal window size.
- `state`: ptem state bits.

The state bits are:
- `REMOTEMODE`: pty remote mode.
- `OFLOW_CTL`: output flow control active.
- `IS_PTSTTY`: X/Open terminal mode.

The header also defines `RDSIDE` and `WRSIDE` constants to distinguish common helper calls from read-side versus write-side put procedures.

## Research Notes

This is a small STREAMS terminal-module state header. The main correctness concerns are stable interpretation of `state` bits and consistent queue/message ownership between ptem read/write-side code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptms.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptms.h

## Role

`ptms.h` defines pseudo-terminal manager/subsidiary shared state, pty locking macros, kernel helper prototypes, owner data, and ptm ioctl command numbers.

## Kernel State

`struct pt_ttys` represents one manager/subsidiary pty pair:
- manager and subsidiary read queues.
- null message for subsidiary close.
- process/minor identifiers.
- reference count and state bits.
- condition variable and mutex.
- zone membership.
- real owner UID/GID.

State bits track pair lock, manager open, subsidiary open, and subsidiary tty status: `PTLOCK`, `PTMOPEN`, `PTSOPEN`, `PTSTTY`.

## Synchronization

The `PT_ENTER_READ`, `PT_ENTER_WRITE`, `PT_EXIT_READ`, and `PT_EXIT_WRITE` macros implement a reader/writer protocol over `pt_refcnt`:
- `-1` means writer.
- `0` means idle.
- positive values count readers.

The macros use `pt_lock` and `pt_cv`, with assertions on exit.

## Ioctls

The header defines ptm commands:
- `ISPTM`: verify manager fd.
- `UNLKPT`: unlock pty pair.
- `PTSSTTY`: set tty flag.
- `ZONEPT`: force pty into a zone.
- `OWNERPT`: set subsidiary owner/group.

`pt_own_t` carries owner UID/GID for owner-setting paths.

## Research Notes

This header is a pty control-plane ABI and internal synchronization contract. Zone ownership and `pt_refcnt` reader/writer semantics are the most important invariants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptyvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptyvar.h

## Role

`ptyvar.h` defines legacy pseudo-terminal driver state, packet/user-control ioctl constants, M_CTL message types, and kernel globals for Berkeley-style pty naming.

## Data Model

`struct pty` contains:
- pty flags.
- queued ioctl message blocks and queued-byte count.
- `tty_common_t` state.
- bufcall ID.
- selecting processes for read/write/exception.
- subsidiary device/vnode references.
- controller-side process group.
- pending controller message/control bytes.
- per-pty mutex and condition variables for flags/read/write state.

Flags cover polling collision, nonblocking/async I/O, open/carrier state, subsidiary gone, packet mode, stop/start state, remote mode, no-stop flow control, user-control modes, ioctl-in-progress, close wait, read/write serialization, and waiters.

## Protocol Constants

The M_CTL message constants describe canonicalization and terminal flag behavior between STREAMS modules. The pty ioctl set includes packet mode (`TIOCPKT`), user-control modes, input queue size/space queries, and legacy Sun `ttysize` get/set calls.

## Kernel Declarations

Under `_KERNEL`, the header declares `npty`, `pty_softc`, `ptcph`, and `pty_initspace()`, plus the Berkeley pty bank/digit naming strings.

## Research Notes

This is a legacy pty driver header, distinct from `ptms.h`. It combines STREAMS tty state with BSD-compatible packet mode and naming conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ptyvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/queue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/queue.h

## Role

`queue.h` is the BSD queue macro collection adapted for illumos. It provides intrusive container macros for singly-linked lists, singly-linked tail queues, lists, simple queues, tail queues, and compatibility circular queues.

## Families

The header defines:
- `SLIST_*`: singly-linked lists, forward traversal, O(n) arbitrary removal.
- `STAILQ_*`: singly-linked tail queues with O(1) tail insert.
- `LIST_*`: doubly-linked forward lists using previous-next pointers.
- `SIMPLEQ_*`: simple queues with first and last-next pointers.
- `TAILQ_*`: doubly-linked tail queues with forward/reverse traversal and O(1) insertion/removal.
- `CIRCLEQ_*`: circular queues retained for compatibility but explicitly discouraged due to pointer-aliasing issues.

Each family has head/entry declarations, class-friendly C++ variants where applicable, initializers, accessors, traversal macros, safe traversal variants, insertion/removal, concatenation or swapping as relevant.

## Debug Facilities

Optional debug support includes:
- `QUEUE_MACRO_DEBUG_TRACE`: stores last two mutation sites in `qm_trace`.
- `QUEUE_MACRO_DEBUG_TRASH`: poisons removed links with `(void *)-1`.
- Kernel `QUEUEDEBUG` assertions for `LIST_*` and `TAILQ_*` integrity.

The file also includes `sys/containerof.h` for previous-element derivation macros such as `STAILQ_LAST()` and `LIST_PREV()`.

## Notable Details

`QUEUE_TYPEOF()` handles C++ class lists. `_NOTE(CONSTCOND)` annotations support lint/warlock expectations around macro loops. Some macros assume valid membership and do not guard against missing elements; callers must maintain list invariants.

## Research Notes

This is foundational infrastructure used across many kernel and userland components. The most important behavior is macro side-effect safety and invariant preservation for intrusive links; changing field semantics or debug poisoning would have broad impact.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/raidioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/raidioctl.h

## Role

`raidioctl.h` defines ioctl numbers and structures for RAID controller configuration and firmware update operations.

## Ioctls and Status

The ioctl base is `RAID_IOC`, with commands:
- `RAID_GETCONFIG`: retrieve RAID volume information.
- `RAID_UPDATEFW`: update IOC firmware.
- `RAID_NUMVOLUMES`: retrieve maximum RAID volume count.

RAID flags include enabled, quiesced, and resyncing. RAID states are optimal, degraded, and failed. Disk status values are good, failed, and missing.

## Structures

`raid_config_t` reports:
- target/unit IDs.
- state/flags.
- RAID level.
- disk count, disk IDs, disk statuses.
- RAID capacity.

`RAID_MAXDISKS` is 32.

`update_flash_t` carries a firmware buffer pointer, size, and type. A 32-bit ABI variant `update_flash_32_t` is defined under `_SYSCALL32`.

## Research Notes

This is a small storage-management ABI. The fixed array sizes and 32-bit pointer translation are the main compatibility constraints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/raidioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ramdisk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ramdisk.h

## Role

`ramdisk.h` defines the ramdisk driver names, admin ioctl ABI, OBP/pseudo ramdisk naming helpers, and kernel-private ramdisk device state.

## User/Admin ABI

The control device is `/dev/ramdiskctl`; block and character devices are under `/dev/ramdisk/<name>` and `/dev/rramdisk/<name>`. Minor 0 is reserved for the control node.

The private `ramdiskadm` ioctl interface uses:
- `RD_CREATE_DISK`
- `RD_DELETE_DISK`

`struct rd_ioctl` carries a fixed-size ramdisk name and 64-bit size. Only disks created through `RD_CREATE_DISK` are deletable through this interface.

## Naming and Limits

The header defines:
- `RD_MAX_DISKS` as 1024.
- `RD_NAME_LEN` as 32.
- property names `Nblocks` and `Size`.
- macros to strip OBP `ramdisk-` prefixes and pseudo-device `,raw` suffixes.

## Kernel State

`rd_devstate_t` represents one ramdisk:
- lock, name, devinfo, minor, size.
- either OBP existing physical ranges or allocated physical pages.
- virtual window mapping metadata.
- block/char/layered open counters.
- fake geometry: `dk_geom`, `vtoc`, `dk_cinfo`.
- kstat lock and kstat pointer.

Kernel defaults include 32 active disks, 25% physical memory cap, and default maxphys of 63 KiB.

## Research Notes

This header bridges admin tooling, firmware-created ramdisks, pseudo ramdisks, and disk-label emulation. The mutually exclusive OBP-range versus allocated-page representation is a key invariant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ramdisk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/random.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/random.h

## Role

`random.h` defines random-device and software-random-provider statistics, kernel entropy/random-byte entry points, and the `getrandom(2)` user ABI flags.

## Statistics

`rnd_stats_t` counts bytes generated for `/dev/random`, bytes read from the random cache, and bytes generated for `/dev/urandom`.

`swrand_stats_t` tracks entropy estimate, entropy in/out, and raw bytes in/out for the kernel random provider.

Kernel/stat macros update per-CPU or global stats through direct increments or atomics.

## Interfaces

Kernel or fake-kernel builds declare:
- `random_add_entropy()`
- `random_get_bytes()`
- `random_get_blocking_bytes()`
- `random_get_pseudo_bytes()`

Userland sees `getrandom(void *, size_t, unsigned int)` and flags:
- `GRND_NONBLOCK`
- `GRND_RANDOM`

## Research Notes

This is the public and kernel-facing random API header. The distinction between blocking, pseudo, and `/dev/random`-selected behavior is the main semantic surface.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/random.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl.h

## Role

`rctl.h` defines illumos resource-control ABI flags, privilege levels, user syscalls, entity types, and the kernel’s resource-control data model and operations.

## Public ABI

It defines local actions such as no-action, signal, deny, maximal, and project-database-originated controls. Global actions/properties include syslog, nobasic, lowerable, deny behavior, file-size/CPU-time classes, no local action, infinity, unobservable, unit types, and syslog suppression.

`getrctl()` flags include first, next, and usage. `setrctl()` operations include insert, delete, replace, and recipient-PID use.

`rctl_qty_t` is the resource quantity type and `rctl_priv_t` names basic, privileged, and system values.

Entities are process, task, project, and zone.

## Kernel Model

Kernel-only structures include:
- `rctl_val_t`: one enforced value with privilege, quantity, local actions, signal recipient, and firing time.
- `rctl_ops_t`: action, usage, set, and test callbacks.
- `rctl_t`: a resource control instance with value list/cursor and dictionary entry.
- `rctl_set_t`: hash table of controls for one entity type.
- `rctl_dict_entry_t`: global resource-control metadata and callbacks.
- `rctl_alloc_gp_t`: preallocation bundle for controls and values.

## Kernel Interfaces

The header declares registration, lookup, default-limit, legacy-limit, model maximum/value, validation, enforced-value, test/action, set creation/dup/reset/free, local get/insert/delete/replace, rlimit translation, locked-memory/swap/lofi accounting, and kstat creation helpers.

## Research Notes

`rctl.h` is a central policy/enforcement header for process, task, project, and zone resource limits. The sorted value list, cursor semantics, callback operations, and preallocation paths are important for correctness under low-memory and enforcement-time constraints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl_impl.h

## Role

`rctl_impl.h` contains resource-control implementation details shared between userland support code and kernel/user ABI translation.

## Key Definitions

It defines `RCTLCTL_GET` and `RCTLCTL_SET` operation values. Outside the kernel it declares:
- `rctlctl()`
- `rctllist()`
- `setprojrctl()`

`rctl_opaque_t` is the concrete layout behind opaque `rctlblk_t` data. It carries:
- configured and enforced quantities.
- privilege.
- global flag/action and syslog level.
- local flag/action and signal.
- local recipient PID.
- firing time.

The header also declares `rlim_fd_cur` and `rlim_fd_max`.

`RCTLBLK_INC()` advances through an array of `rctlblk_t` objects using `rctlblk_size()` rather than `sizeof`, preserving opacity.

## Research Notes

This header is sensitive because it exposes the internal shape of resource-control blocks while the public API treats them as opaque. Consumers must use `rctlblk_size()`-based stepping for compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rds.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rds.h

## Role

`rds.h` defines the user/kernel ABI for Reliable Datagram Sockets with RDMA support. It is imported from the OFED/Linux RDS interface and adapted for illumos/SVR4 type conventions.

## Socket Interface

The file defines:
- `AF_RDS`, `PF_RDS`, and `SOL_RDS`.
- socket options for canceling sent messages, memory-region get/free, receive errors, congestion monitoring, and destination-specific MR registration.
- control-message types for RDMA args, destination, memory mapping, RDMA status, and congestion updates.
- RDS info selectors for counters, connections, messages, sockets, TCP/IB/iWARP connections, and connection stats.

## Info Structures

The header defines packed info records for counters, connections, flows, messages, sockets, TCP sockets, and RDMA connections. It uses `#pragma pack(1)` and `__attribute__((packed))` outside lock-lint paths to preserve ABI layout.

Connection/message/socket records carry addresses, ports, sequence numbers, flags, buffer sizes, and transport names.

## Congestion and RDMA

Congestion monitoring uses a 64-bit port-group mask with `RDS_CONG_MONITOR_BIT()` and `RDS_CONG_MONITOR_MASK()`.

RDMA structures include:
- `rds_rdma_cookie_t`
- `rds_iovec`
- memory-region get/free args.
- destination-specific MR args.
- RDMA transfer args and completion notification.

Flags cover read/write permission, fence, invalidate, use-once, dontwait, and notify-me behavior.

## Research Notes

This is a protocol ABI header. The packed layouts, cross-platform integer typedefs, socket option numbers, and RDMA cookie/control-message formats are the main compatibility risks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/reboot.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/reboot.h

## Role

`reboot.h` defines boot/reboot flags, the userland `reboot()` prototype, and kernel boot-flag globals/helpers.

## Flags

`RB_AUTOBOOT` is zero. Other flags control boot behavior:
- ask boot name, single-user, no sync, halt.
- alternate init name, skip boot rc.
- debugger/debug boot behavior.
- crash dump.
- writable root.
- boot argument string.
- config/reconfigure/verbose modes.
- forthdebug and kmdb loading.
- boot-cluster suppression.
- debugger entry at boot.

## Kernel Interfaces

Outside assembly, userland gets `int reboot(int, char *)`.

Under `_KERNEL`, the header declares `boothowto`. For boot code, `bootflags()` takes a string buffer and size; otherwise it takes `struct bootops *`.

## Research Notes

This header is a stable boot-control ABI. Numeric flag values are externally meaningful to boot loaders, init, kernel reboot paths, and debugging tools.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/reboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refhash.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refhash.h

## Role

`refhash.h` declares a generic reference-counted hash table helper for kernel objects with embedded linkage.

## Data Model

`refhash_link_t` is embedded in client objects and contains:
- per-bucket chain link.
- global object-list link.
- flags.
- reference count.

`RHL_F_DEAD` marks a dead object.

`refhash_t` contains bucket lists, global object list, object size and embedded-offset metadata, hash/compare callbacks, and optional destructor.

## Interfaces

The API supports:
- create/destroy.
- insert/remove.
- lookup and linear search.
- hold/release.
- first/next iteration.
- object validity checking.

Callbacks are typed for hash, compare, destructor, and evaluation predicates.

## Research Notes

This header defines intrusive lifetime-managed hash infrastructure. Correct client use depends on embedding `refhash_link_t` at the registered offset and balancing holds/releases around lookup/iteration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr.h

## Role

`refstr.h` declares the public kernel-facing interface for reference-counted immutable strings.

## Interface

The actual `struct refstr` layout is private. Under `_KERNEL` or `_FAKE_KERNEL`, the API provides:
- `refstr_alloc(const char *)`
- `refstr_value(refstr_t *)`
- `refstr_hold(refstr_t *)`
- `refstr_rele(refstr_t *)`

## Research Notes

This is an intentionally opaque handle API. Consumers should treat returned string values as owned by the `refstr_t` lifetime and should not depend on implementation layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr_impl.h

## Role

`refstr_impl.h` defines the private implementation layout for `refstr_t`.

## Layout

`struct refstr` contains:
- `rs_size`: allocation size.
- `rs_refcnt`: reference count.
- `rs_string[1]`: start of the stored constant string.

The comment states that no allocation should exceed 4 GiB, matching the 32-bit size field.

## Research Notes

This header is for implementation code, not ordinary consumers. The public header intentionally hides this layout, so dependencies on `rs_size`, `rs_refcnt`, or trailing-string allocation should stay inside refstr internals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/refstr_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/resource.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/resource.h

## Role

`resource.h` defines process priority classes, POSIX/BSD resource limits, rlimit/rusage structures, large-file and 32-bit ABI variants, and userland priority/resource APIs.

## Priority and Limits

Priority targets include process, process group, user, group, session, LWP, task, project, zone, and contract.

Resource limits include CPU, file size, data, stack, core, file descriptors, and virtual memory/address space. `RLIM_NLIMITS` is 7.

`rlim_t` and infinity/saved constants vary by LP64 and large-file compilation model. `_SYSCALL32` defines `rlim32_t` and `struct rlimit32`.

## Structures

`struct rlimit` contains current and maximum limits. `struct rlimit64` is available under `_LARGEFILE64_SOURCE`.

`struct rusage` reports user/system time and counters for faults, swaps, block I/O, STREAMS messages, signals, and context switches. `_SYSCALL32` defines `struct rusage32`.

## User APIs

Outside the kernel, the header defines `RUSAGE_SELF`, `RUSAGE_LWP`, and `RUSAGE_CHILDREN`, handles large-file symbol remapping, and declares:
- `setrlimit()`, `getrlimit()`
- optional `setrlimit64()`, `getrlimit64()`
- `getpriority()`, `setpriority()`
- `getrusage()`

## Research Notes

This is a stable ABI header with careful LP64/ILP32 and large-file compatibility. Symbol remapping and saved-limit sentinel values are the most compatibility-sensitive parts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rgb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rgb.h

## Role

`rgb.h` defines console/display color layout structures, 16-color and 256-entry color-map constants, ANSI/VGA/Sun color translations, and RGB conversion helpers.

## Data Model

`rgb_color_t` describes a color component position and size. `rgb_t` groups red, green, and blue component descriptors and is exported as `rgb_info`.

`text_cmap_t` stores red/green/blue arrays for the 16 base colors. `cmap4_to_24` maps 4-bit text colors to 24-bit components.

## Color Translation

The header defines `pc_colors_t` for standard 16-color VGA ordering and `sun_colors_t` for Sun console ordering. Translation tables include dim/bright mappings and Solaris-to-PC/PC-to-Solaris color arrays.

Functions:
- `rgb_to_color()`
- `rgb_color_map()`

## Research Notes

This is console color-format infrastructure. It bridges bootloader-provided RGB bit layouts, VGA-style colors, and Sun console color ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rgb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rlioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rlioctl.h

## Role

`rlioctl.h` defines rlogin STREAMS module ioctl and packet-control constants.

## Constants

The header supplies fallback definitions for `TRUE` and `TIOCPKT_WINDOW`, then defines rlogin-relevant packet bits:
- `TIOCPKT_FLUSHWRITE`
- `TIOCPKT_NOSTOP`
- `TIOCPKT_DOSTOP`

`RLOGIN_MAGIC` is `0xff`, matching RFC 1282’s two-byte magic prefix for rlogin protocol requests.

The ioctl namespace is `RLIOC`, with `RL_IOC_ENABLE` used to start the module and optionally insert provided data at the head of the read-side queue.

## Research Notes

This is a small protocol-control header for rlogin STREAMS support. Its important surface is the packet bit compatibility with pty packet mode and RFC 1282 magic-byte handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rlioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm.h

## Role

`rsm.h` defines kernel-agent ioctl command groups, debug categories, internal ioctl payload structures, polling/event payloads, and remote messaging structures for Remote Shared Memory.

## Ioctl Surface

Command groups cover controller, export segment, import segment, queue, topology, barrier, error count, bell, iovec, and map-address operations. Specific ioctls include controller attributes, barrier info/open/order/close/check, export create/bind/rebind/unbind/publish/republish/unpublish, import connect/disconnect, topology size/data, getv/putv, ring bell, consume event, and address mapping.

`RSM_IOCTL_CMDGRP()` extracts command groups.

## Kernel-Agent Structures

The file defines:
- internal controller attributes with controller address.
- kernel-agent iovec and scatter-gather structures, including 32-bit variants.
- poll event and consume-event messages.
- generic `rsm_ioctlmsg_t` with controller name, argument buffers, virtual address, offsets, segment key, ACL, node/hardware address, permission, barrier, generation number, and resource number.

## Remote Messaging

RSM IPC messages use `rsmipc_cookie_t` plus typed message headers. Message types cover segment connect/disconnect, importing/not-importing, reply, bell, republish, suspend/resume, send-queue readiness, and credits.

Request, control, and reply messages carry segment keys, permissions, adapter hardware addresses, cookies, credits, segment metadata, and owner/mode fields.

## Research Notes

This header is the bridge between RSM user APIs, the kernel agent, and remote-node messaging. ABI-sensitive areas include ioctl numeric grouping, 32-bit structure translation, and the contiguous residual-count/flags assumption in scatter-gather structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_common.h

## Role

`rsm_common.h` defines common RSM/RSMAPI/RSMPI versioning, error codes, segment/service ID ranges, permission bits, direct-access sizes, core handle types, and barrier representation.

## Error and ID Spaces

`RSM_VERSION` is 5. Return codes cover API misuse, bad handles, publication/mapping state errors, permissions, barriers, resource exhaustion, unreachable nodes, connection aborts, timeouts, and bad configuration. RSMPI-specific errors start at 101 and include driver/controller registration, memory binding, handler, queue, and communication failures.

Segment/service ID ranges partition driver-private, cluster transport, library, DLPI, HPC, OPS, and user application spaces.

## Types

The header defines:
- `rsm_addr_t`, `rsm_node_id_t`, `rsm_memseg_id_t`, `rsm_permission_t`.
- import/export segment handle opaque pointer types.
- permissions `RSM_PERM_NONE`, `RSM_PERM_READ`, `RSM_PERM_WRITE`, `RSM_PERM_RDWR`.
- direct-access size enum values for 8/16/32/64-bit access.
- barrier types and barrier mode.

`rsm_barrier_t` is four `rsm_barrier_component_t` unions, each capable of holding integer, byte, char, or pointer representations.

## Research Notes

This is the foundational stable RSM type/error header. Numeric error values and ID ranges are central ABI contracts for both user and provider sides.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_in.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_in.h

## Role

`rsm_in.h` defines internal kernel-agent state for RSM resources, import sharing, resource tables, hash tables, IPC slots, importer tracking, and DR/path-related state.

## Driver and Resource State

The header sets driver constants such as minor number, controller count, IPC queue sizes, service ID, queue size, max segments, max nodes, and max controllers.

`rsm_driver_data` tracks driver state, dynamic reconfiguration callbacks, and synchronization. Driver states cover new, OK, pre/post-delete, DR, registration, and unregistration processing.

`rsm_resource_state_t` models export/import lifecycle states from new/bind/export/connect/mapping/active through quiesce, disconnect, zombie, and abort states. `rsm_resource_type_t` distinguishes export segment, import segment, and barrier resources.

## Segment Model

`rsmresource_t` is the common resource header. `rsmseg_t` embeds it and adds owner IDs, length, region list, flags, poll state, condition variable, NIC segment ID, ACLs, pollhead, devmap cookies, mapinfo, RSMPI handles, umem cookie, shared-import pointer, RDMA count, and process pointer.

`rsm_import_share_t` tracks shared importers for a node/segment: state, refcounts, map counts, mode/owner, mapinfo, flags, and connect cookie.

## Tables and Messaging

The file defines:
- block-based resource table roots.
- hash tables guarded by rwlocks.
- IPC slots with flags/cookie/data and condition variables.
- IPC descriptor with fixed slot array.
- importing and republish tokens.
- list heads/elements for suspend acknowledgements and node-dead state.

## Research Notes

This is an internal state-machine header. Correctness depends on lock macros, resource state transitions, shared-import refcount/mapcount handling, and IPC slot cookie sequencing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_in.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmapi_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmapi_common.h

## Role

`rsmapi_common.h` defines common application-facing RSMAPI handle types, controller attributes, access-list entries, barrier wrapper, scatter-gather structures, and API flags.

## Types and Structures

It declares opaque local-memory and controller handles.

`rsmapi_controller_attr_t` reports direct/atomic access sizes, page size, export/import segment size limits, total import/export map limits, and segment counts.

`rsmapi_access_entry_t` maps a node ID to permissions.

`rsmapi_barrier_t` stores a segment pointer, generation number, and private data.

Scatter-gather I/O uses `rsm_iovec_t` entries, each identifying local memory by handle or virtual address plus local/remote offsets and transfer length. `rsm_scat_gath_t` wraps request/residual counts, flags, remote handle, and iovec pointer.

## Flags

I/O vector types are `RSM_HANDLE_TYPE` and `RSM_VA_TYPE`.

Export creation flags include rebind allowance and nonblocking segment creation. Scatter-gather flags include implicit signal post and no-accumulate signal post behavior.

## Research Notes

This header defines the user-visible shape of RSMAPI bulk-transfer and access-control operations. It must remain aligned with the kernel-agent equivalents in `rsm.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmapi_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmka_path_int.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmka_path_int.h

## Role

`rsmka_path_int.h` defines internal RSM kernel-agent path-management structures for adapters, paths, IPC send queues, receive buffers, work queues, topology reporting, and reference-count macros.

## Path and Work Model

A single-thread/single-task deferred work model handles path-up/path-down processing. `work_token_t` and `work_queue_t` implement a simple FIFO with mutex and condition variable.

Path states include down, up, active, and going-down. Deferred opcodes cover IPC down/up.

`path_t` records remote node/device/hardware address, state, flags, lock, local adapter, sendq token, work tokens, receive buffer, incarnation numbers, reference count, and hold condition variable.

## Adapter and IPC Structures

`adapter_t` represents a local RSM controller with instance, devinfo, hardware address, RSMPI handle/attributes/ops, handler args, path list, and refcount.

`adapter_listhead_t` groups adapters by device name and tracks adapter/path counts.

`ipc_info_t` tracks per-remote-node liveness and sendq token lists.

`sendq_token_t` carries the RSMPI send queue handle, refcount, receiver buffer availability, and wait condition.

`recv_info_t` tracks received-message circular queue state, processed-message counts, remote sendq readiness, and receive taskq.

## Topology ABI

The topology structures describe local controllers and remote controller connections. `rsmka_topology_t` points to per-local-controller `rsmka_connections_t` records, each with remote controller entries and connection state. A 32-bit pointer variant is provided.

## Research Notes

This header is about cluster interconnect path state. The key invariants are reference-count macros, sendq token lifetime, path state transitions, incarnation numbers, and topology structure sizing/alignment.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmka_path_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi.h

## Role

`rsmpi.h` defines the RSM Provider Interface contract between RSM clients/kernel agent and controller drivers. It includes callback types, controller attributes, memory descriptors, scatter-gather I/O, interrupt/send-queue types, the provider operations vtable, controller acquisition APIs, and convenience dispatch macros.

## Provider Capabilities

`rsm_controller_attr_t` describes controller name/address, direct/atomic/error access sizes, error behavior, MMU protection support, page/segment/map limits, I/O-space capabilities, interrupt features, data alignment/size, piggyback support, and resource-callback support.

RSMPI interrupt service ranges divide driver, framework, reserved, Sun, and user service IDs. Send queue flags control fencing, full-queue behavior, and reliability. Send flags control queue/deliver/poll/sleep/lower-fence semantics.

## Memory and I/O

`rsm_memory_local_t` can describe local memory as virtual address, buf, export handle, or invalid. `rsmpi_iovec_t` and `rsmpi_scat_gath_t` define provider-side scatter-gather import get/put operations.

## Operations Vtable

`rsm_ops_t` includes:
- export segment create/destroy/bind/unbind/rebind/publish/unpublish/republish.
- import connect/disconnect.
- typed get/put operations for 8/16/32/64-bit values plus bulk get/put.
- import mapping/unmapping.
- barrier open/close/reopen/order and barrier-mode get/set.
- thread init/fini.
- send queue create/config/destroy/send.
- interrupt handler register/unregister.
- scatter-gather getv/putv.
- peer discovery.
- extension hook.

Macros dispatch each operation through a `rsm_controller_object_t`.

## Research Notes

This is the central RSM driver provider ABI. The vtable layout, callback sentinel values, opaque handle types, and dispatch macros must remain in sync across RSMOPS, controller drivers, and the kernel agent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi_driver.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi_driver.h

## Role

`rsmpi_driver.h` defines the registration interface used by RSMPI controller drivers to register with the RSMOPS module.

## Structures

`rsmops_registry_t` contains:
- RSMPI driver version.
- driver name with `MAX_DRVNAME` 15 plus terminator.
- get-controller handler.
- release-controller handler.
- driver thread entry point.

`rsmops_ctrl_t` records one registered controller: number, outstanding-handle refcount, attributes, provider handle, next pointer, and back pointer to its driver registry.

`rsmops_drv_t` records one registered driver: registry data, controller count, driver list link, controller list head, and thread ID.

## APIs

The header declares:
- `rsm_register_controller()`
- `rsm_unregister_controller()`
- `rsm_register_driver()`
- `rsm_unregister_driver()`

## Research Notes

This is the provider registration companion to `rsmpi.h`. Driver/controller lifetime and outstanding controller-handle refcounts are the main correctness concerns.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsmpi_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rt.h

## Role

`rt.h` defines real-time dispatcher class internal structures.

## Data Structures

`rtdpent_t` is one real-time dispatcher parameter table entry with global priority and default quantum.

`rtproc_t` is the real-time class-specific per-thread/process scheduling state:
- assigned quantum and time remaining.
- RT class priority.
- flags.
- time-quantum signal.
- associated thread pointer.
- next/previous links.

The defined flag is `RTBACKQ`, meaning the process goes to the back of the dispatch queue when preempted.

Under `_KERNEL`, `rtkparms_t` carries kernel RT parameters: priority, quantum, quantum signal, and control flags.

## Research Notes

This is a scheduler-class state header. It is tightly coupled to real-time dispatching and priocntl administration, with `rtpriocntl.h` exposing the user/admin side.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rtpriocntl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rtpriocntl.h

## Role

`rtpriocntl.h` defines real-time class structures and constants for the `priocntl` system call and scheduler administration.

## Priocntl Structures

`rtparms_t` contains real-time priority and time quantum split into seconds and nanoseconds.

`rtinfo_t` reports the configured maximum real-time priority.

Special values:
- `RT_NOCHANGE`
- `RT_TQINF`
- `RT_TQDEF`

Varargs keys identify RT priority, quantum seconds, quantum nanoseconds, and time-quantum signal.

## Dispatcher Administration

`rtadmin_t` points to an array of `rtdpent` entries and carries entry count and command. `_SYSCALL32` defines `rtadmin32_t`.

Commands:
- `RT_GETDPSIZE`
- `RT_GETDPTBL`
- `RT_SETDPTBL`

## Research Notes

This header is the user/admin ABI for real-time scheduler parameters. Its data layouts must match `rt.h` dispatcher table entries and 32-bit syscall translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rtpriocntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock.h

## Role

`rwlock.h` declares the public kernel/DDI readers-writer lock interface.

## Types

`krw_type_t` distinguishes DDI driver rwlocks from default kernel rwlocks.

`krw_t` identifies requested mode:
- writer.
- reader.
- reader that may starve writers.

`krwlock_t` is opaque, represented as one pointer-sized opaque slot.

## Kernel API

Under `_KERNEL`, the header declares:
- init/destroy: `rw_init()`, `rw_destroy()`.
- enter/try/exit: `rw_enter()`, `rw_tryenter()`, `rw_exit()`.
- mode changes: `rw_downgrade()`, `rw_tryupgrade()`.
- state queries: `rw_read_held()`, `rw_write_held()`, `rw_lock_held()`, `rw_read_locked()`, `rw_iswriter()`, `rw_owner()`.
- backoff/delay hooks: `rw_lock_backoff`, `rw_lock_delay`.

Convenience macros map `RW_READ_HELD`, `RW_WRITE_HELD`, `RW_LOCK_HELD`, and `RW_ISWRITER`.

## Research Notes

This is a core kernel synchronization ABI. The implementation layout is hidden here and exposed only in `rwlock_impl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock_impl.h

## Role

`rwlock_impl.h` defines implementation-private layout and bit encodings for kernel readers-writer locks.

## Layout and Bits

`rwlock_impl_t` stores a single `uintptr_t rw_wwwh`, packing waiters, writer-wanted state, write-locked owner, and reader hold count.

Bit meanings:
- `RW_HAS_WAITERS`
- `RW_WRITE_WANTED`
- `RW_WRITE_LOCKED`
- `RW_READ_LOCK`

`RW_WRITE_LOCK(thread)` encodes writer ownership by OR-ing the thread pointer with the write-locked bit. Hold-count and owner masks are derived from `-RW_READ_LOCK`.

## Query Macros

The `_RW_READ_HELD`, `_RW_WRITE_HELD`, `_RW_LOCK_HELD`, and `_RW_ISWRITER` macros are used both by rwlock implementation code and DTrace subroutines, which cannot call the normal `rw_*()` functions.

## Research Notes

This is a low-level synchronization representation header. Pointer alignment, bit packing, and current-thread writer ownership assumptions are essential; changes here affect rwlock internals and DTrace lock-state inspection.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwstlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwstlock.h

## Role

`rwstlock.h` defines an alternate readers-writer lock that is interruptible and may be released by a thread other than the acquiring thread.

## Data Model

`rwstlock_t` contains:
- `rwst_count`: positive reader count, negative writer ownership encoding, or zero.
- reader and writer condition variables.
- mutex.

Writer ownership is encoded with `LONG_MIN | curthread`, and macros can recover the owner by masking off `LONG_MIN`.

## Operations and Macros

Flags:
- `RWST_TRYENTER`
- `RWST_SIG`

Macros test held/read/write ownership, waiters, signal-aware waits, wakeups, and read/write enter/exit count transitions.

The API includes:
- `rwst_enter()`, `rwst_enter_sig()`, `rwst_tryenter()`
- `rwst_exit()`
- `rwst_init()`, `rwst_destroy()`
- `rwst_lock_held()`
- `rwst_owner()`

## Research Notes

Unlike normal rwlocks, this lock is designed for interruptible acquisition and cross-thread release. The encoded owner/count field is the key invariant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwstlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sad.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sad.h

## Role

`sad.h` defines the STREAMS Administrative Driver ABI for autopush configuration, versioned ioctl layout, device names, and kernel autopush cache interfaces.

## Ioctl Versioning

Only `SAD_GAP` and `SAD_SAP` are currently versioned, but the namespace reserves a 4-bit version and 4-bit command field. Userland defaults `AP_VERSION` to 0 unless explicitly defined; the kernel defaults to latest version 1.

Ioctls:
- `SAD_SAP`: set autopush.
- `SAD_GAP`: get autopush.
- `SAD_VML`: validate module list.

Devices are `/dev/sad/user` and `/dev/sad/admin`.

## Autopush Structures

`apcommon` carries command, major, minor, last minor, and number of modules. `apdata` adds an anchor position. `strapush` combines common data, a module-name list of up to `MAXAPUSH`, and versioned data when `AP_VERSION > 0`.

Commands are clear, one minor, range, and all minors.

## Kernel State

Kernel code gets ioctl state constants, version/command extraction macros, versioned structure lengths, `saddev`, `autopush`, and helper prototypes. Autopush cache operations are grouped by locking requirement: no `ss_sad_lock`, internally acquiring it, or requiring it already held.

Audit hooks for STREAMS messages and fd send/receive are declared.

## Research Notes

This is a versioned STREAMS admin ABI. `strapush` growth without breaking old binaries is the main design point, and autopush cache locking requirements are explicitly documented.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahciem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahciem.h

## Role

`ahciem.h` defines the private ioctl interface for AHCI enclosure-management LED services.

## Ioctls

The ioctl base is `AHCI_EM_IOC`, with:
- `AHCI_EM_IOC_GET`: read enclosure-management LED status.
- `AHCI_EM_IOC_SET`: modify LED state.

The interface supports up to 32 ports.

## Data Structures

`ahci_em_led_state_t` defines LED bits:
- identify enable.
- fault enable.
- activity disable.

`AHCI_EM_FLAG_CONTROL_ACTIVITY` marks activity LED control support.

`ahci_ioc_em_get_t` reports port count, flags, and per-port status array.

`ahci_ioc_em_set_t` carries target port, operation, LED bits, and padding. Set operations are add, remove, or replace.

## Research Notes

This is a small private AHCI management ABI. It maps user/admin LED intent onto AHCI enclosure-management state tracked in `ahcivar.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahciem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcireg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcireg.h

## Role

`ahcireg.h` defines AHCI hardware register constants, capability/control/interrupt bits, register address macros, SATA FIS layouts, received-FIS memory layout, PRDT entries, command tables, and command headers.

## Register and Capability Model

The header defines AHCI limits for ports, command slots, and PRDT entries. It provides HBA capability bits for ports, enclosure management, command coalescing, slot count, power states, FIS switching, port multipliers, AHCI-only mode, speed, command-list override, LEDs, staggered spin-up, NCQ, 64-bit addressing, and extended capabilities such as BIOS/OS handoff and DevSleep.

Global register macros compute addresses for CAP, GHC, interrupt status, ports implemented, version, CCC, enclosure management, CAP2, and BOHC.

Per-port macros compute addresses for command-list/FIS bases, interrupt status/enable, command/status, taskfile, signature, SStatus/SControl/SError/SActive, command issue, SNotification, and FIS-based switching.

## Interrupts and Port Bits

Port interrupt bits cover register/PIO/DMA/set-device/unknown FIS events, descriptor processed, connect changes, mechanical presence, PhyRdy, port multiplier errors, overflow, interface/host bus errors, taskfile errors, and cold presence detection.

Port command/status bits cover start, spin-up, power-on, command-list override, FIS receive enable, active command slot, FIS/command-list running, cold/mechanical presence, port multiplier, hotplug, ATAPI, LED, link power management, and ICC state.

## FIS and DMA Structures

The file defines hardware-format structures for:
- host-to-device register FIS.
- device-to-host register FIS.
- set-device-bits FIS.
- DMA setup FIS.
- PIO setup FIS.
- BIST active FIS.
- unknown FIS.
- command FIS.
- received FIS block.

Numerous macros set/get packed FIS fields.

## Command Structures

`ahci_prdt_item_t` describes one physical region descriptor and exposes interrupt-on-completion and byte-count getters.

`ahci_cmd_table_t` contains command FIS, ATAPI CDB area, reserved space, and PRDT array.

`ahci_cmd_header_t` contains command description fields, PRD byte count, command table base addresses, and helper macros for PRDT length, port multiplier port, reset, prefetch, write, ATAPI, and FIS length.

## Research Notes

This is the AHCI hardware ABI header. Correctness depends on exact bit positions, offsets, packed hardware layouts, and PRDT/command-slot sizing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcireg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcivar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcivar.h

## Role

`ahcivar.h` defines private AHCI driver state: address qualifiers, port-multiplier information, per-port DMA/command/event state, controller state, capability flags, attach-state tracking, debug controls, timing constants, and enclosure-management message layouts.

## Addressing

`ahci_addr_t` identifies an HBA port and optional port-multiplier port with qualifier bits for null, port, PM port, and port multiplier. Macros test validity and initialize direct port, PM port, or PMULT addresses.

## Port State

`ahci_pmult_info_t` stores port-multiplier device count, per-PM-port device types/states, NCQ PM port, and pending notification tags.

`ahci_port_t` tracks one HBA port:
- physical port number, device type, port state, PM info.
- flags for mopping, polling, request sense, started, read-log-ext, no-device, port-multiplier read/write, ignored IPMS, PMULT notification, hotplug, and error printing.
- received-FIS DMA state.
- command-list and command-table DMA/access handles.
- sync command condition variable and port mutex.
- NCQ limits, pending non-NCQ/NCQ tags, slot packets/timeouts.
- completed packet queue.
- PRD byte counts.
- error-retrieval and PMULT read/write packets.
- reset-in-progress flag.
- event taskq/args and mop counter.

Warlock annotations document mutex protection.

## Controller State

`ahci_ctl_t` records devinfo, PCI IDs, port/cport mappings, port counts, implemented-port bitmap, port pointers, flags, power state, PCI config handle, AHCI BAR mapping, SATA framework transport, DMA attributes, watchdog timeout, mutex, interrupt handles/metadata, FMA capability, and enclosure-management state.

Controller flags cover attach, detach, suspend, and quiesce. Capability bits include PIO multiple DRQ, command-list limitations, NCQ, power management, 32-bit DMA constraints, SCLO, initialization reset, SNotification, port multiplier switching modes, SRST quirk, enclosure services, and DevSleep.

## Support Macros

The header provides helpers for command-in-progress classification, command type constants, attach-state milestones, delay/poll constants, bit set/clear, debug categories, and `AHCIDBG()` tracing/logging.

Enclosure-management definitions include buffer sizing, LED message values, message types, and packed LED/header message structures.

## Research Notes

This is the AHCI driver’s central private state header. The major invariants are per-port mutex protection, command-slot tag accounting, NCQ versus non-NCQ exclusion, port-multiplier state routing, attach unwind state bits, and enclosure-management readiness flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcivar.h -->