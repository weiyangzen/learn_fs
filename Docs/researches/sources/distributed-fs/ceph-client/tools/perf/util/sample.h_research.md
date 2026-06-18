# sources/distributed-fs/ceph-client/tools/perf/util/sample.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample.h` defines the normalized `struct perf_sample` used throughout perf to represent variable-length `PERF_RECORD_SAMPLE` payloads and auxiliary sample metadata.

## Important APIs, Types, and Functions

Important helper types are `struct regs_dump`, `struct stack_dump`, `struct sample_read_value`, `struct sample_read`, `struct aux_sample`, and `struct simd_flags`. Enums `simd_op_flags` and `simd_pred_flags` describe ARM SIMD operation/predicate metadata. Helpers include `sample_read_value_size`, `next_sample_read_value`, `sample_read_group__for_each`, `perf_sample__init`, `perf_sample__exit`, `perf_sample__user_regs`, `perf_sample__intr_regs`, `perf_sample__fetch_insn`, and inline `perf_sample__synth_ptr`.

`struct perf_sample` contains event identity, timing, IP/address, pid/tid/cpu, period, weights, transaction/data-source/page-size/cgroup fields, branch/callchain pointers, register/stack dumps, raw and AUX data pointers, instruction bytes, deferred/merged callchain state, guest machine ids, cpumode/misc, SIMD flags, and read-format counter data.

## Control Flow

The header mostly defines data shape. Inline read-format helpers compute per-value stride based on `PERF_FORMAT_LOST`, iterate grouped read values, and calculate synthetic raw-data pointer alignment.

## State and Persistence Behavior

`perf_sample` is transient runtime state. Many pointer fields alias the original perf event buffer, so the sample lifetime must be shorter than that buffer unless a field is explicitly copied and marked owned, such as merged callchains or lazy regs dumps.

## Dependencies and Integration Points

It includes Linux perf event and type definitions, and forward-declares evsel/machine/thread. It is a central contract for evsel sample parsing, auxtrace synthesis, reporting, scripting, Python/Perl bindings, and raw sample decoders.

## Risks and Edge Cases

Ownership is mixed and must be respected by initialization and exit helpers. The register cache is bounded by a 64-bit mask. `perf_sample__synth_ptr` assumes raw data is four bytes from an eight-byte boundary. Read-format layout changes must stay aligned with kernel perf ABI. Adding fields can affect scripting bindings that pack or expose the struct.

## Test Signals

Tests should verify sample parsing for each `PERF_SAMPLE_*` field, read-format stride with and without lost values, group iteration, raw-data alignment for synthesized events, lifetime cleanup, register cache use, stack/raw/AUX pointer lifetimes, and scripting binding compatibility.
