# sources/compression/zstd/contrib/gen_html/gen-zstd-manual.sh

Purpose: convenience shell script to generate a local `zstd_manual.html` from `../../lib/zstd.h` using the already-built `gen_html` executable.

Important behavior: extracts major/minor/release macros with `sed`, combines them into `LIBVER_SCRIPT`, echoes the version, and runs `./gen_html $LIBVER_SCRIPT ../../lib/zstd.h ./zstd_manual.html`.

State, dependencies, and integration: writes `./zstd_manual.html` in the contrib directory rather than the committed `doc/zstd_manual.html` path used by the Makefile. It depends on POSIX shell, sed, and a compiled `gen_html` binary.

Risks and test signals: because it emits to a local path, it is more of a manual helper than the release path. Macro-format drift or missing executable causes failure. The release workflow validates the Makefile path, not necessarily this helper.
