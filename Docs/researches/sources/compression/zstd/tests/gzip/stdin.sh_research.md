<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/stdin.sh -->
## sources/compression/zstd/tests/gzip/stdin.sh

Purpose: Ensures gzip-compatible argument `-` is treated as stdin and can be interleaved with named inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip -dc in - in < in`, `compare`, and `Exit`.

Control flow: It compresses a single `a` byte to `in`, prepares expected output `aaa`, then asks gzip to decompress named file `in`, stdin `-`, and named file `in` again. Output must be three decoded copies with no stderr.

State and persistence: Creates `in`, `exp`, `out`, and `err` in the temporary test directory.

Dependencies and integration points: Exercises file iteration and stdin sentinel behavior in zstd's gzip mode.

Risks: If stdin handling consumes too much or too little, the final named input can still run, so the exact output comparison is the key signal.

Test signals: Exit zero, `out` equals `aaa`, and `err` is empty.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/stdin.sh -->
