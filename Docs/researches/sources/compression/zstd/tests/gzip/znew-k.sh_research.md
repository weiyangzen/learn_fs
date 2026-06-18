<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/znew-k.sh -->
## sources/compression/zstd/tests/gzip/znew-k.sh

Purpose: Checks that `znew -K` works without invoking a failing `compress(1)` program.

Important APIs and functions: Sources `init.sh`, creates a local executable `compress` that fails, uses `gzip -c` to create a `.Z`-named file, runs `znew -K`, and checks file existence.

Control flow: The script shadows `compress` in `PATH`, creates `123456.Z` from a large blank input, runs `znew -K 123456.Z`, and requires both command success and original `.Z` file retention.

State and persistence: Creates local `compress` shim and `123456.Z` in the temp directory.

Dependencies and integration points: Tests `znew` conversion semantics and `PATH` shadowing through `path_prepend_ .`.

Risks: Requires basename length at least six for znew behavior. It only checks original retention, not the exact `.gz` output.

Test signals: `znew -K` succeeds, does not call the failing `compress`, and leaves `$name` present.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/znew-k.sh -->
