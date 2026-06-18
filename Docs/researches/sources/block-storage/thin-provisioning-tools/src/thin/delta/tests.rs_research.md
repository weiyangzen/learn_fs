# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta/tests.rs

This file contains unit tests for delta run construction and delta comparison.

Key elements:
- `DeltaCollector` implements `DeltaVisitor` and stores all received `Delta` values.
- `test_build_runs_()` drives the private `RunBuilder` with keys/data values and compares emitted `DataMapping` runs.
- `test_build_runs()` verifies adjacent mapping coalescing and split runs.
- `test_delta()` builds left/right `DataMapping` inputs, converts compact tuple expectations into `Delta` variants, runs `dump_delta_mappings()`, and compares exact output.

Covered cases:
- Left input ending after right input.
- Right input ending after left input.
- Same regions.
- Left-only and right-only gaps.
- Differing mappings over the same thin-block range.

Interactions:
- Tests private implementation via `use super::*`.
- Uses `ir::Visit` only to satisfy the `DeltaVisitor` trait.

Risks and notes:
- Tests focus on in-memory merge behavior, not btree walking, XML serialization, or device/root resolution.
