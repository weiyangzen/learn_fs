# subset-b-006035 research

Grouped research for the requested source files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_core.c -->
# sources/distributed-fs/ceph-client/kernel/kexec_core.c

## Purpose
`kexec_core.c` implements the common in-kernel machinery behind kexec image staging and execution. It validates user- or file-mode segment layouts, allocates control/source pages, builds the self-contained indirection list consumed by architecture `machine_kexec()`, owns the global loaded reboot/crash images, exposes kexec status in sysfs, and provides sysctls that can permanently disable or count-limit kexec loads.

## Important APIs, Types, And Functions
Key exported/shared state is `atomic_t __kexec_lock`, `bool kexec_in_progress`, `bool kexec_file_dbg_print`, `struct kimage *kexec_image`, and `struct kimage *kexec_crash_image`. `do_kimage_alloc_init()` initializes `struct kimage` bookkeeping lists and crash hotplug fields. `sanity_check_segment_list()` enforces page alignment, non-overlap, size limits, crash-reserved-range containment, and memory acceptance. `kimage_alloc_control_pages()`, `kimage_alloc_page()`, `kimage_load_segment()`, `kimage_map_segment()`, and `kimage_free()` are the main image lifecycle helpers. `kexec_load_permitted()` gates loads by `CAP_SYS_BOOT`, `kexec_load_disabled`, and per-type load limits. `kernel_kexec()` executes the loaded image.

## Control Flow
Allocation starts with `do_kimage_alloc_init()`, segment validation, control-page allocation, then per-segment copying through `kimage_load_normal_segment()` or `kimage_load_crash_segment()`. Normal images build an indirection list of `IND_DESTINATION`, `IND_SOURCE`, `IND_INDIRECTION`, and `IND_DONE` entries so the relocation stub can copy pages at reboot time. Crash images copy directly into reserved crash memory. `kernel_kexec()` takes the NMI-safe lock, validates `kexec_image`, calls liveupdate and either the hibernation-like preserve-context path or normal reboot shutdown path, dumps kmsg, and transfers to `machine_kexec()`.

## State And Persistence
Loaded images persist in global pointers until exchanged or freed; page lists in each `kimage` track control, destination, unusable, and CMA-backed pages. Sysctls under `kernel/` hold process lifetime state: `kexec_load_disabled` is one-way to disabled, while `kexec_load_limit_panic` and `kexec_load_limit_reboot` decrement on successful permission checks. Sysfs under `/sys/kernel/kexec` reports `loaded`, crash status, crash size, CMA ranges, and crash elfcore header size when configured.

## Dependencies And Integration Points
The file depends on architecture hooks for allocation, preparation, cache flushing, shutdown, and execution (`arch_kexec_*`, `machine_kexec_*`). It integrates with crash dump reservation, CMA, syscore/PM/freezer/CPU hotplug, vmcoreinfo, liveupdate, sysctl, and `/sys/kernel` via `kernel_kobj`.

## Risks And Edge Cases
The core risks are memory corruption during page relocation, invalid crash-kernel destinations, overflow in segment math, and stale architecture cleanup if `kimage_free()` misses a path. The custom source/destination allocator can become O(N^2), and CMA segments bypass the normal indirection mapping. `kernel_kexec()` must preserve lock release and device resume paths after preserve-context failures.

## Test Signals
Useful signals include successful and failing `kexec_load`/`kexec_file_load` cases, segment overlap/alignment/oversize rejection, crash-kernel loads constrained to `crashk_res`, sysctl count-limit behavior, sysfs `loaded`/`crash_loaded` values, CMA segment loading, and architecture kexec selftests that verify control page allocation and final transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_elf.c -->
# sources/distributed-fs/ceph-client/kernel/kexec_elf.c

## Purpose
`kexec_elf.c` parses ELF executable buffers for `kexec_file_load()` loaders. It validates the ELF header and program headers in an endian-aware way, exposes probe/build/free helpers for architecture loaders, and converts `PT_LOAD` program headers into kexec segments through `kexec_add_buffer()`.

## Important APIs, Types, And Functions
The public helpers are `kexec_build_elf_info()`, `kexec_free_elf_info()`, `kexec_elf_probe()`, and `kexec_elf_load()`. Internal conversion helpers `elf16_to_cpu()`, `elf32_to_cpu()`, and `elf64_to_cpu()` honor `EI_DATA`. `elf_read_ehdr()` canonicalizes `struct elfhdr`; `elf_read_phdrs()` allocates a normalized `elf_info->proghdrs` array; sanity helpers reject truncated tables, unsupported class/data, bad entry sizes, wrapping offsets, and wrapping physical addresses.

## Control Flow
`kexec_build_elf_info()` calls `elf_read_from_buffer()`, accepts `ET_EXEC` and `ET_DYN`, requires program headers, and rejects `PT_INTERP`. `kexec_elf_probe()` adds `elf_check_arch()`. `kexec_elf_load()` iterates `PT_LOAD` headers, chooses file bytes no larger than memory bytes, populates a `struct kexec_buf` with source pointer, file size, memory size, alignment, and preferred physical address, then delegates placement to `kexec_add_buffer()`.

## State And Persistence
The only allocated state is `elf_info->proghdrs`, freed by `kexec_free_elf_info()`. Source buffers remain owned by the caller. Loaded state is persisted by the caller's `struct kimage` after `kexec_add_buffer()` records new segments.

## Dependencies And Integration Points
This file integrates with generic ELF definitions, architecture `elf_check_arch()`, and `kexec_file.c` placement through `struct kexec_buf`. It is loader-neutral and does not call sysfs, sysctl, or architecture relocation itself.

## Risks And Edge Cases
Parsing untrusted kernel images makes integer wrapping and bounds checks critical. Endianness conversion must happen before size and offset use. A `PT_LOAD` with `p_filesz > p_memsz` is clipped to memory size; missing loadable segments would leave `lowest_load_addr` as `ULONG_MAX` unless handled by the caller. Rejection of `PT_INTERP` prevents ordinary dynamically linked executables from being treated as kernels.

## Test Signals
Tests should cover little- and big-endian ELF buffers, bad magic/class/data/version, truncated program/section tables, wrapping offsets, `PT_INTERP` rejection, `ET_EXEC`/`ET_DYN` acceptance, arch mismatch via `kexec_elf_probe()`, and correct `kexec_buf` values for multiple `PT_LOAD` segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_file.c -->
# sources/distributed-fs/ceph-client/kernel/kexec_file.c

## Purpose
`kexec_file.c` implements the `kexec_file_load` syscall path where the kernel, not userspace, reads and interprets the kernel/initrd/cmdline files. It probes architecture file loaders, verifies signatures when configured, constructs kexec segments, locates memory holes, loads purgatory, stores SHA-256 digests for purgatory verification, and atomically installs or unloads default/crash images.

## Important APIs, Types, And Functions
Loader-facing APIs include `kexec_image_probe_default()`, `kexec_image_post_load_cleanup_default()`, `kexec_add_buffer()`, `kexec_locate_mem_hole()`, `kexec_load_purgatory()`, `kexec_purgatory_get_symbol_addr()`, and `kexec_purgatory_get_set_symbol()`. The syscall is `SYSCALL_DEFINE5(kexec_file_load, ...)`. Internal helpers read files with `kernel_read_file_from_fd()`, validate signatures through loader `verify_sig`, prepare segments, and clean temporary `kernel_buf`, `initrd_buf`, `cmdline_buf`, purgatory buffers, and IMA buffers.

## Control Flow
The syscall checks `kexec_load_permitted()`, validates flags, takes `kexec_trylock()`, chooses `kexec_image` or `kexec_crash_image`, handles unload by exchange, and otherwise allocates a file-mode `kimage`. Preparation reads kernel/initrd, probes the arch loader, optionally verifies signatures and lockdown policy, copies a NUL-terminated command line, adds IMA/KHO buffers, and calls the loader. After segment sanity checks, it allocates control and swap pages, calls `machine_kexec_prepare()`, copies vmcoreinfo for crash images, calculates digests, loads every segment, terminates the indirection list, runs post-load hooks, cleans temporary buffers, and exchanges the global image pointer.

## State And Persistence
File contents are transient until converted into `image->segment[]` and segment source pages. Installed images persist in the global kexec pointers. `segment_cma[]` records contiguous CMA allocations for zero-copy placement. Purgatory state lives in `image->purgatory_info` until copied and later cleaned. Signature enforcement is held in static `sig_enforce`, which can be forced on by `set_kexec_sig_enforced()`.

## Dependencies And Integration Points
The file depends on architecture loaders (`kexec_file_loaders`, `arch_kexec_kernel_image_probe()`, `arch_kexec_locate_mem_hole()`, relocation hooks), IMA, lockdown, PE signature verification, KHO handover, crash hotplug, memblock or system RAM walkers, DMA CMA, SHA-256 crypto, and purgatory ELF symbols. It also relies on core functions from `kexec_core.c`.

## Risks And Edge Cases
Major risks include accepting unsigned images under lockdown policy, placing segments over each other or over excluded architecture ranges, stale crash memory protection, CMA overlap, purgatory relocation errors, digest omissions, and cleanup leaks on late errors. The memory-hole search must handle top-down/bottom-up alignment, driver-managed RAM, crash ranges, KHO-only scratch memory, and `CONFIG_ARCH_KEEP_MEMBLOCK` differences.

## Test Signals
Signals include syscall flag validation, unload behavior, permission/limit checks, signature enforced/permissive paths, initrd omission, bad command-line NUL termination, memory-hole placement under overlap/excluded ranges, CMA success/fallback, purgatory symbol set/get, digest verification, crash-image protection toggles, and IMA/KHO segment inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_internal.h -->
# sources/distributed-fs/ceph-client/kernel/kexec_internal.h

## Purpose
`kexec_internal.h` is the private boundary between the kexec core, file loader, ELF loader, purgatory support, and optional handover support. It centralizes shared prototypes and the NMI-safe kexec lock helpers.

## Important APIs, Types, And Functions
It declares `do_kimage_alloc_init()`, `sanity_check_segment_list()`, `kimage_free_page_list()`, `kimage_free()`, `kimage_load_segment()`, `kimage_terminate()`, and `kimage_is_destination_range()`. It defines `kexec_trylock()` and `kexec_unlock()` around `atomic_t __kexec_lock` using acquire/release semantics. Under `CONFIG_KEXEC_FILE`, it exposes `kimage_file_post_load_cleanup()`, `kexec_purgatory`, and `kexec_purgatory_size`. Under `CONFIG_KEXEC_HANDOVER`, it exposes `kho_locate_mem_hole()` and `kho_fill_kimage()`.

## Control Flow
The header does not execute control flow itself, but shapes all kexec paths: loaders allocate a `kimage`, validate segments, load segments, terminate the indirection page list, and free images through this interface. `kexec_trylock()` is used by load and execution paths to serialize image mutation and crash-image access.

## State And Persistence
The only state named here is `__kexec_lock`, which persists for the kernel lifetime. Inline stubs for disabled configs preserve call-site simplicity without storing state.

## Dependencies And Integration Points
The header depends on `<linux/kexec.h>` and optional `<linux/purgatory.h>`. It is included by `kexec_core.c` and `kexec_file.c`, and indirectly constrains architecture hooks that operate on `struct kimage` and `struct kexec_buf`.

## Risks And Edge Cases
Because `__crash_kexec()` may happen during NMI panic, the lock intentionally avoids sleeping locks. Any future replacement must keep NMI safety and release/acquire ordering. Config stubs must retain semantics: no file cleanup when file loading is absent and permissive no-op KHO behavior when handover is absent.

## Test Signals
Compile coverage across `CONFIG_KEXEC_FILE`, `CONFIG_KEXEC_HANDOVER`, and crash dump combinations is the primary signal. Runtime load/execution tests should show no deadlock under concurrent load/unload and panic-crash paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kheaders.c -->
# sources/distributed-fs/ceph-client/kernel/kheaders.c

## Purpose
`kheaders.c` exposes the compressed kernel header archive used for building tracing/eBPF programs through a sysfs binary attribute.

## Important APIs, Types, And Functions
Inline assembly emits `kernel_headers_data` and `kernel_headers_data_end` in `.rodata` by including `kernel/kheaders_data.tar.xz`. `kheaders_attr` is a `struct bin_attribute` created with `__BIN_ATTR_SIMPLE_RO(kheaders.tar.xz, 0444)`. `ikheaders_init()` sets the binary attribute's private pointer and size, then calls `sysfs_create_bin_file(kernel_kobj, ...)`; `ikheaders_cleanup()` removes it.

## Control Flow
At module/init time, the archive symbols are already present in read-only data. The init function publishes the archive under `/sys/kernel/kheaders.tar.xz`; module exit removes the sysfs file.

## State And Persistence
The archive is immutable kernel/module rodata. The only runtime state is the sysfs bin attribute metadata. It persists while the module/built-in feature is active.

## Dependencies And Integration Points
The file depends on `kernel_kobj` from `ksysfs.c`, sysfs binary attributes, module init/exit, and the build-generated `kernel/kheaders_data.tar.xz` artifact.

## Risks And Edge Cases
Failure to initialize `/sys/kernel` first would make `kernel_kobj` invalid. Missing or stale generated header archives break build/reproducibility expectations. The archive is world-readable, so content should be limited to build headers and not secrets.

## Test Signals
Signals are successful creation/removal of `/sys/kernel/kheaders.tar.xz`, correct file size matching linker symbols, readable xz tar content, module load/unload behavior, and build coverage when kernel headers are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kheaders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/kernel/kprobes.c

## Purpose
`kprobes.c` implements dynamic instrumentation for kernel text. It registers and unregisters kprobes and kretprobes, manages breakpoint or ftrace-based arming, aggregates multiple probes at one address, allocates executable out-of-line instruction slots, performs optional jump optimization, maintains blacklists, tracks module lifetime, and exports debugfs/sysctl controls.

## Important APIs, Types, And Functions
The main exported APIs are `register_kprobe()`, `unregister_kprobe()`, batch variants, `enable_kprobe()`, `disable_kprobe()`, `register_kretprobe()`, `unregister_kretprobe()`, `kprobe_on_func_entry()`, `kprobe_flush_task()`, and blacklist/kallsyms helpers. Core state includes `kprobe_table[]`, `kprobe_mutex`, per-CPU `kprobe_instance`, `kprobes_all_disarmed`, `kprobe_blacklist`, and optimization lists. Architecture hooks provide instruction preparation, arming, disarming, relocation, optimized probes, ftrace handlers, and exception notification.

## Control Flow
`register_kprobe()` canonicalizes symbol/address/offset, rejects reserved text, takes module references, and calls `__register_kprobe()`. If a probe already exists at the address, `register_aggr_kprobe()` creates or reuses an aggregator and chains handlers; otherwise it prepares the instruction, inserts into the hash table, arms it, and attempts optimization. Unregistration disables/disarms under `kprobe_mutex`, removes hash/list entries, synchronizes RCU, and frees architecture slots. Kretprobes install a normal entry kprobe whose pre-handler allocates a return instance and hooks the return path through either objpool/trampoline or rethook.

## State And Persistence
Registered probes persist in the static hash table until unregistered or killed by module/init-memory teardown. Instruction slots live in executable pages and are mark-and-sweep reclaimed after RCU grace periods. Optimization queues persist until the `kprobe-optimizer` kthread processes them. Debugfs exposes `/sys/kernel/debug/kprobes/list`, `enabled`, and `blacklist`; sysctl `debug/kprobes-optimization` toggles optimization when enabled.

## Dependencies And Integration Points
This file integrates with kallsyms, modules, ftrace, perf ksymbol events, static calls, jump labels, CPU hotplug locks, text patching via `text_mutex`, debugfs, sysctl, exception notifiers, RCU/tasks-RCU, rethook/objpool, and architecture-specific probe code.

## Risks And Edge Cases
Risks are high because the code modifies live kernel text. It must avoid blacklisted/noinstr/CFI/jump-label/static-call/BUG/gate areas, handle module `.init.text` and unloading, preserve RCU safety while breakpoint handlers traverse tables, avoid optimizer deadlocks with CPU hotplug and `text_mutex`, and prevent ftrace IPMODIFY conflicts. Kretprobe pools can miss returns under pressure, incrementing `nmissed`.

## Test Signals
Signals include registering by symbol and address, duplicate-address aggregation, enable/disable and global debugfs toggling, optimization sysctl on/off, ftrace-backed probes, module load/unload cleanup, blacklist contents, kretprobe return handling and maxactive exhaustion, concurrent registration/unregistration stress, and architecture kprobe selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kstack_erase.c -->
# sources/distributed-fs/ceph-client/kernel/kstack_erase.c

## Purpose
`kstack_erase.c` implements STACKLEAK/KSTACK_ERASE behavior: it tracks the lowest stack pointer reached by a task and poisons the used portion of the kernel stack before returning to userspace to reduce information disclosure and uninitialized stack attack surface.

## Important APIs, Types, And Functions
The entry points are `stackleak_erase()`, `stackleak_erase_on_task_stack()`, `stackleak_erase_off_task_stack()`, and exported `__sanitizer_cov_stack_depth()`. `__stackleak_erase()` computes erase bounds with `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `stackleak_find_top_of_poison()`, `current_stack_pointer`, and `current->lowest_stack`. Optional runtime disable uses static key `stack_erasing_bypass` and sysctl `kernel/stack_erasing`.

## Control Flow
Instrumentation calls `__sanitizer_cov_stack_depth()` to lower `current->lowest_stack` when a deeper stack pointer is observed. On syscall/return paths, erase wrappers skip if disabled, then poison from the previous poison top to either the current stack pointer or the top of the task stack depending on whether execution is on the task stack. The lowest marker resets to the stack high bound for the next syscall.

## State And Persistence
Per-task `lowest_stack` and optional `prev_lowest_stack` carry state across kernel entries. The runtime-disable static key persists globally until sysctl toggles it.

## Dependencies And Integration Points
The file depends on low-level stack helpers, `noinstr` entry constraints, sysctl, jump labels, and compiler sanitizer stack-depth instrumentation. It explicitly exports `__sanitizer_cov_stack_depth` for instrumentation references.

## Risks And Edge Cases
The erase range must not clobber active frames, so wrong `on_task_stack` selection or stack-bound helpers can crash the kernel. `CONFIG_KSTACK_ERASE_TRACK_MIN_SIZE` must not exceed search depth. Runtime disable weakens security and logs a warning. The code is `noinstr`, so instrumentation and tracing constraints are strict.

## Test Signals
Signals include sysctl enable/disable behavior, poison pattern visibility in stack tests, no corruption on task and entry stacks, stack-depth tracking under deep calls, metrics updates when configured, and build-time `BUILD_BUG_ON` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kstack_erase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ksyms_common.c -->
# sources/distributed-fs/ceph-client/kernel/ksyms_common.c

## Purpose
`ksyms_common.c` contains common kallsyms visibility policy that is independent of full `CONFIG_KALLSYMS` implementation details.

## Important APIs, Types, And Functions
The exported function is `kallsyms_show_value(const struct cred *cred)`. Internal `kallsyms_for_perf()` permits symbol values when `CONFIG_PERF_EVENTS` is enabled and `sysctl_perf_event_paranoid <= 1`. The policy also consults global `kptr_restrict` and `security_capable(..., CAP_SYSLOG, CAP_OPT_NOAUDIT)`.

## Control Flow
For `kptr_restrict == 0`, perf-friendly settings allow values to normal users; otherwise it falls through to the capability check. For `kptr_restrict == 1`, `CAP_SYSLOG` permits values. All other cases return false.

## State And Persistence
The file owns no persistent state. It reads global sysctl/security state that can change at runtime.

## Dependencies And Integration Points
It integrates with `/proc/kallsyms`, debugfs/proc users such as kprobes reporting, perf event policy, credentials, security modules, and the initial user namespace.

## Risks And Edge Cases
The risk is kernel address disclosure. The fallthrough logic intentionally allows capable users when `kptr_restrict` is 0 or 1, but not stricter modes. Changes to perf paranoia semantics or capability policy affect observability surfaces.

## Test Signals
Test by reading kallsyms-dependent outputs under different `kptr_restrict`, `perf_event_paranoid`, user credential, and `CAP_SYSLOG` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ksyms_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ksysfs.c -->
# sources/distributed-fs/ceph-client/kernel/ksysfs.c

## Purpose
`ksysfs.c` creates `/sys/kernel` and populates generic kernel-level sysfs attributes not owned by another subsystem.

## Important APIs, Types, And Functions
The file exports `struct kobject *kernel_kobj`. `ksysfs_init()` creates the kobject, installs `kernel_attr_group`, and optionally publishes a binary `notes` file from linker symbols. Attributes include `uevent_seqnum`, `cpu_byteorder`, `address_bits`, optional `uevent_helper`, `profiling`, `vmcoreinfo`, `fscaps`, `rcu_expedited`, and `rcu_normal`.

## Control Flow
Each show/store function formats or parses a simple value using sysfs helpers. `profiling_store()` serializes initialization so profiling buffers and proc entries are only allocated once. `ksysfs_init()` unwinds sysfs group/kobject creation on failure and logs an initialization error.

## State And Persistence
`kernel_kobj` persists for the kernel lifetime and anchors many other features, including kexec and kheaders. Mutable attributes write global state such as `uevent_helper`, `prof_on`, `rcu_expedited`, and `rcu_normal`; most other attributes report read-only build/runtime facts.

## Dependencies And Integration Points
The file integrates with kobject/sysfs, uevent, profiling, vmcoreinfo, file capabilities, RCU policy, linker notes, and architecture byte order definitions. Other files depend on `kernel_kobj` for their own sysfs files.

## Risks And Edge Cases
Store handlers must validate input length and parse errors. `uevent_helper` mutability is security-sensitive when enabled. `profiling_store()` must not reinitialize after profiling is active. Notes size derives from linker symbols and must only create a bin file when positive.

## Test Signals
Signals include `/sys/kernel` creation, expected attributes under config combinations, read/write behavior for RCU and profiling controls, notes bin-file size/content, and dependent sysfs users such as `/sys/kernel/kexec` and `/sys/kernel/kheaders.tar.xz`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ksysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kthread.c -->
# sources/distributed-fs/ceph-client/kernel/kthread.c

## Purpose
`kthread.c` provides the kernel thread creation, lifecycle, parking/stopping, affinity, worker-queue, delayed-work, temporary-mm, and block-cgroup helper APIs used across the kernel.

## Important APIs, Types, And Functions
Key types are `struct kthread_create_info` and private `struct kthread`. Public APIs include `kthread_create_on_node()`, `kthread_create_on_cpu()`, `kthread_bind()`, `kthread_stop()`, `kthread_park()`, `kthread_unpark()`, `kthread_should_stop()`, `kthread_should_park()`, `kthread_worker_fn()`, worker create/destroy/queue/flush/cancel helpers, `kthread_use_mm()`, and `kthread_unuse_mm()`. Global state includes `kthreadd_task`, `kthread_create_list`, and `kthread_affinity_list`.

## Control Flow
Callers enqueue create requests under `kthread_create_lock` and wake `kthreadd`. `kthreadd()` clones a child running `kthread()`, which initializes private metadata, reports completion, sleeps until explicitly woken/stopped, applies default affinity, parks if requested, then runs the caller function and exits through `kthread_exit()`. Stop and park set flag bits, wake the task, and wait on completions/inactive states. Worker APIs run a loop that dequeues work under a raw spinlock, executes callbacks, handles freezing, and supports delayed timers.

## State And Persistence
Each kthread stores flags, CPU/node preference, result, function/data, completions, optional full name, preferred affinity, and optional blkcg association in `task->worker_private`. Worker objects persist until destroyed and own pending/current/delayed work lists. Affinity preferences are kept on a global list and refreshed on housekeeping/cpuhp changes.

## Dependencies And Integration Points
The file integrates with scheduler states, completions, freezer, cgroups, cpusets/housekeeping isolation, CPU hotplug, NUMA, timers, tracepoints, membarrier/MMU context switching, and block cgroups. It is foundational for subsystem daemon threads such as the kprobe optimizer.

## Risks And Edge Cases
Races around creation cancellation, park/unpark, delayed work timer cancellation, worker destruction, and CPU hotplug are the main hazards. Callers must not queue one work item to multiple workers. `kthread_use_mm()` must maintain membarrier and TLB ordering. Affinity APIs require inactive tasks before first wakeup.

## Test Signals
Signals include successful creation under `kthreadd`, killable creation interruption, stop return values, park/unpark state transitions, CPU-bound and preferred-affinity behavior across hotplug/isolation changes, worker queue/flush/cancel/delayed-work semantics, freezer handling, and temporary-mm adoption ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/latencytop.c -->
# sources/distributed-fs/ceph-client/kernel/latencytop.c

## Purpose
`latencytop.c` records scheduler sleep latencies for system-wide and per-task reporting used by the latencytop userspace tool.

## Important APIs, Types, And Functions
Global state includes `latency_record[MAXLR]`, `latency_lock`, and `int latencytop_enabled`. Public functions are `clear_tsk_latency_tracing()` and scheduler-called `__account_scheduler_latency()`. Procfs uses `lstats_show()`, `lstats_write()`, and `lstats_proc_ops`; sysctl uses `kernel/latencytop`.

## Control Flow
When enabled scheduler code calls `__account_scheduler_latency()` with a task, duration, and interruptible flag. Long interruptible waits over 5 ms, zero, and negative durations are ignored. The function captures a stack trace, merges it into the global table for user tasks and into the task-local table, or drops it when fixed-size arrays are full. `/proc/latency_stats` reads formatted counters and symbolized backtraces; writing clears global stats.

## State And Persistence
Latency data is in fixed-size in-memory arrays and persists until overwritten by matching records or cleared. Per-task records live in `task_struct`; global records live for the kernel lifetime. Enabling the sysctl also forces schedstats on.

## Dependencies And Integration Points
The file depends on scheduler latency accounting, stacktrace capture, kallsyms symbol formatting, procfs seq files, sysctl, raw spinlocks, and task-local latency fields.

## Risks And Edge Cases
Fixed arrays drop new causes once full, so userspace must clear regularly. Stack trace identity is pointer-based and can be affected by module unload or symbol visibility. Locking is global and IRQ-saving, so accounting cost matters in scheduler paths.

## Test Signals
Signals include sysctl enabling and schedstat forcing, `/proc/latency_stats` header and rows, write-to-clear behavior, per-task clearing, dropped long interruptible sleeps, and merged counts/max/total for repeated backtraces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/latencytop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/livepatch/Kconfig

## Purpose
This Kconfig file defines feature gates for kernel live patching and klp-build support.

## Important APIs, Types, And Functions
It declares `HAVE_LIVEPATCH` as an architecture capability, `LIVEPATCH` as the user-visible "Kernel Live Patching" option, `HAVE_KLP_BUILD` as an architecture capability for klp-build, and `KLP_BUILD` as a default-on option when both livepatching and architecture support are present.

## Control Flow
Kconfig dependency resolution enables `LIVEPATCH` only with dynamic ftrace register/argument support, modules, sysfs, complete kallsyms, architecture support, and without `TRIM_UNUSED_KSYMS`. `KLP_BUILD` selects `OBJTOOL` and depends on `LIVEPATCH && HAVE_KLP_BUILD`.

## State And Persistence
The file has no runtime state. It determines compile-time availability of livepatch objects and related build tooling.

## Dependencies And Integration Points
It integrates livepatching with ftrace, modules, sysfs, kallsyms, architecture Kconfig selects, unused-symbol trimming policy, and objtool.

## Risks And Edge Cases
Incorrect dependencies could produce a kernel where livepatch modules cannot resolve symbols or redirect calls safely. `TRIM_UNUSED_KSYMS` is explicitly incompatible because live patches may need symbols that appear unused at base build time.

## Test Signals
Signals include Kconfig dependency tests across architectures, expected visibility of `CONFIG_LIVEPATCH`, `CONFIG_KLP_BUILD` selecting `OBJTOOL`, and successful build of livepatch core objects only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/Makefile -->
# sources/distributed-fs/ceph-client/kernel/livepatch/Makefile

## Purpose
The Makefile wires livepatch source files into the kernel build when `CONFIG_LIVEPATCH` is enabled.

## Important APIs, Types, And Functions
It sets `obj-$(CONFIG_LIVEPATCH) += livepatch.o` and defines `livepatch-objs := core.o patch.o shadow.o state.o transition.o`.

## Control Flow
During kbuild, enabling `CONFIG_LIVEPATCH` builds a composite `livepatch.o` from the listed objects; disabling the config omits the directory's livepatch implementation.

## State And Persistence
There is no runtime state. The persistent effect is the build artifact composition for livepatch support.

## Dependencies And Integration Points
This file is driven by the sibling Kconfig and kbuild's composite object rules. The component objects represent livepatch core registration, patch application, shadow variables, state, and transitions.

## Risks And Edge Cases
Missing an object here would compile out part of livepatch behavior despite Kconfig enablement. Adding objects requires keeping this list synchronized with source files and dependency expectations.

## Test Signals
Signals include `CONFIG_LIVEPATCH=y` builds producing `livepatch.o` from all five objects and disabled builds omitting the object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/Makefile -->
