# sources/compression/xz/tests/test_compress_generated_text

Purpose: wrapper for running compression round-trip tests against deterministic lorem-like text.

Important behavior: executes `test_compress.sh compress_generated_text`, selecting the generated text fixture from `create_compress_files.c`.

Control flow: all logic is delegated to the shared compression script, including build-feature skips, fixture generation, preset/filter matrix, decompression, optional `xzdec` validation, and cleanup.

State and persistence: may create `compress_generated_text` in the build tests directory. Temporary compressed and uncompressed outputs are deleted by trap.

Dependencies and integration: included in `TESTS` and intended to run in parallel with other generated fixture wrappers.

Risks: `$srcdir` must be available. Generated text uses deterministic word selection, so stale fixture files can remain if not cleaned.

Test signals: round-trip byte equality over text-like data, covering a workload distinct from repeated and random inputs.
