# sources/distributed-fs/lizardfs/src/common/xor_read_plan_unittest.cc

Purpose: GoogleTest coverage for XOR slice read planning and `XorReadPlan` recovery behavior.

Important APIs/types/functions: helper `checkUnrecoverable(ChunkPartType, PartsContainer)` expects `SliceReadPlanner::isReadingPossible()` to fail; helper `checkReadingParts(first_block, block_count, target_parts, available_parts)` builds synthetic part data, constructs a plan, executes it with `ReadPlanTester`, and compares output blocks.

Control flow: tests prepare target part indexes from `target_parts`, ask `SliceReadPlanner` to plan against available parts, build a plan for a block range, execute read operations against synthetic data, then compare each target part at the expected output offset. Four unrecoverable cases cover missing parity/incompatible slice setups; four positive cases cover direct reads and XOR recovery with nonzero block offsets.

State and persistence: test-only local maps and buffers; no persistent state.

Dependencies and integration: depends on `common/slice_read_planner.h`, `unittests/chunk_type_constants.h`, and `unittests/plan_tester.h`; validates the common read-planning layer used by client/chunk read paths.

Risks: duplicate `Unrecoverable1`/`Unrecoverable2` inputs reduce negative-case diversity. The tests validate generated output but not all malformed planner states or release-build behavior without assertions.

Test signals: this file is itself the direct test signal for XOR read plans and should run in the common unit test suite when tests are enabled.
