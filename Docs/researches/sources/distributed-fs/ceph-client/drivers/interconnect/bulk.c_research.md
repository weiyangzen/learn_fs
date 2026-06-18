# sources/distributed-fs/ceph-client/drivers/interconnect/bulk.c

Purpose: bulk consumer helpers for the interconnect framework, letting drivers acquire, release, vote, enable, and disable multiple named paths through `struct icc_bulk_data`.

Important APIs/types/functions: exports `of_icc_bulk_get()`, `icc_bulk_put()`, `icc_bulk_set_bw()`, `icc_bulk_enable()`, `icc_bulk_disable()`, and `devm_of_icc_bulk_get()`. `struct icc_bulk_devres` records caller-owned path arrays for devres cleanup.

Control flow: acquisition loops over names and calls `of_icc_get()`, unwinding already acquired paths on the first error. Bandwidth and enable loops stop on first error; enable rolls back the already enabled prefix by disabling it.

State and persistence: no independent state; it mutates `paths[i].path` and devres holds the same caller-provided table until device teardown.

Dependencies/integration: core interconnect consumer APIs, OF path names, devres, exported module symbols.

Risks and test signals: test partial acquisition, `-EPROBE_DEFER`, NULL paths for absent DT properties, enable rollback, and devm cleanup. `icc_bulk_set_bw()` does not roll back earlier successful votes.
