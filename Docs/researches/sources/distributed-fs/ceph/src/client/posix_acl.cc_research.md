# sources/distributed-fs/ceph/src/client/posix_acl.cc

## Purpose
`posix_acl.cc` implements validation, mode conversion, chmod inheritance/update, and permission checks for POSIX ACL extended-attribute blobs.

## Important APIs, Types, and Functions
`posix_acl_check()` validates ACL EA header version, entry alignment, tag ordering, and mask requirements. `posix_acl_equiv_mode()` derives Unix mode bits and reports whether the ACL has named entries or a mask. `posix_acl_inherit_mode()` applies create mode to an inherited ACL buffer. `posix_acl_access_chmod()` updates ACL owner/group/other or mask entries for chmod. `posix_acl_permits()` evaluates requested permission bits against owner, named user, group, mask, and other ACL entries.

## Control Flow
Validation walks entries in required order: user_obj, named users, group_obj, named groups, optional mask, other. Permission evaluation checks owner first, then named user, then matching groups, then other. Named users/groups and group_obj permissions are constrained by a later mask entry when present.

## State and Persistence Behavior
Functions operate directly on xattr buffers. Inheritance and chmod mutate the passed `bufferptr`; checks are read-only. Persistent ACL storage is the caller-managed xattr.

## Dependencies and Integration Points
It depends on Ceph endian integer wrappers, `bufferptr`, mode constants, and `UserPerm`. It is used by client-side permission and mode handling around `system.posix_acl_access` and `system.posix_acl_default`.

## Risks
Invalid ACLs return `-EIO` in mutating/checking paths after structural validation failure. Correct endian wrapper conversion is assumed by assigning to native `__u16`/`__u32`. Mask lookup scans forward from the matched named entry and assumes valid ordering.

## Test Signals
Tests should cover minimal three-entry ACLs, named user/group requiring mask, chmod with and without mask, inherited default ACL masking, owner/group/other permit and deny cases, malformed order, wrong version, and unaligned sizes.
