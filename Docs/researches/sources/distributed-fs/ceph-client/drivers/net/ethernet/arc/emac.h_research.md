# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac.h

## Purpose
This header defines ARC EMAC register IDs, bit masks, descriptor layout, ring sizes, private driver state, MMIO helpers, and exported probe/remove/MDIO hooks shared by the ARC EMAC core and platform glue.

## Important APIs, types, and functions
Register masks cover interrupt status/enables, control bits, descriptor ownership/status, and MDIO completion. `enum` register IDs map logical names to MMIO offsets. `struct arc_emac_bd` is the hardware buffer descriptor with `info` and DMA data pointer. `struct buffer_state` tracks skb and DMA mapping metadata. `struct arc_emac_mdio_bus_data` stores reset GPIO timing. `struct arc_emac_priv` holds device, MDIO bus, MMIO base, clock, NAPI, RX/TX rings, DMA handles, skb states, ring indices, link state, speed/duplex, and missed-error tracking. Inline helpers `arc_reg_set/get/or/clr` wrap MMIO access.

## Control flow
The header has only inline register helpers. `emac_main.c` uses them throughout probe, open, stop, interrupt, TX/RX, filtering, and restart paths. Platform glue initializes fields such as `drv_name`, `set_mac_speed`, and `clk` before calling `arc_emac_probe`.

## State and persistence
`arc_emac_priv` is per-netdev runtime state. RX/TX descriptors and skb mapping arrays persist for the device lifetime, with buffers allocated on open and freed on stop. Hardware state persists in MMIO registers and DMA rings.

## Dependencies and integration points
It includes Linux device, DMA, netdevice, PHY, and clock headers. It declares `arc_mdio_probe/remove` from `emac_mdio.c` and `arc_emac_probe/remove` exported by `emac_main.c` for SoC glue.

## Risks
Descriptor and DMA address fields assume hardware can consume the stored address width; the capability is for older ARC EMAC hardware. Ring sizes are fixed at 128. Register helper offsets multiply enum IDs by `sizeof(int)`, so enum ordering is the hardware ABI.

## Test signals
Build coverage across core and glue, probe on revision 5/7 hardware, DMA ring operation, PHY MDIO operation, and interrupt/TX/RX traffic validate the header contract.
