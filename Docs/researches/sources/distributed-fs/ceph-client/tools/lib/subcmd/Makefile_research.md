# sources/distributed-fs/ceph-client/tools/lib/subcmd/Makefile

Purpose: Builds and installs `libsubcmd.a`, the common subcommand/option/pager/process helper library used by Linux tools.

Important APIs/types/functions: Targets include `all`, `$(SUBCMD_IN)`, `$(LIBFILE)`, `install_lib`, `install_headers`, `install`, `clean`, and `FORCE`. Variables configure `srctree`, compiler tools, `CFLAGS`, `OUTPUT`, `LIBFILE`, header install list, `prefix`, and `libdir`.

Control flow: The Makefile derives `srctree` when unset, includes kernel tools build helpers, builds `libsubcmd-in.o` via recursive `$(MAKE) $(build)=libsubcmd`, archives it into `libsubcmd.a`, and installs library/header files under `DESTDIR`/`prefix`.

State and persistence: Produces object files and `$(OUTPUT)libsubcmd.a`; install targets copy artifacts into the configured destination. `clean` removes archive and object/cmd/dependency files.

Dependencies/integration: Includes `../../scripts/Makefile.include`, `../../scripts/utilities.mak`, and `$(srctree)/tools/build/Makefile.include`. Requires kernel tools headers under `tools/include`.

Risks: `find ... | xargs $(RM)` can invoke `rm` with no arguments depending on xargs behavior; usually harmless with `rm -f`. Header install list must stay synchronized with exported API. `WERROR` defaults to enabled unless explicitly `0`, which can break builds on newer compilers.

Test signals: Build with default and custom `OUTPUT`, `DEBUG`, `WERROR=0`, `LP64`, `DESTDIR`, and cross-compile variables; verify archive contents and installed headers.
