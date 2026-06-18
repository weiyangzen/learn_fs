# sources/cloud-native/soci-snapshotter/fs/reader/reader_test.go

Purpose: validates lazy file reads through `reader.file.ReadAt` across span sizes, offsets, and file sizes, and checks error behavior for missing file IDs.

Important APIs and flow: `TestFsReader` calls `testFileReadAt` and `testFailReader` using `metadata.NewTempDbStore`. `testFileReadAt` enumerates read size, inner offset, base offset, file size, span size, and optional tar prefix, builds a synthetic ztoc and metadata reader, opens the test file, reads through the returned `file`, and compares bytes. `testFailReader` finds an unused metadata ID, verifies `OpenFile` fails for it, then opens and reads a valid file successfully.

State and persistence: uses temporary metadata DB stores, memory span cache, and generated gzip/tar ztoc readers. No remote HTTP or FUSE mount is involved.

Dependencies and integration: exercises `ztoc.BuildZtocReader`, `spanmanager.New`, metadata stores, and the reader package together. The tar prefix cases protect name handling for paths with `./`.

Risks and test signals: good signal for offset arithmetic and EOF handling. Tests do not intentionally corrupt tar headers, attrs, xattrs, or span data, so `Verify` failure behavior is not strongly covered despite verification being enabled by default.
