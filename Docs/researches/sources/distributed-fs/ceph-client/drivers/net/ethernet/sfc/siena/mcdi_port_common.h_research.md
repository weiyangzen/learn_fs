# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port_common.h

## Purpose

`mcdi_port_common.h` declares the common MCDI PHY and MAC services shared by Siena port code. It is the contract between NIC type/ethtool/monitor paths and `mcdi_port_common.c`.

## Important APIs, Types, and Functions

The central type is `struct efx_mcdi_phy_data`, which stores firmware-discovered PHY flags, type, supported capabilities, MCDI channel/port, stats mask, name, media type, MMD mask, revision string, and currently forced capability word.

The declared API covers link advertising, PHY polling/probe/remove, ethtool link ksettings get/set, FEC get/set, PHY alive tests, port reconfiguration, PHY BIST and test names, module EEPROM/info reads, MAC reconfiguration, and MAC stats buffer init/fini.

## Control Flow and Integration

Callers usually probe PHY state once, then use the ethtool-oriented methods for user configuration and the poll/event methods for link state maintenance. `efx_siena_mcdi_port_reconfigure()` is the narrow runtime hook used when MAC/PHY mode, loopback, FEC, or advertisement state needs to be pushed to firmware. MAC stats init/fini are paired with the port lifecycle, while start/stop/pull stats are implemented in the C file and referenced through NIC type callbacks.

## State and Persistence Behavior

The header defines the shape of `efx->phy_data` for MCDI PHYs. Most APIs mutate long-lived `struct efx_nic` state and firmware link/MAC state. The header itself has no storage, but its functions assume that `efx->phy_data` is valid after successful probe and invalid after remove.

## Dependencies, Risks, and Test Signals

It includes `net_driver.h`, `mcdi.h`, and `mcdi_pcol.h`, so it exposes MCDI-specific details to its consumers. The major contract risk is lifetime: callers must not use link/FEC/module helpers before probe or after remove. Compile coverage should validate prototypes under ethtool and MCDI header changes; integration tests should pair every probe path with remove and exercise each declared ethtool operation.
