# sources/distributed-fs/ceph-client/tools/lib/symbol/Makefile

Purpose: Builds and installs `libsymbol.a`, containing symbol parsing helpers such as kallsyms support.

Important APIs/types/functions: Targets include `all`, `$(SYMBOL_IN)`, `$(LIBFILE)`, `install_lib`, `install_headers`, `install`, and `clean`. Variables configure compiler/archive tools, `CFLAGS`, `OUTPUT`, `LIBFILE`, header install path, `prefix`, and `libdir`.

Control flow: Determines `srctree`, includes tools make helpers, builds `libsymbol-in.o` recursively via `$(build)=libsymbol`, archives `libsymbol.a`, installs archive and `kallsyms.h`.

State and persistence: Produces `$(OUTPUT)libsymbol.a` and intermediate objects; install copies archive/header to configured destination. `clean` removes outputs and object metadata.

Dependencies/integration: Includes tools build and scripts makefiles; requires `tools/lib`, `tools/include`, and generated fixdep support.

Risks: `CFLAGS += -D_FORTIFY_SOURCE` omits an explicit level, which may behave differently than common `-D_FORTIFY_SOURCE=2`. `WERROR` can break on compiler warning churn. Header install list must stay aligned with public API.

Test signals: Build/install under default/custom `OUTPUT`, `DEBUG=0`, `WERROR=0`, LP64/non-LP64, and DESTDIR packaging.
