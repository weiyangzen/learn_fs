# sources/distributed-fs/ceph-client/lib/zstd/common/bitstream.h

Purpose: Implements inline forward bitstream writing and reverse bitstream reading used by zstd entropy coders. Streams are LIFO: bits written first are read last.

Important APIs/types:
- `BIT_CStream_t` with bit container, bit position, and output pointers.
- `BIT_DStream_t` with bit container, consumed count, current pointer, start, and safe limit.
- `BIT_DStream_status` reports unfinished, end-of-buffer, completed, or overflow.
- Writer functions: `BIT_initCStream`, `BIT_addBits`, `BIT_addBitsFast`, `BIT_flushBits`, `BIT_flushBitsFast`, `BIT_closeCStream`.
- Reader functions: `BIT_initDStream`, `BIT_lookBits`, `BIT_lookBitsFast`, `BIT_readBits`, `BIT_readBitsFast`, `BIT_skipBits`, `BIT_reloadDStream`, `BIT_reloadDStreamFast`, `BIT_endOfDStream`.

Control flow:
- Writers accumulate bits into a machine-word container, flush full bytes to memory, and append a one-bit end mark on close.
- Readers initialize from the end of the byte buffer, locate the end mark in the last byte, then consume bits backward. Reload functions move the pointer toward the start while preserving safe reads near the buffer boundary.
- Safe reload detects overflow and end-of-buffer; fast reload assumes enough distance from the start.

State and persistence:
- State lives in caller-owned stream structs. No global state.
- Read/write pointers define the valid buffer region and must remain stable during operations.

Dependencies and integration:
- Includes `mem.h`, `compiler.h`, `debug.h`, `error_private.h`, and `bits.h`.
- Used by FSE and HUF compression/decompression paths.

Risks:
- Unsafe variants require clean values, nonzero bit counts, and valid buffer margins.
- `BIT_initDStream()` requires exact compressed bitstream size and a nonzero last byte end marker; malformed inputs return zstd errors.
- Pointer and shift arithmetic are performance-critical and easy to break on 32-bit vs 64-bit differences.

Test signals:
- Round-trip bitstream encode/decode on 32-bit and 64-bit builds.
- Boundary tests for 1-byte through word-sized streams, missing end mark, dst too small, overflow, and exact completion.
- Fuzz entropy streams consumed by FSE/HUF.
