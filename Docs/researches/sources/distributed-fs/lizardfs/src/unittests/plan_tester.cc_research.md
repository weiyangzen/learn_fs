# sources/distributed-fs/lizardfs/src/unittests/plan_tester.cc

Purpose: Implements `ReadPlanTester`, a simulator for executing read plans against synthetic standard, XOR, and erasure-coded chunk-part data.

Important APIs/types/functions: `executePlan`; `readDataFromChunkServer`; `startReadOperation`; `startReadsForWave`; `checkPlan`; `buildXorData`; `buildStdData`; `buildECData`; `compareBlocks`.

Control flow: `executePlan` allocates the output buffer, validates plan invariants in debug builds, runs read waves up to 10, records available parts or networking failures, stops when the plan is readable, and runs post-processing. Data builders generate deterministic block-offset payloads; XOR parity is computed with `blockXor`, and EC parity with `ReedSolomon`.

State and persistence: Maintains `available_parts_`, `networking_failures_`, and `output_buffer_` for a simulated execution. No persistence.

Dependencies and integration: Depends on `ReadPlan`, `slice_traits`, `block_xor`, `ReedSolomon`, and chunk constants. Used by read-plan unit tests to verify reconstruction logic without real chunkservers.

Risks and test signals: The simulator asserts non-overlapping read outputs and range bounds in debug builds. It may not model all network behaviors, latency, or partial reads. EC generation must stay aligned with production coding rules.
