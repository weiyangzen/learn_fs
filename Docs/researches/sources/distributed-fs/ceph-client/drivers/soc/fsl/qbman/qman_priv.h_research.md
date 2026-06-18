# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_priv.h

## Purpose
Private QMan header shared by the CCSR, portal, core, and test implementations. It defines management-command result layouts not exposed in the public header, congestion-group bitset helpers, portal configuration, revision constants, private allocator globals, SDQCR/VDQCR constants, and internal cross-file function prototypes.

## Important APIs, types, and functions
Important types are `struct qm_mcr_querywq`, `struct qm_mcr_querycongestion`, `struct qm_mcr_querycgr`, `struct qman_cgrs`, and `struct qm_portal_config`. Inline helpers decode query results (`qm_mcr_querywq_get_chan`, `qm_mcr_querycgr_i_get64`, `qm_mcr_querycgr_a_get64`) and manipulate congestion-group bitsets (`qman_cgrs_init`, `qman_cgrs_fill`, `qman_cgrs_get`, `qman_cgrs_cp`, `qman_cgrs_and`, `qman_cgrs_xor`).

The header declares shared functions such as `qman_wq_alloc`, `__qman_liodn_fixup`, `qman_set_sdest`, `qman_create_affine_portal`, `qman_destroy_affine_portal`, `qman_query_fq`, `qman_alloc_fq_table`, `qman_get_qm_portal_config`, `qm_get_fqid_maxcnt`, `qman_shutdown_fq`, `qman_requires_cleanup`, `qman_done_cleanup`, and `qman_enable_irqs`.

## Control flow and state behavior
This file does not execute runtime control flow itself, but it defines the shared contracts that keep portal and CCSR state aligned. `struct qm_portal_config` carries mapped CE/CI portal windows, device, IOMMU domain, CPU, IRQ, dedicated channel, and accessible pool mask from probe into core portal creation. `struct qman_cgrs` mirrors the eight-word query-congestion result format, so bitset operations can be used directly against management-command output.

## Dependencies and integration points
It includes `dpaa_sys.h`, the public `<soc/fsl/qman.h>`, DMA mapping, and IOMMU headers, and optionally PAMU stash declarations. Its constants are consumed heavily by `qman.c`, `qman_ccsr.c`, and `qman_portal.c`.

## Risks and test signals
Risk comes from ABI-like coupling to hardware result structures and public QMan definitions. Endianness is mixed: some query fields are big-endian while congestion bitsets are treated as raw `u32` words, so callers must use the helper functions. Tests indirectly validate this header by exercising CGR callbacks, SDQCR/VDQCR constants, and portal config paths in the QMan tests and platform probe.
