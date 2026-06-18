# sources/control-plane/csi-driver-nfs/pkg/nfs/tar.go

Purpose: implements Go-native tar/gzip pack and unpack helpers used by snapshot creation and restore when the driver is not configured to shell out to `tar`.

Important APIs and functions: `TarPack`, `tarVisitFileToPack`, `TarUnpack`, `tarUnpackFile`, `tarWriteFile`, and `closeAndWrapErr`.

Control flow: `TarPack` normalizes source and destination paths, rejects destinations under the source directory, creates the archive and optional gzip writer, walks the source tree, writes tar headers for files/directories/symlinks, and copies regular file contents. `TarUnpack` normalizes and creates the destination, resolves destination symlinks, opens optional gzip input, iterates tar headers, rejects zip-slip paths via `filepath.Rel`, checks existing ancestor symlinks to prevent writes outside the destination, creates directories, preserves symlinks as symlinks, removes existing symlinks before regular writes, writes files with mode permissions, verifies regular-file byte counts, and restores file and directory timestamps.

State and persistence behavior: creates archive files during pack and writes directories, files, symlinks, modes, and timestamps during unpack. It does not persist metadata outside filesystem content.

Dependencies and integration points: depends on Go archive/tar, gzip, filesystem, sorting, and error joining APIs. Controller snapshot code calls `TarPack` and `TarUnpack` for snapshot archives unless configured to use the external `tar` command.

Risks: `TarPack` uses `strings.HasPrefix(filepath.Dir(dstPath), srcDirPath)` which can reject prefix-collision paths such as `/tmp/src2` when source is `/tmp/src`; this is conservative but broad. `TarUnpack` preserves absolute symlink targets, which is archive-faithful but can create links pointing outside the destination. It does not apply ownership from tar headers.

Test signals: `tar_test.go` covers code/CLI interoperability, zip-slip rejection, same-directory packing rejection, symlink preservation, and timestamp restoration.
