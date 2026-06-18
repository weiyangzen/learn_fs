# sources/distributed-fs/ceph-client/samples/damon/Kconfig

Purpose: Kconfig menu for three DAMON sample modules: working set estimation, proactive reclamation, and memory tiering.

Important APIs/functions: declares `SAMPLE_DAMON_WSSE`, `SAMPLE_DAMON_PRCL`, and `SAMPLE_DAMON_MTIER`. The first two depend on `DAMON && DAMON_VADDR`; memory tiering depends on `DAMON && DAMON_PADDR`.

Control flow: configuration only; selected symbols drive `samples/damon/Makefile`.

State and persistence: none at runtime.

Dependencies and integration: ties samples to DAMON virtual-address and physical-address monitoring capabilities.

Risks: help text for MTIER contains typos but conveys the intended two-node NUMA/CXL-like topology. Enabling samples without understanding DAMON actions can reclaim or migrate memory.

Test signals: `make menuconfig` should expose "DAMON Samples"; selected symbols should produce the corresponding sample objects.
