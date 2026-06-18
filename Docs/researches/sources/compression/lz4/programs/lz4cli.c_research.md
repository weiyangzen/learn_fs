# sources/compression/lz4/programs/lz4cli.c

Purpose: user-facing `lz4` CLI entry point, including `lz4cat`, `unlz4`, and `lz4c` behavior selected by executable name.

Important APIs/functions: `main()` parses options and dispatches. Helpers cover usage text, executable-name matching, numeric suffix parsing, long-option argument handling, operation auto-detection, and environment defaults (`LZ4_NBWORKERS`, `LZ4_CLEVEL`). It calls `LZ4IO_*` for compression/decompression/listing and `BMK_*` for benchmarks.

Control flow: create default preferences, apply symlink mode defaults, scan long and aggregated short options, collect files, expand recursive inputs when supported, validate console safety, infer output filenames, normalize test/list/benchmark modes, set notification level, then run compression, decompression, legacy compression, listing, or benchmarking.

State and persistence: parser state is mostly local; static display level and legacy-mode flag affect behavior. It may overwrite outputs, write stdout, read stdin, expand directories, and request source removal via prefs.

Dependencies/integration: integrates `platform.h`, `util.h`, `lz4conf.h`, `bench.h`, `lz4io.h`, `lz4hc.h`, and `lz4.h`. It is the bridge from command syntax to `lz4io.c`.

Risks: complex compatibility parser; integer parsing can overflow; output-name inference is suffix-sensitive; console checks vary by platform; `--rm` enables destructive filesystem effects after backend success.

Test signals: option-parser, basic, multiple, legacy, dictionary, sparse, skippable, content-size, huge-file, list, symlink, benchmark, and memory tests in `tests/Makefile`.
