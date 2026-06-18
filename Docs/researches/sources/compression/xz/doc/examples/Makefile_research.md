<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/Makefile -->
# sources/compression/xz/doc/examples/Makefile

Purpose: simple standalone makefile for compiling the documented liblzma examples outside the Autotools build.

Important APIs/types/functions: variables `CC=c99`, `CFLAGS=-g`, `LDFLAGS=-llzma`, `PROGS`, pattern rule `.c:`, and `clean`.

Control flow: `all` builds the five example programs by compiling each source file directly with the configured compiler and linker flags.

State and persistence: persists local executable outputs and removes them in `clean`.

Dependencies and integration: assumes an installed liblzma and C99 compiler are available in normal system paths.

Risks: not tied to build-tree headers/libraries, so it may compile against a different liblzma than the source checkout. No dependency tracking or platform-specific flags.

Test signals: `make`, then run each example on small sample inputs and validate generated `.xz` streams or file-info output.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/Makefile -->
