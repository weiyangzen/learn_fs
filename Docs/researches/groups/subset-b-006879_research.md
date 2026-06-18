# Research: subset-b-006879

This grouped report covers POWER PMU event-code and sampling tests, low-level primitive compatibility headers, and ptrace/debug-register tests under `sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.c

## Purpose
`trace.c` implements a small in-memory tracing facility for PMU EBB selftests. It records register/value pairs, counters, strings, indentation markers, and prints a decoded trace with source buffer locations for debugging event-based branch behavior.

## Important APIs, Types, and Functions
Public functions are `trace_buffer_allocate()`, `trace_log_reg()`, `trace_log_counter()`, `trace_log_string()`, `trace_log_indent()`, `trace_log_outdent()`, `trace_buffer_print()`, and `trace_print_location()`. Internal helpers perform bounds checks, linear allocation from the buffer tail, entry allocation, register-name decoding, and per-entry printing.

## Control Flow and State
Allocation creates a `struct trace_buffer` followed by an mmap-backed payload region and initializes `tb->tail` to the first entry slot. Each log call computes payload size, reserves a `struct trace_entry`, writes typed payload data, and advances the tail. Bounds failures set the buffer overflow flag and return errors. Printing walks entries from the beginning to the tail, adjusts indentation on indent/outdent entries, and prints decoded register or counter payloads.

## Dependencies and Integration Points
The code depends on `trace.h`, `utils.h` integer types, libc allocation/mmap APIs, and the EBB tests that call these trace helpers from instrumentation paths. It is a diagnostics layer rather than a kernel interface.

## Risks and Test Signals
Risks include payload-size mistakes, string length including the terminator, tail corruption, and silent truncation after overflow. Useful signals are deterministic trace dumps, clear overflow reporting, correct indentation nesting, and register names matching the PMU SPR values logged by EBB tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.h

## Purpose
`trace.h` defines the EBB trace buffer ABI used by `trace.c` and PMU EBB tests. It describes the entry types and the buffer/entry layouts consumed by trace logging and printing.

## Important APIs, Types, and Functions
It defines `TRACE_TYPE_REG`, `TRACE_TYPE_COUNTER`, `TRACE_TYPE_STRING`, `TRACE_TYPE_INDENT`, and `TRACE_TYPE_OUTDENT`, plus `struct trace_entry` and `struct trace_buffer`. It declares all trace allocation, logging, printing, and location-reporting functions.

## Control Flow and State
There is no control flow in the header. The persistent state contract is that a trace buffer has a byte size, an overflow flag, and a tail pointer, while each entry stores a type and payload size followed by variable payload bytes.

## Dependencies and Integration Points
It includes `utils.h` for `u64` and is included by EBB tracing code. Any producer or printer must agree on entry type values and payload packing.

## Risks and Test Signals
Risks are ABI drift between log producers and `trace_buffer_print()`, unaligned payload assumptions, and callers passing unallocated buffers. Test signals are successful compilation of EBB tracing clients and readable traces for register, counter, string, indent, and outdent entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.c

## Purpose
`event.c` is the shared perf-event wrapper for powerpc PMU selftests. It normalizes `perf_event_attr` initialization, opens events for common pid/cpu/group combinations, controls descriptors with ioctl, reads scaled counter data, and prints event reports.

## Important APIs, Types, and Functions
Important functions are `perf_event_open()`, `event_init_opts()`, `event_init_named()`, `event_init()`, `event_init_sampling()`, `event_open_with_options()`, `event_open_with_group()`, `event_open_with_pid()`, `event_open_with_cpu()`, `event_open()`, `event_close()`, `event_enable()`, `event_disable()`, `event_reset()`, `event_read()`, and report helpers.

## Control Flow and State
Initialization zeroes `struct event`, fills raw or hardware type/config fields, sets disabled/exclude flags, and for sampling enables `PERF_SAMPLE_REGS_INTR` defaults. Open helpers call the syscall with selected pid/cpu/group values and store the fd. Control helpers issue perf ioctls. Reading fills the `result` value/running/enabled triple for scaled counter reporting. State is per `struct event` plus optional mmap buffer ownership held by callers.

## Dependencies and Integration Points
The wrapper depends on Linux `perf_event.h`, syscall numbers, ioctl constants, and `event.h`. It is used by PMU event-code tests, sampling tests, and other powerpc perf selftests.

## Risks and Test Signals
Risks include assuming `read_format` layout, leaking fds on failed grouped opens, and test misuse of raw versus hardware event types. Signals are consistent open/close behavior, correct negative-open handling, and readable counts after enable/workload/disable cycles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.h

## Purpose
`event.h` declares the powerpc PMU selftest perf-event abstraction and the `struct event` state shared by all PMU test programs.

## Important APIs, Types, and Functions
`struct event` embeds `struct perf_event_attr`, an fd, a result triple of value/running/enabled, a name, and an optional mmap buffer pointer. The header declares initialization, open, close, enable, disable, reset, read, and report functions implemented in `event.c`.

## Control Flow and State
The header has no runtime flow, but it fixes the state layout that tests mutate: attributes are configured before open, fd tracks the kernel perf handle, result stores the last counter read, and `mmap_buffer` is used by sampling tests.

## Dependencies and Integration Points
It includes Linux perf UAPI definitions and `utils.h`, and is the common include for event-code, sampling, and top-level PMU tests.

## Risks and Test Signals
Risks are layout mismatches with `event.c`, callers using uninitialized events, and stale fd values after close. Test signals are clean compilation of all PMU tests and predictable event lifecycle behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/Makefile

## Purpose
`Makefile` builds the POWER PMU event-code validation programs that exercise raw event encodings, alternative-event handling, generic PMU fallback, blacklists, and group constraint rejection paths.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It includes the selftests top-level lib.mk, forces 64-bit compilation with -m64, links the shared PMU helpers from ../event.c and sampling_tests/misc.c where needed, and compiles each C file into a standalone kselftest binary.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is successful production and execution of all listed TEST_GEN_PROGS, especially the negative tests that must fail perf_event_open for invalid or incompatible event groups.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/blacklisted_events_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/blacklisted_events_test.c

## Purpose
`blacklisted_events_test.c` verifies that raw PMU events blacklisted for specific POWER9 DD revisions are rejected by the kernel PMU driver while supported platforms skip or continue appropriately.

## Important APIs, Types, and Functions
The central routine is `check_for_power9_version, blacklisted_events, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `PM_DTLB_MISS_16G, PM_DERAT_MISS_2M, PM_DTLB_MISS_2M, PM_MRK_DTLB_MISS_1G, PM_DTLB_MISS_4K, PM_DERAT_MISS_1G`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/blacklisted_events_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p10.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p10.c

## Purpose
`event_alternatives_tests_p10.c` checks POWER10 event alternative selection by opening events with encodings that should map to valid alternatives and by rejecting incompatible grouped alternatives.

## Important APIs, Types, and Functions
The central routine is `event_alternatives_tests_p10, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `PM_RUN_CYC_ALT, PM_INST_DISP, PM_BR_2PATH, PM_LD_MISS_L1, PM_RUN_INST_CMPL_ALT, EventCode_1`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p9.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p9.c

## Purpose
`event_alternatives_tests_p9.c` checks POWER9 event alternative selection and group compatibility using alternate encodings for run cycles, dispatch, branch, load-miss, and completed-instruction events.

## Important APIs, Types, and Functions
The central routine is `event_alternatives_tests_p9, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `PM_RUN_CYC_ALT, PM_INST_DISP, PM_BR_2PATH, PM_LD_MISS_L1, PM_RUN_INST_CMPL_ALT, EventCode_1`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/generic_events_valid_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/generic_events_valid_test.c

## Purpose
`generic_events_valid_test.c` validates that generic perf hardware/cache event types map to legal PMU encodings on supported POWER platforms and under generic compat PMU registration.

## Important APIs, Types, and Functions
The central routine is `generic_events_valid_test, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test alternates positive and negative opens: valid encodings must return a file descriptor, while invalid or unsupported encodings must fail cleanly without leaving stale event descriptors. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/generic_events_valid_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_cache_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_cache_test.c

## Purpose
`group_constraint_cache_test.c` checks that grouped events agree on MMCR1 cache select constraints; a mismatching sibling must fail while a matching sibling opens successfully.

## Important APIs, Types, and Functions
The central routine is `group_constraint_cache, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_cache_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_l2l3_sel_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_l2l3_sel_test.c

## Purpose
`group_constraint_l2l3_sel_test.c` checks group constraints for POWER10 L2/L3 selection bits so grouped events with different l2l3 selectors are rejected.

## Important APIs, Types, and Functions
The central routine is `group_constraint_l2l3_sel, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_l2l3_sel_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_mmcra_sample_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_mmcra_sample_test.c

## Purpose
`group_constraint_mmcra_sample_test.c` checks that grouped events agree on MMCRA random sampling eligibility/sample mode fields before the kernel accepts the group.

## Important APIs, Types, and Functions
The central routine is `group_constraint_mmcra_sample, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_mmcra_sample_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc56_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc56_test.c

## Purpose
`group_constraint_pmc56_test.c` verifies that events requiring PMC5/PMC6 placement are rejected when they violate the PMU group placement constraints.

## Important APIs, Types, and Functions
The central routine is `group_constraint_pmc56, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc56_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc_count_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc_count_test.c

## Purpose
`group_constraint_pmc_count_test.c` verifies the maximum programmable PMC count in one group by opening several events and expecting the excess sibling to fail.

## Important APIs, Types, and Functions
The central routine is `group_constraint_pmc_count, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc_count_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_radix_scope_qual_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_radix_scope_qual_test.c

## Purpose
`group_constraint_radix_scope_qual_test.c` checks POWER radix scope qualifier constraints so grouped events with incompatible RSQ settings cannot be scheduled together.

## Important APIs, Types, and Functions
The central routine is `group_constraint_radix_scope_qual, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_radix_scope_qual_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_repeat_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_repeat_test.c

## Purpose
`group_constraint_repeat_test.c` checks repeated event group behavior and ensures repeated raw events that collide on PMU resources are rejected consistently.

## Important APIs, Types, and Functions
The central routine is `group_constraint_repeat, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode1, EventCode2`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_repeat_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_cmp_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_cmp_test.c

## Purpose
`group_constraint_thresh_cmp_test.c` checks threshold compare group constraints, including the split between POWER9 raw encoding and POWER10 config1 threshold fields.

## Important APIs, Types, and Functions
The central routine is `group_constraint_thresh_cmp, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `p9_EventCode_1, p9_EventCode_2, p9_EventCode_3, p10_EventCode_1, p10_EventCode_2`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_cmp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_ctl_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_ctl_test.c

## Purpose
`group_constraint_thresh_ctl_test.c` checks MMCRA threshold control/start/stop group constraints by mixing compatible and incompatible threshold-control raw encodings.

## Important APIs, Types, and Functions
The central routine is `group_constraint_thresh_ctl, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_ctl_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_sel_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_sel_test.c

## Purpose
`group_constraint_thresh_sel_test.c` checks threshold selector group constraints, rejecting sibling events whose MMCRA threshold selector differs from the leader.

## Important APIs, Types, and Functions
The central routine is `group_constraint_thresh_sel, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_thresh_sel_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_unit_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_unit_test.c

## Purpose
`group_constraint_unit_test.c` checks MMCR1 unit field constraints for grouped events, allowing only siblings with compatible event units.

## Important APIs, Types, and Functions
The central routine is `group_constraint_unit, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_unit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_pmc56_exclude_constraints_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_pmc56_exclude_constraints_test.c

## Purpose
`group_pmc56_exclude_constraints_test.c` checks that PMC5/PMC6 events interact correctly with exclude_user/exclude_kernel attributes and group placement constraints.

## Important APIs, Types, and Functions
The central routine is `group_pmc56_exclude_constraints, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_pmc56_exclude_constraints_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/hw_cache_event_type_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/hw_cache_event_type_test.c

## Purpose
`hw_cache_event_type_test.c` validates perf hardware cache event type/config combinations and rejects invalid cache op/result encodings on POWER PMUs.

## Important APIs, Types, and Functions
The central routine is `hw_cache_event_type_test, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3, EventCode_4`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/hw_cache_event_type_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/invalid_event_code_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/invalid_event_code_test.c

## Purpose
`invalid_event_code_test.c` ensures obviously invalid raw PMU event codes and reserved event-code bit patterns are rejected by perf_event_open.

## Important APIs, Types, and Functions
The central routine is `invalid_event_code, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `EventCode_1, EventCode_2, EventCode_3`.

## Control Flow and State
The test alternates positive and negative opens: valid encodings must return a file descriptor, while invalid or unsupported encodings must fail cleanly without leaving stale event descriptors. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/invalid_event_code_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_sample_elig_mode_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_sample_elig_mode_test.c

## Purpose
`reserved_bits_mmcra_sample_elig_mode_test.c` verifies that reserved MMCRA sample eligibility/mode bits are rejected, with architecture-specific handling for POWER9 versus POWER10/11.

## Important APIs, Types, and Functions
The central routine is `reserved_bits_mmcra_sample_elig_mode, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_sample_elig_mode_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_thresh_ctl_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_thresh_ctl_test.c

## Purpose
`reserved_bits_mmcra_thresh_ctl_test.c` verifies that reserved MMCRA threshold-control bits in raw event encodings are rejected rather than silently programmed.

## Important APIs, Types, and Functions
The central routine is `reserved_bits_mmcra_thresh_ctl, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_thresh_ctl_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/l3_bank_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/l3_bank_test.c

## Purpose
`l3_bank_test.c` is a focused PMU workload test for an L3-bank-related raw event. It allocates a buffer, touches cache-line-spaced offsets, and expects the event to count activity without setup failure.

## Important APIs, Types, and Functions
The central function is `l3_bank_test()`, run through `test_harness()`. It uses `event_init()`, `event_open()`, `event_enable()`, `event_disable()`, `event_read()`, `event_close()`, and `FAIL_IF` from the selftest utilities.

## Control Flow and State
The test allocates `MALLOC_SIZE`, opens the selected PMU event, enables it, performs a simple memory workload over the allocation, disables and reads the event, then releases resources. State is transient heap memory and one perf event descriptor.

## Dependencies and Integration Points
It depends on the local PMU event wrapper, malloc/free, and kernel support for the raw event. It integrates with the kselftest harness as a standalone PMU program.

## Risks and Test Signals
Risks are weak workload signal, event-code unavailability on some CPUs, and memory allocation failure. A pass indicates the L3 event can be programmed and sampled around a memory workload without perf errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/l3_bank_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.c

## Purpose
`lib.c` provides general PMU selftest helpers for parent/child synchronization, child lifecycle cleanup, address-range discovery from `/proc/self/maps`, CPU-consuming child workloads, and perf paranoid-level checks.

## Important APIs, Types, and Functions
Important functions are `sync_with_child()`, `wait_for_parent()`, `notify_parent()`, `notify_parent_of_error()`, `wait_for_child()`, `kill_child_and_wait()`, `parse_proc_maps()`, and the perf paranoia helper exported with `lib.h`. It also defines `libc` and `vdso` address ranges used by tests that reason about user-space mappings.

## Control Flow and State
Pipe helpers exchange fixed parent/child tokens and report child-side error tokens. Wait helpers reap or kill child processes. `parse_proc_maps()` scans current process mappings and records libc/vdso ranges. The CPU-eating child path synchronizes with its parent and spins until killed. State persists only in process globals and pipe/file descriptors.

## Dependencies and Integration Points
The file depends on POSIX pipes, wait/kill, CPU affinity headers, `/proc/self/maps`, `/proc/sys/kernel/perf_event_paranoid`, and kselftest `utils.h`. It supports PMU tests that need deterministic child process coordination or permission gating.

## Risks and Test Signals
Risks are deadlock if token order changes, false mapping detection across libc path variants, and permission checks that skip too broadly. Signals are clean parent/child handshakes, reliable child cleanup, parsed libc/vdso ranges, and accurate skip behavior under restrictive perf paranoid settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.h

## Purpose
`lib.h` declares the shared PMU helper API and small data structures for pipe synchronization and address-range tracking.

## Important APIs, Types, and Functions
It defines the `union pipe` fd layout, `struct addr_range`, external `libc`/`vdso` ranges, parent/child notification helpers, wait/kill helpers, `parse_proc_maps()`, and the perf paranoid requirement helper.

## Control Flow and State
There is no runtime control flow. The header establishes caller-owned pipe descriptors and global address-range state populated by `lib.c`.

## Dependencies and Integration Points
It includes standard integer, bool, stdio, string, and unistd headers and is included by PMU tests that coordinate child workloads or need mapping/perf-permission checks.

## Risks and Test Signals
Risks are descriptor-direction mistakes and global range use before `parse_proc_maps()`. Test signals are successful compile/link of helper users and deterministic synchronization in multi-process PMU tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/loop.S -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/loop.S

## Purpose
`loop.S` defines deterministic POWER assembly workloads for PMU tests: a fixed 32-instruction loop and a variant containing load-linked/store-conditional traffic.

## Important APIs, Types, and Functions
The exported symbols are `thirty_two_instruction_loop` and `thirty_two_instruction_loop_with_ll_sc`, declared with `FUNC_START`/`FUNC_END` from `ppc-asm.h`. Callers pass loop counts and memory operands according to the local selftest ABI.

## Control Flow and State
Each routine executes a predictable instruction sequence and loops with the count register/branch instructions. The LL/SC variant repeatedly exercises reservation and conditional-store behavior. State is limited to caller registers, condition codes, and the memory location touched by the LL/SC loop.

## Dependencies and Integration Points
The file depends on powerpc assembler syntax and the local ppc assembly macro headers. It is linked into PMU tests that need controlled instruction counts or reservation-failure workloads.

## Risks and Test Signals
Risks are ABI/register convention drift, assembler macro incompatibility, and compiler/linker options that alter symbol visibility. Test signals are stable PMU instruction/cycle counts and successful linkage from C tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/loop.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/per_event_excludes.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/per_event_excludes.c

## Purpose
`per_event_excludes.c` tests per-event exclude flags in a perf group, ensuring user/kernel/hypervisor exclusion attributes are honored independently for grouped POWER PMU events.

## Important APIs, Types, and Functions
The main routine is `per_event_excludes()`, using an array of `struct event`, the shared event lifecycle helpers, `parse_proc_maps()`/mapping helpers from `lib.h`, and kselftest assertions.

## Control Flow and State
The test initializes several events with different exclude settings, opens them as a group, runs code paths intended to generate user-space activity, reads counters, and compares which events should have counted. State is a perf event group, read result triples, and process mapping metadata.

## Dependencies and Integration Points
It integrates with perf group scheduling, per-event exclude_user/exclude_kernel semantics, ELF/mapping helpers, and PMU counting.

## Risks and Test Signals
Risks include noisy counts from unexpected code paths, permission restrictions, and platform differences in kernel/hypervisor event visibility. A pass means grouped events can carry distinct exclude attributes without the kernel collapsing them to the leader settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/per_event_excludes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/Makefile

## Purpose
`Makefile` builds the POWER PMU sampling register selftests that verify sampled interrupt register snapshots expose expected MMCR/MMCRA/SIER/BHRB fields.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It uses the same kselftest lib.mk pattern, -m64, local ../event.c wrappers, misc.c sampling helpers, and the assembly branch loop object for BHRB-oriented workloads.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is that every generated sampling binary can run under the harness and either pass on POWER9/POWER10/POWER11 hardware or skip cleanly when PMU extended-register support is absent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_filter_map_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_filter_map_test.c

## Purpose
`bhrb_filter_map_test.c` exercises valid branch-history rolling buffer filter maps, using common and POWER10-specific filters and expecting supported maps to open while unsupported maps fail cleanly.

## Important APIs, Types, and Functions
The central routine is `bhrb_filter_map_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_filter_map_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_no_crash_wo_pmu_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_no_crash_wo_pmu_test.c

## Purpose
`bhrb_no_crash_wo_pmu_test.c` ensures branch-stack sampling requests do not crash on systems without a usable PMU and either skip or fail the event open safely.

## Important APIs, Types, and Functions
The central routine is `bhrb_no_crash_wo_pmu_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test primarily probes support paths: it constructs an event or helper call that may be unsupported, then requires a clean skip/failure result rather than a kernel crash or malformed sample path. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/bhrb_no_crash_wo_pmu_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/check_extended_reg_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/check_extended_reg_test.c

## Purpose
`check_extended_reg_test.c` checks whether perf supports the platform extended interrupt register mask used by the PMU sampling tests.

## Important APIs, Types, and Functions
The central routine is `check_extended_reg_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test primarily probes support paths: it constructs an event or helper call that may be unsupported, then requires a clean skip/failure result rather than a kernel crash or malformed sample path. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/check_extended_reg_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/intr_regs_no_crash_wo_pmu_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/intr_regs_no_crash_wo_pmu_test.c

## Purpose
`intr_regs_no_crash_wo_pmu_test.c` ensures PERF_SAMPLE_REGS_INTR requests do not crash when PMU support is missing or unavailable.

## Important APIs, Types, and Functions
The central routine is `intr_regs_no_crash_wo_pmu_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test primarily probes support paths: it constructs an event or helper call that may be unsupported, then requires a clean skip/failure result rather than a kernel crash or malformed sample path. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/intr_regs_no_crash_wo_pmu_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.c

## Purpose
`misc.c` is the shared support library for POWER PMU sampling and event-code tests. It centralizes platform/PVR gating, raw event-code field masks, perf mmap sample parsing, interrupt-register extraction, threshold-compare conversion, and generic compat PMU detection.

## Important APIs, Types, and Functions
Important exported helpers are `check_pvr_for_sampling_tests()`, `platform_check_for_tests()`, `perf_get_platform_reg_mask()`, `check_extended_regs_support()`, `event_sample_buf_mmap()`, `__event_read_samples()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, `get_thresh_cmp_val()`, `check_for_generic_compat_pmu()`, and `check_for_compat_mode()`. Global state includes `pvr`, `platform_extended_mask`, and the `ev_mask_*`/`ev_shift_*` field tables consumed by `EV_CODE_EXTRACT`.

## Control Flow and State
Platform setup reads `SPRN_PVR`, checks HWCAP2 bits for EBB and architecture level, probes `PERF_SAMPLE_REGS_INTR`, then initializes event-code field layouts differently for POWER9 versus POWER10/POWER11. Sampling helpers mmap the perf ring buffer, read `data_head`/`data_tail` with a memory barrier, count or return samples, skip branch-stack records when present, and map register names to indexes in the interrupt register array. Threshold comparison conversion clamps POWER10 thresholds and encodes mantissa/exponent values to match MMCRA programming. State is process-global and must be initialized before tests use `EV_CODE_EXTRACT` or `get_reg_value`.

## Dependencies and Integration Points
The library depends on `event.h`, perf UAPI sample formats, auxv platform strings, `/sys/bus/event_source/devices/cpu/caps/pmu_name`, Power ISA HWCAP2 flags, and kselftest utility helpers. It is linked by both `event_code_tests` and `sampling_tests`.

## Risks and Test Signals
Risks are stale field masks for new CPUs, off-by-one register-mask checks, perf ring-buffer parsing assumptions, and false generic-PMU detection if sysfs or auxv changes. Strong signals are clean skips on unsupported systems, successful sample collection, correct register-field extraction across POWER9/10/11, and no mmap parser overrun when branch-stack records precede register payloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.h

## Purpose
`misc.c` is the shared support library for POWER PMU sampling and event-code tests. It centralizes platform/PVR gating, raw event-code field masks, perf mmap sample parsing, interrupt-register extraction, threshold-compare conversion, and generic compat PMU detection.

## Important APIs, Types, and Functions
Important exported helpers are `check_pvr_for_sampling_tests()`, `platform_check_for_tests()`, `perf_get_platform_reg_mask()`, `check_extended_regs_support()`, `event_sample_buf_mmap()`, `__event_read_samples()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, `get_thresh_cmp_val()`, `check_for_generic_compat_pmu()`, and `check_for_compat_mode()`. Global state includes `pvr`, `platform_extended_mask`, and the `ev_mask_*`/`ev_shift_*` field tables consumed by `EV_CODE_EXTRACT`.

## Control Flow and State
Platform setup reads `SPRN_PVR`, checks HWCAP2 bits for EBB and architecture level, probes `PERF_SAMPLE_REGS_INTR`, then initializes event-code field layouts differently for POWER9 versus POWER10/POWER11. Sampling helpers mmap the perf ring buffer, read `data_head`/`data_tail` with a memory barrier, count or return samples, skip branch-stack records when present, and map register names to indexes in the interrupt register array. Threshold comparison conversion clamps POWER10 thresholds and encodes mantissa/exponent values to match MMCRA programming. State is process-global and must be initialized before tests use `EV_CODE_EXTRACT` or `get_reg_value`.

## Dependencies and Integration Points
The library depends on `event.h`, perf UAPI sample formats, auxv platform strings, `/sys/bus/event_source/devices/cpu/caps/pmu_name`, Power ISA HWCAP2 flags, and kselftest utility helpers. It is linked by both `event_code_tests` and `sampling_tests`.

## Risks and Test Signals
Risks are stale field masks for new CPUs, off-by-one register-mask checks, perf ring-buffer parsing assumptions, and false generic-PMU detection if sysfs or auxv changes. Strong signals are clean skips on unsupported systems, successful sample collection, correct register-field extraction across POWER9/10/11, and no mmap parser overrun when branch-stack records precede register payloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_cc56run_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_cc56run_test.c

## Purpose
`mmcr0_cc56run_test.c` samples an event and verifies the MMCR0 CC56RUN field matches the expected counter 5/6 run behavior.

## Important APIs, Types, and Functions
The central routine is `mmcr0_cc56run, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_cc56run_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_exceptionbits_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_exceptionbits_test.c

## Purpose
`mmcr0_exceptionbits_test.c` samples MMCR0 and verifies exception-control bits such as PMAE/PMAO are exposed with expected values.

## Important APIs, Types, and Functions
The central routine is `mmcr0_exceptionbits, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_exceptionbits_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc1ce_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc1ce_test.c

## Purpose
`mmcr0_fc56_pmc1ce_test.c` checks the relationship between MMCR0 FC56 and PMC1CE for sampled events using PMC placement constraints.

## Important APIs, Types, and Functions
The central routine is `mmcr0_fc56_pmc1ce, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc1ce_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc56_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc56_test.c

## Purpose
`mmcr0_fc56_pmc56_test.c` verifies sampled MMCR0 counter freeze state for PMC5/PMC6 events.

## Important APIs, Types, and Functions
The central routine is `mmcr0_fc56_pmc56, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_fc56_pmc56_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmccext_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmccext_test.c

## Purpose
`mmcr0_pmccext_test.c` verifies sampled MMCR0 PMCCEXT state against the event being counted.

## Important APIs, Types, and Functions
The central routine is `mmcr0_pmccext, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmccext_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmcjce_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmcjce_test.c

## Purpose
`mmcr0_pmcjce_test.c` verifies sampled MMCR0 PMCjCE state for the selected event.

## Important APIs, Types, and Functions
The central routine is `mmcr0_pmcjce, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr0_pmcjce_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_comb_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_comb_test.c

## Purpose
`mmcr1_comb_test.c` verifies that the sampled MMCR1 combine field equals the raw event combine encoding.

## Important APIs, Types, and Functions
The central routine is `mmcr1_comb, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_comb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_sel_unit_cache_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_sel_unit_cache_test.c

## Purpose
`mmcr1_sel_unit_cache_test.c` drives L3/cache load activity and compares sampled MMCR1 PMCxSEL, unit, and cache fields to the raw event code.

## Important APIs, Types, and Functions
The central routine is `mmcr1_sel_unit_cache, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `MALLOC_SIZE, EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr1_sel_unit_cache_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_fcs_fch_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_fcs_fch_test.c

## Purpose
`mmcr2_fcs_fch_test.c` verifies sampled MMCR2 freeze-control bits, with a signal handler path used to distinguish hypervisor-related behavior.

## Important APIs, Types, and Functions
The central routine is `sig_usr2_handler, mmcr2_fcs_fch, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `the raw event selected in the file`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_fcs_fch_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_l2l3_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_l2l3_test.c

## Purpose
`mmcr2_l2l3_test.c` checks POWER10 sampled MMCR2 L2/L3 selector programming using an L3 demand-load workload.

## Important APIs, Types, and Functions
The central routine is `mmcr2_l2l3, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode, MALLOC_SIZE`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr2_l2l3_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr3_src_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr3_src_test.c

## Purpose
`mmcr3_src_test.c` checks POWER10/11 sampled MMCR3 source field extraction against the event encoding.

## Important APIs, Types, and Functions
The central routine is `mmcr3_src, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcr3_src_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_any_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_any_test.c

## Purpose
`mmcra_bhrb_any_test.c` requests branch stack sampling and verifies MMCRA branch-filter mode for any branch.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_any_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode, IFM_ANY_BRANCH`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_any_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_cond_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_cond_test.c

## Purpose
`mmcra_bhrb_cond_test.c` requests conditional-branch BHRB filtering and verifies the sampled MMCRA IFM field.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_cond_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode, IFM_COND_BRANCH`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_cond_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_no_branch_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_no_branch_test.c

## Purpose
`mmcra_bhrb_disable_no_branch_test.c` checks that non-branch sampling leaves BHRB disabled in sampled MMCRA where expected.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_disable_no_branch_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_no_branch_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_test.c

## Purpose
`mmcra_bhrb_disable_test.c` checks MMCRA BHRB disable state when branch stack sampling is configured.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_disable_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_disable_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_ind_call_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_ind_call_test.c

## Purpose
`mmcra_bhrb_ind_call_test.c` requests indirect-call branch filtering and verifies sampled MMCRA IFM programming.

## Important APIs, Types, and Functions
The central routine is `mmcra_bhrb_ind_call_test, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode, IFM_IND_BRANCH`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_bhrb_ind_call_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_cmp_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_cmp_test.c

## Purpose
`mmcra_thresh_cmp_test.c` verifies sampled MMCRA threshold compare programming, including POWER10 mantissa/exponent conversion from config1.

## Important APIs, Types, and Functions
The central routine is `mmcra_thresh_cmp, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `p9_EventCode, p10_EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_cmp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_marked_sample_test.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_marked_sample_test.c

## Purpose
`mmcra_thresh_marked_sample_test.c` verifies sampled MMCRA marked, sample mode, threshold selector, and threshold start/stop fields.

## Important APIs, Types, and Functions
The central routine is `mmcra_thresh_marked_sample, main`, run by `test_harness()` from `main()`. It uses `struct event`, `event_init_sampling()`, `event_sample_buf_mmap()`, `collect_samples()`, `get_intr_regs()`, `get_reg_value()`, and field decoders from `misc.h`; key constants include `EventCode`.

## Control Flow and State
The test calls `check_pvr_for_sampling_tests()` or `platform_check_for_tests()`, initializes a sampling `struct event`, enables PERF_SAMPLE_REGS_INTR and sometimes branch-stack sampling, maps the perf ring buffer, runs a small workload, disables the event, counts samples, extracts interrupt registers, and compares sampled fields with helper decoders. State lives in perf event descriptors, the mmap sample buffer, global platform masks initialized by `misc.c`, and transient workload memory or branch-loop execution.

## Dependencies and Integration Points
The file integrates with the powerpc PMU driver, perf sampling ring buffers, interrupt-register sample ABI, POWER9/POWER10/POWER11 HWCAP/PVR detection, and kselftest fail/skip macros.

## Risks and Test Signals
Risks include insufficient workload to overflow, unsupported hardware incorrectly failing rather than skipping, register-mask changes, and architecture-specific bit layouts. A pass means at least one valid sample is collected where required and the sampled PMU control fields match the event configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/sampling_tests/mmcra_thresh_marked_sample_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/Makefile

## Purpose
`Makefile` builds the low-level primitive test directory, centered on load_unaligned_zeropad and local copies of small kernel headers needed by that userspace harness.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It depends on the powerpc selftests make infrastructure and header search paths that point at the primitives asm/linux shim directories.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is a successful load_unaligned_zeropad binary and a pass across page-boundary offsets with exception-table fixups active.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-compat.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-compat.h

## Purpose
`asm-compat.h` provides assembler compatibility macros that let copied powerpc kernel assembly headers build in the selftest environment across 32-bit and 64-bit modes.

## Important APIs, Types, and Functions
Key macros include `PPC_LL`, `PPC_STL`, `PPC_STLU`, compare aliases, `PPC_LONG`, `PPC_LONG_ALIGN`, `PPC_TLNEI`, `PPC_LLARX`, and `PPC_STLCX`. They abstract load/store width and directive differences.

## Control Flow and State
The file has no runtime flow. At assembly/preprocess time it selects instruction mnemonics and data directives based on word size and build defines.

## Dependencies and Integration Points
It is included by `ppc_asm.h` and other local kernel-header copies used by assembly or inline-assembly primitive tests.

## Risks and Test Signals
Risks are incorrect width selection, missing macro aliases for a compiler mode, and divergence from kernel headers. Signals are successful assembly of `loop.S`, `ptrace-gpr.S`, and primitive code under the intended 64-bit selftest build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-const.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-const.h

## Purpose
`asm-const.h` is a minimal guard header for assembly constant compatibility in the primitives selftest copy of powerpc headers.

## Important APIs, Types, and Functions
It provides only the include guard and no active constants in this selftest snapshot.

## Control Flow and State
There is no runtime flow or state.

## Dependencies and Integration Points
It exists so headers imported from the kernel tree can include `<asm/asm-const.h>` without requiring the full kernel include environment.

## Risks and Test Signals
The risk is future imported code requiring missing constant helpers. The signal is continued successful build of primitive tests with this reduced header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/extable.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/extable.h

## Purpose
`extable.h` supplies the relative exception-table macros used by the userspace `load_unaligned_zeropad` test to emulate kernel-style fault fixups.

## Important APIs, Types, and Functions
It defines `ARCH_HAS_RELATIVE_EXTABLE` and macros such as `EX_TABLE(_fault, _target)` that emit relative instruction/fixup entries into the `__ex_table` section.

## Control Flow and State
No C runtime flow exists in the header. At assembly time, faulting instruction and fixup label offsets are emitted; at runtime the test's SIGSEGV handler walks these entries and redirects NIA to the fixup target.

## Dependencies and Integration Points
It is included by `word-at-a-time.h` and consumed by `load_unaligned_zeropad.c` through linker-provided `__start___ex_table` and `__stop___ex_table` symbols.

## Risks and Test Signals
Risks are malformed relative offsets, section-name mismatch, and linker behavior changes. A pass means the SIGSEGV handler finds entries and resumes execution at the expected fixup code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/feature-fixups.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/feature-fixups.h

## Purpose
`feature-fixups.h` is a copied powerpc header that describes feature-fixup section entry formats and assembler macros for alternative instruction patching. In this selftest tree it mainly supports headers that expect these macros to exist.

## Important APIs, Types, and Functions
Important macros include `FTR_ENTRY_LONG`, `FTR_ENTRY_OFFSET`, `START_FTR_SECTION`, `FTR_SECTION_ELSE_NESTED`, `MAKE_FTR_SECTION_ENTRY`, `BEGIN_FTR_SECTION`, `END_FTR_SECTION`, and related CPU/MMU/firmware feature section helpers. It also declares kernel-side fixup functions when built in kernel context.

## Control Flow and State
In userspace selftests the macros are compile/assembly-time constructs. They can emit section metadata but do not run patching code in the test process. State is encoded in ELF sections if a macro is used.

## Dependencies and Integration Points
It is included by `ppc_asm.h` and keeps copied assembly macros close to kernel form while building outside the kernel.

## Risks and Test Signals
Risks are macro drift from the kernel copy, accidental emission of unresolved kernel symbols, and alternative-section size mismatches. Test signals are clean assembly/preprocessing of primitive and ptrace assembly helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/feature-fixups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/firmware.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/firmware.h

## Purpose
`firmware.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc-opcode.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc-opcode.h

## Purpose
`ppc-opcode.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc-opcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc_asm.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc_asm.h

## Purpose
`ppc_asm.h` is a substantial copied powerpc assembler helper header. It supplies register names, function-label macros, save/restore sequences, address-loading helpers, stack-frame layout, feature-fixup hooks, timebase/TLB/cache helpers, and endian-aware vector save/restore macros used by selftest assembly.

## Important APIs, Types, and Functions
Important macros include `FUNC_START`, `FUNC_END`, `_GLOBAL`, `_GLOBAL_TOC`, `SAVE_GPRS`, `REST_GPRS`, `ZEROIZE_GPRS`, `SAVE_FPR`, `SAVE_VR`, `SAVE_VSR`, HMT priority macros, `LOAD_REG_IMMEDIATE`, `LOAD_REG_ADDR`, `PPC_CREATE_STACK_FRAME`, `MFTB`, `TLBSYNC`, `tophys`, `tovirt`, `MTMSRD`, and the `r0` through `r31` register aliases.

## Control Flow and State
The header has no standalone runtime flow. Its macros expand into assembly that saves/restores architectural registers, builds ABI-correct stack frames, loads addresses under TOC or PC-relative models, and emits feature-fixup metadata where configured. State affected by generated code includes GPRs, FPRs, vector registers, LR, CR, stack memory, timebase reads, and TLB/cache instructions.

## Dependencies and Integration Points
It depends on the local `linux/stringify.h`, `asm/asm-compat.h`, `asm/processor.h`, `asm/ppc-opcode.h`, `asm/firmware.h`, `asm/feature-fixups.h`, and `asm/extable.h` shims. It is included by PMU and ptrace assembly helpers copied from kernel-style code.

## Risks and Test Signals
Risks are high because macro changes alter hand-written assembly ABI behavior, symbol visibility, endian handling, or register save layout. Signals are successful assembly across 64-bit selftests and correct runtime behavior of loops, ptrace GPR helpers, and exception-table primitive tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/ppc_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/processor.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/processor.h

## Purpose
`processor.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/bitops.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/bitops.h

## Purpose
`bitops.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/stringify.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/stringify.h

## Purpose
`stringify.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/stringify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/wordpart.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/wordpart.h

## Purpose
`wordpart.h` defines small word-splitting and byte-repetition macros used by copied kernel string/word-at-a-time helpers.

## Important APIs, Types, and Functions
It provides `upper_32_bits()`, `lower_32_bits()`, `upper_16_bits()`, `lower_16_bits()`, `REPEAT_BYTE()`, and `REPEAT_BYTE_U32()`.

## Control Flow and State
All behavior is macro expansion at compile time or inline expression evaluation. No persistent state is held.

## Dependencies and Integration Points
It is included by `word-at-a-time.h` and supports endian/word-size independent byte-mask calculations in the primitive test.

## Risks and Test Signals
Risks include incorrect casts or shifts on 32-bit versus 64-bit builds. Test signals are correct zero-byte detection and load_unaligned_zeropad results at every page offset.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/wordpart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/load_unaligned_zeropad.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/load_unaligned_zeropad.c

## Purpose
`load_unaligned_zeropad.c` is a userspace harness for the powerpc `load_unaligned_zeropad()` primitive. It validates that unaligned word loads crossing into an inaccessible page are fixed up and zero-padded like the kernel helper expects.

## Important APIs, Types, and Functions
Important routines are `__fls()`, `protect_region()`, `unprotect_region()`, `segv_handler()`, `setup_segv_handler()`, `do_one_test()`, `test_body()`, and `main()`. It defines local `struct extbl_entry` matching the relative exception-table entries emitted by `word-at-a-time.h`.

## Control Flow and State
The test mmaps two pages, fills the first with byte values and the second with zeros, installs a SIGSEGV handler, and iterates over every starting offset in the first page. For each offset it reads the expected value while the second page is accessible, protects the second page, calls `load_unaligned_zeropad()`, and compares the result. On SIGSEGV the handler searches `__ex_table`, computes absolute instruction and fixup addresses from relative offsets, and rewrites the saved NIA to resume at the fixup. State includes page protection, signal context, and linker-provided exception-table bounds.

## Dependencies and Integration Points
It integrates `word-at-a-time.h`, `asm/extable.h`, `UCONTEXT_NIA` from the selftest utilities, mmap/mprotect, and kselftest harness macros.

## Risks and Test Signals
Risks are signal-context portability, linker section mismatch, incorrect fixup offset math, and failure to restore page protections during expected reads. A pass across all page offsets is a strong signal that the primitive and exception-table emulation match kernel behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/load_unaligned_zeropad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/word-at-a-time.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/word-at-a-time.h

## Purpose
`word-at-a-time.h` is a copied kernel helper for detecting zero bytes in machine words and for safely loading unaligned words with zero padding across a fault boundary.

## Important APIs, Types, and Functions
It defines architecture-specific `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, `zero_bytemask()`, and `load_unaligned_zeropad()`. The load helper uses exception-table annotations through `EX_TABLE`.

## Control Flow and State
The zero-byte helpers are inline arithmetic/bit operations that produce masks and byte indexes. `load_unaligned_zeropad()` performs an unaligned load and, if a protected following page faults, uses the exception-table fixup to mask unavailable bytes to zero. State is only local registers plus exception-table metadata consumed by the test's signal handler.

## Dependencies and Integration Points
It depends on `linux/wordpart.h`, `asm/extable.h`, powerpc bit operations such as count-leading/trailing-zero helpers provided by the including test, and the primitives harness.

## Risks and Test Signals
Risks include endian-specific mask errors, bad exception-table annotations, and undefined behavior around page boundaries. Test signals are exact agreement between protected zero-padded loads and normal loads from a temporarily unprotected zero-filled second page.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/Makefile -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/Makefile

## Purpose
`Makefile` selects the ptrace powerpc selftests, splitting always-built tests from 64-bit-only transactional-memory, pkey, hardware-breakpoint, TAR, syscall, and VSX programs.

## Important APIs, Types, and Functions
The important interface is the make variable contract: `TEST_GEN_PROGS`, local `CFLAGS`, object prerequisites, and `top_srcdir`/`include .../lib.mk`. These names tell the kselftest runner which binaries are generated and which shared helper objects are pulled in.

## Control Flow and State
There is no runtime control flow in the file itself. During `make`, the selected test names are expanded into output binaries, helper objects are compiled once, and the kselftest framework installs or runs the resulting programs. State is limited to make variables and generated build artifacts under the output directory.

## Dependencies and Integration Points
It pulls in kselftest lib.mk, disables PIE for register/assembly assumptions, links local assembly helpers, and uses kernel UAPI headers for ptrace, pkeys, and breakpoint structures.

## Risks and Test Signals
Risks are mostly build-contract risks: stale `TEST_GEN_PROGS` lists can omit a test, incorrect relative `top_srcdir` breaks the shared selftest rules, and missing `-m64` changes ABI assumptions in PMU or ptrace register tests. The signal is successful build of TEST_GEN_PROGS and runtime pass/skip results on hardware with the required ptrace, TM, pkey, DAWR, and perf capabilities.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/child.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/child.h

## Purpose
`child.h` provides semaphore-based parent/child synchronization helpers for powerpc ptrace tests, including fail/skip macros that wake the other side before exiting.

## Important APIs, Types, and Functions
It defines `struct child_sync`, `CHILD_FAIL_IF`, `PARENT_FAIL_IF`, `PARENT_SKIP_IF_UNSUPPORTED`, `init_child_sync()`, `destroy_child_sync()`, `wait_child()`, `prod_child()`, `wait_parent()`, and `prod_parent()`.

## Control Flow and State
Initialization creates two process-shared semaphores and clears give-up flags. Parent and child alternate wait/post operations; fail macros set the appropriate flag and post the peer so tests do not deadlock. State is held in shared memory containing semaphores and flags.

## Dependencies and Integration Points
The header depends on POSIX semaphores and kselftest macros from `ptrace.h`/utils users. It is used by pkey core/ptrace tests that coordinate register reads while the child changes access rights.

## Risks and Test Signals
Risks are process-shared semaphore failures, missed wakeups on early exit, and tests forgetting to destroy semaphores. Signals are deterministic parent/child progress and clean skip/fail propagation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/child.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/core-pkey.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/core-pkey.c

## Purpose
`core-pkey.c` verifies that POWER protection-key registers are written into ELF core notes correctly. It drives a child to set AMR/IAMR/UAMOR values, forces a core dump, and inspects the resulting core file.

## Important APIs, Types, and Functions
Important routines are `increase_core_file_limit()`, `child()`, `try_core_file()`, `next_note()`, `check_core_file()`, `parent()`, `write_core_pattern()`, `setup_core_pattern()`, `core_pkey()`, and `main()`. `struct shared_info` carries synchronization and expected pkey register values.

## Control Flow and State
The test raises the core size limit, optionally adjusts `/proc/sys/kernel/core_pattern`, creates shared memory, forks, has the child allocate pkeys and update pkey registers, then crashes to produce a core. The parent waits, mmaps the core file, scans ELF notes for pkey register data, compares AMR/IAMR/UAMOR values, and restores core_pattern if changed. Persistent external state is limited to core_pattern and generated core files; both are cleaned/restored by the test path.

## Dependencies and Integration Points
It integrates ptrace/pkey helpers, ELF note parsing, SysV shared memory, `/proc/sys/kernel/core_pattern`, resource limits, and kernel core-dump pkey note support.

## Risks and Test Signals
Risks include insufficient privilege to change core_pattern, small core limits, stale core files, note layout changes, and pkey allocation failure. A pass means core notes preserve the pkey registers established by the child.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/core-pkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/perf-hwbreak.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/perf-hwbreak.c

## Purpose
`perf-hwbreak.c` stress-tests perf hardware breakpoints/watchpoints on powerpc. It covers read/write modes, exclude_user behavior, DAWR-length ranges, overlap semantics, multiple breakpoints, and process versus system-wide event placement.

## Important APIs, Types, and Functions
Important helpers are `perf_event_attr_set()`, process/cpu/system-wide perf open wrappers, fd control helpers, `breakpoint_test()`, `perf_breakpoint_supported()`, `dawr_supported()`, `runtestsingle()`, `runtest_dar_outside()`, multi-DAWR test functions, `get_nr_wps()`, `runtest()`, and `perf_hwbreak()`.

## Control Flow and State
The test first probes breakpoint and DAWR support, discovers online CPUs/watchpoint capacity, and raises fd limits for system-wide runs. Single tests open a disabled breakpoint, enable it around deterministic reads/writes, read counts, and compare against expected hits. Overlap tests watch subranges and verify no/partial/full overlap counts. Multi-watchpoint tests open pairs on same or different addresses and in process or per-CPU modes. State includes perf fds, volatile watched globals, CPU affinity masks, and watchpoint counts.

## Dependencies and Integration Points
It uses `perf_event_open`, `PERF_TYPE_BREAKPOINT`, `linux/hw_breakpoint.h`, powerpc `PPC_PTRACE_GETHWDBGINFO` probing, CPU affinity/sysinfo APIs, and kselftest reporting.

## Risks and Test Signals
Risks are noisy counts from compiler optimizations, CPU hotplug reducing available CPUs, privilege restrictions for system-wide perf, and hardware differences in DAWR overlap semantics. Strong signals are exact expected counts for read/write/exclude combinations and correct multi-watchpoint behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/perf-hwbreak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.S -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.S

## Purpose
`ptrace-gpr.S` is the assembly child loop for the GPR/FPR ptrace test. It loads known nonvolatile GPR and FPR values, synchronizes with shared-memory flags, and loops so the parent can inspect registers.

## Important APIs, Types, and Functions
The exported function is `gpr_child_loop`; macros define GPR size, first tested GPR, number of GPRs, and stack space. It uses constants from `ptrace-gpr.h` and basic assembly helpers.

## Control Flow and State
The routine establishes known register contents, signals readiness through shared pointers, waits for parent progression, and keeps registers live for ptrace reads. State is architectural register contents plus shared-memory flags.

## Dependencies and Integration Points
It integrates with `ptrace-gpr.c`, `ptrace-gpr.h`, and the powerpc ptrace register-access ABI.

## Risks and Test Signals
Risks are compiler/assembler ABI drift, register clobbering, and shared-memory synchronization errors. Passing means the parent observes the expected GPR/FPR patterns through ptrace.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.c

## Purpose
`ptrace-gpr.c` validates ptrace access to general-purpose and floating-point registers by comparing parent-read register sets against values loaded by an assembly child loop.

## Important APIs, Types, and Functions
Important functions are `child()`, `trace_gpr()`, `rand_reg()`, `ptrace_gpr()`, and `main()`. It uses validation helpers from `ptrace-gpr.h` and the external `gpr_child_loop()` assembly routine.

## Control Flow and State
The test creates shared memory, forks, lets the child initialize registers and stop/loop, then the parent attaches or waits, reads GPR/FPR data through ptrace APIs, validates expected values, writes randomized values where applicable, and repeats until pass/fail. State includes shared-memory flags, child pid/status, and expected register constants.

## Dependencies and Integration Points
It depends on `ptrace.h`, register definitions, SysV shared memory, `ptrace-gpr.S`, and kselftest macros.

## Risks and Test Signals
Risks are register save/restore ABI changes, endian/word-width random generation issues, and child synchronization races. A pass means ptrace reports and updates the expected GPR/FPR values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.h

## Purpose
`ptrace-gpr.h` defines known GPR/FPR test values and inline validation helpers shared by GPR and transactional-memory GPR ptrace tests.

## Important APIs, Types, and Functions
It defines `GPR_1` through `GPR_4`, floating constants and their bit representations, plus `validate_gpr()`, `validate_fpr()`, and `validate_fpr_double()`.

## Control Flow and State
Validation helpers scan register arrays for expected values and return match status. No persistent state is held.

## Dependencies and Integration Points
The header is included by `ptrace-gpr.c`, `ptrace-tm-gpr.c`, and `ptrace-tm-spd-gpr.c` to keep register expectations consistent.

## Risks and Test Signals
Risks are floating representation assumptions and array-length mismatches. Test signals are all expected values found in ptrace-read register buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-hwbreak.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-hwbreak.c

## Purpose
`ptrace-hwbreak.c` tests ptrace-managed powerpc hardware breakpoints using both legacy `PTRACE_SET_DEBUGREG` and `PPC_PTRACE_SETHWDEBUG`. It covers exact and range watchpoints, aligned and unaligned ranges, kernel accesses to user buffers, DAWR maximum length, and multiple watchpoints.

## Important APIs, Types, and Functions
Important routines are `get_dbginfo()`, `dawr_present()`, `write_var()`, `read_var()`, `test_workload()`, `check_success()`, `ptrace_set_debugreg()`, `ptrace_sethwdebug()`, `ptrace_delhwdebug()`, `get_ppc_hw_breakpoint()`, many `test_sethwdebug_*()` cases, `ptrace_hwbreak()`, and `main()`.

## Control Flow and State
The child calls `PTRACE_TRACEME`, stops for the parent, then executes a scripted sequence of watched loads/stores. The parent programs each watchpoint before continuing the child, waits for SIGTRAP, validates `siginfo.si_addr` against the expected watched range, single-steps non-8xx children past before-execute watchpoints, deletes handles when needed, and advances to the next case. State includes watched globals/arrays, DAWR feature flags, ptrace handles, signal status, and child register execution state.

## Dependencies and Integration Points
It integrates with powerpc ptrace debug UAPI, DAWR/DABR hardware, syscall `getcwd` for kernel access to userspace, signal delivery, and kselftest macros.

## Risks and Test Signals
Risks include randomized accesses hiding edge failures, hardware-specific before/after execute behavior, incorrect 8xx special handling, and watchpoint slot exhaustion. A pass means ptrace reports SIGTRAP at addresses within expected aligned ranges for every watchpoint mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-hwbreak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-asm.S -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-asm.S

## Purpose
`ptrace-perf-asm.S` provides tiny, label-rich child workloads for `ptrace-perf-hwbreak.c`. The labels let the C test reason precisely about watched load instructions and trap points.

## Important APIs, Types, and Functions
It exports `same_watch_addr_child` and `perf_then_ptrace_child`, plus instruction labels such as `same_watch_addr_load`, `same_watch_addr_trap`, `perf_then_ptrace_load1`, `perf_then_ptrace_load2`, and `perf_then_ptrace_trap`.

## Control Flow and State
The first helper loads from one watched address and traps. The second loads from one address, immediately loads from a second address, then traps. State is limited to registers and watched memory values supplied by the C caller.

## Dependencies and Integration Points
It depends on `ppc-asm.h` function macros and is linked with `ptrace-perf-hwbreak.c`. The exported labels are part of the test contract.

## Risks and Test Signals
Risks are instruction scheduling changes, label removal, or ABI mismatch. Test signals are deterministic child PC values at load and trap labels and correct ptrace/perf watchpoint ordering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-hwbreak.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-hwbreak.c

## Purpose
`ptrace-perf-hwbreak.c` tests interactions between ptrace watchpoints and perf breakpoint counters on the same child, especially priority and instruction-resume semantics when both mechanisms watch the same or adjacent loads.

## Important APIs, Types, and Functions
Important helpers are syscall wrappers for ptrace, `ptrace_getreg_pc()`, `ptrace_setreg_pc()`, `perf_event_open()`, `perf_watchpoint_open()`, `perf_read_counter()`, `ppc_ptrace_init_breakpoint()`, `check_watchpoints()`, `ptrace_fork_child()`, `same_watch_addr_test()`, `perf_then_ptrace_test()`, and `main()`. It also consumes assembly labels from `ptrace-perf-asm.S`.

## Control Flow and State
The parent forks a stopped tracee, checks that at least two watchpoints are available, programs ptrace and perf watchpoints, then continues or single-steps child assembly helpers. For the same-address case, ptrace should trap before the load and perf should not count until the instruction actually executes. For the perf-then-ptrace case, the test validates ordering across consecutive load instructions and may adjust the child PC to known labels. State includes child PC/registers, perf fd counts, ptrace breakpoint handles, watched values, and wait statuses.

## Dependencies and Integration Points
It integrates perf `PERF_TYPE_BREAKPOINT`, powerpc ptrace hardware debug UAPI, assembly helper labels, waitpid signal control, and kselftest assertions.

## Risks and Test Signals
Risks are PC-label mismatch with assembly, ptrace/perf semantic changes, and hardware lacking multiple watchpoints. Passing signals show ptrace before-execute priority and perf after-execute counting remain coherent when both subsystems target nearby data accesses.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-hwbreak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-pkey.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-pkey.c

## Purpose
`ptrace-pkey.c` verifies ptrace read/write behavior for POWER pkey registers AMR, IAMR, and UAMOR while a child actively uses protection keys.

## Important APIs, Types, and Functions
Important routines are `child()`, `parent()`, `ptrace_pkey()`, and `main()`. `struct shared_info` stores synchronization state, valid and invalid AMR/IAMR/UAMOR values, and expected register results.

## Control Flow and State
The child allocates pkeys, maps memory with selected access permissions, updates pkey registers, and synchronizes around user read/write phases. The parent ptrace-attaches, reads pkey registers, attempts valid and invalid writes, checks kernel rejection of disallowed values, and resumes the child. State is shared memory, pkey allocations, child registers, and ptrace stop status.

## Dependencies and Integration Points
It depends on local `pkeys.h`, `child.h`, powerpc ptrace register sets, memory protection key syscalls, and kselftest macros.

## Risks and Test Signals
Risks are absent pkey hardware, permission-dependent ptrace failures, and stale expected masks. A pass means ptrace exposes pkey registers accurately and enforces valid writable bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-pkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-syscall.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-syscall.c

## Purpose
`ptrace-syscall.c` tests powerpc syscall tracing and restart behavior, including register state observed at syscall-entry/exit stops and behavior around syscall emulation controls.

## Important APIs, Types, and Functions
Important pieces are register aliases for syscall number/arguments/IP, `PTRACE_SYSEMU`, global `nerrs`, `wait_trap()`, `test_ptrace_syscall_restart()`, `ptrace_syscall()`, and `main()`.

## Control Flow and State
The test forks a tracee, uses ptrace syscall-stop control, inspects and modifies `struct pt_regs`, verifies syscall arguments and restart/IP behavior, and accumulates errors before returning the kselftest result. State is child register state, wait status, errno/results, and the error counter.

## Dependencies and Integration Points
It integrates with powerpc syscall ABI register layout, ptrace syscall tracing, auxiliary vector platform checks, and kselftest utilities.

## Risks and Test Signals
Risks are ABI differences across 32/64-bit or compat modes, syscall restart semantic changes, and incorrect stop classification. A pass means traced syscall stops expose consistent registers and restart behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.c

## Purpose
`ptrace-tar.c` validates ptrace access to the Target Address Register-related state, along with PPR and DSCR values, using a child that writes known SPR values.

## Important APIs, Types, and Functions
Important functions are `tar()`, `trace_tar()`, `trace_tar_write()`, `ptrace_tar()`, and `main()`, with validation constants from `ptrace-tar.h`.

## Control Flow and State
The child writes known TAR/PPR/DSCR sequences and synchronizes with the parent. The parent reads the corresponding register set through ptrace, validates values, writes alternate values, and resumes the child to verify changes. State includes shared-memory flags, child SPR state, and ptrace status.

## Dependencies and Integration Points
It depends on powerpc ptrace register access, shared memory synchronization, and SPR semantics for TAR/PPR/DSCR.

## Risks and Test Signals
Risks are unsupported SPRs on some hardware, register-set layout changes, and synchronization races. A pass means ptrace reads and writes the expected TAR/PPR/DSCR values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.h -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.h

## Purpose
`ptrace-tar.h` provides known TAR, DSCR, and PPR constants plus validation logic for TAR-related ptrace tests.

## Important APIs, Types, and Functions
It defines `TAR_*`, `DSCR_*`, and `PPR_*` constants and the inline `validate_tar_registers()` helper.

## Control Flow and State
The validation helper compares a three-entry register buffer against expected TAR, PPR, and DSCR values and returns whether all fields match. No persistent state is held.

## Dependencies and Integration Points
It is included by `ptrace-tar.c` and related transactional-memory SPR tests to share constants.

## Risks and Test Signals
Risks are wrong register order assumptions and unsupported SPR state. Test signals are exact matches after ptrace reads and writes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-gpr.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-gpr.c

## Purpose
`ptrace-tm-gpr.c` validates ptrace visibility of GPRs in transactional checkpointed state on POWER transactional-memory systems.

## Important APIs, Types, and Functions
Important functions are `tm_gpr()`, `trace_tm_gpr()`, `ptrace_tm_gpr()`, and `main()`. It uses `tm.h` transaction helpers and GPR validation constants from `ptrace-gpr.h`.

## Control Flow and State
The child enters a transactional-memory sequence, loads known GPR values into transactional or suspended state, records TEXASR/result information, and synchronizes with the parent. The parent uses ptrace to read the relevant register set and validates that expected GPR values are present. State includes shared memory, TM checkpoint/suspended registers, TEXASR, and child stop status.

## Dependencies and Integration Points
It depends on POWER TM hardware/kernel support, ptrace TM register sets, shared memory, and kselftest skip/pass macros.

## Risks and Test Signals
Risks are TM disabled by firmware/kernel, transaction failure modes changing register state, and ptrace register-set ABI drift. A pass means ptrace exposes the correct GPR values for the tested TM state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-gpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-gpr.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-gpr.c

## Purpose
`ptrace-tm-spd-gpr.c` validates ptrace visibility of GPRs in suspended transactional state on POWER transactional-memory systems.

## Important APIs, Types, and Functions
Important functions are `tm_spd_gpr()`, `trace_tm_spd_gpr()`, `ptrace_tm_spd_gpr()`, and `main()`. It uses `tm.h` transaction helpers and GPR validation constants from `ptrace-gpr.h`.

## Control Flow and State
The child enters a transactional-memory sequence, loads known GPR values into transactional or suspended state, records TEXASR/result information, and synchronizes with the parent. The parent uses ptrace to read the relevant register set and validates that expected GPR values are present. State includes shared memory, TM checkpoint/suspended registers, TEXASR, and child stop status.

## Dependencies and Integration Points
It depends on POWER TM hardware/kernel support, ptrace TM register sets, shared memory, and kselftest skip/pass macros.

## Risks and Test Signals
Risks are TM disabled by firmware/kernel, transaction failure modes changing register state, and ptrace register-set ABI drift. A pass means ptrace exposes the correct GPR values for the tested TM state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-gpr.c -->
