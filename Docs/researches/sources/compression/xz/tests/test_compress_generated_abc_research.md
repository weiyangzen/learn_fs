# sources/compression/xz/tests/test_compress_generated_abc

Purpose: Automake-executable wrapper that runs `test_compress.sh` against the deterministic `compress_generated_abc` fixture.

Important behavior: uses `exec "$srcdir/test_compress.sh" compress_generated_abc`, so the wrapper process becomes the main compression test script and propagates its exit status.

Control flow: all substantive work occurs in `test_compress.sh`; this file only selects the repeated `"abc\n"` generated data profile.

State and persistence: causes `create_compress_files` to create `compress_generated_abc` if it does not already exist. Temporary compression outputs are managed by the shared script.

Dependencies and integration: listed in `TESTS` by `Makefile.am`; relies on `$srcdir`, executable shell, and the shared compression script.

Risks: if `$srcdir` is unset or points incorrectly, the wrapper cannot find `test_compress.sh`. Since it uses `exec`, there is no wrapper-specific cleanup after launch.

Test signals: inherits success, failure, or skip status from `test_compress.sh`. This fixture is useful for highly compressible repeated data and run-length-like behavior.
