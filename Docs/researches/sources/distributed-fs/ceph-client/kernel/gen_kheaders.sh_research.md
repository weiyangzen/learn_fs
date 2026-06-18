# sources/distributed-fs/ceph-client/kernel/gen_kheaders.sh

## Purpose
`gen_kheaders.sh` builds the compressed kernel header archive used by `CONFIG_IKHEADERS`. It copies selected source-tree and object-tree headers into a temporary directory, strips non-SPDX block comments, emits make dependencies, and produces a reproducible tar.xz archive.

## Important APIs, types, and functions
The script inputs are `tarfile`, `srclist`, `objlist`, and `timestamp`; environment dependencies include `srctree`, `TAR`, and `XZ`. It creates a dependency file named after the tarball, uses `sed` to normalize source paths and dependency lines, pipes file lists through tar extraction into `tmpdir`, uses `find -print0` plus parallel `xargs perl -pi` for comment stripping, and invokes tar with owner/group/sort/mode/mtime normalization.

## Control flow
The script writes the make dependency fragment first, recreates a `.tmp_dir` beside the output archive, copies source-list files relative to `srctree`, copies object-list files from the current object tree, strips C block comments except SPDX text, then creates the final xz-compressed archive with deterministic metadata. Temporary content is removed at the end.

## State and persistence
Persistent outputs are the requested tarball and its sidecar dependency file. Temporary state is confined to `${dir}/.tmp_dir` and `${tmpdir}.contents.txt`, both removed on the normal path. Because `set -e` is active, failures may leave partial temporary directories for inspection or cleanup by the build.

## Dependencies and integration points
This script is invoked by the kernel build for in-kernel headers. It depends on GNU-ish tar features, xz integration through tar `-I`, Perl, xargs with null-delimited input, and build-system-provided file lists. The dependency file integrates the archive into make's incremental rebuild logic while intentionally excluding `include/generated/autoconf.h` from the object dependency list.

## Risks and test signals
Risks include unescaped paths in dependency output, comment stripping changing headers unexpectedly, non-GNU tar incompatibility, stale temp directories after interrupted builds, and dependence on `srctree` being set. Test signals include reproducible archive hashes with a fixed timestamp, successful extraction of source and generated headers, dependency rebuilds when listed headers change, SPDX comments preserved, and builds with paths containing unusual characters.
