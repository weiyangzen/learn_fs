# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.cpp

## Purpose
Implements a read-only Photon filesystem over an EROFS image. It supports path lookup, file stat/read/fiemap/xattr operations, directory iteration, filesystem magic checks, and filesystem construction from an image file.

## Important APIs and Types
Implements `ErofsFileSystem`, `ErofsFile`, `ErofsDir`, internal `liberofs_nameidata`, `liberofs_dir_context`, `do_erofs_ilookup`, `do_erofs_readdir`, `erofs_check_fs`, and `erofs_create_fs`.

## Control Flow
`ErofsFileSystem` initializes erofs superblock state with target vfops. Path lookup walks components from root, reads directory blocks, compares dirents, and follows symlinks by recursively walking link targets. `ErofsFile::pread` maps file logical ranges with `erofs_map_blocks`, zero-fills holes/EOF, and reads mapped data with `erofs_read_one_data`. `opendir` collects dirents into a vector-backed `ErofsDir`.

## State and Persistence
The filesystem keeps an erofs superblock and a target `liberofs_file` with cache over the image. File objects keep a copied inode. No writes are exposed; most mutating filesystem methods return `-EROFS_UNIMPLEMENTED`.

## Dependencies and Integration Points
Depends on erofs-utils inode, dir, map, xattr, and superblock APIs, Photon filesystem/fiemap/virtual file interfaces, and shared adapters from `erofs_common`.

## Risks
Symlink following lacks an explicit recursion/depth limit. `fiemap` assumes caller-provided extent capacity is sufficient. Many filesystem operations are unimplemented, so consumers must treat it as read-only. `ErofsFileSystem` logs superblock read failure but still constructs an object.

## Test Signals
Signals include magic detection, stat/open/pread for regular files, hole zero-fill, directory iteration, xattr list/get, symlink path traversal, and negative tests for unsupported mutation APIs.
