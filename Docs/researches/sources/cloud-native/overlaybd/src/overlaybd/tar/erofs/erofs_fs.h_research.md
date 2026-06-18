# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_fs.h

## Purpose
Declares the Photon read-only filesystem, file, and directory wrappers for EROFS images.

## Important APIs and Types
`ErofsFileSystem` implements `photon::fs::IFileSystem`; `ErofsFile` extends `VirtualReadOnlyFile` and `IFileXAttr`; `ErofsDir` implements `photon::fs::DIR`. Free functions `erofs_check_fs` and `erofs_create_fs` expose image detection and filesystem creation.

## Control Flow
Consumers call `erofs_check_fs` on an image file, then `erofs_create_fs`, then use standard Photon filesystem methods such as `open`, `stat`, and `opendir`. Returned files support `fstat`, `fiemap`, `pread`, and read-only xattr access.

## State and Persistence
Opaque private structs hold erofs superblock/file inode state in implementation. The wrapper reads from the supplied image file and does not mutate it.

## Dependencies and Integration Points
Depends on Photon filesystem, virtual-file, fiemap, logging, and STL vector headers. Used by tar/image code that wants to mount or inspect generated EROFS layers.

## Risks
The interface advertises the full `IFileSystem` surface, but most mutating methods are implemented as unsupported. Callers need to handle null returns and negative `EROFS_UNIMPLEMENTED` values.

## Test Signals
Compile-time interface conformance, opening real EROFS images, directory traversal, xattr reads, and unsupported-operation assertions are relevant.
