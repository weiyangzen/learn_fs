<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc

Source read size: 70 lines, 2781 bytes.

## Purpose

Implements the FUSE fsctl symlink operation, creating an EOS symlink and returning a compact return-code response.

## Important APIs, Types, and Functions

The endpoint reads env `target`, decodes it with `curl_unescaped` when `eos.encodepath` is set or `UnsealXrdPath` otherwise, and calls `symlink(path, target.c_str(), error, client, 0, 0)`.

## Control Flow

Write access, stall, redirect, and `Fuse-Symlink` stats are applied first. If `target` exists, the target is decoded and passed to the underlying symlink implementation; errors are copied from `error.getErrInfo()`. Missing target returns `EINVAL`. The response is always `symlink: retc=<retc>` with `SFS_DATA`.

## State and Persistence Behavior

The durable side effect is namespace symlink creation. No local persistent state is owned.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::symlink`, XRootD env encoding conventions, and path conversion helpers.

## Risks and Edge Cases

The order of `path` and `target` follows the local `symlink` wrapper signature, not necessarily POSIX naming expectations. Target decoding differs between encoded and sealed modes; callers must set `eos.encodepath` consistently. Existing target/path conflicts are delegated to the underlying implementation.

## Test Signals

Cover encoded and sealed targets, missing target, relative and absolute target strings, existing link path, permission failure, and master redirect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc -->
