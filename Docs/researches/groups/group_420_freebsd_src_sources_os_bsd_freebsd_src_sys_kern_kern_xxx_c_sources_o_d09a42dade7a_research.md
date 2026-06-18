# Group Research: group_420_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_xxx_c_sources_o_d09a42dade7a

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_xxx.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_xxx.c

## Purpose
Implements legacy FreeBSD/BSD compatibility syscalls for old hostname, hostid, `getkerninfo(2)`, and FreeBSD 4-era `uname(2)`/domain-name ABI surfaces. This is compatibility glue that translates obsolete syscall ABIs onto modern `sysctl`-backed kernel state.

## Key Elements
- `ogethostname()` and `osethostname()` forward old hostname get/set calls to `CTL_KERN.KERN_HOSTNAME`.
- `ogethostid()` and `osethostid()` forward old hostid calls to `CTL_KERN.KERN_HOSTID`.
- `oquota()` is a compatibility stub returning `ENOSYS`.
- `ogetkerninfo()` maps old `KINFO_*` selectors to modern sysctl MIBs for routing, processes, files, VM totals, load average, and clockrate.
- `KINFO_BSDI_SYSINFO` fabricates enough BSDI 1.x-style system information for old BSDI `uname()` consumers.
- `freebsd4_uname()` implements the historical FreeBSD 1.1 binary ABI with fixed `SYS_NMLN == 32` fields.
- `freebsd4_getdomainname()` and `freebsd4_setdomainname()` map old domain-name calls to `KERN_NISDOMAINNAME`.

## Behavior
The compatibility entry points are compiled only under `COMPAT_43` or `COMPAT_FREEBSD4`. Most operations build integer sysctl MIB arrays and call `userland_sysctl()` or `kernel_sysctl()` rather than directly touching global variables. String-returning operations explicitly force trailing NUL bytes in fixed-size legacy structures.

## Filesystem / VM Relevance
The file is not a filesystem implementation, but `ogetkerninfo()` exposes old `KINFO_FILE` and `KINFO_METER` views through `KERN_FILE` and `VM_TOTAL`. These are compatibility inspection paths that can affect old administrative tools observing open files, route tables, and VM totals.

## Locking and Safety
The code delegates synchronization and copyin/copyout validation to sysctl and copy routines. The BSDI compatibility path uses static buffers (`bsdi_si`, `bsdi_strings`) to avoid stack bloat, trims output to the caller's buffer size, and writes back the size value on success.

## Notable Edge Cases
- `ogetkerninfo()` returns the amount needed in `td_retval[0]`, even when the caller buffer is smaller.
- The BSDI sysinfo structure stores string offsets relative to the structure base, not kernel pointers.
- `freebsd4_uname()` synthesizes the legacy `version` field by copying from the first `#` up to `:`.
- The file is entirely ABI compatibility support and should not be used as the model for new syscall design.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_xxx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/ksched.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/ksched.c

## Purpose
Provides the kernel scheduler adapter for POSIX P1003.1B realtime scheduling APIs. It maps POSIX policies and priorities onto FreeBSD's `rtprio`/scheduler priority model.

## Key Elements
- Defines `FEATURE(kposix_priority_scheduling, ...)`.
- `struct ksched` stores the round-robin interval reported through POSIX APIs.
- `ksched_attach()` allocates scheduler state and computes `rr_interval` from `hz` and `sched_rr_interval()`.
- `ksched_detach()` frees scheduler state.
- `getscheduler()` maps `RTP_PRIO_FIFO` to `SCHED_FIFO`, `RTP_PRIO_REALTIME` to `SCHED_RR`, and other classes to `SCHED_OTHER`.
- `ksched_setparam()`, `ksched_getparam()`, `ksched_setscheduler()`, and `ksched_getscheduler()` implement POSIX parameter/policy operations.
- `ksched_yield()` delegates to `sched_relinquish(curthread)`.
- `ksched_get_priority_max()`, `ksched_get_priority_min()`, and `ksched_rr_get_interval()` expose POSIX limits.

## Priority Model
POSIX treats numerically higher values as higher priority, while traditional FreeBSD priorities use lower numeric values for higher priority. The file centralizes conversions with:
- `p4prio_to_rtpprio()` / `rtpprio_to_p4prio()` for realtime priorities.
- `p4prio_to_tsprio()` / `tsprio_to_p4prio()` for timeshare priorities.

## Integration
The code depends on scheduler primitives in `<sys/sched.h>` and priority conversion helpers `pri_to_rtp()` and `rtp_to_pri()`. It is called by `p1003_1b.c` after syscall-layer permission checks have selected and locked the target thread/process.

## Notable Edge Cases
- `SCHED_OTHER` priority handling is implementation-defined and maps into the timeshare range.
- Invalid priorities or policies return `EINVAL`.
- `ksched_getparam()` clamps or interprets timeshare priority state so POSIX callers see the expected ascending priority scale.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/ksched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/link_elf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/link_elf.c

## Purpose
Implements FreeBSD's ELF executable/shared-object style kernel linker class (`elf32` or `elf64`) for preloaded and dynamically loaded kernel modules. It parses ELF dynamic sections, maps load segments, applies relocations, exposes symbols/debug/CTF data, manages linker sets, and integrates modules with GDB, DDB, per-CPU data, VNET data, and machine-dependent ELF hooks.

## Key Elements
- `struct elf_file` extends `struct linker_file` with ELF dynamic metadata, SysV hash tables, relocation tables, symbol/string tables, CTF data, constructor state, per-CPU/VNET relocation bases, and optional GDB link-map state.
- `link_elf_methods[]` implements the `linker_if.m` interface for symbol lookup, debug lookup, CTF, loading, unloading, preload finishing, linker sets, and function enumeration.
- `link_elf_init()` creates the kernel linker file from `_DYNAMIC` and preload metadata, parses kernel symbols, initializes linker set tracking, and invokes kernel constructors.
- `parse_dynamic()` handles `DT_HASH`, `DT_STRTAB`, `DT_SYMTAB`, `DT_REL*`, `DT_RELA*`, `DT_JMPREL`, `DT_PLTGOT`, `DT_PLTREL`, and GDB `DT_DEBUG`.
- `link_elf_link_preload()` and `link_elf_link_preload_finish()` attach to loader-preloaded KLDs, parse dynamic metadata, prepare pcpu/VNET storage, protect mappings, relocate, and finish MD registration.
- `link_elf_load_file()` opens a vnode, validates ELF headers, maps `PT_LOAD` segments, reads text/data, zeroes BSS, loads dependencies, relocates, applies final protections, and imports section symbol tables when present.

## Relocation and Symbol Resolution
- `relocate_file()` runs normal relocations first, then GNU IFUNC relocations.
- `relocate_file1()` iterates `REL`, `RELA`, PLT `REL`, and PLT `RELA` tables and calls MD `elf_reloc()`.
- `elf_lookup()` resolves local symbols directly by index and global/weak symbols through `linker_file_lookup_symbol()`.
- `elf_relocaddr()` rewrites addresses that fall in pcpu or VNET linker sets to their allocated runtime bases.
- `link_elf_reloc_local()` applies local relocations before dependencies and external resolution.

## Loader Memory Model
For file-backed loads, the code reserves one contiguous kernel mapping covering the ELF load address range. With `SPARSE_MAPPING`, it allocates a VM object, wires segment ranges, and later downgrades permissions by segment flags. Without it, it uses executable malloc memory. Preloaded modules use `pmap_change_prot()` on supported architectures to temporarily make text/data relocatable and then restore protections.

## Linker Sets, PCPU, and VNET
- `parse_dpcpu()` locates the `pcpu` linker set, validates i386 padding when relevant, allocates per-CPU storage with `dpcpu_alloc()`, copies initial data, and records an address translation range.
- `parse_vnet()` performs analogous setup for VNET data when `VIMAGE` is enabled.
- `elf_set_add()`, `elf_set_find()`, and `elf_set_delete()` maintain sorted non-overlapping address ranges for pcpu/VNET translation during relocation.
- `link_elf_lookup_set()` resolves `__start_set_<name>` and `__stop_set_<name>` symbols.

## Debug and Introspection
- DDB/debug symbols come from dynamic symbols or loader-provided symbol blocks for preloaded modules.
- `link_elf_lookup_debug_symbol()`, `link_elf_debug_symbol_values()`, `link_elf_search_symbol()`, and function iteration helpers support kernel debugging and tracing.
- CTF operations are supplied by included `kern/kern_ctf.c`.
- Optional GDB support maintains `r_debug` and a `link_map` list so a debugger can track module load/unload events.

## Filesystem / VM Relevance
Dynamic module loading is vnode-backed through `vn_open()`, `vn_rdwr()`, `VOP_UNLOCK()`, and `vn_close()`, with MAC load checks via `mac_kld_check_load()`. The loader directly manages kernel VM mappings, page protections, wiring, and executable memory, making it relevant to VM safety and executable code lifecycle.

## Notable Edge Cases
- Program headers are expected to fit in the first page; otherwise the code reports unreadable headers.
- `PT_INTERP` is rejected and dynamically linked objects without `PT_DYNAMIC` are rejected.
- Local symbol leakage into global resolution is tunable through `debug.link_elf_leak_locals`.
- IFUNC relocation is split into early and late paths, including `link_elf_ireloc()` and `link_elf_late_ireloc()` on supported architectures.
- Unload releases pcpu/VNET allocations, GDB link-map entries, mapped memory, symbol strings, and CTF buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/link_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/link_elf_obj.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/link_elf_obj.c

## Purpose
Implements FreeBSD's ELF relocatable-object kernel linker class (`elf32_obj` or `elf64_obj`). Unlike `link_elf.c`, this loader is section-header driven for `ET_REL` modules: it loads allocated sections, builds section-to-runtime-address tables, applies local and external relocations, manages constructors/destructors, and exposes debug/CTF symbols.

## Key Elements
- `Elf_progent` records loaded program sections: runtime address, original address for debuggers, size, flags, original section number, and section name.
- `Elf_relent` and `Elf_relaent` record relocation tables and target section indexes.
- `struct elf_file` stores section headers, program/relocation tables, debug symbols, section string table, CTF data, VM object, and preload state.
- `link_elf_methods[]` implements the same linker interface as `link_elf.c`, but with object-file lookup semantics.
- `link_elf_init()` registers the object linker class at `SI_SUB_KLD`.

## Loading Paths
`link_elf_link_preload()` handles loader-preloaded `ET_REL` modules whose ELF header, section headers, and section contents were already placed in memory. It validates target class/data/machine, relocates saved `sh_addr` values relative to the preload base, builds program and relocation tables, allocates pcpu/VNET section storage, fixes constructor/destructor addresses, and applies local relocations.

`link_elf_load_file()` opens a vnode, reads the ELF header and section headers, validates that exactly one symbol table exists, reads symbol/string/section-name tables, computes a contiguous kernel mapping size for allocated sections, maps and wires a VM object, reads `PROGBITS` and unwind sections, zeroes `NOBITS`, loads relocation tables, updates symbol values to runtime addresses, loads dependencies, performs external relocations, calls MD load hooks, resolves IFUNCs, protects the mapping, invokes constructors, and returns the linker file.

## Relocation and Symbol Resolution
- `link_elf_reloc_local()` handles local relocations and fixes `__start_`/`__stop_` linker-set symbols before relocation.
- `relocate_file()` applies external relocations, again in normal then IFUNC phases.
- `elf_obj_lookup()` resolves defined symbols from adjusted `st_value`, calls IFUNC resolvers when needed, and resolves undefined globals/weak symbols through `linker_file_lookup_symbol()`.
- Successful global lookup results are temporarily cached with `SHN_FREEBSD_CACHED` and later cleaned by `elf_obj_cleanup_globals_cache()`.
- `findbase()` maps a relocation target section number to its loaded section base.

## Memory Protection and Lifecycle
The loader initially grants write/execute access while relocations run, then `link_elf_protect()` derives final page protections from section flags. Since sections can share pages, it merges protections for overlapping page ranges and protects gaps as read-only or read-write for preloaded trailing data. `link_elf_unload_file()` invokes destructors, calls MD unload hooks, frees pcpu/VNET allocations, resets preload mapping protections, removes VM mappings, and frees symbols, relocation tables, section names, and CTF buffers.

## Linker Sets, PCPU, and VNET
- Linker sets are represented as sections named `set_<name>` and returned directly by `link_elf_lookup_set()`.
- `DPCPU_SETNAME` sections are copied into `dpcpu_alloc()` storage and initialized with `dpcpu_copy()`.
- With `VIMAGE`, `VNET_SETNAME` sections are copied into `vnet_data_alloc()` storage and initialized/saved through VNET helpers.
- `link_elf_propagate_vnets()` copies stored VNET data into all VNET instances.

## Filesystem / VM Relevance
This file combines vnode I/O (`vn_open()`, `vn_rdwr()`, `vn_close()`), MAC KLD authorization, kernel VM object allocation, wired mappings, page protections, and executable code loading. It is important for understanding how FreeBSD turns filesystem-resident KLD object files into live kernel text/data.

## Notable Edge Cases
- Non-allocated sections and relocation tables for non-allocated sections are ignored.
- Files with no allocated contents, invalid string tables, or anything other than exactly one symbol table are rejected.
- Constructor sections may be old `.ctors` or `SHT_INIT_ARRAY`; destructor sections may be `.dtors` or `SHT_FINI_ARRAY`.
- `debug.link_elf_obj_leak_locals` controls whether local symbols can participate in global module symbol resolution.
- On i386/amd64, IFUNC local relocations are performed after MD module load notification.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/link_elf_obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/linker_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/linker_if.m

## Purpose
Declares the FreeBSD kobj interface implemented by kernel linker classes. The `.m` file is an interface-definition source used to generate method dispatch glue for `struct linker_file` operations.

## Methods
- Symbol lookup: `lookup_symbol`, `lookup_debug_symbol`, `lookup_debug_symbol_ctf`.
- Symbol values and reverse lookup: `symbol_values`, `debug_symbol_values`, `search_symbol`.
- Function enumeration: `each_function_name`, `each_function_nameval`.
- Linker set lookup: `lookup_set`.
- Lifecycle: `unload`, static `load_file`, static `link_preload`, and `link_preload_finish`.
- CTF support: `ctf_get`, `ctf_lookup_typename`.
- Debug table export: `symtab_get`, `strtab_get`.
- VNET propagation hook: `propagate_vnets` when `VIMAGE` is enabled.

## Contract
Implementations return `ENOENT` for missing symbols/CTF data and zero on success. `load_file` should return zero without modifying the result when a class does not recognize the file type, and should set the result only after a recognized file is loaded.

## Implementations in This Group
`link_elf.c` implements this interface for ELF executable/shared-object style modules. `link_elf_obj.c` implements the same interface for ELF relocatable object modules. Both use these methods to integrate with the generic `kern_linker.c` subsystem.

## Filesystem / VM Relevance
The interface abstracts module loading from module storage. Filesystem-backed loaders implement `load_file`; preloaded-boot loaders implement `link_preload` and `link_preload_finish`; both expose loaded code/data for kernel debugging and VM/module lifecycle management.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/linker_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/msi_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/msi_if.m

## Purpose
Declares the kobj interface for MSI/MSI-X interrupt allocation, release, mapping, and optional IOMMU-domain setup. This is bus/controller glue used by interrupt controller and PCI/MSI providers.

## Methods
- `alloc_msi()` allocates a vector group for a child device with requested and maximum counts.
- `release_msi()` releases a vector group.
- `alloc_msix()` allocates a single MSI-X interrupt source.
- `release_msix()` releases a single MSI-X interrupt source.
- `map_msi()` produces the MSI message address/data pair for an interrupt source.
- `iommu_init()` optionally initializes an IOMMU domain for MSI remapping.
- `iommu_deinit()` tears down optional MSI IOMMU state.

## Defaults
The default `iommu_init()` sets the domain pointer to `NULL` and succeeds. The default `iommu_deinit()` is a no-op. Allocation, release, and mapping methods have no defaults here and must be supplied by implementations.

## Dependencies
The interface imports `<machine/bus.h>`, `<dev/iommu/iommu_msi.h>`, and forward-declares `struct intr_irqsrc`. It is intended for device/bus interrupt plumbing rather than process or filesystem code.

## Filesystem / VM Relevance
There is no direct filesystem behavior. Indirectly, storage and filesystem devices using MSI/MSI-X depend on this interrupt allocation path for device operation, and IOMMU MSI remapping can affect DMA/interrupt isolation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/msi_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/p1003_1b.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/p1003_1b.c

## Purpose
Implements common FreeBSD POSIX P1003.1B realtime syscall glue, especially POSIX priority scheduling syscalls when `_KPOSIX_PRIORITY_SCHEDULING` is configured. It also initializes POSIX.1B configuration values.

## Key Elements
- Defines `M_P31B`, the allocation type used by POSIX.1B support such as `ksched.c`.
- `syscall_not_present()` logs and returns `ENOSYS` for compiled-out runtime features.
- When priority scheduling is not configured, `SYSCALL_NOT_PRESENT_GEN()` stubs are generated for all `sched_*` syscalls.
- When configured, a global `struct ksched *ksched` is attached and `CTL_P1003_1B_PRIORITY_SCHEDULING` is marked as supported.
- Syscall handlers wrap kernel helpers for `sched_setparam`, `sched_getparam`, `sched_setscheduler`, `sched_getscheduler`, `sched_yield`, priority min/max, and round-robin interval.
- `p31binit()` attaches scheduler support and records `PAGESIZE`.

## Permission and Locking Model
Syscall handlers resolve `pid == 0` to the calling thread or use `pfind()` for target processes. They lock the target process while selecting `FIRST_THREAD_IN_PROC()` and calling kernel helpers. Kernel helpers assert the process lock and apply visibility/scheduling checks:
- `p_cansched()` for changing parameters.
- `p_cansee()` for reading parameters or intervals.
- `priv_check(..., PRIV_SCHED_SETPOLICY)` for `sched_setscheduler()`.

## Integration
The file delegates actual priority/policy conversion to `ksched.c`. It exposes kernel helper APIs such as `kern_sched_setparam()`, `kern_sched_getparam()`, `kern_sched_setscheduler()`, `kern_sched_getscheduler()`, `kern_sched_rr_get_interval()`, and `kern_sched_rr_get_interval_td()` for in-kernel callers.

## Notable Edge Cases
- The syscall layer copies `struct sched_param` from userland before locking target processes.
- `sched_yield()` directly calls `sched_relinquish(td)` rather than going through `ksched_yield()`.
- `sched_get_priority_max()` and `_min()` set `td_retval[0]` even though the helper may return an error.
- The fallback stubs are logged, which can reveal programs attempting optional POSIX realtime calls on unsupported kernels.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/p1003_1b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/pic_if.m -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/pic_if.m

## Purpose
Declares the kobj interface for programmable interrupt controllers (PICs). It defines the interrupt-controller operations used by machine-independent interrupt code to map, activate, bind, enable, disable, service, and route interrupts and IPIs.

## Methods
- Interrupt lifecycle: `activate_intr`, `deactivate_intr`, `setup_intr`, and `teardown_intr`.
- Interrupt routing/control: `map_intr`, `bind_intr`, `enable_intr`, and `disable_intr`.
- Post/pre handling callbacks: `post_filter`, `pre_ithread`, and `post_ithread`.
- Secondary CPU setup: `init_secondary`.
- Interprocessor interrupts: `ipi_send` and `ipi_setup`.

## Defaults
The file provides no-op defaults for activation/deactivation/setup/teardown and secondary initialization, default unsupported returns for `bind_intr` and `ipi_setup`, and a no-op default for `ipi_send`. Core methods such as `map_intr`, `enable_intr`, `disable_intr`, and post/pre interrupt hooks must be supplied by concrete PIC implementations.

## Dependencies
Includes bus, cpuset, resource, and interrupt headers. The interface passes `struct intr_irqsrc`, `struct resource`, and `struct intr_map_data` objects, leaving controller-specific interpretation to implementers.

## Filesystem / VM Relevance
There is no direct filesystem behavior. The interface matters to the kernel execution substrate that storage controllers and block devices rely on for interrupts, especially on SMP systems with interrupt affinity and IPIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/pic_if.m -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/posix4_mib.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/posix4_mib.c

## Purpose
Implements the FreeBSD POSIX.1B (`p1003_1b`) sysctl MIB values used by `sysconf(3)` and related consumers to discover realtime/POSIX feature support and limits.

## Key Elements
- `facility[]` stores configured POSIX.1B feature or limit values indexed by `CTL_P1003_1B_* - 1`.
- `facility_initialized[]` records whether each value has been explicitly set.
- `P1B_SYSCTL()` declares read-only integer sysctls under `_p1003_1b`.
- `P1B_SYSCTL_RW()` declares writable sysctls using `p31b_sysctl_proc()`.
- Declared nodes cover asynchronous I/O, mapped files, memory locking/protection, message passing, prioritized I/O, priority scheduling, realtime signals, semaphores, fsync, shared memory objects, synchronized I/O, timers, AIO limits, page size, signal queue limits, timer limits, and semaphore limits.
- `p31b_setcfg()`, `p31b_unsetcfg()`, `p31b_getcfg()`, and `p31b_iscfg()` are the kernel API for feature configuration.
- `p31b_set_standard()` marks always-supported features such as fsync, mapped files, shared memory objects, and page size.

## Sysctl Behavior
Most entries are read-only, capability-readable integer sysctls. `sem_nsems_max` is writable through `p31b_sysctl_proc()`, but only updates `facility[]` if the value was already initialized. Invalid facility indexes are rejected with `EINVAL`.

## Integration
`p1003_1b.c` and other POSIX realtime modules call `p31b_setcfg()` to advertise optional feature support and limits. Userland sees these values through the `_p1003_1b` sysctl namespace.

## Filesystem / VM Relevance
The file exposes feature flags for `fsync`, mapped files, memory protection, page size, and shared memory objects. These are not implementations of those features, but they are user-visible capability declarations relevant to filesystem and VM behavior.

## Notable Edge Cases
- The code keeps `_p1003_1b` as a top-level sysctl namespace because `OID_AUTO` was noted as incompatible with `sysconf(3)` lookup-by-number behavior.
- `p31b_unsetcfg()` does not validate the number before indexing, unlike `p31b_setcfg()` and readers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/posix4_mib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sched_4bsd.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sched_4bsd.c

## Purpose
Implements the classic FreeBSD 4BSD scheduler as a selectable `struct sched_instance`. It provides thread priority decay, run queue management, context-switch integration, SMP wakeup forwarding, priority lending, CPU affinity handling, idle thread behavior, and scheduler statistics/probes.

## Key Elements
- `struct td_sched` extends `struct thread` with 4BSD-specific scheduling state: `%cpu`, estimated CPU, CPU ticks, sleep time, remaining slice, flags, run queue pointer, and optional KTR thread name cache.
- Scheduler flags include `TDF_DIDRUN`, `TDF_BOUND`, `TDF_SLICEEND`, `TDP_RESCHED`, and `TSF_AFFINITY`.
- Global state includes `sched_lock`, `runq`, optional per-CPU run queues, `idle_cpus_mask`, `sched_tdcnt`, `realstathz`, and `sched_slice`.
- Sysctls expose `kern.sched.4bsd.quantum`, `kern.sched.4bsd.slice`, and SMP wakeup-forwarding controls.
- `sched_4bsd_instance` fills the scheduler operation table and is registered with `DECLARE_SCHEDULER(..., "4BSD", ...)`.

## Priority and CPU Accounting
The scheduler uses the traditional 4BSD `estcpu` decay model. `schedcpu()` runs once per second in a kernel process, walks all processes/threads, decays `%cpu` and `ts_estcpu`, tracks sleep time, and recomputes timeshare priorities. `sched_clock_tick()` updates current-thread CPU usage each stat tick, recomputes priority at estimator thresholds, and requests rescheduling when the time slice expires.

Timeshare priority is computed from:
- Base `PUSER`.
- Estimated CPU divided by `INVERSE_ESTCPU_WEIGHT`.
- Nice value weighted by `NICE_WEIGHT`.

## Run Queue Model
On UP, runnable threads go to the global `runq`. On SMP, threads with pinning, binding, or restricted affinity go to per-CPU queues; other threads go to the global queue. `sched_4bsd_choose()` compares the global queue with the current CPU's per-CPU queue and returns the best runnable thread, falling back to the idle thread.

## Context Switch and Lifecycle
- `sched_4bsd_init()` initializes thread0 scheduler state and `sched_lock`.
- `sched_4bsd_setup()` initializes `ccpu`, run queues, load accounting for thread0, and the private scheduler AST.
- `sched_4bsd_sswitch()` handles switch-out accounting, requeues still-running threads, chooses the next thread, performs tracing/hooks, calls `cpu_switch()`, and restores lock/accounting state.
- `sched_4bsd_fork_thread()`, `sched_4bsd_exit_thread()`, `sched_4bsd_fork_exit()`, `sched_4bsd_throw()`, and `sched_4bsd_ap_entry()` cover thread creation, exit, first run, final switch, and AP startup.
- Constructors/destructors are not relevant here; this is runtime scheduler machinery.

## Preemption, Priority Lending, and Sleep/Wakeup
- `maybe_preempt()` requests immediate preemption when a newly runnable thread outranks the current thread and preemption policy allows it.
- `maybe_resched()` defers rescheduling through `TDP_RESCHED` and a scheduler AST.
- `sched_4bsd_lend_prio()`, `sched_4bsd_unlend_prio()`, `sched_4bsd_lend_user_prio()`, and related helpers implement priority inheritance/lending behavior.
- `sched_4bsd_sleep()` resets sleep accounting and may temporarily assign sleep priority.
- `sched_4bsd_wakeup()` updates stale priorities after long sleeps, restores interrupt-thread base priority if needed, resets the time slice, and queues the thread.

## SMP Behavior
SMP support includes per-CPU run queues, load lengths, idle CPU masks, wakeup forwarding, remote CPU kicking, and CPU selection for affinity-restricted threads. `forward_wakeup()` can wake idle CPUs through `cpu_idle_wakeup()` or IPIs; `kick_other_cpu()` sends AST or preemption IPIs when a better-priority thread lands on another CPU's queue. `sched_pickcpu()` chooses the least-loaded allowed CPU, preferring the last CPU when valid.

## Instrumentation
The file emits KTR events, SDT probes (`change-pri`, enqueue/dequeue, on/off CPU, load changes, surrender), scheduler statistics for interrupt-thread demotions/preemptions, optional HWPMC hooks, optional hardware tracing hooks, and DTrace virtual-time switch hooks.

## Filesystem / VM Relevance
The file is not filesystem-specific. It is still relevant to filesystem research because VFS, storage, page daemon, and interrupt/workqueue threads are scheduled through this implementation when 4BSD is active. Run queue latency, priority lending, and interrupt-thread demotion can directly influence filesystem and block I/O responsiveness.

## Notable Edge Cases
- `INVERSE_ESTCPU_WEIGHT` is tuned for statclock frequencies around 100-256 Hz and scales with CPU count on SMP.
- `sched_4bsd_do_timer_accounting()` avoids accounting on halted/disabled HTT CPUs for 4BSD.
- Bound threads can force a voluntary switch when bound to a different CPU.
- Affinity updates may move run-queued threads to valid per-CPU queues or force running threads off disallowed CPUs.
- `sched_4bsd_find_l2_neighbor()` is a stub returning `-1`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sched_4bsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sched_shim.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sched_shim.c

## Purpose
Provides the scheduler dispatch shim that routes the public `sched_*` kernel API to the active runtime-selected scheduler instance. It also defines shared scheduler probes/statistics and sysctls describing scheduler selection and CPU topology.

## Key Elements
- `const struct sched_instance *active_sched` is the selected scheduler implementation.
- `DEFINE_SHIM*` macros generate IFUNC-backed public scheduler entry points that return the matching function pointer from `active_sched`.
- Shimmed functions cover load, round-robin interval, fork/exit, priority changes, sleep/wakeup, run queue operations, CPU binding/affinity, timer accounting, topology helpers, and scheduler initialization hooks.
- Scheduler SDT probes and scheduler statistics are defined here so all scheduler implementations share the same instrumentation names.
- DTrace virtual-time hook globals are defined under `KDTRACE_HOOKS`.
- `sched_name` defaults to `"ULE"` and can be overridden by the `kern.sched.name` tunable.

## Scheduler Selection
`sched_instance_select()` scans the `sched_instance_set` linker set for a name matching `sched_name`. If none matches, it selects the first compiled-in scheduler and copies that scheduler's name into `sched_name`. `schedinit()` panics if selection failed; otherwise it calls the selected scheduler's `init()`.

## Sysinit and Sysctl Behavior
- `sched_setup()` runs at `SI_SUB_RUN_QUEUE`, records CPU topology from `smp_topo()`, and calls `active_sched->setup()`.
- `sched_initticks()` runs after clocks initialize and calls `active_sched->initticks()`.
- `sched_schedcpu()` starts periodic scheduler CPU accounting near the end of boot.
- `kern.sched.name` reports the active scheduler name.
- `kern.sched.available` reports comma-separated names from the scheduler linker set.
- `kern.ccpu` exposes the CPU decay factor.
- `kern.sched.topology_spec` emits an XML-like CPU topology dump from `cpu_top`.

## Filesystem / VM Relevance
The file is not filesystem-specific, but it determines which scheduler implementation all kernel threads, filesystem workers, storage interrupts, and VFS callers run under. The topology sysctl is relevant when analyzing workload placement and I/O-worker CPU behavior.

## Notable Edge Cases
- If the configured scheduler name is unavailable but at least one scheduler is compiled in, the shim silently falls back to the first linker-set entry.
- CPU topology output handles `cpu_top == NULL` by returning a minimal empty group.
- The IFUNC shims assume `active_sched` has been selected before the generated public functions are used.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sched_shim.c -->