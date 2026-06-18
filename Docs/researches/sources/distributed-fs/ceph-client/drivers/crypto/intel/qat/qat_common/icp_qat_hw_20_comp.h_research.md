# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp.h

## Purpose
`icp_qat_hw_20_comp.h` provides typed builders for generation 2.0 QAT compression and decompression CSR configuration words. It converts enum-valued compression settings into firmware/hardware config dwords.

## Important APIs, Types, And Functions
The file defines `icp_qat_hw_comp_20_config_csr_lower`, `icp_qat_hw_comp_20_config_csr_upper`, `icp_qat_hw_decomp_20_config_csr_lower`, and `icp_qat_hw_decomp_20_config_csr_upper`. Builder functions are `ICP_QAT_FW_COMP_20_BUILD_CONFIG_LOWER()`, `ICP_QAT_FW_COMP_20_BUILD_CONFIG_UPPER()`, `ICP_QAT_FW_DECOMP_20_BUILD_CONFIG_LOWER()`, and `ICP_QAT_FW_DECOMP_20_BUILD_CONFIG_UPPER()`.

## Control Flow
Each builder starts with zero, writes each configured enum field with `QAT_FIELD_SET()`, and returns `swab32(val32)`. Compression lower fields include format, search depth, extended delay match, history buffer size, literal buffer controls, min-match, hash behavior, byte skip, and ABD. Compression upper fields include SCB/RMB/SOM controls, hash read, unload, token fusion, buffer memory size, reset mask, lazy, and nice parameters. Decompression builders set speculative decoder, mini-CAM, history/buffer size, format, min-match, and LZ4 checksum options.

## State And Persistence Behavior
The file owns no state. Returned dwords are embedded in compression content descriptors and persist while that descriptor/template is active.

## Dependencies And Integration Points
It includes Linux byte-swap support, generation 2.0 compression definitions, and common firmware bit helpers. Device-specific compression context code calls these builders when preparing QAT 2.0/2.3 compression templates.

## Risks
The return value is byte-swapped, unlike generation 5.1 builders. Mixing generation builders or omitting the swap will misprogram hardware. Defaults live in the defs header; callers must initialize every struct field explicitly or risk zero-valued settings that may not equal intended defaults.

## Test Signals
Compression context dumps should show expected lower/upper dwords for deflate, LZ4S, and zstd-capable 2.3 paths. Functional deflate/LZ4S/zstd tests on QAT 2.0/2.3 hardware validate builder settings.
