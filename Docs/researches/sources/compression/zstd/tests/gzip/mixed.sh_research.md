<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/mixed.sh -->
## sources/compression/zstd/tests/gzip/mixed.sh

Purpose: Tests `gzip -cdf` pass-through behavior for mixed compressed and uncompressed input, including edge sizes around internal buffers.

Important APIs and functions: Sources `init.sh`, uses pipelines to create compressed/uncompressed concatenations, invokes `gzip -cdf`, and compares with `compare`.

Control flow: It verifies plain input is copied, compressed data followed by plain data yields combined plaintext, and concatenated compressed members yield combined plaintext. A known failing case, plain data followed by compressed data, remains commented out. It then generates a range of small, 32 KiB boundary, and 128 KiB boundary plain inputs and requires `gzip -cdf` to act like `cat`.

State and persistence: Creates expected files `exp2` and `exp3`, repeatedly rewrites `in` and `out`, and emits size values to stdout.

Dependencies and integration points: Exercises force-decompress plus stdout mode (`-cdf`) where gzip-compatible zstd must decide whether to decompress or pass data through.

Risks: One mixed-order case is explicitly skipped, so coverage is asymmetric. The test relies on host `printf` supporting precision formatting for arbitrary generated sizes.

Test signals: All active comparisons must match expected plaintext, especially sizes `32831`, `32832`, `32833`, `131071`, `131072`, and `131073`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/mixed.sh -->
