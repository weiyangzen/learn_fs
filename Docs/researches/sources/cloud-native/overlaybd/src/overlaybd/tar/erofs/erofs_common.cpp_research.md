# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/erofs_common.cpp

## Purpose
Adapts Photon `IFile` objects to erofs-utils virtual file operations and provides a small sector cache that handles unaligned 512-byte reads/writes required by EROFS image construction and reading.

## Important APIs and Types
Implements `ErofsCache::write_sector`, `read_sector`, `flush`, `erofs_read_photon_file`, `erofs_write_photon_file`, target vfops (`pread`, `pwrite`, `fsync`, `fallocate`, `ftruncate`, `read`, `lseek`), and source vfops (`read`, `lseek`, with other operations unimplemented).

## Control Flow
Unaligned reads/writes round the requested span to sector boundaries, use a scratch sector for partial first/last sectors, and process aligned middle sectors through the cache. The cache evicts the lowest-address cached sector when at capacity, flushing dirty data before reuse. Target vfops call the helper functions; source vfops expose sequential read and lseek from the tar source file.

## State and Persistence
`ErofsCache` stores sector buffers in a map plus dirty address set and writes dirty sectors to the underlying Photon file on eviction or flush. This is the main persistence bridge for generated EROFS image bytes.

## Dependencies and Integration Points
Depends on `erofs_common.h`, Photon logging, erofs-utils `erofs_vfile` operations, and Photon file APIs. Used by both `liberofs.cpp` image creation and `erofs_fs.cpp` image reading.

## Risks
The eviction policy is address-ordered rather than LRU. The destructor does not flush or free cache entries by itself, so callers must call `flush`. `erofs_target_fallocate` checks `if (ret)` inside a loop even successful writes return nonzero, which can return early incorrectly for chunks larger than 4096.

## Test Signals
Tests should cover unaligned partial-sector writes/reads, dirty eviction, flush persistence, target pwrite/pread round trips, and source read/lseek behavior.
