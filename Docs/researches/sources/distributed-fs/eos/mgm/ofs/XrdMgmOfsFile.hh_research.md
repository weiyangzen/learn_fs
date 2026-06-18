# Research: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.hh

## Purpose

`XrdMgmOfsFile.hh` declares the EOS MGM implementation of the XRootD `XrdSfsFile` interface. It is the file-handle object used by the MGM for file opens, metadata-only proc command reads, close/stat/truncate/sync handling, page-read support, redirection scheduling, copy-on-write support, and per-open state such as identity, opaque CGI parameters, namespace file id, encryption key, and proc command result streaming.

## Important APIs, Types, and Functions

- `XrdMgmOfsFile` derives from `XrdSfsFile` and `eos::common::LogId`.
- `open(...)`, `close()`, `sync()`, `stat()`, `truncate()`, `read(offset,buff,len)`, and `pgRead(...)` are the main supported XRootD file operations.
- `write(...)`, async read/write, `pgWrite(...)`, async page I/O, and mmap are explicitly unsupported or no-op, which reflects that ordinary EOS data I/O is redirected to FSTs rather than served by the MGM.
- `handleHardlinkDelete()` and `create_cow()` are static helpers for hard-link deletion and copy-on-write clone behavior. `cowUpdate`, `cowDelete`, and `cowUnlink` define the supported clone modes.
- `targetParams` plus `setProxyFwEntrypoint()` model scheduled target host/port/http-port plus proxy/firewall redirection suffixes.
- Test-harness-visible helpers include `IsRainRetryWithExclusion()`, `GetTriedrcErrno()`, `RedirectTpcAccess()`, `LogSchedulingInfo()`, `GetExcludedFsids()`, `GetClientApplicationName()`, `GetPosixOpenFlags()`, and `GetXrdAccessOperation()`.

## Control Flow

The header exposes the intended file-control flow. Construction initializes the per-handle `VirtualIdentity` to `Nobody`. External XRootD open calls delegate to the overload that can also accept a precomputed `VirtualIdentity`; implementation code is expected to parse CGI opaque values, map identity, perform authorization, consult namespace metadata, and either return errors, proc-command data, or redirection details. Normal file data reads are not MGM-served except for proc command output, so `read(offset,buff,len)` is reserved for streaming command results while real files are usually redirected at open.

Unsupported write and async methods call `Emsg()` with `EOPNOTSUPP`, keeping the MGM file object a control-plane endpoint rather than a data-plane endpoint. The private scheduling helpers imply open-time logic that can exclude prior failed fsids, interpret `triedrc`, redirect third-party-copy access, and select proxy/firewall entrypoints.

## State and Persistence Behavior

The class stores transient per-open state: `oh`, `fileName`, `openOpaque`, `mFid`, `mProcCmd`, `fmd`, `vid`, `mEosKey`, `mEosObfuscate`, and `mIsZeroSize`. It does not itself persist metadata in the declaration, but its implementation is expected to mutate or read namespace state through `IFileMD`, `IContainerMD`, copy-on-write helpers, and close/truncate/stat code. `openOpaque` ownership and `mProcCmd` lifetime are important resource-management details because the file object can survive between auth-plugin RPC calls until close.

## Dependencies and Integration Points

This header depends on EOS identity mapping, logging, proc command interfaces, XRootD `XrdOucErrInfo`, `XrdSfsInterface`, `XrdSecEntity`, and namespace metadata interfaces. It integrates with XRootD by overriding `XrdSfsFile`, with MGM scheduling/redirection code through target parameters and access-operation mapping, with proc commands through `IProcCommand`, and with namespace hard-link/COW behavior through `IFileMD` and `IContainerMD`.

## Risks and Edge Cases

- The MGM intentionally does not serve normal file writes, so callers must handle redirects or `EOPNOTSUPP`; any path that accidentally expects direct MGM writes will fail.
- `openOpaque` is a raw pointer, so construction, open failure, and destruction paths need strict ownership discipline.
- Retry parsing and fsid exclusion logic can influence data placement and must distinguish legitimate retry from client-side exclusion.
- TPC redirection, firewall entrypoints, proxy endpoints, and port validation are security-sensitive because they populate redirect responses.
- Copy-on-write and hard-link deletion helpers can mutate namespace topology and must be lock-safe in their implementation.

## Test Signals

Useful tests should cover open-mode to POSIX flag conversion, access-operation mapping, unsupported write/async/page-write errors, proc-command read offsets, redirection target validation, retry opaque parsing with and without `triedrc`, excluded fsid extraction, TPC redirection, COW update/delete/unlink behavior, close/stat/truncate side effects, and destructor cleanup of opaque/proc state.
