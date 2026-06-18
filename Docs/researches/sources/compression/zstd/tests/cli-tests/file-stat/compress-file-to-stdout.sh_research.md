# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-stdout.sh

## Purpose
This test covers file-input to stdout-output compression with `--trace-file-stat`.

## APIs, control flow, and integration
It generates `file`, runs `zstd file -cq --trace-file-stat > file.zst`, and tests the redirected output. The `-c` path avoids normal output file naming while still tracing the input file stat.

## State, dependencies, risks, and test signals
State is `file` and redirected `file.zst`. The test depends on stdout binary data not being polluted by trace diagnostics. Pass indicates diagnostics remain on stderr and the compressed stdout stream is valid.
