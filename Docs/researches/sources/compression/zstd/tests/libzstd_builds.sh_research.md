<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/libzstd_builds.sh -->
## sources/compression/zstd/tests/libzstd_builds.sh

Purpose: Validates libzstd build feature switches by inspecting generated library objects and executable-stack metadata.

Important APIs and functions: Shell helpers `die`, `isPresent`, and `mustBeAbsent` check `tmplog` produced by `nm`. The script repeatedly runs `make -C ../lib libzstd` or `libzstd.a` with different environment variables and verifies object presence.

Control flow: It builds the default library and requires compression, decompression, and dictionary builder objects while excluding legacy and deprecated zbuff objects. It checks `readelf -lW libzstd.so` for a non-executable `GNU_STACK`. It then rebuilds static library variants with compression disabled, decompression disabled, deprecated disabled/enabled, dictionary builder disabled, decompression plus dictionary builder disabled, and legacy support enabled, cleaning artifacts between cases.

State and persistence: Produces and removes `../lib/libzstd.a`, `../lib/libzstd.so*`, and local `tmplog`. Build products in the lib directory are mutated repeatedly.

Dependencies and integration points: Depends on `make`, `nm`, `grep`, `readelf`, and zstd's makefile feature variables: `ZSTD_LIB_COMPRESSION`, `ZSTD_LIB_DECOMPRESSION`, `ZSTD_LIB_DEPRECATED`, `ZSTD_LIB_DICTBUILDER`, and `ZSTD_LEGACY_SUPPORT`.

Risks: `readelf` is assumed available. Object names are implementation details, so source-file renames can break this test even if feature behavior remains correct. `mustBeAbsent` intentionally echoes on success due to shell behavior noted in the script.

Test signals: Each feature combination must include/exclude the expected `.o` names; `GNU_STACK` must not contain `RWE`; any mismatch calls `die`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/libzstd_builds.sh -->
