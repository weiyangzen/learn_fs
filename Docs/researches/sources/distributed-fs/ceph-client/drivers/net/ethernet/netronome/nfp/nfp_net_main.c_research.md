# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_main.c

## Purpose

`nfp_net_main.c` is the PF-side NFP netdev entry point. It maps firmware runtime symbols, allocates and initializes PF data vNICs and optional control vNICs, starts the selected NFP application, registers devlink resources and debugfs, allocates IRQs, tracks physical port table changes, and cleans everything up on PCI remove.

## Important APIs, Types, and Functions

Important exported functions are `nfp_net_get_mac_addr()`, `nfp_net_lr2speed()`, `nfp_net_speed2lr()`, `nfp_net_refresh_port_table_sync()`, `nfp_net_refresh_port_table()`, `nfp_net_refresh_eth_port()`, `nfp_net_pci_probe()`, and `nfp_net_pci_remove()`. Local helpers allocate/free/init/clean vNICs, distribute IRQs, map/unmap BAR-like CPP areas, start/stop app control vNICs, update ETH-table port state, and schedule asynchronous port refresh work.

## Control Flow

PF probe requires a runtime symbol table, reads max data vNIC count, maps data vNIC control memory, optional MAC stats, VF config tables, and queue-controller memory, validates firmware ABI/class, determines queue stride, allocates/initializes the app, registers shared buffers and devlink params, creates debugfs, allocates vNIC objects from consecutive CSR slices, allocates/distributes IRQ vectors, starts the app/control vNIC/SR-IOV state, initializes data vNICs, then registers devlink. Remove reverses the sequence: unregister devlink, clean/free data vNICs, stop app/control vNIC, remove debugfs/devlink params, unregister shared buffers, free IRQs/app, unmap memory, and cancel refresh work.

## State and Persistence Behavior

The file mutates `struct nfp_pf` fields for mapped areas, vNIC lists, vNIC count, app pointer, control vNIC, IRQ entries, debugfs dentry, shared port refresh work, MAC stats memory, VF config memory, and port lists. It updates `struct nfp_net` BAR pointers, IDs, app/port pointers, queue stride, and data-vNIC lifecycle. It writes CFG BAR link-rate mirror values based on NSP ETH-table speed.

## Dependencies and Integration Points

It integrates with nfpcore CPP/runtime symbols, NFP NSP ETH tables, NFFW/MIP data, `nfp_app` lifecycle, devlink, shared-buffer registration, NFP port helpers, SR-IOV app hooks, core `nfp_net_init()`/`nfp_net_clean()`, MSI-X allocation helpers, and debugfs.

## Risks and Edge Cases

Probe has many partial-failure labels; cleanup ordering must avoid leaked CPP areas, devlink locks, debugfs dentries, vNICs, IRQs, and app resources. ETH-table refresh can mark ports invalid and unregister vNICs, so callers must hold the devlink lock and use RTNL around port state. Firmware ABI version checks gate queue stride and VF isolation. Empty vNIC lists are treated as remove races in refresh.

## Test Signals

PF probe/remove tests should cover missing symbol table, unsupported firmware ABI, missing optional MAC/VF symbols, control-vNIC app requirement, multiple data vNICs, IRQ scarcity, invalid ETH-table overrides, port refresh work, SR-IOV enabled at start, and repeated bind/unbind with lockdep/KMEMLEAK enabled.
