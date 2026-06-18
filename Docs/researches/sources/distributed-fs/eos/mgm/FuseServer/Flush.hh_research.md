<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Flush.hh

Purpose: Declares `FuseServer::Flush`, a mutex-protected map of currently flushing FUSE clients keyed by inode and client, with a fixed 60-second validity window.

Important APIs/types/functions: `cFlushWindow` is 60 seconds. Public methods are `beginFlush()`, `endFlush()`, `hasFlush()`, `validateFlush()`, `expireFlush()`, and `Print()`. Private `flush_info_t` stores the client string, expiry `timespec`, and reference count and provides `Add()`/`Remove()` helpers.

Control flow: The implementation uses `XrdSysMutex` inheritance and locks the whole map per operation. Entries are created with an expiry in the future, incremented on repeated begins, decremented on ends, and removed either when references reach zero or when the expiry passes.

State and persistence behavior: `flushmap` is process-local and nonpersistent. It is a coordination hint rather than a durable write journal; after MGM restart, flush awareness is lost and clients must recover through normal protocol behavior.

Dependencies and integration points: Includes `mgm/Namespace.hh`, timing/logging, `map`, and XRootD pthread mutex wrappers. It is exposed through `gFuseServer.Flushs()` and used by FUSE server flush handling, heartbeat maintenance, and file close/open conflict paths.

Risks: The API accepts raw `std::string client` by value and does not encode ownership semantics beyond string equality. `validateFlush()` is public but assumes callers understand it mutates state by expiring entries. Tests should verify fixed-window behavior with controlled time, reference counts, cleanup after last client, and that diagnostics do not require external locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.hh -->
