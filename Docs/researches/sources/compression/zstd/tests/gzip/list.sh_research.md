<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/list.sh -->
## sources/compression/zstd/tests/gzip/list.sh

Purpose: Exercises gzip `--list`/`-l` behavior on invalid and valid inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip -l`, `gzip -9`, `compare`, and `Exit`.

Control flow: It writes a plain input file, requires `gzip -l in` to fail, compresses it at level 9, then runs `gzip -l in.gz` directly and through a pipe to `cat`. The two outputs must be identical.

State and persistence: Creates `in`, `orig`, `in.gz`, `out1`, and `out2` under the temporary directory.

Dependencies and integration points: Validates the zstd CLI list mode under gzip-compatible naming, including stdout behavior when output is piped.

Risks: Does not assert exact list content, only consistency between TTY-like and piped output paths. If both paths are consistently wrong, this test will not catch it.

Test signals: Listing a non-compressed file fails; listing a valid `.gz` succeeds and produces stable output independent of being piped.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/list.sh -->
