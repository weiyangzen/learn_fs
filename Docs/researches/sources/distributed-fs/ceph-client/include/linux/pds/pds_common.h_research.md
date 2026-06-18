<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h

## Purpose
Collects common PDS driver constants, device type identifiers, exported device-name strings, and public helper declarations shared between the core PDS driver and client modules.

## Important APIs, Types, And Functions
- `PDS_CORE_DRV_NAME`, `PDS_PAGE_SIZE`, `PDS_CORE_ADDR_LEN`, and `PDS_CORE_ADDR_MASK` describe common naming and address/page assumptions.
- `enum pds_core_driver_type` encodes OS/driver environments such as Linux, Windows, DPDK, FreeBSD, iPXE, ESXi.
- `enum pds_core_vif_types` classifies PDS devices as core, vDPA, VFIO, Ethernet, RDMA, live migration, and fwctl.
- `PDS_VDPA_DEV_NAME` and `PDS_VFIO_LM_DEV_NAME` build auxiliary/client names.
- Exported helpers include `pdsc_register_notify()`, `pdsc_unregister_notify()`, `pdsc_get_pf_struct()`, `pds_client_register()`, and `pds_client_unregister()`.

## Control Flow
Client drivers discover or receive the PF core object, register for notifications if needed, register a named client to get a firmware client ID, use client-specific AdminQ flows, then unregister. Notification blocks hook clients into core event distribution.

## State And Persistence
Persistent state is mostly registry state outside this header: notifier blocks, PF `struct pdsc` instances, and firmware client IDs. Constants here must stay stable because they are shared across modules and reflected in firmware-visible identify/register traffic.

## Dependencies And Integration Points
Includes `<linux/notifier.h>` and forward-declares `struct pdsc`. The prototypes integrate PDS core with PCI VFs, Linux notifier chains, auxiliary clients, vDPA, VFIO live migration, RDMA/Ethernet clients, and fwctl.

## Risks And Edge Cases
`PDS_CORE_ADDR_MASK` references `PDS_ADDR_LEN`, while this header defines `PDS_CORE_ADDR_LEN`; if no external macro supplies `PDS_ADDR_LEN`, this is a build bug. Client registration must handle duplicate names, missing PFs, reset-time unregistration, and notifier lifetime. Device type counts are bounded by `PDS_DEV_TYPE_MAX`, so firmware and driver tables must agree.

## Test Signals
Build coverage should catch the address-mask macro issue. Runtime signals include client register/unregister success, notifier callback delivery and removal, PF lookup from VF PCI device, and all named auxiliary-client probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_common.h -->
