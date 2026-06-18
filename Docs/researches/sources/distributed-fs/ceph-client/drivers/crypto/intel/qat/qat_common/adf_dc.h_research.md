# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.h

## Purpose
This header defines QAT data-compression algorithm identifiers and declares the common compression context builder.

## Important APIs, Types, And Functions
`enum adf_dc_algo` names `QAT_DEFLATE`, `QAT_LZ4`, `QAT_LZ4S`, and `QAT_ZSTD`. The public function is `qat_comp_build_ctx(struct adf_accel_dev *accel_dev, void *ctx, enum adf_dc_algo algo)`.

## Control Flow
No executable flow exists. The enum selects algorithm-specific config in generation-specific DC ops.

## State And Persistence Behavior
No state is defined. Callers allocate and retain context buffers.

## Dependencies And Integration Points
It forward-declares `struct adf_accel_dev` and is used by hardware-data files and compression algorithm code.

## Risks
Enum additions require updates in every generation's `build_comp_block()` and `build_decomp_block()` implementation. Unsupported algorithms should return errors consistently.

## Test Signals
Build coverage and compression selftests for each advertised algorithm validate this header.
