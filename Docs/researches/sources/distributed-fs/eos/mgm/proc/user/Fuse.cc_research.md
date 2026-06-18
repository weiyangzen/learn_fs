# sources/distributed-fs/eos/mgm/proc/user/Fuse.cc

Purpose: implements the legacy FUSE directory-listing proc command `ProcCommand::Fuse()`. It returns a compact inode directory listing consumed by FUSE clients, with optional per-entry stat payloads.

Important APIs and types: uses `pOpaque` fields `mgm.path`, `mgm.statentries`, and `eos.encodepath`, path mapping macros, `XrdMgmOfsDirectory`, `gOFS->newDir`, `eosView->getFile`, `eosView->getContainer`, `FileId::FidToInode`, `Path`, `_stat`, and fast integer-to-hex conversion for struct stat fields.

Control flow: the handler maps and validates the path, opens the directory through the MGM OFS layer, initializes `mResultStream` with either `inodirlist` or `inodirlist_pathencode`, then loops through directory entries. Names are escaped, `.` and `..` are inserted at fixed positions, file metadata is tried first to derive a file inode, and container metadata is tried as a fallback. If requested, `_stat` is called and selected stat fields are appended in a compact brace-delimited hex format.

State and persistence: this command is read-only apart from MGM statistics and result stream state. It allocates a directory object with `gOFS->newDir` and deletes it after closing.

Dependencies and integration: sits on the legacy FUSE wire contract and the MGM namespace cache. It relies on exact output ordering and encoding conventions understood by clients.

Risks: response construction uses mutable string insertion offsets for dot entries and fixed stack buffers. Missing metadata yields zero or omitted inode data rather than a hard failure for ordinary entries. Tests should validate path encoding modes, statentries binary-compatible field order, dot/dotdot ordering, file and directory inode conversion, permission failures, and cleanup of directory handles on errors.
