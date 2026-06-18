# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.c

## Purpose
`qat_comp_zstd_utils.c` translates QAT-produced LZ4S token streams into zstd sequence/literal arrays that can be passed to kernel zstd sequence compression. It is support code for the QAT LZ4S-backed zstd compression path.

## Important APIs, Types, And Functions
The public function is `qat_alg_dec_lz4s()`. Internal helper `emit_delimiter()` inserts explicit zstd block delimiters. Important constants define LZ4S token split (`ML_BITS`, `RUN_BITS`), masks, `LZ4S_MINMATCH`, and `QAT_ZSTD_BLOCK_MAX`.

## Control Flow
`qat_alg_dec_lz4s()` walks the LZ4S buffer byte by byte. For each token, it decodes literal length with extension bytes, copies literal bytes into the literal output buffer in fixed 8-byte chunks, then either emits a trailing literal-only sequence at end of input or reads a 16-bit offset and match length with extension bytes. Nonzero matches are converted into `ZSTD_Sequence` entries, with any accumulated historical literal length folded in. If the next sequence would exceed the zstd block maximum, it emits a delimiter first and resets block size. Zero-length matches defer literal length to the next sequence. Capacity checks return `-EOVERFLOW`.

## State And Persistence Behavior
The function owns no persistent state. It writes caller-provided sequence and literal buffers and updates `lit_len`. Local `hist_literal_len`, `block_decomp_size`, and sequence index track translation state for one stream.

## Dependencies And Integration Points
It depends on kernel zstd sequence types, unaligned little-endian reads, string copying, and debug logging. `qat_comp_algs.c` calls it from the LZ4S-zstd post-processing callback.

## Risks
The literal copy loop copies `QAT_ZSTD_LIT_COPY_LEN` bytes at a time and relies on caller scratch capacity including extra copy slack. The parser assumes valid LZ4S input from firmware; malformed input could overrun `ip` because extension-byte loops do not explicitly check `end_ip` before each read. Sequence delimiter capacity reserves one slot, so max sequence tests are important.

## Test Signals
Tests should cover empty input, literal-only streams, sequences with extended literal/match lengths, zero-length-match literal accumulation, block delimiter insertion at 128KB, capacity overflow, and round-trip zstd output compared with software zstd.
