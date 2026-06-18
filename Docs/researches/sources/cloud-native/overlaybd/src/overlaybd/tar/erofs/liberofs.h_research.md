# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.h

## Purpose
Declares the small public `LibErofs` wrapper for converting tar data into an EROFS-backed OverlayBD target.

## Important APIs and Types
`LibErofs(photon::fs::IFile *target, uint64_t blksize, bool import_tar_headers = false)` stores the output file, block size, and tar-header import mode. `extract_tar(photon::fs::IFile *source, bool meta_only, bool first_layer)` performs the conversion.

## Control Flow
Callers instantiate `LibErofs` with a writable target and then call `extract_tar` for each source tar stream, passing `first_layer` to select initial vs incremental EROFS construction.

## State and Persistence
The object stores the target file pointer, block size, and `ddtaridx` flag. Actual persistence is performed in `liberofs.cpp` through erofs-utils and LSMT remote mapping ioctls.

## Dependencies and Integration Points
Depends on Photon filesystem/fiemap and string view headers. Used by tar import code that wants EROFS layout generation.

## Risks
The class does not own or validate the target pointer. `meta_only` behavior is not visible in the declaration and is currently unused in the implementation.

## Test Signals
Construction with valid/invalid target files, first-layer and incremental extraction, and import_tar_headers mode should be covered.
