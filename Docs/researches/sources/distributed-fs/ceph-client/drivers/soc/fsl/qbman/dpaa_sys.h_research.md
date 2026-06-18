# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.h

Purpose: shared DPAA1 system helper header. It provides cache maintenance wrappers, ring helpers, portal resource constants, assertion behavior, private-memory init prototype, memremap policy, and IRQ affinity helper.

Important APIs/macros: `DPAA_PORTAL_CE` and `DPAA_PORTAL_CI` index portal resources. `dpaa_flush()`, `dpaa_invalidate()`, `dpaa_zero()`, `dpaa_touch_ro()`, and `dpaa_invalidate_touch_ro()` abstract cache operations. `DPAA_ASSERT()` becomes `WARN_ON()` under checking. `dpaa_cyc_diff()` computes cyclic ring distance. `DPAA_GENALLOC_OFF` avoids genalloc zero ambiguity. `QBMAN_MEMREMAP_ATTR` selects WB on PPC and WC elsewhere. `dpaa_set_portal_irq_affinity()` validates and sets IRQ affinity.

Control flow and integration: BMan and QMan portal code use these helpers for ring cache handling, portal mapping, BPID/FQID allocation, and CPU affinity.

State and persistence: no persistent state. Inline helpers perform immediate cache or IRQ operations.

Dependencies and risks: depends on architecture cacheflush support, prefetch, genalloc, platform devices, OF reserved memory, and IRQ affinity APIs. Risks include architecture-specific cache assumptions, especially PPC-only flush behavior and ARM non-cacheable mapping assumptions.

Test signals: portal rings operate without stale cache data, checking builds produce warnings for invalid API state, portal IRQs affined to expected CPUs, and memremap attributes matching platform coherency requirements.
