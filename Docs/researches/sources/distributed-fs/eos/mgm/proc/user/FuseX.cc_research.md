# sources/distributed-fs/eos/mgm/proc/user/FuseX.cc

Purpose: implements `ProcCommand::FuseX()`, the newer eosxd metadata command for GET, LS, and GETCAP operations by path, inode, or child lookup.

Important APIs and types: consumes `mgm.inode`, `mgm.clock`, `mgm.path`, `mgm.child`, `mgm.op`, client ids, auth ids, and inline-response flags. It uses `Prefetcher`, `eosView`, directory and file metadata services, `fusex::md`, `gOFS->zMQ->gFuseServer.HandleMD`, `SymKey::Base64`, `XrdOucBuffer`, access macros, and timing/stat macros.

Control flow: path input is URL-decoded and resolved to an inode by trying file metadata then container metadata. Child lookup prefetches parent children and resolves a child file or container; for small directories it may return the parent listing instead of only the child entry. Operation flags set the `fusex::md` request type. If a client clock is supplied, the function attempts a metadata clock comparison and returns `EEXIST` when unchanged. It delegates metadata construction or capability generation to `HandleMD`, validates GETCAP client clock skew, and either returns raw result stream data or a base64 inline payload in `mError`.

State and persistence: read-only for metadata GET and LS. GETCAP may issue capability data through the fuse server layer. It updates timing and MGM stats.

Dependencies and integration: deeply integrated with eosxd protocol semantics, ZeroMQ fuse server handling, namespace services, prefetching, and the MGM error channel.

Risks: clock comparison code has a local `md_clock` shadow in the container branch, which can undermine the intended cache validation. Inline responses use the error channel with `EIDRM`, so client compatibility is sensitive. Child lookup has special small-directory behavior. Tests should cover path versus inode lookup, child lookup, unchanged clocks, inline payload size threshold, GETCAP clock skew, permission bounces, and ENOENT/non-ENOENT error mapping.
