# File Research: sources/cow-pools/nilfs-utils/include/Makefile.am

Installs public headers `nilfs.h` and `nilfs_gc.h`. Internal headers cover compatibility, parsing, cleaner control, segment iteration, vector helpers, CRC, mount/device lookup, paths, and feature handling.

If `CONFIG_UAPI_HEADER_INSTALL` is enabled, bundled kernel UAPI headers `linux/nilfs2_api.h` and `linux/nilfs2_ondisk.h` are installed with path preservation. Otherwise they remain non-installed internal headers.
