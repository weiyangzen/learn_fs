# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/Makefile

Purpose: Kselftest manifest for networking benchmark tests, currently page-pool benchmark support.

Important APIs/types/functions: Sets `TEST_GEN_MODS_DIR := page_pool`, adds `test_bench_page_pool.sh` to `TEST_PROGS`, and includes `../../lib.mk`.

Control flow: Kselftest build rules descend into the `page_pool` module directory and expose the shell runner as a test program.

State and persistence behavior: Build artifacts include kernel module files under the output/module directory. No runtime state is created by the Makefile.

Dependencies and integration points: Integrates with `bench/page_pool/Makefile` to build `bench_page_pool.ko` and with `test_bench_page_pool.sh` to load it.

Risks: Requires a configured kernel build directory for module compilation. Benchmark modules may be skipped or fail on systems that cannot build/load modules.

Test signals: Successful build produces the page-pool module and test script in kselftest output.
