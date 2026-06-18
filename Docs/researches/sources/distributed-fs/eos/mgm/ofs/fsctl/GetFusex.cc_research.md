<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc

Source read size: 76 lines, 3114 bytes.

## Purpose

Implements the read-side eosxd/FUSE metadata-stat fsctl entry point `XrdMgmOfs::GetFusex`. It proxies `/proc/user/` requests to the legacy `ProcCommand` path and returns the command result as an `XrdOucBuffer`.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::GetFusex(...)`. It uses `ProcCommand::open("/proc/user/", ininfo, vid, &error)`, `ProcCommand::GetResult(size_t&)`, and returns data through `XrdOucErrInfo::setErrInfo(len, XrdOucBuffer*)`.

## Control Flow

The function enters read mode, applies stall and redirect handling, records `Eosxd::prot::STAT`, validates that the fsctl path is exactly `/proc/user/`, opens a proc command, copies the returned result into malloc-owned memory, wraps it in an `XrdOucBuffer`, and returns `SFS_DATA`. Invalid paths, proc open errors, or allocation failures are reported through `Emsg`.

## State and Persistence Behavior

No durable state is owned. It allocates a buffer that is handed to XRootD error-info ownership. Command side effects depend on the proc command described by `ininfo`.

## Dependencies and Integration Points

Integrates fsctl FUSE stat requests with `ProcCommand`, MGM stats, XRootD buffers, and normal MGM read redirection/stall macros.

## Risks and Edge Cases

The path must include the trailing slash. Result copying uses `malloc(len)` without adding a terminator, which is correct for explicit-length buffers but dangerous if downstream code treats it as C string data. `ProcCommand::GetResult` is virtual/legacy and must provide a stable pointer for the copy.

## Test Signals

Exercise valid `/proc/user/` stat requests, invalid path rejection, command open failure, zero-length and large results, allocation failure injection, and ownership cleanup of the returned `XrdOucBuffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc -->
