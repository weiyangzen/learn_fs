<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agp_backend.h -->
# sources/distributed-fs/ceph-client/include/linux/agp_backend.h

## Purpose
`agp_backend.h` declares backend AGPGART structures and APIs for managing AGP bridges, aperture information, and AGP memory bindings.

## Important APIs, types, and functions
Types include `enum chipset_type`, `struct agp_version`, `struct agp_kern_info`, and `struct agp_memory`. Important globals are `agp_bridge`, `agp_bridges`, and `agp_find_bridge`. APIs include memory allocate/free, info copy, bind/unbind, enable, backend acquire, and backend release. Memory type constants distinguish normal and user memory variants.

## Control flow
Drivers acquire a bridge for a PCI device, query bridge/aperture info, allocate AGP memory, bind it at an aperture page offset, then unbind/free and release the bridge. `agp_enable()` programs mode.

## State and persistence behavior
AGP bridge state and bridge lists are global. `struct agp_memory` records pages, scatterlist DMA mappings, binding status, flush status, key, type, and aperture start.

## Dependencies and integration points
The header integrates PCI, VM operations, pages, scatterlists, and AGPGART frontend interfaces.

## Risks and test signals
Risks include aperture offset mistakes, bind/unbind ordering bugs, DMA mapping leaks, stale global bridge pointers, and user memory type confusion. Test signals include AGP bridge probe, allocation/bind/unbind cycles, mmap/aperture tests, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/agp_backend.h -->
