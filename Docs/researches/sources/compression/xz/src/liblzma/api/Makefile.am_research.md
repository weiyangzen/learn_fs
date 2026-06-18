# sources/compression/xz/src/liblzma/api/Makefile.am

Purpose: declares the installed public liblzma headers and optional Doxygen API documentation targets.

Important APIs/types/functions: `nobase_include_HEADERS` installs `lzma.h` and all `lzma/*.h` subheaders while preserving the `lzma/` directory layout. Under `COND_DOXYGEN`, it defines `all-local`, `install-data-local`, `uninstall-local`, and `clean-local` for `doc/api`.

Control flow: normal builds install headers only. Doxygen-enabled builds run `doxygen/update-doxygen api` with source and build roots, then install generated HTML into `$(docdir)/api`.

State and persistence: generated API docs live under `$(top_builddir)/doc/api`; installed docs live under `$(DESTDIR)$(docdir)/api`; clean removes generated docs.

Dependencies/integration: establishes the public include surface consumed by applications as `<lzma.h>` plus internal subheaders included by that umbrella. Header list must stay aligned with `lzma.h` include order and symbol maps.

Risks: omitting a header breaks installation even if source builds. Installing subheaders is intentional, but each subheader guards against direct inclusion; downstream code must include `<lzma.h>`.

Test signals: install/dist checks, downstream compile tests against installed headers, and Doxygen generation when `COND_DOXYGEN` is enabled.
