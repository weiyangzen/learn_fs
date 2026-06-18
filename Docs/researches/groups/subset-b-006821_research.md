# Research: subset-b-006821

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_synctypes.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_synctypes.py

## Research

This Python selftest verifies that bpftool's UAPI-derived type names, help text, RST documentation, and bash completion stay synchronized. It reads `tools/include/uapi/linux/bpf.h`, bpftool source files, bpftool documentation, and `bash-completion/bpftool`, then compares sets of map types, program attach types, cgroup attach types, command options, and common options. Environment variables such as `BPFTOOL_DIR`, `BPFTOOL_DOC_DIR`, `BPFTOOL_BASHCOMP_DIR`, and `INCLUDE_DIR` let the harness point at non-default build/source locations.

Important code is organized around parsers and extractors. `BlockParser`, `ArrayParser`, and `InlineListParser` scan enum blocks, `const bool` arrays, RST inline lists, help strings, macro-expanded help fragments, and bash-completion variable blocks. `FileExtractor` provides shared operations including `get_enum()`, `get_types_from_array()`, and `make_enum_map()`. Specialized extractors know the exact files and block names for bpftool maps, programs, cgroups, generic commands, main options, man pages, substitutions, and bash completion.

`main()` builds source truth from UAPI enums and bpftool arrays, normalizes deprecated cgroup storage map enum aliases to the names exposed by bpftool, and calls `verify()` for every expected pair. The only persistent state is process-local `retval`, which is set to `1` on any mismatch before `sys.exit(retval)`. Failures print the symmetric difference and the compared files, making the test signal a direct list of out-of-sync names. Risks are tight regex coupling to source/doc formatting, brittle block start/end markers, and manual normalization for enum aliases. Missing files or reordered formatting can fail before comparison, but that is useful because this test is intended to catch synchronization drift in bpftool's public interface.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_bpftool_synctypes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_btf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_btf.h

## Research

This header is a compact BTF raw-record construction helper for BPF selftests. It does not implement runtime logic; instead it provides macros that encode BTF type records and their payload words into `__u32` initializer streams used by raw BTF tests. `BTF_END_RAW` is a sentinel used by consumers to find the end of a raw fixture.

The main API surface mirrors kernel BTF kinds: `BTF_INFO_ENC()`, `BTF_TYPE_ENC()`, `BTF_TYPE_INT_ENC()`, `BTF_FWD_ENC()`, `BTF_TYPE_ARRAY_ENC()`, `BTF_STRUCT_ENC()`, `BTF_UNION_ENC()`, `BTF_VAR_ENC()`, `BTF_VAR_SECINFO_ENC()`, `BTF_MEMBER_ENC()`, `BTF_ENUM_ENC()`, `BTF_ENUM64_ENC()`, `BTF_TYPEDEF_ENC()`, pointer/qualifier encoders, function prototype/function encoders, float encoders, declaration-tag encoders, and type-tag encoders. `BTF_MEMBER_OFFSET()` packs bitfield size and bit offset into the member offset representation.

Control flow is entirely compile-time macro expansion. The header depends on BTF constants such as `BTF_KIND_INT`, `BTF_KIND_ARRAY`, and `BTF_MAX_VLEN` being visible to the including source. It has no state, persistence, allocation, or external side effects. Integration points are raw BTF tests that need dense fixture arrays without repeating the low-level bit packing.

Risks are semantic drift when the kernel BTF encoding changes or when a macro silently packs a value that exceeds the expected field width. Because these macros generate binary ABI fixtures, incorrect packing can make downstream tests fail in confusing verifier paths. Test signals come from consumers such as BTF verifier and dedup tests: successful kernel load, expected verifier errors, and exact raw BTF comparisons indirectly validate the macros.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_cpp.cpp -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_cpp.cpp

## Research

This C++ smoke test verifies that libbpf public headers, BTF APIs, generated skeletons, and selected C APIs are usable from C++ translation units. It includes `<bpf/libbpf.h>`, `<bpf/bpf.h>`, `<bpf/btf.h>`, Linux UAPI headers, and generated skeleton headers `test_core_extern.skel.h` and `struct_ops_module.skel.h`.

The key local abstraction is `template <typename T> class Skeleton`, an RAII wrapper around generated skeleton types. It stores a `T *`, destroys it in the destructor with `T::destroy()`, and exposes `open()`, `load()`, `attach()`, `detach()`, `operator->()`, and `get()`. `try_skeleton_template()` opens `test_core_extern`, edits data variables, loads and attaches it, checks a kconfig field, validates the program name `handle_sys_enter`, manually replaces a link, and detaches.

`main()` then exercises representative libbpf entry points: `libbpf_set_print()`, `bpf_prog_get_fd_by_id()`, `btf__new()`, `btf_dump__new()`, generated `open_and_load()`/`destroy()` helpers for two skeletons, and `bpf_enable_stats(BPF_STATS_RUN_TIME)`. State is limited to skeleton object lifetimes, a BTF object pointer, link replacement, and an optional stats FD closed on success. The program prints failures for smoke-test diagnostics and `DONE!` at the end.

Dependencies include C++ compilation, generated skeleton headers, kernel BPF support, and libbpf symbols with C++-safe declarations. Risks are mostly compile/link regressions, null skeleton handling after failed loads, and runtime privilege/configuration differences for stats or attach operations. Test signals are successful compilation and execution without crashes, expected stderr messages for unavailable kernel features, and the final `DONE!`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_cpp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_doc_build.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_doc_build.sh

## Research

This shell selftest validates that bpftool documentation can be built from the selftests tree. It is a small harness around the bpftool documentation Makefile rather than a unit test for BPF behavior.

Control flow is linear. The script enables `set -e`, computes `SCRIPT_DIR`, builds `OUTPUT` as an absolute `tools/testing/selftests/bpf/tools` directory, and derives `KDIR_ROOT_DIR` by walking five levels up to the kernel source root. It then invokes `make` in `tools/bpf/bpftool/Documentation` with `OUTPUT`, `srctree`, `PYTHON`, `RST2MAN_OPTS=--exit-status=1`, and `doc`. The `RST2MAN_OPTS` value makes docutils warnings fatal, so formatting or reference issues fail the test.

There is no persistent state beyond generated documentation/build artifacts under the selected output directory. Dependencies include GNU make, Python, docutils/rst2man, the bpftool documentation sources, and a valid kernel source layout. Integration points are the BPF selftests harness and bpftool's documentation build target.

Risks are environment sensitivity and toolchain availability. A system with missing `rst2man`, incompatible Python, or a nonstandard source tree can fail without indicating a bpftool documentation regression. The main test signal is the exit status of `make doc`; any warning promoted by `--exit-status=1` or build failure terminates the script through `set -e`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_doc_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_ftrace.sh

## Research

This shell test checks ftrace interaction needed by BPF selftests, specifically that enabling fentry tracing on `bpf_fentry_test1` is visible in the trace pipe after triggering the test module path. It also behaves as an environment gate for missing tracefs or missing kernel support.

The script locates tracefs at `/sys/kernel/tracing`, skips with exit code `4` if unavailable, and checks whether `bpf_fentry_test1` appears in `available_filter_functions`. It installs a `trap` that disables tracing, clears the trace buffer, removes the ftrace filter, and removes `bpf_testmod`. The main flow loads `bpf_testmod`, writes `bpf_fentry_test1` into `set_ftrace_filter`, enables `function` tracing, triggers the module by reading `/sys/kernel/bpf_testmod`, disables tracing, and greps `trace` for `bpf_fentry_test1`. If the symbol is absent from the trace output, it prints a failure and returns nonzero.

State side effects are all kernel/debugfs scoped: loaded module state, ftrace current tracer, function filter, trace buffer contents, and the module sysfs read trigger. Dependencies include tracefs, ftrace function tracer support, root privileges, `modprobe`, and the `bpf_testmod` module exposing the sysfs trigger.

Risks are host configuration sensitivity, symbol name changes, concurrent tracing users, and cleanup races if another test manipulates the same ftrace files. Test signals are explicit skip output for unsupported environments and a successful grep of the trace buffer after the sysfs read trigger.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_iptunnel_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_iptunnel_common.h

## Research

This header defines shared constants, protocol structures, and map declarations for BPF IP tunnel selftests. It is included by BPF programs and/or user-space harness code that need common tunnel metadata layout.

The central types are `struct geneve_opt`, `struct vxlan_metadata`, and `struct bpf_fou_encap`, which model tunnel option and encapsulation metadata. The header defines tunnel port constants for VXLAN, GENEVE, FOU, and GUE, plus `PROTO_IPIP` and `PROTO_IPV6`. It also declares BPF maps using libbpf-style SEC annotations: `rxcnt` as a one-entry array of packet counters, `vip2tnl` as a hash from a virtual IP key to tunnel endpoint data, and `jmp_table` as a program array with two entries for tail calls or dispatch.

Control flow is absent; map definitions become ELF map metadata at compile time. Runtime state is the kernel map content once a BPF object using this header is loaded. The maps integrate with selftest loaders that populate tunnel endpoint data, read packet counters, and attach/dispatch programs through the program array.

Dependencies include BPF helper headers, `struct vip`, `struct iptnl_info`, `struct geneve_opt`, and `struct bpf_fou_encap` consumers matching the same ABI layout. Risks are structure layout drift, endian/packing assumptions for tunnel metadata, and mismatched `max_entries` or key/value sizes between BPF programs and user-space tests. Test signals are successful object load, successful map population, tail-call behavior through `jmp_table`, and expected RX counter updates after tunnel traffic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_iptunnel_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmod.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmod.sh

## Research

This shell harness runs BPF selftests that require a special kernel module under `test_kmods/`, then unloads the module afterward. It is primarily a build/load/test orchestration script.

The script enables `set -e` and computes paths relative to the selftests BPF directory. It builds the module by invoking `make` in `test_kmods`, then attempts to load it with `modprobe -q bpf_testmod`. If loading fails, it prints a skip-style message and exits with code `4`. The normal path runs `./test_progs` with `-t module_attach,ksyms_module,kfunc_call,kfunc_call/module,attach_probe` and finally unloads `bpf_testmod`.

State side effects include building kernel module artifacts in the module test directory, loading `bpf_testmod` into the running kernel, creating module sysfs and BTF entries, and running test programs that attach BPF programs to module functions, kfuncs, ksyms, and probes. There is no durable repository state except build outputs.

Dependencies include kernel headers/build tree compatibility, root privileges, `make`, `modprobe`, `rmmod`, the test module source, `test_progs`, and kernel support for BPF module attach/kfunc/module BTF features. Risks include cleanup gaps if `test_progs` fails before `rmmod`, interference from an already loaded module, and environment-specific skips when module loading is disabled. Test signals are the module build/load exit status and the selected `test_progs` subtest results.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/Makefile

## Research

This Makefile builds the kernel modules used by BPF selftests. It is a thin wrapper around the kernel build system and selects module objects for `bpf_testmod`, rqspinlock, module-order tests, and no-CFI struct_ops validation.

The important variables are `TESTMODS_DIR`, `KDIR`, and `VMLINUX_BTF`. `obj-m` lists the module targets. `bpf_testmod-objs` composes `bpf_testmod.o` with generated trace event support, while other module targets are single-object modules. The default `all` target invokes `$(MAKE) -C $(KDIR) M=$(TESTMODS_DIR) modules`, optionally passing `KBUILD_EXTRA_SYMBOLS` to resolve exported symbols from the main selftests build. `clean` delegates to the kernel build system clean target.

Control flow and state are make-driven. It creates kernel module build artifacts such as `.ko`, `.o`, `.mod`, generated module metadata, and potentially BTF-enabled module output when `VMLINUX_BTF` is available. Dependencies include a configured kernel build tree, module build support, compiler/toolchain compatibility, and any symbols exported by the broader selftest build.

Risks are mostly build-environment coupling: wrong `KDIR`, stale generated files, missing vmlinux BTF, unavailable architecture features, or unresolved symbols. Test signals are successful `make modules` output and loadable `.ko` files consumed by `test_kmod.sh`, ftrace tests, split-BTF tests, and rqspinlock tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_x.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_x.c

## Research

This tiny kernel module exposes one BPF kfunc for module-order selftests. `bpf_test_modorder_retx()` is annotated `__bpf_kfunc` and returns the character value `'x'`. The module wraps the function in `__bpf_kfunc_start_defs()` / `__bpf_kfunc_end_defs()`, declares a `BTF_KFUNCS_START` ID set containing the function, and registers that set for `BPF_PROG_TYPE_SCHED_CLS` during module initialization.

Control flow is minimal: `bpf_test_modorder_x_init()` calls `register_btf_kfunc_id_set()` with owner `THIS_MODULE`; `bpf_test_modorder_x_exit()` is empty. Runtime state is the module's registered kfunc ID set and its module ownership lifetime. Dependencies include kernel BTF ID support, kfunc registration APIs, and module BTF generation.

The integration point is any BPF selftest that loads multiple modules and checks kfunc discovery or ordering across module BTF sources. The return value distinguishes this module from `bpf_test_modorder_y`. Risks are name or registration changes that break expected discovery, failure to generate module BTF, and cleanup relying on module unload rather than explicit unregister logic. Test signals are successful module load and successful BPF verifier resolution/call of `bpf_test_modorder_retx()`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_y.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_y.c

## Research

This module is the `y` counterpart to the module-order kfunc test. It defines `bpf_test_modorder_rety()` as an `__bpf_kfunc` returning `'y'`, places it into a BTF kfunc ID set, and registers that set for `BPF_PROG_TYPE_SCHED_CLS` from module initialization.

The API surface is intentionally tiny: one kfunc, one `btf_kfunc_id_set`, and module init/exit functions. Control flow is registration-only; exit does no explicit cleanup. State is limited to the loaded module and registered kfunc set owned by `THIS_MODULE`. It depends on the same kernel BTF/kfunc/module infrastructure as the `x` module.

Its integration role is to provide a second module with a similarly named but distinct kfunc so selftests can validate module BTF ordering, lookup, and call target disambiguation. Risks are the same as `bpf_test_modorder_x.c`: module BTF absence, registration failure, name drift, or changed verifier handling for module kfuncs. Test signals are successful load and a BPF program being able to resolve/call `bpf_test_modorder_rety()` and distinguish its return value from the `x` module.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_modorder_y.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_no_cfi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_no_cfi.c

## Research

This kernel module verifies that BPF struct_ops registration rejects missing CFI stubs and succeeds when stubs are provided. It defines `struct bpf_test_no_cfi_ops` with two function pointers and dummy verifier/init/register callbacks.

The init path is the test. `bpf_test_no_cfi_init()` first calls `register_bpf_struct_ops()` with `test_no_cif_ops` while `cfi_stubs` is unset. Success would mean the negative case failed, so the module returns `-EINVAL` if registration unexpectedly succeeds. It then sets `test_no_cif_ops.cfi_stubs` to `__test_no_cif_ops`, a struct populated with stub functions, and retries registration; the second return value becomes the module init result. Exit is empty.

State is kernel struct_ops registration state owned by the module. Dependencies include BPF struct_ops infrastructure, CFI stub enforcement, module support, and BTF for `bpf_test_no_cfi_ops`. Integration is through module-load tests that expect this module to load only because the second registration succeeds after the first rejection.

Risks include semantic changes in struct_ops CFI requirements, lack of cleanup if a future registration path partially succeeds, and the confusing `cif` spelling in local variable names. Test signals are module load success plus implicit evidence that missing stubs were rejected; unexpected first-registration success fails the module load with `-EINVAL`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_no_cfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_rqspinlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_rqspinlock.c

## Research

This kernel module stress-tests `rqspinlock_t` behavior under normal thread context and NMI/perf-event context. It creates worker kthreads, pinned hardware perf events, and per-CPU histograms to exercise nested lock acquisition patterns.

Important state includes three rqspinlocks, module parameters `test_mode`, `normal_delay`, and `nmi_delay`, per-CPU `rqsl_cpu_hist`, arrays of perf events and kthreads, readiness counters, and a pause flag. Modes choose lock ordering: `AA`, `ABBA`, or `ABBCCA`. `rqsl_get_lock_pair()` maps each CPU and mode to worker/NMI lock choices. `rqspinlock_worker_fn()` repeatedly acquires worker-side locks, delays, and records success/failure latency. Perf event overflow/NMI handling acquires the paired lock and records NMI-context results.

Init allocates per-CPU perf events, starts worker threads, waits for readiness, enables events, and reports configuration. Exit pauses workers, disables/frees perf events, stops threads, prints latency histograms, and releases allocated arrays. State is entirely kernel runtime state; no files are persisted.

Dependencies are architecture support for `asm/rqspinlock.h`, perf hardware cycle events, kthreads, SMP, atomics, and module parameters. Risks include hardware perf unavailability, long delays causing slow tests, CPU hotplug assumptions, and contention patterns that can expose hangs or soft lockups if rqspinlock is broken. Test signals are successful module load/unload, no deadlock, populated success/failure counters, and printed histograms with slow-bucket visibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_rqspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod-events.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod-events.h

## Research

This trace event header defines the tracepoints exported by `bpf_testmod`. It uses the Linux tracepoint framework pattern with `TRACE_SYSTEM bpf_testmod`, guarded declarations, and a final `trace/define_trace.h` include.

The main event is `TRACE_EVENT(bpf_testmod_test_read)`, which records current task PID, command, read offset, and length from `struct bpf_testmod_test_read_ctx`. It also declares bare tracepoints for write, nullable-argument testing, raw tracepoint null-argument testing, writable tracepoint testing, and fentry helper tracepoints `bpf_testmod_fentry_test1` and `bpf_testmod_fentry_test2`. `BPF_TESTMOD_DECLARE_TRACE` adapts to kernels with `DECLARE_TRACE_WRITABLE`, otherwise falling back to normal `DECLARE_TRACE`.

There is no independent control flow; including `CREATE_TRACE_POINTS` before this header in `bpf_testmod.c` instantiates the tracepoints. Runtime state is kernel tracepoint registration and event metadata. Dependencies include `linux/tracepoint.h`, `bpf_testmod.h`, and generated trace definitions.

Integration points are BPF raw tracepoint, tracepoint, fentry/fexit, nullable annotation, and writable tracepoint selftests. Risks are tracepoint prototype drift, writable tracepoint availability differences, and BTF/nullability annotation changes. Test signals include successful module build/load, tracepoint attach success, correct context field values, and writable tracepoint mutation behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.c

## Research

`bpf_testmod.c` is the main kernel-side fixture module for BPF selftests. It exports tracepoints, sysfs triggers, BTF kfuncs, struct_ops families, module ksyms, fentry/fexit targets, networking kfuncs, iterator kfuncs, reference-counted objects, and uprobe helpers.

Important APIs include many `__bpf_kfunc` functions registered through BTF ID sets for common, tracing, SCHED_CLS, syscall, and struct_ops program types. It defines iterator kfuncs for `bpf_iter_testmod_seq`, dynptr/trusted/RCU/refcount tests, signed and unsigned kfunc argument tests, memory-size annotated arguments, destructive/sleepable kfuncs, socket lifecycle and kernel socket-operation kfuncs, implicit-argument kfuncs, and context-check triggers. It also declares `bpf_struct_ops` providers for `bpf_testmod_ops`, `ops2`, `ops3`, `bpf_testmod_st_ops`, and `bpf_testmod_multi_st_ops`, including prologue/epilogue instruction generation for struct_ops tests.

Control flow centers on module init and sysfs-triggered callbacks. `bpf_testmod_init()` registers kfunc sets, fmodret IDs, struct_ops providers, destructor kfuncs, creates `/sys/kernel/bpf_testmod`, optionally creates `/sys/kernel/bpf_testmod_uprobe`, initializes socket state, and populates trampoline function pointers. `bpf_testmod_test_read()` deliberately exercises many attach targets, struct/union argument ABI cases, raw/nullable/writable tracepoints, fentry functions, trampoline count, and stacktrace hooks, then returns `-EIO`. Write triggers the bare write tracepoint. Exit waits for outstanding references, synchronizes irq work/tasklets, closes sockets, and removes sysfs files.

State includes per-CPU ksym storage, global result fields, module-owned sockets protected by `sock_lock`, registered struct_ops pointers protected by mutexes or spinlocks, a refcounted test object, optional uprobe registration state, sysfs bin attributes, tracepoints, and BPF registration tables. Dependencies are broad: module BTF, tracepoints, sysfs, kfunc registration, struct_ops, ftrace/fentry, socket APIs, RCU tasks trace, cgroup kfunc IDs, and architecture-specific uprobe register mutation on x86_64.

Risks are high because this fixture intentionally touches many kernel subsystems. Changes in BTF annotations, kfunc flags, verifier access checks, struct_ops CFI, module unload lifetime, socket API behavior, tracepoint prototypes, or generated prologue/epilogue instruction contracts can break consumers. Test signals are selected `test_progs` subtests successfully loading/attaching/calling module kfuncs, sysfs read/write triggers firing tracepoints, struct_ops registration behavior, split module BTF availability, and clean module unload without leaked refs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.h

## Research

This header defines shared ABI structures for the `bpf_testmod` kernel module and BPF/user-space tests that interact with it. It is intentionally type-heavy and logic-free.

The context structures `bpf_testmod_test_read_ctx`, `bpf_testmod_test_write_ctx`, and `bpf_testmod_test_writable_ctx` describe tracepoint payloads and writable tracepoint mutation state. `bpf_iter_testmod_seq` defines the simple iterator state used by module iterator kfuncs. `bpf_testmod_ops`, `ops2`, `ops3`, `bpf_testmod_st_ops`, and `bpf_testmod_multi_st_ops` define struct_ops layouts used by BPF programs to install callbacks into the module. The primary `bpf_testmod_ops` structure intentionally includes nullable/refcounted arguments, shadow-copy fields, unsupported fields, data fields, and forty trampoline function pointers to test multi-page trampoline allocation.

State and persistence are external to the header. Once compiled into module/BPF objects, these layouts become BTF ABI contracts. Dependencies include Linux integer types and forward declarations for `task_struct`, `cgroup`, `module`, and `hlist_node`.

Risks are layout drift and annotation mismatches. Because BPF verifier and struct_ops tests depend on exact field names, offsets, function prototypes, and BTF-emitted types, changing this header can affect many tests. Test signals include successful BTF matching between BPF programs and module types, struct_ops map creation/attach, correct nullable/refcounted argument verification, and trampoline stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod_kfunc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod_kfunc.h

## Research

This header is the shared type contract for `bpf_testmod` kfunc selftests. It is included both by kernel module code and by BPF program code, with conditional includes and definitions for `__KERNEL__` versus BPF-side compilation.

It defines nested structures used to validate verifier handling of argument shapes, nested members, trusted pointers, reference-counted kfunc returns, pass/fail parameter layouts, address arguments, socket initialization arguments, and sendmsg arguments. Kernel-only definitions include `prog_test_member1`, `prog_test_member`, and `prog_test_ref_kfunc` with a `refcount_t`; BPF-side builds use `vmlinux.h`, `bpf_helpers.h`, and `__ksym` declarations. The header also provides prototypes or external symbol declarations consumed by BPF programs for module kfunc calls.

There is no control flow or persistent state in the header, but its types control verifier semantics for size-suffixed memory parameters, acquire/release pairs, nullable returns, trusted/RCU pointers, socket address bounds, and implicit arguments. Dependencies include vmlinux BTF on the BPF side and kernel definitions such as `refcount_t` on the module side.

Risks are ABI and annotation drift. If field order, names, or suffix conventions such as `__sz`, `__nullable`, or reference annotations change, verifier expectations and kfunc registration tests can fail. Test signals are successful BPF object compilation, kfunc resolution against module BTF, expected verifier accept/reject outcomes for pass/fail structures, and correct runtime behavior for reference and socket kfunc tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod_kfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2.sh

## Research

This shell selftest exercises BPF integration with LIRC mode2 devices through the kernel `rc-loopback` driver. It is an environment-dependent harness that skips when required privileges or loopback devices are absent.

The script requires root, loads `rc-loopback`, scans `/sys/class/rc/rc*/uevent` for `DRV_NAME=rc-loopback`, derives both the `/dev/lircN` and `/dev/input/eventM` paths from uevents, then runs `./test_lirc_mode2_user $LIRCDEV $INPUTDEV`. It prints colored PASS/FAIL output and exits with the helper status or kselftest skip code `4` if no loopback LIRC device is found.

State side effects are the loaded `rc-loopback` module, discovered LIRC/input device use, and kernel BPF subsystem state as driven by the C helper. The shell script itself does not persist files. Dependencies include root privileges, `modprobe`, `rc-loopback`, sysfs RC class entries, the compiled `test_lirc_mode2_user` binary, and kernel support for attaching BPF programs to LIRC mode2 hooks.

Risks are primarily environmental: missing root privileges, unavailable `rc-loopback`, missing device nodes, or incompatible kernel configuration will skip or fail. Test signals are skip messages, PASS/FAIL lines for `lirc_mode2`, and the helper's success/failure status for actual BPF LIRC behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2_user.c

## Research

This user-space helper loads and attaches a LIRC mode2 BPF program to an rc-loopback LIRC device, then validates decoded events through the associated input event device. It is the executable backend for `test_lirc_mode2.sh`.

The program expects `/dev/lircN` and `/dev/input/eventM`. It loads `test_lirc_mode2_kern.bpf.o` as `BPF_PROG_TYPE_LIRC_MODE2`, opens the LIRC FD read/write nonblocking and the input FD read-only nonblocking, checks that detach before attach returns `-ENOENT`, queries attached programs, attaches with `bpf_prog_attach(..., BPF_LIRC_MODE2, 0)`, writes raw IR values `0x1dead` and `0x20101`, and polls/reads input events until it observes `EV_MSC/MSC_SCAN/0xdead` and `EV_REL/REL_Y/1`. It then verifies exactly one attached program is reported and detaches it.

Runtime state includes the LIRC FD, input event FD, loaded BPF object/program FD, program attachment state, and transient IR/input event buffers. Cleanup relies on process exit and explicit detach at the end; no repository state is persisted. Dependencies include the kernel LIRC and input subsystems, rc-loopback device nodes, permissions to access both devices, and the compiled BPF object expected by the helper.

Risks are kernel/device timing sensitivity and infinite polling loops if expected events never arrive. Device drivers can differ in accepted sample formats, reads may fail with nonblocking behavior, and missing LIRC attach support will fail even though the test source is correct. Test signals are successful load/query/attach/detach, successful raw IR writes, expected input events, and nonzero exit on any syscall/libbpf mismatch.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lirc_mode2_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_loader.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_loader.c

## Research

`test_loader.c` is the generic annotation-driven BPF object test runner used by many selftests. It opens generated skeleton ELF bytes, reads BTF declaration tags on each BPF program, derives expected load/runtime behavior, and runs privileged and optional unprivileged subtests.

Important types are `struct test_spec` and `struct test_subspec`, which hold program names, expected verifier messages, translated/JIT disassembly patterns, stdout/stderr stream patterns, return values, capability requirements, custom BTF path, log level, program flags, architecture/load-mode masks, and execution controls. `compile_regex()`, `__push_msg()`, `collect_decl_tags()`, and `parse_test_spec()` turn `bpf_misc.h` decl-tag comments into structured expectations. `validate_msgs()` checks ordered positive patterns, negative patterns scoped between positives, and next-line expectations.

Control flow begins in `test_loader__run_subtests()`, which calls `process_subtest()`. The loader opens the object from memory, parses specs for each program, skips auxiliary programs as top-level cases, and calls `run_subtest()` for privileged and unprivileged variants. `run_subtest()` reopens the object, autoloads only the target plus needed auxiliary programs, configures logs/flags/maps, optionally drops capabilities, loads the object, validates verifier logs, restores capabilities for info reads, optionally validates xlated/JIT text, attaches struct_ops maps for executable tests, runs `bpf_prog_test_run_opts()`, and validates BPF stdout/stderr streams.

State is process-local log buffers, compiled regex arrays, temporary libbpf objects, BPF FDs, links, capability masks, and cached unprivileged sysctl state. Dependencies include libbpf, BTF, selftest assertion helpers, capability helpers, unprivileged sysctl helpers, disassembly helpers, and JIT availability for JIT text checks.

Risks include strict coupling to decl-tag syntax, regex length limits, arch-specific disassembly differences, capability restoration bugs, and environment-dependent unprivileged/JIT support. Test signals are named subtests with clear failures for unexpected load result, missing verifier/disassembly/stdout/stderr patterns, wrong retval, unsupported JIT disassembly, or failed struct_ops attachment.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lru_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lru_map.c

## Research

This standalone C selftest validates kernel LRU hash and LRU per-CPU hash map eviction semantics. It compares LRU maps against expected ordinary hash maps after controlled lookup, update, delete, CPU-affinity, and datapath-reference-bit sequences.

Key helpers include `create_map()`, `bpf_map_lookup_elem_with_ref_bit()`, `map_subset()`, `map_equal()`, `sched_next_online()`, `__tgt_size()`, and `__map_size()`. The special lookup helper loads a tiny SCHED_CLS BPF program that performs `bpf_map_lookup_elem()` from datapath context, which marks the LRU reference bit differently from syscall lookup. The numbered `test_lru_sanity0()` through `test_lru_sanity8()` scenarios cover two-entry eviction, referenced versus unreferenced recycling, active/inactive list rotation, deletion, one-element maps across CPUs, per-CPU `BPF_F_NO_COMMON_LRU` behavior, and syscall versus datapath reference-bit differences.

`main()` sets libbpf strict mode, discovers possible CPUs, then runs all sanity tests for `BPF_MAP_TYPE_LRU_HASH` and `BPF_MAP_TYPE_LRU_PERCPU_HASH` with both common LRU and `BPF_F_NO_COMMON_LRU`. State is transient kernel map/program FDs, CPU affinity changes for child/current processes, and expected-map contents. Cleanup closes FDs after each case.

Dependencies include libbpf, BPF syscall support, SCHED_CLS program load/test-run support, CPU affinity, and possible CPU discovery. Risks are timing/CPU topology sensitivity, changing LRU internals, and reliance on negative libbpf return conventions in assertions. Test signals are printed `Pass` per scenario, assertion failures on unexpected errno or map contents, and final process exit status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lru_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.c

## Research

`test_maps.c` is a broad standalone ABI regression suite for BPF map operations. It uses assert-style checks and selected libbpf helpers to exercise hash, per-CPU hash, array, per-CPU array, devmap, queue, stack, sockmap, map-in-map, large maps, parallel update/delete, read-only/write-only maps, reuseport sockarray, and additional map tests included from `map_tests/tests.h`.

Important APIs are `bpf_map_create()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_lookup_and_delete_elem()`, `bpf_map_delete_elem()`, `bpf_map_get_next_key()`, map ID/info iteration, `bpf_prog_test_load()`, `bpf_prog_attach()`/`detach2()`, libbpf object/map lookup, and socket syscalls. `map_update_retriable()` and `map_delete_retriable()` add retry/backoff for concurrent or no-prealloc races. `__run_parallel()` forks many children to stress shared map FDs.

Control flow is `main()` setting strict libbpf mode, running `run_all_tests()` once with default map flags and again with `BPF_F_NO_PREALLOC`, then invoking generated extra map tests. `run_all_tests()` sequences basic semantics, stress, sockmap, map-in-map, permission flags, reuseport, queue, and stack cases. The sockmap test creates TCP sockets, loads SK_SKB/SK_MSG programs, attaches parser/verdict programs, validates invalid attach/detach paths, sends data, and forks concurrent map mutators.

State includes many transient kernel map/program/object FDs, sockets, forked child processes, global `map_opts`, and skip count `skips`. Dependencies include root/BPF privileges, networking on loopback, object files such as `sockmap_parse_prog.bpf.o`, and support for each map type. Risks are environmental flakiness from port conflicts, resource pressure, high fork counts, unsupported map types, and assert aborts that skip cleanup. Test signals are assertion success, explicit skip count, printed failure context, and final `test_maps: OK`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.h

## Research

This small header shares retry helper declarations for map tests. It defines `retry_for_error_fn`, a predicate callback type used to decide whether a failed map operation should be retried, and declares `map_update_retriable()`.

The implementation in `test_maps.c` retries `bpf_map_update_elem()` with exponential backoff while the callback says the current `errno` is transient. This supports concurrent and `BPF_F_NO_PREALLOC` stress tests, where `EAGAIN`, `EBUSY`, `ENOMEM`, or `E2BIG` can be recoverable under contention or allocation pressure.

The header has no state, persistence, or control flow. It integrates with additional generated map tests under `map_tests/` that need the same retry behavior without duplicating the implementation. Dependencies are standard C types and the including test source providing the implementation.

Risks are signature drift between declaration and implementation or misuse with callbacks that retry permanent failures indefinitely if attempts are too high. Test signals are successful compilation of included map tests and stable parallel map update behavior under contention.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.h -->
