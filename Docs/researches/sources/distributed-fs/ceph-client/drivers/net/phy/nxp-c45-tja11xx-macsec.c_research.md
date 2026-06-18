# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx-macsec.c

## Purpose
This file implements MACsec offload support for NXP Clause 45 TJA11xx PHYs that expose an embedded MACsec engine. It bridges Linux `macsec_ops` to vendor MMD registers for SecY, TX/RX SC, TX/RX SA, keys, packet number handling, statistics, PN wrap interrupts, and the adapter TLV tag insertion required by the hardware.

## Important APIs, Types, and Functions
Private MACsec state is represented by `struct nxp_c45_macsec`, which owns a SecY list and bitmaps for active SecYs and allocated TX SC slots. `struct nxp_c45_secy` tracks the kernel `macsec_secy`, optional RX SC, SA list, hardware SecY id, and RX SC0 point-to-point implementation flag. `struct nxp_c45_sa` tracks a TX or RX SA, AN, hardware key bank A/B, and register layout.

Register helpers `nxp_c45_macsec_read()` and `nxp_c45_macsec_write()` map 32-bit MACsec registers onto 16-bit MDIO VEND2 accesses. The exported entry points used by the C45 core are `nxp_c45_macsec_probe()`, `nxp_c45_macsec_config_init()`, `nxp_c45_macsec_remove()`, and `nxp_c45_handle_macsec_interrupt()`. The kernel-facing `nxp_c45_macsec_ops` table implements the full add/update/delete lifecycle for SecY, RXSC, RXSA, TXSA, stats, open/stop, and TX tag insertion.

## Control Flow
Probe allocates the MACsec state, initializes the SecY list, and installs `phydev->macsec_ops`. Config-init enables MACsec and adapter functions, configures the adapter, sets the PN wrap threshold, and installs an MKA pass-through filter for PAE EtherType. Adding a SecY validates MAC address uniqueness, slot availability, and hardware point-to-point constraints, then selects the SecY slot, writes TX SCI and TX filters, updates TX SC config, enables PN wrap IRQs if valid, and links the object into software state.

Opening a SecY enables its TX filter, optional RX SC, RX SC0 mode, and global MACsec bypass when the first SecY becomes active. Stopping reverses that and disables global MACsec when no SecYs remain active. RXSC and RXSA callbacks program SCI, replay windows, validation mode, PN thresholds, keys, salt/SSCI for XPN, and active bits. TXSA callbacks program PN/key material and update the currently encoded SA when applicable. Deletion disables hardware entries, clears stats, frees list nodes, clears bitmaps, and clears global stats when all SecYs are gone.

Stats callbacks read 32-bit or split 64-bit counters into Linux MACsec stats structures. The interrupt handler reads `MACSEC_EVR`, maps the bit position to a SecY id, finds the active encoding SA, calls `macsec_pn_wrapped()`, acknowledges the event, and marks the parent IRQ handled.

## State and Persistence
Software state persists in `struct nxp_c45_phy::macsec` for the PHY lifetime. Hardware state persists in selected MACsec register banks and is selected by writing SecY id to RX/TX selector registers. SA allocation alternates key bank A/B and enforces at most two SAs per direction. Packet number state, replay lower PN, XPN salt/SSCI, and counters live in hardware and are synchronized by ops callbacks.

## Dependencies and Integration Points
The file depends on `<net/macsec.h>`, phylib MDIO helpers, `nxp-c45-tja11xx.h`, netdev MAC addresses, sk_buff headroom handling, ethtool netlink stats/cable constants, and the parent NXP C45 driver for ability detection and interrupt dispatch. It is compiled only when `CONFIG_MACSEC` enables the non-stub declarations from the header.

## Risks
Key and salt programming uses casts to `u32 *`, so alignment and endianness assumptions are important. SecY validity is constrained by hardware point-to-point and port-1 SCI rules; unsupported topologies return `-EINVAL` or `-EBUSY`. Bitmap/list state must remain synchronized with hardware selection registers. PN wrap interrupt handling depends on correct bit-to-SecY mapping and active SA lookup. Some read helpers ignore return values for stats, so MDIO failures can surface as stale or zeroed data rather than hard errors.

## Test Signals
Test MACsec offload add/update/delete for SecY, RXSC, RXSA, and TXSA; XPN and non-XPN keys; 128-bit and 256-bit keys; replay protection windows; port-1/end-station constraints; multiple SecY slot exhaustion; MKA pass-through; PN wrap notification; stats reads; TX TLV insertion headroom; module removal cleanup; and interrupt coexistence with link/PTP events.
