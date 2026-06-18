# sources/compression/xz/tests/create_compress_files.c

Purpose: generates deterministic input files used by compression/decompression round-trip tests, reducing source package size by avoiding checked-in large fixtures.

Important functions and macros: `maybe_create_test()` conditionally creates one named fixture; `file_exists()`, `file_create()`, and `file_finish()` provide portable file handling; `write_abc()`, `write_random()`, and `write_text()` generate the three data profiles. `main()` creates all files or only the requested `compress_generated_<name>`.

Control flow: the generator skips existing files, supports one optional filename argument, writes to `compress_generated_abc`, `compress_generated_random`, and `compress_generated_text`, and exits nonzero on I/O failure. `write_random()` uses a fixed linear congruential sequence for reproducibility. `write_text()` emits one original lorem paragraph followed by deterministic randomized word sequences.

State and persistence: writes generated fixture files in the current tests build directory. There is no persistent internal state beyond deterministic seeds.

Dependencies and integration: used by `test_compress.sh` when a `compress_generated_*` test is requested. Depends only on `sysdefs.h` and stdio, making it portable across the supported test environments.

Risks: `maybe_create_test()` only compares `argv[1]`, so it intentionally supports one selected fixture at a time. Existing fixture files are trusted and not regenerated unless cleaned, which can leave stale/corrupt files after interrupted runs.

Test signals: downstream shell tests compress/decompress each generated profile with multiple presets and filters, so this generator's correctness is observed through round-trip comparisons.
