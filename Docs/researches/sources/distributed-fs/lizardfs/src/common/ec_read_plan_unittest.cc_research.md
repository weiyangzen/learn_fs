# sources/distributed-fs/lizardfs/src/common/ec_read_plan_unittest.cc

Purpose: tests EC read planning and reconstruction behavior through higher-level planners.

Important APIs/types/functions: helper `ec(k,m,part_index)`, `checkReadingParts`, and `checkReadingChunk`. Tests `VerifyRead1` through `VerifyRead5` target slice-part reads; `VerifyChunkRead1` targets standard chunk reconstruction from EC parts.

Control flow: helpers synthesize part data, prepare planners with target and available parts, assert reading is possible, build a plan, execute it through `ReadPlanTester`, then compare output buffer regions against expected part data.

State and persistence: test-only maps of part data and planner buffers.

Dependencies and integration: includes `slice_read_planner.h`, `chunk_read_planner.h`, chunk type constants, and test plan executor. It validates integration rather than only `ECReadPlan` internals.

Risks: tests cover a small set of `(3,2)` EC cases and do not sweep larger data/parity counts, all parity losses, or impossible read scenarios.

Test signals: strong integration signal that EC planner and Reed-Solomon recovery produce expected buffers for representative missing parts.
