# Group Research: group_446_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_mtio_h_sources_os_bsd_05de3a72b30b

Scope: `Docs/research_subset_a.md`

This grouped report covers FreeBSD `sys/sys` headers that define public ioctl ABIs, kernel synchronization and lookup interfaces, per-CPU storage, physical-memory boot helpers, pipe state, hwpmc control/logging ABI, scheduling/privilege constants, and small utility APIs.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mtio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mtio.h

This header defines the magnetic tape ioctl ABI shared by userland tools and tape drivers. It includes `<sys/ioccom.h>` and, outside the kernel, `<sys/types.h>`, then exposes operation request structures, status structures, SCSI tape error reporting, extended positioning, XML-style extended status/parameter exchange, and ioctl numbers.

The core command structure is `struct mtop`, containing an operation code and count. Operation codes cover classic tape actions (`MTWEOF`, spacing files/records, rewind, offline, cache toggles) and FreeBSD extensions for block size, density, erase, EOD, compression, retension, setmarks, load, and immediate EOF writes. `struct mtget` is the legacy status structure: it includes device type, device-dependent status/error registers, residual count, FreeBSD block size/density/compression fields per mode, and current file/block numbers.

The SCSI-oriented error ABI is `struct scsi_tape_errors`, wrapped in `union mterrstat` with fixed 256-byte padding. It separates last data-I/O and control-I/O sense/CDB/residual state and reserves cumulative read/write error counters. Additional structs define block limits (`mtrblim`), extended locate (`mtlocate`), extended XML status (`mtextget`), typed parameter values (`mtparamset`), and batch parameter setting (`mtsetlist`).

The ioctl namespace uses magic `'m'`: `MTIOCTOP`, `MTIOCGET`, logical/hardware position reads and locates, `MTIOCERRSTAT`, EOT model get/set, block limits, extended locate/get, parameter get/set, and list set. The default userland tape device is `DEFTAPE "/dev/nsa0"`. Filesystem relevance is indirect: this is a stable device-control ABI for sequential storage devices used by backup/archive tooling, with careful fixed-size layouts for kernel/user compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mutex.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mutex.h

This kernel header defines FreeBSD mutex types, state bits, APIs, fast-path macros, thread lock helpers, mutex pools, Giant handling, and sysinit glue. It includes lock object definitions and, under `_KERNEL`, per-CPU, lock profiling/stat, atomic, and CPU function headers.

Mutex initialization options include `MTX_DEF` sleep mutexes, `MTX_SPIN` spin mutexes, recursion support, WITNESS/profile suppression, and `MTX_NEW`. Runtime state is stored in `mtx_lock`; sleep mutexes use flag bits for recursion, waiters, and destroyed state, while spin locks are handled separately. Public macros intentionally route through members like `mtx_lock` to catch malformed objects at compile time.

The header is performance-critical: non-debug kernels inline common lock/unlock paths using atomic compare-and-swap/fcmpset operations, only falling back to sleep or spin helper functions when profiling is active or the fast path fails. SMP spin lock paths enter critical spinlock state before acquisition and release it on unlock; UP paths maintain recursion directly. Debug/profile configurations route calls through out-of-line wrappers that preserve file/line information.

It also defines `thread_lock`, `thread_unlock`, `mtx_sleep`, ownership/recursion/initialization/name accessors, and mutex pool helpers. `DROP_GIANT`/`PICKUP_GIANT` save and restore Giant recursion around code that must temporarily release it. `MTX_SYSINIT` creates static initializer and uninitializer records. This file is foundational kernel synchronization infrastructure used throughout VFS, VM, device drivers, and networking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/namei.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/namei.h

This header defines FreeBSD pathname lookup state and flags. It is central to VFS name resolution: `namei()` converts a pathname plus lookup policy into result vnodes and associated metadata.

`enum nameiop` distinguishes lookup, create, delete, and rename operations. `struct componentname` carries per-component lookup arguments and state: flags, credentials, operation type, lock flags, pathname buffer, current component pointer, and component length. `struct nameidata` wraps the whole lookup request and result set, including source pathname, segment type, capability rights, start/root/top directories, dirfd for `*at` calls, filecaps, result vnode/parent vnode, result flags, symlink/path traversal state, embedded component name, RBENEATH capability tracking, and sequence counters used by UFS/cache validation.

Kernel-only flags are split between operational modifiers (`LOCKLEAF`, `LOCKPARENT`, `FOLLOW`, `EMPTYPATH`, `RBENEATH`, etc.), parameter descriptors (`RDONLY`, `NOCROSSMOUNT`, `AUDITVNODE*`, `OPENREAD`, `OPENWRITE`, `MAKEENTRY`, `ISLASTCN`, `ISDOTDOT`, and others), internal flags callers must not provide, result flags, and local call flags for strict relative/capability lookup handling. The `NDINIT*` macros initialize `struct nameidata` for common absolute, dirfd-relative, rights-aware, and vnode-starting cases; invariant builds poison and validate fields to catch API misuse.

The header declares `namei`, `vfs_lookup`, `vfs_lookup_isroot`, `vfs_lookup_nameidata`, `vfs_relookup`, fast-path cache lookup support, pathname buffer/free helpers, and name cache statistics (`struct nchstats`). Filesystem relevance is direct and high: VFS, filesystems, capability mode, auditing, mount crossing, symlink expansion, whiteouts, and vnode locking policy all meet at this interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nlist_aout.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/nlist_aout.h

This header defines legacy a.out symbol table entries and associated constants. `struct nlist` represents one symbol, with conditional layout support for `_AOUT_INCLUDE_`: the name field can be a memory pointer or an on-disk string-table offset union, otherwise it is exposed as a pointer for consumers of `nlist.h`.

The fields record symbol type, auxiliary/binding bits, stab description, and value/address. Constants define classic a.out symbol classes such as undefined, absolute, text, data, BSS, indirect, common, GNU set symbols, file/warning entries, external bit, type mask, and debugger/stab mask. Helper macros extract/pack the low-nibble auxiliary field and high-nibble binding field from `n_other`, with definitions for object/function auxiliary types and weak binding.

Filesystem relevance is historical/tooling oriented: this is not part of runtime VFS, but it defines on-disk executable symbol metadata understood by older tools and compatibility code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nlist_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/nv.h

This header declares the FreeBSD nvlist public API for name/value lists. It includes the opaque base type from `<sys/_nv.h>`, and in userland pulls in standard bool, integer, stdio, varargs, and namespace-renaming support.

It defines maximum name length, all supported value type numbers, and nvlist flags for case-insensitive lookup and non-unique names. The API covers lifecycle and error state (`nvlist_create`, `destroy`, `error`, `empty`, `flags`, `set_error`, `clone`), diagnostic dumps in userland, packed-size calculation, pack/unpack, socket send/recv/xfer, iteration, parent/array linkage queries, and existence checks by type.

For each supported type, the API provides add, append-to-array, move/consume, get, take/remove-and-return, and free operations. Types include null, bool, number, string, nested nvlist, binary, arrays of those core types, and userland-only descriptor/descriptors arrays. The distinction between `add` and `move` is important: add copies caller-provided data while move consumes caller-owned buffers or descriptors.

Filesystem and kernel relevance comes from structured control-plane data exchange. Nvlists are used by facilities that need extensible typed parameters across kernel/user or subsystem boundaries without adding a new fixed struct for every revision.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nv_namespace.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/nv_namespace.h

This header remaps nvlist, nvpair, cnvlist, and dnvlist symbols to `FreeBSD_`-prefixed names. It is included by userland-facing nvlist headers so FreeBSD's libnv symbols can coexist with other libraries or operating-system implementations that expose similarly named nvlist APIs.

The file is entirely preprocessor definitions. It covers public nvlist APIs, internal-looking helpers that are still linked from userland objects, descriptor functions, append/move/take/free variants, pack/unpack routines, nvpair construction and accessors, and the `nvlist_t` type name itself.

Its significance is ABI hygiene rather than algorithmic behavior. By redirecting names at compile time, FreeBSD can preserve a broad nvlist API while reducing symbol collision risk in portable codebases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/nv_namespace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/osd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/osd.h

This header defines object-specific data slots for kernel objects. `struct osd` stores a slot count, slot pointer array, and list linkage. Comments document locking domains: container object lock and/or `osd_object_lock` for slot state, and `osd_list_lock` for global list linkage.

Kernel APIs allow subsystems to register a slot for an object type with optional destructor and method table, deregister it, reserve storage, set/get/delete values, call registered methods, and clean up all data on object exit. Defined object classes are thread, jail, and khelp, with convenience macros wrapping the generic API for thread and jail storage.

The thread delete macro asserts the target is `curthread`, reflecting lifecycle assumptions around thread OSD mutation. Filesystem relevance is indirect: OSD is an extensibility mechanism for kernel subsystems, allowing modules and policies to associate private state with long-lived core objects without growing those structures for every optional feature.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/osd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/param.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/param.h

This is a core system parameter header. It defines BSD and FreeBSD version macros, kernel compatibility version milestones, common system limits, device/block/page conversion macros, priority sleep flags, filesystem buffer constants, path/symlink limits, bitmap helpers, min/max, byte-order aliases for kernel builds, fixed-point load-average scaling, and miscellaneous container/array helpers.

`__FreeBSD_version` is set to `1600018`, with comments documenting its encoding and update policy for ports and external consumers. Kernel-only `P_OSREL_*` constants record behavior-version thresholds used for compatibility decisions. General limits include command/login/hostname/device-name sizes, process/open-file/argument limits, and `NODEV`.

Storage and filesystem constants are prominent: `DEV_BSHIFT`/`DEV_BSIZE`, `BLKDEV_IOSIZE`, `DFLTPHYS`, `MAXDUMPPGS`, mbuf cluster sizing, page rounding/truncation and page/block conversions, `btodb`/`dbtob`, `MAXBSIZE`, `MAXBCACHEBUF`, `BKVASIZE`, `MAXPATHLEN`, and `MAXSYMLINKS`. These constants constrain buffer cache sizing, block-device I/O granularity, and pathname processing.

The header is widely included and intentionally conservative. Changes here have broad compile-time and ABI/KBI impact across kernel, userland, filesystems, VM, networking, and drivers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pciio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pciio.h

This header defines the `/dev/pci` ioctl ABI for userland inspection and limited manipulation of PCI devices. It includes `<sys/ioccom.h>`, defines `PCI_MAXNAMELEN`, and provides selection, match, result, config access, BAR, VPD, mmap, and BAR I/O request structures.

`struct pcisel` identifies a PCI function by domain, bus, device, and function. `struct pci_conf` reports device IDs, class/subclass/progif/revision, driver name/unit, NUMA domain, reported length, bridge bus fields, and spare room for future ABI expansion. `struct pci_match_conf` and `struct pci_conf_io` implement filtered enumeration with generation/offset/status handling.

Other ioctls operate on config registers (`struct pci_io`), BAR metadata (`pci_bar_io`), VPD element lists, BAR mmap setup, and direct BAR read/write (`pci_bar_ioreq`). Ioctl commands include read/write/attached, get BAR, list VPD, BAR mmap, BAR I/O, and get config.

Filesystem relevance is device-node ABI related: this header defines the stable structures used when userland opens a character device and issues ioctls into PCI bus code. It is important for storage controllers and other filesystem-adjacent hardware discovery/configuration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pciio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pcpu.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pcpu.h

This header defines machine-independent per-CPU state and dynamic per-CPU data access. It refuses assembler inclusion, includes core lock/cpuset/resource/queue headers plus machine-specific `pcpu.h`, and is mostly kernel-facing.

Dynamic per-CPU data is represented by linker set boundaries `__start_set_pcpu`/`__stop_set_pcpu`, an offset array `dpcpu_off[]`, and macros for defining, declaring, and accessing per-CPU variables. `DPCPU_GET`, `SET`, `PTR`, `ID_*`, `SUM`, `VARSUM`, and `ZERO` abstract access to current and remote CPU copies. Some module/architecture combinations avoid `static` definitions because PC-relative loads may not get relocations suitable for KLD per-CPU allocation.

`struct pcpu` records core per-CPU runtime state: current/idle/fp/dead threads, current PCB, scheduler state, context-switch timing, CPU id, all-CPU linkage, spinlock list, CPU state ticks, device handle, netisr state, VFS free vnode hint, memory domain, rmlock queue, dynamic per-CPU base, early counter, zpcpu offset, and machine-dependent fields kept last for offset stability.

The zpcpu helpers provide access to UMA per-CPU allocations with protected set/add/sub operations, CPU-specific offset translation hooks, and replacement helpers. The header also declares CPU/per-CPU initialization, lookup, allocation, copy, free, and debug display hooks. Filesystem relevance includes per-CPU counters, VFS free vnode accounting, UMA per-CPU allocation patterns, and synchronization-sensitive kernel performance.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pcpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pctrie.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pctrie.h

This header defines a path-compressed trie interface used for keyed pointer/value indexing in the kernel. It includes private trie and SMR definitions, provides an iterator structure with reset/init helpers, and under `_KERNEL` declares generic trie functions plus macro generators for typed wrappers.

`PCTRIE_DEFINE` creates a type-safe family of inline functions for a containing structure whose embedded `uint64_t` field is the trie key/value anchor. It asserts field size and flag-bit alignment, converts between embedded value pointers and containing structures, and generates insert, find-or-insert, insert-with-lookup-LE, lookup, range lookup, LE/GE lookup, iterator lookup/stride/next/prev/value/jump/step, replace, remove, remove-lookup, reclaim, and reclaim-with-callback helpers. Allocation and free functions for internal nodes are supplied by the instantiating caller.

`PCTRIE_DEFINE_SMR` extends the generated API with unlocked lookup/range lookup under a provided SMR domain. Low-level functions implement insert lookup, node insertion, lookups, range scans, iterator movement, reclamation, removal, replacement, node sizing, and zone initialization.

The trie encodes leaves by setting low pointer bit `PCTRIE_ISLEAF`, with `PCTRIE_NULL` representing an empty leaf. Width is 4 on LP64 and 3 on 32-bit, chosen to keep child arrays cache-line friendly while relying on path compression. Filesystem/VM relevance is high: this kind of keyed sparse index is used for page, object, or other kernel maps where efficient ordered lookup and range scans matter.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pctrie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/physmem.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/physmem.h

This header declares early physical memory configuration helpers. It allows machine/platform code to add hardware RAM regions, add exclusion regions, query available/all physical memory tables, initialize global `dump_avail` and `phys_avail`, print tables, and test whether a physical range is excluded.

Exclusion flags distinguish no-dump and no-alloc regions. The comments explain the intended boot flow: collect hardware regions and exclusions in any order, then call `physmem_init_kernel_globals()` once early initialization is complete so the generated arrays communicate usable RAM to the rest of the kernel.

When `FDT` is enabled, inline helpers convert arrays of `struct mem_region` into hardware or excluded regions. Filesystem relevance is indirect but foundational: VM and buffer cache behavior depend on correct physical memory availability, and crash dump exclusion affects postmortem filesystem/storage diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/physmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pidctrl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pidctrl.h

This header defines a simple integer proportional-integral-derivative controller for kernel daemons and resource regulation. The comments describe its goal: replace threshold-based high/low water behavior that creates bursty sawtooth activity with smoother adaptive control.

`struct pidctrl` stores current/old error, integral, derivative, last input/output, last sampling tick, plus tunable configuration: setpoint, interval, integral bound, and divisors for proportional/integral/derivative gains. Gains are represented as inverse integer divisors to avoid floating point. Defaults are provided for proportional, integral, derivative, and bound factors.

The API includes initialization, sysctl initialization, a classic controller that can produce negative output for bidirectional control loops, and a daemon-oriented controller whose output is positive work required to reduce an input variable. The daemon variant supports repeated calls in overload cases but warns that stable control depends on interval behavior and tuning.

Filesystem relevance is workload regulation: reclaimers, flushers, or maintenance daemons can use this style of controller to avoid latency spikes caused by abrupt threshold-driven work.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pidctrl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pipe.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pipe.h

This header defines kernel pipe buffer and endpoint structures. It sets default pipe sizes (`PIPE_SIZE`, `BIG_PIPE_SIZE`, `SMALL_PIPE_SIZE`), direct-write threshold (`PIPE_MINDIRECT`), and maximum page slots for direct mappings (`PIPENPAGES`).

`struct pipebuf` tracks circular buffer count, input/output offsets, buffer size, and KVA pointer. `struct pipemapping` supports direct transfers by recording count, position, number of wired pages, and page array. Pipe state bits cover async I/O, reader/writer waiters, rundown, select activity, EOF, pointer/data exclusive access, direct write active, and direct mode eligibility. `PIPE_TYPE_NAMED` marks named pipes.

`struct pipe` is one endpoint in a bidirectional pair. It contains the buffer, direct mapping state, select info, timestamps, async signal info, peer/container pointers, state/type/presence fields, waiter/busy counters, named-pipe writer generation, and fake inode number. `struct pipepair` contains read/write endpoints, mutex, MAC label pointer, and owner credential for accounting. Macros expose pipe mutex locking/assertions.

Kernel prototypes cover destruction, named pipe construction, and select wakeup. Filesystem relevance is direct for FIFO/named-pipe behavior and VFS file operations: pipe endpoints are represented as file objects, expose stat-like metadata, and coordinate readiness with select/poll/kqueue paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pmc.h

This is the main FreeBSD hwpmc ABI and kernel-private state header. It includes event definitions, process/counter/machine-dependent PMC headers, and, in kernel builds, epoch and CK queue support. It defines module name, name/class limits, ABI version `0x0A010000`, and a CPU model string buffer.

Large macro tables enumerate supported CPU types and PMC classes, preserving sparse numeric assignments for ABI stability. Other enums define PMC hardware/software states, operating modes (system/thread and sampling/counting combinations), row dispositions, capabilities, and event numbers generated from `pmc_events.h`. Helper macros test mode categories and encode/decode `pmc_id_t` fields for CPU, mode, class, and row index.

The user/kernel syscall interface is described by `enum pmc_ops` and operation structs for configure/flush/close log, CPU info, driver stats, PMC info, admin, allocate, attach/detach, get MSR, release, read/write, set count, start/stop, write log, dynamic event info, and capability lookup. Allocation carries requested caps, CPU, class, event, flags, mode, initial/sample count, returned id, and MD extension union.

Kernel-only sections define driver sizing constants, locking annotations, syscall argument wrapper, human-readable PMC descriptors, target/process/thread/owner tracking, hardware PMC rows, sample buffers, multipart payloads, per-CPU PMC state, CPU binding state, class-dependent method vectors, and machine-dependent dispatch vectors. Debug builds wire a detailed KTR-based tracing macro family by subsystem/minor category. The header declares MD initialization/finalization, interrupt processing, callchain capture, CPU binding, class allocation, and timestamp helpers.

Filesystem relevance is mostly observability: hwpmc can profile kernel and user execution, including VFS/filesystem hot paths, block I/O stacks, and cache behavior. Its ABI stability and binary log compatibility are important for profiling tools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmckern.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pmckern.h

This header defines the interface used by the base kernel to call into the hwpmc module. It includes core kernel headers, `sys/pmc.h`, and machine CPU functions.

It assigns hook function numbers for process exec, context switch in/out, sample processing, mmap/munmap, user callchain capture, soft sampling, thread create/exit/userret, and thread/process logging. Small structs describe exec address changes, map-in/map-out events, and software PMC samples. `ring_type_t` distinguishes hardware, software, and userret sample rings.

The soft-PMC macros define and register dynamic software events at SYSINIT/SYSUNINIT time. `PMC_SOFT_CALL` and `PMC_SOFT_CALL_TF` conditionally invoke the hwpmc hook when a software event is running, disabling interrupts around trapframe setup/capture where required.

Global hook pointers (`pmc_hook`, `pmc_intr`), `pmc_sx`, per-CPU sampled flags, system-wide sampling count, kernel version, per-CPU trapframes, and per-domain log buffer headers are declared. Hook invocation macros support epoch-protected calls, exclusive-lock calls, and lock-free calls for context switch/clock paths. Helper macros detect active hooks, PMC-using processes, pending samples/callchains, active system sampling, and CPU sample availability. CPU availability and soft-event registration/acquire/release functions are declared.

Filesystem relevance is profiling integration: this is how exec, mmap, context switch, and sampling paths notify hwpmc so profiler output can be correlated with processes, mappings, and kernel activity.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmckern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmclog.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/pmclog.h

This header defines the binary log record ABI produced by hwpmc. It includes `sys/pmc.h`, enumerates log record types, declares packed record layouts, provides header bitfield helpers, and exposes kernel log-processing prototypes.

`enum pmclog_type` preserves versioned ABI additions: V1 records for close/drop/init/allocate/attach/detach/context switch/exec/exit/fork/sys exit/user data, V2 map-in/map-out/callchain replacements, V3 dynamic allocation, and V6 thread/process creation records. Each record begins with a common header containing a 32-bit packed magic/type/length header, spare field, and 64-bit timestamp counter.

Packed structs define payloads for callchains, initialization, mappings, PMC allocation, attach/detach, process context switch, process create/exec/exit/fork, syscall exit, thread create/exit, user data, and dynamic allocation. Callchain CPU/mode flags and multipart callchain payload tags are defined. `union pmclog_entry` sizes scratch areas for all record variants.

Header macros extract length, type, and magic from a record header and validate the `0xEE` magic. Kernel prototypes configure/deconfigure/flush/close logs and enqueue/process all record types. Filesystem relevance is observability and tooling: profiler logs include executable mappings and paths, which are crucial for attributing sampled time to filesystem and storage code paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/pmclog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/poll.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/poll.h

This header provides the FreeBSD-compatible `poll.h` ABI. It defines `nfds_t`, `struct pollfd`, requestable event bits, always-reported event bits, BSD extensions, and userland function prototypes.

Requestable events include readable, priority/OOB readable, writable, normal read/write aliases, and band events. BSD-visible extensions add `POLLINIGNEOF` and `POLLRDHUP`. Always-returned events are error, hangup, and invalid descriptor. `POLLSTANDARD` groups the traditional set, and `INFTIM` requests an infinite wait.

For userland, `poll()` is declared. When POSIX.1-2024 visibility is enabled, `sigset_t`, `timespec`, and `ppoll()` are exposed. Fortify support includes `<ssp/poll.h>` when enabled. Filesystem relevance is readiness notification: file descriptors for regular files, pipes, sockets, devices, and filesystem-backed special files report readiness through this ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/posix4.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/posix4.h

This header supports POSIX.1b/P1003.1b kernel facilities. It includes system parameter, ioctl, malloc, and scheduler headers, then declares module-stub support and configuration helpers.

`SYSCALL_NOT_PRESENT_GEN` generates syscall stubs that call `syscall_not_present()` for optional loadable functionality. `M_P31B` declares a malloc type. `p31b_proc()` resolves a target process by PID, and `p31b_setcfg`, `getcfg`, `iscfg`, and `unsetcfg` manage feature configuration flags.

When `_KPOSIX_PRIORITY_SCHEDULING` is enabled, the header defines scheduler operation IDs, a read/write access vector macro, an opaque `struct ksched`, and attach/detach plus set/get/yield/priority/round-robin interval methods. Filesystem relevance is low but systemic: optional POSIX kernel facilities and scheduling policy affect process behavior around I/O workloads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/posix4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/power.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/power.h

This header defines user and kernel power-management interfaces. User-visible content includes `enum power_transition` for standby, suspend, and hibernate requests, plus `PIOTRANSITION`, an ioctl accepting a `uint32_t` transition selector.

Kernel-only content defines power management provider types, command constants, and `enum power_stype`, which maps high-level transitions to concrete sleep methods such as awake, standby, firmware suspend, suspend-to-idle, firmware hibernate, and poweroff. It provides fixed-length names, a static name table, global sysctl-selected sleep type variables, and conversion helpers between names and sleep types.

Power management providers register with `power_pm_register()` by type, callback, argument, and supported sleep-type set. The header also declares provider type lookup, suspend entry, performance/economy power profile state accessors, and a `power_profile_change` eventhandler. Filesystem relevance is suspend/resume coordination: filesystems and storage stacks must tolerate power state transitions, and userland initiates them through this ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/priority.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/priority.h

This header defines FreeBSD scheduler priority classes and numeric ranges. Classes include interrupt thread, realtime, timeshare, and idle. `PRI_FIFO` overlays a FIFO bit on realtime priority, and helper macros extract the base class, test realtime, and decide whether round-robin behavior is needed.

The priority number space is 0 to 255, where lower values are higher priority. Ranges are reserved for interrupt threads, realtime user threads, kernel threads, timeshare user threads, and idle user threads. Constants define representative interrupt priorities, kernel sleep priorities (`PSWP`, `PVM`, `PINOD`, `PRIBIO`, `PVFS`, `PZERO`, etc.), and user/idle range boundaries. Kernel-only `PRI_USER` and `PRI_UNCHANGED` are arguments to yield behavior.

`struct priority` stores scheduling class, normal priority level, native priority before propagation, and user priority derived from CPU/nice accounting. Filesystem relevance is practical: I/O wait priorities, VFS sleep priority (`PVFS`), inode priority (`PINOD`), and buffer I/O priority (`PRIBIO`) influence scheduling latency in filesystem paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/priority.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/priv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/priv.h

This header defines FreeBSD's named privilege numbers and kernel privilege-check API. The comments emphasize that numeric assignments are part of the loadable kernel module ABI and must not be renumbered casually; new privileges also need jail-policy consideration.

Privileges are grouped loosely by subsystem. Early values cover base system capabilities such as accounting, resource-limit bypasses, ktrace, dump configuration, reboot, swap, message buffer, low-level I/O, drivers, and time setting. Later groups cover audit, credentials, debugging, DTrace, firmware, jail management, kernel environment, KLD load/unload, MAC policies, process controls, IPC, POSIX message queues, performance counters, scheduling, semaphores, signals, sysctl, tty, UFS, ZFS, NFS, VFS, VM, devfs, random reseed, network stacks and protocols, VM86, pipe buffer reserve, module-reserved slots, DDB, cpuctl, CAPI, OpenAFS, resource controls, memory devices, KDB, veriexec, and vmm.

VFS/filesystem-specific privileges are numerous: read/write/admin/exec/lookup DAC overrides, block reserve, chflags on devices, chown, chroot/fchroot, retain sugid bits, quota bypass and management, system extended attributes, file-handle operations, generation numbers, hardlink policy bypass, mknod variants, mount/unmount and mount flags, setgid, sticky file, system flags, MAC stat override, and read-dirfd override. UFS, ZFS, and NFS also have subsystem-specific privileges.

`_PRIV_LOWEST`, `_PRIV_HIGHEST`, and `PRIV_VALID()` define an approximate valid range. Kernel APIs are `priv_check()`, `priv_check_cred()`, and specialized credential checks for VFS lookup, VFS lookup without MAC, and VFS generation. This header is central to authorization decisions across VFS, storage, networking, process control, and kernel modules.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/prng.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/prng.h

This small public-domain header wires in the PCG pseudo-random generator variants and declares kernel PRNG helpers. It sets `PCG_USE_INLINE_ASM` before including `<contrib/pcg-c/include/pcg_variants.h>`.

Under `_KERNEL`, it declares `prng32()`, `prng32_bounded()`, `prng64()`, and `prng64_bounded()`. These provide fast non-cryptographic pseudo-random values and bounded variants for kernel consumers.

Filesystem relevance is incidental: such PRNG helpers may be used by kernel subsystems for randomized choices that do not require cryptographic randomness, but this header itself contains no filesystem-specific policy.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/prng.h -->