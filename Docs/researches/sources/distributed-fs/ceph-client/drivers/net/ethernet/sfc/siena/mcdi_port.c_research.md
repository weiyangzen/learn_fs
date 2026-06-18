# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.c

## Purpose

`mcdi_port.c` is the Siena driver's small port-facing wrapper around Management Controller Driver Interface (MCDI) PHY and MAC services. It wires Linux MDIO callbacks to firmware MDIO commands, checks MAC fault state through `MC_CMD_GET_LINK`, and sequences port probe/remove by delegating the heavy PHY and MAC statistics work to `mcdi_port_common.c`.

## Important APIs, Types, and Functions

The local MDIO callbacks `efx_mcdi_mdio_read()` and `efx_mcdi_mdio_write()` translate `struct mii_bus`-style read/write requests into `MC_CMD_MDIO_READ` and `MC_CMD_MDIO_WRITE` RPCs. Both populate bus, port address, device address, register address, and optionally value fields with `MCDI_SET_DWORD`, then require a firmware status of `MC_CMD_MDIO_STATUS_GOOD`.

Exported driver entry points are `efx_siena_mcdi_mac_check_fault()`, `efx_siena_mcdi_port_probe()`, and `efx_siena_mcdi_port_remove()`. The check-fault path treats any failed `GET_LINK` command as a fault. Probe installs the MDIO callbacks in `efx->mdio`, calls `efx_siena_mcdi_phy_probe()`, and then allocates MAC stats state with `efx_siena_mcdi_mac_init_stats()`. Remove calls `efx_siena_mcdi_phy_remove()` and `efx_siena_mcdi_mac_fini_stats()`.

## Control Flow

Port initialization starts in the NIC type's `probe_port` callback. This file first exposes a Clause 45/Clause 22-emulated MDIO surface backed by the management controller, then asks the common MCDI PHY layer to discover PHY configuration, link state, loopback modes, advertised capabilities, and default flow-control/FEC settings. Only after PHY state exists does it initialize the MAC stats DMA buffer.

Port teardown is straight-line and assumes higher-level code has quiesced the port: PHY private state is freed and the stats buffer is released. There is no local locking here; callers rely on the core driver lifecycle and `mac_lock` sequencing used by the common port layer.

## State and Persistence Behavior

This file mutates `efx->mdio.mode_support`, `mdio_read`, `mdio_write`, and the state created by delegated PHY/stat helpers. MDIO transactions are not cached; every read/write is a firmware RPC. MAC fault state is also read directly from firmware. Persistent resources created through probe include PHY private data and the coherent DMA stats buffer, but ownership is in `efx->phy_data` and `efx->stats_buffer` rather than this file.

## Dependencies and Integration Points

Dependencies include `mcdi.h`/`mcdi_pcol.h` for command encoding, `net_driver.h` for `struct efx_nic`, `mcdi_port_common.h` for the actual PHY and stats implementation, and the Linux MDIO/netdev interfaces. It integrates with ethtool, monitor, link reconfiguration, and stats paths indirectly through the common helpers it initializes.

## Risks and Test Signals

Failure handling is deliberately conservative: failed `GET_LINK` means MAC fault, and MDIO bad status maps to `-EIO`. Probe has an ordering risk: if MAC stats initialization fails after PHY probe succeeds, this function returns the error without calling `efx_siena_mcdi_phy_remove()`, so callers or future edits should verify unwind ownership. Useful tests are MCDI fault injection for MDIO status and RPC errors, probe/remove leak checks, ethtool MDIO access through supported PHYs, and link fault reporting during firmware reset.
