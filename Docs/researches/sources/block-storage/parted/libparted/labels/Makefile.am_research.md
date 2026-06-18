# File Research: sources/block-storage/parted/libparted/labels/Makefile.am

Purpose: Automake build definition for libparted disk-label backends.

Content: Builds `liblabels.la` from common label sources, conditionally includes S390/DASD sources when `COMPILE_FOR_S390` is true, wires include paths and libraries, and generates `pt-limit.c` from `pt-limit.gperf`.

Important details: The gperf output is post-processed with Perl to add `static` before `__GNUC_STDC_INLINE__`, then installed as a read-only generated file. `pt-limit.c` is a built source included by `pt-tools.c`, not compiled independently.

Risks/tests: Build correctness depends on gperf availability for maintainer builds and on `S390_SRCS` matching platform configuration. Dist and maintainer-clean rules must keep generated and source gperf files in sync.
