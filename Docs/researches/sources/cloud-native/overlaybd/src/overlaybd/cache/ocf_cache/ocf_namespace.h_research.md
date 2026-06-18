<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h

## Purpose
Declares the abstract namespace service used by OCF cache to map individual source files into one cache-core logical address space.

## Important APIs, Types, And Functions
`OcfNamespace` exposes `init`, `locate_file`, `block_size`, and nested `NsInfo { blk_idx, file_size }`. Factories declare filesystem-backed and RocksDB-backed namespace implementations.

## Control Flow
Consumers initialize the namespace once, then call `locate_file` per opened source path to get its base block index and file size.

## State And Persistence
The base class stores only configured block size. Persistence is implementation-specific; the filesystem implementation writes checked namespace files.

## Dependencies And Integration Points
Extends Photon `Object` and uses Photon `IFile`, `estring`, and callbacks. Integrated by `ocf_cache.cpp`.

## Risks And Test Signals
The RocksDB factory is declared here but not implemented in this subset. `NsInfo` size and checksum are part of the persisted format, so ABI changes affect compatibility. Source size reviewed: 46 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h -->
