# sources/distributed-fs/ceph-client/fs/gfs2/acl.h

## Purpose
Declares GFS2 POSIX ACL helpers and defines the block-size-scaled maximum ACL entry count.

## Important APIs, Types, And Functions
`GFS2_ACL_MAX_ENTRIES(sdp)` computes the maximum ACL entries from superblock block-size shift. Declarations include `gfs2_get_acl()`, `__gfs2_set_acl()`, and `gfs2_set_acl()`.

## Control Flow
No runtime control flow beyond macro expansion.

## State And Persistence
No state. The macro constrains ACL state stored by `acl.c`.

## Dependencies And Integration Points
Includes `incore.h` for `struct gfs2_sbd` access and is consumed by ACL and inode operation code.

## Risks
The macro must match xattr storage capacity; underestimating rejects valid ACLs, overestimating risks impossible xattr writes.

## Test Signals
Compile users of ACL helpers and test ACL entry limits across supported GFS2 block sizes.
