<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h

Purpose: declares B0/B1 hardware capability records, aliases for S-device variants, operation-table symbols, and selected B0 hardware helper APIs.

Important APIs/types: extern caps for AQC100/107/108/109/111/112, aliases for AQC100S through AQC112S, `hw_atl_ops_b0`, `hw_atl_ops_b1` alias, and declarations for RSS/offload/ring/mac/flow-control/loopback/IRQ/filter/start helpers.

Control flow: PCI board matching selects these caps and ops for B0/B1 device IDs. Other hardware modules can call declared B0 helper functions when sharing behavior with later Atlantic variants.

State and persistence: no direct state; referenced caps and ops drive runtime hardware programming elsewhere.

Dependencies and integration: includes `aq_common`, and its prototypes reference `aq_hw_s`, `aq_ring_s`, `aq_ring_param_s`, `aq_rss_parameters`, and `aq_nic_cfg_s`.

Risks: aliases assume S variants share the same capabilities; exported helper prototypes must stay synchronized with implementation and any ATL2 reuse; ops aliasing means B1 behavior changes with B0 implementation. Test signals include link/load coverage for all B0/B1 IDs and compile coverage for helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_b0.h -->
