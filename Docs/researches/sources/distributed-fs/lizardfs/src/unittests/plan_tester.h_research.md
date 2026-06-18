# sources/distributed-fs/lizardfs/src/unittests/plan_tester.h

Purpose: Declares `unittests::ReadPlanTester`, a helper for read-plan execution and synthetic chunk data generation.

Important APIs/types/functions: `executePlan`; templated `buildData`; `compareBlocks`; protected read/start/check/build helpers; public state vectors `available_parts_`, `networking_failures_`, `output_buffer_`.

Control flow: The templated `buildData` inspects requested part types, groups by slice type, and delegates to standard, XOR, or EC builders implemented in the `.cc`.

State and persistence: Declares transient test execution state. No persistence.

Dependencies and integration: Depends on `common/read_plan.h` and `slice_traits`. Used by read-plan tests to avoid duplicating data generation and simulation logic.

Risks and test signals: Public mutable state is convenient but can leak between test assertions if reused without `executePlan` reset. Template behavior depends on each part's `getSliceType`.
