# sources/distributed-fs/ceph-client/samples/damon/Makefile

Purpose: maps DAMON sample Kconfig symbols to module objects.

Important APIs/functions: `obj-$(CONFIG_SAMPLE_DAMON_WSSE) += wsse.o`, `obj-$(CONFIG_SAMPLE_DAMON_PRCL) += prcl.o`, and `obj-$(CONFIG_SAMPLE_DAMON_MTIER) += mtier.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: integrates with kbuild and symbols from `samples/damon/Kconfig`.

Risks: no conditional dependency logic here; Kconfig must enforce DAMON support.

Test signals: selected sample config symbols should compile the matching `.ko` files.
