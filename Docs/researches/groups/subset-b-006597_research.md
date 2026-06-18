# Research: subset-b-006597

Grouped research for x86 perf tests under `sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-period.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-period.c

## Purpose
This file implements an x86 perf test suite for AMD IBS sample-period behavior. It exercises both `ibs_fetch` and `ibs_op` PMUs through direct `perf_event_open`, mmap ring-buffer sample collection, period/frequency constraints, `PERF_EVENT_IOC_PERIOD`, invalid configuration rejection, and L3MissOnly filtering. The test is AMD-only, IBS-PMU-only, and intentionally skipped on kernels older than v6.15 because it verifies fixes expected in that kernel generation.

## Important APIs, Types, and Data
The central exported entry point is `test__amd_ibs_period(struct test_suite *, int)`. Global state includes `page_size`, `fetch_pmu`, `op_pmu`, and `perf_event_max_sample_rate`. Local helpers build `struct perf_event_attr` instances with `fetch_prepare_attr()` and `op_prepare_attr()`, using PMU type IDs found through `perf_pmus__find("ibs_fetch")` and `perf_pmus__find("ibs_op")`.

The data tables drive most behavior:

- `struct ibs_configs fetch_configs[]` and `op_configs[]` validate IBS-specific `MaxCnt` configuration encoding.
- `struct ibs_period fetch_period[]` and `op_period[]` validate kernel normalization of period/frequency requests against hardware minimums and granularity.
- `struct ibs_ioctl fetch_ioctl[]` and `op_ioctl[]` validate dynamic period updates through `PERF_EVENT_IOC_PERIOD`.
- `struct ibs_l3missonly fetch_l3missonly` and `op_l3missonly` validate filtered IBS events where hardware discards many tagged operations before software sees a sample.

Ring-buffer helpers `copy_sample_data()`, `rb_read()`, `rb_skip()`, and `rb_drain_samples()` read `PERF_RECORD_SAMPLE` records from an mmaped perf buffer. The sample contract is narrow: `sample_type = PERF_SAMPLE_PERIOD`, so sample records are expected to contain only the header and sampled period payload.

## Control Flow
`test__amd_ibs_period()` initializes page size, reads `/proc/sys/kernel/perf_event_max_sample_rate`, locates IBS PMUs, skips non-AMD/non-IBS/old-kernel systems, resolves the current perf executable path, pins the process to CPU 0, then runs five checks in order:

1. `ibs_config_test()` opens events with period encoded in `attr.config` and drains samples to ensure observed periods equal expected derived periods.
2. `ibs_period_constraint_test()` opens events in period and frequency modes, checks success/error expectations, and validates either exact period equality or minimum-period compliance.
3. `ibs_ioctl_test()` opens a baseline event and applies many period values via `PERF_EVENT_IOC_PERIOD`, expecting acceptance only for valid hardware-aligned values in period mode and broader acceptance in frequency mode.
4. `ibs_freq_neg_test()` ensures an over-large frequency encoded through IBS config is rejected and does not bypass `perf_event_max_sample_rate`.
5. `ibs_l3missonly_test()` runs `perf bench sched messaging` pinned to CPU 0 and validates period constraints under L3MissOnly filtering when the PMU exposes the `l3missonly` format.

The two workloads are deliberately different. `dummy_workload_1()` allocates executable memory, copies two tiny instruction sequences that return 1 and 2, executes them repeatedly, and thereby creates fetch/op activity. `dummy_workload_2()` constructs and invokes `taskset -c 0 <perf> bench sched messaging -g 10 -l 5000` to create memory behavior suitable for L3-miss filtering.

## State and Persistence
No durable repository state is written. Runtime state is kernel and process state: perf event file descriptors, mmaped ring buffers, process CPU affinity, executable memory from `mprotect(PROT_EXEC)`, and a shell command spawned via `system()`. `rb_read()` advances `data_tail` after copying records, so sample consumption is destructive within the mapped buffer. The test mutates selected table rows at runtime when requested frequency exceeds the current kernel `perf_event_max_sample_rate`, changing expected `ret` to `FD_ERROR`.

## Dependencies and Integration Points
The file depends on Linux perf UAPI (`linux/perf_event.h`, `PERF_EVENT_IOC_*`, mmap ring-buffer metadata), syscalls, `sched_setaffinity`, `mprotect`, `uname`, and `/proc/sys/kernel/perf_event_max_sample_rate`. It integrates with perf tooling through `arch-tests.h`, `tests/tests.h`, PMU discovery (`pmu.h`, `pmus.h`), `perf_exe()`, `x86__is_amd_cpu()`, `ARRAY_SIZE`, `strbuf`, and debug logging. The test is registered by `arch-tests.c` with `DEFINE_SUITE_EXCLUSIVE("AMD IBS sample period", amd_ibs_period)`, making it an x86 architecture test but exclusive because it changes CPU affinity and uses CPU-wide events.

## Risks and Edge Cases
The test is hardware-, kernel-, privilege-, and system-load-sensitive. It opens CPU-wide events on CPU 0, so perf paranoid settings, missing IBS support, lack of PMU formats, or container restrictions can cause skips or failures. The ring-buffer drain loop stops when a header cannot be read; if samples are lost or non-sample records dominate, it may report zero samples without failing in some table paths. Executable anonymous memory and `system()` execution increase environmental sensitivity. The kernel-version parser assumes `major.minor` at the start of `utsname.release`; unusual release strings could skip incorrectly. The `period->ret` mutation based on runtime sample-rate policy means repeated calls reuse adjusted expectations.

## Test Signals
Strong positive signals are `TEST_OK` with debug output showing accepted/rejected config values, nonzero samples where available, and period equality or minimum-period compliance. Expected skip signals are non-AMD CPU, missing IBS PMUs, or kernel older than v6.15. Failures indicate regressions in IBS period validation, config-to-period conversion, ioctl validation, perf sample-rate enforcement, or L3MissOnly period clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-period.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-via-core-pmu.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-via-core-pmu.c

## Purpose
This file verifies that AMD IBS op sampling can be reached through selected core PMU event encodings and rejected for unsupported encodings. It is a small architecture test that opens precise perf events and checks whether kernel perf maps or rejects them as expected.

## Important APIs, Types, and Functions
`struct sub_tests` records `type`, `config`, and expected validity. The table contains five cases: CPU cycles valid, instructions invalid, raw `0x076` valid, raw `0x0C1` valid, and raw `0x012` invalid. `event_open()` builds a `struct perf_event_attr` with `disabled = 1`, `precise_ip = 1`, `sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID`, and `sample_period = 100000`, then calls `sys_perf_event_open(&attr, -1, 0, -1, 0)` for CPU 0 across all processes.

The exported entry point is `test__amd_ibs_via_core_pmu(struct test_suite *, int)`. It uses `perf_pmus__find("ibs_op")` as a capability gate and returns `TEST_SKIP` if IBS op PMU is unavailable.

## Control Flow
The test locates `ibs_op`, iterates the static sub-test table, opens each event, logs the event type/config/fd, and marks failure when a valid case cannot open or an invalid case unexpectedly opens. Valid fds are closed immediately. The final status is the OR-style aggregate of all subtests: any mismatch makes the suite return `TEST_FAIL`.

## State and Persistence
There is no persistent state. Runtime state consists only of transient perf file descriptors. The event is opened disabled and not mmaped or enabled, so the test validates event admission rather than collecting samples.

## Dependencies and Integration Points
The file depends on perf UAPI constants, perf's `sys_perf_event_open()` wrapper, PMU discovery (`perf_pmus__find`), and test/debug infrastructure. `arch-tests.c` registers it with `DEFINE_SUITE("AMD IBS via core pmu", amd_ibs_via_core_pmu)`.

## Risks and Edge Cases
The test assumes the kernel and PMU expose the expected AMD IBS forwarding policy. Systems with restrictive perf permissions, virtualized PMUs, or changed raw-event mappings can produce failures unrelated to parser code. It checks `fd > 0` for invalid open success and close handling; file descriptor `0` is unlikely from perf in normal test processes but would not be closed or treated as success by that condition. Because events are CPU-wide on CPU 0, perf_event permissions still matter.

## Test Signals
Expected outcomes are a skip when `ibs_op` is absent, pass when valid events open and invalid events fail, and fail when admission policy differs. Debug lines provide per-case `Pass`/`Fail` evidence with event type and config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-via-core-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/arch-tests.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/arch-tests.c

## Purpose
This file is the x86 architecture test registry for perf's test harness. It declares suite objects and exposes the `arch_tests[]` array consumed by the generic perf test runner to discover x86-specific tests.

## Important APIs, Types, and Functions
The file uses perf test macros from `tests/tests.h` and local prototypes from `arch-tests.h`. It conditionally declares suites:

- `DEFINE_SUITE("x86 instruction decoder - new instructions", insn_x86)` when `HAVE_EXTRA_TESTS` is enabled.
- `DEFINE_SUITE("x86 bp modify", bp_modify)` only on `__x86_64__`.
- `DEFINE_SUITE("AMD IBS via core pmu", amd_ibs_via_core_pmu)`.
- `DEFINE_SUITE_EXCLUSIVE("AMD IBS sample period", amd_ibs_period)`.

It defines explicit `struct test_case` arrays for Intel PT and hybrid parsing, then wraps them in `struct test_suite suite__intel_pt` and `suite__hybrid`.

## Control Flow
There is no runtime algorithm beyond static registration. At compile time, feature macros decide which suite symbols are emitted and which pointers appear in `arch_tests[]`. At runtime, the generic harness walks `arch_tests[]` until the terminating `NULL`, presenting and executing each suite.

## State and Persistence
All state is static process memory: suite descriptors and arrays of test cases. The file writes no persistent data and owns no resources.

## Dependencies and Integration Points
This file integrates all x86 perf tests into the common test runner. It depends on externally defined suite/test entry points such as `intel_pt_pkt_decoder`, `intel_pt_hybrid_compat`, `dwarf_unwind`, `insn_x86`, `bp_modify`, `amd_ibs_via_core_pmu`, `amd_ibs_period`, `hybrid`, and `x86_topdown`. `HAVE_DWARF_UNWIND_SUPPORT`, `HAVE_EXTRA_TESTS`, and `__x86_64__` shape the final registry.

## Risks and Edge Cases
The main risk is registration drift: adding or renaming an x86 test without updating this array makes it invisible to the harness, while including a suite without a matching compiled symbol breaks the build. Ordering also matters for user-visible test lists and for tests marked exclusive. `suite__amd_ibs_period` is exclusive, so it should remain registered through the exclusive macro rather than a normal suite macro.

## Test Signals
Build success verifies all declared suite symbols match enabled feature macros. Runtime `perf test` listing should show Intel PT, optional DWARF unwind and instruction decoder tests, x86 breakpoint modify on x86_64, AMD IBS tests, hybrid parsing, and x86 topdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/arch-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/bp-modify.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/bp-modify.c

## Purpose
This x86_64-only perf test validates kernel ptrace behavior for modifying hardware breakpoints through debug registers. It checks both a successful breakpoint address change and rejection of a bogus address while preserving the original breakpoint.

## Important APIs, Types, and Functions
The file defines two noinline breakpoint targets, `bp_1()` and `bp_2()`, to provide stable function addresses. `spawn_child()` forks a tracee, calls `ptrace(PTRACE_TRACEME)`, raises `SIGCONT` to let the parent attach, then calls `bp_1()` and exits.

`bp_modify1()` writes debug register 0 (`struct user.u_debugreg[0]`) first with `bp_2`, then overwrites it with `bp_1`, enables the breakpoint through debug register 7 (`dr7 = 1`), continues the child, reads `rip` from `struct user_regs_struct`, detaches, and expects the stop RIP to equal `bp_1`.

`bp_modify2()` sets a breakpoint on `bp_1`, enables it, attempts to change debug register 0 to `(unsigned long)-1`, expects that write to fail, then continues the child and verifies it still stops at `bp_1`.

`test__bp_modify()` is the exported test entry point and uses `TEST_ASSERT_VAL` to require both subtests to return `TEST_OK`.

## Control Flow
Each subtest follows the same parent/child control pattern: fork, wait for the trace stop, program debug registers with `PTRACE_POKEUSER`, continue, wait for a breakpoint stop, read `rip` using `PTRACE_PEEKUSER`, detach, then compare the observed instruction pointer against `bp_1`. Failures use `goto out` to ensure detach is attempted.

## State and Persistence
No persistent state is written. Runtime state includes a child process, ptrace relationship, x86 hardware debug registers DR0 and DR7 in the tracee, and signal/wait status. The child is detached at the end of each subtest unless detach itself fails.

## Dependencies and Integration Points
The test depends on x86_64 ptrace ABI details (`struct user`, `u_debugreg[]`, `struct user_regs_struct.rip`), `<asm/ptrace.h>`, Linux wait/signal behavior, and perf's test/debug macros. It is registered only when `__x86_64__` is defined by `arch-tests.c`.

## Risks and Edge Cases
The test is sensitive to ptrace restrictions such as Yama policy, sandboxing, seccomp, container capabilities, and nonstandard debug-register behavior. It assumes the breakpoint trap RIP reported by ptrace equals the function address exactly. If compiler/linker instrumentation, sanitizers, control-flow protection, or architecture behavior changes stop addresses, the equality check may fail. Early child exit paths can leak a still-running child if parent error handling changes; the current detach path mitigates most ptrace setup failures.

## Test Signals
Passing signals are both modify tests reaching `rip == bp_1`. Failure logs identify whether PTRACE_TRACEME, debug-register writes, continue, peek, or detach failed. A failure in the bogus-address path indicates the kernel accepted an invalid debug-register value or lost the original breakpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/bp-modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/dwarf-unwind.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/dwarf-unwind.c

## Purpose
This file supplies x86-specific sample preparation for perf's DWARF unwind tests. It captures the current user register set and copies a bounded slice of the current user stack into a `struct perf_sample` so the generic unwinder can operate on synthetic sample data.

## Important APIs, Types, and Functions
`test__arch_unwind_sample(struct perf_sample *sample, struct thread *thread)` is the exported architecture hook. It obtains the sample's `struct regs_dump` with `perf_sample__user_regs(sample)`, allocates a `PERF_REGS_MAX` register buffer, loads live registers through `perf_regs_load()`, and fills `abi`, `regs`, and `mask` using `PERF_SAMPLE_REGS_ABI` and `PERF_REGS_MASK`.

`sample_ustack()` allocates an 8192-byte buffer, reads the current stack pointer from `regs[PERF_REG_X86_SP]`, locates the containing map via `maps__find(thread__maps(thread), sp)`, bounds the copied stack to the end of the map and `STACK_SIZE`, copies bytes from the live stack, optionally unpoisons them for MemorySanitizer, and stores the result in `sample->user_stack`.

## Control Flow
The exported hook allocates and fills registers first, then delegates stack copying. Stack copying fails if allocation fails or the stack pointer is not found in the thread maps. On success, the sample receives both register and stack data; on failure, it returns `-1` after freeing the stack buffer when appropriate.

## State and Persistence
The function allocates heap buffers for registers and stack data and attaches them to the caller-owned `perf_sample`. It does not free the register buffer after assignment; ownership transfers to the sample/test cleanup path. It does not persist data outside the process.

## Dependencies and Integration Points
The file depends on perf register helpers (`perf_regs.h`), sample/event structures, `thread`, `map`, and `maps` APIs. It is used only when DWARF unwind support is enabled and `arch-tests.c` includes `suite__dwarf_unwind`.

## Risks and Edge Cases
The code copies live stack memory from the current process, so bad map lookup or unexpected stack pointer values cause failure. `map__end(map) - sp` assumes `sp` lies inside the map returned by `maps__find`; incorrect maps could underflow. MemorySanitizer builds need the explicit `__msan_unpoison()` to avoid false positives from copied stack poison. Allocation failure leaves partial sample state if register allocation succeeded but stack allocation fails.

## Test Signals
Success is a prepared sample with valid x86 register mask and non-empty stack dump suitable for unwinding. Failure debug logs distinguish register allocation, stack allocation, and stack map lookup issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/dwarf-unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.awk -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.awk

## Purpose
This AWK script converts annotated `objdump -dSw` output from `insn-x86-dat-src.o` into C initializer rows consumed by the x86 instruction decoder test. It is part of the generator pipeline for `insn-x86-dat-32.c` and `insn-x86-dat-64.c`.

## Important APIs, Variables, and Patterns
The `BEGIN` block emits a generated-file banner and initializes `op`, `branch`, `rel`, and `going`. `/ Start here /` and `/ Stop here /` delimit the source region that should become test data. Disassembly lines matching `/^\s*[0-9a-fA-F]+\:/` are parsed only while `going` is true. The script extracts bytes from fields that look like two hex digits, counts instruction length, escapes tabs in the disassembly text, and emits rows shaped like `{{ bytes }, len, rel, op, branch, "disassembly",},`.

Lines containing `Expecting:` set metadata for the next instruction row. The script scans fields after `Expecting:` into `op`, `branch`, and `rel`, then resets those values after emitting a row.

## Control Flow
Generation is streaming: banner first, toggle active region on markers, capture expected metadata when encountered, and emit one C initializer per matching disassembly line inside the active region. Metadata applies to the next emitted instruction and then returns to defaults.

## State and Persistence
The script itself writes only to stdout. Its transient state is the active-region flag and the expected metadata for the next instruction. Generated persistence happens in the caller script that redirects stdout to `insn-x86-dat-32.c` or `insn-x86-dat-64.c`.

## Dependencies and Integration Points
The script depends on GNU/binutils-style `objdump -dSw` formatting: address-colon prefixes, whitespace-delimited hex byte fields, and source annotation comments containing `Expecting:`. `gen-insn-x86-dat.sh` invokes it after compiling the source fixture in 64-bit and 32-bit modes.

## Risks and Edge Cases
Parser fragility is the main risk. Changes in objdump formatting, localized output, extra non-byte tokens before instruction text, or different source annotation spacing can produce malformed C rows. The script assumes `Expecting:` fields appear in a fixed order and that instruction bytes are exactly two hex characters. It has no explicit error reporting for missing metadata or empty active regions.

## Test Signals
Useful signals are successful regeneration of `insn-x86-dat-32.c` and `insn-x86-dat-64.c`, clean compilation of the generated C includes, and passing `insn_x86` decoder tests. Diffs in generated rows should be reviewed because they may reflect either intended binutils support changes or generator/parser drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.sh -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.sh

## Purpose
This shell script regenerates x86 instruction decoder fixture data from `insn-x86-dat-src.c`. It builds the fixture as both 64-bit and 32-bit objects, disassembles them with objdump, and filters the disassembly through `gen-insn-x86-dat.awk`.

## Important Commands and Behavior
The script uses `set -e`, rejects non-`x86_64` hosts, changes to its own directory, and installs an EXIT trap warning that a newer binutils may be required if generation fails. It then runs:

- `gcc -g -c insn-x86-dat-src.c`
- `objdump -dSw insn-x86-dat-src.o | awk -f gen-insn-x86-dat.awk > insn-x86-dat-64.c`
- `gcc -g -c -m32 insn-x86-dat-src.c`
- `objdump -dSw insn-x86-dat-src.o | awk -f gen-insn-x86-dat.awk > insn-x86-dat-32.c`

The temporary object is removed after each generation pass, the trap is cleared on success, and the script ends by asking the user to inspect `git diff`.

## Control Flow
Generation is sequential and fail-fast. Any failing compiler, objdump, awk, or cleanup command exits the script because of `set -e`; the trap then emits the binutils hint. The 64-bit fixture is generated before the 32-bit fixture.

## State and Persistence
The script overwrites `insn-x86-dat-64.c` and `insn-x86-dat-32.c` in place and temporarily creates `insn-x86-dat-src.o`. It does not commit results or update indexes.

## Dependencies and Integration Points
It depends on an x86_64 host, GCC with 32-bit compilation support (`-m32` multilib headers/libraries as needed for object generation), binutils `objdump`, AWK, and the source annotations understood by `gen-insn-x86-dat.awk`. The generated files are included by `insn-x86.c` when extra tests are enabled.

## Risks and Edge Cases
The script is intentionally host/toolchain-sensitive. Missing 32-bit GCC support, older binutils that cannot decode newer instructions, or objdump formatting changes can fail generation or silently alter fixtures. Because outputs are overwritten before final success, a failure after the first pass can leave one generated file changed and the other stale unless the user reviews the diff.

## Test Signals
Success prints both compile phases and `Done (use git diff to see the changes)`. Downstream validation is a clean build and passing x86 instruction decoder tests with the regenerated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/hybrid.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/hybrid.c

## Purpose
This file tests perf event parsing on x86 hybrid-PMU systems. It verifies that parser output correctly represents PMU-qualified hardware events, event groups mixing hardware/software/raw events, modifiers, raw events, cache aliases, and explicit PMU config terms.

## Important APIs, Types, and Functions
The core data type is `struct evlist_test`, containing an event string, optional validity predicate, and checker callback. `test__hybrid_events[]` enumerates ten parser cases such as `cpu_core/cycles/`, grouped `cpu_core` events, mixed `cpu-clock` groups, raw `r1a`, `cpu_core/r1a/`, explicit `config/config1/config2/period`, `LLC-loads`, and a group containing both `cycles` and `cpu-cycles`.

Checker helpers inspect parsed `struct evlist` and `struct evsel` objects:

- `test_config()` masks `evsel->core.attr.config` with `PERF_HW_EVENT_MASK`.
- `test_perf_config()` performs the same check on `struct perf_evsel`.
- `test_hybrid_type()` extracts the PMU type bits via `PERF_PMU_TYPE_SHIFT`.
- Several `test__hybrid_*` functions assert event count, event type, config, hybrid PMU type, modifiers, and group leader relationships.

`test_event()` owns parser invocation and error handling. `test_events()` runs the table and combines results through `combine_test_results()`. The exported `test__hybrid()` skips non-hybrid systems where `perf_pmus__num_core_pmus() == 1`.

## Control Flow
For each table entry, `test_event()` allocates an evlist, initializes `parse_events_error`, calls `parse_events(evlist, e->name, &err)`, prints parser diagnostics on failure, maps trace-event access errors to `TEST_SKIP`, otherwise runs the entry-specific checker, then cleans up the error object and evlist. `test_events()` preserves failure over later results and preserves skip when previous entries skipped but later entries pass.

## State and Persistence
There is no durable state. Runtime state consists of allocated evlists, evsels, parser error structures, and PMU lookups. Every evlist is deleted before returning from `test_event()`.

## Dependencies and Integration Points
The file depends on perf parser APIs (`parse_events`, `parse_events_error`), evlist/evsel internals, PMU discovery (`perf_pmus__find_by_type`, `perf_pmus__num_core_pmus`), and perf UAPI event type/config constants. `arch-tests.c` registers it as the `"x86 hybrid"` suite with a skip reason of `"not hybrid"`.

## Risks and Edge Cases
The test encodes assumptions about hybrid PMU names beginning with `cpu_`, PMU type packing into `attr.config`, and specific parser behavior for aliases and groups. It runs only meaningful checks on hybrid hosts; non-hybrid systems skip. Event parser behavior involving trace-event permissions can return skip, so parser regressions must be distinguished from environment restrictions. If PMU alias names change, the string fixtures may fail while lower-level event encoding remains valid.

## Test Signals
Passing output means all ten event strings parse and the evlist structure matches expected type/config/group semantics. Failures identify the table index and event string. Skip is expected on non-hybrid machines or when parser errors are solely due to inaccessible trace events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/hybrid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-32.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-32.c

## Purpose
This generated C include provides 32-bit-mode instruction fixtures for perf's x86 instruction decoder tests. Each row pairs raw instruction bytes with expected decode metadata and the original objdump text, allowing `insn-x86.c` to validate decoder length and classification across a broad instruction corpus.

## Important Structure and Data
The file is generated by `gen-insn-x86-dat.sh` and `gen-insn-x86-dat.awk` from `insn-x86-dat-src.c`; the header explicitly says not to edit it by hand. It contains 1,618 initializer entries over 3,244 lines. Each entry has the shape:

`{{ byte0, byte1, ... }, length, rel, op, branch, "objdump disassembly",},`

For this 32-bit fixture, the sampled file contains empty `op` and `branch` strings and `rel` set to `0` throughout the inspected generated rows, so its main value is byte-sequence and length coverage plus disassembly text. The corpus starts with simple and legacy examples such as `rdtsc` and `bound`, includes ModRM/SIB/displacement combinations, and extends into modern VEX/EVEX and special-purpose instructions such as AVX-512 vector operations, MPX `bnd*` instructions, prefetches, `wrmsrns`, `hreset`, `serialize`, TSX load-tracking instructions, SGX instructions, `pconfig`, and `wbnoinvd`.

## Control Flow
There is no executable control flow in this file by itself. It is intended to be included into a test translation unit as a data table. The consuming decoder test iterates entries, feeds the byte array to the x86 instruction decoder, and compares decoded length/classification against the initializer metadata.

## State and Persistence
The file is persistent generated source. It has no runtime mutable state. Any change should come from regenerating the fixture pipeline, not manual edits, so generated diffs remain reproducible from source annotations and toolchain output.

## Dependencies and Integration Points
It depends on the exact initializer schema expected by `insn-x86.c`. It is produced by GCC `-m32`, objdump `-dSw`, and the AWK converter. It is registered indirectly when `HAVE_EXTRA_TESTS` enables the x86 instruction decoder suite in `arch-tests.c`.

## Risks and Edge Cases
Generated fixture drift is the main risk. Different binutils versions may decode instructions differently, add support for newer opcodes, or format operands differently, producing large diffs. Because this is the 32-bit fixture, it covers 32-bit addressing forms such as `%eax`, `%ebp`, SIB addressing, absolute displacements, and 16-bit operand-size prefixes; decoder changes must preserve those mode-specific expectations. Manual edits can desynchronize the fixture from `insn-x86-dat-src.c` and make regeneration noisy.

## Test Signals
The primary test signal is the x86 instruction decoder suite passing with `HAVE_EXTRA_TESTS`. Build failures indicate schema or syntax breakage in the generated include. Runtime decoder failures identify byte sequences whose decoded length or metadata no longer match this fixture, often pointing to instruction decoder regressions or intentional fixture/toolchain updates that need review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-32.c -->
