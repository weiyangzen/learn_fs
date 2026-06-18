<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c

## Purpose

This workload creates threads that execute a very large unrolled sequence of arm64 `add` instructions, generating long contiguous code traces for CoreSight validation.

## Research

`struct args` holds a pthread, input seed, and return pointer. `thrfn` loops 10,000 times and executes inline assembly built from nested macros `SNIP1` through `SNIP5`, expanding to a large number of repeated `add %w[in], %w[in], #1` instructions. `new_thr` starts a pthread. `main` validates thread count 1 to 256, seeds each thread's input with `rand()`, starts all threads, and joins them. State is per-thread args only; the arithmetic result is intentionally not consumed. Dependencies are arm64 inline assembly, pthreads, and compiler macro expansion. Integration is with CoreSight AUX packet threshold tests. Risks include compiler optimizing or rejecting the asm constraints, very large generated text size, and runtime/trace volume variability. Test signal is enough decoded ETM packets from the unrolled workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/unroll_loop_thread.c -->
