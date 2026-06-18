# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.c

## Purpose
Implements the Microchip RDS PTP hardware clock and MII timestamper support used by the LAN887x T1 PHY path. It registers a PHC, attaches `phydev->mii_ts`, programs the PHY 1588/PTP register blocks, services timestamp FIFO interrupts, and matches hardware TX/RX timestamps back to SKBs by PTP sequence ID.

## Important APIs, Types, And Functions
- Exported entry points are `mchp_rds_ptp_probe()`, `mchp_rds_ptp_top_config_intr()`, and `mchp_rds_ptp_handle_interrupt()`.
- Register access helpers translate clock-vs-port offsets through base addresses and selected MMD.
- PTP clock callbacks implement adjustment, read/set time, perout enable, and pin verification.
- MII timestamp callbacks implement TX/RX timestamping, hardware timestamp policy get/set, and ethtool timestamp info.
- Timestamp matching is split between TX SKB completion, RX SKB matching, and RX timestamp list retention.

## Control Flow
Probe allocates `struct mchp_rds_ptp_clock`, creates pin descriptors, registers the PHC, initializes TX/RX queues and RX timestamp list state, binds callbacks into `phydev->mii_ts`, marks default timestamping enabled, then initializes hardware. Initialization disables PTP/TSU, resets TSU state, configures latency correction, standalone operating mode, reference clock parameters, parser defaults, PTP versions, then reenables TSU and PTP.

`hwtstamp_set` maps user policy to parser layer bits, version filters, timestamp-enable registers, and one-step Sync insertion. It flushes stale queues, drains both hardware FIFOs, enables or disables PTP interrupts based on RX filtering, then stores active TX/RX policy. The interrupt handler repeatedly reads status, drains RX/TX FIFO entries, handles overflow by flushing, and completes or injects SKBs.

## State And Persistence
Runtime state lives in `struct mchp_rds_ptp_clock`: TX/RX SKB queues, RX timestamp list, timestamp policy, parser layer/version, PHC lock, RX timestamp spinlock, pin config, and event/perout ownership. Hardware state is in PHY MMD registers until reset or reconfiguration.

## Dependencies And Integration Points
Depends on phylib MMD access, `ptp_clock_register()`, MII timestamper APIs, PTP packet classification/parsing, SKB timestamp APIs, ethtool hardware timestamp configuration, and LAN887x interrupt masking from `microchip_t1.c`.

## Risks
- `mchp_get_pulsewidth()` can leave the pulse-width output unset for too-large `on` values.
- RX sequence extraction pushes `ETH_HLEN` and has early failure paths that need validation for SKB pointer restoration.
- Software queues have no timeout aging beyond FIFO flushes and policy resets.
- Matching by PTP sequence ID alone can be ambiguous across simultaneous flows.

## Test Signals
Build with `CONFIG_MICROCHIP_PHY_RDS_PTP`, validate `ethtool -T`, run two-step and one-step `ptp4l`, exercise RX/TX FIFO overflow interrupts, and verify perout pin 3 duty-cycle behavior.
