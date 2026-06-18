<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc

Source read size: 73 lines, 2907 bytes.

## Purpose

Implements the FUSE fsctl endpoint for updating file timestamps.

## Important APIs, Types, and Functions

The function reads `tv1_sec`, `tv1_nsec`, `tv2_sec`, and `tv2_nsec`, fills a two-element `timespec` array, and calls `_utimes(path, tvp, error, vid, ininfo)`.

## Control Flow

The handler uses write access, stall, redirect, and `Fuse-Utimes` stats. When all timestamp fields are present, it parses them as base-10 integers, calls `_utimes`, and returns `utimes: retc=<retc>`. Missing fields return `EINVAL`.

## State and Persistence Behavior

The durable side effect is namespace metadata timestamp mutation. No local state persists.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::_utimes`, XRootD env fields, and MGM permission/redirect macros.

## Risks and Edge Cases

Fields are parsed with `strtol` without range or trailing-character validation. Comments label the first element as ctime, although POSIX `utimens`-style arrays are usually atime and mtime; correctness depends on `_utimes`' expected convention. Nanosecond bounds are not checked locally.

## Test Signals

Test valid timestamp updates, missing fields, malformed values, nanosecond overflow/negative values, permission failure, and timestamp ordering expected by `_utimes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc -->
