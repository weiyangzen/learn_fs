<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/richacl.cc -->
# sources/distributed-fs/lizardfs/src/common/richacl.cc

## Purpose
Implements RichACL mode conversion, effective mask computation, inheritance, POSIX-mode equivalence, inode inheritance, and explicit inheritance expansion. The source was read completely for this report.

## Important APIs, Types, And Functions
`RichACL::isSameMode`, `setMode`, `getMode`, `createFromMode`, `allowedToWho`, `groupClassAllowed`, `computeMaxMasks`, `removeInheritOnly`, `checkInheritFlags`, `inherit`, `equivMode`, `inheritInode`, and `createExplicitInheritance` are implemented.

## Control Flow
Mode conversion maps POSIX mode bits to ACL masks, optionally removes delete-child on files, and builds allow/deny ACE sequences. Mask computation walks ACEs in reverse to derive owner/group/other maxima. Inheritance copies directory ACEs to child ACLs according to directory/file/no-propagate/inherit-only flags, then applies auto-inherit/protected behavior. POSIX equivalence attempts to collapse ACLs back to mode bits.

## State And Persistence Behavior
State mutated is the ACL object: flags, owner/group/other masks, and ACE list. Persistence occurs only when ACLs are serialized by higher layers.

## Dependencies And Integration Points
Depends on `richacl.h` definitions for ACE flags/masks and is used by ACL converters, metadata, and permission handling.

## Risks And Edge Cases
ACL semantics are order-sensitive and easy to regress. `equivMode` rejects unsupported ACE flags and non-special entries. File-vs-directory delete-child handling must remain consistent with permission checks.

## Test Signals
Needs broad ACL tests for POSIX-equivalent ACLs, named/group ACEs, inheritance flags, auto-inherit/protected transitions, mask computation, and mode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/richacl.cc -->
