<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/Makefile.am -->
# sources/compression/xz/debug/Makefile.am

Purpose: Automake recipe for non-installed debug helper programs in `debug/`.

Important APIs/types/functions: declares `noinst_PROGRAMS` for `repeat`, `sync_flush`, `full_flush`, `memusage`, `crc32`, `known_sizes`, `hex2bin`, and `testfilegen-arm64`; sets include paths for `src/common` and liblzma API headers; links against `src/liblzma/liblzma.la`, optional `lib/libgnu.a`, and `$(LTLIBINTL)`.

Control flow: Automake builds each listed helper from same-named sources, applies `AM_CPPFLAGS`, and conditionally appends gnulib support when `COND_GNULIB` is true.

State and persistence: no runtime state; persisted build outputs are local, non-installed helper executables.

Dependencies and integration: integrates with top-level `configure.ac` conditionals, liblzma, common headers, gnulib replacement objects, and gettext/linker flags.

Risks: debug helpers are linked against current build-tree liblzma, so stale builds or missing optional gnulib objects can cause misleading failures. They are intentionally not installed, so packaging should not rely on them.

Test signals: `make -C debug` should produce all helpers; link failures indicate broken liblzma or replacement-function configuration.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/Makefile.am -->
