# sources/distributed-fs/ceph-client/lib/xz/xz_dec_stream.c

## Purpose
Implements `.xz` container decoding: stream header/footer validation, block header parsing, filter-chain setup, block size accounting, CRC/check handling, Index validation, and the public `xz_dec_*` API.

## APIs and control flow
Public APIs are `xz_dec_init`, `xz_dec_reset`, `xz_dec_run`, and `xz_dec_end`. `struct xz_dec` tracks the main sequence, VLI parser, CRC, check type, mode, block metadata/hash, index metadata/hash, temp buffer, LZMA2 decoder, and optional BCJ decoder. `dec_main` moves through Stream Header, Block Start/Header/Uncompress/Padding/Check, Index/Padding/CRC32, and Stream Footer. Block headers validate CRC, flags, optional sizes, optional BCJ, required LZMA2 filter ID/properties, and padding. Index records are hashed and compared with observed block hashes.

## State, dependencies, and integration
Decoder state persists across multi-call invocations. `allow_buf_error` implements the two-no-progress rule for `XZ_BUF_ERROR`; single-call mode resets and rolls back positions on failure. Dependencies include `xz_private.h`, `xz_stream.h`, LZMA2, optional BCJ, CRC32, and allocation helpers. `xz_dec_syms.c` exports the APIs.

## Risks and test signals
Risks include accepting malformed VLIs, bad CRCs, unsupported checks/filters, bad padding, size mismatches, and index/footer inconsistencies. Tests need valid streams with CRC32/no check, multiple blocks, optional sizes, BCJ chains, unsupported options, corrupt containers, truncation, and small incremental buffers across every sequence transition.
