# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/floating-point.json

Purpose: defines 28 Nehalem EP floating-point, MMX, SSE, and SIMD integer events. It covers x87 FP assists, floating-point computational uops by ISA/type, MMX/FP transition events, and 64-bit and 128-bit SIMD integer pack, arithmetic, logical, multiply, shift, shuffle/move, and unpack operations.

Important APIs/types/functions: static descriptors use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` on the three `FP_ASSIST.*` precise events. `FP_COMP_OPS_EXE.*` rows share event code `0x10` with different umasks; `SIMD_INT_128.*` uses `0x12`, and `SIMD_INT_64.*` uses `0xFD`.

Control flow: `jevents.py` converts rows into generated perf aliases. Runtime perf programs the selected core event to count FP/SIMD execution, assists, or transition activity. PEBS-capable assist events can be used in sampling flows where supported by kernel and hardware.

State and persistence: static source data. Runtime state exists in programmable PMU counters and optional PEBS buffers. Default sample periods are encoded as metadata; the file itself persists no measurements.

Dependencies and integration points: depends on Nehalem EP core PMU encoding and perf JSON schema. Integrates with `perf stat` for instruction mix analysis and `perf record` for precise FP assist investigation. It complements pipeline and frontend events by exposing execution-unit class rather than generic uop flow.

Risks: old ISA terminology such as MMX, x87, and SSE must remain historically accurate for Nehalem EP; renaming for modern terminology would break aliases. PEBS is only marked on assists, so assuming precise attribution for all FP/SIMD events would be wrong. Shared event codes make umask edits high risk.

Test signals: JSON validation, generated alias inspection, and workload smoke tests using x87 assists, SSE floating point, MMX transitions, and SIMD integer kernels. PEBS tests should specifically target `FP_ASSIST.ALL`, `.INPUT`, and `.OUTPUT`.
