<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h

Purpose: declares the public A0 hardware capability records and operation table for PCI board matching.

Important APIs/types: extern declarations for `hw_atl_a0_caps_aqc100`, `hw_atl_a0_caps_aqc107`, `hw_atl_a0_caps_aqc108`, `hw_atl_a0_caps_aqc109`, and `hw_atl_ops_a0`.

Control flow: `aq_pci_func.c` references these symbols when a supported early Aquantia PCI ID/revision maps to A0 hardware. The selected caps feed `aq_nic_cfg_start`; the ops table drives reset/init/ring/filter/IRQ functions.

State and persistence: no direct state. The referenced constants describe hardware capability and ops linkage.

Dependencies and integration: includes `aq_common` for `aq_hw_caps_s` and `aq_hw_ops` declarations. It is the boundary between PCI enumeration and A0 implementation.

Risks: missing or mismatched declarations would break board selection; adding new A0 variants requires matching caps and PCI table entries. Test signals are compile/link coverage and successful probe of A0 revision devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_a0.h -->
