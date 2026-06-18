# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw.h

## Purpose
`icp_qat_hw.h` defines common QAT hardware algorithm enums, capability masks, and descriptor setup structures for authentication, cipher, and compression services.

## Important APIs, Types, And Functions
Key enums include AE/QAT IDs, auth algorithms/modes, slice masks, capability masks, cipher algorithms/modes/direction/convert flags, and compression direction/delayed-match/algo/depth/file-type. Important structures include `icp_qat_hw_auth_config`, `icp_qat_hw_auth_setup`, `icp_qat_hw_auth_sha512`, `icp_qat_hw_auth_algo_blk`, `icp_qat_hw_cipher_config`, `icp_qat_hw_ucs_cipher_config`, `icp_qat_hw_cipher_algo_blk`, and `icp_qat_hw_compression_config`. Macros build auth, auth counter, cipher, and compression config words and define key/block/state sizes.

## Control Flow
The header is declarative. `qat_algs.c` fills auth and cipher blocks using `ICP_QAT_HW_AUTH_CONFIG_BUILD()` and `ICP_QAT_HW_CIPHER_CONFIG_BUILD()`. Compression context builders use the compression config builder. Hardware capability masks gate algorithm registration and feature paths such as AES v2.

## State And Persistence Behavior
No state is owned here. The structures are embedded in DMA content descriptors that persist for a crypto transform or compression context. Capability masks reflect hardware/firmware state discovered during device initialization.

## Dependencies And Integration Points
It includes `linux/bits.h` and is included by common firmware and algorithm files. It bridges Linux Crypto API algorithm choices to QAT hardware slice configuration words.

## Risks
Descriptor field constants must match hardware. Duplicate AES-XTS key size macros appear in the file, which is harmless if identical but a maintenance smell. SHA3 algorithm encoding splits across normal and high bits in the auth config builder, so adding auth algorithms requires care. Compression algo mask is only one bit while enum includes zstd value, so generation-specific headers may be needed for newer formats.

## Test Signals
Crypto and compression selftests validate config words indirectly. Capability-based registration tests should confirm algorithms are exposed only when hardware supports the required slices/features.
