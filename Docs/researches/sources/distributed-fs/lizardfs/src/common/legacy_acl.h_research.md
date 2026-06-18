<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/legacy_acl.h -->
# sources/distributed-fs/lizardfs/src/common/legacy_acl.h

## Purpose
Provides legacy ACL serialization/conversion wrappers around the newer `AccessControlList` representation. The source was read completely for this report.

## Important APIs, Types, And Functions
`legacy::ExtendedAcl`, nested `Entry`, and `legacy::AccessControlList` convert named user/group entries, owning group masks, and POSIX mode into the old serialized form.

## Control Flow
Assignment from modern ACL extracts group mask and named entries. Conversion back reconstructs a modern ACL and sets mode. Serialization macros write mode and optional extended ACL data.

## State And Persistence Behavior
State is in-memory `mode`, optional `ExtendedAcl`, and entry vectors; persistence occurs only through project serialization.

## Dependencies And Integration Points
Depends on `access_control_list.h`, `massert.h`, and serialization macros. Integrates with metadata/protocol compatibility for older ACL formats.

## Risks And Edge Cases
The copy assignment only resets `extendedAcl` when the source has one; assigning from a legacy ACL without an extended ACL after one with an extended ACL may leave stale state. Schema/order compatibility is sensitive.

## Test Signals
Needs round-trip tests with minimal ACLs, extended ACLs, named users/groups, move/copy assignment, and legacy metadata compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/legacy_acl.h -->
