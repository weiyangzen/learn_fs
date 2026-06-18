<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend.go

Purpose: implements the platform-neutral file operation backend for mkdir, mkfile, symlink, rm, copy, user ownership mapping, wildcard handling, timestamps, and docker-compatible archive unpack.

Important APIs and types: helpers `timestampToTime`, `mkdir`, `symlink`, `mkfile`, `rm`, `rmPath`, `docopy`, `cleanPath`; public `NewFileOpBackend`, `ReadUserCallback`, and `Backend` methods `Mkdir`, `Mkfile`, `Symlink`, `Rm`, `Copy`, `readUserWrapper`.

Control flow: backend methods validate mount types, locally mount snapshot mountables, read owner info from optional user/group mounts, then call helpers. Helpers resolve paths with `fs.RootPath`, trim host-root prefixes from `os.PathError`, apply chown/utime, support wildcard removal/copy, optionally create destination paths, and attempt archive unpack before normal copy when requested.

State and persistence: mutates mounted snapshot filesystems; no separate persistent metadata. Mutable/immutable ref lifecycle is handled by `RefManager`, not this file. Dependencies include continuity fs, BuildKit snapshot/fileoptypes/pb, fsutil copy, user identity mapping, and OS filesystem calls.

Integration points: file op solver invokes this backend to apply LLB file actions to cache refs.

Risks and test signals: path escaping prevention relies on `fs.RootPath`; wildcard and archive behavior can be subtle; xattr errors are logged and ignored during copy. `backend_test.go` covers `rmPath` allow-not-found behavior, while Windows-specific copy behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend.go -->
