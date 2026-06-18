<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/unpack-invalid.sh -->
## sources/compression/zstd/tests/gzip/unpack-invalid.sh

Purpose: Regression test for invalid legacy `unpack`/gzip-like input that gzip 1.5 mishandled by outputting invalid data.

Important APIs and functions: Sources `init.sh`, writes byte-exact fixtures with `printf`, runs `gzip -d <in >out 2>err`, and exits through `Exit`.

Control flow: For each crafted byte string, it writes `in` and requires decompression to fail. If any input succeeds, `fail` becomes `1`.

State and persistence: Reuses `in`, `out`, and `err` in the temporary test directory.

Dependencies and integration points: Targets invalid stream detection in gzip-compatible decompression paths.

Risks: The loop resets `fail` to `0` on each failing input, so only the last case's result is authoritative unless an earlier success is followed by a later failure. That is a test weakness inherited from the script.

Test signals: Each active crafted input should make `gzip -d` return nonzero; the intended final result is failure if any invalid stream is accepted.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/unpack-invalid.sh -->
