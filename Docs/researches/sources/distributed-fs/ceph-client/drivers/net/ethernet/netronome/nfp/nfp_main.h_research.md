# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.h

## Purpose
Declares PF-wide NFP driver state, firmware dump structures, and cross-module helpers for PCI probe/remove, hwmon, runtime-symbol access, PF mailbox commands, flash update, dumps, shared buffers, devlink params, and link-rate conversion.

## Important APIs, Types, and Functions
- `struct nfp_dumpspec` stores firmware dump TLV data.
- `struct nfp_pf` is the PF container with PCI/CPP/app handles, BAR mappings, mailbox symbol, MSI-X entries, SR-IOV state, firmware metadata, HWInfo/ETH/NSP tables, hwmon/debugfs, vNIC/port lists, workqueue, refresh work, shared buffers, and counts.
- Declares exported helpers including `nfp_net_pci_probe/remove()`, `nfp_hwmon_register/unregister()`, `nfp_pf_rtsym_read_optional()`, `nfp_pf_map_rtsym()`, `nfp_mbox_cmd()`, `nfp_flash_update_common()`, dump helpers, shared-buffer helpers, devlink params, and speed/link-rate conversions.

## Control Flow
No executable flow. This header defines the PF state contract used by probe, devlink, app, netdev, hwmon, dump, and shared-buffer modules.

## State and Persistence Behavior
`struct nfp_pf` centralizes mutable PF runtime state. Fields that may change after probe are documented as protected by the devlink instance lock. Persistent device/firmware state is accessed through handles in this struct but not stored on disk here.

## Dependencies and Integration Points
Depends on Linux PCI, workqueue, ethtool, devlink, list types, and many forward-declared NFP core structs. It is included by almost every PF-level source file in this subset.

## Risks
The PF struct has broad ownership and locking requirements. Misusing fields that require devlink lock can race with port refresh, SR-IOV, or devlink operations. The comment has a typo ("proble") but the locking contract is clear.

## Test Signals
Build coverage across modules, lockdep for devlink-locked fields, probe/remove leak checks, and validation of declared helpers through devlink/hwmon/shared-buffer/dump paths.
