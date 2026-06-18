# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp_defs.h

## Purpose
`icp_qat_hw_51_comp_defs.h` defines generation 5.1 compression/decompression CSR fields, masks, enum values, and defaults. It covers newer zstd, dictionary, DMM, CNV, ASB, buffer-memory, and internal control features.

## Important APIs, Types, And Functions
Compression definitions include SOM, skip-hash-read, bypass compression, DMM algorithm, token fusion, BMS, SCB reset, zstd frame generation, CNV disable, ASB disable, internal decoder/CAM controls, HBS, ABD, LLLBD, search depth, format, min-match, hash behavior, byte-skip, and LZ4 checksum. Decompression definitions include discard data, BMS, zstd frame generation, internal decoder/CAM controls, HBS, format, and LZ4 checksum.

## Control Flow
The file is constant-only. Its values are used by `icp_qat_hw_51_comp.h` builders and device-specific context construction.

## State And Persistence Behavior
No runtime state exists. The constants represent generation 5.1 hardware descriptor semantics.

## Dependencies And Integration Points
It includes `linux/bits.h` for `GENMASK()` and is included by the generation 5.1 builder header. It integrates with QAT 6xxx hardware-data code and compression algorithm registration gated by extended capabilities.

## Risks
Several fields are marked internal-only by name but are still exposed as definitions; callers must avoid enabling unsupported modes. `ICP_QAT_HW_COMP_51_SEARCH_DEPTH_LEVEL_9` and `LEVEL_10` share the same value, which may be intentional aliasing or a documentation hazard. Format defaults differ from classic deflate-oriented defaults.

## Test Signals
Hardware context dumps should match expected 5.1 default and zstd/LZ4 configurations. Functional tests should include zstd frame-generation behavior, CNV/ASB overflow paths, and decompression discard/format controls where supported.
