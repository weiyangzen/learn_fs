# sources/distributed-fs/ceph-client/arch/sh/mm/cache-debugfs.c

Purpose: reports SH cache geometry and register-derived cache information through debugfs.

Important functions: `cache_debugfs_show` and `cache_debugfs_init`.

Control flow: seq_file output prints I-cache/D-cache and optional secondary-cache fields from `boot_cpu_data`, including ways, sets, entry masks, alias masks, and flags.

State and persistence: read-only diagnostic view of boot-probed CPU cache state.

Dependencies and integration: debugfs, seq_file, `asm/cache.h`, `asm/processor.h`, and `arch_debugfs_dir`.

Risks: output must stay in sync with `struct cache_info`; debugfs consumers should not treat it as stable ABI.

Test signals: debugfs file presence and values matching boot log cache parameters.
