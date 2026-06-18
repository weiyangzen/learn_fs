# File Research: sources/block-storage/util-linux/libmount/samples/Makemodule.am

Automake fragment for libmount sample programs.

Key responsibilities:
- Adds Linux-only sample check programs for mount overwrite, statmount, and listmount.
- Defines source files, link libraries, and include flags for each sample.

Important behavior:
- Samples are included only when `LINUX` is true.
- `statmount` and `listmount` also link `libcommon.la`; `overwrite` links only `libmount.la` plus common `LDADD`.

Dependencies:
- Depends on the larger Automake build variables: `check_PROGRAMS`, `AM_CFLAGS`, `ul_libmount_incdir`, `LDADD`, `libmount.la`, and `libcommon.la`.

Notable risks:
- These are check/sample binaries, not installed utilities.
