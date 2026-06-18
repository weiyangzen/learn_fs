# sources/cloud-native/containers-storage/userns_test.go

Purpose: Linux unit tests for automatic user namespace ID mapping and passwd/group size inference.

Important APIs and control flow: `TestGetAutoUserNSMapping` table-tests `getAutoUserNSIDMappings` with normal contiguous ranges, insufficient UID/GID availability, used ranges, additional mappings, and discontinuous intervals. Expected maps verify that occupied host IDs and reserved container IDs are skipped while additional mappings are appended. `TestParseMountedFiles` writes temporary passwd and group files and checks `parseMountedFiles` output for normal users, passwd-only, group-only, empty files, invalid file contents, and nobody/nogroup handling.

State and persistence: uses temporary directories and files; no persistent storage. The tests avoid mounting and layer-store operations.

Dependencies and integration: uses `idtools.IDMap`, the package's `idSet` and `interval` helpers, and Go testing. Build tag limits it to Linux.

Risks: `reflect.DeepEqual` makes ordering part of the contract. The tests cover pure allocation logic but not `getAutoUserNS` end-to-end with store locks, image layers, or cleanup failures.

Test signals: strong signal for arithmetic correctness in range subtraction/zipping and for ignoring nobody/nogroup sentinel IDs when sizing user namespaces.
