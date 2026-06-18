# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_priv.h

Purpose: private BMan header connecting CCSR, portal, and high-level BMan API implementation files.

Important APIs/types/macros: defines portal interrupt source `BM_PIRQ_RCRI`, BMan revision constants, external `bman_ip_rev` and `bm_bpalloc`, `struct bm_portal_config`, `bman_create_affine_portal()`, `bman_p_irqsource_add()`, visible IRQ mask, `bman_get_bm_portal_config()`, cleanup status functions, and `bm_shutdown_pool()`.

Control flow and integration: included by `bman.c`, `bman_ccsr.c`, `bman_portal.c`, and tests so they share portal configuration, revision state, and cleanup contracts.

State and persistence: declares externally-owned persistent state rather than owning it. `bm_portal_config` carries mapped CE/CI addresses, device, CPU, and IRQ for each portal.

Dependencies and risks: depends on `dpaa_sys.h` and public `soc/fsl/bman.h`. Risks include tight coupling among implementation files and exported globals that require initialization ordering discipline.

Test signals: compile-time consistency across BMan objects, portal probe calling API functions correctly, and tests seeing revision constants through the private include path.
