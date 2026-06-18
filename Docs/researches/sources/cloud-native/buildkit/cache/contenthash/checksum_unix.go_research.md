# sources/cloud-native/buildkit/cache/contenthash/checksum_unix.go

Purpose: Unix implementation of filesystem walking and process privilege hooks for contenthash.

Important APIs/types/functions: `(*cacheContext).walk`, `enableProcessPrivileges`, and `disableProcessPrivileges`.

Control flow: `walk` delegates to `filepath.Walk`. Privilege functions are no-ops on non-Windows.

State and persistence behavior: no state is stored here; it feeds `scanPath` in `checksum.go`.

Dependencies and integration points: built on `!windows`, imported by contenthash scan logic.

Risks: `filepath.Walk` order and error behavior affect deterministic scan insertion and error propagation. Unix privilege no-ops assume normal permissions are enough for mounted snapshots.

Test signals: contenthash tests on Unix exercise this path through all scan-based checksum operations.
