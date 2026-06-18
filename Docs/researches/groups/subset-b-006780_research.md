# Research: subset-b-006780

Grouped research for the source-tree-aligned files in work item `subset-b-006780`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/Makefile

Purpose: builds and packages the `x86_energy_perf_policy` utility, a privileged x86 power-policy tool. It supports normal in-tree builds, `O=` redirected builds, installation into `$(DESTDIR)$(PREFIX)`, cleanup, and a snapshot tarball that carries enough copied kernel headers to build outside the kernel tree.

Important APIs and targets: `CC=$(CROSS_COMPILE)gcc`, `BUILD_OUTPUT`, `PREFIX`, `DESTDIR`, and `SNAPSHOT` are the main variables. The explicit `x86_energy_perf_policy : x86_energy_perf_policy.c` dependency is built by the generic `%: %.c` rule. `override CFLAGS` adds optimization, warnings, the tools include path, `MSRHEADER` pointing at `arch/x86/include/asm/msr-index.h`, and `_FORTIFY_SOURCE=2`. Targets are `clean`, `install`, and `snapshot`.

Control flow: `all` is implicit through the first target. The pattern rule creates the output directory and invokes the compiler. `install` first builds the tool, then installs the binary and man page. `snapshot` removes any same-day staging directory, copies the sources and man page, rewrites `msr-index.h` include assumptions, emits compatibility `bits.h` and `build_bug.h`, writes a standalone Makefile, and archives the snapshot.

State and persistence: build artifacts land in `$(BUILD_OUTPUT)`, which defaults to the source directory and switches to `$(O)` when `O=` is supplied. `install` persists under `$(DESTDIR)$(PREFIX)`. `snapshot` creates and replaces date-stamped directories and `.tar.gz` files in the working directory.

Dependencies and integration: depends on kernel tools make infrastructure only indirectly through include paths and the x86 `msr-index.h` header. Snapshot mode deliberately removes that dependency by copying and rewriting header fragments. Runtime dependencies of the built tool are in the C source, not the Makefile.

Risks: the `snapshot` target performs broad `rm -rf $(SNAPSHOT)` and `rm -f $(SNAPSHOT).tar.gz` operations based on a generated date name. The MSR header path is relative and fragile if the tool moves. `install` assumes `x86_energy_perf_policy.8` exists beside the Makefile.

Test signals: successful `make`, `make O=/tmp/out`, `make install DESTDIR=/tmp/stage`, and `make snapshot` are the relevant checks. Compile should fail quickly if `MSRHEADER` or kernel include paths are wrong.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/x86_energy_perf_policy.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/x86_energy_perf_policy.c

Purpose: implements Intel x86 energy/performance policy inspection and mutation. It reads and writes EPB, HWP request/capability MSRs, turbo enable bits, cpufreq sysfs min/max limits, SoC power slider sysfs parameters, and platform profile state.

Important APIs/types/functions: `struct msr_hwp_cap` models HWP capability bytes, and `struct msr_hwp_request` models min/max/desired/EPP/window/use_pkg request fields. Global flags such as `update_epb`, `update_hwp_min`, `update_hwp_max`, `update_turbo`, `update_soc_slider_balance`, and `update_platform_profile` drive the mutation path. Parser functions include `parse_cmdline_epb()`, `parse_cmdline_hwp_min()`, `parse_cmdline_hwp_max()`, `parse_cmdline_hwp_desired()`, `parse_cmdline_hwp_window()`, `parse_cmdline_hwp_epp()`, `parse_cmdline_turbo()`, `parse_cmdline_cpu()`, `parse_cmdline_pkg()`, and `cmdline()`. Hardware access is through `get_msr()`, `put_msr()`, `read_sysfs()`, `write_sysfs()`, `get_epb_sysfs()`, and `set_epb_sysfs()`.

Control flow: `main()` determines the current CPU, probes `/dev/cpu/N/msr` or Android-style `/dev/msrN`, initializes CPU/package sets from `/proc/stat` and topology sysfs, performs early CPUID detection, parses arguments, then performs full CPUID validation. It defaults to all CPUs when no scope is specified, optionally enables HWP first, verifies HWP availability on the selected set, validates requested bounds, and either prints state or applies updates. CPU updates run EPB sysfs writes, cpufreq sysfs min/max writes, then MSR writes in that order. Package updates write `MSR_HWP_REQUEST_PKG` through the first CPU in each selected package.

State and persistence: the program does not keep its own files. It persists changes directly into kernel MSR state and sysfs knobs: EPB under `cpu*/power/energy_perf_bias`, HWP request MSRs, `MSR_IA32_MISC_ENABLE` turbo disable bit, cpufreq `scaling_min_freq` and `scaling_max_freq`, SoC slider module parameters, and platform profile sysfs. Global process state tracks selected CPUs/packages, package first CPUs, CPUID feature bits, and pending request values.

Dependencies and integration: requires x86 CPUID, MSR support, root or MSR device permissions, `/proc/stat`, CPU topology sysfs, and kernel x86 MSR constants included via `MSRHEADER`. It integrates with `intel_pstate` or cpufreq by preferring sysfs min/max writes before direct HWP request writes to avoid driver clipping surprises. It refuses unsupported package HWP controls when CPUID lacks them.

Risks: it is a privileged hardware-control tool; incorrect inputs can reduce performance, violate expected platform policy, or affect all CPUs by default. CPU/package parsing accepts ranges and undocumented `even`/`odd` CPU selectors. `MAX_PACKAGES` is fixed at 64. `write_sysfs()` returns unsigned values but may return `-1`, which becomes a large unsigned value. HWP min/max may be handled via sysfs, causing `hwp_limits_done_via_sysfs` to suppress equivalent MSR fields. Hypervisor detection is best effort and reads only a portion of `/proc/cpuinfo`.

Test signals: useful tests are argument parser cases, CPU/package selection validation, read-only execution on real Intel hardware, update attempts with and without `--force`, missing MSR device behavior, HWP-disabled behavior, sysfs EPB read/write paths, and debug output around old/new HWP requests. Snapshot builds from the Makefile also test the `MSRHEADER` abstraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/x86_energy_perf_policy/x86_energy_perf_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/extract-stall.sh -->
# sources/distributed-fs/ceph-client/tools/rcu/extract-stall.sh

Purpose: extracts RCU CPU stall warning snippets from a console or dmesg log, including configurable context before and after each stall line while filtering out clocksource noise.

Important APIs/functions: `usage()` prints guidance and an error. The main body validates that `$1` is a readable file, assigns `preceding_lines` from `$2` defaulting to 3 and `trailing_lines` from `$3` defaulting to 10, and runs an `awk` state machine followed by `tr -d '\015'` and `grep -v clocksource`.

Control flow: the script prints the input path, then `awk` maintains a rolling `last[]` buffer while not in suffix mode. When a line matches `detected stall`, it prints the preceding buffer including the matched line and sets `suffix` to the trailing count. While `suffix > 0`, it prints following lines and emits a blank line at the end of the snippet.

State and persistence: no persistent state. Runtime state is held in awk variables `last[]` and `suffix`.

Dependencies and integration: POSIX shell plus `awk`, `tr`, `grep`, and `basename`. It integrates with RCU debugging workflows by reducing large logs to stall excerpts.

Risks: matching is plain `/detected stall/`, so it can include non-RCU lines with that phrase and miss differently worded warnings. `grep -v clocksource` removes any line containing that string, even if it is useful context. Unquoted `$(basename $0)` in `usage()` is minor shell-style risk.

Test signals: run against logs with no stall, one stall, adjacent stalls, CRLF line endings, custom preceding/trailing counts, and unreadable/missing files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/extract-stall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/rcu-cbs.py -->
# sources/distributed-fs/ceph-client/tools/rcu/rcu-cbs.py

Purpose: drgn script that sums outstanding RCU callbacks across possible CPUs and prints the total callbacks in flight.

Important APIs/functions: `get_rdp0(prog)` attempts to locate `rcu_preempt_data`, falls back to `rcu_sched_data`, then to `rcu_data` in `kernel/rcu/tree.c`, returning the per-CPU symbol address. The main loop uses `for_each_possible_cpu(prog)`, `per_cpu_ptr()`, and `rdp.cblist.len.value_()`.

Control flow: resolve the correct RCU per-CPU data symbol, initialize `sum`, iterate all possible CPUs, fetch the per-CPU RCU data pointer, read callback list length, add it to the sum, then print one summary line.

State and persistence: no persistent state. It reads live or crash-dump kernel memory through drgn.

Dependencies and integration: requires `drgn`, kernel debug/BTF information sufficient to resolve RCU symbols and fields, and helpers from `drgn.helpers.linux`. It integrates with RCU diagnostics by exposing a compact backlog count.

Risks: field and symbol names differ across kernels; the fallback chain handles old RCU flavors but still assumes `cblist.len`. The script shadows built-in names `sum` and `len`. It reports only a total, not per-CPU distribution, so it can hide skew.

Test signals: run under `sudo drgn rcu-cbs.py` on kernels with `rcu_preempt_data`, older kernels with `rcu_sched_data`, and kernels exposing only `rcu_data`; compare totals with optional per-CPU debug prints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/rcu-cbs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/rcu-updaters.sh -->
# sources/distributed-fs/ceph-client/tools/rcu/rcu-updaters.sh

Purpose: samples RCU update-side and grace-period primitives with bpftrace and prints a histogram of call counts.

Important APIs/functions: the script builds an optional `exitclause` from the first argument, then runs one `bpftrace -e` program with many `kprobe:` targets including `call_rcu`, SRCU, Tasks RCU, barrier, synchronize, poll-state, and `rcu_gp_init`. The action is `@counts[func] = count();`.

Control flow: if a duration is provided, add an interval probe that exits after that many seconds. Otherwise, tell the user to use control-C. The bpftrace program accumulates counts by probed function name until termination.

State and persistence: no files or persistent state. Aggregation lives in bpftrace maps and is printed by bpftrace on exit.

Dependencies and integration: requires bpftrace, kprobe support, sufficient privileges, and kernel symbols for the named functions. It tolerates missing functions by relying on bpftrace diagnostics while continuing with available probes.

Risks: kprobe availability varies with config, inlining, and symbol visibility. High-frequency probes can add overhead. Shell interpolation of `duration` is simple and assumes a numeric value. The count for `rcu_gp_init()` is normal non-expedited grace periods, while other entries are primitive invocations, so interpretation is not one uniform unit.

Test signals: run with a short duration, run without duration and interrupt, validate behavior when some symbols are absent, and compare expected increases while running workloads that call RCU primitives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/rcu/rcu-updaters.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched/dl_bw_dump.py -->
# sources/distributed-fs/ceph-client/tools/sched/dl_bw_dump.py

Purpose: drgn diagnostic that prints deadline scheduling bandwidth accounting fields from each online CPU runqueue.

Important APIs/functions: `print_dl_bws_info()` reads `prog['runqueues']`, iterates `for_each_possible_cpu(prog)`, obtains each `rq` with `per_cpu()`, skips offline runqueues through `rq.online`, then prints `rq.dl.running_bw`, `this_bw`, `extra_bw`, `max_bw`, and `bw_ratio`.

Control flow: argparse is initialized with a descriptive help string, then the script calls `print_dl_bws_info()`. Per-CPU memory access is guarded by exception handlers for `drgn.FaultError`, `AttributeError`, and generic exceptions.

State and persistence: no persistent state; it reads live kernel memory or a drgn target.

Dependencies and integration: requires drgn, scheduler debug symbols/BTF for `runqueues`, and Linux helper functions. It integrates with SCHED_DEADLINE analysis by reporting the per-runqueue `dl_rq` accounting state.

Risks: imports `os` and common helpers that are unused. Kernel structure changes can rename or remove fields. It iterates possible CPUs and manually skips offline CPUs, so hotplug races can produce transient faults.

Test signals: run on a kernel with SCHED_DEADLINE enabled, compare output before and during deadline workloads, and verify graceful messages on kernels lacking expected `dl_rq` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched/dl_bw_dump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched/root_domains_dump.py -->
# sources/distributed-fs/ceph-client/tools/sched/root_domains_dump.py

Purpose: drgn diagnostic that prints unique scheduler root domains and their CPU masks.

Important APIs/functions: `print_root_domains_info()` reads `prog['runqueues']` and `prog['def_root_domain']`, iterates possible CPUs, gets `rq.rd`, de-duplicates root-domain pointers in `seen_root_domains`, and prints the first CPU seen plus cpumask strings through `cpumask_to_cpulist()`.

Control flow: argparse sets help text, then the root-domain printer walks per-CPU runqueues. It labels the default root domain specially when the pointer equals `def_root_domain.address_`; other root domains are printed by address. Fault, attribute, and generic exceptions are reported per CPU.

State and persistence: no persistent state. Runtime state is only the set of already printed root-domain addresses.

Dependencies and integration: requires drgn and scheduler symbols/BTF for runqueues, root domains, and cpumask helpers. It is useful for cpuset, CPU hotplug, and scheduling-domain debugging.

Risks: the script prints both `Span` and `Online` from `root_domain.span[0]`; this appears suspicious because a separate online mask may exist or the label may be misleading. Pointer conversion with `int(root_domain)` depends on drgn object behavior. Kernel field changes can break access.

Test signals: run on a normal single-root-domain system, then with cpuset partitions or hotplug configurations that create multiple root domains; verify that duplicate pointers are suppressed and masks match scheduler debugfs expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched/root_domains_dump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/Kconfig -->
# sources/distributed-fs/ceph-client/tools/sched_ext/Kconfig

Purpose: documents a kernel configuration fragment for building and testing sched_ext schedulers and related tracing/debugging capabilities.

Important entries: mandatory scheduler and BPF options include `CONFIG_BPF`, `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_BPF_JIT_ALWAYS_ON`, `CONFIG_BPF_JIT_DEFAULT_ON`, and `CONFIG_SCHED_CLASS_EXT`. Test coverage and debugging entries include `CONFIG_SCHED_DEBUG`, `CONFIG_SCHED_AUTOGROUP`, `CONFIG_SCHED_CORE`, `CONFIG_SCHED_MC`, `CONFIG_PREEMPT`, `CONFIG_PREEMPT_DYNAMIC`, lockdep/prove-locking options, ftrace/kprobe/uprobe/BPF event options, `CONFIG_IKHEADERS`, and IKCONFIG options.

Control flow: no executable control flow; this is consumed as a config checklist or fragment.

State and persistence: persistent state is kernel build configuration. It has no runtime state by itself.

Dependencies and integration: integrates with the sched_ext examples by ensuring BPF, BTF, struct_ops, tracing, sched core, and debug infrastructure exist. `CONFIG_KALLSYMS_ALL` is called out for Rust schedulers. `CONFIG_DEBUG_INFO_REDUCED` is explicitly disabled for arm64.

Risks: enabling debug lock and tracing options can add overhead and may not be desirable in production. It is a broad testing profile, not a minimal runtime profile. Comments reference LAVD and Rust schedulers beyond the C examples in this subset.

Test signals: use `scripts/kconfig/merge_config.sh` or equivalent to apply the fragment, then verify `/sys/kernel/sched_ext`, `/sys/kernel/btf/vmlinux`, BPF JIT, tracing, and sched_ext example load behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/Makefile -->
# sources/distributed-fs/ceph-client/tools/sched_ext/Makefile

Purpose: builds sched_ext C example schedulers and their BPF struct_ops programs. It handles libbpf, bpftool, `vmlinux.h` generation, BPF object linking, skeleton/subskeleton generation, final C loader binaries, installation, cleanup, and help text.

Important APIs/variables/targets: includes tools build infrastructure and architecture makefiles. Key paths are `OUTPUT_DIR`, `OBJ_DIR`, `INCLUDE_DIR`, `BPFOBJ_DIR`, `SCXOBJ_DIR`, `BINDIR`, `BPFOBJ`, `HOST_BPFOBJ`, `RESOLVE_BTFIDS`, and `DEFAULT_BPFTOOL`. `VMLINUX_BTF_PATHS` searches build outputs, `../../vmlinux`, `/sys/kernel/btf/vmlinux`, and `/boot/vmlinux-$(uname -r)`. `BPF_CFLAGS` sets target arch, endian, include paths, system include fallbacks, and `-target bpf` compile flags. `c-sched-targets` lists produced schedulers.

Control flow: the default target builds `all_targets`. The Makefile selects clang when `LLVM` is set and derives target flags for cross compilation. It builds host and target libbpf as needed, builds bpftool, generates `vmlinux.h`, compiles each `%.bpf.c` into a BPF object, runs bpftool link stabilization and `diff` on linked objects, emits skeleton headers, then compiles each user-space `%.c` loader and links it with libbpf. `install` copies binaries under `/usr/local/bin` in `DESTDIR`.

State and persistence: all generated artifacts are under `build/` by default or `$(O)/build`. Generated skeleton headers and `vmlinux.h` live under the output include directory. `clean` removes output trees and stray root-level generated files.

Dependencies and integration: depends on clang for BPF, libelf, zlib, pthread, libbpf sources under `tools/lib/bpf`, bpftool under `tools/bpf/bpftool`, generated kernel headers when available, and a discoverable vmlinux BTF source. It integrates the headers in `include/scx` and includes `include/bpf-compat` to paper over distro header issues for BPF builds.

Risks: hard failure if no `VMLINUX_BTF` is found. Cross builds have separate host/target libbpf paths and can fail if host tools are unavailable. `get_sys_includes` depends on compiler diagnostic format. The skeleton generation assumes repeated bpftool linking converges and verifies it with `diff`.

Test signals: `make help`, `make LLVM=1`, individual scheduler targets, `O=/tmp/sched_ext make all`, missing-vmlinux failure, cross compile with `CROSS_COMPILE`, and successful execution of built schedulers are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/bpf-compat/gnu/stubs.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/bpf-compat/gnu/stubs.h

Purpose: dummy `gnu/stubs.h` used only during BPF compilation to avoid accidental inclusion of glibc architecture stubs that may require missing 32-bit development headers.

Important APIs/functions: no symbols or declarations; the file intentionally provides an empty compatibility header.

Control flow: none.

State and persistence: none.

Dependencies and integration: placed before system include directories by `BPF_CFLAGS` in the sched_ext Makefile. It intercepts `/usr/include/gnu/stubs.h` when clang compiles `-target bpf` and `__x86_64__` is not defined.

Risks: it is safe only because the real glibc stubs content is irrelevant to these BPF programs. If future included headers genuinely depend on glibc stubs declarations, this shim could mask a real requirement.

Test signals: BPF builds on x86 systems without 32-bit glibc-devel installed should pass; removing this file should reproduce the missing `stubs-32.h` class of failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/bpf-compat/gnu/stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.bpf.h

Purpose: BPF-side compatibility header for BPF arena address-space pointers, arena allocation kfuncs, and portable loop break helpers.

Important APIs/macros: defines `PAGE_SIZE` from `__PAGE_SIZE`, `__arena`, `__arena_global`, `cast_kern()`, and `cast_user()` depending on compiler support for `__BPF_FEATURE_ADDR_SPACE_CAST`. When unavailable, `bpf_addr_space_cast()` emits raw BPF address-space-cast instructions through inline assembly. Declares weak arena kfuncs `bpf_arena_alloc_pages()`, `bpf_arena_free_pages()`, and `bpf_arena_reserve_pages()`. Defines `can_loop`, `cond_break`, and `cond_break_label` using `may_goto` or raw instruction encoding, plus `bpf_preempt_disable()`, `bpf_preempt_enable()`, and `bpf_arena_mapping_nr_pages()`.

Control flow: compile-time feature tests select either native LLVM address-space casts or inline assembly fallback. Loop helpers expand into verifier-aware control-flow constructs that can break portable BPF loops.

State and persistence: no persistent state. It controls pointer address-space annotations and generated BPF instructions at compile time.

Dependencies and integration: included by BPF code through `common.bpf.h` paths when arena functionality is needed. It depends on BPF kfunc availability in the running kernel and compiler feature macros.

Risks: raw instruction emission is architecture and verifier sensitive. Weak kfuncs may be unavailable at load/runtime, so users must gate behavior. `PAGE_SIZE` fallback assumes `__PAGE_SIZE` exists in generated BTF context.

Test signals: compile BPF programs with old and new LLVM, with and without `__BPF_FEATURE_ADDR_SPACE_CAST`, and load on kernels with and without arena kfuncs. Verifier acceptance of loops using `cond_break` is a key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.h

Purpose: user-space counterpart for BPF arena code, allowing shared headers to compile outside BPF while treating arena annotations and casts as no-ops.

Important APIs/macros: defines `arena_container_of()`, includes `<sys/user.h>` to get `PAGE_SIZE`, defines empty `__arena`, `__arg_arena`, `cast_kern()`, and `cast_user()`, provides weak `arena[1]`, fallback `offsetof`, and a stub `bpf_arena_alloc_pages()` returning `NULL`.

Control flow: none beyond the inline stub allocation function.

State and persistence: the weak `arena` symbol is a compile/link placeholder. No runtime persistent state.

Dependencies and integration: included by user-space `common.h`. It lets code that names arena-qualified pointers or helpers compile in loaders and tests without pulling in BPF-only declarations.

Risks: user-space arena allocation always returns `NULL`; shared code must not assume it can allocate real arena memory outside BPF. Empty annotations may hide type/address-space issues that only appear in BPF builds.

Test signals: compile user-space sched_ext loaders and any shared arena-using code; ensure no accidental user-space runtime path depends on successful `bpf_arena_alloc_pages()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/bpf_arena_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.bpf.h

Purpose: central BPF-side sched_ext support header. It imports `vmlinux.h`, declares sched_ext and BPF kfuncs, provides struct_ops section macros, safe verifier-friendly pointer helpers, kptr/list/rbtree/cpumask/task/cgroup declarations, CPU iterators, time helpers, READ/WRITE_ONCE, math helpers, task-weight scaling, random helper, and scheduler clock accessors.

Important APIs/macros: `BPF_STRUCT_OPS()` and `BPF_STRUCT_OPS_SLEEPABLE()` define struct_ops program sections. `scx_bpf_exit()`, `scx_bpf_error()`, and `scx_bpf_dump()` wrap bstr kfuncs with variadic formatting. `RESIZABLE_ARRAY()`, `MEMBER_VPTR()`, and `ARRAY_ELEM_PTR()` are used heavily by sched_ext examples to satisfy verifier bounds requirements. It declares kfuncs such as `scx_bpf_create_dsq()`, `scx_bpf_select_cpu_dfl()`, `scx_bpf_dispatch_nr_slots()`, `scx_bpf_kick_cpu()`, DSQ iterators, cpuperf kfuncs, cpumask kfuncs, task/cgroup kfuncs, and BPF object/list/rbtree helpers.

Control flow: mostly inline helpers and macros. CPU iterator definitions wrap `bpf_iter_bits`. Time comparison helpers use signed subtraction. `is_migration_disabled()` handles the ambiguity introduced by BPF execution disabling migration. Clock helpers use CO-RE shadow structs for `rq` and optional IRQ/paravirt accounting fields.

State and persistence: no persistent data of its own, but it declares extern kernel symbols such as `runqueues`, weak `cpu_irqtime`, and kconfig variables. It gives BPF programs access to mutable kernel scheduler state through kfuncs and CO-RE reads.

Dependencies and integration: requires bpftool-generated `vmlinux.h`, libbpf BPF helper headers, `user_exit_info.bpf.h`, generated enum definitions, and finally includes `compat.bpf.h` plus `enums.bpf.h`. It is the foundational include for all sched_ext BPF examples in this subset.

Risks: many helpers depend on kernel version and weak kfunc availability. Verifier-friendly macros return `NULL` on failed bounds proof and require immediate checks. Clock accessors require correct callback context and rq locking assumptions. The bstr wrappers rely on format checking but still pass raw values to kernel kfuncs.

Test signals: BPF compile and verifier load across kernel versions, especially with changed sched_ext kfunc signatures, missing optional fields, old clang/pahole enum handling, and examples using resizable arrays and rbtree/list helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.h

Purpose: central user-space sched_ext support header used by loader programs.

Important APIs/macros: defines fixed-width typedef aliases (`u8`, `u16`, `u32`, `u64`, `s8`, `s16`, `s32`, `s64`), `SCX_BUG()` and `SCX_BUG_ON()` fatal-report macros, and `RESIZE_ARRAY()` for libbpf skeleton data-section resizing that matches BPF-side `RESIZABLE_ARRAY()`.

Control flow: `SCX_BUG()` prints file/line and optional `errno` text, prints a formatted message, then exits. `RESIZE_ARRAY()` sets map value size for a custom data section and refreshes the skeleton pointer with `bpf_map__initial_value()`.

State and persistence: no persistent state. It mutates libbpf skeleton map sizes and initial-value pointers before load.

Dependencies and integration: includes generated enum definitions, user-exit handling, user-space compatibility helpers, enum initialization helpers, and arena stubs. All C loaders in this subset include it either directly or through skeleton workflows.

Risks: `SCX_BUG()` exits immediately and is intended for fatal loader errors. `RESIZE_ARRAY()` must be called before load and must match BPF declarations; incorrect element counts produce malformed data-section expectations.

Test signals: user-space scheduler loader builds, successful skeleton open/load after resizing arrays, and intentional fatal-path checks such as invalid CPU counts or missing BTF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.bpf.h

Purpose: BPF-side compatibility layer for sched_ext kernel API evolution.

Important APIs/macros: `__COMPAT_ENUM_OR_ZERO()` checks enum value existence. It wraps renamed or changed kfuncs including task cgroup lookup, DSQ move/consume/dispatch variants, cpumask populate, DSQ peek fallback, sub-dispatch, enqueue CPU-selected detection, `scx_bpf_now()`, event counters, NUMA-aware idle CPU helpers, current-task lookup, packed-argument variants of `scx_bpf_select_cpu_and()` and `scx_bpf_dsq_insert_vtime()`, boolean-returning `scx_bpf_dsq_insert()`, task slice/vtime setters, local reenqueue, generic DSQ reenqueue, and `SCX_OPS_DEFINE()`.

Control flow: wrappers use `bpf_ksym_exists()`, `bpf_core_type_exists()`, and `bpf_core_enum_value_exists()` to choose the best available implementation at load/runtime. Some fallbacks directly read or write task fields when newer authority-checking kfuncs are absent.

State and persistence: no persistent state. It changes generated BPF call paths based on kernel features.

Dependencies and integration: included at the tail of `common.bpf.h`, so every sched_ext BPF example gets these wrappers. It depends on weak kfunc declarations, CO-RE type/enum detection, and generated `HAVE_*` macros.

Risks: compatibility branches can hide behavior changes across kernel versions. Some fallbacks return success after void older kfunc calls, which differs from newer boolean semantics. Generic reenq fallback intentionally errors if an unsupported DSQ reenqueue is requested.

Test signals: load the same BPF examples on kernels before and after sched_ext renames/signature changes, especially v6.13, v6.15, v6.19, v6.20, and v7.1-related paths noted in comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.h

Purpose: user-space compatibility layer for sched_ext loader programs, primarily using vmlinux BTF to adapt skeleton struct_ops fields and enum values to the running kernel.

Important APIs/macros: `__COMPAT_load_vmlinux_btf()`, `__COMPAT_read_enum()`, `__COMPAT_has_ksym()`, and `__COMPAT_struct_has_field()` query kernel BTF. `SCX_OPS_FLAG()` and `SCX_PICK_IDLE_FLAG()` expose enum-derived flags. `scx_hotplug_seq()` reads `/sys/kernel/sched_ext/hotplug_seq`. `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, and `SCX_OPS_ATTACH()` wrap skeleton open, enum initialization, optional op nulling for unsupported fields, UEI sizing, load, and struct_ops attach.

Control flow: loaders call `SCX_OPS_OPEN()` before setting rodata/options. The macro verifies the minimum `sched_ext_ops.dump` field, opens the skeleton, initializes hotplug sequence and generated enums, then conditionally disables callbacks not supported by the running kernel. Load and attach macros complete the lifecycle.

State and persistence: caches `__COMPAT_vmlinux_btf` in a weak global. Reads but does not persist hotplug sequence state.

Dependencies and integration: requires libbpf BTF APIs, `fcntl`, `unistd`, generated enum helpers, and `user_exit_info.h`. It is used by all sched_ext C loaders in this subset through `common.h`.

Risks: BTF must be available and accurate. `SCX_BUG_ON()` terminates on missing required BTF operations. Compatibility nulling can silently disable callbacks with only a warning, so behavior may differ on older kernels.

Test signals: run loaders against kernels with and without newer `sched_ext_ops` fields such as `cgroup_set_bandwidth`, `cgroup_set_idle`, and sub-scheduler fields; validate warnings and successful attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enum_defs.autogen.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enum_defs.autogen.h

Purpose: generated feature-definition header declaring which sched_ext enum constants were known when the headers were generated.

Important APIs/macros: `HAVE_*` macros cover public constants, CPU preemption reasons, dequeue/enqueue flags, DSQ IDs and flags, task states, exit codes, kfunc masks, kick flags, ops flags, idle-pick flags, slices, reenqueue flags, rq flags, scheduling state, task-group state, and wake flags.

Control flow: none; it is compile-time feature data.

State and persistence: generated static header content.

Dependencies and integration: consumed by `common.bpf.h` and compatibility code to guard references to enum names that may be absent from generated `vmlinux.h` or running kernels.

Risks: it must be regenerated when enum coverage changes. Stale `HAVE_*` definitions can make compatibility wrappers take incorrect branches or reference unavailable enum values.

Test signals: regenerate with the upstream script, compile all sched_ext examples, and ensure compatibility paths for gated enum constants compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enum_defs.autogen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.bpf.h

Purpose: generated BPF-side enum-value indirection header for sched_ext constants.

Important APIs/macros: declares weak `const volatile u64 __SCX_*` variables and maps public macro names such as `SCX_SLICE_DFL`, `SCX_DSQ_GLOBAL`, `SCX_DSQ_LOCAL`, task state constants, and rq flags to those weak variables.

Control flow: none; macros substitute constants with load-time initialized weak variables.

State and persistence: BPF rodata-style weak variables hold enum values supplied/relocated by the loader environment.

Dependencies and integration: included through `enums.bpf.h`. User-space generated enum initialization populates matching skeleton fields so BPF code can use current kernel enum values without hard-coding them.

Risks: if initialization is missing, constants may remain zero and cause severe scheduler misbehavior. Weak volatile variables also reduce compile-time constant folding.

Test signals: verify `SCX_ENUM_INIT()` in user-space loaders populates these fields and that BPF examples behave correctly on kernels with changed enum numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.h

Purpose: generated user-space enum initialization support for sched_ext skeletons.

Important APIs/functions: this header defines the generated side of `SCX_ENUM_INIT()` used by `compat.h` during `SCX_OPS_OPEN()`. It maps kernel BTF enum names and entries into skeleton rodata variables matching the BPF-side weak `__SCX_*` variables.

Control flow: the generated macro/function sequence reads enum values from vmlinux BTF through compatibility helpers and writes them into the skeleton before load.

State and persistence: mutates skeleton rodata initial values only; no persistent external state.

Dependencies and integration: included by `enums.h`, which is included by `common.h`. It relies on `compat.h` enum-reading helpers and must stay in sync with `enums.autogen.bpf.h`.

Risks: stale generation or missing BTF enum entries can leave values zero or fallback values. Because many schedulers use `SCX_SLICE_DFL`, DSQ IDs, and ops flags, bad enum initialization can break scheduling semantics.

Test signals: build loaders, inspect rodata values after `SCX_OPS_OPEN()`, and load on kernels with both matching and shifted enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.autogen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.bpf.h

Purpose: lightweight BPF-side wrapper that exposes generated sched_ext enum indirections to BPF programs.

Important APIs/functions: includes `enums.autogen.bpf.h`; it does not define independent logic.

Control flow: none.

State and persistence: delegates weak enum-value variables to the generated header.

Dependencies and integration: included at the tail of `common.bpf.h` after compatibility declarations, so all BPF examples can use enum-like macros.

Risks: any issue is inherited from generated enum headers. The small wrapper is easy to overlook when regenerating files.

Test signals: BPF examples compile and link with generated enum variables available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.h

Purpose: lightweight user-space wrapper exposing generated sched_ext enum initialization to loaders.

Important APIs/functions: includes `enums.autogen.h`; no independent functions are defined.

Control flow: none in this wrapper.

State and persistence: delegates skeleton enum initialization behavior to the generated header.

Dependencies and integration: included by `common.h`; loaders get `SCX_ENUM_INIT()` through this path.

Risks: wrapper must stay present for include stability even though the generated file carries the implementation.

Test signals: C loaders compile and `SCX_OPS_OPEN()` can call generated enum initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.bpf.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.bpf.h

Purpose: BPF-side definitions for sharing sched_ext exit status, message, and debug dump data with user space.

Important APIs/macros: `UEI_DEFINE(name)` declares a resizable dump array, dump length rodata, and `struct user_exit_info` in `.data`. `UEI_RECORD(name, ei)` copies `reason`, `msg`, and `dump` from `struct scx_exit_info`, conditionally records `exit_code`, and publishes `kind` with an atomic compare-and-swap as a memory barrier.

Control flow: BPF schedulers call `UEI_RECORD()` from their `.exit` callback. User space polls the shared data through the skeleton.

State and persistence: BPF `.data` holds the exit info and dump buffer for the lifetime of the loaded scheduler.

Dependencies and integration: includes `vmlinux.h`, `bpf_core_read.h`, and `user_exit_info_common.h`. All sched_ext examples in this subset use `UEI_DEFINE(uei)` and record exit information.

Risks: dump size must be set correctly from user space or defaults are used. Atomic publication assumes readers observe `kind` after reason/message/dump have been copied.

Test signals: force normal exit, BPF error exit, and dump-producing exit; verify `UEI_EXITED()` and `UEI_REPORT()` in user space observe complete data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.h

Purpose: user-space companion for sched_ext exit reporting.

Important APIs/macros: `UEI_SET_SIZE()` sizes the BPF dump buffer using `exit_dump_len` or `UEI_DUMP_DFL_LEN`. `UEI_EXITED()` atomically reads the shared `kind`. `UEI_REPORT()` prints an optional debug dump, prints exit reason/message, and returns `exit_code`. It duplicates selected `scx_exit_code` and `uei_ecode_mask` values and defines `UEI_ECODE_USER()`, `UEI_ECODE_SYS_RSN()`, `UEI_ECODE_SYS_ACT()`, and `UEI_ECODE_RESTART()`.

Control flow: loaders call `SCX_OPS_LOAD()`, which handles UEI sizing; their monitor loops stop when `UEI_EXITED()` becomes true; after detach they call `UEI_REPORT()` and optionally restart on hotplug restart codes.

State and persistence: reads and reports BPF `.data` state through the skeleton. No external persistence.

Dependencies and integration: depends on `RESIZE_ARRAY()` from `common.h` and `user_exit_info_common.h`. Used by all C sched_ext loaders in the subset.

Risks: `UEI_REPORT()` assumes dump pointer fields generated by libbpf skeleton naming conventions. Long dumps go to stderr. Restart handling is left to each loader.

Test signals: verify default and custom dump lengths, normal exit, restart exit code handling in loaders that loop on `UEI_ECODE_RESTART()`, and BPF error message display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info_common.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info_common.h

Purpose: shared BPF/user-space definition of sched_ext exit info sizes and payload shape.

Important APIs/types: `enum uei_sizes` defines `UEI_REASON_LEN` 128, `UEI_MSG_LEN` 1024, and `UEI_DUMP_DFL_LEN` 32768. `struct user_exit_info` contains `kind`, `exit_code`, `reason[]`, and `msg[]`.

Control flow: none.

State and persistence: defines the shared memory layout used in BPF `.data` maps and user-space skeleton views.

Dependencies and integration: optionally includes `../vmlinux.h` for LSP mode. Included by both BPF and user-space UEI headers.

Risks: changing field order or sizes is an ABI change for skeleton-shared data. `s64` must be available from BPF or user-space typedef context.

Test signals: compile both BPF and C users, inspect skeleton layout, and verify exit info fields retain expected sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.bpf.c

Purpose: BPF implementation of a central FIFO sched_ext scheduler where one central CPU makes dispatch decisions for all CPUs, demonstrates LOCAL_ON dispatching, tickless infinite slices, timer-driven preemption, and kthread priority handling.

Important APIs/types/functions: rodata inputs are `central_cpu`, `nr_cpu_ids`, and `slice_ns`. State includes `central_q` BPF queue of PIDs, resizable arrays `cpu_gimme_task` and `cpu_started_at`, a `central_timer`, counters, and `UEI_DEFINE(uei)`. Struct_ops callbacks are `central_select_cpu()`, `central_enqueue()`, `central_dispatch()`, `central_running()`, `central_stopping()`, `central_init()`, and `central_exit()`.

Control flow: wakeups are steered to the central CPU. Enqueue sends single-CPU kthreads directly to local DSQs with preemption; other tasks are pushed into `central_q` or fallback DSQ on overflow, and the central CPU is kicked. Central dispatch services other CPUs that set `cpu_gimme_task`, then itself. Non-central CPUs consume fallback tasks, mark themselves as needing work, and kick the central CPU. The timer periodically checks CPU runtime against `slice_ns` and kicks CPUs that should rotate.

State and persistence: BPF maps and globals persist while the scheduler is loaded. `cpu_started_at` tracks running slice start times, `cpu_gimme_task` is the request bitmap, and counters expose behavior to user space.

Dependencies and integration: uses sched_ext DSQs, BPF queue maps, BPF timers, task lookup by PID, CPU kicks, and `SCX_OPS_ENQ_LAST`. User space must resize arrays to `nr_cpu_ids` before load.

Risks: central scheduling can bottleneck on one CPU. Queue overflow falls back to DSQ 0. PID lookup can fail after enqueue, counted as lost. BPF timer CPU pinning falls back when unsupported, but pinned-mode mismatch is considered fatal. Correctness relies on dispatch buffer slot availability and explicit retry kicks.

Test signals: run with default and nonzero central CPU, observe counters for queued/dispatch/retry/mismatch/overflow, test with nohz_full for tickless behavior, verify kthreads remain forward-progress safe, and trigger hotplug restart handling from user space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.c

Purpose: user-space loader and monitor for `scx_central.bpf.c`.

Important APIs/functions: uses `SCX_OPS_OPEN()`, `RESIZE_ARRAY()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, and `UEI_REPORT()`. Options are `-s` slice microseconds, `-c` central CPU, `-v`, and `-h`.

Control flow: install signal handlers, open skeleton, initialize rodata (`central_cpu`, `nr_cpu_ids`, `slice_ns`), parse options, validate central CPU, resize `cpu_gimme_task` and `cpu_started_at`, load and attach struct_ops, then print BPF counters once per second until signal or UEI exit. On exit, detach, report UEI, destroy the skeleton, and restart when the exit code requests restart.

State and persistence: no external persistence. Runtime state includes `exit_req`, libbpf verbosity, skeleton rodata/data/bss, and the struct_ops link.

Dependencies and integration: depends on generated `scx_central.bpf.skel.h`, libbpf, `common.h`, sched_ext sysfs/BTF, and possible CPU count from libbpf.

Risks: uses `assert()` for CPU count assumptions; assertions can be compiled out. Restart uses `goto restart` and re-parses options. Invalid central CPU exits after destroying the skeleton.

Test signals: CLI parse tests, invalid central CPU rejection, successful attach, per-second stats output, SIGINT/SIGTERM cleanup, and hotplug restart path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_central.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.bpf.c

Purpose: minimal sched_ext scheduler that funnels runnable work to CPU0 through a custom DSQ to stress bypass/load-balancer behavior.

Important APIs/types/functions: rodata `nr_cpus`, `UEI_DEFINE(uei)`, custom DSQ ID `DSQ_CPU0`, per-CPU array `stats` with local and CPU0 counters, `stat_inc()`, and callbacks `cpu0_select_cpu()`, `cpu0_enqueue()`, `cpu0_dispatch()`, `cpu0_init()`, and `cpu0_exit()`.

Control flow: `select_cpu` always returns CPU0. `enqueue` sends tasks already on CPU0 to `DSQ_CPU0`; tasks that cannot run on CPU0 are queued to their local DSQ and counted separately. `dispatch` only moves from `DSQ_CPU0` when running on CPU0. `init` creates the custom DSQ.

State and persistence: per-CPU `stats` map persists while loaded; UEI stores exit data. No filesystem state.

Dependencies and integration: uses sched_ext DSQs, BPF per-CPU maps, and common UEI exit reporting. User space reads the stats map and sets `nr_cpus`.

Risks: intentionally creates pathological CPU0 concentration and can trigger stalls if bypass behavior fails. It ignores `enq_flags` for local fallback and always tries CPU0 as a hint.

Test signals: stats should show CPU0 versus local queueing, CPU0 should drain `DSQ_CPU0`, and stress tests should exercise bypass without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.c

Purpose: user-space loader and stats printer for the CPU0 sched_ext example.

Important APIs/functions: `read_stats()` reads the per-CPU `stats` map for two counters and sums them across possible CPUs. `main()` uses `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, and `UEI_REPORT()`.

Control flow: set libbpf logging and signal handlers, open skeleton, set `nr_cpus`, parse `-v`/`-h`, load and attach, print `local=` and `cpu0=` once per second, detach/report/destroy, and restart if UEI encodes a restart action.

State and persistence: no persistent state. Runtime state is the skeleton, BPF link, exit flag, and per-iteration stats buffer.

Dependencies and integration: requires generated skeleton, libbpf, sched_ext, and access to BPF maps. It relies on libbpf's possible CPU count matching the per-CPU map value layout.

Risks: uses a variable-length stack array `cnts[2][nr_cpus]`, which can be large on high-CPU systems. Map lookup failures are silently skipped in stats aggregation.

Test signals: successful load/attach, monotonic stats under load, signal cleanup, and restart-on-hotplug behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_cpu0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.bpf.c

Purpose: BPF scheduler implementing flattened hierarchical cgroup CPU control. It compounds active cgroup weights into a flat virtual-time competition, then schedules tasks inside each selected cgroup by weighted vtime or FIFO.

Important APIs/types/functions: rodata `nr_cpus`, `cgrp_slice_ns`, and `fifo_sched`; global `cvtime_now`; stats map; per-CPU `fcg_cpu_ctx`; cgroup local storage `fcg_cgrp_ctx`; task storage `fcg_task_ctx`; rbtree `cgv_tree` of `cgv_node`; stash map of kptr nodes. Key helpers include `cgrp_refresh_hweight()`, `cgrp_cap_budget()`, `cgrp_enqueued()`, `update_active_weight_sums()`, and `try_pick_next_cgroup()`. Struct_ops include select/enqueue/dispatch/runnable/running/stopping/quiescent/init_task/cgroup callbacks/init/exit.

Control flow: runnable/quiescent callbacks update active weight sums up the cgroup tree. Enqueue either bypasses tasks with restricted affinity into local/global fallback DSQs or inserts into a cgroup DSQ using FIFO/vtime and marks the cgroup queued in the rbtree. Dispatch keeps the current cgroup until its slice expires or empties, charges unused/used virtual time, drains fallback DSQ first, then repeatedly picks the lowest virtual-time cgroup from the rbtree and moves a task from that cgroup DSQ to local. Cgroup init creates a DSQ, storage, and rbtree node stash; exit destroys DSQ and removes stash.

State and persistence: BPF maps and kptr rbtree nodes persist while loaded. Cgroup storage tracks weights, active counts, runnable counts, hweight, child sums, task vtime, cgroup vtime delta, and queued state. Task storage tracks bypass charge points.

Dependencies and integration: uses sched_ext DSQs keyed by cgroup ID, cgroup local storage, task storage, BPF rbtree/kptr APIs, cgroup kfuncs, task weight scaling helpers, and UEI exit reporting. User space sets slice duration, FIFO mode, and CPU count.

Risks: comments acknowledge flattening can mishandle thundering-herd cgroups behind low-priority parents. Some operations are intentionally opportunistic/racy because BPF spin locks cannot cover complex map operations. Cgroup ID is treated as a DSQ ID despite DSQ width caveats. Exiting cgroups with nodes still in the rbtree are drained later in dispatch.

Test signals: cgroup weight ratio workloads, nested cgroup hierarchy benchmarks, FIFO vs weighted-vtime mode, cgroup creation/deletion, task cgroup moves, restricted-affinity tasks, and stats counters for enqueue/race/pick paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.c

Purpose: user-space loader and monitor for the flattened cgroup scheduler.

Important APIs/functions: parses options `-s`, `-i`, `-f`, `-v`, `-h`; `read_cpu_util()` computes CPU utilization from `/proc/stat`; `fcg_read_stats()` reads and sums the per-CPU stats map; main uses common sched_ext open/load/attach/UEI macros.

Control flow: open skeleton, initialize rodata (`nr_cpus`, default cgroup slice, FIFO flag), parse options, load/attach, then periodically read CPU utilization and BPF stats and print a monitoring line until signal or UEI exit. On exit, detach, report UEI, destroy, and restart on restart exit code.

State and persistence: keeps last `/proc/stat` sum/idle values to compute deltas and stores BPF stats snapshots in local arrays. No external persistent state.

Dependencies and integration: generated skeleton, libbpf, common sched_ext headers, `/proc/stat`, and `scx_flatcg.h` stat names/indices.

Risks: CPU utilization parsing assumes the first `/proc/stat` line format and uses simple tokenization. Large CPU counts affect per-CPU stats reads. Output is monitoring-oriented rather than structured.

Test signals: option parsing, CPU utilization sanity, stat counter changes under cgroup workloads, FIFO flag propagation, signal cleanup, and hotplug restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.h

Purpose: shared constants, statistic indices, stat names, and cgroup context layout for `scx_flatcg`.

Important APIs/types: defines `FCG_HWEIGHT_ONE` and `FCG_NR_STATS`; `enum fcg_stat_idx` enumerates local/global enqueue, activation/deactivation, hweight cache/update/race/skip, enqueue skip/race, current-cgroup selection outcomes, pick-next-cgroup outcomes, and failure counters. It defines `fcg_stat_names[]` under non-BPF builds. `struct fcg_cgrp_ctx` holds weight, active/runnable counts, child weight sum, hierarchical weight generation/value, task virtual time, cgroup virtual-time delta, and queued flag.

Control flow: none.

State and persistence: `struct fcg_cgrp_ctx` is persisted in BPF cgroup local storage by the BPF scheduler.

Dependencies and integration: included by both BPF and user-space flatcg code. Stat enum order must match user-space stat printing and BPF stat increments.

Risks: changing enum order without updating names breaks monitoring. Struct layout changes affect BPF storage expectations.

Test signals: compile both BPF and user-space users, validate stats names align with incremented indices, and inspect cgroup storage initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_flatcg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.bpf.c

Purpose: BPF core-scheduling demo that pairs CPUs and ensures each pair runs tasks from the same CPU cgroup during a batch window.

Important APIs/types/functions: rodata/resizable arrays `nr_cpu_ids`, `pair_batch_dur_ns`, `pair_cpu`, `pair_id`, and `in_pair_idx`; `struct pair_ctx` with spin lock, current cgid, start time, draining, active and preempted masks; cgroup queue maps `top_q`, `cgrp_q_arr`, `cgrp_q_idx_hash`, `cgrp_q_len`, and IDR-like busy/cursor arrays. Main callbacks are `pair_enqueue()`, `pair_dispatch()`, `pair_cpu_acquire()`, `pair_cpu_release()`, `pair_cgroup_init()`, `pair_cgroup_exit()`, and `pair_exit()`.

Control flow: enqueue maps a task's cgroup to a per-cgroup FIFO and pushes the cgroup ID to `top_q` when it transitions from empty to non-empty. Dispatch clears this CPU's active bit, expires/drains the current cgroup when the batch expires or empties, waits for the pair CPU or higher-priority preemption to clear, opportunistically selects the next non-empty cgroup, then pops a PID from that cgroup queue and dispatches it globally. CPU release marks the pair preempted and kicks the pair CPU with wait; acquire clears preemption and kicks the pair again.

State and persistence: BPF arrays, queues, hash maps, counters, and pair contexts persist while loaded. Per-cgroup queue indices are allocated on cgroup init and freed on exit.

Dependencies and integration: uses sched_ext cgroup callbacks, CPU acquire/release callbacks, BPF queues, array-of-maps populated by user space, spin locks, task lookup by PID, and shared `scx_pair.h` limits.

Risks: the implementation is intentionally complex due to BPF map and synchronization limitations. It does not handle dequeues from per-cgroup PID queues, so missing PIDs are retried. Top queue can contain duplicate cgroup IDs. Requires even CPU count and correct user-space pairing arrays.

Test signals: cgroup workloads pinned to paired CPUs, higher-priority scheduler preemption, odd CPU count rejection in user space, queue overflow/error counters, and pair consistency under different stride values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.c

Purpose: user-space loader for the CPU-pair core-scheduling demo.

Important APIs/functions: parses `-S` stride, `-v`, and `-h`; uses `RESIZE_ARRAY()` for `pair_cpu`, `pair_id`, and `in_pair_idx`; creates inner queue maps for `cgrp_q_arr`; uses `SCX_OPS_OPEN/LOAD/ATTACH` and UEI reporting.

Control flow: open skeleton, set possible CPU count and batch duration, parse stride, reject non-positive stride and odd CPU counts, resize pair arrays, compute pair relationships by stride, load skeleton, populate the array-of-maps with `MAX_CGRPS` BPF queue maps, attach, print counters periodically, then detach/report/destroy and restart on restart exit code.

State and persistence: no external persistence. Runtime state includes generated pairing arrays and inner BPF queue map fds installed into the outer map.

Dependencies and integration: generated skeleton, libbpf map creation/update APIs, common sched_ext headers, and `scx_pair.h`.

Risks: invalid stride can create self-pairs or three-CPU conflicts and is guarded by `SCX_BUG_ON()`. Initializing many cgroup queues is potentially slow and can be interrupted by `exit_req`. The loader requires even possible CPU count.

Test signals: default pairing, custom stride pair layout, invalid stride errors, array-of-maps population success, stats output under cgroup workloads, and signal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.h -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.h

Purpose: shared limits for the pair scheduler.

Important APIs/constants: defines `MAX_CGRPS` as 1024 and `MAX_QUEUED` as 4096.

Control flow: none.

State and persistence: constants size BPF maps and user-space-created queue maps.

Dependencies and integration: included by both `scx_pair.bpf.c` and `scx_pair.c`; values must match across BPF and loader.

Risks: fixed limits can reject or fail workloads with too many cgroups or queued tasks. Increasing them raises memory and initialization cost.

Test signals: cgroup counts near `MAX_CGRPS`, per-cgroup queue depth near `MAX_QUEUED`, and loader memory/map creation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_pair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.bpf.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.bpf.c

Purpose: BPF implementation of a five-level FIFO queue sched_ext example and stress-test scheduler. It demonstrates BPF queue maps, task storage, weighted queue selection, core-sched ordering, cpuperf control, DSQ iteration/move APIs, cgroup and sub-scheduler callbacks, dumps, timers, and deliberate failure/stall test knobs.

Important APIs/types/functions: rodata knobs include `slice_ns`, stall intervals, dispatch infinite-loop threshold, dispatch batch, high-priority boosting, printing flags, sub-cgroup ID, disallowed TGID, dump suppression, always-enqueue-immediate, and immediate stress interval. Maps include five FIFO `qmap` queues, `queue_arr`, task storage `task_ctx_stor`, per-CPU `cpu_ctx_stor`, monitor and low-priority timers, plus `dump_store`. Key callbacks are `qmap_select_cpu()`, `qmap_enqueue()`, `qmap_dequeue()`, `qmap_dispatch()`, `qmap_tick()`, `qmap_core_sched_before()`, `qmap_init_task()`, dump callbacks, cgroup callbacks, CPU hotplug callbacks, `qmap_init()`, `qmap_exit()`, `qmap_sub_attach()`, and `qmap_sub_detach()`.

Control flow: weights map to queue indices 0-4. `select_cpu` tries direct local dispatch for eligible tasks. `enqueue` handles reenqueues, optional stall/error injection, per-task core-sched sequence assignment, immediate stress, local direct dispatch, low-priority DSQ path, direct dispatch when select_cpu was skipped, reenqueued task handling, and FIFO insertion with optional high-priority marking. `dispatch` first expedites high-priority tasks, consumes shared DSQ if possible, optionally triggers infinite loop behavior, then round-robins queues with exponentially larger dispatch counts and inserts popped PIDs into `SHARED_DSQ`. It kicks home CPUs for affinity mismatches. Timers monitor cpuperf/events, dispatch high-priority tasks from timer context, dump DSQs, and periodically reenq low-priority tasks.

State and persistence: BPF queues store PIDs, task storage stores force-local/high-priority/core-sched sequence, per-CPU storage stores dispatch cursor and cpuperf target, globals hold counters and queue sequence numbers, timers persist while the scheduler is loaded, and UEI stores exit info.

Dependencies and integration: uses sched_ext DSQ create/move/reenq APIs, task and cgroup kfuncs, BPF timers, cpumask/cpuperf/event kfuncs, core scheduling, cgroup bandwidth callbacks, sub-scheduler dispatch, CPU hotplug callbacks, and compatibility helpers for API drift.

Risks: it is a demo/stress scheduler, not production policy. PID queues cannot remove arbitrary dequeued tasks, so stale PID lookups are expected. Stall and infinite-loop knobs can intentionally trigger scheduler failures. Queue dumps destructively pop and restore, racing with enqueues. High-priority scans and timer dispatch add overhead. Some paths depend on optional newer kfuncs.

Test signals: run with each CLI knob, monitor counters for enqueue/dispatch deltas, trigger dump paths, use core scheduling, CPU hotplug, cgroup weight/bandwidth changes, low-priority nice workloads, high-priority boost with batch dispatch, and kernels with/without cpuperf and generic reenq kfuncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.c -->
# sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.c

Purpose: user-space loader, option parser, and monitor for the qmap sched_ext example.

Important APIs/functions: parses options for slice, error/stall injection, infinite-loop trigger, dispatch batch, DSQ/event printing, debug messages, high-priority boosting, sub-cgroup path, disallowed PID, exit dump length, dump suppression, partial switching, always-enqueue-immediate, immediate stress, verbosity, and help. Uses `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, `UEI_REPORT()`, and `__COMPAT_has_ksym()`.

Control flow: open skeleton, set default `slice_ns`, parse options into rodata/bss/struct_ops fields, resolve `-c` cgroup path with `stat()` and store inode as sub-cgroup ID, set flags for partial switching and always-immediate modes, load and attach, then print scheduler counters and optional cpuperf statistics once per second until signal or UEI exit. It detaches, reports, destroys, and exits without hotplug restart because qmap implements CPU online/offline callbacks.

State and persistence: no filesystem persistence. Runtime state is the skeleton, struct_ops link, signal flag, and BPF maps/globals exposed through skeleton fields.

Dependencies and integration: generated skeleton, libbpf, sched_ext common headers, `sys/stat.h` for cgroup inode lookup, and optional cpuperf ksym.

Risks: many options intentionally enable failure or pathological behavior. `-c` uses `st_ino` as cgroup ID and assumes the supplied path is a cgroup. Counters are read locklessly from BPF globals, so monitoring is approximate.

Test signals: option parsing coverage, cgroup sub-scheduler attachment with `-c`, stats output, cpuperf output only when ksym exists, signal cleanup, and expected no-restart behavior on CPU hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.c -->
