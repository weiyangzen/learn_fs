# sources/distributed-fs/ceph-client/net/mac802154/main.c

Purpose: provides mac802154 subsystem allocation, registration, default PHY setup, RX tasklet dispatch, and module init/exit.

Important APIs and functions: `ieee802154_alloc_hw()` allocates a `wpan_phy` with aligned `ieee802154_local` and driver-private memory, initializes queues, work items, tasklet, completion, supported ranges, and interface types. `ieee802154_configure_durations()` derives symbol/SIFS/LIFS durations from page/channel. `ieee802154_register_hw()` creates workqueues, registers the PHY, and creates default `wpan%d` node interface. `ieee802154_unregister_hw()` tears down tasklet, workqueues, interfaces, and phy registration.

Control flow and state: RX interrupt-safe packets are queued into `local->skb_queue`; `ieee802154_tasklet_handler()` drains only `IEEE802154_RX_MSG` packets to `ieee802154_rx()`. Registration establishes `local->workqueue` for TX, `local->mac_wq` for MAC-command/scan/beacon work, `ifs_timer`, and advertised capabilities based on hardware flags.

Dependencies and integration: integrates with `cfg.h`, cfg802154 `wpan_phy`, `ieee802154_if_add/remove`, tasklets, workqueues, RTNL, and exported driver API symbols.

Risks and test signals: registration has multi-step unwind paths; allocation requires valid driver ops. Tests should exercise failure injection for workqueue/PHY/interface creation, RX tasklet handling of invalid packet types, and duration calculation for supported channel pages.
