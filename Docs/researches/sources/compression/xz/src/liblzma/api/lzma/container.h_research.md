# sources/compression/xz/src/liblzma/api/lzma/container.h

Purpose: declares high-level container-format encoding and decoding APIs for `.xz`, legacy `.lzma`, `.lz`/lzip, MicroLZMA, presets, and multithreaded operation.

Important APIs/types/functions: defines preset macros `LZMA_PRESET_DEFAULT`, `LZMA_PRESET_LEVEL_MASK`, `LZMA_PRESET_EXTREME`; declares `lzma_mt` with threading, block size, timeout, preset/filter/check, and decoder memory-limit fields. Encoder APIs include easy memusage, easy encoder, easy buffer encoder, stream encoder, multithreaded stream encoder and memusage, `lzma_mt_block_size`, legacy alone encoder, stream buffer bound/encode, and MicroLZMA encoder. Decoder flags include `LZMA_TELL_NO_CHECK`, `LZMA_TELL_UNSUPPORTED_CHECK`, `LZMA_TELL_ANY_CHECK`, `LZMA_IGNORE_CHECK`, `LZMA_CONCATENATED`, and `LZMA_FAIL_FAST`; decoder APIs include stream, multithreaded stream, auto, alone, lzip, stream-buffer, and MicroLZMA decoders.

Control flow: high-level callers initialize `lzma_stream` through one of these functions, then use `lzma_code()` with the action set supported by that coder. Single-call APIs operate on `in/out` buffers and update position pointers only on success. Multithreaded encoders can split Blocks and accept barriers; threaded decoders parallelize only suitable multi-Block streams.

State and persistence: persistent state is held in `lzma_stream.internal`; `lzma_mt` is caller-owned configuration. Decoder memory limits may be adjusted via base APIs; buffer decoders can update a memlimit pointer on `LZMA_MEMLIMIT_ERROR`.

Dependencies/integration: central API used by xz CLI (`src/xz/coder.c`), tests, and downstream applications. Depends on base stream lifecycle, filters, checks, LZMA options, and hardware helpers for recommended memory choices.

Risks: decoder flags alter return-code semantics and integrity behavior. `LZMA_CONCATENATED` requires `LZMA_FINISH` to receive final stream end. Large `memlimit_threading` can permit huge buffering; `memlimit_stop` is the hard cap. MicroLZMA encoder has unusual single-call `lzma_code()` behavior and requires callers to check consumed/produced totals.

Test signals: CLI round trips, `tests/test_bcj_exact_size.c`, lzip and MicroLZMA tests, stream buffer tests, memory-limit tests, and threaded encoder/decoder builds.
