# sources/distributed-fs/ceph-client/lib/dhry_1.c

## Purpose
Contains the first implementation part of the Dhrystone benchmark, including global benchmark state, main benchmark loop, and several procedures.

## APIs, Types, and Functions
Defines exported benchmark globals `Int_Glob` and `Ch_1_Glob`, plus static globals `Ptr_Glob`, `Next_Ptr_Glob`, `Bool_Glob`, `Ch_2_Glob`, `Arr_1_Glob`, and `Arr_2_Glob`. Internal procedures include `Proc_1`, `Proc_2`, `Proc_3`, `Proc_4`, and `Proc_5`. The public entry is `int dhry(int n)`, which returns a measured Dhrystones-per-second value or an error-style result when validation fails.

## Control Flow
`dhry()` allocates two records, initializes Dhrystone globals and strings, captures start time, runs the historical Dhrystone loop for `n` iterations, captures end time, validates final variable values with assertion macros, frees records, and reports a rate based on elapsed microseconds. The loop exercises procedure calls, string operations, arithmetic, conditionals, and array/record access in the prescribed benchmark pattern. The static procedures mutate record fields, globals, and reference parameters as required by the original benchmark.

## State and Persistence
Benchmark state is global during a `dhry()` run, but records are allocated and freed per invocation. The static arrays and scalar globals retain their final values after a run until overwritten by the next invocation.

## Dependencies and Integration Points
Depends on `dhry.h`, kernel timekeeping, slab allocation, and string helpers. `dhry_run.c` invokes `dhry()` from module init or a module parameter.

## Risks and Test Signals
Risks include compiler optimization altering benchmark semantics, allocation failure, timing granularity for small `n`, overflow in rate calculation for extreme inputs, and validation failures if procedures drift from the Dhrystone reference. Test signals include `dhry()` self-checks, multiple iteration counts, module runner output, and build tests under different optimization levels.
