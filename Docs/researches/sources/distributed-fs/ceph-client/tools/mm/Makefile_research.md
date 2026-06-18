# sources/distributed-fs/ceph-client/tools/mm/Makefile

Purpose: Builds and installs Linux VM/MM user-space tools in `tools/mm`.

Important APIs and targets: `BUILD_TARGETS` are `page-types`, `slabinfo`, `page_owner_sort`, and `thp_swap_allocator_test`; `INSTALL_TARGETS` additionally includes the script `thpmaps`. The generic `%: %.c` rule compiles C tools. `$(LIBS)` builds `../lib/api/libapi.a`. Targets are `all`, `clean`, and `install`.

Control flow: The default target builds all C tools after the shared libapi dependency. `clean` removes binaries and cleans libapi. `install` creates `$(DESTDIR)$(sbindir)` and installs binaries/scripts with mode 755.

State and persistence behavior: Produces local tool binaries and may install them under `/usr/sbin` or a supplied destination. It does not track generated dependency files.

Dependencies and integration points: Includes `../scripts/Makefile.include`, adds `-I../lib/`, links libapi and pthreads, and fits the kernel tools build/install conventions.

Risks: Every C target links pthread even when not needed. The pattern rule assumes target and source basename match. Installing `thpmaps` assumes script executable semantics.

Test signals: Run `make -C tools/mm`, `make clean`, and `make DESTDIR=<tmp> install`; verify expected binaries and installed script.
