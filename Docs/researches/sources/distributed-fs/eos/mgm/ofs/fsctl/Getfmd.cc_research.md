<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc

Source read size: 127 lines, 4961 bytes.

## Purpose

Implements `XrdMgmOfs::Getfmd`, an fsctl endpoint that returns file metadata for a decimal file id in EOS env-string form. It is used by clients that need compact metadata without a full proc command.

## Important APIs, Types, and Functions

The endpoint reads `mgm.getfmd.fid`, prefetches metadata with `Prefetcher::prefetchFileMDWithParentsAndWait`, resolves `IFileMD` and full URI, calls `IFileMD::getEnv(fmdEnv, true)`, patches container/name fields, and may allocate a response buffer from `mXrdBuffPool`.

## Control Flow

After write-mode access, stall, redirect, and stats, the handler parses the fid. For nonzero fid it prefetches the file and parents, takes `eosViewRWMutex`, loads file metadata and URI, serializes metadata to an env string, releases the lock, appends the parent container path, patches empty checksum values to `none`, and seals names containing ampersands. Missing or invalid fid returns a `getfmd: retc=<errno>` response. Responses larger than 2 KiB are copied into an aligned XRootD buffer pool allocation.

## State and Persistence Behavior

The function is read-only with respect to namespace state. It uses the metadata prefetch cache and the shared XRootD buffer pool for large transient responses.

## Dependencies and Integration Points

Depends on namespace view/file services, `Path`, `StringConversion`, `BufferManager`, `Prefetcher`, and `mXrdBuffPool`. It returns wire-format env strings compatible with XRootD opaque parsing.

## Risks and Edge Cases

Only decimal fid is accepted. `XrdOucEnv` cannot represent empty checksum values, so the response deliberately rewrites `checksum=` to `checksum=none`; clients must know this sentinel. Names and parent paths with `&` require sealing. Very large metadata depends on buffer-pool max size and failure handling.

## Test Signals

Test existing fid, nonexistent fid, missing fid, metadata with empty checksum, names and parent paths containing `&`, responses above and below 2 KiB, and buffer-pool allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc -->
