# sources/distributed-fs/ceph-client/drivers/net/ppp/bsd_comp.c

Purpose: Implements PPP BSD-Compress as a `struct compressor` for `CI_BSD_COMPRESS`. It adapts BSD/LZW-style dictionary compression to packetized PPP streams.

Important APIs, types, and functions: `struct bsd_db` stores hash sizing, code width, max code, sequence number, MRU, ratio counters, stats, dictionary, and optional decompression code lengths. `struct bsd_dict` stores hash and reverse-code data. Allocation/init/reset paths are `bsd_alloc()`, `bsd_comp_alloc()`, `bsd_decomp_alloc()`, `bsd_init()`, `bsd_reset()`, and `bsd_clear()`. Data paths are `bsd_compress()`, `bsd_incomp()`, and `bsd_decompress()`. Module init registers `ppp_bsd_compress` through `ppp_register_compressor()`.

Control flow: CCP negotiation validates a three-byte BSD-Compress option and dictionary bit size. TX emits address/control, `PPP_COMP`, a two-byte sequence, variable-width LZW codes, and optional CLEAR when the ratio check says the dictionary should reset. It returns zero when output is not smaller. RX checks sequence, decodes variable-width codes, handles the KwKwK case, updates dictionary/lens tables, accepts CLEAR only at packet end, and returns recoverable or fatal PPP decompression errors. Uncompressed packets in a compression session call `bsd_incomp()` to keep dictionaries synchronized.

State and persistence behavior: Dictionary contents, sequence number, code width, ratio/checkpoint counters, and stats persist per CCP session. They reset on CCP reset/close and are freed with vmalloc/slab cleanup. No state persists after module unload.

Dependencies and integration points: Depends on PPP comp/defs headers, endian-specific dictionary layout, vmalloc/slab allocation, and compressor registry symbols from `ppp_generic.c`. It can be autoloaded via `ppp-compress-CI_BSD_COMPRESS`.

Risks and test signals: High-risk areas are sequence synchronization, bit packing, dictionary clearing, hash invalidation, MRU overflow, and memory use for 15-bit dictionaries. The checked-out file contains duplicated assignment/source lines that should be caught by build/static checks. Test option validation, 9-15 bit dictionaries, compressible/incompressible packets, no-output `bsd_incomp()`, CLEAR handling, sequence mismatch, bad code fatal errors, KwKwK decoding, output-too-large fallback, and pppd interop.
