# sources/distributed-fs/eos/mgm/http/HttpHandler.cc

## Purpose
`HttpHandler.cc` implements the MGM-side plain HTTP protocol handler. It dispatches HTTP verbs, delegates REST URLs to `RestApiManager`, maps file and directory operations to EOS/XRootD namespace calls, and builds `PlainHttpResponse` objects or redirect/stall/error responses for clients.

## Important APIs, Types, and Functions
`HttpHandler::Matches()` accepts standard HTTP verbs. `HandleRequest()` decides REST versus plain HTTP, adds the `eos.app` tag, applies MGM routing via `gOFS->ShouldRoute()`, updates `MgmStats`, and invokes verb-specific methods. `Get()` handles access checks, symlink redirects, ETag conditions, directory index redirects, tape-offline rejection, SFS file open/read, and HEAD support through `isHEAD`. `Put()` handles OwnCloud chunking, partial PUT, ETag preconditions, booking/target size opaque parameters, mtime and `ArchiveMetadata`, SFS open/create retries, and redirect/error translation. `Delete()` drives `/proc/user` `mgm.cmd=rm`. `Options()` advertises WebDAV-capable verbs, while `Post()`, `Trace()`, `Connect()`, and `Patch()` return `501`.

## Control Flow
Requests enter through `HandleRequest()`. REST paths are routed directly to the registered REST handler with the current virtual identity. Plain requests first pass the EOS routing module; a route match returns a redirect without running verb logic. Otherwise the parsed method selects the handler branch. GET/HEAD perform access and stat before choosing directory, file, redirect, or error responses. PUT prepares an EOS opaque query, opens an SFS file, and usually returns `201 Created` or a redirect to the storage endpoint. DELETE validates existence, builds a proc command, and maps EOS return codes to HTTP status.

## State and Persistence Behavior
The handler itself is request-scoped and persists only `mHttpResponse`. Persistent effects are delegated to EOS: file reads use `gOFS->newFile()`, writes/open-create use SFS flags and opaque options, deletes invoke MGM proc commands, and stats/attrs/checksums come from the namespace. ETags and mtime headers reflect namespace metadata. OwnCloud chunk headers and atomic-upload options influence downstream persistence but are not stored in this class.

## Dependencies and Integration Points
The implementation depends on `gOFS`, `XrdMgmOfs`, `XrdSfsFile`, `XrdSecEntity`, `ProcCommand`, `MgmStats`, `HttpServer` response helpers, `OwnCloud` remapping/chunk helpers, EOS mode/timing utilities, and `RestApiManager`. It integrates with the MGM redirector, FST redirects, WebDAV advertisement, CTA archive metadata, and tape-aware namespace flags.

## Risks
Several logging lines check lowercase header keys but print mixed-case variants, which can insert empty map entries or log the wrong value. GET reads the whole file body into memory when no redirect occurs, which is risky for large files or proc-style files. The directory browsing path is intentionally disabled unless `sys.http.index` exists. The tape-offline guard returns `424 Failed Dependency` for files with backup and offline flags. PUT has nuanced OwnCloud and partial-upload behavior where opaque query composition and redirect CGI must remain exact.

## Test Signals
Tests should cover REST bypass, route redirects, all verb dispatch stats, GET/HEAD ETag preconditions, external symlink redirects, directory index attr redirects, tape-offline GET rejection, checksum digest on HEAD, GET SFS redirect/error/data/stall paths, PUT OwnCloud chunk and partial uploads, booking/target size query creation, archive metadata propagation, ENOENT create retry, DELETE file and recursive directory removal, and unimplemented verb status codes.
