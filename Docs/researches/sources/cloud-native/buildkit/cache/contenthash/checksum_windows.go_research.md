# sources/cloud-native/buildkit/cache/contenthash/checksum_windows.go

Purpose: Windows-specific contenthash scan support, including backup privilege toggling for accessing protected files.

Important APIs/types/functions: package globals for `SeBackupPrivilege`, `(*cacheContext).walk`, `enableProcessPrivileges`, and `disableProcessPrivileges`.

Control flow: `walk` calls `winio.EnableProcessPrivileges` before `filepath.Walk` and defers disabling. The public `cacheManager.Checksum` also enables/disables privileges around the checksum operation, so Windows scans get elevated read capability during filesystem traversal.

State and persistence behavior: no contenthash metadata is persisted here; it only affects scan permissions.

Dependencies and integration points: uses Microsoft `go-winio` for privilege management and standard filepath walking. Built only on Windows.

Risks: process-wide privilege changes must be balanced to avoid leaking elevated capability. Errors from privilege changes are not surfaced in the declarations seen here, so access failures may appear later during walk/stat.

Test signals: Windows compile/test lanes cover it; several checksum tests skip paths requiring unsupported bind-mount behavior.
