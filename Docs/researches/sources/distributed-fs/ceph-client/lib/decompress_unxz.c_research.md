# sources/distributed-fs/ceph-client/lib/decompress_unxz.c

## Purpose
Provides the XZ wrapper used for kernel, initramfs, and initrd decompression, including support for constrained preboot environments.

## APIs, Types, and Functions
The main API is `unxz()`, with preboot `__decompress()` under `XZ_PREBOOT`. In static builds the file maps kernel allocation names to decompressor allocation helpers and supplies simple memory helpers such as `memeq`, `memzero`, and `memmove` when needed. It uses `xz_dec_init()`, `xz_dec_run()`, and `xz_dec_end()` from the in-kernel XZ decoder.

## Control Flow
`unxz()` initializes an XZ decoder, sets up input/output buffers for single-call or streaming mode, and loops calling `xz_dec_run()`. If input is exhausted, it reads more through `fill` or reports buffer error. If output fills or the decoder returns a final/error status, it flushes pending bytes when a `flush` callback is present. On completion it records consumed input, ends the decoder, maps `XZ_STREAM_END` to success, and maps format/options/data/buffer/memory errors to caller-visible error strings.

## State and Persistence
All decoder state is per-call in the `xz_dec` instance and `xz_buf`. Temporary input/output buffers may be allocated and freed within the call. No global state is mutated.

## Dependencies and Integration Points
Depends on the in-kernel XZ decoder, CRC32 support in preboot configuration, decompressor memory helpers, and the generic decompressor ABI. It integrates with `decompress.c` for XZ magic and architecture boot code that may decompress in place.

## Risks and Test Signals
Risks include in-place decompression safety margins, unsupported XZ options, streaming buffer starvation, short flush writes, and preboot helper mismatches. Test signals include XZ-compressed kernel boot tests, BCJ/LZMA2 option coverage, corrupt/truncated streams, single-call and callback modes, and comparison with known XZ output.
