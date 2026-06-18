# sources/distributed-fs/ceph-client/lib/dhry_run.c

## Purpose
Provides the loadable/module-parameter wrapper for running the kernel Dhrystone benchmark.

## APIs, Types, and Functions
Defines module parameters `run` and `iterations`. `run` uses a custom `kernel_param_ops` setter `dhry_run_set()` so writing true triggers a benchmark run. `dhry_benchmark()` invokes `dhry(iterations)` and prints results. `dhry_init()` optionally runs the benchmark at module initialization. Module metadata names the author, description, and GPL license.

## Control Flow
If `run` is set at load time or later through the module parameter, `dhry_run_set()` parses the boolean, stores it, and calls `dhry_benchmark()` when true. `dhry_benchmark()` chooses or reports the iteration count, calls `dhry()`, and prints the resulting Dhrystones per second. `dhry_init()` performs the same action when the module is initialized with `run=true`.

## State and Persistence
Persistent module state is `dhry_run` and `iterations`. Benchmark implementation globals live in `dhry_1.c` and are reset by each `dhry()` invocation.

## Dependencies and Integration Points
Depends on module parameter APIs, printk, and `dhry.h`. It integrates the benchmark with module loading and sysfs/module-parameter control.

## Risks and Test Signals
Risks include running CPU-bound benchmark work unexpectedly from parameter writes, invalid iteration values, noisy logs, and benchmark output affected by CPU frequency or scheduling. Test signals include loading with `run=1`, writing the parameter after load, using explicit and default iteration counts, and checking that invalid parameter input is rejected.
