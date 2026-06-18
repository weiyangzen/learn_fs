<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/z-suffix.sh -->
## sources/compression/zstd/tests/gzip/z-suffix.sh

Purpose: Checks custom suffix handling with `-Sz`.

Important APIs and functions: Sources `init.sh`, uses `gzip -Sz`, `gzip -dSz`, `test -f`, `compare`, and `Exit`.

Control flow: It creates `F` and copy `G`, compresses `F` using suffix `z`, requires original `F` removed and `Fz` created, then decompresses using the same suffix and requires `Fz` removed and regenerated `F` equal to `G`.

State and persistence: Creates `F`, `G`, and `Fz` in the temporary test directory.

Dependencies and integration points: Exercises gzip-compatible suffix parsing, output naming, and source removal.

Risks: The last comparison line contains `fail\1`, which appears to be a typo for `fail=1`; if the comparison fails, shell behavior may not set the failure flag as intended. The earlier file-existence checks still cover part of the flow.

Test signals: Correct behavior removes the source on compression, creates `Fz`, removes `Fz` on decompression, and restores content identical to `G`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/z-suffix.sh -->
