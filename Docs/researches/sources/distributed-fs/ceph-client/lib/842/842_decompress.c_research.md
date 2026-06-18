<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_decompress.c -->
# sources/distributed-fs/ceph-client/lib/842/842_decompress.c

## Purpose
Implements software decompression for 842 streams. It reconstructs the original byte stream from template opcodes, literal fields, dictionary indexes, repeat/zero/short-data commands, and validates the trailing CRC.

## APIs, Types, and Functions
The exported API is `sw842_decompress(const u8 *in, unsigned int ilen, u8 *out, unsigned int *olen)`. Internal `struct sw842_param` tracks input bit cursor, compressed bytes remaining, output cursor, output start, and output bytes remaining. `decomp_ops` maps template opcodes to four decode actions. Core helpers are `next_bits()`, `do_data()`, `__do_index()`, `do_index()`, and `do_op()`.

## Control Flow, State, and Persistence
The decompressor reads 5-bit opcodes until `OP_END`. Normal opcodes dispatch through `decomp_ops`, copying literal 2/4/8-byte data from the bitstream or copying 2/4/8 bytes from a rolling output FIFO. Index resolution computes a candidate offset from the index and adjusts it into the current FIFO section so it refers to already-produced bytes. `OP_REPEAT` copies the previous 8 bytes `rep + 1` times, `OP_ZEROS` writes eight zero bytes, and `OP_SHORT_DATA` copies 1-7 literal bytes for software-generated non-8-byte inputs. After `OP_END`, it reads the 32-bit CRC and compares it with `crc32_be()` over reconstructed output. State is per-call except optional template counters.

## Dependencies and Integration
Depends on `842.h`, `842_debugfs.h`, unaligned big-endian accessors, CRC32, exported symbol support, and module init/exit. It is compiled by `lib/842/Makefile` under `CONFIG_842_DECOMPRESS`, which selects CRC32 from `lib/Kconfig`. It is the correctness counterpart for `sw842_compress()` and can also consume hardware-compressed streams that use the standard template set.

## Risks and Test Signals
Risks include malformed index offsets pointing before available output, `OP_REPEAT` before any prior block, short-data underflow if output space checks regress, bit-reading over compressed-buffer boundaries, CRC validation rejecting valid streams if endian handling changes, and stream padding being ignored after end. Test signals include round trips from the software compressor, hardware sample streams, all templates, invalid opcodes, out-of-range indexes, repeat-at-start rejection, small output buffers, truncated compressed input, corrupt CRC, and optional debugfs counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_decompress.c -->
