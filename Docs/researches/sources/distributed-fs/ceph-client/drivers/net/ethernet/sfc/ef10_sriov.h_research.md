# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.h

Purpose: Defines EF10 VF bookkeeping and declares EF10 SR-IOV/vswitching/vport/vAdaptor control APIs.

Important APIs and types: `struct ef10_vf` stores a VF's active `efx_nic`, `pci_dev`, firmware `vport_id`, `vport_assigned` flag, MAC, and default VLAN. `EFX_EF10_NO_VLAN` encodes no VLAN. Prototypes cover SR-IOV configure/init/fini, VF MAC/VLAN/spoof-check/link-state/config, PF/VF vswitching probe/restore/remove, vport MAC add/delete, and vAdaptor alloc/query/free.

Control flow and integration: Used by EF10 NIC type callbacks and generic SR-IOV ndo wrappers to manage firmware switching resources and per-VF policy.

State and persistence: Header defines the shape of runtime VF state stored under EF10 NIC private data. Firmware resources referenced by IDs persist outside the C struct and must be freed explicitly.

Dependencies: Includes `net_driver.h`, PCI types, and netlink VF configuration types through shared headers. Implementations are split across this file's matching C code and EF10 NIC MCDI support.

Risks: `efx_ef10_sriov_wanted()` currently returns false inline, affecting RSS channel limiting unless overridden by type behavior elsewhere. Public vport/vAdaptor helpers expose firmware-resource operations that require strict call ordering.

Test signals: Compile SR-IOV builds, validate ABI between EF10 NIC private data and this struct, and exercise all declared callbacks via netdev SR-IOV operations.
