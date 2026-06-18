<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc

Source read size: 92 lines, 4112 bytes.

## Purpose

Implements `XrdMgmOfs::FuseStat`, the FUSE stat fsctl endpoint. It returns an `lstat` result as a fixed field list in an XRootD buffer.

## Important APIs, Types, and Functions

The endpoint calls `lstat(path, &buf, error, client, ininfo)`, formats `struct stat` fields into `stat: ...`, wraps malloc-owned memory in `XrdOucBuffer`, and returns it through `error.setErrInfo`.

## Control Flow

The function uses `ACCESSMODE_R_MASTER`, stall and redirect handling, records `Fuse-Stat`, executes lstat, and on success formats device, inode, mode, link count, uid/gid, rdev, size, block size/count, and timestamp seconds/nanoseconds. On failure it returns `stat: retc=<errno>`.

## State and Persistence Behavior

Read-only. The response buffer is transferred to XRootD ownership.

## Dependencies and Integration Points

Depends on the MGM stat/lstat implementation, XRootD buffer ownership, and platform-specific timestamp fields.

## Risks and Edge Cases

The success path uses `malloc(16384)` and `sprintf` without checking allocation before formatting. The endpoint forces read-master access, so follower behavior differs from normal read-only stat. The buffer length passed to `XrdOucBuffer` is `strlen(statinfo)`, while `setErrInfo` uses `BuffSize()`.

## Test Signals

Cover file, directory, symlink, missing path, permission failure, null allocation injection, timestamp formatting, and master redirection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc -->
