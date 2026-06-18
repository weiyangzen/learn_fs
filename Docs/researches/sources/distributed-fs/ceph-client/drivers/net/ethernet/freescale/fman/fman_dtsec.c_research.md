# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_dtsec.c

## Purpose

`fman_dtsec.c` implements the 1G dTSEC MAC backend for FMan. It configures dTSEC registers, integrates with phylink and a TBI PCS, manages MAC address filtering and multicast hash tables, handles dTSEC and 1588 timestamp interrupts, and installs a `mac_device` operation table used by the surrounding DPAA Ethernet driver.

## Important APIs, Types, And Functions

The file defines the dTSEC register map (`struct dtsec_regs`), configuration structure (`struct dtsec_cfg`), and private MAC state (`struct fman_mac`). Initialization enters through exported `dtsec_initialization()`, which sets `mac_device` callbacks, creates the private object with `dtsec_config()`, finds the `tbi-handle` MDIO device, advertises supported phylink interfaces, and calls `dtsec_init()`.

Important operations include `dtsec_mac_config()`, `dtsec_link_up()`, `dtsec_link_down()`, `dtsec_select_pcs()`, `dtsec_modify_mac_address()`, `dtsec_add_hash_mac_address()`, `dtsec_del_hash_mac_address()`, `dtsec_set_promiscuous()`, `dtsec_set_allmulti()`, `dtsec_set_tstamp()`, and `dtsec_set_exception()`. Interrupt handlers are `dtsec_isr()` and `dtsec_1588_isr()`.

## Control Flow

`dtsec_initialization()` populates phylink and MAC callbacks, allocates/configures `struct fman_mac`, applies the global FMan max frame size, resolves an available TBI PCS node, and registers phylink interface capabilities based on device-tree mode and hardware capability bits. `dtsec_init()` optionally resets the MAC, validates configuration and callbacks, calls the low-level `init()` register programming routine, resets/configures the TBI control register, reports max frame length to FMan, allocates multicast/unicast hash tables, and registers error and normal interrupt callbacks with FMan.

At link-up, the driver programs pause behavior, speed bits, duplex and byte/nibble mode, calls `mac_dev->update_speed()`, enables RX/TX, and clears graceful stop bits. Link-down asserts graceful stop and disables RX/TX. Address changes stop the MAC gracefully, write station address registers, and restart.

## State And Persistence Behavior

Private state stores the MMIO register pointer, MAC address, phy interface, callbacks, hash tables, exception mask, PTP flags, TBI MDIO device, PCS wrapper, and saved FMan revision. Hash entries are allocated in software lists and mirrored into dTSEC hash registers. Exception state is kept in `dtsec->exceptions` and the hardware `imask`. Runtime link state persists in hardware registers until reconfigured by phylink callbacks.

## Dependencies And Integration Points

The file depends on `fman.h`, `fman_mac.h`, and `mac.h`, plus Linux phylink/PHY/MDIO, CRC32, bit reversal, OF MDIO, IO, and delay APIs. It integrates upward through `mac_device` callbacks and downward through FMan interrupt registration and max-frame validation. `tbi-handle` in device tree is mandatory for PCS access.

## Risks And Edge Cases

The dTSEC errata paths are timing-sensitive and include a documented race in the TX FIFO underrun workaround. Hash programming depends on CRC-derived buckets; bucket collisions are tracked in software lists so removal must preserve bits until a bucket is empty. The driver rejects unicast hash operations when group hash translation is active. This snapshot contains apparent compile-breaking anomalies: duplicated `tdfr` member in `struct dtsec_regs`, an extra brace after `check_init_parameters()`, and a duplicated `dtsec->exceptions &= ~bit_mask;` line.

## Test Signals

Build tests should catch the malformed struct/braces. Runtime tests should cover SGMII/1000BASE-X/2500BASE-X PCS selection, RGMII/RMII mode programming, link-up/down register effects, pause frame configuration including illegal FMan v2 pause time, multicast/unicast hash add/delete collisions, allmulti/promiscuous toggles, timestamp enable and 1588 error interrupts, and error interrupt callback mapping for all enabled dTSEC events.
