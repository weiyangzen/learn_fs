# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_main.c

Purpose: Core Prestera switch/netdev driver lifecycle. It registers devices from transport drivers, initializes switch subsystems, creates netdev ports, handles link events, LAG/upper-device notifications, multicast flood-domain objects, workqueues, and module lifecycle.

Important APIs/types/functions: Exported `prestera_device_register/unregister()`, workqueue helpers, port lookup helpers, port config helpers, LAG helpers, flood-domain/MDB helpers, and netdev identity helpers. Netdev ops implement open/stop/xmit/setup_tc/change_mtu/get_stats64/set_mac_address. Switch lifecycle is `prestera_switch_init/fini()`; port lifecycle is `prestera_port_create/destroy()`.

Control flow: Transport calls `prestera_device_register()`, which allocates devlink private switch state and runs switch init. Switch init initializes hardware, base MAC, netdevice notifier, router, switchdev, RX/TX, event handlers, counters, ACL, SPAN, devlink traps, LAG table, ports, then registers devlink. Port creation allocates an etherdev, reads firmware port IDs/caps, registers devlink port, sets MTU/MAC/MAC/PHY config, initializes RX/TX port state, registers netdev, and binds SFP phylink where device tree describes it. Teardown reverses setup.

State and persistence: Maintains switch port list under rwlock, base MAC, LAG table, OF node, per-port cached config/state/stats, delayed stat workers, phylink state, VLAN list, and pointers to ingress/egress flow blocks. State is runtime and firmware-backed, not persisted across module reload.

Dependencies/integration: Integrates almost every Prestera subsystem: hardware, ACL, flow, SPAN, RX/TX, devlink, ethtool, counter, switchdev, router, phylink, netdevice notifier, bridge, VLAN, and LAG kernel APIs.

Risks: Initialization and unwind ordering is critical because subsystems depend on earlier hardware and notifier setup. `prestera_lag_create()` tests `if (lag)` after a loop where `lag` will be non-NULL even when no free entry is found, so full-table handling depends on surrounding logic. Port SFP bind returns `err` even when no matching node is found; correctness relies on prior initialization along all loop paths. Link event code reads `port->state_mac.oper` after cache write instead of local `smac.oper`, relying on immediate cache consistency.

Test signals: PCI probe through device registration, all init error-injection unwind paths, netdev register/unregister, port open/close for copper and SFP/phylink, link up/down events and carrier changes, delayed stats, MTU/MAC validation, tc setup, bridge/LAG/VLAN upper device notifier behavior, multicast MDB flood-domain programming, and module load/unload leak checks.
