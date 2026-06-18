# sources/cloud-native/soci-snapshotter/metadata/util_test.go

Purpose: shared behavioral test suite for metadata Readers. It builds synthetic tar/ztoc fixtures and asserts Reader traversal, attributes, link behavior, xattrs, and open-file metadata across compression modes and path prefixes.

Important APIs/types/functions: `readerFactory` and `testableReader` abstract the implementation under test. `testReader` defines test cases for files, directories, hardlinks, path cleanup/device types, and allowed prefixes. Check helpers include `numOfNodes`, `sameNodes`, `linkName`, `hasNumLink`, `hasDirChildren`, `hasChardev`, `hasBlockdev`, `hasFifo`, `hasFile`, `hasMode`, `hasOwner`, `hasModTime`, `hasXattrs`, and `lookup`. `newCalledTelemetry` verifies telemetry hook invocation.

Control flow: for each fixture, prefix, and gzip compression level, tests build a ztoc reader, construct the metadata reader with telemetry, optionally dump the node tree, run all checks, and assert telemetry was called. `lookup` recursively resolves paths through `GetChild` from the root.

State and persistence: generated tar/gzip/ztoc fixtures and metadata reader state are temporary per test. Check functions only read through the Reader interface.

Dependencies/integration points: uses project `util/testutil` tar-entry builders, `ztoc.BuildZtocReader`, Go gzip levels, and the metadata Reader interface. This suite anchors contract behavior for any Reader implementation.

Risks: extensive cross-product of prefixes and compression levels can be expensive. `ForeachChild` order is ignored by using a map. `hasModTime` allows equality through before/after checks. Tests assume hardlink targets appear before hardlinks so the reader can resolve them.

Test signals: strong functional coverage for regular files, directories, nested paths, owners, modes, modtimes, xattrs, hardlinks sharing node IDs, symlinks, directory link counts, char/block devices, FIFOs, path normalization, and telemetry.
