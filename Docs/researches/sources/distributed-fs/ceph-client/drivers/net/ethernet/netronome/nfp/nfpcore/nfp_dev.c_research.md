# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.c

Purpose: Defines chip-family-specific static parameters for supported NFP PF and VF device IDs.

Important APIs/types/functions: `nfp_dev_info[NFP_DEV_CNT]` supplies DMA masks, queue-controller index/address limits, queue size bounds, PF chip names, PCIe explicit BAR config offsets, explicit data offsets, and queue-controller area sizes.

Control flow/state: No runtime control flow beyond static table access. Values are selected by PCI ID mapping elsewhere and passed into low-level PCIe setup.

Dependencies/integration: Used by PCI probe/transport setup, queue controller allocation code, and `nfp6000_pcie.c` for BAR CSR offsets and explicit data layout.

Risks: Wrong offsets or masks break DMA capability setup, queue controller addressing, or explicit PCIe access. VF entries intentionally omit PF-only fields; callers must avoid using PF-only fields for VFs.

Test signals: Probe each supported PF/VF ID, verify DMA mask setup, queue allocation bounds, and PCIe explicit access on PF devices.
