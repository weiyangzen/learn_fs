# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp.h

## Purpose
`icp_qat_hw_51_comp.h` provides typed builders for generation 5.1 QAT compression and decompression CSR configuration words.

## Important APIs, Types, And Functions
The config structs are `icp_qat_hw_comp_51_config_csr_lower`, `icp_qat_hw_comp_51_config_csr_upper`, `icp_qat_hw_decomp_51_config_csr_lower`, and `icp_qat_hw_decomp_51_config_csr_upper`. Builder functions are `ICP_QAT_FW_COMP_51_BUILD_CONFIG_LOWER()`, `ICP_QAT_FW_COMP_51_BUILD_CONFIG_UPPER()`, `ICP_QAT_FW_DECOMP_51_BUILD_CONFIG_LOWER()`, and `ICP_QAT_FW_DECOMP_51_BUILD_CONFIG_UPPER()`.

## Control Flow
The builders pack selected enum fields into a zeroed `u32` using `QAT_FIELD_SET()` and return the value without byte-swapping. Compression lower packs ABD, LLLBD, search depth, min-match, and LZ4 checksum. Compression upper packs DMM algorithm, buffer memory size, and SCB reset behavior. Decompression lower currently packs LZ4 checksum, and decompression upper packs buffer memory size.

## State And Persistence Behavior
No state is owned here. Built values become part of generation 5.1 compression descriptors/templates.

## Dependencies And Integration Points
It includes common firmware helpers and generation 5.1 defs. Device-specific 6xxx hardware data uses these builders when preparing compression context words.

## Risks
Generation 5.1 fields differ significantly from generation 2.0 and are not byte-swapped. Some defined fields in the defs header are not exposed in these compact config structs, so new features may require builder expansion. Callers must initialize all struct fields.

## Test Signals
QAT 6xxx compression/decompression context build tests, CSR/config dumps, and async compression selftests validate packing. Cross-generation tests should confirm 5.1 builders are not used on 2.0 hardware.
