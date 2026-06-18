# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.h

## Purpose
Defines the SR-IOV data model and build-time interface for the `bnx2x` driver. It describes PF-owned VF records, per-VF queues, mailbox/bulletin DMA layout, resource counters, state constants, TLV channel locking, and all PF and VF SR-IOV function prototypes. When `CONFIG_BNX2X_SRIOV` is disabled, it supplies stubs that let the rest of the driver compile and behave as non-SR-IOV.

## Important APIs, Types, and Functions
Key types are `struct bnx2x_sriov` for PCI SR-IOV capability metadata, `struct bnx2x_vf_bar`, `struct bnx2x_vf_queue`, `struct bnx2x_vf_queue_construct_params`, `struct bnx2x_vf_mac_vlan_filter`, `struct bnx2x_vf_mac_vlan_filters`, `struct bnx2x_virtf`, `struct bnx2x_vf_mbx_msg`, `struct bnx2x_vf_mbx`, `struct bnx2x_vf_sp`, `struct hw_dma`, and `struct bnx2x_vfdb`. Inline helpers map VF queues and IDs, including `vfq_get`, `vf_igu_sb`, `vf_hc_qzone`, `vfq_cl_id`, `vfq_stat_id`, and `vfq_qzone_id`.

Important macros include `BNX2X_VF_MAX_QUEUES`, `BNX2X_VF_MAX_TPA_AGG_QUEUES`, VF states (`VF_FREE`, `VF_ACQUIRED`, `VF_ENABLED`, `VF_RESET`, `VF_LOST`), VF config flags (`VF_CFG_STATS_COALESCE`, `VF_CFG_EXT_BULLETIN`, `VF_CFG_VLAN_FILTER`), resource accessors (`vf_rxq_count`, `vf_txq_count`, `vf_sb_count`, `vf_mac_rules_cnt`, `vf_vlan_rules_cnt`, `vf_mc_rules_cnt`), iteration helpers (`for_each_vf`, `for_each_vfq`, `for_each_vf_sb`), and handle conversion macros (`HW_VF_HANDLE`, `FW_VF_HANDLE`). The declared functions span IOV setup/teardown, mailbox handling, queue/filter/mcast/RSS/TPA operations, FLR cleanup, bulletin handling, VF-side VF-PF requests, and netdev VF controls.

## Control Flow and State
The header has little runtime flow beyond inline ID mapping and build-time stub dispatch. Its state model is central: `struct bnx2x_vfdb` hangs from `bp->vfdb` and owns the VF array, global VF queue array, context pages, SR-IOV PCI metadata, mailbox array, bulletin DMA, slowpath DMA, FLR bitmaps, event mutex/state, and bulletin mutex. Each `struct bnx2x_virtf` tracks lifecycle state, FLR/malicious flags, spoof check, stat/bulletin DMA addresses, resource counters, IGU base, queue pointer, BDF/BAR identity, filtering state, leading RSS client, multicast/RSS objects, per-VF operation mutex/current TLV, fastpath HSI version, and credit pools.

## State and Persistence Behavior
The declarations encode which state persists in software across operations and which state mirrors hardware/guest-visible resources. VF queue state persists in `struct bnx2x_vf_queue` objects and associated slowpath objects. Mailbox and bulletin persistence is represented by DMA-backed `struct hw_dma` regions and per-VF guest physical addresses. Compile-time stubs convert SR-IOV resource counts to zero and make SR-IOV actions no-ops when support is not built.

## Dependencies and Integration Points
Includes `bnx2x_vfpf.h` for TLV and bulletin structures and `bnx2x.h` for core driver types. The header is consumed by `bnx2x_sriov.c`, `bnx2x_vfpf.c`, `bnx2x_stats.c`, main event/timer/probe paths, netdev ndo declarations, and queue/filter/RSS/multicast code. Its stubs are important integration points for non-SR-IOV builds.

## Risks and Test Signals
Risks are ABI-like: wrong handle conversion, resource counter semantics, queue indexing, mailbox alignment, or stub behavior can break PF/VF communication or non-SR-IOV builds. The pointer arithmetic macros for `bnx2x_vf_sp` and mailbox/bulletin DMA require matching allocation sizes. Test signals include allmodconfig and `CONFIG_BNX2X_SRIOV=n` builds, VF acquire/init with maximum queues, FLR paths using initialized and uninitialized VF objects, stats coalescing mode, long and legacy bulletin support, and code paths that include this header without SR-IOV enabled.
