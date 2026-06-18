# subset-b-006751 research

Grouped research for 40 perf test and trace/beauty files. Each file section preserves the source path in its title and is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/topology.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/topology.c

## Purpose
This perf unit test validates that CPU topology written into a temporary `perf.data` header can be read back and agrees with perf's runtime CPU aggregation helpers. It specifically exercises `HEADER_CPU_TOPOLOGY`, `HEADER_NRCPUS`, and `HEADER_ARCH` serialization through `perf_session__write_header()` and later verifies socket, die, core, CPU, node, and thread-index fields produced by `aggr_cpu_id__*()`.

## Important APIs, Types, And Functions
Key local helpers are `get_temp()`, `session_write_header()`, `check_cpu_topology()`, and `test__session_topology()`. The file depends on `struct perf_session`, `struct perf_data`, `struct perf_cpu_map`, `struct perf_env`, `struct aggr_cpu_id`, and `struct target`. Integration APIs include `perf_session__new()`, `evlist__new_default()`, `perf_header__set_feat()`, `perf_session__write_header()`, `perf_session__env()`, `perf_cpu_map__new_online_cpus()`, `perf_cpu_map__for_each_cpu()`, `aggr_cpu_id__cpu/core/die/socket/node()`, and `cpu__get_node()`.

## Control Flow
`test__session_topology()` creates a `/tmp/perf-test-XXXXXX` file with `mkstemp()`, writes a minimal perf session header with topology features enabled, obtains the online CPU map, then calls `check_cpu_topology()`. `check_cpu_topology()` opens the file read-only as a perf session, initializes CPU-node lookup state, applies architecture-specific skips, iterates all online CPUs for debug output, then performs five assertion passes over CPU, core, die, socket, and node aggregation IDs. Cleanup releases the CPU map, deletes the perf session, and unlinks the temp file.

## State, Dependencies, And Integration
Persistent state is limited to the temporary perf data file; runtime state comes from sysfs/proc topology and the host architecture. The test integrates with perf's suite registry via `DEFINE_SUITE("Session topology", session_topology)`. It is sensitive to platform topology export quirks: s390/aarch64 may expose large IDs, and ppc64le can omit `physical_package_id`.

## Risks And Test Signals
Risks include false skips or failures on large, sparse, or partially exposed CPU topologies, and reliance on `/tmp` and host CPU map consistency while the test runs. Success is `TEST_OK` from matching aggregation IDs; expected non-failure outcomes include `TEST_SKIP` for unsupported or incomplete topology cases and `TEST_FAIL` on header/session/cpumap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/unit_number__scnprintf.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/unit_number__scnprintf.c

## Purpose
This is a focused unit test for `unit_number__scnprintf()`, verifying that byte counts are formatted into perf's compact binary units with expected suffixes.

## Important APIs, Types, And Functions
The only test function is `test__unit_number__scnprint()`, registered with `DEFINE_SUITE("unit_number__scnprintf", unit_number__scnprint)`. It uses `u64`, `PRIu64`, `unit_number__scnprintf()`, `strcmp()`, `pr_debug()`, and perf's `TEST_OK`/`TEST_FAIL` convention.

## Control Flow
The function walks a sentinel-terminated table of input values and expected strings: `1 -> 1B`, `10*1024 -> 10K`, `20*1024*1024 -> 20M`, `30*1024*1024*1024ULL -> 30G`, and `0 -> 0B`. For each case it formats into a fixed 100-byte buffer, emits debug output, and fails immediately on any string mismatch.

## State, Dependencies, And Integration
There is no persistent state. The test depends on `units.h` for the formatter and `tests.h` for suite registration. It runs as a normal perf C test and does not depend on host hardware.

## Risks And Test Signals
Coverage is intentionally narrow: it checks exact binary-unit thresholds for only whole-unit values and does not test truncation, fractional output, larger suffixes, or small buffers. A passing test strongly signals stable canonical formatting for common byte-unit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/unit_number__scnprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/util.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/util.c

## Purpose
This perf utility test validates two unrelated utility surfaces: character replacement via `strreplace_chars()` and the in-tree BLAKE2s implementation used for build-id-sized hashing.

## Important APIs, Types, And Functions
Local helpers are `test_strreplace()` and `test_blake2s()`, with `test__util()` as the suite entry point. It uses `strreplace_chars()`, `free()`, `strcmp()`, `blake2s_init()`, `blake2s_update()`, `blake2s_final()`, `memcmp()`, and `TEST_ASSERT_VAL()`. Constants are `MAX_DATA_LEN` at 512 and `HASH_LEN` at 20 bytes, matching ELF build ID length.

## Control Flow
`test__util()` asserts replacement behavior for empty strings, no-match input, single replacement, repeated replacement, and replacement strings longer than the needle. It then delegates to `test_blake2s()`. The BLAKE2s test fills deterministic data bytes, hashes every prefix length from 0 through 512, verifies one-shot and two-part update consistency, feeds each digest into a parent BLAKE2s context, then compares the final hash-of-hashes to a Python-generated constant.

## State, Dependencies, And Integration
All state is local stack memory. The file depends on `util/blake2s.h`, `util/debug.h`, `string2.h`, and perf's test macros. It is registered as `DEFINE_SUITE("util", util)`.

## Risks And Test Signals
The string-replacement assertions catch allocation or expansion errors in common cases but do not test allocation failure. The hash test is deterministic and relatively broad across input lengths; failures indicate a regression in streaming, finalization, digest sizing, or endian/byte handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/vmlinux-kallsyms.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/vmlinux-kallsyms.c

## Purpose
This test compares symbols loaded from a matching `vmlinux` image against symbols parsed from `/proc/kallsyms`, validating perf's kernel symbol loading, relocation, map splitting, symbol lookup, and tolerance for known architecture/linker artifacts.

## Important APIs, Types, And Functions
Important functions are `is_ignored_symbol()`, three verbose map comparison callbacks, and `test__vmlinux_matches_kallsyms()`. It uses `struct machine`, `struct maps`, `struct map`, `struct dso`, `struct symbol`, rb-tree symbol iteration, `machine__create_kernel_maps()`, `machine__load_kallsyms()`, `machine__load_vmlinux_path()`, `machine__find_kernel_symbol()`, `machine__find_kernel_symbol_by_name()`, `map__unmap_ip()`, `map__for_each_symbol()`, `maps__for_each_map()`, and `arch__compare_symbol_names()`.

## Control Flow
The test initializes separate `machine` instances for kallsyms and vmlinux. It creates kernel maps for kallsyms, loads `/proc/kallsyms` without kcore, captures the kallsyms kernel map, creates vmlinux maps, auto-locates a matching vmlinux, and then iterates every non-empty vmlinux symbol. For each symbol, it maps vmlinux IPs to runtime addresses, finds a kallsyms symbol at that address, accepts exact or architecture-normalized name matches, tolerates end-address skew below one page, ignores aliases to `_etext`, and filters known synthetic/local/debug/absolute symbols. Any remaining missing symbol marks failure. Verbose mode prints map-only and renamed-map diagnostics.

## State, Dependencies, And Integration
The test reads live host kernel state from `/proc/kallsyms`, `/proc/modules`, module files, and vmlinux search paths. It registers as `DEFINE_SUITE("vmlinux symtab matches kallsyms", vmlinux_matches_kallsyms)`. It owns `machine` lifetimes and releases both via `machine__exit()`.

## Risks And Test Signals
It is host-sensitive: missing permissions, unavailable matching vmlinux, module churn, restricted kallsyms, or unusual linker symbols can skip or fail the test. `TEST_SKIP` is expected when kernel maps, kallsyms, or vmlinux cannot be loaded. True failures signal symbol relocation, filtering, or lookup regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/vmlinux-kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/brstack.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/brstack.c

## Purpose
This workload generates predictable branch-stack activity for perf tests: direct calls, returns, a conditional branch, an unconditional loop branch, and an indirect call.

## Important APIs, Types, And Functions
Local functions are `brstack_bar()`, `brstack_foo()`, `brstack_bench()`, and workload entry `brstack()`. It uses `atoi()` for optional loop count parsing and `DEFINE_WORKLOAD(brstack)` for registration. The static volatile `cnt` prevents the compiler from fully collapsing the branch behavior.

## Control Flow
`brstack()` defaults to `BENCH_RUNS` loops, optionally overrides it from `argv[0]`, then loops until `cnt` exceeds the threshold. Each iteration calls `brstack_bench()`, which increments `cnt`, conditionally calls `brstack_foo()`, calls `brstack_bar()` directly, and calls `brstack_foo()` through a function pointer.

## State, Dependencies, And Integration
State is a process-local volatile counter. The workload is integrated through perf's workload registry and is intended to be run under perf record/script/report branch sampling tests.

## Risks And Test Signals
Compiler optimization and inlining are the main risks because the test relies on recognizable call/branch shape; the simple function boundaries and volatile counter mitigate this. The signal is not an assertion here but downstream perf output containing the expected branch types and symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/brstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.c

## Purpose
This C workload wraps a Rust function to provide a bounded runtime and signal handling for perf data type profiling tests that need mixed C/Rust code and discoverable Rust data types.

## Important APIs, Types, And Functions
The exported dependency is `extern void test_rs(uint count)`, implemented in `code_with_type.rs`. The workload entry is `code_with_type()`, registered with `DEFINE_WORKLOAD(code_with_type)`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and a `volatile sig_atomic_t done` flag.

## Control Flow
The workload sets the thread name, parses optional seconds and loop count arguments, installs SIGINT and SIGALRM handlers, arms an alarm, and repeatedly calls `test_rs(num_loops)` until `done` is set. Signal handling remains in C because the Rust standard library path here intentionally avoids external signal-management crates.

## State, Dependencies, And Integration
State is only the `done` flag. Integration requires the Rust object defining `test_rs()` to be linked with the perf workload binary. The named thread and bounded alarm help perf tests identify and constrain samples.

## Risks And Test Signals
Risks include link failures if Rust support or the companion object is unavailable, and optimized Rust code that changes profile shape. Downstream tests should observe Rust function/type information while the process exits cleanly after the requested duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.rs -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.rs

## Purpose
This Rust companion workload creates a concrete `Buf` structure and mutates it in a loop so perf data type profiling can find Rust type and field information.

## Important APIs, Types, And Functions
The core type is private `struct Buf { data1: u64, data2: String, data3: u64 }`. The public ABI is `#[no_mangle] pub extern "C" fn test_rs(count: u32)`, which is called from `code_with_type.c`.

## Control Flow
`test_rs()` allocates a mutable `Buf` with `data2` set to `"data"`, then iterates from `1` to `count - 1`. Each iteration increments `data1`, adds an extra increment when `data1 == 123`, and accumulates `data1` into `data3`.

## State, Dependencies, And Integration
State is stack/local Rust data only; it is not persisted or shared. Integration depends on C-compatible symbol naming and the perf build path linking Rust into the workload. `data2` ensures the type includes a nontrivial standard-library field.

## Risks And Test Signals
The function has no observable return value, so aggressive optimization is a risk if debug/type information or side effects are insufficient for the target test. The expected test signal is the presence of `Buf` and its fields in perf's data type profiling output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/code_with_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/datasym.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/datasym.c

## Purpose
This workload repeatedly accesses a static data symbol with a controlled layout so perf tests can attribute samples to data symbols and offsets.

## Important APIs, Types, And Functions
The file defines aligned `struct buf` with `data1`, 55 reserved bytes, and `data2`, plus a volatile static instance `workload_datasym_buf1`. Workload entry `datasym()` uses `signal()`, `alarm()`, and `atoi()`, and is registered with `DEFINE_WORKLOAD(datasym)`.

## Control Flow
The workload parses an optional duration, installs SIGINT/SIGALRM handlers, arms an alarm, and loops until `done`. Each iteration increments `data1`, conditionally performs an extra increment at value 123, then accumulates `data1` into `data2`.

## State, Dependencies, And Integration
Persistent state is only the process-lifetime static volatile buffer in the data section. The 64-byte alignment and initialized reserved byte are deliberate to create a visible data symbol and cache-line-shaped layout. It integrates with perf data-symbol and memory-access sampling tests.

## Risks And Test Signals
The conditional branch is an Arm N1 SPE erratum workaround to avoid a pathological repeated instruction stream. Risks include compiler layout changes if attributes are altered and sampling bias on affected hardware. Downstream success is observing accesses to `workload_datasym_buf1` and its fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/datasym.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/inlineloop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/inlineloop.c

## Purpose
This workload creates an always-inlined call chain inside a bounded CPU loop so perf can test inline call attribution and symbol reporting.

## Important APIs, Types, And Functions
It defines `leaf()` and `middle()` as `static inline __attribute__((always_inline))`, `parent()` as `noinline`, and workload entry `inlineloop()`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and `DEFINE_WORKLOAD(inlineloop)`.

## Control Flow
`inlineloop()` sets a recognizable thread name, parses duration, installs signal handlers, arms an alarm, and calls `parent(sec)`. `parent()` calls `middle()`, which inlines `leaf()`. `leaf()` loops with a `goto` label, incrementing volatile `a` until the signal handler sets `done`.

## State, Dependencies, And Integration
State consists of volatile integer `a` and `volatile sig_atomic_t done`. The function attributes create an expected profile shape: a non-inlined parent with inline children. Integration is through perf workload registration and downstream script/report tests.

## Risks And Test Signals
Compiler behavior is central: changing attributes or optimization flags can destroy the intended inline stack. A good signal is perf output showing samples in `parent` with inline frames for `middle`/`leaf` according to debug info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/inlineloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/landlock.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/landlock.c

## Purpose
This workload issues `landlock_add_rule` syscalls with two rule types so `perf trace` can test enum and struct argument augmentation, especially with BTF.

## Important APIs, Types, And Functions
The workload locally defines missing Landlock syscall numbers, access bits, rule constants, and `landlock_path_beneath_attr` / `landlock_net_port_attr` when older system headers lack them. The only entry point is `landlock()`, registered with `DEFINE_WORKLOAD(landlock)`.

## Control Flow
`landlock()` initializes dummy file descriptor and flags values, builds a path-beneath rule with a fake parent fd, builds a network-port rule with a fake port, and calls `syscall(__NR_landlock_add_rule, ...)` twice. It ignores syscall return values because only argument capture matters.

## State, Dependencies, And Integration
There is no persistent state. The workload depends on raw syscall availability but does not require successful Landlock setup. It is integrated into perf tests that intercept syscall arguments and decode enum values.

## Risks And Test Signals
Hard-coded syscall number 445 is architecture-sensitive if used outside the intended supported environment. Since invalid fds/flags are intentional, syscall failure is not a workload failure. The signal is `perf trace` displaying decoded rule types and augmented struct fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/landlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/leafloop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/leafloop.c

## Purpose
This workload provides stable non-inlined `parent` and `leaf` symbols in a timed CPU loop for perf script/report symbol tests.

## Important APIs, Types, And Functions
It declares and defines `noinline void leaf(volatile int b)` and `noinline void parent(volatile int b)`, plus workload entry `leafloop()`. It uses `signal()`, `alarm()`, `atoi()`, and `DEFINE_WORKLOAD(leafloop)`.

## Control Flow
`leafloop()` parses duration, installs SIGINT/SIGALRM handlers, arms an alarm, and calls `parent(sec)`. `parent()` calls `leaf()`, and `leaf()` increments volatile static `a` until `done` is set.

## State, Dependencies, And Integration
State is `a` and `done`, both process-local. `noinline` is the important integration contract because downstream tests expect visible `parent` and `leaf` symbols rather than optimized-away frames.

## Risks And Test Signals
Changing function names, attributes, or compiler flags can break downstream symbol matching. Success is usually measured outside the workload by perf output containing the expected function symbols for sampled CPU time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/leafloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/noploop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/noploop.c

## Purpose
This is a minimal timed busy loop used as a generic perf sampling workload with a recognizable thread name and almost no application-side behavior.

## Important APIs, Types, And Functions
The workload entry is `noploop()`, registered with `DEFINE_WORKLOAD(noploop)`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and a `volatile sig_atomic_t done` flag.

## Control Flow
`noploop()` sets the thread name to `perf-noploop`, parses an optional duration, installs SIGINT/SIGALRM handlers, arms an alarm, and spins in an empty loop until the handler sets `done`.

## State, Dependencies, And Integration
There is no persisted state and no data structure dependency beyond the signal flag. Its integration value is to provide stable CPU activity for tests that need samples without branch, syscall, data, or thread complexity.

## Risks And Test Signals
The empty loop is intentionally simple; changes that add syscalls or sleeps would reduce sample density. The main risk is compiler optimization, mitigated by volatile signal state. Downstream success is a bounded process that consumes CPU and exits after the alarm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/noploop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/sqrtloop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/sqrtloop.c

## Purpose
This workload generates floating-point/libm activity in a child process so perf tests can exercise profiling across forked workloads and math-library symbols.

## Important APIs, Types, And Functions
Functions are `__sqrtloop(int sec)` and workload entry `sqrtloop()`. It uses `fork()`, `wait()`, `signal()`, `alarm()`, `sqrt()`, `rand()`, `atoi()`, and `DEFINE_WORKLOAD(sqrtloop)`.

## Control Flow
The parent parses an optional duration and forks. The child installs SIGALRM handling, arms the alarm, and repeatedly calls `sqrt(rand())` until done. The parent waits for the child and returns success unless `fork()` failed.

## State, Dependencies, And Integration
State is only the child process's signal flag. Dependencies include libc process control and libm. It integrates with perf tests that need child-process sampling or dynamic/library call activity.

## Risks And Test Signals
The workload depends on fork support and libm linkage. It ignores the child's exact exit status by using `wait(NULL)`, so downstream tests should validate perf data rather than workload return detail. Success is a bounded child process with samples around `sqrt`/random computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/sqrtloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/thloop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/thloop.c

## Purpose
This workload creates one or more threads that spin in a stable `test_loop` symbol, enabling perf tests for threaded sampling, reports, and symbol aggregation.

## Important APIs, Types, And Functions
The key exported shape is `noinline void test_loop(void)`. Other functions are `thfunc()` and workload entry `thloop()`, registered with `DEFINE_WORKLOAD(thloop)`. It uses `pthread_create()`, `pthread_join()`, `calloc()`, `free()`, `signal()`, `alarm()`, and `atoi()`.

## Control Flow
`thloop()` parses duration and thread count, rejects non-positive values, installs signal handlers, allocates a `pthread_t` array, starts worker threads for indexes 1 through `nt - 1`, arms the alarm, and runs `test_loop()` on the main thread. On creation failure it sets `done` so already-started threads exit, then joins all started threads and frees memory.

## State, Dependencies, And Integration
Shared process state is the `volatile sig_atomic_t done` flag. The loop function is passed indirectly to workers, preserving a clear call target. The workload depends on pthreads and integrates with perf tests that inspect per-thread samples.

## Risks And Test Signals
The thread list uses index 0 for the main thread and starts at index 1 by design. Risks include excessive requested thread counts and scheduler variance. Success signals include clean timeout exit and perf samples attributed to `test_loop` across multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/thloop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/traploop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/traploop.c

## Purpose
This workload creates repeated privileged-register trap/return activity on AArch64 for perf tests that need exception/trap samples; on other architectures it degrades to an empty loop.

## Important APIs, Types, And Functions
The architecture-dependent helper is `trap_bench()`. On `__aarch64__` it executes inline assembly `mrs ID_AA64ISAR0_EL1`, which traps from EL0. The workload entry is `traploop()`, registered with `DEFINE_WORKLOAD(traploop)`.

## Control Flow
`traploop()` parses an optional iteration count, defaults to `BENCH_RUNS`, and calls `trap_bench()` in a counted loop. The AArch64 helper reads a system register into a local variable; the non-AArch64 helper is empty.

## State, Dependencies, And Integration
There is no persistent state. The key dependency is CPU/OS behavior for user-mode access to `ID_AA64ISAR0_EL1`. It integrates as a perf workload for exception-heavy traces.

## Risks And Test Signals
On non-AArch64 the workload has little profiling value beyond loop overhead. On AArch64, kernel configuration and CPU behavior determine trap characteristics. Downstream success is visible trap/exception behavior in perf data rather than workload output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/workloads/traploop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/wp.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/wp.c

## Purpose
This perf test suite validates hardware watchpoint events for read-only, write-only, read/write, and attribute modification scenarios using `perf_event_open()`.

## Important APIs, Types, And Functions
Important helpers are `wp_read()`, `get__perf_event_attr()`, `__event()`, `test__wp_ro()`, `test__wp_wo()`, `test__wp_rw()`, and `test__wp_modify()`. It uses `struct perf_event_attr`, `PERF_TYPE_BREAKPOINT`, `HW_BREAKPOINT_R/W`, `PERF_SAMPLE_IP`, `sys_perf_event_open()`, `perf_event_open_cloexec_flag()`, `read()`, `ioctl(PERF_EVENT_IOC_MODIFY_ATTRIBUTES)`, and `PERF_EVENT_IOC_ENABLE`.

## Control Flow
Each subtest opens a breakpoint event on volatile globals `data1` or `data2`, performs reads and/or writes, reads the event counter, and asserts expected counts. `test__wp_modify()` opens a write watchpoint on `data1`, modifies it to watch two bytes of `data2` while disabled, verifies writes are not counted until enabling the event, then verifies only writes inside the watched range count.

## State, Dependencies, And Integration
State is process-local volatile watched memory and kernel perf event file descriptors. The suite is declared manually as `suite__wp` with four `TEST_CASE_REASON` entries. Architecture guards skip s390x broadly, x86/i386 for read-only watchpoints, and i386 uses a 32-bit watched word due to hardware length limits.

## Risks And Test Signals
Hardware support, kernel breakpoint constraints, and `PERF_EVENT_IOC_MODIFY_ATTRIBUTES` availability drive skips and failures. `-ENODEV` maps to missing hardware support. Passing counts signal correct watchpoint triggering, disabled-state handling, and modified address/length semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/wp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/asm/irq_vectors.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/asm/irq_vectors.h

## Purpose
This vendored x86 kernel header defines interrupt vector constants used by perf trace beauty generation/formatting for x86 IRQ vector names and ranges.

## Important APIs, Types, And Functions
The file is macro-only. Important constants include `NMI_VECTOR`, `FIRST_EXTERNAL_VECTOR`, `IA32_SYSCALL_VECTOR`, `ISA_IRQ_VECTOR(irq)`, APIC vectors from `SPURIOUS_APIC_VECTOR` down through posted interrupt and timer vectors, `NR_VECTORS`, `FIRST_SYSTEM_VECTOR`, `NR_EXTERNAL_VECTORS`, `NR_SYSTEM_VECTORS`, `NR_IRQS_LEGACY`, `CPU_VECTOR_LIMIT`, `IO_APIC_VECTOR_LIMIT`, and `NR_IRQS`.

## Control Flow
There is no runtime control flow. Preprocessor conditionals validate `SPURIOUS_APIC_VECTOR`, select `FIRST_SYSTEM_VECTOR` based on `CONFIG_X86_LOCAL_APIC`, and size `NR_IRQS` based on `CONFIG_X86_IO_APIC` and `CONFIG_PCI_MSI`.

## State, Dependencies, And Integration
The header depends on `linux/threads.h`, `NR_CPUS`, `MAX_IO_APICS`, and kernel config macros. In perf's copy, it provides stable source constants for generated or direct x86 vector beautifiers.

## Risks And Test Signals
The risk is drift from upstream kernel UAPI/internal x86 vector definitions, causing perf trace to print stale names. Build failures or mismatched generated tables are the main signals; runtime signals are incorrect x86 IRQ vector labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/asm/irq_vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/uapi/asm/prctl.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/uapi/asm/prctl.h

## Purpose
This x86 UAPI header defines `arch_prctl` operation codes and feature bits consumed by perf trace's `arch_prctl` argument beautifier.

## Important APIs, Types, And Functions
It declares macros for FS/GS base operations (`ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`), CPUID toggles, extended state permission queries/requests, AMX xcomp component IDs, VDSO mapping options, tagged-address operations, shadow-stack operations, and shadow-stack feature bits (`ARCH_SHSTK_SHSTK`, `ARCH_SHSTK_WRSS`).

## Control Flow
There is no runtime control flow. The header is protected by `_ASM_X86_PRCTL_H` and consists of numeric macro definitions grouped by command family.

## State, Dependencies, And Integration
No state is held. The integration point is `trace/beauty/arch_prctl.c`, which includes generated arrays built from these constants and formats syscall argument values into names.

## Risks And Test Signals
The main risk is ABI drift when new x86 `arch_prctl` commands are added upstream but this copy or generated tables are not refreshed. Tests should check that known codes print as symbolic `ARCH_*` names and unknown values fall back to hex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/uapi/asm/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.c

## Purpose
This C shim includes the generated architecture-specific errno name lookup array/function implementation for perf environment handling.

## Important APIs, Types, And Functions
The file contains only `#include "trace/beauty/generated/arch_errno_name_array.c"`. The generated file is produced by `arch_errno_names.sh` and provides per-architecture errno-to-name functions plus `arch_syscalls__strerrno_function()`.

## Control Flow
There is no local control flow; compilation injects generated switch tables at this include site.

## State, Dependencies, And Integration
It depends on the build system generating `trace/beauty/generated/arch_errno_name_array.c`. `tools/perf/util/env.c` includes this shim so perf can resolve errno names according to recorded architecture rather than only the host architecture.

## Risks And Test Signals
Risks are missing generated files, stale generated tables, or incorrect include paths. Build failure is the strongest signal. Runtime issues appear as unknown or wrong errno names when processing perf data from non-host architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.sh

## Purpose
This generator emits C code mapping errno numbers to names for each architecture with a specific UAPI `errno.h`, plus a dispatcher that chooses the lookup function by architecture string.

## Important APIs, Types, And Functions
Shell functions are `arch_string()`, `asm_errno_file()`, `create_errno_lookup_func()`, `process_arch()`, and `create_arch_errno_table_func()`. Inputs are a gcc command and `toolsdir`; output is C source using `strcmp()` and type `arch_syscalls__strerrno_t`.

## Control Flow
The script prints a C header block, discovers architectures under `$toolsdir/arch/*/include/uapi/asm/errno.h`, processes `generic` and each discovered architecture, and finally emits `arch_syscalls__strerrno_function()`. Each architecture preprocesses the relevant errno header with `$gcc -E -dM`, filters `#define E... <number>` lines, sorts by numeric value, and converts them into a switch returning the symbolic name or `"(unknown)"`.

## State, Dependencies, And Integration
It has no persistent state besides generated stdout redirected by the Makefile. It depends on gcc preprocessing, grep, awk, sort, sed, shell pipelines, and the tools UAPI header tree. Architecture names are normalized by replacing spaces/hyphens with underscores and lowercasing.

## Risks And Test Signals
Regex assumptions can miss aliases, expressions, or non-decimal definitions. Build-time generation should be tested by checking generated C compiles and maps representative errno values on generic and architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_errno_names.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_prctl.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_prctl.c

## Purpose
This beautifier formats x86 `arch_prctl` command codes as symbolic `ARCH_*` names for `perf trace`.

## Important APIs, Types, And Functions
The file includes generated `x86_arch_prctl_code_array.c` and defines three offset strarrays: `x86_arch_prctl_codes_1`, `_2`, and `_3`. It combines them with `DEFINE_STRARRAYS(x86_arch_prctl_codes)`. Public formatter `syscall_arg__scnprintf_x86_arch_prctl_code()` delegates to `x86_arch_prctl__scnprintf_code()`.

## Control Flow
At formatting time, the syscall argument value is read from `arg->val`; `strarrays__scnprintf()` searches the grouped strarrays and writes either a symbolic name, with optional prefix based on `arg->show_string_prefix`, or a `%#x` fallback.

## State, Dependencies, And Integration
Static generated arrays hold the decode tables. The formatter is declared in `beauty.h` as `SCA_X86_ARCH_PRCTL_CODE` and is used by `perf trace` syscall argument format metadata for x86 arch-prctl-like operations.

## Risks And Test Signals
Risks include generated table drift as new prctl codes appear and incorrect offset grouping for sparse ranges. Tests should verify known codes such as `ARCH_SET_FS` and shadow-stack commands render symbolically, while unknown codes render hex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch_prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/beauty.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/beauty.h

## Purpose
This is the central header for perf trace syscall argument beautifiers. It defines string-table containers, syscall argument context, augmented-argument metadata, and the function/macro names used by syscall format tables.

## Important APIs, Types, And Functions
Core types are `struct strarray`, `struct strarrays`, `struct augmented_arg`, `struct syscall_arg`, and lightweight `struct file`. Key macros are `DEFINE_STRARRAY`, `DEFINE_STRARRAY_OFFSET`, `DEFINE_STRARRAYS`, and many `SCA_*` / `STUL_*` aliases. Declared formatters cover file descriptors, integers, pointers, clone flags, fcntl, flock, mount/open/rename/socket/futex-related flags, x86 MSRs/IRQ vectors/arch_prctl, prctl args, timespecs, and more.

## Control Flow
No runtime control flow is implemented here, but the header defines the dispatch contract: each syscall argument formatter receives a buffer, size, and `struct syscall_arg`; it may inspect `arg->val`, other syscall arguments via `syscall_arg__val()`, augmented payloads, thread/trace context, and may set masks or return-value formatters.

## State, Dependencies, And Integration
The state model is explicit in `struct syscall_arg`: raw argument value, complete argument blob, formatting metadata, optional augmented eBPF payload, thread/trace context, private formatter parameter, dynamic-array length, argument index, mask, and prefix display policy. This header is included by individual beauty C files and by `builtin-trace.c` syscall tables.

## Risks And Test Signals
Because this is a shared ABI inside perf, field changes can break many formatters. Risks include inconsistent prefix handling, incorrect argument masks, and augmented payload size misuse. Tests should exercise representative syscall formatters and parsing helpers through `perf trace` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/beauty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.c

## Purpose
This formatter decodes `clone`/related clone flag bitmasks for `perf trace` and masks syscall arguments that are irrelevant unless specific clone flags are present.

## Important APIs, Types, And Functions
The local helper `clone__scnprintf_flags()` includes generated `clone_flags_array.c`, defines `strarray__clone_flags`, and calls `strarray__scnprintf_flags()`. Public formatter `syscall_arg__scnprintf_clone_flags()` uses `CLONE_PARENT_SETTID`, `CLONE_CHILD_SETTID`, `CLONE_CHILD_CLEARTID`, and `CLONE_SETTLS`.

## Control Flow
The formatter reads `flags = arg->val`, conditionally sets bits in `arg->mask` for parent tid pointer, child tid pointer, and TLS arguments when the corresponding clone flags are absent, then returns the rendered flag string.

## State, Dependencies, And Integration
Static generated data maps flag bit positions to names. Runtime state mutation is limited to `arg->mask`, which affects later argument display in `perf trace`. The formatter is exposed as `SCA_CLONE_FLAGS` through `beauty.h`.

## Risks And Test Signals
Correctness depends on generated flag tables and mask bit positions matching syscall argument indexes. Tests should verify flags render with and without `CLONE_` prefixes and that unused pointer arguments are hidden when controlling flags are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.sh

## Purpose
This generator reads UAPI `linux/sched.h` and emits a C string array mapping clone flag bit positions to suffix names for `clone.c`.

## Important APIs, Types, And Functions
It is a shell script taking an optional beauty UAPI linux directory. It uses grep, sed, and xargs to emit `static const char *clone_flags[]`.

## Control Flow
The script selects `tools/perf/trace/beauty/include/uapi/linux/` by default, sets `linux_sched`, prints an array opener, greps `#define CLONE_* 0x...` lines, rewrites each to `<hex> <name_without_CLONE_>`, and formats entries as `[ilog2(value) + 1] = "NAME"`.

## State, Dependencies, And Integration
No persistent state is written directly; the Makefile redirects stdout to a generated include. It depends on bitmask values being powers of two because the generated index uses `ilog2(value) + 1`.

## Risks And Test Signals
The regex only captures hex constants and may miss expression-defined or non-power-of-two flags. Generated output should compile and `perf trace` should decode representative clone flags correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/drm_ioctl.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/drm_ioctl.sh

## Purpose
This generator builds a DRM ioctl command-name array for perf trace ioctl beautification.

## Important APIs, Types, And Functions
The script takes an optional DRM header directory, reads `drm.h` and `i915_drm.h`, and emits `static const char *drm_ioctl_cmds[]`. It preserves `DRM_COMMAND_BASE` with a guarded preprocessor definition before the array.

## Control Flow
It prints `#ifndef DRM_COMMAND_BASE`, copies the `DRM_COMMAND_BASE` define from `drm.h`, then parses generic `DRM_IOCTL_* DRM_IO*` macros into array entries indexed by the ioctl command number. It separately parses i915 private command macros and indexes them at `DRM_COMMAND_BASE + value` with `I915_` prefixes.

## State, Dependencies, And Integration
Output is redirected by `Makefile.perf` into the generated ioctl table included by `trace/beauty/ioctl.c`. It depends on grep/sed regexes and header macro formatting.

## Risks And Test Signals
Format drift in DRM headers can silently drop commands. Device-specific coverage is limited here to i915. Tests should confirm `perf trace` formats common DRM ioctls as `DRM_*` and i915 private ioctls as `DRM_I915_*` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/drm_ioctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/eventfd.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/eventfd.c

## Purpose
This inline beautifier formats `eventfd2` flag values for `perf trace`.

## Important APIs, Types, And Functions
It defines fallback constants for `EFD_SEMAPHORE`, `EFD_NONBLOCK`, and `EFD_CLOEXEC` when system headers lack them. The local formatter is `syscall_arg__scnprintf_eventfd_flags()`, exposed as `SCA_EFD_FLAGS`.

## Control Flow
The formatter returns `NONE` for zero flags. Otherwise it tests known bits in a fixed order, appends `SEMAPHORE`, `CLOEXEC`, and `NONBLOCK` with optional `EFD_` prefix, clears handled bits, and appends any unknown remainder as hex.

## State, Dependencies, And Integration
It has no persistent state and mutates no argument masks. It relies on `scnprintf()` and the `struct syscall_arg` prefix policy. `builtin-trace.c` maps eventfd flags to `SCA_EFD_FLAGS`.

## Risks And Test Signals
Fallback constants must match UAPI values. Tests should cover zero, each known flag, combined flags, prefix suppression, and unknown extra bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fadvise.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fadvise.sh

## Purpose
This generator emits an array mapping `POSIX_FADV_*` advice numbers to names for perf trace formatting.

## Important APIs, Types, And Functions
It reads `fadvise.h` from an optional or default UAPI linux header directory and emits `static const char *fadvise_advices[]`.

## Control Flow
The script greps decimal `POSIX_FADV_*` defines, rewrites each to `<number> <suffix>`, sorts numerically, formats array entries, and filters out s390-specific duplicate/odd `DONTNEED` and `NOREUSE` values at indexes 6 and 7.

## State, Dependencies, And Integration
The generated table is consumed by perf trace syscall argument formatters for fadvise-like syscalls. It depends on grep, sed, sort, xargs, and stable header formatting.

## Risks And Test Signals
The script contains a documented architecture hack and is not fully per-architecture. Cross-architecture perf.data formatting can be wrong for s390-like differences. Tests should verify common advice constants and document the known 6/7 filtering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fadvise.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fcntl.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fcntl.c

## Purpose
This formatter improves `fcntl` tracing by decoding command values, formatting the third argument according to the command, setting return-value formatters, and masking ignored arguments.

## Important APIs, Types, And Functions
Important helpers are `fcntl__scnprintf_getfd()`, `syscall_arg__scnprintf_fcntl_getfd()`, `fcntl__scnprintf_getlease()`, `syscall_arg__scnprintf_fcntl_getlease()`, `syscall_arg__scnprintf_fcntl_cmd()`, and `syscall_arg__scnprintf_fcntl_arg()`. It uses `F_GETFL`, `F_GETFD`, `F_DUPFD_CLOEXEC`, `F_DUPFD`, `F_GETOWN`, `F_GETLEASE`, `F_GET_SEALS`, `F_GETSIG`, `F_SETFD`, `F_SETFL`, `F_SETOWN`, `F_SETLEASE`, lock commands, RW hint commands, and helpers such as `open__scnprintf_flags()` and `syscall_arg__set_ret_scnprintf()`.

## Control Flow
When formatting the command argument, the code installs specialized return-value formatters for commands whose return value is flags, fd flags, fd, pid, or lease type. It masks the third argument for commands that ignore it. When formatting the third argument, it switches on the previously captured command and chooses fd, fd flags, open flags, pid, lease, pointer-as-hex, or long formatting.

## State, Dependencies, And Integration
Runtime state changes occur through `arg->mask` and return-format callback installation. It depends on `linux/fcntl.h` and `beauty.h`. `builtin-trace.c` supplies the fcntl command strarrays and hooks these formatters into syscall metadata.

## Risks And Test Signals
Command coverage must track kernel UAPI. Incorrect mask behavior can hide useful arguments or show meaningless ones. Tests should cover representative get/set/dup/lock commands and return-value formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fcntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/flock.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/flock.c

## Purpose
This formatter decodes `flock` operation bitmasks for `perf trace`.

## Important APIs, Types, And Functions
It defines fallback values for `LOCK_MAND`, `LOCK_READ`, `LOCK_WRITE`, and `LOCK_RW`, then implements `syscall_arg__scnprintf_flock()`. It uses standard `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, and `LOCK_UN` from `linux/fcntl.h` plus the fallback mandatory-locking values.

## Control Flow
The formatter returns `NONE` for zero. It then emits matching known commands with optional `LOCK_` prefix, clears handled bits, and appends leftover bits as hex. It checks compound `LOCK_RW` before separate read/write handling in the declared macro order.

## State, Dependencies, And Integration
No persistent state and no masks are modified. The function is declared as `SCA_FLOCK` in `beauty.h` and used by perf trace syscall tables.

## Risks And Test Signals
There is a minor macro cleanup typo (`#undef P_OP` instead of `P_CMD`), but it is local to preprocessing and generally harmless unless included in a context that reuses the macro name. Tests should cover zero, shared/exclusive/nonblock/unlock, mandatory modes, combined flags, and unknown bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.c

## Purpose
This formatter decodes `AT_*` flags for filesystem syscalls and special-cases `faccessat2` where `AT_EACCESS` reuses a value that can mean something else in other contexts.

## Important APIs, Types, And Functions
It includes generated `fs_at_flags_array.c`, defines `strarray__fs_at_flags`, and implements `syscall_arg__scnprintf_fs_at_flags()` plus `syscall_arg__scnprintf_faccessat2_flags()`. It defines `AT_EACCESS` fallback value `0x200` for older headers.

## Control Flow
Generic `fs_at` formatting delegates to `strarray__scnprintf_flags()`. `faccessat2__scnprintf_flags()` first detects `AT_EACCESS`, emits `EACCESS` with optional `AT_` prefix, clears the bit, then appends any remaining flags through the generated strarray formatter.

## State, Dependencies, And Integration
No state is persisted. The generated array is built by `fs_at_flags.sh`. The functions are exposed through `SCA_FS_AT_FLAGS` and `SCA_FACCESSAT2_FLAGS` in `beauty.h`.

## Risks And Test Signals
Several `AT_*` values are context-specific aliases; using the generic formatter in the wrong syscall can produce misleading names. Tests should cover `AT_EACCESS` for faccessat2 and common directory/symlink/stat flags for generic filesystem syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.sh

## Purpose
This generator emits a bit-indexed `AT_*` flag name array for filesystem-at syscall beautifiers.

## Important APIs, Types, And Functions
It accepts an optional UAPI linux header directory, reads `fcntl.h`, and emits `static const char *fs_at_flags[]`. It uses grep, sed, and xargs with `ilog2(value) + 1` indexing.

## Control Flow
The script filters `#define AT_* 0x...` lines, explicitly excludes context-specific aliases such as `AT_EACCESS`, `AT_STATX_SYNC_TYPE`, handle flags, and `AT_RENAME_NOREPLACE`, then strips the `AT_` prefix and formats entries.

## State, Dependencies, And Integration
The generated table is included by `fs_at_flags.c`. It depends on bitmask values being powers of two and on header defines being hex literals.

## Risks And Test Signals
The intentional exclusions must stay aligned with C-side special cases and syscall-specific formatters. Tests should verify generated entries do not include aliases that would make generic output misleading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsconfig.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsconfig.sh

## Purpose
This generator emits a command-name array for the `fsconfig` syscall's `FSCONFIG_*` command enum.

## Important APIs, Types, And Functions
It takes an optional UAPI linux header directory, reads `mount.h`, and emits `static const char *fsconfig_cmds[]`.

## Control Flow
The script prints the array opener, then uses `sed -nr` to match enum-style lines of the form `FSCONFIG_NAME = NUMBER,` and emits array entries indexed by that number.

## State, Dependencies, And Integration
Output is consumed by `builtin-trace.c`, which defines `strarray__fsconfig_cmds` and uses it for syscall argument formatting. The script depends on mount.h using enum syntax rather than preprocessor defines.

## Risks And Test Signals
If upstream changes formatting or assigns expressions instead of decimal literals, entries may be missed. Tests should check that known commands such as set-string, set-binary, set-path, and command create/reconfigure print symbolically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.c

## Purpose
This formatter decodes `fsmount`/mount attribute flags, including the special zero-valued relative-atime mode.

## Important APIs, Types, And Functions
It includes generated `fsmount_arrays.c`, defines `strarray__fsmount_attr_flags`, and exposes `syscall_arg__scnprintf_fsmount_attr_flags()`. It defines fallbacks for `MOUNT_ATTR__ATIME` and `MOUNT_ATTR_RELATIME`.

## Control Flow
The helper first prints generated flags only if bits outside the atime mask are set. It then checks whether the atime mask equals `MOUNT_ATTR_RELATIME` and appends `RELATIME`, with optional `MOUNT_ATTR_` prefix. The public function reads `arg->val` and delegates.

## State, Dependencies, And Integration
No persistent state is used. The generated array comes from `fsmount.sh`, and the public formatter is declared as `SCA_FSMOUNT_ATTR_FLAGS` in `beauty.h`.

## Risks And Test Signals
Zero-valued flags are awkward in bitmask printers; this file's explicit `RELATIME` handling is the critical edge. Tests should cover zero/relative-atime, non-atime flags, and combinations with noatime/strictatime if present in generated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.sh

## Purpose
This generator emits mount attribute flag arrays for `fsmount.c`.

## Important APIs, Types, And Functions
It reads `mount.h` from an optional/default UAPI linux header directory and emits `static const char *fsmount_attr_flags[]`.

## Control Flow
The script filters `MOUNT_ATTR_` hex defines whose suffix starts with an alphanumeric character, excludes `MOUNT_ATTR_RELATIME` because it is zero-valued, strips the prefix, and indexes names by `ilog2(value) + 1`.

## State, Dependencies, And Integration
It writes generated C to stdout for inclusion by `fsmount.c`. It assumes one-bit hex flag values except for deliberately excluded/special mask values.

## Risks And Test Signals
Mask constants and zero constants need C-side handling rather than generated bit-array entries. Build generation plus `perf trace` formatting tests for mount attributes are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.c

## Purpose
This formatter decodes `fspick` syscall flags for `perf trace`.

## Important APIs, Types, And Functions
It includes generated `fspick_arrays.c`, defines `strarray__fspick_flags`, and exposes `syscall_arg__scnprintf_fspick_flags()`.

## Control Flow
The formatter reads `arg->val` as an unsigned long and delegates directly to `strarray__scnprintf_flags()` with prefix behavior controlled by `arg->show_string_prefix`.

## State, Dependencies, And Integration
No persistent state is used. The generated table is produced by `fspick.sh`, and the formatter is declared in `beauty.h` as `SCA_FSPICK_FLAGS`.

## Risks And Test Signals
Correctness depends almost entirely on generated table freshness and flag bit indexing. Tests should cover known `FSPICK_*` flags, combinations, zero flags, and unknown bit fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.sh -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.sh

## Purpose
This generator emits a bit-indexed array for `FSPICK_*` mount API flags.

## Important APIs, Types, And Functions
It accepts an optional UAPI linux directory, reads `mount.h`, and emits `static const char *fspick_flags[]` using grep, sed, and xargs.

## Control Flow
The script filters hex `#define FSPICK_*` lines, rewrites each into `<value> <suffix>`, and formats entries as `[ilog2(value) + 1] = "SUFFIX"`.

## State, Dependencies, And Integration
No direct state is persisted; Makefile generation captures stdout. The output is included by `fspick.c`.

## Risks And Test Signals
It assumes flags are hex powers of two. Header formatting drift or compound masks would be missed. Tests should ensure generated arrays include all current `FSPICK_*` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_op.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_op.c

## Purpose
This formatter decodes futex operation values and hides syscall arguments that are unused for a given futex command.

## Important APIs, Types, And Functions
It uses `FUTEX_CMD_MASK`, `FUTEX_PRIVATE_FLAG`, `FUTEX_CLOCK_REALTIME`, common futex operations, and fallback definitions for newer ops. The formatter is `syscall_arg__scnprintf_futex_op()`, exposed as `SCA_FUTEX_OP`.

## Control Flow
The function splits `op` into command and option bits, formats the command name or hex fallback, and sets `arg->mask` bits for unused timeout/uaddr2/val3 arguments depending on the command. It then appends `PRIVATE_FLAG` and `CLOCK_REALTIME` suffixes if set.

## State, Dependencies, And Integration
Runtime state mutation is the syscall argument mask, which affects later futex argument display in `perf trace`. The file depends on `linux/futex.h` and `beauty.h` conventions.

## Risks And Test Signals
Futex has command-specific argument meanings, so incorrect masks can make traces misleading. The formatter also needs updates for new futex commands. Tests should cover each command family, private/realtime modifiers, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_op.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_val3.c -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_val3.c

## Purpose
This formatter decodes the futex `val3` bitset argument, primarily recognizing the all-bits match-any sentinel.

## Important APIs, Types, And Functions
It defines fallback `FUTEX_BITSET_MATCH_ANY` as `0xffffffff` and implements `syscall_arg__scnprintf_futex_val3()`, exposed as `SCA_FUTEX_VAL3`.

## Control Flow
The formatter reads `arg->val` as an unsigned int. If it equals `FUTEX_BITSET_MATCH_ANY`, it prints `MATCH_ANY` with optional `FUTEX_BITSET_` prefix. Otherwise it prints the bitset numerically.

## State, Dependencies, And Integration
No persistent state and no argument masks are modified. It is used for futex operations whose `val3` argument carries a bitset, with masking controlled by `futex_op.c`.

## Risks And Test Signals
The fallback numeric format string is `%#xd`, which prints hexadecimal followed by a literal `d`; this may be intentional legacy output or a typo worth review. Tests should check both match-any and arbitrary bitset formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_val3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/linux/socket.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/linux/socket.h

## Purpose
This vendored Linux socket header supplies socket ABI types, constants, helper macros, and kernel syscall prototypes used by perf trace beauty code and generated socket lookup tables.

## Important APIs, Types, And Functions
Important types include `sa_family_t`, `struct sockaddr`, `struct sockaddr_unsized`, `struct linger`, `struct msghdr`, `struct user_msghdr`, `struct mmsghdr`, `struct cmsghdr`, `struct ucred`, and `struct scm_timestamping_internal`. Important macros include `CMSG_ALIGN`, `CMSG_DATA`, `CMSG_SPACE`, `CMSG_LEN`, `CMSG_FIRSTHDR`, `CMSG_OK`, `for_each_cmsghdr`, `AF_*`, `PF_*`, `SOMAXCONN`, `MSG_*`, `SOL_*`, and `MSG_INTERNAL_SENDMSG_FLAGS`.

## Control Flow
The only executable logic is inline ancillary-data iteration: `__cmsg_nxthdr()` advances by aligned cmsg length and returns null if the next header would exceed the control buffer; `cmsg_nxthdr()` wraps it for `struct msghdr`; `msg_data_left()` returns the remaining iterator count.

## State, Dependencies, And Integration
The header depends on `asm/socket.h`, `linux/sockios.h`, `linux/uio.h`, `linux/types.h`, `linux/compiler.h`, and `uapi/linux/socket.h`. In perf's beauty tree, constants feed socket family/level/protocol decoders, while structure definitions support augmented syscall argument interpretation.

## Risks And Test Signals
This copy must track kernel ABI definitions. Drift can cause wrong string tables or struct interpretation for recorded syscalls. Tests should verify socket family, protocol level, message flag, and ancillary-data related formatting against current UAPI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/linux/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/drm.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/drm.h

## Purpose
This vendored Direct Rendering Manager UAPI header defines the generic DRM userspace ABI: core structs, flags, capabilities, ioctl numbers, private ioctl ranges, and event layouts. In this perf tree it is primarily input for DRM ioctl beautifier generation.

## Important APIs, Types, And Functions
Major type groups include legacy DRM core handles (`drm_context_t`, `drm_drawable_t`, `drm_magic_t`), lock/map/buffer/DMA structs, vblank structs, AGP and scatter-gather structs, GEM handle structs, capability structs, PRIME sharing structs, syncobj structs, CRTC sequence structs, client naming, and DRM event structs. Key macros include `DRM_IOCTL_BASE`, `DRM_IO*`, all `DRM_IOCTL_*` command definitions, `DRM_COMMAND_BASE`, `DRM_COMMAND_END`, `DRM_EVENT_*`, `DRM_CAP_*`, `DRM_CLIENT_CAP_*`, syncobj flags, PRIME flags, and legacy lock/stat/map flags.

## Control Flow
There is no runtime control flow; this is an ABI declaration header. Preprocessor flow selects Linux/kernel/BSD type includes, preserves C++ linkage, includes `drm_mode.h`, and exposes userspace typedef aliases outside `__KERNEL__`.

## State, Dependencies, And Integration
The header defines stable binary layouts shared between kernel and userspace. `trace/beauty/drm_ioctl.sh` parses its `DRM_IOCTL_* DRM_IO*` macros and `DRM_COMMAND_BASE` to generate the generic DRM ioctl name array used by `trace/beauty/ioctl.c`. It also relies on companion `i915_drm.h` for i915 private commands.

## Risks And Test Signals
This file is large and ABI-sensitive; local edits can break ioctl numbering or struct layout assumptions. For perf, the main risk is stale or unparsable macros causing missing ioctl names. Tests should regenerate the ioctl table, compile `ioctl.c`, and verify representative generic commands such as `DRM_IOCTL_VERSION`, KMS mode ioctls, GEM/PRIME, syncobj, and recent client/name commands are decoded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/drm.h -->
