# Research: subset-b-004695

Grouped source research for the Linux PHY library subset under `sources/distributed-fs/ceph-client/drivers/net/phy`. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy-core.c

Purpose: Provides the core PHY utility layer used by phylib and PHY drivers: link speed/duplex/rate-matching stringification, RGMII delay-mode adjustment, interface fanout metadata, device-tree policy parsing, pause/autoneg resolution, downshift detection, generic MMD access, register modify helpers, and safe paged-register access.

Important APIs and functions: `phy_speed_to_str()`, `phy_duplex_to_str()`, and `phy_rate_matching_to_str()` translate core enums for diagnostics. `phy_fix_phy_mode_for_mac_delays()` reconciles RGMII delay modes with MAC-provided internal delays. `phy_interface_num_ports()` maps a `phy_interface_t` to the number of logical ports it can carry. `phy_set_max_speed()` and internal `__set_phy_supported()` clamp PHY and per-port supported link modes. `of_set_phy_supported()`, `of_set_phy_eee_broken()`, and `of_set_phy_timing_role()` apply DT properties. `phy_resolve_aneg_linkmode()`, `phy_resolve_aneg_pause()`, `phy_check_downshift()`, and `phy_speed_down_core()` derive runtime link outcomes from local and partner advertisements. `mmd_phy_read()`, `mmd_phy_write()`, `__phy_read_mmd()`, `phy_read_mmd()`, `__phy_write_mmd()`, and `phy_write_mmd()` abstract Clause 45 and Clause 22 indirect MMD access. `phy_modify*()` and `phy_modify_mmd*()` implement read-modify-write helpers. `phy_save_page()`, `phy_select_page()`, `phy_restore_page()`, `phy_read_paged()`, `phy_write_paged()`, and `phy_modify_paged*()` manage paged PHY registers under the MDIO bus lock.

Control flow: Most entry points are synchronous helpers. Capability clamping walks global link-capability mappings and any `phy_port` instances. DT helpers return early when OF MDIO is disabled or no node exists. Autoneg resolution intersects `phydev->lp_advertising` with `phydev->advertising`, picks the fastest or slowest matching capability depending on caller intent, then updates `phydev->speed`, `duplex`, `pause`, and downshift indicators. MMD helpers choose direct Clause 45 transactions for C45 PHYs and otherwise program `MII_MMD_CTRL`/`MII_MMD_DATA` for indirect access. Paged helpers lock the bus, save/select a page, perform an unlocked register operation, restore the original page, and propagate the earliest meaningful error.

State and persistence: The file mutates runtime fields in `struct phy_device`: supported and advertising bitmaps, per-port supported masks, EEE disabled modes, master/slave preference, negotiated speed/duplex, pause flags, `downshifted_rate`, and page selection through driver callbacks. It owns no durable persistence, but it enforces MDIO bus locking for multi-register sequences and preserves the previous page after paged accesses.

Dependencies and integration points: Depends on `linux/phy.h`, `linux/phy_port.h`, OF helpers, `phylib.h`, `phylib-internal.h`, and `phy-caps.h`. It integrates with PHY driver optional callbacks (`read_mmd`, `write_mmd`, `read_page`, `write_page`), MDIO bus primitives, device-tree bindings such as `max-speed`, `eee-broken-*`, and `timing-role`, and higher-level users in `phy.c`, `phy_device.c`, and package helpers.

Risks: The build-time assertion in `phy_speed_to_str()` must be updated when ethtool link modes change. MMD address validation uses boundary checks and driver overrides; mistakes can hit wrong MMDs. Clause 22 indirect MMD sequences require correct bus locking by callers. Paged helpers must always call `phy_restore_page()` after `phy_save_page()`/`phy_select_page()` or the bus lock and page state can leak. DT max-speed and EEE broken masks can silently remove advertised capabilities if bindings are wrong.

Test signals: Compile after adding link modes or interface modes; exercise C22 indirect and C45 direct MMD reads/writes; inject read/write/page callback failures and verify lock release; validate `max-speed`, EEE broken properties, and timing role DT parsing; test RGMII delay-mode combinations; verify downshift warnings and speed-down advertisement changes across autonegotiated links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy.c

Purpose: Implements the active PHY control framework: link state machine, interrupt handling, autonegotiation start/restart, ethtool operations, MII ioctls, cable tests, PLCA, loopback, EEE, Wake-on-LAN, pause configuration, and helper paths for MAC drivers to start/stop and observe PHY link state.

Important APIs and functions: `phy_print_status()`, `phy_get_rate_matching()`, `phy_restart_aneg()`, `phy_aneg_done()`, `phy_check_valid()`, `phy_ethtool_ksettings_get()` and `phy_ethtool_ksettings_set()` expose link settings. `phy_mii_ioctl()`, `phy_do_ioctl()`, and `phy_do_ioctl_running()` implement MII and PHY hardware timestamp ioctls. `phy_trigger_machine()`, `phy_start_machine()`, `phy_stop_machine()`, `phy_state_machine()`, `phy_start()`, `phy_stop()`, `phy_mac_interrupt()`, and `phy_error()` drive lifecycle. `phy_request_interrupt()`, `phy_free_interrupt()`, `phy_disable_interrupts()`, and the threaded `phy_interrupt()` integrate IRQ mode. `phy_start_cable_test()`, `phy_start_cable_test_tdr()`, PLCA get/set/status helpers, ethtool stats helpers, EEE helpers, WOL helpers, `phy_loopback()`, `phy_speed_down()`, and `phy_speed_up()` cover optional PHY services.

Control flow: Link management is centered on `phydev->state`. `phy_start()` resumes the PHY, marks it `PHY_UP`, and schedules the delayed work. `_phy_state_machine()` runs under `phydev->lock`: `PHY_UP` triggers `_phy_start_aneg()`, `PHY_NOLINK` and `PHY_RUNNING` call `phy_check_link_status()` and driver stats updates, `PHY_CABLETEST` polls driver cable-test status, and `PHY_HALTED`/`PHY_ERROR` force link down and request suspend work after unlocking. Polling PHYs reschedule according to the driver-provided update time or `PHY_STATE_TIME`; interrupt-driven PHYs rely on IRQ or MAC interrupt triggers. Ettool setting changes update advertised masks, master/slave and MDIX control, then either restart the running state machine from `PHY_UP` or configure autoneg immediately. Cable tests allocate ethtool notification state, force carrier down, enter `PHY_CABLETEST`, and return to `PHY_UP` when complete or aborted. EEE updates can trigger a synthetic link down/up to inform the MAC when only LPI state changed.

State and persistence: Mutates runtime link state in `phydev`: `state`, `link`, `speed`, `duplex`, `pause`, `asym_pause`, `lp_advertising`, `advertising`, `adv_old`, `autoneg`, `master_slave_set/get/state`, MDIX, EEE active/config flags, `enable_tx_lpi`, `loopback_enabled`, `interrupts`, `irq_suspended`, `irq_rerun`, `link_down_events`, and netdev testing/carrier state. State is in-memory only, but delayed work, IRQ threads, and ethtool calls coordinate through `phydev->lock` and workqueue cancellation.

Dependencies and integration points: Depends on netdevice, ethtool netlink, MDIO/MII, SFP, workqueue, PM sleep, timestamping, and PHY driver callbacks such as `config_aneg`, `read_status`, `handle_interrupt`, `config_intr`, `get_stats`, `cable_test_*`, `get/set_plca_*`, `get/set_wol`, `get_rate_matching`, `config_inband`, and `update_stats`. It calls generic helpers in `phy-core.c` and `phy_device.c`, netdev carrier APIs, LED trigger updates, ethtool cable-test notifications, and MII timestamp providers.

Risks: State transitions are lock-sensitive; callers that bypass locking or trigger work after detach can race with delayed work. The MII ioctl path writes raw registers and can desynchronize phylib-managed state if used carelessly. Interrupt handling during suspend defers work and disables IRQs until resume, so missed reruns would strand link state. Cable-test paths must always free notification state and clear `netif_testing`. `phy_speed_down(sync=false)` is explicitly risky for suspend if autoneg completion IRQs wake the system. EEE noneg updates intentionally bounce link notifications, which can surprise MAC drivers if they do not tolerate rapid carrier changes.

Test signals: Link up/down under polling, PHY IRQ, and MAC-interrupt modes; start/stop/detach with pending work; suspend/resume with wake IRQ rerun; ethtool link setting changes for autoneg and forced 10/100/1000; MII ioctl read/write/reset paths; cable test success, failure, and abort; PLCA validation failures; EEE enable/disable and LPI timer changes; WOL callbacks; loopback enable/disable and speed changes; injected MDIO and driver callback errors leading to `PHY_ERROR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c

Purpose: Maintains a normalized mapping between ethtool link modes and PHY speed/duplex capabilities, then provides lookup, validation, conversion, max-speed filtering, interface capability, and medium/pair filtering helpers for the rest of phylib.

Important APIs and functions: `phy_caps_init()` initializes the static `link_caps` table from `link_mode_params`. `phy_caps_speeds()` returns distinct supported speeds. `phy_caps_lookup_by_linkmode()` and `phy_caps_lookup_by_linkmode_rev()` choose fastest or slowest matching capabilities. `phy_caps_lookup()` matches speed/duplex against a supported mask with exact or fallback behavior. `phy_caps_linkmode_max_speed()` removes modes above a speed limit. `phy_caps_valid()` checks if a speed/duplex pair exists in a linkmode set. `phy_caps_linkmodes()` expands internal `LINK_CAPA_*` bitmasks to ethtool link modes. `phy_caps_from_interface()` maps PHY interface modes to possible speeds. `phy_caps_medium_get_supported()` and `phy_caps_mediums_from_linkmodes()` translate between media/pair metadata and linkmode masks.

Control flow: At module init, `phy_caps_init()` iterates every ethtool link mode, checks pair-count consistency, converts speed/duplex to an internal capability slot, and sets that linkmode bit. Lookup helpers then scan the resulting table in ascending or descending speed order. Medium filtering walks `link_mode_params`, keeping special non-medium bits and including modes whose medium and pair constraints match.

State and persistence: The `link_caps` array is marked `__ro_after_init`; after initialization it is effectively read-only kernel state. Helper functions mutate caller-provided linkmode bitmaps but maintain no per-device state.

Dependencies and integration points: Depends on `linux/ethtool.h`, `linux/linkmode.h`, `linux/phy.h`, and `phy-caps.h`. It is consumed by core helpers, port handling, generic PHY link status resolution, max-speed DT policy, interface capability derivation, and PHY probing.

Risks: The internal `LINK_CAPA_*` enum must track every meaningful speed/duplex in `link_mode_params`; unknown non-`SPEED_UNKNOWN` entries make `phy_caps_init()` fail. Descending lookup semantics prefer full duplex at the same speed because of table order. Medium and pair calculations rely on ethtool metadata correctness. `phy_caps_from_interface()` must be updated when new PHY interface modes or aggregate interfaces appear.

Test signals: Boot/module init after ethtool link-mode changes; unit-style validation that known linkmodes map to expected speeds and duplexes; max-speed clamping for PHY and port masks; interface-to-capability checks for RGMII, SGMII, USXGMII, Base-X, 10G/25G/50G/100G modes; medium/pair filtering for BaseT 1/2/4-pair and fiber modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_device.c

Purpose: Provides PHY device discovery, creation, registration, driver binding, attach/detach to net devices, PM integration, generic PHY driver implementations, SFP and port setup, LED class-device setup, sysfs attributes, fixup infrastructure, fwnode lookup helpers, ethtool PHY op registration, and phylib module initialization/exit.

Important APIs and functions: Device lifecycle APIs include `phy_device_create()`, `get_phy_device()`, `phy_device_register()`, `phy_device_remove()`, `phy_device_free()`, `phy_get_c45_ids()`, `phy_find_next()`, `phy_connect_direct()`, `phy_connect()`, `phy_disconnect()`, `phy_attach_direct()`, and `phy_detach()`. Driver registration uses `phy_drivers_register()` and `phy_drivers_unregister()`. Fixups are registered through `phy_register_fixup_for_uid()` and `phy_register_fixup_for_id()`. PM and wake helpers include `phy_may_wakeup()`, `phy_suspend()`, `__phy_resume()`, `phy_resume()`, and MDIO bus PM callbacks. Generic PHY helpers include `genphy_read_abilities()`, `genphy_config_aneg()` via `__genphy_config_aneg()`, `genphy_restart_aneg()`, `genphy_update_link()`, `genphy_read_status()`, `genphy_c37_*()`, `genphy_soft_reset()`, `genphy_suspend()`, `genphy_resume()`, `genphy_loopback()`, pause/EEE helpers, and property helpers. SFP/port/topology helpers include `phy_get_sfp_port()`, `fwnode_mdio_find_device()`, `fwnode_phy_find_device()`, and `fwnode_get_phy_node()`.

Control flow: Module init registers the MDIO class and bus, installs ethtool PHY ops and phylib stubs, initializes capability tables and feature masks, then registers generic Clause 45 and Clause 22 PHY drivers. Bus scanning uses Clause 22 ID reads or Clause 45 devices-in-package probing, then allocates `struct phy_device` with default state and requests matching driver modules. Registration adds the MDIO device, deasserts reset, runs fixups, and publishes the device. Driver probe sets `phydev->drv`, disables unsupported IRQ mode, runs driver probe/configuration, reads supported modes, applies DT limits and timing/EEE policy, builds ports and optional SFP upstreams, registers LED triggers and OF LEDs, then sets state `PHY_READY`. Attach takes device and module references, binds generic drivers if needed, sets `attached_dev`, link topology, sysfs links, interface and IRQ mode, initializes hardware, resumes, and may add PM device links. Detach reverses timestamp provider, topology, sysfs, driver/module references, reset, and device references. Generic autoneg writes advertisement registers, master/slave control, EEE advertisement, restarts negotiation, and status readers update link, LPA, speed, duplex, pause, and master/slave state.

State and persistence: Owns global feature masks (`phy_basic_features`, `phy_gbit_features`, EEE masks), the global fixup list, generic driver instances, phylib stubs, and module-level bus/class registration. Per-device state includes `phy_id`, C45 IDs, `supported`, `advertising`, EEE masks/config, `state`, `irq`, `drv`, `attached_dev`, `phylink`, `sfp_bus`, `ports`, `leds`, sysfs-link flags, `is_genphy_driven`, `is_internal`, `is_gigabit_capable`, `suspended`, `suspended_by_mdio_bus`, `wol_enabled`, topology `phyindex`, PM links, and driver private side effects. Hardware-visible persistence includes reset line state, PHY register programming, and driver-created LED/SFP resources until explicit teardown.

Dependencies and integration points: Integrates with Linux device model, MDIO bus core, module autoloading, netdevice, rtnetlink/RCU timestamp provider handling, PM runtime/system sleep, SFP bus, PSE control, LED framework, OF/fwnode properties, ethtool PHY ops, phylib stubs, link topology xarray helpers, and PHY driver callbacks (`probe`, `remove`, `get_features`, `config_init`, `config_intr`, `suspend`, `resume`, `soft_reset`, LED ops, SFP port ops, attach port ops). It uses helpers from `phy-core.c`, `phy.c`, `phy_caps.c`, `phy_port.c`, and `phy_link_topology.c`.

Risks: Probe and attach have many staged resources and require exact reverse cleanup to avoid leaked refs, sysfs links, LED class devices, SFP upstreams, topology nodes, or reset-state mismatches. Generic driver fallback manually assigns `d->driver`, probes, and binds, so module reference handling is delicate. Clause 45 probing has vendor-MMD exceptions and can misdetect noncompliant PHYs. `phy_detach()` reads the bus before `put_device()` to avoid use-after-free, highlighting lifetime sensitivity. PM suspend must stop the state machine before inaccessible PHY operations to avoid deadlocks, and WOL policy prevents some suspends. OF LED setup depends on driver LED callbacks; partial failures must unregister earlier LEDs. Port setup can shrink `phydev->supported` based on active ports and SFP compatibility, making incorrect firmware descriptions user-visible.

Test signals: MDIO bus scan for C22, C45, zero-ID fallback, and absent devices; device register/remove error unwinds; driver registration validation; attach/detach with generic and specific drivers; netdev sysfs link creation before and after netdev kobject readiness; PM suspend/resume with and without WoL; SFP insert/remove and incompatible module handling; OF `mdi` ports and default port creation; LED trigger and OF LED registration failures; generic autoneg forced/autoneg modes, master/slave conflicts, link status latched-low behavior, EEE support/disable; module init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c

Purpose: Provides legacy PHY LED trigger support that exposes one link trigger and one trigger per supported speed, then updates those triggers when link speed changes.

Important APIs and functions: `phy_led_trigger_change_speed()` is called by link-up/link-down paths to set LED trigger state. `phy_led_triggers_register()` allocates and registers the per-PHY trigger set. `phy_led_triggers_unregister()` unregisters and frees those triggers. Static helpers map speeds to triggers, turn all triggers off when no link exists, format trigger names as `bus:addr:suffix`, and register/unregister individual `led_trigger` objects.

Control flow: Registration asks `phy_supported_speeds()` for distinct speeds from `phydev->supported`, creates the `link` trigger, allocates speed triggers, registers each speed trigger using the human-readable speed string, initializes `last_triggered`, and calls `phy_led_trigger_change_speed()` to reflect current link state. On speed changes, no-link clears the previous speed and link triggers; link-up finds the matching speed trigger, enables the link trigger if this is the first active speed, disables the previous speed trigger when speed changes, and enables the new speed trigger.

State and persistence: Mutates `phydev->phy_num_led_triggers`, `phy_led_triggers`, `led_link_trigger`, and `last_triggered`. Trigger registrations persist in the LED subsystem until unregistered. No durable state is stored.

Dependencies and integration points: Depends on `linux/leds.h`, `linux/phy.h`, `linux/phy_led_triggers.h`, netdevice logging, and `phy_supported_speeds()` from internal phylib. It is called from PHY probe/remove and from `phy_link_up()`/`phy_link_down()` in the state machine.

Risks: Registration unwind must unregister only successfully created triggers and free both link and speed arrays. If current `phy->speed` is not represented in the registered speed list, the code logs an alert and turns triggers off. `phy->attached_dev` is used for alert logging, so calls before attachment would need care. Trigger names depend on MDIO bus ID/address and speed string stability.

Test signals: Probe/remove with zero, one, and many supported speeds; allocation or registration failure at each stage; link down clearing LEDs; speed transitions between supported modes; unsupported speed alert path; repeated register/unregister cycles during driver reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_led_triggers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c

Purpose: Maintains a per-netdev topology of PHY devices directly or indirectly attached to a MAC, including PHYs behind another PHY such as SFP module PHYs.

Important APIs and functions: `phy_link_topo_add_phy()` creates the topology container if needed, allocates a `phy_device_node`, records upstream relationship metadata, and assigns or reuses a stable `phyindex`. `phy_link_topo_del_phy()` removes a PHY from the topology xarray and frees its node. Static `netdev_alloc_phy_link_topology()` initializes `struct phy_link_topology` and its xarray.

Control flow: Adding a PHY lazily creates `dev->link_topo`, fills `pdn->phy`, stores either upstream netdev or upstream PHY based on `enum phy_upstream`, captures parent SFP bus when applicable, records upstream type, then inserts by existing `phy->phyindex` or allocates cyclically from index 1. Deletion erases by `phy->phyindex` and intentionally leaves that index on the PHY for reuse if the same object is later reattached.

State and persistence: Mutates `dev->link_topo`, the topology xarray, `next_phy_index`, and `phy->phyindex`. State is in-memory per netdev and persists across detach/reattach of the same PHY object until the netdev topology is destroyed elsewhere.

Dependencies and integration points: Depends on `linux/phy_link_topology.h`, `linux/phy.h`, RTNL assumptions, xarray allocation, and SFP helpers. It is called from `phy_attach_direct()`, `phy_detach()`, SFP connect/disconnect upstream ops, and user-visible topology consumers such as ethtool netlink.

Risks: The file includes `rtnetlink.h` but does not assert RTNL in these helpers; callers must serialize topology updates. A failed insert must free the node. Leaving `phyindex` set after deletion is intentional, but stale indexes can collide if a different node is inserted at the same ID before reuse. Topology lifetime for `dev->link_topo` must be handled by netdev core or other owners outside this file.

Test signals: Attach first PHY to a netdev with no topology; add nested SFP PHYs; detach and reattach same PHY to verify index reuse; allocation and xarray insertion failure; invalid upstream type; multiple PHYs on one netdev with stable unique indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_link_topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c

Purpose: Provides shared state and package-relative register access for multi-PHY packages, such as quad PHY transceivers that expose shared global registers and package-level private data.

Important APIs and functions: `phy_package_get_node()` and `phy_package_get_priv()` return package DT node and shared private storage. `__phy_package_read()`, `__phy_package_write()`, `__phy_package_read_mmd()`, and `__phy_package_write_mmd()` access C22/C45 registers at `base_addr + addr_offset`. `phy_package_init_once()` and `phy_package_probe_once()` provide per-package one-shot flags. `phy_package_join()`, `of_phy_package_join()`, `phy_package_leave()`, `devm_phy_package_join()`, and `devm_of_phy_package_join()` manage shared package membership and lifetime.

Control flow: `phy_package_join()` validates base address, takes `bus->shared_lock`, allocates a `phy_package_shared` entry in `bus->shared[base_addr]` on first use, optionally allocates shared private memory, sets refcount to one, or increments an existing entry when `priv_size` matches. `of_phy_package_join()` derives the package node from the PHY DT parent named `ethernet-phy-package`, reads its `reg` as base address, joins, and stores the node pointer. `phy_package_leave()` drops a DT node reference if present, decrements the shared refcount under the bus lock on last user, clears the bus slot, frees private memory, and nulls `phydev->shared`. Devm variants allocate a devres pointer and call leave automatically.

State and persistence: Maintains `struct phy_package_shared` instances referenced from each member `phydev->shared` and from `mii_bus->shared[base_addr]`, with `base_addr`, `np`, `refcnt`, `flags`, `priv_size`, and `priv`. Shared private data is runtime-only and driver-managed for locking. One-shot flags persist for the package lifetime.

Dependencies and integration points: Depends on OF, `linux/phy.h`, internal MDIO/MMD helpers from `phylib.h`, and bus-level `shared_lock`/`shared[]`. PHY drivers call these helpers during probe/config init to coordinate package-global initialization and register access.

Risks: All members of a package must use the same base address and private size; mismatches fail. Package-relative address bounds reject offsets that exceed `PHY_MAX_ADDR`, but callers must know the package map. Shared `priv` has no built-in locking beyond allocation/refcounting. `of_phy_package_join()` stores the package node and `phy_package_leave()` drops references for each member, so reference handling depends on balanced joins/leaves. MMD helpers assume the whole package is either C22 or C45.

Test signals: Join first and subsequent package members; mismatched `priv_size` and invalid base address failures; devm cleanup on probe failure; DT package node success and bad parent/name/reg failures; one-shot init/probe flags across multiple members; package-relative C22 and C45 register reads/writes at valid and invalid offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c

Purpose: Implements PHY port objects that describe physical media-side or MII-side ports, parse firmware connector metadata, derive supported link modes from media/pair/interface data, restrict media choices, and expose a netdev `PORT_*` type.

Important APIs and functions: `phy_port_alloc()` and `phy_port_destroy()` allocate/free `struct phy_port`. `phy_of_parse_port()` parses an `ethernet-connector.yaml`-style DT node into a port, including `media` and BaseT `pairs`. `phy_port_update_supported()` derives or filters `port->supported`. `phy_port_restrict_mediums()` masks medium support and updates link modes. `phy_port_get_type()` returns `PORT_TP`, `PORT_FIBRE`, or `PORT_OTHER`.

Control flow: DT parsing reads a medium string, converts it to an ethtool medium, validates BaseT pair counts as 1, 2, or 4, rejects `pairs` for non-BaseT media, then returns a populated port. Supported-mode update first infers missing `pairs` from already-set supported link modes, then accumulates medium-compatible link modes for every medium bit. If `port->supported` is empty it adopts that mask; otherwise it intersects existing support with medium support. For MII/SFP-style ports without medium data, it derives internal `LINK_CAPA_*` from every set PHY interface mode and expands those to link modes. Restricting mediums rejects an empty result and filters supported modes to the remaining media.

State and persistence: Mutates each `phy_port`'s list node, `supported` bitmap, `mediums`, `pairs`, `interfaces`, `is_mii`, `is_sfp`, parent pointers, and active/not-described flags set by callers. No global state or durable persistence exists.

Dependencies and integration points: Depends on OF/fwnode properties, ethtool medium and pair metadata, `linux/phy_port.h`, and `phy-caps.h`. It is used by `phy_device.c` when parsing `mdi` child nodes, creating default ports, setting up SFP ports, and aggregating port capabilities back into `phydev->supported`.

Risks: Firmware descriptions directly constrain advertised PHY modes; bad `media` or `pairs` values can make probe fail or overly restrict support. `phy_port_update_supported()` preserves manual bits only if they intersect derived support, so call order with PHY driver attach hooks matters. SFP/MII support depends on `port->interfaces` being populated by a driver or SFP flow. `phy_port_restrict_mediums()` prevents empty media sets but can still remove needed modes when passed the wrong mask.

Test signals: Parse valid BaseT 1/2/4-pair and invalid pair values; parse unsupported medium strings; reject `pairs` on non-BaseT; derive supported modes from medium/pairs and from MII interface lists; restrict mediums success and empty-result failure; integration with PHY probe aggregation and `phydev->port` selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h

Purpose: Declares private phylib interfaces shared between implementation files but not exposed as the primary public PHY API.

Important APIs and types: Forward-declares `struct mdio_device` and `struct phy_device`; exposes `mdio_bus_type` and `mdio_bus_class`; declares internal helpers `phy_supported_speeds()`, `of_set_phy_supported()`, `of_set_phy_eee_broken()`, `of_set_phy_timing_role()`, `phy_speed_down_core()`, `phy_check_downshift()`, `mdiobus_register_device()`, `mdiobus_unregister_device()`, and `genphy_c45_read_eee_adv()`.

Control flow: The header has no executable flow. It forms the compile-time contract that lets `phy.c`, `phy-core.c`, `phy_device.c`, `phy_led_triggers.c`, and package/device registration code call helpers that remain internal to the PHY library implementation.

State and persistence: Owns no state. The declared bus/class globals are defined elsewhere and persist for the phylib module lifetime after `phy_init()`.

Dependencies and integration points: Included by implementation files needing cross-file internal helpers. It intentionally avoids pulling in heavy headers by using forward declarations.

Risks: Prototype drift between this header and implementations can break multiple phylib objects. Because these helpers are internal, moving declarations to public headers would widen ABI/API surface unintentionally. Bus/class globals must remain initialized before users rely on them.

Test signals: Full phylib build coverage; module init/exit for bus/class availability; compile tests after changing helper signatures or moving internal functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h

Purpose: Declares phylib-internal-but-shared helpers for PHY package management and low-level MMD access used across PHY implementation files and drivers compiled in the PHY subsystem.

Important APIs and types: Forward-declares `struct device_node`, `struct phy_device`, and `struct mii_bus`. Declares package accessors, package-relative C22 and MMD read/write helpers, one-shot package init/probe flags, explicit and devm package join/leave functions, OF package join helpers, and `mmd_phy_read()`/`mmd_phy_write()`.

Control flow: The header itself has no runtime flow. It provides the shared contract implemented by `phy_package.c` and `phy-core.c`, allowing PHY drivers and implementation files to join packages and perform package/global register accesses.

State and persistence: Owns no state. Its functions operate on runtime `phydev->shared`, `mii_bus->shared[]`, and MDIO hardware registers owned by implementation files and callers.

Dependencies and integration points: Included by `phy-core.c`, `phy_package.c`, and package-aware PHY drivers. It bridges package helpers to generic MDIO/MMD helpers without including full implementation details of `struct phy_package_shared`.

Risks: The header exposes unlocked `__phy_package_*` helpers, so callers must follow the same locking expectations as raw `__phy_read()`/`__phy_write()`. Prototype changes can break package-aware drivers. Because the shared package struct is opaque, callers must use accessors and cannot verify internal lifetime except through balanced join/leave calls.

Test signals: Build package-aware PHY drivers; join/leave and devm cleanup paths; direct and package-relative MMD access on C22 and C45 PHY packages; compile tests after signature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phylib.h -->
