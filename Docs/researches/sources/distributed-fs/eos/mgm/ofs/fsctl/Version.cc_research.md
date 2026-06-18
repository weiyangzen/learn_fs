<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc

Source read size: 77 lines, 2872 bytes.

## Purpose

Implements an fsctl endpoint that returns EOS version and optional feature information using the existing proc command implementation.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Version(...)`. It checks `mgm.version.features`, opens `ProcCommand` on `/proc/user` with `mgm.cmd=version` and optional `mgm.option=f`, then streams the proc output into a `version: retc=<retc>` response.

## Control Flow

The handler applies read access, stall, redirect, and records `Version`. It opens the proc command, sets `retc=EINVAL` on open failure, and on success repeatedly reads 4095-byte chunks until EOF or a short read. The final response is returned through `XrdOucErrInfo`.

## State and Persistence Behavior

Read-only. It allocates no persistent state and uses a stack buffer for streaming.

## Dependencies and Integration Points

Depends on `ProcCommand`, the user `version` proc command, XRootD env flags, and normal MGM read routing.

## Risks and Edge Cases

Proc open errors are collapsed to `EINVAL`. The read loop stops on the first short read, assuming normal stream semantics. Large version output is accumulated in memory in an `XrdOucString`.

## Test Signals

Cover normal version output, features output, proc open failure, chunked output larger than 4095 bytes, empty output, and HTTP/FUSE clients consuming the prefixed response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc -->
