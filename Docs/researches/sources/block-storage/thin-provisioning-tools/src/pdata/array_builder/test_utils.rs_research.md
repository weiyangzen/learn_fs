# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/test_utils.rs

This file provides test utilities for building arrays and inspecting their layout.

Important components:
- `ArrayLayout` stores emitted array block locations plus the B-tree layout.
- Accessors expose height, node counts, root node, nodes/leaves by height, array blocks, and first array block under a tree node.
- `build_array_blocks()` builds raw array blocks from a value slice.
- `build_array_from_values()` builds array blocks and manually builds a B-tree layout from array-block mappings.

Integration points:
- Used by array-builder tests to validate physical layout and B-tree structure.
- Reuses B-tree builder test utilities.

Risks and notes:
- `build_array_from_values()` asserts that values are nonempty.
- Layout introspection assumes B-tree test utilities remain aligned with production builder behavior.
