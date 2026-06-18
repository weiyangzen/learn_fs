# sources/compression/xz/tests/test_files.sh

Purpose: shell validation of known-good, known-bad, and unsupported compressed fixtures for `xz` and optionally `xzdec`.

Important functions and variables: resolves `XZ` and `XZDEC`, skips when neither exists or decoder support is disabled, defines `have_feature()` to skip feature-specific fixtures while returning final status 77 if anything was skipped, and uses `NO_WARN` when check types are disabled.

Control flow: loops over good `.xz` files with per-filter feature gates and expects decode success from available tools. Bad `.xz` files must fail; unsupported files must fail for `xz`; unsupported-check is expected to pass under `-Q` and with `xzdec -qQ`. It also tests a historical `xz -l` index overflow fixture. `.lzma` good/bad fixtures are tested with `xz`; `.lz` fixtures run only when `HAVE_LZIP_DECODER` is enabled.

State and persistence: no output files are retained; all decoded data goes to `/dev/null`.

Dependencies and integration: depends on fixture naming conventions in `tests/files`, built tools, `config.h` macros, and shell globbing.

Risks: comments note partial decoder configurations can still produce failures because availability is checked coarsely. xzdec has different unsupported-check warning behavior, so assertions diverge by tool.

Test signals: unexpected success on bad/unsupported input or unexpected failure on good input exits 1. Skipped feature cases leave final status 77.
