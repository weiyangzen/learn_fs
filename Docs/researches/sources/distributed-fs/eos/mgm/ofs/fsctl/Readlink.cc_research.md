<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc

Source read size: 68 lines, 2700 bytes.

## Purpose

Implements the FUSE fsctl readlink operation, returning the symlink target in a compact `readlink:` response.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Readlink(...)`. It calls `readlink(path, error, link, client)`, optionally URL-escapes the target when `eos.encodepath` is set, and writes the return code plus target into `XrdOucErrInfo`.

## Control Flow

The handler performs read access, stall, redirect, and stats. It calls the underlying MGM readlink implementation, maps errors from `error.getErrInfo()` or `-1`, and returns `readlink: retc=<retc> [target]`.

## State and Persistence Behavior

Read-only. All state is local to the request.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::readlink`, `StringConversion::curl_escaped`, XRootD env fields, and normal MGM read redirection.

## Risks and Edge Cases

Targets containing spaces or `&` are only escaped when the caller asks for `eos.encodepath`; unencoded callers must handle raw target text. An underlying error with no errno becomes `-1`.

## Test Signals

Cover existing symlink, missing path, permission failure, encoded and raw targets with reserved characters, redirect behavior, and error propagation when `readlink` sets no errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc -->
