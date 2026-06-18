<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_compress.c -->
# sources/distributed-fs/ceph-client/lib/842/842_compress.c

## Purpose
Implements the software compressor for IBM/NX 842 format. It accepts arbitrary input, emits the 842 template stream plus a big-endian CRC32, and exports `sw842_compress()` for kernel compression users that select `CONFIG_842_COMPRESS`.

## APIs, Types, and Functions
The public API is `sw842_compress(const u8 *in, unsigned int ilen, u8 *out, unsigned int *olen, void *wmem)`. The caller supplies scratch memory that must fit `SW842_MEM_COMPRESS`. Internal state lives in `struct sw842_param`: input/output cursors, remaining lengths, bit cursor, cached 8/4/2-byte input fragments, candidate indexes, and three rolling hash tables. `comp_ops` maps each normal template to four actions and the encoded opcode. Important helpers are `add_bits()`, `add_template()`, `add_repeat_template()`, `add_short_data_template()`, `add_zeros_template()`, `add_end_template()`, `check_template()`, `get_next_data()`, `update_hashtables()`, and `process_next()`.

## Control Flow, State, and Persistence
`sw842_compress()` initializes rolling dictionaries for 8-, 4-, and 2-byte matches, rejects non-8-byte input in `strict` mode, then processes full 8-byte groups. It coalesces repeated 8-byte blocks into repeat templates, emits a zeros template for all-zero blocks, otherwise searches `comp_ops` from best to fallback template and writes either literal data fields or dictionary indexes. After each block it updates the ring-indexed hash tables from current input. Remaining 1-7 bytes use the software-only short-data template unless strict mode rejected the buffer. The stream ends with `OP_END`, CRC32, and zero padding to an 8-byte output length. Persistent state is limited to module parameters and optional debugfs counters; compression dictionaries are per-call scratch state.

## Dependencies and Integration
Depends on `842.h` for opcodes and format constants, `842_debugfs.h` for optional counters, `linux/hashtable.h`, unaligned big-endian accessors, CRC32, module parameters, and exported symbol plumbing. It is built by `lib/842/Makefile` when `CONFIG_842_COMPRESS` is set and is selected from `lib/Kconfig`; zswap, crypto/compression wrappers, or architecture NX fallback paths can call the exported function.

## Risks and Test Signals
Risks include bitstream boundary errors in `add_bits()`, output-length accounting near `ENOSPC`, dictionary-index mismatches between compressor and decompressor, non-hardware-compatible short-data templates, CRC endian mismatch, and template-table corruption. The `strict` module parameter changes accepted input shape. Test signals should include round trips through `sw842_decompress()`, buffers of 0-15 bytes, non-8-byte inputs with strict on/off, repeated and zero blocks, every normal template, output buffers that are exactly full or one byte short, CRC mismatch injection, and hardware 842 compatibility checks for strict-mode streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_compress.c -->
