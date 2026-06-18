# sources/distributed-fs/lizardfs/src/common/ec_read_plan.h

Purpose: defines `ECReadPlan`, the erasure-coded slice read plan implementation that reconstructs missing parts through Reed-Solomon.

Important APIs/types/functions: `ECReadPlan : SliceReadPlan`; nested `RecoverParity` computes a parity part from continuous data parts; `postProcessRead` invokes base slice post-processing then calls `recoverParts` if requested parts were unavailable; `recoverParts` configures `ReedSolomon` fragment maps and erased map.

Control flow: `postProcessRead` builds an availability bitset from available chunk parts. If any requested part was missing, `recoverParts` chooses up to `k` available parts as data inputs, maps read operation buffers by slice part, maps missing requested parts to output positions, and calls `rs.recover`.

State and persistence: read-plan state is inherited: requested parts, read operations, buffer sizes, and slice type. No persistence.

Dependencies and integration: depends on `read_plan.h`, `slice_read_plan.h`, `reed_solomon.h`, `Goal::Slice::Type`, and protocol block size. It integrates with `SliceReadPlanner` and `ChunkReadPlanner`.

Risks: relies heavily on assertions for valid EC type, buffer bounds, and matching slice type. The recovery map chooses erased parts once `available_count >= k`, which is correct for decoding but sensitive to read operation preparation.

Test signals: `ec_read_plan_unittest.cc` exercises missing data/parity reads and whole-chunk reconstruction through planner/tester utilities.
