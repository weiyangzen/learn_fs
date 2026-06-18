# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/Makefile

Purpose: this Makefile builds the TCP-AO selftest suite for both IPv4 and IPv6 variants and links each program against a shared local static test library. It is the build integration point for the TCP-AO sources in this subset.

Important APIs and variables: `TEST_BOTH_AF` lists programs compiled for both address families, including `bench-lookups`, `connect`, `connect-deny`, `icmps-accept`, `icmps-discard`, and `key-management`. `TEST_IPV4_PROGS`, `TEST_IPV6_PROGS`, and `TEST_GEN_PROGS` derive output names. `LIBSRC` lists shared library sources, and `LIB`, `LIBOBJ`, `LIBDEPS`, `CFLAGS`, and `LDLIBS` define build products and flags.

Control flow: it includes `../../lib.mk`, builds `$(OUTPUT)/lib/libaotst.a` with `$(HOSTAR)`, compiles library objects from `./lib/*.c`, and makes every generated test depend on the library. Pattern rules build `%_ipv4` normally and `%_ipv6` with `-DIPV6_TEST`. Per-target flags add `-DTEST_ICMPS_ACCEPT` for `icmps-accept` and `-lm` for `bench-lookups`.

State and persistence: generated state is confined to `$(OUTPUT)` and the `$(OUTPUT)/lib` subdirectory. `EXTRA_CLEAN` records library objects and archive for cleanup. Source files are not modified.

Dependencies and integration points: depends on kernel headers via `$(KHDR_INCLUDES)`, selftest `lib.mk`, pthreads, and math library for benchmark statistics. It includes headers from `../../../../include/` and `./lib/`.

Risks: `icmps-accept.c` and `icmps-discard.c` share the same source body semantics, with target-specific behavior selected by compile flags; missing the per-target flag would invert the accept test. All tests are compiled twice, so source code must remain address-family-generic through `aolib.h` macros.

Test signals: build success creates IPv4 and IPv6 binaries in `$(OUTPUT)`. Correct target-specific behavior is visible in `icmps-accept_*` receiving `TEST_ICMPS_ACCEPT` and benchmark binaries linking successfully with `-lm`.
