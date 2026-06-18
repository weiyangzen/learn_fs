## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/Makefile

Purpose: kselftest build and install manifest for netfilter selftests. It lists runnable shell tests, generated helper binaries, extended/manual tests, support files, and libmnl linkage.

Important variables and integration points: `top_srcdir`, `HOSTPKG_CONFIG`, `MNL_CFLAGS`, `MNL_LDLIBS`, `TEST_PROGS`, `TEST_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_FILES`, and `TEST_INCLUDES`. It includes `../../lib.mk`, which provides kselftest build rules for generated binaries and script installation.

Control flow: Make does not define explicit test execution logic here; it declares files for the kselftest framework. Helpers `nf_queue` and `conntrack_dump_flush` receive libmnl compile/link flags, and `udpclash` receives `-lpthread`. `TEST_PROGS` includes many netfilter scripts beyond this subset, while `TEST_GEN_FILES` ensures compiled helpers are available for shell harnesses.

State and persistence: build artifacts are created under `$(OUTPUT)` through kselftest conventions. Dependencies are `pkg-config`, `libmnl`, shell tools, and kernel selftest make infrastructure. Risks include missing libmnl pkg-config data, scripts referencing helpers not built or not in cwd, and `TEST_PROGS_EXTENDED` excluding performance tests from default runs. Test signal is build/install success and subsequent kselftest discovery.
