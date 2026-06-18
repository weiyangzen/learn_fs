# sources/compression/xz/tests/test_scripts.sh

Purpose: shell tests for installed-style helper scripts `xzdiff` and `xzgrep`.

Important variables and flow: resolves `XZ`, `XZDIFF`, and `XZGREP` from an optional executable directory or build defaults, skips if any required executable is missing, and skips when decompression support is disabled. It prepends the xz binary directory to `PATH` so scripts find the local tool.

Control flow: `xzdiff` is run on two equivalent decompressed files and expected to exit 0, on differing files and expected to exit 1, and with a missing operand and expected to exit 2. `xzgrep` copies two fixtures to temporary names, runs combinations of patterns (`el`, `Hello`, `NOMATCH`) and options (``, `-l`, `-h`, `-H`), captures stdout/stderr and return values, then compares against `xzgrep_expected_output`.

State and persistence: creates `xzgrep_test_1.xz`, `xzgrep_test_2.xz`, and `xzgrep_test_output`; `Makefile.am clean-local` removes them.

Dependencies and integration: gated by `COND_SCRIPTS` in `Makefile.am`. Depends on fixture files, local scripts, local xz, shell utilities, and expected-output fixture.

Risks: exact expected output can be sensitive to script diagnostics and grep behavior. PATH manipulation is necessary but can hide external tool differences.

Test signals: verifies script exit-status contract and stable xzgrep output across option combinations.
