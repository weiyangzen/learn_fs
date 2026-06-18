# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.h

## Purpose
`packer.h` defines the compressed block on-disk overlay, packer bin/packer runtime structures, default bin count, and public packer API.

## Important APIs, Types, and Functions
`struct compressed_block_header` stores a packed version and fragment sizes. `struct compressed_block` overlays the header and data area. `VDO_COMPRESSED_BLOCK_DATA_SIZE` and `VDO_MAX_COMPRESSED_FRAGMENT_SIZE` define compressed-fragment limits. `struct packer_bin` stores sorted-list links, used slots, free space, and incoming data VIO pointers. `struct packer` stores thread ID, bin count/list, canceled bin, admin state, flush generation, and statistics. The header declares compressed-fragment lookup, packer lifecycle, statistics, packing/flush/drain/resume, lock-holder removal, generation increment, and dump functions.

## Control Flow
The header sets the data contracts used by compression paths: compressed reads decode fragments from `compressed_block`, write paths submit VIOs to the packer, administrative paths flush/drain/resume it, and diagnostics query stats/dumps.

## State and Persistence Behavior
`compressed_block_header` and `compressed_block` describe durable block layout. `packer_bin` and `packer` describe volatile batching state. `flush_generation` and `admin_state` gate which VIOs can remain in the packer.

## Dependencies and Integration Points
It includes Linux lists plus VDO admin-state, constants, encodings, statistics, types, and wait-queue definitions. It is used by data VIO compression/write paths and compressed read decode paths.

## Risks and Edge Cases
The compressed block layout is packed and versioned; changing header size or slot count affects disk compatibility. Flexible arrays require correct allocation through `vdo_allocate_extended()`. Bin incoming slots are bounded by `VDO_MAX_COMPRESSION_SLOTS`.

## Test Signals
Compile-time layout checks, compressed block decode vectors, packer lifecycle tests, and admin drain/flush behavior validate the header contract.
