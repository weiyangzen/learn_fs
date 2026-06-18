# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.c

## Purpose
`mv88e1xxx.c` implements the `gphy`/`cphy_ops` driver for Marvell 88E1xxx 10/100/1000 copper PHYs used by cxgb boards. It handles PHY reset, MDIO configuration, autonegotiation, speed/duplex advertisement, loopback, link-status decoding, downshift, LEDs, and interrupt routing through Elmer0.

## Important APIs, Types, and Functions
The exported factory is `const struct gphy t1_mv88e1xxx_ops`, with `mv88e1xxx_phy_create()` and a no-op chip reset. The `mv88e1xxx_ops` vtable provides reset, interrupt enable/disable/clear/handler, autoneg enable/disable/restart, advertise, loopback, set speed/duplex, and get link status. Helper functions `mdio_set_bit()` and `mdio_clear_bit()` perform read-modify-write on standard PHY registers. `mv88e1xxx_downshift_set()` configures downshift after failed gigabit attempts.

## Control Flow
Creation allocates a `struct cphy`, initializes it with MDIO ops and the vtable, applies special 88E1111 transmitter class-A configuration on supported twisted-pair boards, enables downshift, and programs an LED mode on T2. Per-port reset sets `BMCR_RESET` and polls for completion. Autoneg enable sets crossover auto and restarts negotiation; autoneg disable forces manual MDI crossover and clears autoneg with a restart as required by Alaska PHY behavior. Advertisement writes both gigabit control and base advertisement registers.

Interrupt enable writes the PHY interrupt mask and sets Elmer0 GPIO interrupt bits; disable clears both; clear reads the PHY interrupt status and writes Elmer0 cause bits. The handler loops until no enabled cause remains, updating `cphy->state` for link and autoneg readiness and returning `cphy_cause_link_change` when link status should be re-evaluated.

## State and Persistence
Runtime state lives in the PHY hardware registers and in `struct cphy->state`. Advertisement, speed/duplex, crossover, downshift, interrupt mask, loopback, and LED configuration persist in the PHY until reset. The driver does not persist settings outside hardware.

## Dependencies and Integration Points
The file depends on `common.h`, `mv88e1xxx.h`, `cphy.h`, and `elmer0.h`. It integrates with the generic link-management path through `t1_link_start()` and `t1_link_changed()`, with MDIO through `simple_mdio_read/write()`, with board detection through `board_info()`, and with Elmer0 for interrupt routing. `cxgb2.c` sees its results through `struct link_config` and netdevice carrier updates.

## Risks
The interrupt handler appears to test link up using the PHY specific status register but compares with an interrupt bit name; that logic is hardware-sensitive and should be treated carefully during maintenance. Disabling autoneg requires manual crossover behavior that is easy to regress. The MDIO helpers ignore read/write errors, so hardware failures may silently produce stale configuration. Elmer0 interrupt bit usage differs between T1 and T2 and must remain board-aware.

## Test Signals
Signals include PHY reset completion, autoneg enable/disable/restart, forced 10/100 and attempted 1000 behavior, advertisement masks, link up/down interrupts, downshift operation, loopback toggling, LED programming on T2, `ethtool` link setting changes, MII ioctl reads/writes, and link-status decoding for speed/duplex/pause.
