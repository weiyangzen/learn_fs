# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_main.c

## Purpose
Provides module entry/exit and auxiliary-driver lifecycle for mlx4 Ethernet support. It validates module parameters, builds the per-device Ethernet profile, allocates mlx4 core resources shared by all Ethernet ports, registers event and netdev notifiers, creates one netdev per Ethernet port, and tears the device down on auxiliary remove.

## Important APIs, Types, and Functions
Module-level state includes parameters `udp_rss`, `pfctx`, `pfcrx`, and `inline_thold`, plus the `mlx4_en_adrv` auxiliary driver. Public helpers include `en_print` for per-port logging and `mlx4_en_update_loopback_state` for loopback feature propagation. Lifecycle functions are `mlx4_en_probe`, `mlx4_en_remove`, `mlx4_en_event`, `mlx4_en_get_profile`, `mlx4_en_verify_params`, `mlx4_en_init`, and `mlx4_en_cleanup`.

## Control Flow
Initialization verifies module parameters, initializes the mlx4-to-ethtool link-mode map, and registers an auxiliary driver named `mlx4_core.eth`. Probe allocates `mlx4_en_dev`, a protection domain, UAR, UAR mapping, and memory region, then derives the driver profile from module parameters and device capabilities. It counts Ethernet ports, sets default RX ring counts, creates a single-thread workqueue, marks the device up, registers the mlx4 event notifier, initializes netdevs for each Ethernet port, and registers a netdev notifier for bonding updates. Remove unregisters the event notifier, marks `device_up` false under `state_lock`, destroys every port netdev, destroys the workqueue, frees MR/UAR/PD resources, unregisters the netdev notifier, and frees `mdev`.

## State and Persistence Behavior
`struct mlx4_en_dev` is the main in-memory device container: core `mlx4_dev`, PCI device, DMA device, profile, UAR/PD/MR, workqueue, per-port netdev pointers, notifier blocks, and device-up state. Module parameters persist for the module lifetime and are copied into `mdev->profile`. Hardware resources such as PD, UAR, and MR persist until auxiliary remove. Loopback state updates per-port flags and, when supported, updates RX QPs through firmware source-check loopback controls.

## Dependencies and Integration Points
Depends on Linux module, auxiliary bus, netdevice, workqueue, memory mapping, and mlx4 core driver APIs. It integrates with `en_netdev.c` for per-port netdev creation/destruction and netdev notifier handling, `en_rx.c` for RX ring count selection, `en_resources.c` for loopback QP updates, and `en_ethtool.c` for PTYS map initialization.

## Risks
Probe has a staged resource allocation sequence; unwind labels must match the allocation order. Event handling queues link work rather than directly changing carrier, so queued work must be flushed before netdev memory is freed. Loopback update walks RSS QPs under `state_lock` and depends on valid `rss_map` state. Parameter validation mutates module parameter globals, so validation must run before profile creation.

## Test Signals
Module load/unload, auxiliary probe/remove, low-memory profile selection, invalid module parameter correction, UDP RSS disabled when unsupported, PFC parameter propagation, per-port netdev creation failure unwind, mlx4 event notifier link-up/link-down queuing, catastrophic event logging, and teardown with pending workqueue items are key validation signals.
