# sources/compression/xz/src/liblzma/api/lzma/bcj.h

Purpose: declares Branch/Call/Jump conversion filter IDs, shared BCJ options, and raw in-place helper functions for selected architectures.

Important APIs/types/functions: defines `LZMA_FILTER_X86`, `POWERPC`, `IA64`, `ARM`, `ARMTHUMB`, `SPARC`, `ARM64`, and `RISCV`; declares `lzma_options_bcj { uint32_t start_offset; }`; exports raw `lzma_bcj_arm64_encode/decode`, `lzma_bcj_riscv_encode/decode`, and `lzma_bcj_x86_encode/decode`.

Control flow: as normal filters, BCJ stages are configured through `lzma_filter` chains and implemented elsewhere. The raw helpers transform a caller-supplied buffer in place and return the processed byte count, leaving an architecture-specific tail unprocessed if needed.

State and persistence: no persistent state in the header. `start_offset` lets separately processed executable sections produce consistent relative-address conversions.

Dependencies/integration: included by `lzma.h` after `filter.h` and `vli.h`; the xz CLI maps command-line filter names to these IDs. `tests/test_filter_flags.c`, BCJ exact-size tests, and CLI argument parsing use these constants.

Risks: BCJ filters do not currently support `LZMA_SYNC_FLUSH`; using them in flush-sensitive streams returns options errors. Decoding requires matching non-default `start_offset`. Raw helpers are special-purpose and require alignment constraints for ARM64 and RISC-V offsets.

Test signals: `tests/test_filter_flags.c`, `tests/test_bcj_exact_size.c`, filter string tests, and command-line option parsing around `--x86`, `--arm64`, and similar filters.
