# Group Research: group_1266_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_makesyscalls_sh_sourc_781c044e8d0e

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` source tree. All eight listed source files are recorded in the research manifests for this group and were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/makesyscalls.sh -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/makesyscalls.sh

Read completely: 1277 lines.

Generates NetBSD syscall interface artifacts from a configured `syscalls.master`-style input file. The shell wrapper sources a config file, validates numeric settings such as `nsysent` and `maxsysargs`, prepares temporary output fragments, normalizes input with `sed`, and then runs a large embedded `awk` program that parses syscall table rows and emits C headers, switch tables, names arrays, autoload metadata, DTrace syscall-provider helpers, and rump syscall marshalling code.

Configuration contract:
- Required or expected config variables include `sysnames`, `sysnumhdr`, `syssw`, `sysautoload`, `sysarghdr`, `systrace`, `compatopts`, `switchname`, `namesname`, `constprefix`, `emulname`, `registertype`, `nsysent`, `sysalign`, and rump output paths.
- Defaults include `sys_nosys=sys_nosys`, `maxsysargs=8`, and `/dev/null` outputs for optional systrace/autoload/rump files.
- `addsuffix()` preserves `/dev/null` targets while deriving fragment filenames for normal outputs.

Input processing and parser behavior:
- The pre-awk `sed` pass strips dollar signs, joins backslash-continued lines, and inserts spaces around `{}`, `()`, `*`, `|`, and commas for easier token parsing.
- The awk script tracks syscall numbers, conditional nesting, and compatibility wrappers; it reports hard errors for out-of-sync syscall numbers, malformed prototypes, unbalanced preprocessor conditionals, and unknown syscall keywords.
- `parseline()` handles row modifiers including `INDIR`, `MODULAR`, `RUMP`, syscall aliases, compatibility suffixes, return type, function prefix/base name, fixed arguments, varargs, and padding/alignment expectations.
- Keywords routed to full entries include `STD`, `NODEF`, `NOARGS`, `INDIR`, `NOERR`, `EXTERN`, and configured compatibility keywords. `OBSOL`, `UNIMPL`, `EXCL`, and `IGNORED` produce filler or nullop/nosys entries.

Generated kernel/user artifacts:
- `sysnumhdr` receives syscall number macros, max argument macros, prototype comments used by libc lint stub generation, and final `MAXSYSCALL`/`NSYSENT` definitions.
- `sysarghdr` receives `syscallarg` ABI wrapper definitions, argument structures, compile-time size checks, and syscall prototypes.
- `syssw` receives `struct sysent` entries with argument counts, byte sizes, function pointers, and flags such as indirect, pointer-argument, 64-bit argument, 64-bit return, wide-return, and modular-autoload markers.
- `sysnames` receives both kernel-visible include handling and userland-friendly primary/alternate syscall names arrays.
- `sysautoload` receives `struct sc_autoload` entries for modular syscalls and terminates with a `{ 0, NULL }` sentinel.

Rump and tracing generation:
- Rump output includes syscall wrappers, public/renamed prototypes, `rump_sysent`, `rump_sysent_nomodbits`, `rumpns_sysent` aliasing, and a syscall map file.
- Rump wrappers convert user-facing arguments into generated syscall argument structures using endian-sensitive `SPARG`, issue `rumpclient_syscall` or `rump_syscall`, translate errno, and reconstruct return values from `register_t retval[2]`.
- The `pipe` syscall is handled specially because it returns two file descriptors through `retval`.
- DTrace output includes `systrace_args`, entry argument descriptions, and return argument descriptions. Pointer-like types are cast appropriately for register-array extraction.

Compatibility and ABI details:
- Compatibility wrappers are generated from `compatopts` with preprocessor-controlled macros that either call the compatibility function namespace or `sys_nosys`.
- `uncompattypes` maps selected old ABI structure names such as `timeval50`, `timespec50`, `stat30`, and `kevent100` to modern public rump prototype types.
- `isarg64()` and `isretwide()` encode syscall dispatch metadata for 64-bit arguments and ABIs that need careful sign extension of 32-bit results on wide registers.
- The script enforces optional 64-bit argument alignment for `off_t`, `dev_t`, and `time_t`, with an explicit exception for `sys_posix_fadvise`.

Risks and notes:
- This is build-critical generated-code infrastructure; parse errors or config variable mistakes can corrupt multiple generated ABI surfaces at once.
- The parser is whitespace/token sensitive after the custom `sed` preprocessing pass, so unusual type syntax can break generation unless it matches the expected grammar.
- Allocation-size checks depend on `maxsysargs` and generated `check_syscall_args`; invalid syscall signatures can fail at generation time or compile time.
- Rump syscall generation assumes integral return types and has special-case compatibility behavior, so new syscall types may require script changes.
- Temporary files are removed by a trap, but generation writes many partial outputs before final concatenation; interrupted or failed builds should rely on the build system to avoid stale generated files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/makesyscalls.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sched_4bsd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sched_4bsd.c

Read completely: 569 lines.

Implements the NetBSD 4.4BSD-style scheduler policy hooks. It plugs into the machine-independent scheduler framework with priority decay, round-robin tick handling, nice-value updates, fork/exit CPU accounting, and sysctl exposure of scheduler name and round-robin quantum.

Core scheduling model:
- The central metric is `l_estcpu`, a fixed-point estimate of recent CPU usage.
- `sched_schedclock()` increments `l_estcpu` for running `SCHED_OTHER` LWPs by `ESTCPU_ACCUM`, clamps with `ESTCPULIM`, and recalculates priority.
- `sched_pstats_hook()` decays `l_estcpu` once per scheduler statistics interval unless the LWP slept long enough to defer recalculation until wakeup.
- `updatepri()` applies batched decay for LWPs that slept more than one second before becoming runnable.
- `resetpriority()` computes time-sharing priority from `l_estcpu` and process nice value, then calls `lwp_changepri()` when the priority changes.

Decay and priority math:
- The file documents the classic BSD load-dependent decay formula: decay is approximately `(2 * loadavg) / (2 * loadavg + 1)`.
- `decay_cpu()` performs the fixed-point decay and avoids 64-bit arithmetic on non-LP64 when the multiplication is known safe.
- `decay_cpu_batch()` repeatedly applies decay for sleep intervals, with a shortcut that returns zero after sufficiently long sleeps relative to load.
- `ESTCPU_SHIFT`, `ESTCPU_MAX`, and `ESTCPU_ACCUM` bound how much recent CPU use can influence priority; comments explain the split between estimated CPU history and nice levels.

Round-robin and preemption behavior:
- `sched_tick()` runs every `sched_rrticks` hardclock ticks, defaulting to about 100 ms.
- Idle CPUs are asked to reschedule immediately.
- `SCHED_FIFO` threads are not time-sliced.
- `SCHED_RR` threads are forced toward `mi_switch()` by requesting a reschedule at real-time kernel priority.
- Normal threads first set `SPCF_SEENRR`, then `SPCF_SHOULDYIELD`, and finally can be forced into kernel preemption if they remain stuck in kernel code across intervals.
- On SMT or asymmetric systems, non-first-class CPUs push harder to find a better CPU for the LWP.

Process/LWP lifecycle hooks:
- `sched_nice()` updates `p_nice` under `p_lock` and recalculates all LWPs in the process.
- `sched_proc_fork()` records the parent's first LWP `l_estcpu` and current scheduler tick in the child process.
- `sched_proc_exit()` charges excess child CPU history back to the parent after decaying the inherited estimate from fork time.
- `sched_lwp_fork()` copies `l_estcpu` to the new LWP.
- `sched_lwp_collect()` adds a collected LWP's `l_estcpu` back to the current LWP.
- Hooks such as `sched_wakeup()`, `sched_slept()`, `sched_oncpu()`, and `sched_newts()` are present but no-op for this policy.

Sysctl integration:
- `SYSCTL_SETUP(sysctl_sched_4bsd_setup, ...)` creates `kern.sched`.
- Exposes `kern.sched.name` as `4.4BSD`.
- Exposes `kern.sched.rtts`, reporting the round-robin interval in milliseconds through `sysctl_sched_rtts()`.

Risks and notes:
- Priority recalculation assumes caller-side locking: many functions assert `lwp_locked(l, NULL)` or `p_lock` ownership.
- `sched_tick()` relies on careful locking around `spc_lock()` and comments note possible interruption of priority-inheritance trylock paths.
- Parent chargeback in `sched_proc_exit()` only uses the first LWP of each process and has an old `XXX` about init-parent handling.
- The decay model favors interactive/sleeping threads by design; changes to fixed-point constants can alter system-wide scheduling behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sched_4bsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sched_m2.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sched_m2.c

Read completely: 468 lines.

Implements the NetBSD M2 scheduler policy hooks. Compared with `sched_4bsd.c`, this scheduler is centered on priority-indexed time slices and priority boosting/penalizing rather than an explicit recent-CPU fixed-point estimator.

Core scheduler state:
- `min_ts`, `max_ts`, and `sched_rrticks` hold minimum time-sharing quantum, maximum time-sharing quantum, and real-time round-robin quantum.
- `ts_map[PRI_COUNT]` maps effective priority to time slice length.
- `high_pri[PRI_COUNT]` maps time-sharing priorities to boosted priorities used after sleeps or starvation.
- `PRI_HIGHEST_TS` defines the top time-sharing priority; priorities above it are treated as real-time.

Initialization:
- `sched_rqinit()` requires `hz >= 100`, sets defaults of about 20 ms minimum time slice, 150 ms maximum time slice, and 100 ms round-robin real-time slice, then calls `sched_precalcts()`.
- `sched_precalcts()` fills `ts_map` so lower numerical time-sharing priorities get larger time slices, and fills `high_pri` for boost behavior.
- Initial `lwp0` setup is partly marked `notyet`; current code directly assigns `lwp0.l_sched.timeslice` from `ts_map`.

Priority and time-slice behavior:
- `sched_newts()` sets an LWP's time slice from `ts_map[lwp_eprio(l)]`.
- `sched_nice()` stores the new process nice value and shifts `SCHED_OTHER` LWP priorities by a coarse nice-derived delta.
- `sched_slept()` rewards non-batch sleeping time-sharing threads by increasing their priority, with special handling for negative nice values.
- `sched_wakeup()` boosts threads that slept at least one second using `high_pri`.
- `sched_pstats_hook()` penalizes repeated CPU-bound batch behavior by lowering priority, and can boost runnable threads that have not run for at least a second.
- `sched_oncpu()` loads the per-CPU scheduler tick counter from the LWP's current time slice.

Tick handling:
- `sched_tick()` runs with the current LWP lock held.
- `SCHED_FIFO` threads reset their time quantum and keep running.
- `SCHED_OTHER` threads have priority decreased numerically on quantum expiration, with positive nice values causing larger decreases.
- If the effective priority is no better than the CPU's maximum runnable priority or a target CPU migration exists, the thread is marked `SPCF_SHOULDYIELD` and the CPU is rescheduled.
- Otherwise the same LWP continues with a refreshed time slice.

Lifecycle hooks:
- `sched_proc_fork()` walks child LWPs and recalculates their time slices.
- `sched_proc_exit()`, `sched_lwp_fork()`, `sched_lwp_collect()`, `sched_setrunnable()`, and `sched_schedclock()` are no-op hooks for this policy.

Sysctl integration:
- `SYSCTL_SETUP(sysctl_sched_m2_setup, ...)` creates `kern.sched`.
- Exposes `kern.sched.name` as `M2`.
- Exposes read-only `rtts` and read-write `maxts`/`mints` in milliseconds.
- `sysctl_sched_mints()` and `sysctl_sched_maxts()` validate new values, lock every CPU scheduler state, update the global quantum, recalculate maps, and unlock CPUs.

Risks and notes:
- The file still carries TODOs for fair-share queue implementation and NUMA support.
- Updating `min_ts`/`max_ts` takes all CPU scheduler locks and assumes the lock ordering is safe in the shown loop.
- Several hooks are intentionally empty, so this policy depends more heavily on tick/wakeup/sleep transitions than per-hardclock CPU accounting.
- Nice handling is coarse, based on shifts around `NZERO`, and directly mutates priorities for time-sharing LWPs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sched_m2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_acl_nfs4.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_acl_nfs4.c

Read completely: 620 lines.

Provides shared utility routines for filesystems implementing NFSv4 ACLs. The file supports both kernel builds and a libc-oriented non-kernel build path for trivial ACL construction used by ACL library helpers.

Core helpers:
- `_acl_append()` appends an ACL entry with a tag, permissions, entry type, undefined ID, and zero flags.
- `acl_nfs4_trivial_from_mode()` builds a trivial ACL from a POSIX mode using the PSARC/2010/029-compatible inherited ACL algorithm.
- `acl_nfs4_sync_acl_from_mode()` is the kernel entry point for rebuilding an ACL from mode bits; the current `file_owner_id` parameter is unused.
- `__acl_nfs4_trivial_from_mode_libc()` exposes the trivial-mode builder to libc when `_KERNEL` is not defined.

Mode reconstruction:
- `__acl_nfs4_sync_mode_from_acl()` walks non-inherit-only ALLOW/DENY ACEs and derives user/group/other read, write, and execute mode bits.
- It handles `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, and `ACL_EVERYONE`; `ACL_EVERYONE` can populate still-unseen user, group, and other bits.
- First-seen semantics matter: a permission bit is marked seen whether an ALLOW or DENY entry caused it; only ALLOW adds the corresponding mode bit.
- Non-permission bits preserved by `ACL_PRESERVE_MASK` are copied from the original mode.

Inheritance:
- `acl_nfs4_inherit_entries()` copies inheritable non-owner/group/everyone ACEs from a parent ACL into a child ACL.
- It filters by `ACL_ENTRY_FILE_INHERIT`, `ACL_ENTRY_DIRECTORY_INHERIT`, object type, and `ACL_ENTRY_NO_PROPAGATE_INHERIT`.
- Inherited entries are marked `ACL_ENTRY_INHERITED` and generally have `ACL_ENTRY_INHERIT_ONLY` cleared unless directory/file inheritance rules require it.
- ALLOW entries that apply to the new object have permissions masked: some permissions are never inherited, and read/write/execute data permissions are limited according to group mode bits.

PSARC-style ACL construction:
- `acl_nfs4_compute_inherited_acl_psarc()` derives base `user_allow`, `group_allow`, and `everyone_allow` permission masks from the requested mode.
- It grants common metadata permissions to all three classes and adds write-owner/ACL/attribute permissions to the owner.
- It computes owner and group DENY entries needed to prevent broader group/everyone permissions from exceeding narrower owner/group permissions.
- It optionally appends inherited parent ACEs before appending final owner, group, and everyone ALLOW ACEs.
- `acl_nfs4_compute_inherited_acl()` is the kernel wrapper around this PSARC-compatible implementation.

Triviality and validation:
- `_acls_are_equal()` compares ACL count and all ACE fields exactly.
- `acl_nfs4_is_trivial()` computes mode from the ACL, rebuilds a trivial ACL from that mode, and compares for equality; it immediately rejects ACLs with more than six entries.
- `acl_nfs4_check()` validates count, tag/id combinations, allowed NFSv4 permission bits, ALLOW/DENY entry types, allowed flags, unsupported audit/alarm flags, and inheritance flags on non-directories.

Risks and notes:
- Several commented-out helpers and comments reference alternate canonical-six trivial ACL logic, but the implemented triviality check only returns the PSARC comparison result.
- ACL validity is intentionally permissive about multiple or missing owner/group/everyone entries because NFSv4 permits more flexible ACL forms.
- `file_owner_id` is currently unused in exported functions, so owner-specific inheritance policy is not represented here.
- `__acl_nfs4_sync_mode_from_acl()` depends on ACE order; reordering semantically similar ACLs can change reconstructed mode bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_acl_nfs4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_acl_posix1e.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_acl_posix1e.c

Read completely: 341 lines.

Provides shared POSIX.1e ACL utility routines for filesystems. It converts between inode mode bits and ACL entries, validates POSIX.1e ACL structure, and combines creation modes with default ACLs for new files.

Mode-to-ACL helpers:
- `acl_posix1e_mode_to_perm()` maps `S_IRWXU`, `S_IRWXG`, or `S_IRWXO` bits to `ACL_READ`, `ACL_WRITE`, and `ACL_EXECUTE` according to the requested tag.
- `acl_posix1e_mode_to_entry()` builds a base ACL entry for `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, or `ACL_OTHER`, filling the owner uid, group gid, or undefined ID as appropriate.
- Invalid tags are reported with `printf()` and return an empty/undefined entry rather than panicking.

ACL-to-mode helpers:
- `acl_posix1e_perms_to_mode()` converts three relevant ACL entries back into user/group/other mode bits.
- `acl_posix1e_acl_to_mode()` finds `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, `ACL_OTHER`, and optional `ACL_MASK` entries in a complete ACL.
- If `ACL_MASK` exists, its permissions replace group bits in the resulting mode, matching POSIX.1e behavior.
- Missing required base entries or unknown tags cause `panic()`, reflecting the expectation that callers validate ACLs first.

Validation:
- `acl_posix1e_check()` verifies `acl_cnt <= ACL_MAX_ENTRIES`.
- It requires exactly one `ACL_USER_OBJ`, exactly one `ACL_GROUP_OBJ`, exactly one `ACL_OTHER`, and zero or one `ACL_MASK`.
- If any named `ACL_USER` or `ACL_GROUP` entries are present, exactly one `ACL_MASK` must be present.
- Named user/group entries must have defined IDs; base entries and mask are forced to `ACL_UNDEFINED_ID` before checking.
- Permissions must be limited to `ACL_PERM_BITS`, and tags outside the POSIX.1e set are rejected with `EINVAL`.

New-file mode composition:
- `acl_posix1e_newfilemode()` preserves non-ACL mode bits through `ACL_PRESERVE_MASK`.
- It applies the current policy that a permission bit must be present both in the requested creation mode and in the default ACL-derived mode to survive.
- It reconstructs affected permission bits with `ACL_OVERRIDE_MASK & cmode & acl_posix1e_acl_to_mode(dacl)`.

Risks and notes:
- `acl_posix1e_check()` mutates `ae_id` for base and mask entries while validating, which is surprising for a function named as a checker.
- `acl_posix1e_acl_to_mode()` panics on malformed ACLs; callers must run validation before using it on untrusted ACL data.
- The validator explicitly does not check uniqueness of named user/group qualifier IDs.
- Default ACL composition does not take a separate process umask argument here; comments note that may eventually be pushed into per-filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_acl_posix1e.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_asan.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_asan.c

Read completely: 1306 lines.

Implements NetBSD's kernel AddressSanitizer support glue. It provides shadow-memory mapping and poisoning helpers, access checking and reports, wrappers around memory/string/copy/atomic/bus/DMA operations, global registration handling, and compiler ASan ABI entry points.

Initialization and shadow mapping:
- `kasan_shadow_map()` maps shadow pages for a kernel address range after translating through machine-dependent `kasan_md_addr_to_shad()`.
- `kasan_early_init()` delegates early setup to `kasan_md_early_init()`.
- `kasan_init()` runs machine-dependent initialization, flips `kasan_enabled`, and calls compiler-generated ASan constructors from `__CTOR_LIST__` to `__CTOR_END__`.
- `kasan_softint()` marks an LWP uarea/stack region valid when used for soft interrupt context.
- The file includes `<machine/asan.h>` for MD constants and helpers, and enforces supported compiler ASan ABI versions.

Poisoning and validation:
- `kasan_add_redzone()` rounds allocation sizes to the shadow scale and appends one shadow-scale redzone.
- `kasan_mark()` marks the valid prefix of an allocation and poisons the redzone suffix with a caller-provided code.
- `kasan_shadow_Nbyte_fill()` fills shadow bytes with a poison code after alignment and unsupported-address checks.
- `kasan_shadow_1byte_markvalid()` and `kasan_shadow_Nbyte_markvalid()` make byte ranges addressable, including partial shadow-byte handling.
- Fast validators exist for 1, 2, 4, and 8-byte accesses, falling back to byte-by-byte validation for other sizes or boundary-crossing accesses.
- `kasan_shadow_check()` gates checks on `kasan_enabled`, DDB recovery state, zero size, and unsupported MD ranges, then calls `kasan_report()` on invalid access.

Reporting:
- `kasan_code_name()` maps poison codes to labels such as generic redzone, malloc/kmem/pool redzone, pool use-after-free, stack left/middle/right, use-after-return, and use-after-scope.
- `kasan_report()` prints or panics depending on `KASAN_PANIC`, includes access address, program counter, byte size, read/write direction, and poison label, then invokes `kasan_md_unwind()`.

Wrapped memory and user-copy APIs:
- `kasan_memcpy()`, `kasan_memmove()`, `kasan_memcmp()`, `kasan_memset()`, `kasan_strcpy()`, `kasan_strcmp()`, `kasan_strlen()`, `kasan_strcat()`, `kasan_strchr()`, and `kasan_strrchr()` check source and/or destination ranges before delegating to builtins.
- `kasan_kcopy()`, `kasan_copyin()`, `kasan_copyinstr()`, and `kasan_copyoutstr()` check only kernel buffers where appropriate before calling the underlying kernel copy routines.
- `_ucas_*` and `_ufetch_*` wrappers check kernel result/output buffers before invoking machine/user access primitives.

Atomic, bus, and DMA instrumentation:
- Macro families generate wrappers for add, and, or, compare-and-swap, swap, decrement, and increment atomic operations across 32-bit, 64-bit, int, long, uint, ulong, and pointer forms.
- Atomic wrappers validate the target memory as writable for the operation size before calling the original atomic primitive.
- When `__HAVE_KASAN_INSTR_BUS` is defined, macro families wrap bus-space read/write multi/region and stream variants for 1, 2, 4, and 8-byte element sizes.
- `kasan_dma_load()` records the buffer pointer, length, and buffer type in a DMA map.
- `kasan_dma_sync()` validates DMA buffers for linear buffers, mbuf chains, or kernel-space uios, using the sync operation flags to decide read/write direction; raw buffers are skipped.

Compiler ASan ABI:
- `__asan_register_globals()` poisons global-variable redzones according to compiler-provided descriptors.
- `__asan_unregister_globals()` is present but intentionally does nothing.
- `__asan_load{1,2,4,8,16}` and `__asan_store{1,2,4,8,16}` plus `_noabort` variants call `kasan_shadow_check()`.
- `__asan_loadN` and `__asan_storeN` handle dynamic sizes.
- `__asan_set_shadow_*` routines fill shadow memory with specific poison bytes.
- `__asan_poison_stack_memory()`, `__asan_unpoison_stack_memory()`, `__asan_alloca_poison()`, and `__asan_allocas_unpoison()` implement stack and alloca redzone ABI hooks.
- `__asan_handle_no_return()` is a no-op in this kernel implementation.

Risks and notes:
- Many helpers assert shadow-scale alignment and size multiples; callers that poison allocator memory must honor KASAN alignment contracts.
- `kasan_shadow_check()` suppresses checks while DDB recovery is active to avoid recursive faults in debugger paths.
- DMA uio checking skips non-kernel vmspaces, so user-space DMA buffers are not shadow-validated here.
- Bus write wrappers mark source buffers as `write` in their checks even though CPU-side access is a read from the source buffer; this reflects existing code and should be reviewed carefully before changing because poison semantics may be intentional or historical.
- The file deliberately uses `#undef` to bypass macro interposition and call original primitives; include/order changes can break wrapper binding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_asan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_autoconf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_autoconf.c

Read completely: 4041 lines.

Implements NetBSD's machine-independent device autoconfiguration core. It manages configured driver/attachment/cfdata tables, device allocation and naming, matching and attachment, deferred configuration queues, detach/shutdown/deactivation, device lookup and lifetime references, compatible-string matching, power-management registration and locking, activity handlers, and safe iteration over the live device tree.

Global configuration state:
- Static ioconf exports `cfdata` and `cfroots`; the file keeps all loaded cfdata tables in `allcftables`.
- `allcfdrivers` tracks all registered `cfdriver` structures, and `allcfattachiattrs` tracks rare attachment-provided interface attributes.
- `alldevs` is the global device list guarded by `alldevs_lock`, with generation counters and reader/writer counters to support iteration while detaching.
- `config_misc_lock` and `config_misc_cv` protect pending attach/detach state, deferred queues, and device reference draining.
- Autoconfiguration timings are mixed into the entropy pool through `rnd_autoconf_source`.

Driver, attachment, and cfdata management:
- `config_init()` initializes locks, callouts, built-in drivers and attachments, the initial cfdata table, and the autoconf entropy source.
- `config_init_component()` and `config_fini_component()` add/remove module-provided driver, attachment, and cfdata sets with rollback on failure.
- `config_cfdriver_attach()` rejects duplicate driver names and inserts into `allcfdrivers`; `config_cfdriver_detach()` refuses removal while instances or attachments remain.
- `config_cfattach_attach_iattrs()` attaches a `cfattach` to a driver and records its interface attributes; detach refuses removal while any live device uses the attachment.
- `config_cfdata_attach()` adds supplemental cfdata and optionally rescans existing parents; `config_cfdata_detach()` detaches all devices backed by that cfdata before removing it.

Matching and searching:
- `config_match()` and `config_probe()` invoke a candidate attachment's match routine.
- `config_stdsubmatch()` compares locators for an interface attribute before calling `config_match()`.
- `cfdriver_get_iattr()`, `cfattach_get_iattr()`, `device_get_iattr()`, and `cfiattr_lookup()` resolve interface attribute descriptors.
- `cfparent_match()` verifies that a candidate parent device supports the required interface attribute and optional specific parent name/unit.
- `config_search_internal()` scans all cfdata tables for eligible children, filters by found-state and interface attribute, invokes submatch/default match, and returns the best-priority candidate.
- `config_rootsearch()` searches root cfdata entries from `cfroots`.

Attachment and device allocation:
- `cfargs_canonicalize()` validates and normalizes `struct cfargs`, enforcing mutually exclusive submatch/search callbacks.
- `config_devalloc()` allocates the device structure and driver private storage, assigns a unit, builds `dv_xname`, initializes the PMF lock/CV, copies locators, creates the property dictionary, initializes localcount references, and records interface attributes in properties.
- `config_unit_alloc()` uses `config_makeroom()` to grow `cd_devs` arrays as needed under the global device lock.
- `config_attach_internal()` links the device, marks cfdata found, prints attach messages, registers the device, sends devmon attach events, prevents detach during attach/deferred work, calls the driver's attach routine, clears `dv_attaching`, runs deferred config for the parent, and returns a referenced device.
- `config_found_acquire()`, `config_attach_acquire()`, and `config_attach_pseudo_acquire()` are reference-returning APIs; legacy `config_found()`, `config_attach()`, and `config_attach_pseudo()` immediately release the returned reference.
- `config_rootfound()` attaches root devices.

Deferred and final configuration:
- `config_defer()` queues callbacks until the parent finishes attaching all children.
- `config_interrupts()` queues callbacks until interrupts are enabled, with worker threads created by `config_create_interruptthreads()`.
- `config_mountroot()` queues callbacks until after root mount, with joinable mountroot threads created/finalized by `config_create_mountrootthreads()` and `config_finalize_mountroot()`.
- `config_pending_incr()` and `config_pending_decr()` maintain per-device pending counters and the global pending list.
- `config_finalize_register()` stores iterative finalizers until finalization; if finalization already happened it runs the callback immediately until it makes no more progress.
- `config_finalize()` waits for pending deferred work, attaches pseudo-devices, runs finalizers to quiescence, releases finalizer records, handles boot twiddle state, and reports hardware detection errors.

Detach, shutdown, and deactivation:
- `config_detach_enter()` waits for attach/deferred work and any competing detach, then marks the current LWP as detaching.
- `config_detach_release()` calls the driver's detach routine, handles forced-detach panic semantics, commits detach if the driver did not, clears active state, drains `device_lookup_acquire()` references, notifies userland, checks for children under DIAGNOSTIC, notifies the parent, updates cfdata found-state, and unlinks or garbage-marks the device.
- `config_detach_commit()` is an idempotent signal from a driver detach routine that future device lookups should fail promptly.
- `config_detach_children()` detaches direct children.
- `config_detach_all()` iterates active devices leaves-first for shutdown unless reboot flags skip detach.
- `config_deactivate()` walks descendants root-first and invokes `ca_activate(..., DVACT_DEACTIVATE)` under `splhigh()`.
- `config_collect_garbage()` and `config_dump_garbage()` defer actual device memory destruction until no readers/writers are iterating the device list.

Device lookup, references, and iteration:
- `device_lookup()` is non-sleeping and safe up to IPL_VM, but returns an unreferenced device that callers must know is stable.
- `device_lookup_acquire()` sleeps until attach/detach state stabilizes and returns a reference acquired through `localcount`.
- `device_acquire()` and `device_release()` manage per-device localcount references.
- `device_find_by_xname()` and `device_find_by_driver_unit()` search by external name or driver/unit.
- `deviter_init()`, `deviter_next()`, and `deviter_release()` provide generation-based iteration over devices, supporting normal, read-write, shutdown, root-first, and leaves-first traversal modes.
- Iterators maintain `alldevs_nread`/`alldevs_nwrite` to prevent immediate reclamation of detached device structures.

Compatible matching:
- String-array helpers implement exact and `pmatch(9)` pattern matching.
- `device_compatible_match()` and `device_compatible_pmatch()` rank matches by the position of the matched device compatible string.
- String-list variants support OpenFirmware-style NUL-separated compatible lists.
- ID variants match integer IDs against `device_compatible_entry` arrays with a sentinel.
- Lookup variants return the matching `device_compatible_entry` rather than just a score.

Power management and activity:
- Driver, bus, and class PMF registration stores suspend/resume/shutdown callbacks and private data on the device.
- Suspend/resume is layered: class, driver, and bus flags gate each other so deeper layers suspend/resume in the intended order.
- `device_pmf_lock()`/`device_pmf_unlock()` serialize PMF operations, allow recursive locking by the same LWP, and wake waiters during deregistration.
- `device_pmf_driver_deregister()` clears power handler state and waits until outstanding PMF locks/waiters drain.
- Activity handlers can be dynamically registered and deregistered; `device_active()` invokes them for device activity events.

Userland and sysctl integration:
- `devmon_report_device()` emits property-dictionary attach/detach events through `devmon_insert_vec` when drvctl/devmon is present.
- Device property dictionaries include driver, unit, parent, and interface attribute locator descriptions.
- `sysctl_detach_setup()` creates writable `kern.detachall` to control shutdown detach behavior.
- Boot `twiddle` support provides progress feedback for silent boot modes.

Risks and notes:
- Device lifetime is subtle: legacy APIs return unreferenced `device_t` values and rely on the kernel lock as a fragile race defense, while newer acquire APIs require explicit `device_release()`.
- Comments explicitly note that not all detach callers hold the iterator/read-write protection needed to avoid use-after-free races.
- `config_makeroom()` drops and reacquires `alldevs_lock` around sleeping allocation; callers must re-check state after it returns.
- Forced detach panics if a driver refuses or fails detach, so driver detach callbacks must distinguish removable-hardware force paths carefully.
- PMF deregistration intentionally wakes and waits on PMF lock holders; incorrect lock ordering around device PMF locks can deadlock suspend/resume paths.
- `device_pmf_driver_shutdown()` and `device_pmf_bus_shutdown()` dereference function pointer slots in a way that assumes callback storage is initialized consistently.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_autoconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_blist.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_blist.c

Read completely: 1142 lines.

Implements a wired-memory bitmap block allocator using a radix tree with hints and collapsed all-free/all-allocated states. It is designed for contexts such as swap allocation where allocation and free operations must not allocate memory after initialization. The file can also be built standalone for debugging outside the kernel.

Data structures:
- `struct blist` records total managed blocks, root radix coverage, root skip distance, free block count, root metadata pointer, and number of metadata records allocated.
- `blmeta_t` is each radix-tree node. It stores either available-block count for meta nodes or a bitmap for leaves, plus `bm_bighint`, the largest-known contiguous free range hint.
- Leaf nodes cover `BLIST_BMAP_RADIX` blocks; meta nodes branch by `BLIST_META_RADIX` (16).
- The radix tree is stored in a linear array. Children immediately follow parent nodes, and `skip` values let recursion jump between child subtrees.
- A `bm_bighint` value of `(blist_blkno_t)-1` marks an out-of-range terminator for trees whose allocated metadata is smaller than the theoretical root radix.

Public API:
- `blist_create()` computes the minimal root radix/skip covering the requested block count, allocates the `struct blist`, calculates exact metadata needs by calling `blst_radix_init(NULL, ...)`, allocates metadata, initializes the tree, and returns the allocator.
- `blist_destroy()` frees the metadata array and allocator structure.
- `blist_alloc()` allocates a contiguous run and decrements `bl_free` on success; failures return `BLIST_NONE`.
- `blist_free()` frees a range and increments `bl_free`, panicking on detected inconsistencies.
- `blist_fill()` marks a range allocated regardless of current state and returns how many blocks were actually free before the fill.
- `blist_resize()` creates a new allocator, copies free-space state from the old tree, optionally frees newly added space, and destroys the old allocator.
- Under `BLIST_DEBUG`, `blist_print()` and a standalone `main()` provide interactive test commands for allocate/free/fill/resize/print.

Allocation internals:
- `blst_leaf_alloc()` handles leaf bitmaps. The one-block case uses a binary mask search; multi-block allocation scans for a contiguous set of free bits.
- `blst_meta_alloc()` handles meta nodes, respecting all-allocated and all-free collapsed states.
- When descending from an all-free meta node, `blst_meta_alloc()` lazily initializes child nodes before continuing.
- Allocation relies on `bm_bighint` to skip subtrees that cannot satisfy the request.
- On allocation failure, bighints are lowered to avoid repeating impossible searches.
- The allocator cannot allocate more than `BLIST_BMAP_RADIX` blocks per call; larger requests can panic in meta allocation.

Freeing and filling:
- `blst_leaf_free()` computes a bitmap mask for the freed range and panics if any target bit is already free.
- `blst_meta_free()` updates available counts, handles all-allocated/all-free collapsed states, recursively splits arbitrary free ranges across children, and expands bighints as children become freer.
- `blst_leaf_fill()` clears bits for a requested range and counts how many were previously free.
- `blst_meta_fill()` recursively allocates a specific range, supports all-allocated/all-free collapsed states, and decrements available counts by the number of newly filled blocks.

Copying and initialization:
- `blst_copy()` transfers free-space state from one radix tree to another by freeing corresponding ranges in the destination for every free range found in the source.
- It handles all-allocated, all-free, partial meta, and leaf bitmap cases.
- `blst_radix_init()` initializes leaves and meta nodes as all allocated, and inserts terminator nodes beyond the requested block count.
- `blst_radix_init()` is also used in sizing mode with `scan == NULL`, returning how many metadata records are required.

Standalone/debug mode:
- Outside `_KERNEL`, the file maps `kmem_alloc`, `kmem_zalloc`, and `kmem_free` to libc allocation routines, includes a local `panic()` implementation, and enables `BLIST_DEBUG` unless disabled.
- The debug CLI supports `a` allocate, `f` free, `l` fill, `r` resize, `p` print, and help commands.

Risks and notes:
- The implementation is not internally synchronized; callers must serialize access to a `blist_t`.
- `blist_create()` has comments noting unchecked arithmetic overflow while growing radix/skip.
- `blist_alloc()` does not explicitly validate `count` before reaching lower-level routines; oversized allocations can panic.
- `blist_resize()` assumes `*pbl` is a valid existing allocator and starts with the new allocator all allocated, then copies/free marks source-free regions into it.
- Hints may be too high but must never be too low; bugs in hint maintenance would cause either performance degradation or allocation failure despite available space.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_blist.c -->