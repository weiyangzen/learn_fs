# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.h

Purpose: declares DH895xCC VF constants and hw-data init/cleanup prototypes.

Important definitions: PMISC BAR is 1, ETR BAR is 0, accelerator and engine masks are both `0x1`, maximum accelerators/engines are one each, RX rings start at offset 8, TX rings mask is `0xFF`, and ETR max banks is one.

Control flow and integration: constants are used by VF hw-data initialization and VF PCI probe to configure ring and BAR access for a single virtual accelerator.

State and persistence: no runtime state; constants define the persistent hardware contract for VF instances.

Risks and test signals: mismatch with PF-provided VF resources would break ring setup or interrupt handling. Tests should verify BAR/resource mapping, ring service layout, and compatibility with `ADF_GEN2_DEFAULT_RING_TO_SRV_MAP`.
