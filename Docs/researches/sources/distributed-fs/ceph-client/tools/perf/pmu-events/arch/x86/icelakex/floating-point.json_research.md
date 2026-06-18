# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/floating-point.json

Purpose: Defines 13 Ice Lake Xeon core PMU aliases for floating-point assists and retired scalar/vector floating-point arithmetic. The file supports workload analysis for SSE, AVX, and AVX-512 instruction mix and for detecting microcode FP assist overhead.

Important schema fields and events: All entries use `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and `SampleAfterValue`. `ASSISTS.FP` uses event `0xc1` and umask `0x2`. The remaining 12 aliases use `FP_ARITH_INST_RETIRED` event `0xc7` with umasks that separate scalar single/double (`0x2`/`0x1`), scalar aggregate (`0x3`), 128-bit packed single/double (`0x8`/`0x4`), 256-bit packed single/double (`0x20`/`0x10`), 512-bit packed single/double (`0x80`/`0x40`), aggregate 4-FLOP and 8-FLOP classes (`0x18`, `0x60`), and all vector forms (`0xfc`). Entries are available on generic counters `0,1,2,3,4,5,6,7`.

Control flow: `jevents.py` parses the JSON at build time and emits named aliases into generated `pmu-events.c`. Runtime perf selects the `icelakex` table, then programs raw event `0xc7` or `0xc1` with the requested umask when users request aliases such as `fp_arith_inst_retired.512b_packed_single` or `assists.fp`.

State and persistence behavior: The file is immutable event metadata. Its generated form persists in the perf binary. There is no mutable state, but the descriptions encode important interpretation state: many counts represent instructions retired rather than true FLOP totals, fused multiply-add and dot-product instructions can count twice, and the public descriptions state that DAZ and FTZ MXCSR flags need to be set when using the arithmetic events.

Dependencies and integration points: Depends on perf PMU JSON schema and generated event tables. It integrates with perf stat/record, HPC analysis workflows, and any metrics that derive floating-point intensity from retired instruction classes. It also interacts with workload/compiler behavior because AVX width, FMA use, and denormal handling materially change counts.

Risks: Users may misinterpret instruction counts as operation counts without applying lane width and FMA semantics. Aggregate masks overlap narrower aliases, so summing aliases can double-count. The DAZ/FTZ note is operationally important; denormal behavior or FP exceptions can change assist counts and arithmetic-event reliability. AVX-512 availability and frequency behavior are outside this file, so event presence does not prove a workload actually executed at a given vector width.

Test signals: Validate 13 JSON entries. Build perf and confirm all `ASSISTS.FP` and `FP_ARITH_INST_RETIRED.*` aliases appear. Run scalar, SSE/AVX2, AVX-512, FMA, and denormal-heavy microbenchmarks to check that only the expected width/precision aliases move and that `ASSISTS.FP` increases on assist-prone inputs.
