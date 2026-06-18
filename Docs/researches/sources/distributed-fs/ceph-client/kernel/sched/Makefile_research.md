# sources/distributed-fs/ceph-client/kernel/sched/Makefile

## Purpose
This Makefile defines how the scheduler subsystem is compiled. It sets instrumentation policy, compiler flags, and the main object layout for scheduler compilation units.

## Important APIs, Types, And Functions
There are no C APIs here. Important build variables are `CONTEXT_ANALYSIS_core.o`, `CONTEXT_ANALYSIS_fair.o`, `ccflags-y`, `KCOV_INSTRUMENT`, `KCSAN_SANITIZE`, `KCSAN_INSTRUMENT_BARRIERS`, `CFLAGS_core.o`, `CFLAGS_build_policy.o`, `CFLAGS_build_utility.o`, and `obj-y`.

## Control Flow
Kbuild evaluates warning suppression first, disables KCOV for scheduler files, disables KCSAN sanitization while keeping barrier instrumentation, conditionally adds frame-pointer flags for `core.o`, disables branch profiling for aggregate build files when branch profiling is enabled, then builds `core.o`, `fair.o`, `build_policy.o`, and `build_utility.o`.

## State And Persistence
The file affects build outputs only. Its state is Kbuild configuration derived from Kconfig symbols and make variables; nothing persists at runtime.

## Dependencies And Integration Points
It integrates with Kbuild, compiler feature probing via `cc-disable-warning`, sanitizer/instrumentation infrastructure, profiling flags, architecture frame-pointer expectations, and the aggregate scheduler source files.

## Risks
Instrumentation choices are correctness-sensitive because scheduler code runs in contexts where tracing, KCOV, KCSAN, or branch profiling can add recursion, noise, or noinstr violations. Changing object partitioning can significantly affect build parallelism and compile memory use.

## Test Signals
The key signal is successful kernel build across configurations with and without frame pointers, trace branch profiling, KCOV, and KCSAN. Runtime scheduler tests mainly validate source files included by this build layout rather than the Makefile directly.
