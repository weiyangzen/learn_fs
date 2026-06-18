<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c

Purpose: implements the ARM kprobe self-test framework, including API tests, kretprobe tests, optional benchmarking, decode-table consistency checks, decode coverage tracking, and the runtime harness that compares direct instruction execution with probed instruction simulation/emulation.

Important functions: `run_all_tests()`, `run_api_tests()`, `test_kprobe()`, `test_kretprobe()`, `run_benchmarks()`, `table_test()`, `coverage_start()`, `coverage_add()`, `coverage_end()`, `__kprobes_test_case_start()`, `kprobes_test_case_start()`, `setup_test_context()`, `kprobes_test_case_end()`, and result-dump helpers. It also defines pre/post handlers for before, case, and after probes.

Control flow: API tests register probes on small ARM/Thumb functions and verify handler calls and unregister behavior. Instruction tests parse inline metadata emitted by `test-core.h`, register probes around the instruction under test, run a reference execution, insert a probe on the instruction, rerun under varied CPSR/IT scenarios, and compare resulting registers and memory. Coverage logic walks decode tables, marks matched entries, and checks register-class coverage.

State and persistence: maintains test counters, current inline test metadata, expected/result `pt_regs`, expected memory snapshots, active test probes, CPSR scenario state, and coverage tables allocated with `kmalloc`.

Dependencies and integration: depends on kprobe APIs, `core.h`, decode tables, ARM/Thumb opcode helpers, and test case catalogs from `test-arm.c` or `test-thumb.c`. Registered as a module init or `late_initcall`.

Risks: the harness manipulates stack, CPSR, IT state, interrupt masking, and PC values; mistakes can produce false failures or unstable tests. Coverage table capacity is fixed at 256 entries. It ignores CPSR A/F bits because kernel context can vary them.

Test signals: final logs report total simulation tests, pass/fail counts, coverage failures, API failures, and benchmark timings. Any nonzero failure returns `-EINVAL` or another error to module/init infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c -->
