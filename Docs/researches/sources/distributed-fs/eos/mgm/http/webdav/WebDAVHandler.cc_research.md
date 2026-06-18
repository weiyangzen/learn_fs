## sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.cc

Purpose: dispatches WebDAV extension methods and implements MKCOL, MOVE, and COPY mutations against EOS MGM.

Important APIs/types/functions: `Matches` recognizes PROPFIND, PROPPATCH, MKCOL, COPY, MOVE, LOCK, UNLOCK. `HandleRequest` optionally routes to another MGM, records stats, creates response builders, and calls `BuildResponse`. `MkCol` calls `gOFS->mkdir`. `Move` parses/decodes Destination, applies OwnCloud remapping, calls `gOFS->rename`, and handles overwrite by deleting destination through `/proc/user`. `Copy` calls `/proc/user` `mgm.cmd=file&mgm.subcmd=copy`, with optional forced overwrite.

Control flow: all WebDAV requests add EOS app metadata, check federation/routing with `gOFS->ShouldRoute`, then switch by parsed method. Error mapping distinguishes `SFS_ERROR`, `SFS_REDIRECT`, `SFS_STALL`, and errno values such as `EEXIST`, `ENOENT`, `EPERM`, `ENOSPC`. Successful MKCOL returns 201 with `OC-FileId`; successful MOVE/COPY generally return 201 or 204 for overwrite.

State and persistence: MKCOL creates directories; MOVE renames/removes existing destinations; COPY creates files through proc command. PROPFIND/PROPPATCH/LOCK/UNLOCK behavior is delegated to response objects, some of which are dummy.

Dependencies and integration points: integrates `HttpServer`, `PropFindResponse`, `PropPatchResponse`, `LockResponse`, `gOFS`, MGM stats, `OwnCloud`, `ProcCommand`, `XrdSecEntity`, and common HTTP responses.

Risks and test signals: several error branches call `HttpServer::HttpError(..., response->BAD_REQUEST)` while `response` is null; enum access through null pointer compiles but is unsafe style and should be reviewed. Destination header handling uses 1024-byte decode buffers and skips decoding longer destinations. Copy command concatenates URL parameters without obvious escaping. Tests should cover routing redirects, missing body/path/destination, overwrite true/false, remote.php remapping, long/encoded destinations, permission errors, stalls, redirects, and proc-command injection-sensitive characters.
