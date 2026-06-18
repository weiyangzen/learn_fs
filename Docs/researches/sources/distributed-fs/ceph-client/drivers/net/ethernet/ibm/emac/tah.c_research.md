
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.c

## Purpose
`tah.c` implements the IBM EMAC TAH helper block, used for checksum assist and transmit acceleration support. It provides a small platform driver that maps TAH registers, resets/configures the block, tracks users, and contributes register dumps to EMAC ethtool output.

## Important APIs, Types, and Functions
Public functions are `tah_attach()`, `tah_detach()`, `tah_reset()`, `tah_get_regs_len()`, `tah_dump_regs()`, `tah_init()`, and `tah_exit()`. `tah_probe()` allocates and initializes `struct tah_instance`, maps registers, stores drvdata, and calls `tah_reset()`.

## Control Flow
TAH probe resets the hardware immediately and logs initialization. EMAC probe attaches to the TAH phandle/channel, enabling EMAC features such as IP checksum and scatter-gather. EMAC configuration calls `tah_reset()` when TAH is present, so the assist block is reset alongside EMAC mode changes. Detach only decrements the user count. Register dumps copy the whole `struct tah_regs` block after an EMAC subheader.

## State and Persistence
State is minimal: mapped registers, mutex, user count, and platform device. Hardware mode register state is set to enable checksum verification and configure a 10KB TX FIFO with selected thresholds. There is no disk persistence.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO, and local EMAC register-dump framing. EMAC core uses TAH presence to enable `NETIF_F_IP_CSUM`, `NETIF_F_SG`, RX checksum marking, and TAH-specific TX/RX descriptor status interpretation.

## Risks
Attach/detach do not validate channel values beyond user tracking. Reset uses a tight polling loop and only logs timeout. TAH mode settings are hard-coded, including a comment that TSO is not enabled yet. Incorrect TAH presence can produce wrong checksum behavior.

## Test Signals
TAH probe logs, EMAC feature flags showing checksum/SG support, RX checksum-offload counters, TX checksum behavior, ethtool register dump inclusion, and reset timeout absence are useful signals.
