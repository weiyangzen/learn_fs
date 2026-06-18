# File Research: sources/cow-pools/openzfs/lib/libzpool/Makefile.am

Automake definition for `libzpool.la`, the userland build of substantial ZFS kernel logic used by tools and tests.

Key structure:
- Includes `lib/libzpool/include/Makefile.am`.
- Defines `libzpool_la_CFLAGS`, `CPPFLAGS`, library target, and cppcheck target.
- `dist_libzpool_la_SOURCES` lists platform/userland shim files such as `abd_os.c`, `kernel.c`, `util.c`, `zfs_file_os.c`, and `zfs_debug.c`.
- `nodist_libzpool_la_SOURCES` pulls in Lua, common ZFS code, crypto/compression/checksum code, SPA/DMU/DSL/vdev/ZIO modules, and other kernel sources for userland linking.
- `btree.c` and `range_tree.c` are compiled as sources, not linked via `LIBADD`, to avoid exporting their symbols from the libzpool API.
- Links against `libicp`, `libnvpair`, `libzstd`, `libzutil`, clock/zlib/math libraries, and `-lgeom` on FreeBSD.

It also adds PowerPC AltiVec flags for the relevant raidz math object files.
