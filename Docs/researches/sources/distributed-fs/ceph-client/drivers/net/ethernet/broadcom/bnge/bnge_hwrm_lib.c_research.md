# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.c

## Purpose
This file provides command-specific HWRM wrappers above the generic request engine. It discovers firmware version and capabilities, registers the driver, configures backing-store memory, reserves rings, allocates VNIC/RSS/filter/stat/ring resources, configures PHY/link/TPA, and queries port/function statistics.

## Important APIs, Types, And Functions
Key public functions are `bnge_hwrm_ver_get`, `bnge_hwrm_func_reset`, `bnge_hwrm_fw_set_time`, `bnge_hwrm_func_drv_rgtr`, `bnge_hwrm_func_drv_unrgtr`, `bnge_hwrm_func_qcaps`, `bnge_hwrm_func_qcfg`, `bnge_hwrm_func_resc_qcaps`, `bnge_hwrm_vnic_qcaps`, `bnge_hwrm_queue_qportcfg`, `bnge_hwrm_func_backing_store_qcaps`, `bnge_hwrm_func_backing_store`, `bnge_hwrm_reserve_rings`, VNIC helpers, L2 filter helpers, ring alloc/free helpers, stats helpers, and link helpers. Internal helpers translate firmware capability responses into `bd` and `bn` fields.

## Control Flow
Probe paths first call version/capability queries, driver registration, function/resource queries, queue configuration, and backing-store capability setup. Open paths allocate stat contexts, rings, VNICs, RSS contexts, filters, and TPA configuration. Link paths use PHY qcaps/qcfg/cfg wrappers to update cached link state and apply ethtool requests. Stats paths query counter masks and trigger DMA updates.

## State And Persistence
The file populates persistent firmware-derived state in `struct bnge_dev`: firmware version strings, HWRM limits, chip ID, capability flags, PF identity, maximum MTU, doorbell aperture, resource maxima/reservations, RSS capability, queue mapping, PHY flags, and backing-store context metadata. It also updates `bnge_net` VNIC IDs, RSS context IDs, stat context IDs, ring firmware IDs, filter IDs, TPA settings, and stats sizes.

## Dependencies And Integration Points
It depends on `bnge_hwrm.c` for command transport, `bnge_rmem.c` for backing-store page tables, `bnge_resc.c` for ring-count calculations, `bnge_link.c` for common link request field construction, and `bnge_netdev.c` for ring/VNIC data structures. It uses HSI command structures heavily.

## Risks
Many functions assume firmware responses are internally consistent. Ring reservation has to reconcile TX, RX, completion, IRQ, stat, VNIC, and RoCE resource counts. Backing-store qcaps iteration depends on `next_valid_type`; a bad response can skip types or leave partially allocated `bd->ctx`. Resource-free helpers generally log and continue, so firmware/local ID skew is possible after failed cleanup.

## Test Signals
Probe/open/close cycles, ethtool link changes, RSS enablement, multicast/unicast filter updates, RoCE-enabled and disabled configurations, jumbo/GRO/LRO traffic, and stats collection exercise most wrappers. HWRM error injection should produce mapped errno values and clean local rollback.
