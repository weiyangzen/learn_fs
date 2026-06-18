<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go

Purpose: provides Windows-specific ownership defaults and copy filtering for protected snapshot-root folders.

Important APIs and types: `mapUserToChowner` and `platformCopy`.

Control flow: if no SID is supplied, ownership defaults to `ContainerAdministratorSidString`; otherwise the supplied user is returned. `platformCopy` appends exclude patterns for `System Volume Information` and `WcSandboxState` only when copying from the mount root, then delegates to fsutil `copy.Copy`.

State and dependencies: no durable state. Depends on BuildKit Windows utilities and fsutil copy.

Integration points: compiled on Windows and used by file backend copy/chown paths for container snapshots.

Risks and test signals: excluding protected folders only at root avoids access-denied failures without hiding nested user files with the same names. `backend_windows_test.go` covers this root-only behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows.go -->
