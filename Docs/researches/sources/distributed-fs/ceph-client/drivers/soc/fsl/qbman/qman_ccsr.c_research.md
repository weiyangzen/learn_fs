# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_ccsr.c

## Purpose
Initializes and owns the global QMan CCSR register block. It discovers the QMan IP revision, maps global control registers, initializes reserved FQD and PFDR memory, enables global error reporting, seeds QMan gen_pool allocators, and exposes revision-dependent channel constants and cleanup status to the portal layer.

## Important APIs, types, and functions
Global exported state includes `qman_ip_rev`, `qm_channel_pool1`, and `qm_channel_caam`. Main helpers include `qm_set_memory`, `qm_init_pfdr`, `qm_set_pfdr_threshold`, `qm_set_sfdr_threshold`, `qm_set_corenet_initiator`, `qman_resource_init`, `qman_is_probed`, `qman_requires_cleanup`, `qman_done_cleanup`, `__qman_liodn_fixup`, and `qman_set_sdest`. `fsl_qman_probe` is the platform-driver entry point for `"fsl,qman"`.

The file defines error bit names and decoders for ECIR, ECIR2, EADR, and EDATA registers. `qman_isr` logs hardware error causes, logs additional portal/FQID/ECC context when capture registers indicate valid detail, disables noisy PFDR low-watermark and enqueue-blocked interrupts, and clears handled status bits.

## Control flow and state behavior
Probe maps the CCSR resource, reads `REG_IP_REV_1`, rejects unsupported revision 1.0, normalizes supported major/minor values into `QMAN_REVxx`, and adjusts pool/CAAM channel bases for rev3 hardware. It initializes FQD and PFDR private memory through `qbman_init_private_mem`; if BAR registers were already programmed with the same addresses, `qm_set_memory` returns a reuse signal and sets `__qman_requires_cleanup`. Fresh PFDR memory is initialized with an MCR command. After thresholds and scheduling defaults are programmed, the error IRQ is registered and enabled, gen_pools are created, FQID/pool/CGR ranges are seeded, the FQ lookup table is allocated, and the portal workqueue is created.

## Dependencies and integration points
This file provides the allocator and revision foundation for `qman.c` and `qman_portal.c`. It relies on reserved-memory setup via `qbman_init_private_mem`, platform resources and IRQs, Linux genalloc, and big-endian MMIO. Optional PPC compatibility paths zero legacy device-tree memory and flush dcache for noncoherent QMan access.

## Risks and test signals
Risks concentrate around reserved memory address/size validity, stale hardware state after kexec, revision-specific register layouts, and broad error IRQ enablement. `qman_resource_init` loops over `cgrid_num` while building `qm_pools_sdqcr`, so rev-specific pool and CGR counts should be checked carefully. Observable test signals are probe success, `qman_is_probed() == 1`, allocator range availability, error IRQ logs with decoded context, and portal cleanup running only when `qman_requires_cleanup()` is set.
