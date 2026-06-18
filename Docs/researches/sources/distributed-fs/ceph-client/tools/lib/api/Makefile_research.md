<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/api/Makefile

## Purpose
This Makefile builds and installs the small `tools/lib/api` static library, `libapi.a`, plus its public headers. The library provides reusable support code for kernel tools: filesystem mount discovery, debug printing hooks, CPU sysfs helpers, buffered I/O, and poll fd arrays.

## Important APIs, types, and functions
Key variables are `srctree`, `OUTPUT`, `LIBFILE`, `API_IN`, `CFLAGS`, `HDRS`, `FD_HDRS`, `FS_HDRS`, and install path variables derived from `prefix`, `DESTDIR`, and `LP64`. It includes `tools/build/Makefile.include` and `tools/scripts/Makefile.include`, builds the recursive `libapi` object through `$(MAKE) $(build)=libapi`, archives it with `$(AR) rcs`, and installs headers under `$(prefix)/include/api`.

## Control flow
The default `all` target depends on `fixdep` and `$(LIBFILE)`. `$(API_IN)` triggers the tools build system for the `libapi` directory. `$(LIBFILE)` removes any stale archive before archiving the combined object. `install` runs both `install_lib` and `install_headers`. `clean` removes the archive and object/dependency files under `OUTPUT` or the current tree.

## State and persistence behavior
Persistent outputs are `$(OUTPUT)libapi.a`, intermediate object files, and installed headers/libraries. No runtime state is involved. `DESTDIR` supports packaging installs into an alternate root.

## Dependencies and integration points
This file is tightly integrated with the Linux tools build framework, including `fixdep`, quiet command macros, architecture variables, and recursive `Build` files. Consumers include perf and other tools that link the local API support archive instead of duplicating helpers.

## Risks and edge cases
The `clean` rule uses `find ... | xargs $(RM)` without `-print0`, so unusual filenames are not robust. `CFLAGS` enables `-Werror` by default unless `WERROR=0`, which can break cross builds on newer compilers. Header installation mirrors only selected public headers; adding new public headers requires updating this Makefile.

## Test signals
Run `make -C tools/lib/api O=<out>` and `make install_headers DESTDIR=<tmp> prefix=/usr`, verify `libapi.a` is produced, installed headers land under `include/api`, and `make clean` removes generated archive/object state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/Makefile -->
