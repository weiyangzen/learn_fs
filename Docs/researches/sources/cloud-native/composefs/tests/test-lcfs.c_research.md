# sources/cloud-native/composefs/tests/test-lcfs.c

## Purpose
`test-lcfs.c` is the C unit/regression test for public libcomposefs APIs and a handcrafted image-load security regression.

## Important APIs, Types, And Functions
Helpers are `cleanup_node`, `write_cb`, and `testwrite_node`. Test cases are `test_basic`, `test_xattr_addremove`, `test_xattr_doubleadd`, `test_add_uninitialized_child`, `test_hardlinked_whiteout_load`, and `test_no_verity`.

## Control Flow
Tests create nodes, set modes/xattrs, add children, write to an in-memory stream, assert success or expected failure, construct a minimal EROFS image in memory for a hardlinked whiteout, and call fsverity measure on a temp fd.

## State And Persistence
Uses in-memory image buffers and a temporary file for fsverity absence testing. Node refs are managed by cleanup attributes.

## Dependencies And Integration Points
Includes public headers plus EROFS wrapper details for the handcrafted image. Links against `libcomposefs`.

## Risks
Assertions abort on failure, so the executable is suitable for test harnesses but not diagnostic-rich. The hardcoded image layout must track EROFS struct definitions.

## Test Signals
Directly covers child ownership, write validation, xattr unset/set/overwrite semantics, kernel fsverity error canonicalization, and rejection of invalid hardlinked whiteouts that previously risked use-after-free.
