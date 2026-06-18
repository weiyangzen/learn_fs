# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.h

## Purpose
`timerlat.h` defines timerlat-specific parameters and tracing mode selection for RTLA, plus the shared timerlat APIs used by top/hist modes.

## Important APIs, Types, and Functions
`enum timerlat_tracing_mode` documents three modes: BPF-only, tracefs-only, and mixed mode. `struct timerlat_params` embeds `common_params` and adds timerlat period, stack printing, DMA latency, auto-analysis toggle, task dumping, deepest idle-state setting, selected tracing mode, optional BPF action program path, and stack formatting. `to_timerlat_params()` converts from embedded common params. Prototypes expose `timerlat_apply_config()`, `timerlat_main()`, `timerlat_enable()`, `timerlat_analyze()`, and `timerlat_free()`.

## Control Flow and Integration
Timerlat top/hist mode files allocate this struct and use the shared apply/enable/analyze/free functions in their `tool_ops`. `rtla.c` dispatches to `timerlat_main()`.

## State and Persistence
The struct records requested changes to tracefs timerlat period, print stack, CPU DMA latency, CPU idle states, and BPF behavior. Actual persistence is handled by implementation cleanup paths.

## Dependencies and Integration Points
It includes `osnoise.h`, and therefore inherits RTLA common/action/trace utility dependencies. `enum stack_format` comes from the local tracing/util header chain.

## Risks and Edge Cases
Mode selection must stay consistent with BPF support and action/auto-analysis requirements. Fields that use sentinel values, such as DMA latency or deepest idle state, require mode parsers to initialize them correctly.

## Test Signals
Compile timerlat top/hist and run parsers that set all fields, especially BPF action, AA-only, DMA latency, idle-state, and stack-format options.
