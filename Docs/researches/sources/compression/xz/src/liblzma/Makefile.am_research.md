# sources/compression/xz/src/liblzma/Makefile.am

Purpose: top-level Automake recipe for building `liblzma.la`, installing pkg-config metadata, including feature-specific source fragments, and handling Windows export artifacts.

Important APIs/types/functions: defines `SUBDIRS = api`, `lib_LTLIBRARIES = liblzma.la`, `liblzma_la_CPPFLAGS` include paths and `-DTUKLIB_SYMBOL_PREFIX=lzma_`, `liblzma_la_LDFLAGS = -no-undefined -version-info 13:3:8`, and conditionally adds linker version scripts. It includes `common/Makefile.inc`, `check/Makefile.inc`, and optional filter directories gated by `COND_FILTER_*`.

Control flow: Automake conditionals select source sets for threads, LZ, LZMA1/rangecoder, delta, simple filters, Windows resources, shared-library `.def` generation, and pkg-config generation. The `.rc.lo` suffix rule compiles Windows resources for shared libraries while replacing static objects with an empty C object.

State and persistence: build-time generated files include `liblzma.pc`, Windows `liblzma.def`, `liblzma.def.in`, and `empty.c`, all cleaned by `CLEANFILES` or `clean-local`. No runtime state.

Dependencies/integration: anchors all liblzma compilation, symbol version scripts, public API subdir, tuklib physmem/cpucores helpers, and `liblzma.pc`. It must stay in sync with source file additions and configure condition names.

Risks: missing a source fragment or conditional can silently remove codecs/checks from builds. Version-info and symbol-map changes affect ABI. The Windows `.def` generation depends on shared linking side effects and GNU-like tooling assumptions.

Test signals: `make distcheck`, shared/static builds, Windows builds, symbol-map validation via `validate_map.sh`, and pkg-config install tests are the main signals.
