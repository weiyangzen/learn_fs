# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-mc.c

Purpose: SGI IP22 memory-controller initialization. It maps the MC, configures parity, write buffering, RPSS timing, GIO arbitration, and memory discovery.

Important APIs and control flow: bank helpers decode memory config base/size. `probe_memory()` is a no-op on IP28/32-bit builds where PROM owns usable memory, otherwise it adds valid banks above segment 1 to memblock. `sgimc_init()` maps `sgimc`, disables watchdog, clears error status, sets parity/check bits except on IP28, programs write-buffer depth and divider, builds GIO64 arbitration flags based on FullHouse/Guiness and board revision, writes `giopar`, and probes memory. IP28 also defines `prom_cleanup()` to switch ECC/WR_COL mode after ARCS is no longer needed.

State, persistence, and integration: exported `sgimc` and MC register configuration feed GIO, bus-error, timer, and platform code. Dependencies include `sgihpc_init()` having selected board type and IOC registers. Risks include direct hardware tuning, conditional memory discovery differences, and cache/ECC mode changes that can be hard to test. Test signals are MC revision log, correct memblock RAM, stable GIO DMA, and no parity/bus-error storms.
