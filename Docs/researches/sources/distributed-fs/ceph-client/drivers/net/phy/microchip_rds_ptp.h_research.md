# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_rds_ptp.h

## Purpose
Defines the Microchip RDS PTP register map, bit fields, driver state structures, and conditional public API used by `microchip_rds_ptp.c` and the LAN887x PHY driver.

## Important APIs, Types, And Constants
It declares clock/LTC, rate/step adjustment, parser, timestamp FIFO, interrupt, TSU, and perout register constants. `struct mchp_rds_ptp_clock` embeds the MII timestamper, PHC handles, queues, timestamp lists, parser policy, pin configuration, locks, and base addresses. `struct mchp_rds_ptp_rx_ts` carries RX FIFO timestamps until SKB matching. Public declarations are `mchp_rds_ptp_probe()`, `mchp_rds_ptp_top_config_intr()`, and `mchp_rds_ptp_handle_interrupt()`, with no-op/NULL stubs when disabled.

## Control Flow
No executable control flow beyond feature-gated inline stubs. Macro groups mirror hardware blocks consumed by the implementation.

## State And Persistence
The header declares in-memory state but performs no persistence. Hardware state represented by constants remains in PHY registers until reset.

## Dependencies And Integration Points
Includes PTP clock, PTP classification, network timestamping, MII, and PHY headers. Consumed by `microchip_t1.c` and `microchip_rds_ptp.c`.

## Risks
Offsets are added to caller-supplied clock/port base addresses, so incorrect bases corrupt unrelated registers. The disabled-config probe returns `NULL` while enabled failures often return `ERR_PTR()`. The full mutable clock struct is exposed to integration code.

## Test Signals
Build enabled and disabled `CONFIG_MICROCHIP_PHY_RDS_PTP` configurations and validate register-offset MDIO traces against hardware documentation.
