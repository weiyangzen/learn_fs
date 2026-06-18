# Group Research: group_1258_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_exec_elf_c_sources_os_52849947d64e

Scope: `Docs/research_subset_a.md`, source tree `sources/os/bsd/netbsd-src`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf.c

## Purpose
Shared machine-independent ELF executable loader implementation, included by the 32-bit and 64-bit ELF wrapper files after defining `ELFSIZE`.

## Main Interfaces
- `exec_elf_makecmds()` validates ELF headers, reads program headers, handles `PT_INTERP`, probes NetBSD ELF notes/emulation, builds VM commands for loadable segments, loads the interpreter, and sets the initial entry point.
- `elf_check_header()` validates magic, ELF class, machine IDs, flags, and program/section header counts.
- `elf_load_psection()` converts one `PT_LOAD` segment into `vmcmd_map_pagedvn`, `vmcmd_map_readvn`, and `vmcmd_map_zero` commands.
- `elf_load_interp()` opens and maps the dynamic loader, checking execute permissions, `MNT_NOEXEC`, and `MNT_NOSUID`.
- `elf_copyargs()` and `elf_populate_auxv()` append ELF auxiliary vectors, including program headers, page size, interpreter base, entry address, stack base, credentials, and optional `AT_SUN_EXECNAME`.
- `netbsd_elf_signature()`, `netbsd_elf_note()`, and `netbsd_elf_probe()` recognize NetBSD ELF notes and populate OS version, PaX, machine-arch, and machine code-model metadata.
- `elf_free_emul_arg()` releases the per-exec ELF argument block.

## Dependencies
Uses the NetBSD exec package, vnode/text marking, UVM VM command infrastructure, PaX ASLR/mprotect hooks, emulation path lookup, kauth credentials, ELF note definitions, and machine-dependent ELF macros.

## Implementation Notes
The file is template-style C: symbol names are remapped through `ELFNAME` macros so the same body emits `elf32_*` and `elf64_*` functions. Dynamic executables can be relocated by `elf_placedynexec()` using PaX ASLR offsets. Loadable writable segments get special tail handling because the paged vnode pager cannot zero-fill a partial final data page.

## Research Notes
This is central executable-loader code with strong ordering and cleanup requirements. Failure paths must release interpreter path buffers, free program-header storage, clear emulation args, and kill pending VM commands. Any change to program-header validation, interpreter placement, auxv sizing, or note parsing can affect native execution, compatibility emulations, ASLR, and set-id handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf32.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf32.c

## Purpose
Builds and registers the 32-bit specialization of the shared ELF loader.

## Main Interfaces
- Defines `ELFSIZE 32` and includes `exec_elf.c`, producing 32-bit ELF loader symbols.
- `exec_elf32_execsw[]` registers ELF32 executable switch entries for NetBSD ELF binaries.
- `exec_elf32_modcmd()` adds or removes the ELF32 exec switch on native 32-bit kernels.
- On 64-bit kernels, the module initializes as dormant so ELF32 support symbols remain available for compat layers such as `netbsd32` and `linux32` without registering as a native exec handler.

## Dependencies
Depends on the shared `exec_elf.c` template, `emul_netbsd`, ELF32 aux vector layout, `exec_add()`, `exec_remove()`, `exec_setup_stack()`, and ELF32 core dump support.

## Implementation Notes
`ELF32_AUXSIZE` reserves space for aux entries plus an executable name path. Optional `EXEC_ELF_NOTELESS` support adds a lower-priority generic ELF32 entry when configured.

## Research Notes
This file is a thin registration wrapper; most behavior comes from `exec_elf.c`. Changes here mainly affect whether ELF32 binaries are recognized natively and how much argument-stack space is reserved for auxv data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf64.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf64.c

## Purpose
Builds and registers the 64-bit specialization of the shared ELF loader.

## Main Interfaces
- Defines `ELFSIZE 64` and includes `exec_elf.c`, producing 64-bit ELF loader symbols.
- `exec_elf64_execsw[]` registers native ELF64 execution support.
- `exec_elf64_modcmd()` handles module init/fini by adding or removing the ELF64 exec switch.

## Dependencies
Depends on shared ELF loader code, ELF64 aux vector layout, NetBSD emulation registration, ELF64 core dump generation, and exec switch management.

## Implementation Notes
The primary exec switch entry uses `netbsd_elf64_probe` and first priority. Optional `EXEC_ELF_NOTELESS` support registers a generic ELF64 fallback at `EXECSW_PRIO_ANY`.

## Research Notes
This file is intentionally small and mirrors the 32-bit wrapper without the 64-bit dormant special case. Functional risk is concentrated in registration priority, aux size accounting, and conditional noteless ELF handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_elf64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_script.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_script.c

## Purpose
Implements `#!` script execution support by transforming a script exec into an interpreter exec with synthetic arguments.

## Main Interfaces
- `exec_script_execsw` registers script recognition using `SCRIPT_HDR_SIZE`.
- `exec_script_modcmd()` adds/removes the script exec handler and refuses autounload to avoid repeated transient unload/reload.
- `exec_script_makecmds()` parses the shebang line, extracts interpreter and optional single interpreter argument, creates fake argv entries, recursively invokes `check_exec()` on the interpreter, and arranges script path or `/dev/fd/N` delivery.

## Dependencies
Uses exec switch infrastructure, pathbuf/namei helpers, file descriptor allocation, vnode access/close operations, optional `FDSCRIPTS`, optional `SETUIDSCRIPTS`, and generic stack setup.

## Implementation Notes
The parser rejects recursive script handling via `EXEC_INDIR`, requires a newline within the script header buffer, strips whitespace before the interpreter, and preserves the historical behavior that all text after the interpreter path is passed as one argument. With `FDSCRIPTS`, unreadable or set-id scripts are passed to the interpreter via `/dev/fd/N`.

## Research Notes
Important invariants are vnode ownership, fd cleanup, fake-argument freeing, and set-id metadata preservation. Error paths close either the temporary fd or original script vnode and destroy VM commands built during a failed interpreter exec.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_script.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_subr.c

## Purpose
Provides common exec VM-command and stack setup helpers used by executable format loaders.

## Main Interfaces
- `new_vmcmd()` appends a VM command and references any vnode it carries.
- `vmcmdset_extend()` grows VM command storage.
- `kill_vmcmds()` releases vnode references and frees VM command arrays.
- `vmcmd_map_pagedvn()` maps demand-paged vnode-backed executable segments.
- `vmcmd_map_readvn()` allocates anonymous memory then reads file data into it.
- `vmcmd_readvn()` performs user-space segment reads and adjusts protections.
- `vmcmd_map_zero()` maps zero-filled memory, including stack regions.
- `exec_read()` reads exact-size executable data from a vnode.
- `exec_setup_stack()` builds accessible stack, inaccessible growth reservation, and guard mappings.

## Dependencies
Uses UVM maps/objects, vnode mapping/access operations, PaX mprotect and ASLR stack hooks, process resource limits, stack-direction macros, and exec package VM command structures.

## Implementation Notes
`vmcmd_get_prot()` centralizes requested/max protection calculation and PaX validation. `exec_setup_stack()` supports 32-bit stack limits through `EXEC_32`, applies stack ASLR, and creates separate guard, inaccessible, and accessible stack VM commands.

## Research Notes
This file is shared by multiple executable loaders. Changes to protection handling or VM command lifetime can affect all exec formats, demand paging, W^X enforcement, stack layout, and vnode reference safety.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/gendevcalls.awk -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/gendevcalls.awk

## Purpose
AWK generator for device call definition files, producing C header fragments with argument structures, binding unions, string macros, and invoke macros.

## Main Interfaces
- `emit_binding(field)` emits a generic binding union plus optional typed binding data.
- `emit_name_macro()` emits `<CALL>_STR`.
- `emit_invoke_macro(field, marg, carg)` emits a compound-literal macro used to invoke a device call.
- `start_decl(arg)` validates declaration state and enforces subsystem-prefixed call names.
- Main pattern rules parse a `subsystem ...;` declaration, call declarations with argument blocks, and call declarations without arguments.
- `END` validates final parser state and emits the header guard close.

## Dependencies
Consumes a specific device-call DSL and emits headers that include `<sys/device.h>` for `struct device_call_generic`.

## Implementation Notes
The generator tracks explicit parser states: expecting subsystem, expecting declaration start, and expecting declaration end. It also converts hyphenated names to underscore C identifiers and uppercase macro names.

## Research Notes
The script is small but strict: malformed declaration order, missing subsystem prefixes, unexpected braces, or unterminated declarations terminate generation with diagnostics. Generated code stability depends on the input DSL preserving the expected first-line version marker and syntax.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/gendevcalls.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/genlintstub.awk -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/genlintstub.awk

## Purpose
AWK generator used by kernel Makefiles to create C lint stubs from specially formatted comments in assembly files.

## Main Interfaces
- Recognizes `LINTSTUB: Empty`, `Func`, `Var`, `include`, and `Ignore` directives.
- `process_word(i)` trims semicolons or comment terminators while scanning declarations.
- `error(msg)` records malformed directives and reports line-specific diagnostics.
- `END` exits nonzero if any directive errors were seen.

## Dependencies
Consumes comments embedded in `.S` files and emits C suitable for lint checking. It assumes function stub return types are only `void`, `int`, or `long`.

## Implementation Notes
Generated output begins with repeated “do not edit” notices. Function directives emit `/* ARGSUSED */`, a stub function body, and a synthetic `return(0)` for `int`/`long`. Include directives pass through as literal `#include` lines.

## Research Notes
This script is build-tooling support rather than runtime kernel code. Its main risk is parser brittleness: comments must match the exact directive spelling and tokenization expected by the AWK patterns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/genlintstub.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_main.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/init_main.c

## Purpose
Primary machine-independent NetBSD kernel startup path: initializes core subsystems, configures devices, mounts root, creates init, starts kernel daemons, and enters the scheduler.

## Main Interfaces
- `main()` performs kernel initialization sequencing from console setup through `uvm_scheduler()`.
- `configure()`, `configure2()`, and `configure3()` split autoconfiguration into early hardware probing, post-CPU/device setup, and mountroot-dependent callbacks.
- `rootconf()` and `rootconf_handle_wedges()` choose root devices, including disk wedge translation.
- `start_init()` waits for root readiness, constructs a small user stack, and tries `/sbin/init`, `/sbin/oinit`, `/sbin/init.bak`, and `/rescue/init`.
- `check_console()` verifies `/dev/console`.
- `calc_cache_size()` computes cache sizing bounded by physical memory and virtual address space.
- `banner()` prints the startup memory/version banner.

## Dependencies
Touches nearly every kernel subsystem: console, locks, UVM, sysctl, kauth/secmodel, modules, buffers, VFS, file descriptors, kqueue, tty, networking, autoconf, random/CPRNG, scheduler, CPU topology, Veriexec, PaX, accounting, ktrace, root mount, and process exec.

## Implementation Notes
Ordering is the core design. The file creates process 0, disables preemption during boot, initializes VFS and devices before root mount, creates process 1 early but gates its exec using `start_init_exec`, finalizes modules/configuration before root selection, then starts pageout and syncer threads.

## Research Notes
This file is the boot choreography. Changes must preserve initialization ordering, especially around sysctl setup, module class initialization, autoconfiguration, root mount, `initproc` race avoidance, preemption enablement, and the point at which process 1 is allowed to exec.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysctl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/init_sysctl.c

## Purpose
Registers and implements many non-base `kern`, `hw`, `debug`, and related sysctl nodes for the full kernel.

## Main Interfaces
- `SYSCTL_SETUP(sysctl_kern_setup)` creates `kern.*` nodes for limits, boot state, vnode/process/file settings, POSIX capability constants, root device/partition, driver listing, coredump settings, build metadata, and message verbosity.
- `SYSCTL_SETUP(sysctl_hw_misc_setup)` creates `hw.usermem`, `hw.usermem64`, and `hw.cnmagic`.
- `SYSCTL_SETUP(sysctl_debug_setup)` conditionally exposes debug variables when `DEBUG` is enabled.
- Handler functions implement validation or computed data for `kern.maxvnodes`, `kern.messages`, `kern.boottime`, `kern.rtc_offset`, `kern.maxproc`, `kern.hostid`, `kern.defcorename`, `kern.cp_time`, `kern.maxptys`, `kern.lwp`, `kern.forkfsleep`, `kern.root_partition`, `kern.drivers`, set-id core settings, CPU IDs, user memory, console magic, root device, and console device.
- `fill_lwp()` copies selected LWP state into `struct kinfo_lwp`.

## Dependencies
Uses sysctl creation/lookup, vnode and VFS drain/reinit paths, kauth authorization, process/LWP locks, CPU iteration, ktrace MIB accounting, device switch conversion tables, console state, UVM accounting, and boot flags.

## Implementation Notes
Several handlers copy kernel snapshots out to user buffers while carefully dropping and reacquiring sysctl locks. `sysctl_kern_lwp()` uses process reference locks and verifies LWP list membership after copyout. Security-sensitive settings use kauth checks before committing changes.

## Research Notes
This file is user-visible kernel ABI surface. Risks are validation mistakes, lock ordering during process/device walks, stale pointer exposure, address exposure policy via `get_expose_address()`, and maintaining compatibility with historic sysctl MIB numbers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysctl_base.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/init_sysctl_base.c

## Purpose
Creates base sysctl tree nodes and minimal `kern`/`hw` nodes shared by normal kernels and rump kernels.

## Main Interfaces
- `sysctl_basenode_init()` creates permanent top-level nodes: `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `ddb`, `proc`, `vendor`, `emul`, and `security`.
- `SYSCTL_SETUP(sysctl_kernbase_setup)` registers base kernel identity nodes such as `ostype`, `osrelease`, `osrevision`, `version`, `hostname`, `domainname`, and `rawpartition`.
- `SYSCTL_SETUP(sysctl_hwbase_setup)` registers hardware identity/capability nodes such as `model`, `machine`, `machine_arch`, `ncpu`, `byteorder`, `physmem`, `pagesize`, `alignbytes`, `physmem64`, and `ncpuonline`.
- `sysctl_hw_machine_arch()` returns per-process machine architecture where applicable.
- `sysctl_setlen()` updates cached hostname/domainname lengths after writes.

## Dependencies
Uses sysctl infrastructure, kernel identity globals, CPU model hooks, memory sizing globals, disklabel constants, and process machine-architecture selection macros.

## Implementation Notes
This file intentionally contains a smaller base set than `init_sysctl.c` because rump kernels cannot use the full kernel sysctl initializer.

## Research Notes
This is foundational sysctl setup. Changes here affect early sysctl tree shape and compatibility for both full NetBSD kernels and rump kernels.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysctl_base.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysent.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/init_sysent.c

## Purpose
Generated native NetBSD system call switch table.

## Main Interfaces
- `struct sysent sysent[]` maps syscall numbers 0-511 to argument sizes/counts, syscall flags, and handler functions.
- Compatibility macros map old ABI handlers to `compat_*` symbols when configured, or to `sys_nosys` otherwise.
- `sysent_nomodbits[]` records which syscall slots are not module-backed.
- Macros `s`, `n`, and `ns` compute argument structure byte sizes and register counts.

## Dependencies
Generated by `makesyscalls.sh` from `syscalls.master`. Includes syscall argument declarations, socket/mount/sched/idtype/ACL types, and optional kernel config headers for modular, NTP, and SysV support.

## Implementation Notes
Entries encode pointer arguments with `SYCALL_ARG_PTR`, wide returns with `SYCALL_RET_WIDE`, 64-bit argument placement with `SYCALL_ARG*_64`, indirect syscall slots, and conditional fillers. Many legacy or optional subsystems route to `sys_nomodule`, allowing module loading or compatibility handling elsewhere; absent slots use `sys_nosys`.

## Research Notes
This file should not be edited directly. It is kernel ABI-critical: syscall number ordering, flags, and argument sizes must match generated headers and userland libc expectations. Filesystem-relevant entries include classic path syscalls, `*at` variants, mount/unmount, stat/vfs/statvfs, extended attributes, ACL operations, `fdiscard`, `posix_fallocate`, `memfd_create`, and exec-related calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/init_sysent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_acct.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_acct.c

## Purpose
Implements BSD process accounting: enabling/disabling accounting files, monitoring free space, and writing accounting records on process exit.

## Main Interfaces
- `acct_init()` initializes global accounting state and lock.
- `sys_acct()` authorizes accounting changes, opens/truncates-validates the accounting file, swaps accounting state, stores credentials, and starts the watcher thread.
- `acct_process()` writes one `struct acct` record at process exit.
- `acctwatch()` periodically checks filesystem free space and suspends/resumes accounting.
- `acct_stop()` closes the accounting vnode and releases credentials.
- `acct_chkfree()` compares available blocks against suspend/resume thresholds.
- `encode_comp_t()` encodes elapsed/user/system times and I/O counts into BSD compact accounting format.

## Dependencies
Uses kauth authorization, vnode open/close/getattr/setattr/statvfs, process resource usage, credentials, tty/session state, kernel threads, rwlocks, syslog, and syscall argument definitions.

## Implementation Notes
`acct_lock` serializes syscalls and watcher/thread state. Accounting is suspended below `acctsuspend` percent free blocks and resumed above `acctresume`. `sys_acct()` truncates partial trailing accounting records when reusing an existing file. `acct_process()` temporarily raises `RLIMIT_FSIZE` to avoid user file-size limits preventing kernel accounting writes.

## Research Notes
The major correctness concerns are vnode lifetime during forced unmounts, watcher shutdown, credential ownership for writes, and avoiding deadlocks around process locks and accounting file I/O. This file is part of process-exit behavior, so failures must be logged without destabilizing exit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_acct.c -->