# sources/cloud-native/overlaybd/src/overlaybd/tar/libtar.cpp

Purpose: implementation of `UnTar` extraction into a Photon filesystem, including permissions, xattrs, regular file data, hardlinks, symlinks, directories, special nodes, and turboOCI metadata-only mapping.

Important APIs/types/functions: `UnTar::set_file_perms`, `dump_tar_headers`, `extract_all`, `extract_file`, `extract_regfile_meta_only`, `extract_regfile`, `extract_hardlink`, `extract_symlink`, `extract_dir`, and `extract_block_char_fifo`.

Control flow: `extract_all` loops through `read_header`, normalizes names, skips root, dispatches to `extract_file`, and applies deferred directory mtimes after all entries. `extract_file` ensures parent directories, converts OCI whiteouts, handles overwrite removal, dispatches by tar type, applies permissions/xattrs/time, defers directory mtime, and tracks unpacked paths. `dump_tar_headers` writes file headers and skips regular file payloads. Regular extraction streams payload blocks from the source tar into an output file while respecting tar block padding. Meta-only extraction creates sparse file extents, reads fiemap data, and writes remote mappings to the base LSMT file instead of copying payload bytes.

State and persistence: extraction mutates the target Photon filesystem. `unpackedPaths` prevents whiteout/removal logic from deleting entries already created by the current tar stream. `dirs` stores directory mtime values for delayed restoration. Meta-only mode persists file extents through `LSMT::RemoteMapping` ioctl calls into `fs_base_file`.

Dependencies/integration: depends on `TarCore` parsing, Photon FS and xattr APIs, Photon fiemap, LSMT remote mapping ioctls, POSIX ownership/time/mode semantics, and whiteout helpers in `whiteout.cpp`.

Risks: exact ownership and device-node restoration depends on privileges and `TAR_CHECK_EUID`. Xattr failures are selectively ignored only for unsupported or invalid user namespace cases. Hardlink targets are trusted after path normalization. Meta-only mapping relies on fiemap, fallocate, and the overloaded `header.devmajor` offset when replaying tar-index streams.

Test signals: tar integration tests cover full untar, metadata-only replay equivalence, gzip stream tar metadata, and generated tar header adaptor behavior; EROFS tests reuse `dump_tar_headers` for image equivalence.
