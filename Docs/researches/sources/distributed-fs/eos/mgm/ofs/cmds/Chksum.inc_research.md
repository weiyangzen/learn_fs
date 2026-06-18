# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chksum.inc

## Purpose

`Chksum.inc` implements XRootD checksum queries for EOS files. It supports the XRootD checksum size probe and checksum get/calc operations, returning the checksum type and hex digest derived from EOS file layout metadata.

## Important APIs, Types, and Functions

- `XrdMgmOfs::chksum(csFunc Func, const char* csName, const char* inpath, XrdOucErrInfo&, const XrdSecEntity*, const char* ininfo)` is the only exported function.
- `csSize` returns a fixed maximum checksum length of 20 bytes.
- `csGet` and `csCalc` both return the existing namespace checksum rather than causing data-plane recalculation.
- `LayoutId::GetChecksumStringReal()`, `GetChecksumLen()`, and `IFileMD::getChecksum()` define the returned checksum type and digest bytes.

## Control Flow

The function handles `csSize` before path mapping and authorization. Other operations perform namespace mapping, identity mapping with `AOP_Stat`, external authorization, access-mode/stall/redirect checks, and file metadata prefetch. It then takes a read lock on `eosViewRWMutex`, fetches the file metadata, detects missing replicas, and may redirect `ENONET` to a remote master if this MGM is not master and the remote master is alive.

For valid `csCalc` or `csGet`, it formats a response as `!<type> <hex-digest>` using the file's layout id and stored checksum bytes, sets that in `XrdOucErrInfo`, and returns `SFS_OK`.

## State and Persistence Behavior

This is read-only against namespace metadata. It increments `IdMap`, `Checksum`, and possible `RedirectENONET` stats. It does not recalculate or persist checksum values, so returned data reflects metadata already stored with the file.

## Dependencies and Integration Points

Dependencies include identity mapping, external authorization, namespace prefetch, `eosView`, master/remote-master routing, `LayoutId`, and XRootD checksum function enums. It integrates with clients that call XRootD checksum APIs and with master/slave redirect behavior for replica-less metadata.

## Risks and Edge Cases

- `csSize` returns 20 unconditionally; clients expecting name-specific support may not get strict validation.
- Missing path returns `EINVAL`; missing file returns `ENOENT` and may trigger stall/redirect macros.
- Files with no committed replicas can redirect to a remote master; remote master id parsing failure is surfaced as an EOS error.
- `csCalc` does not calculate from bytes; it returns stored metadata checksum.
- Buffer formatting relies on fixed `MAXPATHLEN + 8` storage and checksum lengths from layout metadata.

## Test Signals

Tests should cover `csSize`, `csGet`, `csCalc`, invalid function, missing path, missing file, zero-location redirect on slave, checksum type/length per layout, empty checksum formatting, authorization denial, and stats counters.
