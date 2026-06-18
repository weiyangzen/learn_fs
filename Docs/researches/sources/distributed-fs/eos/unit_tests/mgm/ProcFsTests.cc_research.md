# sources/distributed-fs/eos/unit_tests/mgm/ProcFsTests.cc

## Purpose
Tests classification helpers for MGM proc filesystem commands that operate on filesystems, scheduling groups, and spaces. It verifies entity type detection and move operation classification.

## Important APIs, types, and functions
The tests call `get_entity_type()` and `get_operation_type()` from `mgm/proc/proc_fs.hh`, expecting `EntityType::{FS,GROUP,SPACE,UNKNOWN}` and `MvOpType::{FS_2_GROUP,FS_2_SPACE,GRP_2_SPACE,SPC_2_SPACE,UNKNOWN}`.

## Control flow
Entity tests pass numeric fs ids, `space.group` strings, simple spaces, and malformed combinations. Move tests pass source/destination strings and verify only supported movement directions are classified.

## State and persistence
No state is modified. Classification results drive command behavior and error paths in proc_fs operations.

## Dependencies and integration points
Depends on Google Test, proc filesystem command helpers, and XRootD `XrdOucString` output/error buffers.

## Risks and test signals
The tests protect common grammar but not whitespace, negative ids, huge numeric ids, or names containing dots. Misclassification could move or configure the wrong scope, so parser edge coverage is important.
