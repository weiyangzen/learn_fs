# sources/distributed-fs/ceph-client/drivers/net/ppp/ppp_deflate.c

Purpose: Adapts kernel zlib to the PPP CCP compressor API for RFC 1979 Deflate and the older draft Deflate option.

Important APIs, types, and functions: `struct ppp_deflate_state` stores sequence number, negotiated window size, unit, MRU, debug flag, zlib stream, and stats. Allocation/init/reset/free functions are `z_comp_alloc()`, `z_decomp_alloc()`, `z_comp_init()`, `z_decomp_init()`, `z_comp_reset()`, `z_decomp_reset()`, `z_comp_free()`, and `z_decomp_free()`. Data paths are `z_compress()`, `z_decompress()`, and `z_incomp()`. Module init registers `ppp_deflate` and `ppp_deflate_draft`.

Control flow: CCP options are validated for option type, length, Deflate method, sequence checking, and window size. TX writes PPP_COMP plus sequence, compresses from the protocol field using `Z_PACKET_FLUSH`, increments sequence, and returns zero if the compressed frame is not smaller. RX validates sequence, inflates with raw Deflate history, reconstructs the PPP protocol field, probes for MRU overflow, updates stats, and returns recoverable or fatal decompression errors. Uncompressed packets feed `z_incomp()` to maintain inflate history.

State and persistence behavior: zlib stream history, sequence number, and stats persist per CCP direction until reset/close. Workspaces are vmalloc-backed and freed with the compression state. No durable state exists.

Dependencies and integration points: Depends on `linux/zlib.h`, PPP comp/defs headers, unaligned helpers, vmalloc/slab, and `ppp_generic.c` compressor registration. Kconfig selects zlib inflate/deflate. Module aliases support both Deflate protocol option numbers.

Risks and test signals: Synchronization relies on exact sequence and history updates. Buffer sizing must handle compressed output, PPP header reconstruction, one-byte PFC, and overflow probing. Test valid/invalid options, both option IDs, min/max window sizes, sequence mismatch, incompressible packets, output larger than input, reset, MRU overflow, PFC/non-PFC frames, registration unwind, and pppd interop.
