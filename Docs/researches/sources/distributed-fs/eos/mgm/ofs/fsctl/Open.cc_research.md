<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc

Source read size: 72 lines, 2891 bytes.

## Purpose

Implements an fsctl endpoint for parallel I/O layout opens. It opens the file through `XrdMgmOfsFile` with an opaque marker requesting PIO access and returns the redirect data as payload.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::Open(...)`. It allocates `XrdMgmOfsFile(client->tident)`, appends `eos.cli.access=pio` to the opaque info, calls `file->open(path, SFS_O_RDONLY, 0, client, opaque.c_str())`, and copies `file->error` into the fsctl error object.

## Control Flow

The handler uses read access, stall, redirect, and `OpenLayout` stats. A successful PIO layout request is expected to return `SFS_REDIRECT`; in that case the error code is replaced with the length of the redirect text and the endpoint returns `SFS_DATA`. Allocation failure returns `SFS_ERROR` with `ENOMEM`.

## State and Persistence Behavior

No persistent state is owned. It opens a temporary `XrdMgmOfsFile` object and immediately deletes it after extracting redirect information.

## Dependencies and Integration Points

Depends on `XrdMgmOfsFile::open`, open-layout redirect semantics, access macros, and XRootD error-info encoding.

## Risks and Edge Cases

Only redirect success is converted to data; non-redirect successful opens would still return `SFS_ERROR`. `client` and `client->tident` are assumed non-null. Opaque concatenation assumes `ininfo` already has compatible separator syntax.

## Test Signals

Test normal read redirect, allocation failure, non-redirect open return paths, opaque construction with existing query parameters, and malformed/null client handling if supported by the surrounding interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc -->
