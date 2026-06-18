# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_sriov.h

Purpose: Declares EF100 SR-IOV configuration and disable entry points for NIC type and PCI integration.

Important APIs: `efx_ef100_sriov_configure()` handles Linux PCI SR-IOV configure requests. `efx_ef100_pci_sriov_disable()` is exposed for forced teardown paths. The header includes `net_driver.h` for `struct efx_nic`.

Control flow and integration: Used by EF100 NIC-type registration and teardown code to bridge kernel PCI SR-IOV callbacks to EF100-specific representor and MAE behavior.

State and persistence: No direct state. It exposes functions that mutate PCI VF state and `efx->vf_count`.

Dependencies: Requires matching `ef100_sriov.c` implementation, PCI SR-IOV availability, and representor support when `CONFIG_SFC_SRIOV` is active.

Risks: No include guard is present in the file as read, so repeated inclusion relies on build usage not producing conflicts. Prototype visibility should stay aligned with EF100 NIC type callbacks.

Test signals: Build with EF100 SR-IOV support and call through the PCI `.sriov_configure` path.
