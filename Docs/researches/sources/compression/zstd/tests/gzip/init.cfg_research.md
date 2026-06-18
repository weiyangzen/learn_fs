<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.cfg -->
## sources/compression/zstd/tests/gzip/init.cfg

Purpose: Local extension point loaded by `init.sh` after its generic shell-test harness setup.

Important APIs and functions: Defines `testdir_prefix_()` to print `gz`, overriding the default `gt` prefix for temporary directories.

Control flow: `init.sh` sources this file if present before calling `setup_ "$@"`. The overridden function is then used by `setup_` to construct temp directory templates such as `gz-$ME_.XXXX`.

State and persistence: Does not write state directly. It changes temporary directory naming for every gzip test sourcing `init.sh`.

Dependencies and integration points: Depends on the `init.sh` documented override hook. It integrates with cleanup, diagnostics, and temp directory creation indirectly through the harness.

Risks: Minimal risk; any syntax error here breaks all gzip tests. A non-unique prefix would not be enough to cause collisions because random suffixes are still used.

Test signals: Temporary directories created by gzip tests should use the `gz-` prefix.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.cfg -->
