# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.c

## Purpose

`mcdi_port_common.c` implements the firmware-backed PHY, link, FEC, module EEPROM, cable test, MAC reconfiguration, MAC statistics, and link event handling used by Siena-style SFC devices. It translates Linux ethtool/netdev concepts into MCDI command payloads and keeps `struct efx_nic` link-related state synchronized with firmware.

## Important APIs, Types, and Functions

PHY discovery is centered on `efx_mcdi_get_phy_cfg()` and `efx_siena_mcdi_phy_probe()`, which fill `struct efx_mcdi_phy_data`, MDIO addressing, supported media, loopback mask, initial link state, advertising, FEC config, and default flow control. Runtime link paths include `efx_siena_mcdi_phy_poll()`, `efx_siena_mcdi_port_reconfigure()`, `efx_siena_mcdi_phy_get_link_ksettings()`, and `efx_siena_mcdi_phy_set_link_ksettings()`.

Capability conversion helpers include `mcdi_to_ethtool_linkset()`, `ethtool_linkset_to_mcdi_cap()`, `ethtool_fec_caps_to_mcdi()`, and `mcdi_fec_caps_to_ethtool()`. FEC public entry points are `efx_siena_mcdi_phy_get_fecparam()` and `efx_siena_mcdi_phy_set_fecparam()`. Test and module APIs include `efx_siena_mcdi_phy_test_alive()`, `efx_siena_mcdi_phy_run_tests()`, `efx_siena_mcdi_phy_test_name()`, `efx_siena_mcdi_phy_get_module_eeprom()`, and `efx_siena_mcdi_phy_get_module_info()`.

MAC-side APIs are `efx_siena_mcdi_set_mac()`, `efx_siena_mcdi_mac_init_stats()`, `efx_siena_mcdi_mac_fini_stats()`, plus local stats controls `efx_siena_mcdi_mac_start_stats()`, `efx_siena_mcdi_mac_stop_stats()`, and `efx_siena_mcdi_mac_pull_stats()`. Link-change events are decoded by `efx_siena_mcdi_process_link_change()`.

## Control Flow

PHY probe allocates `efx_mcdi_phy_data`, issues `GET_PHY_CFG`, then `GET_LINK`. If autonegotiation is active, firmware capabilities are converted into ethtool advertising; otherwise the forced capability word is saved. Probe validates loopback enum compatibility with compile-time checks, fetches supported loopbacks, decodes current speed/duplex/flow control, records an ethtool-representable FEC mode, and applies default wanted flow control through common link helpers.

Setting link ksettings converts requested autoneg advertisement or forced speed/duplex into an MCDI capability word, ORs in FEC bits derived from current `efx->fec_config`, applies PHY flags for TX-disable/low-power/off modes, and calls `MC_CMD_SET_LINK`. FEC setting follows the same pattern but recomputes the capability word from saved advertising or forced capability, validates that requested FEC maps to supported MCDI bits, updates firmware, and then persists `efx->fec_config`.

Module EEPROM reads identify SFP/QSFP media, calculate page count and starting page, read 128-byte pages with `GET_PHY_MEDIA_INFO`, and tolerate missing upper QSFP pages by zero-filling when appropriate. BIST starts a firmware test, polls up to 10 seconds, records pass/fail, and extracts SFT9001 cable diagnostics when available.

MAC reconfiguration builds `SET_MAC` with current MAC address, MTU-derived max frame length, unicast reject policy, RX-FCS inclusion, and flow control policy. MAC stats allocate a coherent DMA buffer and control periodic or one-shot firmware DMA through `MC_CMD_MAC_STATS`; pull waits briefly for a generation marker to change.

## State and Persistence Behavior

Persistent state includes `efx->phy_data`, `phy_type`, MDIO bus/port/mmd fields, `link_advertising`, `wanted_fc`, `fec_config`, `link_state`, `loopback_modes`, and `stats_buffer`. Firmware state includes link capabilities, PHY mode flags, loopback mode, MAC address/MTU/filter/flow-control settings, and periodic MAC stats DMA. Link-change events update `efx->link_state` outside `mac_lock` based on an explicit ordering assumption: polling only runs after event queues are flushed.

## Dependencies and Integration Points

This file depends heavily on `mcdi_pcol.h` command layouts, `efx_siena_mcdi_rpc*()` transports, ethtool link/FEC/module APIs, MDIO constants, common link helpers in `efx_common.h`, stats buffer helpers from `nic.c`, and `net_driver.h` state definitions. It is called from port probe, ethtool get/set operations, monitor polling, MAC reconfiguration, self-test, and event processing.

## Risks and Test Signals

Risk areas include capability translation drift as new ethtool link modes are added, ambiguous FEC combinations, firmware output-length compatibility, 25G/50G BASER vs RS semantics, and QSFP page read error handling. MAC stats pull is timing-sensitive and relies on the last stat word as a generation marker. Tests should cover autoneg and forced link settings, FEC get/set on 10/25/40/50/100G media, module EEPROM reads across SFP and QSFP variants, BIST polling timeout/failure, link-change events, MAC stats start/pull/stop, and MCDI error injection for short responses.
