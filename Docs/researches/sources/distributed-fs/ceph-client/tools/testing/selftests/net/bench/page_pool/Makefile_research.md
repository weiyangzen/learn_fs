# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bench/page_pool/Makefile

Purpose: Builds the `bench_page_pool.ko` kernel module from page-pool benchmark sources.

Important APIs/types/functions: Defines `KDIR ?= /lib/modules/$(shell uname -r)/build`, quiet/verbose `Q`, `obj-m += bench_page_pool.o`, and `bench_page_pool-y += bench_page_pool_simple.o time_bench.o`. `all` and `clean` invoke kernel module builds with `make -C $(KDIR) M=$(BENCH_PAGE_POOL_SIMPLE_TEST_DIR)`.

Control flow: Running `make` compiles the module against the selected kernel build tree; `clean` delegates cleanup to Kbuild.

State and persistence behavior: Produces module build artifacts in the source/output module directory depending on Kbuild invocation.

Dependencies and integration points: Requires a matching kernel build tree, module build support, and the two C files in this directory.

Risks: Building against headers for a different running kernel can produce an unloadable module. Tests require module load permissions.

Test signals: Presence of `bench_page_pool.ko` and successful `insmod` by the shell runner indicate build success.
