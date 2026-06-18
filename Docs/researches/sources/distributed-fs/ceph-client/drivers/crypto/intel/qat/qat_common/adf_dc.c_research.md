# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.c

## Purpose
This file builds QAT compression/decompression request context templates shared by compression algorithms. It fills common firmware request headers, compression flags, CRC initialization, slice chaining IDs, and delegates generation-specific compression/decompression config blocks to `adf_dc_ops`.

## Important APIs, Types, And Functions
The public API is `qat_comp_build_ctx(struct adf_accel_dev *accel_dev, void *ctx, enum adf_dc_algo algo)`. It operates on two adjacent `struct icp_qat_fw_comp_req` templates: compression first, decompression second.

## Control Flow
The function clears the first template, initializes common request header flags for stateless compression with SGL pointers, calls `GET_DC_OPS(accel_dev)->build_comp_block()`, sets legacy Adler/CRC and request parameter flags including SOP/EOP/BFINAL/CNV recovery, sets current/next slice IDs, copies the compression template to the next slot, advances the template pointer, and calls `build_decomp_block()`.

## State And Persistence Behavior
The caller owns the context buffer. The initialized templates persist as transform or instance state in compression code outside this file. No global state is modified.

## Dependencies And Integration Points
It depends on QAT firmware compression request structures and generation-specific `adf_dc_ops` implementations from Gen2/Gen4/Gen6 hardware data. It is used by QAT compression algorithm setup.

## Risks
The buffer must be large enough for two templates. Unsupported algorithms return errors through generation ops. Header flag mismatches can make firmware reject requests or produce wrong compression output.

## Test Signals
Compression/decompression selftests for DEFLATE, ZSTD where supported, invalid algorithm rejection, CNV recovery behavior, and generation-specific config block verification validate this file.
