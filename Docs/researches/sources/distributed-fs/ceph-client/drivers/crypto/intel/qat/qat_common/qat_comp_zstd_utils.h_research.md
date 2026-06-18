# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.h

## Purpose
`qat_comp_zstd_utils.h` declares the LZ4S-to-zstd sequence conversion helper used by QAT zstd compression support.

## Important APIs, Types, And Functions
It defines `QAT_ZSTD_LIT_COPY_LEN` as 8 and declares `qat_alg_dec_lz4s(ZSTD_Sequence *out_seqs, size_t out_seqs_capacity, unsigned char *lz4s_buff, unsigned int lz4s_buff_size, unsigned char *literals, unsigned int *lit_len)`.

## Control Flow
The header has no executable flow. Callers allocate sequence and literal buffers, pass a firmware LZ4S output buffer and capacity, then use the returned sequence count and literal length with kernel zstd APIs.

## State And Persistence Behavior
No state is owned here. All output is caller-owned scratch memory for a single compression request or stream operation.

## Dependencies And Integration Points
It includes `linux/zstd_lib.h` for `ZSTD_Sequence` and is included by `qat_comp_algs.c`. It is specific to the zstd facade backed by QAT LZ4S.

## Risks
The API assumes buffers are large enough for fixed-width literal copying and the advertised sequence capacity. Callers must treat negative returns as errors and avoid using partially written sequence data.

## Test Signals
Compile coverage validates zstd type availability. Runtime zstd compression tests through QAT LZ4S validate the declared helper contract.
