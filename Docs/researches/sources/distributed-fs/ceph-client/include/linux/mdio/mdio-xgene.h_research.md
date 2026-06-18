<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h

## Purpose
This header defines register offsets, bitfield helpers, platform data, and exported routines for the AppliedMicro X-Gene MDIO controller.

## Important APIs, types, and functions
It declares CSR offsets for MAC, diagnostics, MDIO, management, reset/clock, and MIIM registers; bitfield positions/lengths; command enums; `enum xgene_mdio_id`; and `struct xgene_mdio_pdata` holding clocks, device, MMIO bases, bus, ID, and MAC lock. Inline helpers `xgene_enet_set_field_value()` and `xgene_enet_get_field_value()` back `SET_VAL`, `SET_BIT`, `GET_VAL`, and `GET_BIT`. Exported functions include MAC read/write, RGMII read/write, and PHY registration.

## Control flow
The X-Gene driver uses the platform data to access the correct CSR block, composes bitfields for MDIO commands, waits on busy/done indicators, serializes MAC register access with `mac_lock`, and registers PHY devices on the `mii_bus`.

## State and persistence
Runtime state is in MMIO registers, clock/reset state, bus registration, and the spinlock. PHY register state persists in hardware.

## Dependencies and integration points
It depends on bits, spinlocks, clocks, devices, IO memory, and phylib. It integrates X-Gene Ethernet MAC variants with MDIO/PHY infrastructure.

## Risks and test signals
Risks include duplicate macro definitions, incorrect bitfield width shifts, wrong CSR base for RGMII versus XFI, busy polling timeouts, and missing locking around MAC access. Test RGMII reads/writes, PHY registration, reset/clock enable, timeout handling, and concurrent MAC register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-xgene.h -->
