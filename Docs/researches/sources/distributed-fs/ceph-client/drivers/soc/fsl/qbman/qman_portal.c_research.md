# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_portal.c

## Purpose
Binds QMan portal platform devices to CPU-affine `qman_portal` instances. It maps each portal's cache-enabled and cache-inhibited register windows, chooses a CPU, configures PAMU/stashing destination state, creates the affine portal, handles CPU hotplug retargeting, and performs stale frame-queue cleanup after kexec-style reuse.

## Important APIs, types, and functions
The file exports `qman_dma_portal` and `qman_portals_probed`. `portal_set_cpu` configures optional PAMU L1 stash and calls `qman_set_sdest`. `init_pcfg` applies LIODN fixup, creates the affine portal, enables configured interrupt sources, initializes all CGRs once the possible CPU portal set is populated, and selects the DMA portal. `qman_offline_cpu` and `qman_online_cpu` retarget IRQ affinity and SDEST when CPUs change state. `qman_portal_probe` owns platform resource parsing and portal initialization.

## Control flow and state behavior
Portal probe first waits for the global QMan CCSR driver via `qman_is_probed`; a zero return defers probing and a negative value fails. It allocates `struct qm_portal_config`, reads CE and CI resources, reads `cell-index` as the portal channel, obtains the IRQ, maps CE with `memremap` and CI with `ioremap`, and copies the pool SDQCR mask. Under `qman_lock`, it assigns the first not-yet-used possible CPU. Extra unassigned portals are mapped but skipped. Assigned portals set a 40-bit DMA mask and call `init_pcfg`.

After all portals are probed, if the CCSR layer detected preprogrammed private memory, this file iterates all FQIDs and calls `qman_shutdown_fq` to return hardware to reset-like state, then calls `qman_done_cleanup` to enable IRQs and clear cleanup state.

## Dependencies and integration points
Depends on `qman.c` for portal creation, IRQ-source programming, CGR initialization, and FQ cleanup; on `qman_ccsr.c` for global probe state, pool masks, LIODN/SDEST programming, and cleanup flags; on device tree compatible `"fsl,qman-portal"`; and optionally on PAMU/IOMMU stashing support.

## Risks and test signals
Hotplug retargeting assumes another online CPU exists when offlining a portal CPU. Probe error paths unmap CE/CI resources but do not destroy an already created portal after later cleanup failure. Cleanup iterates every possible FQID and can be slow or fail if hardware queues cannot drain. Test signals include one portal per possible CPU, `qman_portals_probed() == 1`, IRQ affinity updates on CPU hotplug, and successful stale-FQ cleanup when CCSR memory was reused.
