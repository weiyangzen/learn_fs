# sources/cloud-native/overlaybd/src/overlaybd/tar/whiteout.cpp

Purpose: OCI whiteout and directory helper logic for `UnTar` extraction.

Important APIs/types/functions: constants define `.wh.`, `.wh..wh.`, `.wh..wh..opq`, and the PAX xattr prefix string. `UnTar::mkdir_hier` ensures parent directory existence. `UnTar::remove_all` recursively removes filesystem entries while respecting paths already unpacked in the current tar. `UnTar::convert_whiteout` maps OCI whiteout entries to target removal operations.

Control flow: `mkdir_hier` strips trailing slash, returns success for existing directories, fails for existing non-directories, and otherwise calls Photon recursive mkdir. `convert_whiteout` splits filename into directory/base; opaque directory markers remove children of the target directory without removing the directory itself, while `.wh.<name>` removes the target file or directory and returns a consumed-whiteout signal. `remove_all` lstat's the path, unlinks files if not unpacked, recursively traverses directories, closes the iterator, and optionally removes the directory.

State and persistence: mutates the extraction target filesystem by deleting files/directories. Reads `unpackedPaths` from `UnTar` to avoid deleting objects already produced by the current archive stream.

Dependencies/integration: called from `UnTar::extract_file` before type dispatch. Depends on Photon `Path`, directory iteration, recursive mkdir, logging, and OCI layer whiteout naming rules.

Risks: recursive removal ignores return values from nested `remove_all` calls, so partial deletion failures can be lost. Opaque directory handling requires the directory to already exist. The code assumes `basename().substr(0, whiteoutPrefix.size())` is safe for short names, which is valid for `std::string` but still easy to misread.

Test signals: EROFS stress TC008 and TC009 exercise whiteout deletion and delete-then-recreate behavior; clean/incremental simple tests include `.wh.dir2` semantics.
