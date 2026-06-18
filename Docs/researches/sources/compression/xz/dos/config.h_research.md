<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/dos/config.h -->
# sources/compression/xz/dos/config.h

Purpose: static configuration header for DJGPP/DOS builds.

Important APIs/types/functions: defines `ASSUME_RAM`, enabled checks, all listed encoders/decoders, LZMA match finders, x86 CRC assembly, lzip decoder, C headers/types, `NDEBUG`, package metadata, `SIZEOF_SIZE_T`, visibility, builtin byte-swap/alignment support, and fast unaligned access.

Control flow: no execution; preprocessor macros drive conditional compilation across liblzma, tuklib, getopt, and xz.

State and persistence: compile-time state only.

Dependencies and integration: consumed when `HAVE_CONFIG_H` is set by `dos/Makefile`.

Risks: diverges from Autoconf probes and must match DJGPP reality manually. Missing macros for newer features can silently disable code paths; incorrect macros can cause portability bugs.

Test signals: successful DOS build plus runtime compression/decompression tests; preprocessor inspection can verify expected feature gates.
<!-- END_FILE_RESEARCH: sources/compression/xz/dos/config.h -->
