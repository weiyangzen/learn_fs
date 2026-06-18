# sources/distributed-fs/ceph-client/include/linux/zutil.h

## Purpose
`zutil.h` is an internal zlib compatibility/configuration header in the kernel tree. It provides shared typedefs, deflate block constants, match limits, preset dictionary flag definitions, zlib checksum callback typing, and an inline Adler-32 implementation for compression-library internals. It explicitly warns applications to include public `zlib.h` instead.

## Important APIs, Types, And Data
The header includes `linux/zlib.h`, `linux/string.h`, and `linux/kernel.h`. It defines shorthand integer aliases `uch`, `ush`, and `ulg`, block-type constants `STORED_BLOCK`, `STATIC_TREES`, and `DYN_TREES`, match length bounds `MIN_MATCH` and `MAX_MATCH`, zlib header flag `PRESET_DICT`, and default `OS_CODE` as Unix (`0x03`) unless already supplied.

`check_func` is a function pointer type for checksum callbacks with signature `uLong (*)(uLong check, const Byte *buf, uInt len)`. Adler-32 support defines `BASE`, `NMAX`, and loop-unrolling macros `DO1`, `DO2`, `DO4`, `DO8`, and `DO16`. The only inline function is `zlib_adler32(uLong adler, const Byte *buf, uInt len)`.

## Control Flow
`zlib_adler32()` initializes `s1` and `s2` from the incoming Adler value. If `buf` is `NULL`, it returns the Adler initial value `1L`. Otherwise it processes the buffer in chunks up to `NMAX` bytes to keep intermediate sums within 32-bit bounds, uses `DO16()` for 16-byte unrolled accumulation, handles the tail one byte at a time, reduces both sums modulo `BASE`, and returns `(s2 << 16) | s1`.

The block and match constants are not executed here; they are consumed by zlib deflate/inflate implementation code to classify stored/static/dynamic blocks, match lengths, and preset-dictionary headers.

## State And Persistence Behavior
The header has no persistent state and no hidden allocation. Adler state is passed in and returned by value, so callers can compute a checksum incrementally across multiple buffer reads. All other data is compile-time macro configuration.

## Dependencies And Integration Points
This file integrates with in-kernel zlib compression and decompression sources that need internal helpers beyond the public zlib API. It depends on public zlib scalar types `uLong`, `Byte`, and `uInt`. The checksum function pointer type allows deflate/inflate code to abstract checksum selection.

Because it is internal, its macros may be included by several translation units and can affect generated code through unrolled checksum macros and `OS_CODE`. External modules should avoid relying on it as a stable API.

## Risks
The checksum loop depends on `NMAX` being small enough to prevent overflow before modulo reduction. Changes to `BASE`, `NMAX`, or the unrolled macros can silently break Adler-32 compatibility. `zlib_adler32(NULL)` intentionally returns the initializer, so callers must not treat NULL as a no-op update preserving the incoming checksum.

Macro names such as `DO1` and short typedefs are generic and can collide if this internal header is included in broad scopes. Because this is internal API, external consumers risk breakage if they depend on these names.

## Test Signals
Checksum tests should compare `zlib_adler32()` against known Adler-32 vectors, including empty input, NULL initialization, one-byte updates, incremental multi-buffer updates, and buffers crossing `NMAX` boundaries. Build tests should compile deflate/inflate users with this header and public `linux/zlib.h` to catch type drift or macro conflicts.
