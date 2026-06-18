# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.h

## Purpose
Declares shared EROFS wrapper constants, cache structures, Photon-file helpers, and erofs-utils virtual file operation adapters.

## Important APIs and Types
Defines sector constants, alignment macros, `EROFS_ROOT_XATTR_SZ`, `EROFS_UNIMPLEMENTED`, `EROFS_UNIMPLEMENTED_FUNC`, `liberofs_inmem_sector`, `ErofsCache`, and `liberofs_file`. Declares read/write helpers and target/source vfops.

## Control Flow
The declarations establish two directions: target operations read/write the generated EROFS image through an `ErofsCache`, while source operations read/lseek the incoming tar stream.

## State and Persistence
`ErofsCache` state includes the backing file pointer, capacity, cached sectors, and dirty sector set. This state controls when generated image sectors hit the backing file.

## Dependencies and Integration Points
Depends on erofs-utils `erofs/io.h`, Photon filesystem abstractions, and STL maps/sets. Included by `erofs_common.cpp`, `erofs_fs.cpp`, and `liberofs.cpp`.

## Risks
Macros such as `erofs_min(a, b)` lack protective parentheses around the whole expression. Cache ownership is raw-pointer based and relies on explicit flush/free paths in implementation code.

## Test Signals
Compile checks against erofs-utils headers, sector alignment unit tests, and cache flush/eviction tests are appropriate.
