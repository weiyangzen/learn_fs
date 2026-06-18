# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.c

## Purpose
This file translates firmware PHY/link state into Linux ethtool state and translates ethtool link requests back into HWRM PHY configuration fields. It covers speed, lanes, media, signal mode, pause, FEC reporting, module status, and async link-event dispatch.

## Important APIs, Types, And Functions
Public functions include `bnge_init_ethtool_link_settings`, `bnge_probe_phy`, `bnge_hwrm_set_link_common`, `bnge_hwrm_set_pause_common`, `bnge_update_phy_setting`, `bnge_get_port_module_status`, `bnge_support_speed_dropped`, `bnge_report_link`, `bnge_get_link`, `bnge_get_link_ksettings`, `bnge_set_link_ksettings`, and `bnge_link_async_event_process`. Important internal helpers map firmware speed/media/signal values to ethtool modes and back.

## Control Flow
Probe queries PHY capabilities, updates link state, and initializes cached ethtool settings. Link update paths compare requested pause/speed/autoneg state against firmware-reported state, then call HWRM PHY configuration only when changes are needed. `get_link_ksettings` builds supported, advertising, link-partner, FEC, speed, duplex, lanes, and port values. `set_link_ksettings` validates autoneg or forced speed/lane combinations and applies them if the netdev is running.

## State And Persistence
The durable state is split between `bd->link_info`, which mirrors firmware qcfg/qcaps state, and `bn->eth_link_info`, which stores requested ethtool settings. Retry state for failed PHY updates lives in `link_info.phy_retry` and is driven by the netdev timer in `bnge_netdev.c`.

## Dependencies And Integration Points
The file depends on HSI link constants, `bnge_hwrm_lib.c` command wrappers, ethtool linkmode helpers, and netdev carrier state. Async events set bits in `bn->sp_event`; the service task later calls qcaps/qcfg and refreshes ethtool caches.

## Risks
Speed mapping is dense and hardware-generation specific, especially 50G through 800G with NRZ, PAM4 56G, PAM4 112G, media type, and lanes. Advertising masks collapse multiple ethtool media modes into firmware speed bits, so installed media priority matters. Unsupported lane/speed requests must fail without corrupting cached settings.

## Test Signals
Use `ethtool` get/set for autoneg, forced speeds, lanes, pause, and FEC display. Validate link up/down messages, carrier transitions, module warnings, link partner advertising, and async link-speed/config/status events. Hardware with different optics and DAC media is important coverage.
