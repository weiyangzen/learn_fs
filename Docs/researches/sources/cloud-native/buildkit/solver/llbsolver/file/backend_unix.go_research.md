<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go

Purpose: provides Unix-specific ownership mapping and copy behavior for the file backend.

Important APIs and types: `mapUserToChowner` and `platformCopy`.

Control flow: when no user is specified, the chowner preserves existing ownership, except nil ownership under an idmap maps root to host ids. When a user is specified, it copies the user and maps UID/GID to host ids if an identity mapping exists. `platformCopy` directly delegates to fsutil `copy.Copy`.

State and dependencies: no persistent state; returns callback functions used by copy/chown operations. Depends on BuildKit/user identity mapping and fsutil copy.

Integration points: compiled on non-Windows builds and used by backend mkdir/mkfile/symlink/copy operations.

Risks and test signals: idmap conversion errors fail file actions. The nil-user behavior is subtle because non-nil old ownership is assumed already mapped. No direct Unix-only test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_unix.go -->
