# sources/compression/xz/src/xzdec/xzdec.c

Purpose: implements the tiny single-threaded `xzdec`/`lzmadec` command that only decompresses to stdout and never deletes input files.

Important functions: `main()`, `parse_options()`, `uncompress()`, `my_errorf()`, `help()`, `version()`, and optional `sandbox_enter()`. `TOOL_FORMAT` and decoder choice switch between `.xz` stream decoding and `.lzma` alone decoding using `LZMADEC`.

Control flow: `main()` initializes program name, locale, optional sandbox prerequisites, parses options, sets binary mode on DOS-like systems, and reuses one `lzma_stream` across all input files. Each file is opened, optionally enters a strict sandbox for the last file, then `uncompress()` streams BUFSIZ chunks through `lzma_code()` and writes BUFSIZ output chunks to stdout. `.xz` uses `LZMA_CONCATENATED` and `LZMA_FINISH` at EOF; `.lzma` manually rejects trailing garbage after `LZMA_STREAM_END`.

State and persistence: process-local `display_errors` is decremented by `-q` and affects diagnostics and final `tuklib_exit()`. The reused `lzma_stream` preserves allocations between files but is reset by decoder initialization. No output files are created; stdout is the only data sink.

Dependencies and integration: depends on liblzma, tuklib program-name/nonprint/exit helpers, bundled getopt, optional Capsicum, OpenBSD `pledge()`, and Linux Landlock. Test scripts use this binary as an independent decoder oracle when built.

Risks: all decoding exits immediately on first read, write, allocation, or data error. On native Windows broken pipe can appear as `EINVAL` and suppresses an error message. The strict sandbox is only entered for the final named file so earlier files can still be opened.

Test signals: `test_compress.sh` compares `xzdec` decompression output against original generated inputs when `xzdec` exists. `test_files.sh` feeds good, bad, and unsupported `.xz` files to `xzdec`, with special handling for unsupported checks.
