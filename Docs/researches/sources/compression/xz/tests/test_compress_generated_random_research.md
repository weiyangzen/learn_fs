# sources/compression/xz/tests/test_compress_generated_random

Purpose: wrapper for running the compression round-trip suite against deterministic pseudo-random data.

Important behavior: executes `test_compress.sh compress_generated_random` through `$srcdir`, inheriting all logic and exit statuses from the shared script.

Control flow: the shared script invokes `create_compress_files` for `compress_generated_random`, compresses with presets and supported filters, decompresses with `xz`, optionally verifies with `xzdec`, and compares bytes.

State and persistence: may create the `compress_generated_random` fixture in the build tests directory. Temporary round-trip files are cleaned by the shared script trap.

Dependencies and integration: part of Automake `TESTS`; depends on generated-file support, `xz`, optional `xzdec`, and shell tools.

Risks: the fixture is intentionally hard to compress, so it can expose expansion and buffer-size behavior. Runtime may be larger than the tiny abc fixture but remains deterministic.

Test signals: inherited exit 0/1/77 from the shared script. Byte-for-byte comparison is the key correctness signal.
