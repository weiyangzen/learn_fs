# Group Research: group_293_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_Makefile_sources_o_4aff712f968b

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/Makefile

## Summary
Small kernel-directory makefile focused on regenerating syscall dispatch artifacts and descending into selected subdirectories.

## Main Responsibilities
- Defines `sysent` target for regenerating `init_sysent.c`, `syscalls.c`, `syscall.mk`, `sysproto.h`, and `sysunion.h`.
- Backs up existing generated syscall files before running `makesyscalls.sh syscalls.master`.
- Declares `firmware` and `libmchain` as subdirectories.

## Important Behavior
The default `all` target only prints `make sysent only`, so this file is not a general kernel build driver. Its main operational path is the generated syscall-table refresh flow.

## Risks
Generated outputs span both `sys/kern` and `sys/sys`; partial regeneration or interrupted backup/rewrite can leave syscall metadata inconsistent.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/bus_if.m -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/bus_if.m

## Summary
Defines the DragonFly BSD `bus` kernel object interface consumed by the device method generator. It specifies parent-bus methods for child enumeration, resource management, interrupt management, and child metadata.

## Main Responsibilities
- Provides `bus` interface method declarations.
- Supplies defaults for generic child printing, driver-added handling, resource-list lookup, child-present checks, interrupt config, interrupt enable/disable, DMA tag retrieval, and failed resource allocation.
- Documents expected bus/child contracts for ivars, resources, interrupts, and PnP/location strings.

## Key Methods
- Child lifecycle and metadata: `print_child`, `probe_nomatch`, `read_ivar`, `write_ivar`, `child_detached`, `driver_added`, `add_child`.
- Resource handling: `alloc_resource`, `activate_resource`, `deactivate_resource`, `release_resource`, `set_resource`, `get_resource`, `delete_resource`, `get_resource_list`.
- Interrupt handling: `setup_intr`, `teardown_intr`, `enable_intr`, `disable_intr`, `config_intr`.
- Bus properties: `child_present`, `child_pnpinfo_str`, `child_location_str`, `get_dma_tag`.

## Important Behavior
`alloc_resource` defaults to `null_alloc_resource`, so buses that do not implement it fail allocation cleanly. The interrupt-disable contract explicitly says disabling prevents future handler calls but does not interlock with a currently running handler.

## Risks
This file defines generated ABI-style driver hooks. Signature drift or default behavior changes affect many bus and device drivers. Resource `rid` handling is bus-specific, so callers must not assume returned IDs equal requested IDs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/bus_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/cpu_if.m -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/cpu_if.m

## Summary
Defines a minimal `cpu` kernel object interface.

## Main Contents
- Includes bus and sensor headers.
- Declares `INTERFACE cpu`.
- Defines one method, `get_sensdev`, returning a `struct ksensordev *` for a CPU device.

## Risks
The interface has no default implementation. Drivers or CPU bus glue calling `CPU_GET_SENSDEV` need a concrete method or must handle absent method behavior from the generated interface layer.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/cpu_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/device_if.m -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/device_if.m

## Summary
Defines the DragonFly BSD `device` kernel object interface used by generated driver method glue. It covers standard probe, identify, attach, detach, shutdown, suspend, resume, quiesce, and register hooks.

## Main Responsibilities
- Declares the core device lifecycle method set.
- Documents probe return-value semantics, including negative priority matches and positive errno failures.
- Provides null defaults for shutdown, suspend, resume, quiesce, and register.

## Key Methods
- `probe(device_t dev)`.
- Static `identify(driver_t *driver, device_t parent)`.
- `attach(device_t dev)`.
- `detach(device_t dev)`.
- `shutdown`, `suspend`, `resume`, `quiesce`, `register`.

## Important Behavior
A probe success code below zero is only a priority match; drivers returning it must not assume attach will follow or that probe-time softc state survives. A zero probe success means the driver can assume it will attach.

## Risks
This is a cross-driver ABI surface. Incorrect default assumptions in drivers can leak probe resources or retain invalid softc state when competing drivers probe the same device.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/device_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/firmware/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/firmware/Makefile

## Summary
Kernel module makefile for the firmware subsystem.

## Main Contents
- Sets `.PATH` to the parent kernel directory.
- Builds `KMOD=firmware`.
- Uses `subr_firmware.c` as the only source.
- Includes `bsd.kmod.mk`.

## Risks
The module source is outside the `firmware` directory via `.PATH`, so build and source ownership are split between this subdirectory and `sys/kern/subr_firmware.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/firmware/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/genassym.sh -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/genassym.sh

## Summary
Shell/AWK helper that converts special common symbols in an object file into C preprocessor `#define` constants for assembly support.

## Main Responsibilities
- Accepts `genassym [-o outfile] objfile`.
- Runs `${NM:-nm}` with optional `NMFLAGS`.
- Parses `nm` common-symbol records ending in `sign`, `w0`, `w1`, `w2`, and `w3`.
- Reconstructs a hex value from four 16-bit word fragments and emits `#define name value`.

## Important Behavior
The script detects negativity through a companion `sign` symbol, strips leading zeroes, prefixes nonzero values with `0x`, and writes either to stdout or the `-o` file via shell redirection.

## Risks
The file comment notes imperfect representation of values like two's-complement `INT_MIN`. Correct output depends on symbol naming conventions emitted by the corresponding genassym C source and on `nm` output format.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/genassym.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_elf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_elf.c

## Summary
Implements DragonFly BSD ELF image activation and ELF core dump generation. It validates ELF binaries, selects ABI brand information, maps loadable segments into a new process VM space, loads interpreters, builds auxiliary vectors, and writes ELF core/checkpoint metadata.

## Main Responsibilities
- Maintains the ELF brand registry via `__elfN(insert_brand_entry)`, `__elfN(remove_brand_entry)`, and `__elfN(brand_inuse)`.
- Validates ELF headers, program header placement, target class/data/version, and supported machine brands.
- Loads `PT_LOAD` segments from vnode-backed VM objects, including BSS expansion and final-page copy handling.
- Finds brand information through ABI notes, `EI_OSABI`, old FreeBSD header branding, interpreter path, or fallback brand sysctl.
- Handles ET_DYN/PIE base selection and optional interpreter path rewriting/emulation prefixes.
- Constructs DragonFly ELF auxargs in `__elfN(dragonfly_fixup)`.
- Generates ELF core files through `generic_elf_coredump`, including notes, VM segment headers, vnode file handles, signal state, and open-file checkpoint metadata.

## Key APIs
- Exec path: `exec_elf32_imgact` or `exec_elf64_imgact` through `EXEC_SET_ORDERED`.
- Loader helpers: `__elfN(load_section)`, `__elfN(load_file)`, `extract_interpreter`, `check_PT_NOTE`.
- Core dump path: `__elfN(coredump)`, `generic_elf_coredump`, `__elfN(corehdr)`, `__elfN(puthdr)`, `elf_putallnotes`, `elf_puttextvp`, `elf_putsigs`, `elf_putfiles`.

## Important Behavior
`__elfN(load_section)` maps file-backed text/data with copy-on-write and disables core dumping for read-only sections. When `memsz > filsz`, it creates anonymous backing for BSS and copies the file tail fragment into the anonymous page.

The main image activator rejects non-ELF files with `-1`, but returns errno after recognizing an ELF header. Program headers must fit in the first page. `PT_INTERP` strings and ABI notes may be read beyond the first page using `exec_map_page`.

For core dumps, writable or otherwise dumpable normal map entries become `PT_LOAD` segments. Additional checkpoint-oriented data is appended after notes: VM text/data info, vnode file handles for mapped vnode objects, signal dispositions, timers, masks, and selected open vnode file descriptors.

## State and Integration
Sysctls expose fallback brand and PIE-base behavior under `kern.elf32` or `kern.elf64`, plus legacy coredump mode under `debug`. The loader sets `p_sysent`, `p_osrel`, `entry_addr`, VM text/data sizing, and `imgp->auxargs`.

## Risks
Brand registry scanning is explicitly race-prone for unload checks. Program-header support is limited to headers fitting in the first page for the main executable. Core/checkpoint output depends on stable vnode file handles and can silently omit vnode handles when `VFS_VPTOFH` fails.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_resident.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_resident.c

## Summary
Implements resident executable support: privileged processes can snapshot an executable's VM space so later execs of that vnode reuse the resident VM image instead of loading from disk.

## Main Responsibilities
- Maintains a global `exec_res_list` protected by `exec_list_lock`.
- Exposes `vm.resident` sysctl reporting resident executable IDs, paths, entry addresses, and stat data.
- Provides `exec_resident_imgact()` image activation for vnodes with `v_resident`.
- Implements `exec_sys_register` and `exec_sys_unregister` syscalls.

## Important Behavior
Registration requires `SYSCAP_NOVM_RESIDENT`, uses the current process text vnode, holds the vnode, forks the current `vmspace`, initializes its pmap, stores syscall vector and entry address, and links the resident record to `vp->v_resident`.

Activation increments `vr_refs` while under shared list lock, switches the exec target to the resident `vmspace` with `exec_new_vmspace`, sets `imgp->resident`, `p_sysent`, and `entry_addr`, then decrements the ref.

Unregister supports current process (`id == -1`) and all entries (`id == -2`), waiting briefly when `vr_refs` indicates an exec race.

## Risks
Resident entries tie vnode lifetime, VM space lifetime, entry address, and syscall vector together. The unregister wait loop uses `tsleep(..., 1)` polling and depends on `vr_refs` dropping promptly.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_resident.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_shell.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_shell.c

## Summary
Implements `#!` shell-script image activation by rewriting the exec argument buffer to invoke the interpreter with optional interpreter arguments and the script filename.

## Main Responsibilities
- Detects shell scripts by endian-adjusted `#!` magic.
- Prevents recursive script interpretation through `imgp->interpreted`.
- Parses interpreter tokens from the first page until newline, `#`, NUL, or page end.
- Replaces original `argv[0]` with interpreter tokens and appends the original script path.
- Stores the interpreter pathname in `imgp->interpreter_name`.

## Important Behavior
The parser treats spaces and tabs as separators and increments `argc` for each interpreter token. It preserves the existing argument/environment tail by moving it forward in the exec argument buffer, then adjusts `begin_envv`, `endp`, and remaining space.

## Risks
Only the first page is searched. A line that reaches page end returns `ENAMETOOLONG`. The parser's `#` comment termination means interpreter arguments after `#` are ignored.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/imgact_shell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/init_main.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/init_main.c

## Summary
Core machine-independent boot orchestration for DragonFly BSD. It initializes process 0, executes ordered SYSINIT entries, creates process 1, mounts initial roots/devfs context, and starts `/sbin/init`.

## Main Responsibilities
- Defines static bootstrap objects for `proc0`, `lwp0`, `thread0`, session, process group, credentials, file descriptors, limits, and VM space.
- Implements `mi_proc0init()` for low-level CPU0 thread/LWP/proc linkage.
- Implements `mi_startup()` to sort and run linker-set SYSINIT records, including dynamically added SYSINITs.
- Initializes proc0/session/pgrp/credentials/sigacts/fd table/limits/vmspace in `proc0_init`.
- Creates and later schedules the init process through `create_init` and `kick_init`.
- Implements `start_init()` to set root directory, mount devfs, build user stack arguments, and try paths in `kern.init_path`.
- Initializes the user/kernel shared `kpmap` timing page metadata and per-CPU globaldata fields.

## Important Behavior
`mi_startup()` bubble-sorts SYSINIT entries by subsystem and order, marks completed entries with `SI_SPECIAL_DONE`, and restarts if `sysinit_add()` merges new entries.

`start_init()` obtains the root vnode from the boot mount, sets `fd_cdir` and `fd_rdir`, sets namecache roots, mounts devfs, creates a one-page user stack, and tries colon-separated init paths. It passes boot flags like `-s` when single-user mode is requested.

## Filesystem/VFS Signals
The file establishes the first process's root/cwd vnode references and namecache root, mounts devfs, and later executes init through `sys_execve`. Its early setup is foundational for all subsequent path lookup and VFS behavior.

## Risks
Boot ordering is critical. Incorrect SYSINIT subsystem/order values can run components before proc0, VM, clocks, root, or helper threads are ready. `start_init()` panics if no init path succeeds.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/init_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/init_sysent.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/init_sysent.c

## Summary
Generated system call dispatch table. It maps syscall numbers to argument sizes, message sizes, and kernel syscall handler functions.

## Main Responsibilities
- Defines `struct sysent sysent[]`.
- Uses `AS(name)` to express argument structure size in register units.
- Maps active, obsolete, compatibility, module-reserved, and unimplemented syscall slots.
- Covers syscalls 0 through 555 in this snapshot.

## Filesystem-Relevant Entries
Includes core filesystem and VFS operations such as `open`, `close`, `link`, `unlink`, `chdir`, `fchdir`, `mknod`, `chmod`, `chown`, `mount`, `unmount`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `umask`, `chroot`, `msync`, `munmap`, `mprotect`, `madvise`, `rename`, `flock`, `mkdir`, `rmdir`, `utimes`, `quotactl`, `getfh`, `statfs`, `fstatfs`, `fhstatfs`, `fhopen`, ACL syscalls, extattr syscalls, `sendfile`, modern `*at` calls, `statvfs`, `fstatvfs`, `fhstatvfs`, `getvfsstat`, `fexecve`, `posix_fallocate`, `fdatasync`, and `futimesat`.

## Important Behavior
Many historical or reserved slots dispatch to `sys_nosys`; slots 210-219 dispatch to `sys_lkmnosys` for loadable module syscall placeholders. The file is marked do-not-edit and regenerated from `syscalls.master`.

## Risks
Manual edits will be overwritten. Dispatch table, syscall numbers, generated prototypes, syscall headers, and user ABI must remain synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/init_sysent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_acct.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_acct.c

## Summary
Implements BSD process accounting: privileged users can enable accounting to a regular file, and exiting processes append compact accounting records.

## Main Responsibilities
- Implements `acct(2)` via `sys_acct`.
- Opens and tracks the accounting vnode.
- Writes process accounting records from `acct_process`.
- Periodically suspends/resumes accounting based on free filesystem space.
- Provides sysctls for suspend percentage, resume percentage, and check frequency.

## Important Behavior
`sys_acct` requires `SYSCAP_NOACCT`, opens the target path with `FWRITE|O_APPEND`, requires a regular file, closes any previous accounting vnode, and starts `acctwatch`.

`acct_process` snapshots command name, user/system CPU time, elapsed time, memory average, I/O block counts, real uid/gid, controlling tty, and accounting flags. It temporarily removes the process file-size rlimit before appending `struct acct`.

`acctwatch` uses `VFS_STATFS` on the accounting file mount. It moves `acctp` to `savacctp` when free blocks fall below `kern.acct_suspend` and resumes when above `kern.acct_resume`.

## Risks
Accounting relies on a live vnode and mount; forced unmount or `VBAD` causes closure. The code serializes vnode switching with `acct_lock`, but record appends occur while holding that lock, so slow filesystem writes can delay accounting control paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_acct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_acl.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_acl.c

## Summary
Implements generic syscall wrappers for filesystem ACL operations. It handles path/fd to vnode conversion and user/kernel ACL copying, while filesystem-specific semantics live in VOP ACL methods.

## Main Responsibilities
- Wraps `VOP_SETACL`, `VOP_GETACL`, and `VOP_ACLCHECK`.
- Implements path-based ACL syscalls: `__acl_get_file`, `__acl_set_file`, `__acl_delete_file`, `__acl_aclcheck_file`.
- Implements fd-based ACL syscalls: `__acl_get_fd`, `__acl_set_fd`, `__acl_delete_fd`, `__acl_aclcheck_fd`.

## Important Behavior
Path syscalls use `nlookup` with `NLC_FOLLOW`, then `cache_vref` to obtain a vnode reference. FD syscalls use `holdvnode`. Set/delete operations lock the vnode exclusive; get/check rely on the VOP path.

User ACL data is copied into kernel memory before set/check and copied back after get.

## Risks
`vacl_delete()` ignores its `type` argument and calls `VOP_SETACL(vp, ACL_TYPE_DEFAULT, 0, ucred)`, so delete behavior is hardwired to default ACLs in this file. ACL permission and semantic validation are delegated to individual filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_caps.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_caps.c

## Summary
Implements DragonFly syscall capability restriction helpers and `syscap_get`/`syscap_set` syscalls. Capabilities here are restriction bits stored in credentials and checked alongside root/group/jail policy.

## Main Responsibilities
- Provides `sys_syscap_get` and `sys_syscap_set`.
- Implements exec-time capability inheritance in `caps_exec`.
- Provides raw and checked helpers: `caps_get`, `caps_set_locked`, `caps_priv_check`, `caps_priv_check_td`, and `caps_priv_check_self`.
- Checks parent-process capability state when `__SYSCAP_INPARENT` is requested.

## Important Behavior
`syscap_set` only adds restriction bits; it compares requested flags with current state and atomically creates a new credential with `cratom_proc` when changes are needed. It also marks `SYSCAP_ANY` bits.

`caps_exec` shifts EXEC restriction bits into SELF bits and preserves EXEC bits across exec. `caps_priv_check` enforces root unless `__SYSCAP_NOROOTTEST` is present, optionally permits wheel via `__SYSCAP_WHEELOK`, then checks credential capability bits and jail restrictions.

## Risks
The `kern.caps_available` sysctl is declared but not consulted in this implementation. Resource data for syscaps is effectively unimplemented here; `syscap_get` returns an EOF marker and `syscap_set` rejects non-null data.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_caps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_checkpoint.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_checkpoint.c

## Summary
Implements process checkpoint freeze/thaw support using ELF core-style files. It can write a checkpoint through the generic ELF core dump path and restore process registers, signals, VM mappings, and selected vnode-backed file descriptors.

## Main Responsibilities
- Implements `sys_checkpoint` for `CKPT_FREEZE` and `CKPT_THAW`.
- Reads and validates ELF headers/program headers from checkpoint files.
- Restores ELF notes into register/fpreg/process-name state.
- Restores signal actions, timers, signal masks, and parent signal.
- Restores VM text/data sizing and vnode-backed mappings from stored file handles.
- Restores selected open vnode file descriptors.
- Generates checkpoint filenames from `kern.ckptfile`.

## Important Behavior
Freeze requires membership in `kern.ckptgroup` unless it is `-1`. Direct freeze can use a supplied writable fd or the signal-handler path, which expands a filename, unlinks any previous checkpoint file, opens a new `0600` file with `O_NOFOLLOW`, stops other threads, and calls `generic_elf_coredump`.

Thaw requires a readable fd and current-process restore. It parses the ELF core header, notes, vnode mapping table, signal info, file descriptor info, then maps saved program segments. Restored mappings may be backed by original vnode handles or by the checkpoint file itself.

## Filesystem/VFS Signals
Checkpoint restore depends heavily on file handles: `ckpt_fhtovp` resolves `fhandle_t` through `vfs_getvfs` and `VFS_FHTOVP`, and vnode-backed mappings are reopened with `fp_vpopen`.

## Risks
The implementation has explicit limitations around multiple LWPs and non-vnode descriptors. Restore can fail if mounts or file handles are stale. The fd restore path closes descriptors `>= 3`, so it is intentionally destructive to the restoring process's current descriptor table.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_checkpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_clock.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_clock.c

## Summary
Implements DragonFly BSD core clock, timekeeping, CPU accounting, scheduler/stat clocks, NTP adjustments, PPS support, and timestamp APIs.

## Main Responsibilities
- Initializes per-CPU hardclock, statclock, and scheduler clock systimers.
- Maintains global ticks, scheduler ticks, uptime, realtime, boottime, basetime FIFO, and ticktime snapshots.
- Applies `adjtime`, NTP permanent/one-shot corrections, and leap-second adjustments.
- Charges CPU time to user, nice, system, interrupt, and idle buckets.
- Updates process timers, profiling, resource usage integrals, and scheduler accounting.
- Registers CPU percentage collection callbacks with `kcollect`.
- Exposes clock and CPU accounting sysctls.
- Provides micro/nano uptime and realtime APIs.
- Implements PPS ioctls/events and simple TSC delay helpers.

## Important Behavior
CPU 0 owns system-wide ticks, NTP correction, basetime updates, ticktime snapshots, `kpmap` timestamp updates, and leap-second state. Other CPUs copy hardtime state from CPU 0 through a FIFO/index scheme with memory fences.

`hardclock` also drives soft ticks, existential-lock pseudo ticks, VM/VFS cache rollups, process interval timers, and deferred work. `statclock` measures elapsed microseconds from the CPU timer and charges the interrupted thread/process. `schedclock` calls the user scheduler and updates resource usage maximum RSS.

Fast `getmicrotime`/`getnanotime` return ticktime snapshots; precise `microtime`/`nanotime` read the CPU timer and add current basetime.

## Filesystem/VFS Signals
Although not a filesystem file, it calls `vfscache_rollup_cpu()` from hardclock and supplies time APIs used by VFS timestamps, accounting, checkpointing, and timeout logic.

## Risks
The file relies on careful CPU-local state, memory fences, and CPU0-only basetime publication. Time can step for realtime corrections; comments warn `time_second` can backstep while uptime remains monotonic.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_collect.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_collect.c

## Summary
Implements the `kcollect` rolling statistics framework. A kernel thread samples registered counters every 10 seconds and exposes scale, identifier, and sample records through `kern.collect_data`.

## Main Responsibilities
- Registers and unregisters collection slots with callbacks and scale metadata.
- Provides `kcollect_setvalue` and `kcollect_setscale` for callbacks/rollups.
- Allocates a ring buffer sized by `kern.collect_samples`.
- Runs `kcollect_thread` to populate timestamped samples.
- Exposes collected data through a sysctl.

## Important Behavior
If `kern.collect_samples` is left at `-1`, it auto-sizes to 1024 or 8192 samples based on `kmem_lim_size()`. Each sample stores current `ticks`, realtime, and all callback values. The sysctl emits a scale record, an 8-byte-per-slot id record, then recent samples in reverse chronological ring order.

## Risks
Callbacks run under `kcollect_lock`, so registered callbacks should avoid long blocking behavior. `kcollect_setvalue` assumes the array and sample count are valid and is intended for normal callback-time rollup use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_collect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_condvar.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_condvar.c

## Summary
Implements DragonFly condition-variable primitives on top of `tsleep`, `lksleep`, and `mtxsleep`.

## Main Responsibilities
- Initializes and destroys `struct cv` spinlock state.
- Provides timed wait helpers for lockmgr locks and mutexes.
- Provides signal/broadcast wakeups.
- Exposes `cv_has_waiters`.

## Important Behavior
Wait paths manually interlock with `tsleep_interlock`, increment `cv_waiters` under `cv_lock`, then sleep with `PINTERLOCKED`. `_cv_signal` checks `cv_waiters`; broadcast zeroes the count and calls `wakeup`, while single signal decrements and calls `wakeup_one`.

## Risks
`cv_waiters` is a lightweight waiter hint rather than a fully audited wait-queue count. Timeouts or interrupted sleeps are not decremented in the wait path, so callers should treat `cv_has_waiters` as advisory.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_condvar.c -->