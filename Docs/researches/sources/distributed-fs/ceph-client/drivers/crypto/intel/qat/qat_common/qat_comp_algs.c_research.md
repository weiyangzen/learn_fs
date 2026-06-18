# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_algs.c

## Purpose
`qat_comp_algs.c` implements QAT async compression algorithms for the Linux acomp API. It registers deflate, native zstd when supported, and a zstd facade backed by QAT LZ4S plus software zstd sequence emission on capable hardware. It maps SGLs, builds compression firmware requests, handles overflow/CNV status, performs fallback, and manages shared zstd scratch streams.

## Important APIs, Types, And Functions
Key types are `qat_zstd_scratch`, `qat_compression_ctx`, `qat_compression_req`, and `qat_callback_params`. Important functions include `qat_zstd_alloc_scratch()`, `qat_zstd_free_scratch()`, `qat_alg_send_dc_message()`, `qat_comp_generic_callback()`, `qat_comp_alg_callback()`, `qat_comp_alg_init_tfm()`, `qat_comp_alg_compress_decompress()`, `qat_comp_alg_zstd_decompress()`, `qat_comp_lz4s_zstd_callback()`, `qat_comp_alg_lz4s_zstd_compress()`, fallback helpers, and `qat_comp_algs_register()/unregister()`.

## Control Flow
Transform init gets a compression instance for the requested algorithm and builds firmware request context templates. Deflate requests call the common compress/decompress path directly. That path validates source/destination and adjusted lengths, adds a device overflow buffer for compression, converts SGLs to QAT buffer lists with skip parameters, copies the template, fills source/destination/length/opaque fields, and submits through the DC ring. Generic completion decodes status, errors, consumed/produced counters, maps overflow to `-E2BIG`, rejects unsupported verified compression, checks actual output length against caller buffer, sets `areq->dlen`, calls an optional algorithm-specific callback, frees buffer lists, completes the acomp request, and drains backlog.

For zstd native decompression, the input frame header is inspected; large windows or content sizes fall back to software zstd. For LZ4S-backed zstd compression, size limits choose hardware or software fallback. The callback reads LZ4S output, decodes it into zstd sequences/literals using `qat_alg_dec_lz4s()`, and calls `zstd_compress_sequences_and_literals()`.

## State And Persistence Behavior
Per-transform context persists the QAT compression template context, instance pointer, optional fallback acomp, and optional post-processing callback. Per-request state persists firmware request bytes, mapped buffer lists, direction, actual output length, and async request pointer. `qat_zstd_streams` owns a pool of scratch contexts with large buffers and zstd CCtx workspaces.

## Dependencies And Integration Points
The file depends on QAT compression instances/context builders, common firmware comp request helpers, transport/backlog, buffer-list conversion, Linux acomp API, scatterwalk copy helpers, kernel zstd APIs, and device capability bits for extended zstd/LZ4S support.

## Risks
The LZ4S-to-zstd bridge has large scratch buffers and sequence limits; overflow must be handled carefully. Native zstd decompression reads only the first source SG page for the frame header, so fragmented short headers are a risk. Compression uses an overflow buffer beyond caller output to detect actual overflow; failure to clear/check it can leak stale data or misreport. Registration has three separate active-device counters that must unwind according to capability bits.

## Test Signals
Acomp selftests should cover deflate compress/decompress, zstd native paths, LZ4S-backed zstd paths, software fallback thresholds, multi-SG input/output, output overflow, verified compression unsupported status, plain/uncompressed output flag, invalid zstd headers, and repeated register/unregister with capability combinations.
