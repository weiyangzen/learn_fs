<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/Makefile.am -->
# sources/compression/xz/src/Makefile.am

Purpose: top-level Automake dispatcher for XZ Utils source subdirectories.

Important APIs/types/functions: `SUBDIRS` always includes `liblzma` and `xzdec`, conditionally adds `xz`, `lzmainfo`, and `scripts`; `EXTRA_DIST` lists common helper sources/resources.

Control flow: Automake descends into enabled subdirectories according to configure conditionals.

State and persistence: build artifacts are created in child directories; this file persists distribution membership for common files.

Dependencies and integration: controlled by component conditionals from `configure.ac`.

Risks: forgetting a common file in `EXTRA_DIST` can break release tarballs. Conditional subdir ordering matters because tools link against liblzma.

Test signals: `make distcheck` validates distribution completeness; configure toggles should include/exclude subdirs as expected.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/Makefile.am -->
