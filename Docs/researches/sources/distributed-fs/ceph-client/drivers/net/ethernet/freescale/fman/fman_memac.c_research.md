# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_memac.c

## Purpose

`fman_memac.c` implements the mEMAC backend for FMan, supporting 1G/2.5G/10G-oriented interfaces, PCS selection, optional SerDes control, MAC filtering, pause configuration, interrupt handling, phylink integration, and ethtool statistics.

## Important APIs, Types, And Functions

The file defines `struct memac_regs`, `struct memac_cfg`, and private `struct fman_mac`. Exported entry is `memac_initialization()`. The `mac_device` callbacks installed include `memac_set_promiscuous()`, `memac_modify_mac_address()`, `memac_add_hash_mac_address()`, `memac_del_hash_mac_address()`, `memac_set_exception()`, `memac_set_allmulti()`, `memac_set_tstamp()`, `memac_enable()`, `memac_disable()`, and ethtool stat readers.

Phylink operations are `memac_get_caps()`, `memac_select_pcs()`, `memac_prepare()`, `memac_mac_config()`, `memac_link_up()`, and `memac_link_down()`. Interrupt callbacks are `memac_err_exception()` and `memac_exception()`.

## Control Flow

`memac_initialization()` normalizes legacy XGMII to 10GBASE-R, installs callbacks, allocates/configures private state, creates named PCS handles for XFI/QSGMII/SGMII with compatibility fallback, optionally obtains a SerDes PHY, derives supported interface masks, applies SoC-specific half-duplex restrictions, defaults in-band autonegotiation when appropriate, and calls `memac_init()`.

`memac_init()` validates callbacks, optionally performs software reset, writes the primary MAC address, initializes command config/max-frame/pause/interrupt registers, applies an RX FIFO corruption erratum for FMan 6.0/6.3 by disabling CRC forwarding, validates max frame length with FMan core, allocates hash tables, and registers error/normal FMan interrupt callbacks. Link-up configures pause, IF_MODE speed/duplex, TX FIFO sections for 10G or 1G speeds, notifies `update_speed()`, and enables RX/TX. Link-down disables RX/TX.

## State And Persistence Behavior

Private state tracks register base, MAC address, callbacks, hash tables, exception mask, FMan revision, PCS handles, optional SerDes, allmulti flag, and RGMII half-duplex restriction. Hash state is software-list based for multicast only; unicast hash adds are rejected. Etthool stat functions read 64-bit counters by sampling high/low/high until stable.

## Dependencies And Integration Points

This file depends on FMan core APIs, shared MAC helpers, generic `mac_device`, phylink, Lynx PCS, Linux PHY/SerDes APIs, fixed PHY support, and OF MDIO/property helpers. It integrates with FMan by calling `fman_get_revision()`, `fman_get_max_frm()`, `fman_set_mac_max_frame()`, and interrupt registration APIs.

## Risks And Edge Cases

PCS fallback behavior is compatibility-sensitive when `pcs-handle-names` is absent. Optional SerDes affects supported interface discovery; without SerDes, only the default interface is assumed supported. `memac_enable()` must unwind `phy_init()` if `phy_power_on()` fails, which it does. Hash delete does not warn if an address was missing. The normal interrupt path masks with `MEMAC_ALL_ERRS_IMASK`, so magic-packet notification handling deserves scrutiny because the comment and mask naming focus on error bits. This snapshot has an apparent extra brace after `memac_config()`, which a build should catch.

## Test Signals

Build tests should catch syntax anomalies and all optional PHY/PCS configurations. Probe tests should cover named PCS handles, unnamed fallback, missing PCS, deferred PCS, optional SerDes success/failure, and machine-compatible half-duplex restrictions. Runtime tests should exercise link-up/down for MII/RGMII/SGMII/QSGMII/10GBASE-R, 10G TX FIFO settings, multicast hash collisions/allmulti transitions, pause stats, RMON and IEEE stats, SerDes power sequencing, and mEMAC exception callback mapping.
