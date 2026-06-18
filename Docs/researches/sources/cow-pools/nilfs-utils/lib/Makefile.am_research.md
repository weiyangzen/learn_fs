# File Research: sources/cow-pools/nilfs-utils/lib/Makefile.am

Builds shared public libraries `libnilfs.la` and `libnilfsgc.la` plus internal helper libraries. `libnilfs` consists of `nilfs.c`, `sb.c`, and `lookup_device.c`; `libnilfsgc` consists of `gc.c`, `vector.c`, and `cnormap.c`.

Internal libraries include realpath, feature parsing, parser, mount checking, CRC32, old cleaner exec, segment parsing, cleaner control, and static variants. It also emits pkg-config files when enabled.
