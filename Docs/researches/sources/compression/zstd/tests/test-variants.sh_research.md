# sources/compression/zstd/tests/test-variants.sh

Purpose: This shell test verifies that specialized zstd binary variants include and exclude the intended feature symbols and still perform their supported compression/decompression roles.

Important APIs and functions: It defines paths to variant executables in `programs/`. Helpers include `println()`, `die()`, `symbol_present()`, `symbol_not_present()`, feature-specific symbol absence checks, `test_help()`/`test_no_help()`, `extras_not_present()`, `test_compress()`, `test_decompress()`, and `test_zstd()`.

Control flow: With `set -e -u -x`, the script fails on unset variables, failed commands, and echoes commands. It checks frugal/compress/decompress variants for missing dictionary, legacy, benchmark, and trace symbols; checks compress-only and decompress-only binaries for absent opposite-direction APIs; checks dictBuilder and nolegacy variants; verifies old legacy symbols are absent from the main binary; then runs small pipe-based compression/decompression tests and help-option expectations.

State and persistence: It creates no durable files except transient pipe data. It inspects binaries with `nm` and invokes zstd commands in pipelines.

Dependencies and integration points: Requires the variant binaries to already be built, plus `nm`, `grep`, a POSIX shell, and the main `zstd` binary for validation. It integrates with the zstd build matrix for variant targets.

Risks and test signals: `symbol_present()` treats an `nm` failure as text piped to `grep`, so missing binaries may produce less direct diagnostics. Symbol checks are platform/toolchain-sensitive because link-time optimization, stripping, or symbol visibility can change `nm` output. Success ends with "Success!"; any unexpected symbol/help support or failed pipe test exits nonzero.
