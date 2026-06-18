# sources/distributed-fs/ceph-client/arch/sh/mm/cache-shx3.c

Purpose: performs SH-X3 secondary/cache-related initialization.

Important function: `shx3_cache_init`.

Control flow: invoked after SH4 cache init for SH7786/SHX3-style CPUs and adjusts cache settings or hooks for those cores.

State and persistence: mutates CPU cache configuration/hook state at boot.

Dependencies and integration: selected from `cpu_cache_init` based on `boot_cpu_data.type`.

Risks: SH-X3 cache behavior can require cross-core maintenance; missing setup may affect SMP coherency.

Test signals: SH-X3 boot, SMP cache flush tests, and debugfs cache parameter inspection.
