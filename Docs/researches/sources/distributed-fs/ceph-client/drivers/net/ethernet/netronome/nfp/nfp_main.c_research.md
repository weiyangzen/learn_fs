# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_main.c

## Purpose
Implements the NFP PF PCI driver lifecycle: device ID matching, PCI enable/resource setup, CPP/NSP initialization, firmware selection/loading/unloading, runtime-symbol mailbox operations, SR-IOV configuration, devlink/PF allocation, vNIC probe/remove delegation, hwmon registration, and module init/exit.

## Important APIs, Types, and Functions
- `nfp_pci_probe()` is the PF probe path. It enables PCI, sets DMA mask, reserves regions, allocates devlink/PF state, creates workqueue, opens CPP, reads HWInfo, waits board-ready, initializes NSP/firmware, reads MIP/rtsyms, validates SR-IOV limits, configures HWInfo, probes net vNICs, and registers hwmon.
- `__nfp_pci_shutdown()`, `nfp_pci_remove()`, and `nfp_pci_shutdown()` unwind runtime state and optionally unload firmware.
- `nfp_fw_load()` implements firmware load policy from NSP HWInfo, optional reset, disk firmware lookup, stored firmware fallback, and unload-on-remove tracking.
- `nfp_net_fw_find()` searches firmware by serial/interface, PCI name, then card/media model.
- `nfp_mbox_cmd()` serializes PF mailbox commands via runtime symbol offsets.
- `nfp_pcie_sriov_enable/disable/configure()` coordinates PCI SR-IOV and app-specific VF setup under devlink lock.
- `nfp_main_init()` registers PF and VF PCI drivers and debugfs; exit unregisters them.

## Control Flow
Probe is staged with a strict goto unwind ladder. Firmware initialization opens NSP, waits for management firmware, reads ports and NSP identity, applies firmware load policy, and marks whether this driver instance should unload firmware later. After runtime symbols and app capability data are available, `nfp_net_pci_probe()` owns vNIC/app construction. Remove/shutdown reverses registration, disables SR-IOV, removes vNICs, frees firmware metadata, optionally resets firmware, destroys workqueue/CPP/devlink/PCI resources.

## State and Persistence Behavior
Owns the PF-wide `struct nfp_pf` lifetime through devlink private data. Mutates persistent firmware/flash state when loading stored/disk firmware or flashing through shared helper. Runtime state includes CPP handle, HWInfo, ETH table, NSP identify info, MIP/rtsym table, mailbox symbol pointer, firmware-loaded flags, VF limits/count, dumpspec, workqueue, vNIC/port lists, and hwmon pointer.

## Dependencies and Integration Points
Depends on Linux PCI/devlink/firmware/SR-IOV APIs, NFP CPP/nfpcore/NSP/rtsym/HWInfo/MIP layers, app abstractions, common netdev probe/remove, hwmon, debugfs, and ABI constants from `nfp_abi.h`. Exports helpers used by devlink, shared-buffer, app, and vNIC code.

## Risks
Firmware policy handling is complex: multiple PFs/interfaces may share loading responsibility, and `unload_fw_on_remove` is intentionally conservative. Mailbox command polling can timeout or race if firmware does not clear command state. Probe unwind must match every successful allocation. SR-IOV disable refuses assigned VFs, leaving hardware enabled but driver state partially constrained.

## Test Signals
PF probe/remove/shutdown across supported PCI IDs, firmware found/not found/load-from-flash policies, reset policies, board initialization timeout, NSP unavailable, runtime symbol missing/small mailbox, SR-IOV enable over limit/disable with assigned VFs, flash update, and module init failure after PF driver registration but before VF driver registration.
