# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/intf.c

## Purpose
`intf.c` manages mlx4 auxiliary devices and event notifier dispatch for protocol subdrivers. It creates auxiliary devices for Ethernet and IB capabilities, registers/unregisters auxiliary drivers, rescans subdevices when the core device state or bonding mode changes, dispatches core events through an atomic notifier chain, and exposes devlink port access.

## Important APIs, Types, and Functions
Public APIs include `mlx4_adev_init()`, `mlx4_adev_cleanup()`, `mlx4_register_auxiliary_driver()`, `mlx4_unregister_auxiliary_driver()`, `mlx4_do_bond()`, `mlx4_dispatch_event()`, `mlx4_register_event_notifier()`, `mlx4_unregister_event_notifier()`, `mlx4_register_device()`, `mlx4_unregister_device()`, and `mlx4_get_devlink_port()`. Internal helpers are `is_eth_supported()`, `is_ib_supported()`, `adev_release()`, `add_adev()`, `del_adev()`, `add_drivers()`, `delete_drivers()`, and `rescan_drivers_locked()`. State is guarded by the global `intf_mutex` and auxiliary-device IDs are allocated by `mlx4_adev_ida`.

## Control Flow
`mlx4_adev_init()` allocates a unique auxiliary-device ID and the per-device auxiliary pointer array. `mlx4_register_device()` marks the interface up under `intf_mutex`, rescans supported auxiliary devices, unwinds on failure, and starts catastrophic-error polling. Rescanning deletes unsupported devices and adds supported missing devices based on current port types and IBoE capability. `mlx4_unregister_device()` stops catas polling, handles VF communication-channel error state during deletion, marks the interface down, and rescans to delete all auxiliary devices.

`mlx4_do_bond()` toggles bonded mode after checking port-remap support and programming RX port check or virtual-to-physical port map. It then locks the interface list, finds loaded auxiliary devices whose drivers advertise bonding support, skips SR-IOV multifunction devices, deletes and recreates those auxiliary devices so protocol drivers re-probe with the new bonding mode. Event notifier functions wrap `atomic_notifier_call_chain()` and notifier registration. Auxiliary driver registration delegates to the kernel auxiliary bus.

## State and Persistence
There is no filesystem persistence. Runtime state includes the global auxiliary IDA, `priv->adev_idx`, `priv->adev[]`, `dev->persist->interface_state`, `dev->flags` bonded bit, catastrophic polling state, auxiliary device lifecycle references, and registered notifier blocks. Auxiliary devices persist in the kernel device model until deleted/uninitialized and released.

## Dependencies and Integration Points
The file depends on the Linux auxiliary bus, IDA allocation, device model locking, devlink ports, atomic notifier chains, mlx4 core state, port capability fields, bonding flags, firmware helpers `mlx4_disable_rx_port_check()` and `mlx4_virt2phy_port_map()`, catastrophic error polling, and VF communication health handling. It is the bridge that lets mlx4 Ethernet and IB protocol drivers bind to the same PCI core device.

## Risks
Risks include auxiliary-device lifetime mistakes, rescanning while drivers are bound, global mutex ordering with device locks, partial add failure cleanup, bonded-mode reprobe behavior, SR-IOV restrictions during bonding, interface-state races during remove, and error-state transition if VF communication is already down. Support detection must stay aligned with port type and IBoE capability or subdrivers may fail to probe or remain loaded incorrectly.

## Test Signals
Important tests include registering/unregistering the core device with Ethernet-only, IB-only, mixed, and IBoE configurations; auxiliary driver bind/unbind paths; add failure injection and unwind; notifier registration and event dispatch; bonded mode enable/disable with bonding-capable and non-capable subdrivers; SR-IOV bonding refusal; VF deletion with communication error; repeated register/unregister cycles; and devlink port retrieval.
