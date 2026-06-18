## sources/distributed-fs/eos/mgm/ofs/fsctl/Checksum.cc

Purpose: fsctl handler that returns a file checksum for FUSE clients or other MGM fsctl callers.

Important APIs and types: `XrdMgmOfs::Checksum`, `eos::Resolver::retrieveFileIdentifier`, `IFileMD`, `LayoutId`, `appendChecksumOnStringAsHex`, `RWMutexReadLock`, and access-mode/stall/redirect macros.

Control flow: marks read-master access, applies stall/redirect, increments `Fuse-Checksum`, detects `mgm.option=fuse` to use the layout-specific checksum length, takes the namespace read lock, resolves path as fid when possible or as normal file path otherwise, appends checksum bytes as hex into the response string, catches metadata exceptions into `retc`, and returns `checksum: <hex> retc=<code>` as `SFS_DATA`.

State and persistence behavior: read-only except stats and potential prefetch/cache effects from metadata service access.

Dependencies and integration points: supports fid-addressed checksum lookups and FUSE-readable shortened checksum output. Uses SHA256 length as default output width.

Risks: no explicit `_access` check is performed in this handler; it relies on trusted fsctl context, access-mode macros, and routing/auth wrappers. `mgm.option` parsing is strict string equality with `fuse`. Empty checksum with retc 0 is possible for metadata without checksum bytes.

Test signals: path lookup, fid lookup, missing file retc, FUSE layout-length output, default SHA256-length output, response format, and read-master redirect behavior.
