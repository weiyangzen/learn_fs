<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/trailing-nul.sh -->
## sources/compression/zstd/tests/gzip/trailing-nul.sh

Purpose: Verifies gzip behavior with trailing bytes after a compressed member, especially accepted trailing NUL bytes.

Important APIs and functions: Sources `init.sh`, creates three compressed files with appended bytes, runs `gzip -d`, and uses `compare`.

Control flow: `0.gz` has one trailing NUL and should exit `0`; `00.gz` has two trailing NULs and should exit `0`; `1.gz` has a trailing byte `\1` and should exit `1`. For non-error cases, the decompressed file content must equal the corresponding line.

State and persistence: Creates `0.gz`, `00.gz`, `1.gz`, decompressed outputs `0`, `00`, `1` as applicable, and `exp`.

Dependencies and integration points: Exercises trailing-garbage policy in gzip-compatible decompression and source removal behavior after `gzip -d`.

Risks: The script compares numeric return code to the loop variable, so the file names deliberately encode expected status. A behavior change around multiple trailing NULs will be caught.

Test signals: Exit status equals `0`, `0`, and `1` respectively; successful outputs match their expected line.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/trailing-nul.sh -->
