# sources/compression/zstd/lib/common/bitstream.h

Purpose: inline bitstream encoder/decoder used by FSE/HUF entropy code. Encoders write forward into a buffer but produce a stream decoded backward as a LIFO bit stack.

Important types/functions: `BIT_CStream_t`, `BIT_DStream_t`, `BIT_DStream_status`, `BIT_initCStream`, `BIT_addBits`, `BIT_addBitsFast`, `BIT_flushBits`, `BIT_flushBitsFast`, `BIT_closeCStream`, `BIT_initDStream`, `BIT_lookBits`, `BIT_readBits`, `BIT_readBitsFast`, `BIT_skipBits`, `BIT_reloadDStream`, `BIT_reloadDStreamFast`, and `BIT_endOfDStream`.

Control flow: compression initializes a local bit container and buffer pointers, accumulates bit fields, flushes whole bytes to memory, appends a one-bit end marker on close, and reports zero if the destination overflowed. Decompression initializes from an exact source size, validates the end marker from the last byte, loads a machine-word container from the end of the stream, reads bits from high positions while advancing `bitsConsumed`, and reloads backward through the buffer with status values distinguishing unfinished, end-of-buffer, completed, and overflow.

State and persistence: stream state lives in the `BIT_*Stream_t` structs: container, bit position/consumption, and buffer pointers. No globals.

Dependencies/integration: `mem.h` for endian unaligned access, `compiler.h` for inline/branch attributes, `debug.h`, `error_private.h`, and `bits.h`. Optional BMI2 intrinsics accelerate masking.

Risks: fast/unsafe functions require clean values, nonzero bit counts, and valid buffer space. Many look/read functions rely on caller ensuring enough bits are loaded. Incorrect source size or missing end marker is detected as corruption, but misuse can become undefined behavior through shifts or out-of-range pointer arithmetic.

Test signals: round-trip bit sequences with varied bit widths, small source sizes below container width, overflow destination buffers, malformed end marker, 32-bit and 64-bit builds, BMI2 and non-BMI2 paths, and exact `BIT_endOfDStream` completion.
