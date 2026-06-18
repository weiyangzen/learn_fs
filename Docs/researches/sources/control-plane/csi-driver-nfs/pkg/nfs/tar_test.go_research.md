# sources/control-plane/csi-driver-nfs/pkg/nfs/tar_test.go

Purpose: validates the tar/gzip helpers for archive compatibility, traversal safety, symlink handling, and timestamp preservation.

Important APIs and helpers: `TestPackUnpack`, `produce`, `assertUnpackedFilesEqual`, `generateFileSystem`, `TestUnpackZipSlip`, `TestPackSameDir`, `TestSymlinks`, and `TestTarUnpackPreservesTimestamps`.

Control flow: pack/unpack compatibility generates combinations of four alternating pack/unpack operations using either Go code or the system `tar` CLI, then hashes resulting directories with `dirhash`. Zip-slip builds a malicious tar header with `../` and expects `tar.ErrInsecurePath`. Same-dir verifies pack rejects an archive inside the source. Symlink tests pack and unpack absolute and relative symlinks. Timestamp tests set known file and directory mtimes, pack/unpack, then compare restored mtimes with tolerance.

State and persistence behavior: creates temporary source/output directories, archives, symlinks, and a large test file. The large-file generator repeatedly overwrites a 1 MiB file rather than appending to 100 MiB, so it still tests non-empty binary content without the comment's implied size.

Dependencies and integration points: depends on the local tar helpers, the host `tar` executable for compatibility cases, `golang.org/x/mod/sumdb/dirhash`, and filesystem timestamp behavior.

Risks: CLI compatibility tests depend on `tar` availability and platform behavior. Absolute symlink tests can fail on platforms that restrict symlink creation. Hash comparisons focus on content and names, not every metadata bit.

Test signals: strong security and interoperability signal for snapshot archive operations.
