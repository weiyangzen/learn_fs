# Group Research: group_407_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_unionfs_union_vnops_c__a349f07efb32

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vnops.c

## Summary
Implements the FreeBSD unionfs vnode operation vector. It routes VOPs to an upper or lower vnode, creates upper-layer shadow objects on demand, handles whiteouts, manages copy-up for writes and metadata mutations, and supplies unionfs-specific locking/reclaim behavior.

## Main Responsibilities
- Implements lookup, create, remove, rename, mkdir/rmdir, symlink, link, open/close, read/write, readdir, ACL, extattr, MAC label, vnode locking, strategy, writecount, text, and UNIX-domain socket VOPs.
- Presents upper-layer contents when present, otherwise falls back to lower-layer contents.
- Performs copy-up for lower regular files before write-like operations, locks, ACL/label/extattr mutation, and some rename/link paths.
- Creates shadow directories in the upper layer when traversing or renaming lower-only directories.
- Creates whiteouts when deleting or renaming over lower-layer entries, depending on mount whiteout mode and lower vnode presence.

## Key APIs and Operations
- `unionfs_lookup()` is the central name resolution path. It looks up lower first, then upper, handles dot/dotdot, whiteout and opaque directory behavior, shadow directory creation, unionfs vnode creation, cache insertion, and serialized in-progress directory lookups.
- `unionfs_open()` and `unionfs_close()` track per-thread node status and lower/upper open counts, copy lower regular files before write opens, open lower directories for merged readdir, and keep `vp->v_object` aligned with the active backing vnode.
- `unionfs_readdir()` reads upper entries first, then lower entries unless the upper directory is opaque. It tracks readdir state in `unionfs_node_status` and merges cookies when both layers are read.
- `unionfs_rename()` maps unionfs source/target vnodes to upper backing vnodes, copy-ups lower-only sources, creates shadow dirs or copies symlinks/files, rejects unsupported flags and cross-device operations, and returns `ERELOOKUP` when dropped locks require lookup replay.
- `unionfs_lock()` locks the active backing vnode rather than the unionfs vnode itself, restarting if a lower lock becomes invalid due to concurrent copy-up or reclaim.
- `unionfs_vnodeops` registers the operation vector with `VFS_VOP_VECTOR_REGISTER()`.

## Important Behavior
Writes target the upper vnode once one exists. If a write-like operation targets a lower regular file, unionfs generally calls `unionfs_copyfile()` first, then uses the new upper vnode.

Directory behavior is layered. Lookups may synthesize a unionfs vnode from both upper and lower vnodes, may suppress lower entries under whiteouts or opaque upper directories, and may create an upper shadow directory for lower directories when the mount is writable.

Delete operations act on upper vnodes when present and create whiteouts when lower entries must be hidden. Lower-only deletes create a whiteout instead of modifying the lower filesystem.

Several helper paths deliberately exchange locks instead of holding upper and lower vnode locks together. `unionfs_lock_lvp()` and `unionfs_unlock_lvp()` drop the unionfs/default lock while operating on a lower vnode to reduce cross-filesystem lock-order problems.

## State and Lifetime
Per-vnode state lives in `struct unionfs_node`, reached through `VTOUNIONFS()`. Per-thread open/readdir state lives in `struct unionfs_node_status`. Reclaim removes unionfs node state with `unionfs_noderem()`, inactive clears `v_object` and recycles the vnode.

The code relies on vnode references, holds, `VI_LOCK`, and backing vnode locks to survive lock drops during copy-up, lower locking, rename replay, and unmount/reclaim races.

## Risks
This file is lock-order sensitive. Many paths intentionally drop and reacquire vnode locks, return `ERELOOKUP`, or restart lock acquisition to avoid stale upper/lower backing choices. Copy-up and whiteout behavior is also security-sensitive because it changes whether later VOPs affect upper storage, lower storage, or only name visibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/Make.tags.inc -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/Make.tags.inc

## Summary
Defines common file and directory lists included by architecture-specific kernel `make tags` targets.

## Main Contents
- `SYS ?= ${.CURDIR}/..` defaults the kernel source root.
- `COMM` lists common source globs for ctags, including `sys/vnode.h`, major `dev`, `fs`, `geom`, `kern`, networking, UFS, VM, and `sys` headers/sources.
- `COMMDIR1` and `COMMDIR2` list directories used by tag generation.

## Important Behavior
The file intentionally places `/sys/sys` include files at the end of `COMM` so subroutine definitions win over same-name struct tags, such as `vmmeter`.

## Risks
This is build tooling, not runtime code. The main maintenance risk is stale directory lists causing incomplete kernel tags for developers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/Make.tags.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/Makefile

## Summary
Small makefile wrapper for generating kernel syscall tables and related headers.

## Main Contents
Defines `GENERATED` outputs: `init_sysent.c`, `syscalls.c`, `systrace_args.c`, and generated syscall headers/make fragments under `${SYSDIR}/sys`.

## Important Behavior
Includes `../conf/sysent.mk`, which contains the actual syscall generation rules.

## Risks
This file is declarative. Incorrect `GENERATED` entries would affect cleanup or dependency tracking for syscall-generation artifacts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/bus_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/bus_if.m

## Summary
Defines the FreeBSD KObj `bus` interface: methods implemented by bus drivers that own child devices, manage bus-specific instance variables, allocate resources, configure interrupts, and coordinate child lifecycle.

## Main Responsibilities
- Specifies child enumeration, probing notifications, attach/detach notifications, and driver-added callbacks.
- Defines resource allocation, activation, mapping, unmapping, adjustment, translation, release, and resource-list/rman access.
- Defines interrupt setup, teardown, suspend/resume, binding, trigger/polarity configuration, remapping, and descriptive metadata.
- Defines child metadata callbacks for PnP info, location, device path, properties, DMA tags, bus tags, VM domain, CPU sets, and reset preparation/post/reset.

## Key Methods
Important methods include `print_child`, `probe_nomatch`, `read_ivar`, `write_ivar`, `child_deleted`, `child_detached`, `driver_added`, `add_child`, `rescan`, `alloc_resource`, `activate_resource`, `map_resource`, `unmap_resource`, `deactivate_resource`, `adjust_resource`, `translate_resource`, `release_resource`, `setup_intr`, `teardown_intr`, `set_resource`, `get_resource`, `delete_resource`, `get_resource_list`, `get_rman`, `child_present`, `child_pnpinfo`, `child_location`, `bind_intr`, `config_intr`, `describe_intr`, `hinted_child`, `get_dma_tag`, `get_bus_tag`, `hint_device_unit`, `new_pass`, `remap_intr`, `suspend_child`, `resume_child`, `get_domain`, `get_cpus`, `reset_prepare`, `reset_post`, `reset_child`, `get_property`, and `get_device_path`.

## Defaults
The file supplies default implementations for unsupported resource allocation, interrupt remapping fallback, child add panic, reset hooks, rman/resource-list lookup, and many methods through `bus_generic_*`.

## Integration
The `.m` file is consumed by FreeBSD's interface generator to create typed dispatch wrappers/macros for bus methods. It is part of the kernel device model rather than a concrete bus implementation.

## Risks
Method contracts are broad and many drivers depend on their exact semantics. Defaults can hide missing implementation for optional methods, while required methods such as resource activation or interrupt setup must be supplied correctly by real bus drivers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/bus_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/clock_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/clock_if.m

## Summary
Defines the KObj `clock` interface for device-independent clock drivers.

## Key Methods
- `gettime(device_t dev, struct timespec *ts)` reads the clock.
- `settime(device_t dev, struct timespec *ts)` sets the clock.

## Important Behavior
The comments specify that `EINVAL` from `gettime` means the clock has an illegal setting.

## Risks
This is an interface definition. Runtime behavior depends on driver implementations honoring the timespec contract and using `EINVAL` consistently for invalid hardware clock state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/clock_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/coredump_vnode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/coredump_vnode.c

## Summary
Implements the traditional vnode-backed coredumper. It expands `kern.corefile`, opens and validates the target file, serializes writers, invokes the process ABI's coredump routine through a `coredump_writer`, and optionally sends devctl notifications.

## Main Responsibilities
- Registers `vnode_coredumper` at `SI_SUB_EXEC`.
- Exposes sysctls/tunables for core naming, indexed core rotation, capability-mode core dumps, NODUMP flagging, and devctl notifications.
- Implements vnode writer callbacks `core_vn_write()` and `core_vn_extend()`.
- Expands core filename templates using process name, pid, uid, signal, hostname, and optional `%I` index.
- Creates, rotates, truncates, locks, writes, and closes core files.

## Key APIs
- `corefile_open()` expands `kern.corefile`, appends compression suffixes, and opens the target vnode.
- `corefile_open_last()` implements `%I` rotation by finding an unused core filename or the oldest existing one.
- `coredump_vnode()` is the registered coredumper handler.
- `core_vn_write()` writes core payload through `vn_rdwr_inchunks()` with direct and range-locked I/O.
- `core_vn_extend()` extends/truncates the vnode under a write transaction.

## Important Behavior
Core files are created with `O_CREAT | FWRITE | O_NOFOLLOW`; setuid/setgid processes use `O_EXCL` in the non-indexed path. The target must be a regular file, have one link, not be a system vnode, and be owned by the effective user.

Before writing, the code takes a full-file vnode range lock and attempts an advisory write lock. It truncates the file to zero, optionally sets `UF_NODUMP`, marks `ACORE`, and then calls `p->p_sysent->sv_coredump()`.

When `kern.coredump_devctl` is enabled and writing succeeds, the code emits a quoted devctl event containing executable path, core path, jail id, pid, parent pid, and signal.

## State and Synchronization
`corefilename` is protected by `allproc_lock`. Core writing uses vnode locks, vnode range locks, optional advisory locks, and mount write transactions for extension/truncation.

## Risks
The file-name formatter is security-sensitive because it expands kernel-controlled paths into vnode opens. The code avoids following symlinks and validates ownership/link count/type, but changes to this area can easily weaken corefile safety.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/coredump_vnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/cpufreq_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/cpufreq_if.m

## Summary
Defines the KObj `cpufreq` interface for CPU frequency policy and driver backends.

## Key Methods
- Policy-level methods: `set`, `get`, and `levels` operate on `struct cf_level`.
- Driver-level methods: `drv_set`, `drv_get`, `drv_settings`, and `drv_type` operate on `struct cf_setting` or driver type.

## Important Behavior
The interface separates aggregate CPU frequency levels from individual driver settings, allowing a cpufreq core to combine multiple providers.

## Risks
This file is an interface contract. Driver implementations must agree on units, priorities, level counts, and type semantics declared elsewhere in the cpufreq subsystem.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/cpufreq_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/device_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/device_if.m

## Summary
Defines the KObj `device` interface implemented by all FreeBSD device drivers. It covers driver matching, child identification, attach/detach, shutdown, suspend/resume, quiesce, and handler registration.

## Key Methods
- `probe(device_t dev)` participates in driver election. Return `0` wins immediately, negative values are ranked matches, `ENXIO` means no match, and positive errno values signal errors.
- `identify(driver_t *driver, device_t parent)` lets drivers enumerate children not otherwise discovered.
- `attach(device_t dev)` initializes hardware and allocates resources after a successful probe.
- `detach(device_t dev)` tears down a driver instance.
- `shutdown`, `suspend`, `resume`, `quiesce`, and `register` handle system-wide lifecycle and registration events.

## Defaults and Instrumentation
Default no-op implementations exist for shutdown, suspend, resume, quiesce, and register. Probe and attach methods include `TSENTER2`/`TSEXIT2` timestamp instrumentation around `device_get_name(dev)`.

## Integration
Generated wrappers from this `.m` file are used throughout kernel autoconfiguration and driver lifecycle code. Documentation comments describe normal `KOBJMETHOD(device_*, ...)` usage.

## Risks
Probe return semantics are subtle and affect which driver attaches. Drivers must release probe-time resources before returning because a successful probe does not guarantee attachment unless it returns the special immediate-match value.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/device_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/firmw.S -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/firmw.S

## Summary
Assembly helper for embedding a firmware binary into a kernel object.

## Main Contents
- Defines `FIRMW_START(S)` and `FIRMW_END(S)` symbol macros.
- Places contents of `FIRMW_FILE` into `.rodata` using `.incbin`.
- Exports `_binary_<symbol>_start` and `_binary_<symbol>_end`-style object symbols.
- Emits an AArch64 GNU property note when building for `__aarch64__`.

## Important Behavior
The build system supplies `FIRMW_SYMBOL` and `FIRMW_FILE`. The resulting object exposes firmware start/end addresses for C code to consume.

## Risks
Incorrect macro definitions or file paths would create missing or misnamed firmware symbols. The data is read-only and has no runtime logic beyond symbol layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/firmw.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genassym.sh -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/genassym.sh

## Summary
Shell script that converts special `nm` output from an object file into C preprocessor `#define` constants for assembly.

## Main Behavior
The script accepts `[-o outfile] objfile`. Its `awk` program reads common symbols ending in `sign`, `w0`, `w1`, `w2`, and `w3`, reconstructs a hex value from the four words, applies a sign marker, strips leading zeroes, and emits `#define <symbol> <value>`.

## Inputs and Outputs
Uses `${NM:-nm}`, `${NMFLAGS}`, and `${AWK:-awk}`. With `-o`, output is redirected through file descriptor 3 to the chosen outfile; otherwise it writes to stdout.

## Risks
The comment notes imperfect representation for values such as `INT_MIN` because a negative hex literal can have the wrong C type. The script depends on the exact symbol naming convention produced by the assym-generation C code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genassym.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genoffset.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/genoffset.c

## Summary
Small C source used to emit structure field offset symbols for kernel assembly/header generation.

## Main Contents
Defines `GENOFFSET` unless `OFFSET_TEST` is set, includes kernel headers, and invokes `OFFSYM()` for selected `struct thread` fields: `td_priority`, `td_critnest`, `td_pinned`, and `td_owepreempt`.

## Integration
The object produced from this file is consumed by `genoffset.sh`, which reads `__assym_offset__` symbols and generates a lightweight C structure/offset assertion header.

## Risks
This file must stay synchronized with low-level code that needs thread-field offsets. Wrong field type declarations in `OFFSYM()` would make generated offset validation misleading.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genoffset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genoffset.sh -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/genoffset.sh

## Summary
Shell script that turns `__assym_offset__` symbols from an object file into a generated C include containing lite structure layouts and static offset assertions.

## Main Behavior
The script accepts `[-o outfile] objfile`. It emits include guards, then, when not compiling with `GENOFFSET` and not in an untied KLD module, reads decimal `nm` output for `__assym_offset__` symbols, sorts by structure and offset, and generates `struct <name>_lite` definitions with padding arrays and target fields.

## Validation
For each emitted field it appends `_Static_assert(__builtin_offsetof(struct s_lite, f) == o, ...)`, then undefines the helper macro. This lets generated structure shims validate expected offsets at compile time.

## Inputs and Outputs
Uses `${NM:-nm}` with `${NMFLAGS}` and standard shell tools `grep`, `sed`, and `sort`. With `-o`, output goes to the selected file; otherwise stdout is used.

## Risks
The script depends on exact symbol naming and sort layout after replacing double underscores. A malformed or unexpected symbol name can corrupt generated structure syntax.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/genoffset.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_aout.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_aout.c

## Summary
Implements the legacy FreeBSD a.out image activator for i386 or amd64 running 32-bit a.out binaries.

## Main Responsibilities
- Defines the a.out `sysentvec` for i386 or amd64 compatibility.
- Provides stack fixup that writes `argc` below the stack base.
- Validates a.out headers, machine IDs, magic variants, sizes, entry address, and resource limits.
- Creates a new VM space, maps text/data/bss, maps the stack, sets process ABI state, and registers an execsw entry.

## Key APIs
- `exec_aout_imgact()` is the image activator.
- `aout_fixup()` writes the initial `argc` word.
- `aout_sysent()` initializes the amd64 32-bit signal-code size from embedded VDSO symbols.
- `EXEC_SET(aout, aout_execsw)` registers the activator.

## Important Behavior
The loader recognizes FreeBSD, BSDI, and NetBSD-compatible a.out markings. It handles `ZMAGIC` and `QMAGIC`, including network-byte-order compatibility. For BSD/OS-style `MID_ZERO` QMAGIC binaries, it passes `PS_STRINGS`.

The loader rejects invalid entry points, non-page-rounded text/data sizes, truncated files, and text/data/bss sizes above process/system limits. It unlocks the executable vnode around `exec_new_vmspace()` to avoid deadlocks, then maps text executable/readable and data writable with copy-on-write.

## Risks
This is compatibility code for old executable formats. It has architecture-specific assumptions, 32-bit address bounds on amd64, and manual VM layout logic. Mistakes could map malformed binaries or create unsafe legacy ABI process state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_aout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_binmisc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_binmisc.c

## Summary
Implements the miscellaneous binary image activator. It lets sysctl-managed rules match executable header bytes and rewrite execution to a configured user-level interpreter.

## Main Responsibilities
- Maintains a locked SLIST of interpreter rules.
- Supports sysctl operations to add, remove, enable, disable, look up, and list rules under `kern.binmisc`.
- Matches image headers using magic bytes, optional masks, offsets, and enabled flags.
- Rewrites `argv` to prepend interpreter arguments, including `##` escaping and `#a` old-argv0 substitution.
- Optionally pre-opens interpreter vnodes for rules with `IBF_PRE_OPEN`.

## Key APIs
- `imgact_binmisc_add_entry()`, `remove_entry()`, `enable_entry()`, `disable_entry()`, `lookup_entry()`, and `get_all_entries()`.
- `sysctl_kern_binmisc()` dispatches user sysctl commands using `ximgact_binmisc_entry_t`.
- `imgact_binmisc_find_interpreter()` matches the current image header.
- `imgact_binmisc_exec()` performs image activation by rewriting args and setting `interpreter_name` or `interpreter_vp`.
- `SYSINIT`/`SYSUNINIT` initialize and destroy the interpreter-list lock and entries.

## Important Behavior
Interpreter strings are normalized so whitespace separates arguments. Spaces become NUL separators when copied into `begin_argv`. `#a` expands to the original executable name or `/dev/fd/<fd>` for `fexecve`.

The activator rejects nested binmisc interpretation by checking `IMGACT_BINMISC`. Rule addition validates magic sizes, offsets, ASCII names/interpreters, version, flags, entry count, duplicate names, and valid `#` macros.

## State and Synchronization
Rules are allocated from `M_BINMISC` and protected by an `sx` lock. The add path preallocates entries before taking the write lock to avoid lock-order problems with optional interpreter pre-open lookup.

## Risks
This code rewrites exec arguments in-kernel and can hold pre-opened vnodes. Incorrect offset calculations for interpreter strings or macro expansion could corrupt argv layout. Rule matching also exposes execution policy through mutable sysctls, so validation and locking are important.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_binmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_elf.c

## Summary
Implements FreeBSD ELF image activation and ELF core dump generation for the selected `__ELF_WORD_SIZE`. It handles ELF header validation, brand detection, interpreter loading, VM segment mapping, ASLR/W^X policy, aux vector construction, process ABI setup, and ELF-format core notes/segments.

## Main Responsibilities
- Maintains ELF brand registration and selection for FreeBSD, GNU/kFreeBSD, fallback brands, interpreter paths, OSABI fields, legacy branding, and ABI notes.
- Validates ELF headers and program headers, including class/data/version/machine, program-header count, segment alignment, PT_INTERP, PT_GNU_STACK, PT_PHDR, and PT_NOTE constraints.
- Maps executable and interpreter PT_LOAD sections into a fresh process VM space, handling partial pages, non-page-aligned file offsets, bss, copy-on-write, no-core mappings, executable text references, and resource limits.
- Implements ASLR and PIE base selection, stack/shared-page randomization flags, `MAP_WXORX`, and feature-control notes.
- Builds ELF auxargs and stack fixup data.
- Generates ELF core dumps with PT_NOTE, PT_LOAD entries, register notes, procstat notes, and optional compression.

## Key Exec APIs
- `__elfN(check_header)()` validates basic ELF identity and ensures at least one brand exists for the machine.
- `__elfN(get_brandinfo)()` selects ABI brand by note, OSABI, legacy header brand, header callback, interpreter path, or fallback brand.
- `__elfN(load_section)()` maps one PT_LOAD segment, including initialized data and zero-fill/bss.
- `__elfN(load_sections)()` maps all loadable segments and reports the first base address.
- `__elfN(load_file)()` loads an interpreter/shared object by pathname.
- `__CONCAT(exec_, __elfN(imgact))()` is the main ELF image activator.
- `__elfN(freebsd_copyout_auxargs)()` emits aux vector entries.
- `__elfN(freebsd_fixup)()` writes `argc` on the user stack.
- `EXEC_SET(ELF_ABI_ID, __elfN(execsw))` registers the activator.

## Key Core-Dump APIs
- `__elfN(coredump)()` sizes segments/notes, checks core limits/accounting, sets up compression, writes headers/notes, and outputs dumpable VM segments.
- `each_dumpable_segment()` filters VM map entries for core dumping.
- `__elfN(prepare_notes)()` builds the note list.
- `__elfN(puthdr)()` emits ELF and program headers, including extended numbering when needed.
- `__elfN(register_note)()`, `register_regset_note()`, `populate_note()`, and `putnote()` manage note sizing and serialization.
- Note emitters cover `PRPSINFO`, `PRSTATUS`, FP registers, thread metadata, ptrace LWP info, procstat proc/files/vmmap/groups/umask/rlimit/osrel/psstrings/auxv/kqueues.

## Important Exec Behavior
The activator accepts `ET_EXEC` and supported `ET_DYN` binaries. It rejects too many program headers, wraparound in program-header ranges, invalid segment alignment, multiple interpreters, invalid stack permissions, unknown brands, and unsupported executable shared objects.

For setid binaries it clears user ASLR and W^X preference flags. ASLR decisions combine ABI support, sysctls, process flags, PIE state, and FreeBSD feature-control notes. If ASLR is enabled, it randomizes PIE base, `anon_loc`, stack, and optionally shared-page placement.

The code unlocks the executable vnode around `exec_new_vmspace()` to avoid vnode/VM deadlocks while relying on executable text references to prevent modification. It relocks before loading sections.

## Important Core-Dump Behavior
Core dumping sizes all dumpable segments first, computes header/note size, charges RACCT core usage, rejects dumps above the limit, optionally compresses, and then writes PT_NOTE plus page-aligned PT_LOAD segment contents.

Dumpable segment filtering excludes inaccessible mappings unless `SVC_ALL` is requested, honors `MAP_ENTRY_NOCOREDUMP`, ignores submaps and fictitious backing objects, and supports a legacy mode that dumps only read/write mappings.

## State and Tunables
Important sysctls/tunables include `fallback_brand`, `debug.elf*.legacy_coredump`, `nxstack`, `vdso`, `read_exec` for 32-bit x86, `pie_base`, ASLR enablement knobs, `sigfastblock`, `allow_wx`, and program-header count limit `phnums`.

## Risks
This file is security-critical. It parses untrusted executable headers, maps user VM, applies ABI policy, and emits core files. High-risk areas include integer overflow checks, vnode lock dropping/relocking, text-reference accounting, feature-control note parsing, W^X/ASLR policy precedence, and note-size prediction for coredumps.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf32.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_elf32.c

## Summary
Build wrapper that instantiates `kern/imgact_elf.c` for 32-bit ELF.

## Main Contents
Defines `__ELF_WORD_SIZE 32` and includes `<kern/imgact_elf.c>`.

## Important Behavior
All ELF loader/core-dump logic comes from the shared `imgact_elf.c` template, with macros resolving to 32-bit ELF types and symbol names.

## Risks
This file has no independent runtime logic. Its risk is compile-time configuration: it must be included only in builds that need the 32-bit ELF image activator.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf64.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_elf64.c

## Summary
Build wrapper that instantiates `kern/imgact_elf.c` for 64-bit ELF.

## Main Contents
Defines `__ELF_WORD_SIZE 64` and includes `<kern/imgact_elf.c>`.

## Important Behavior
All ELF loader/core-dump logic comes from the shared `imgact_elf.c` template, with macros resolving to 64-bit ELF types and symbol names.

## Risks
This file has no independent runtime logic. Its risk is compile-time configuration: it must be included only in builds that need the 64-bit ELF image activator.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_elf64.c -->