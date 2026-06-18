# sources/cloud-native/soci-snapshotter/idtools/idmap_test.go

Purpose: verifies core container-to-host UID/GID translation and overflow rejection for `IDMap`.

Important APIs and flow: `TestToHost` builds two UID mapping ranges and two GID mapping ranges, then checks boundary and interior mappings plus unmapped users returning `invalidUser` with an error. `TestToHostOverflow` constructs ranges near `uint32` overflow boundaries and asserts `ToHost` fails safely for both UID and GID overflow cases.

State and persistence: no filesystem state is used. The tests are pure in-memory mapping checks.

Dependencies and integration: uses OCI runtime `LinuxIDMapping` and `testify/assert`. It tests the arithmetic helpers indirectly through `ToHost`.

Risks and test signals: strong signal for range translation and overflow protection. It does not test `Unmarshal`, label loading, recursive chown, symlink handling, or preservation of special permission bits; those require filesystem or integration-level coverage.
