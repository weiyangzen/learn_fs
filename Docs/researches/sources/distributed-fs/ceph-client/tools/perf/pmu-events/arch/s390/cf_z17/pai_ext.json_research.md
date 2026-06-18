# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/pai_ext.json

## Purpose
Defines z17 Processor Activity Instrumentation extension events for NNPA and integrated accelerator operations. The aliases expose neural-network processing activity such as arithmetic, activation, pooling, convolution, matrix multiplication, tensor/frame-size classes, and exception/normalization operations.

## APIs, Types, and Functions
The file contains 37 PMU event records with `Unit: PAI-EXT`, event codes 6144 through 6180, and descriptive names. `jevents.py` maps `PAI-EXT` to `pai_ext`. The catalog starts with `NNPA_ALL`, covers operation-level counters (`NNPA_ADD`, `NNPA_MUL`, `NNPA_CONVOLUTION`, `NNPA_MATMUL_OP`), workload-shape counters (`NNPA_SMALLBATCH`, `NNPA_LARGEDIM`, `NNPA_1MFRAME`, `NNPA_2GFRAME`), and newer operations such as `NNPA_GELU`, `NNPA_LAYERNORM`, `NNPA_SQRT`, and `NNPA_REDUCE`.

## Control Flow, State, and Persistence
Build-time parsing produces generated perf event aliases. Runtime selection follows z17 CPU matching and availability of the kernel `pai_ext` PMU. The JSON records are static metadata; the live state is entirely in hardware PAI counters read through perf.

## Dependencies and Integration
Depends on z17 model matching, `jevents.py` unit conversion, and kernel PAI extension support. It relates to `extended.json`, which contains CPU-M-CF NNPA counters for invocations, completions, lock waits, and accelerator locality; this file provides the PAI operation breakdown.

## Risks and Test Signals
Risks are mismatched code assignments, hardware/firmware availability differences for newer NNPA operations, and vague descriptions for workload-shape counters labeled only as counter numbers. Test signals are successful JSON generation, `perf list pai_ext`, alias-to-code inspection in generated `pmu-events.c`, and z17 hardware runs for `NNPA_ALL` plus a few individual operation counters.
