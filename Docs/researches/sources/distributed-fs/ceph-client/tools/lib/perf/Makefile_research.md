## sources/distributed-fs/ceph-client/tools/lib/perf/Makefile

Purpose: Builds, tests, installs, and packages libperf static/shared libraries, headers, pkg-config file, docs, and tests.

Important targets/variables: Version triplet `0.0.1`, `LIBPERF_A`, `LIBPERF_SO`, `LIBPERF_PC`, `LIBAPI`, `libs`, `tests`, `install_*`, and generated object targets via tools build system.

Control flow: Determines `srctree`, includes make helpers, sets includes/CFLAGS, builds `libapi`, compiles `libperf-in.o`, archives static library, links shared library with version script and symlinks, builds tests static/shared, substitutes pkg-config template, and installs libraries/headers/docs.

State/persistence: Outputs are under `$(OUTPUT)` or current dir. Install writes under `DESTDIR`/`prefix`.

Dependencies/integration: Integrates with Linux tools build infrastructure, `tools/lib/api`, arch include discovery, version script, and documentation makefile.

Risks: `prefix ?=` defaults empty, so install paths require caller care. Clean removes broad local patterns. Shared link depends on `libapi` and version script. Header install includes internal headers, exposing unstable internals.

Test signals: Run `make libs`, `make tests`, shared-library load with `LD_LIBRARY_PATH`, `make install DESTDIR=... prefix=/usr`, and verify symlinks/pkg-config contents.
