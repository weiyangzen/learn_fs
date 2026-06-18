# sources/compression/zstd/programs/zstdcli.c

## Purpose

This is the zstd command-line entry point. It parses executable aliases and CLI options, initializes preferences, dispatches to compression, decompression, test, list, benchmark, and dictionary-training subsystems, and handles process-level cleanup.

## Important APIs, Types, and Functions

Key helpers include `checkLibVersion`, `exeNameMatch`, `usage`, `usageAdvanced`, `badUsage`, numeric parsers for unsigned/int/size suffixes, `longCommandWArg`, dictionary parameter parsers, adaptive/compression parameter parsers, `setMaxCompression`, `printVersion`, `printDefaultCParams`, `printActualCParams`, `init_cLevel`, `init_nbWorkers`, and `main`. `zstd_operation_mode` selects compress, decompress, test, bench, train, or list. Global tuning state tracks overlap and LDM parameters.

## Control Flow, State, and Persistence

`main()` creates `FIO_prefs_t`, `FIO_ctx_t`, and filename tables, maps program names such as `zstdmt`, `unzstd`, `zstdcat`, `gzip`, `xz`, and `lz4` variants to default modes, then walks arguments. Long and short options update local variables and preference objects; `--filelist` inputs are loaded and merged; recursive paths are expanded; symlinks are ignored unless forced. It then branches to list, benchmark, dictionary training, compression, or decompression/test. Before dispatch it validates console safety, output mode, compression levels, dictionary/patch conflicts, progress policy, and memory limits. `_end` frees contexts/tables, handles optional pause, finishes tracing, and returns the operation result.

## Dependencies and Integration Points

It integrates with `fileio.h`, `fileio_common.h`, `fileio_asyncio.h`, `benchzstd.h`, `dibio.h`, `zstdcli_trace.h`, zstd library APIs, and utility filesystem helpers. Environment variables `ZSTD_CLEVEL` and `ZSTD_NBTHREADS` influence defaults.

## Risks and Test Signals

The parser has many interacting modes, optional build features, and alias-specific defaults. Risks include malformed numeric suffix handling, stdout/stderr console policy regressions, incorrect filelist merge semantics, multi-thread default differences, format-specific behavior, and conflicting dictionary/patch options. Tests should cover help/version, bad arguments, memory suffixes, output-dir validation, gzip compatibility, pass-through, recursive/filelist input, async toggles, benchmark/train/list modes, and cleanup on early returns.
