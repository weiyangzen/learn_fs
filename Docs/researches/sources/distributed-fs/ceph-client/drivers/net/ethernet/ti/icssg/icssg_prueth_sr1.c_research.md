<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c

## Purpose

`icssg_prueth_sr1.c` is the AM654 SR1.0-specific ICSSG Ethernet platform driver. It reuses common ICSSG RX/TX/config/stat helpers but provides different firmware boot, shared-memory load-time config, command transport, management RX flows, timestamp handling, receive-mode programming, probe/remove, and netdev lifecycle for SR1 hardware.

## Important APIs, Types, and Functions

Key routines include `icssg_config_sr1()`, `emac_send_command_sr1()`, `icssg_config_set_speed_sr1()`, `emac_adjust_link_sr1()`, SR1 `emac_phy_connect()`, `prueth_process_rx_mgm()`, `prueth_tx_ts_sr1()`, management IRQ threads, SR1 `prueth_emac_start/stop()`, SR1 `emac_ndo_open/stop()`, `emac_ndo_set_rx_mode_sr1()`, SR1 `prueth_netdev_init()`, `prueth_probe()`, and `prueth_remove()`. It defines fixed SR1 firmware names and platform match data for `"ti,am654-sr1-icssg-prueth"`.

## Control Flow

Probe parses available ports, gets MII regmaps, PRUSS cores, shared RAM, an SRAM pool sized by `MSMC_RAM_SIZE_SR1`, both IEP instances, initializes IEPs, creates netdevs, registers them, and connects PHYs. Open clears shared memory on first port, sets classifier MAC/default state, creates TX, RX data, and RX management channels, requests IRQs for data RX, management responses, and management timestamps, boots PRU/RTU firmware for that slice, prepares RX buffers, enables DMA channels and NAPI, starts PHY, and queues stats work. Commands are sent as CPPI command packets on the highest-priority TX channel and completed by management response IRQs.

## State and Persistence Behavior

SR1 stores `struct icssg_sr1_config` in shared RAM per slice, including MSMC base address, RX flow IDs, management flow ID, buffer sizes, and random seed. It keeps an extra RX management channel and an extra TX management channel in `struct prueth_emac`. Unlike SR2, each port starts/stops its own PRU/RTU pair and there is no TX_PRU firmware in the SR1 firmware table.

## Dependencies and Integration Points

It depends on common `icssg_prueth.h` state, MII helpers, classifier helpers, K3 UDMA glue, CPPI descriptor pools, page pool helpers through common RX code, PHY/MDIO, remoteproc/pruss, genalloc SRAM, and IEP APIs. It uses shared ethtool ops and common TX/RX/stat/timestamp netdev callbacks where compatible.

## Risks and Edge Cases

`emac_send_command_sr1()` returns the raw `wait_for_completion_timeout()` value on success rather than normalizing to zero, which callers treat mostly as truthy/nonzero only in stop paths. `prueth_process_rx_mgm()` pushes replacement buffers through `emac->rx_chns` instead of `rx_mgm_chn`, which is worth checking against common helper expectations. Probe connects PHYs without checking `emac_phy_connect()` return in the success path. SR1 intentionally disables multi-TX-channel user exposure due to timeouts.

## Test Signals

Validate SR1 probe/remove, both-port and one-port configurations, command response IRQ completion for shutdown and speed/duplex commands, management timestamp IRQs, open/close loops, PHY speed transitions, multicast/promiscuous/allmulti receive-mode changes, TX queue timeout absence with one visible TX queue, and error unwinds for management IRQ/channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_prueth_sr1.c -->
