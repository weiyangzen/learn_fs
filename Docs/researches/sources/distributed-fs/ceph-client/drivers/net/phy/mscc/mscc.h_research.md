# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc.h

## Purpose
Provides shared register definitions, IDs, firmware metadata, private state structures, and cross-file function declarations for Microsemi/Microchip VSC85xx PHY support.

## Important APIs, Types, And Constants
Defines standard, extended, GPIO, CSR, token-ring, test-page, 1588, and MACsec page/register constants; supported PHY IDs; VDDMAC values; LED mode masks; firmware filenames/start addresses/CRCs; and processor command bits. `struct vsc8531_private` stores LED modes, stats, package addressing, optional MACsec state, MII timestamper, PTP state, GPIO, timestamp locks, and RX SKB wait list. Feature-gated declarations expose MACsec and PTP helpers or no-op stubs.

## Control Flow
No executable flow except inline stubs. Conditional sections allow core code to call optional MACsec/PTP hooks unconditionally.

## State And Persistence
The header defines per-PHY private state, package-shared GPIO lock state, optional MACsec flow lists/bitmaps, PTP locks/queues, and firmware metadata. Hardware state is represented through page/register macros.

## Dependencies And Integration Points
Included by MSCC core, SerDes, MACsec, and PTP implementation files. Integrates with phylib, `CONFIG_OF_MDIO`, `CONFIG_MACSEC`, and `CONFIG_NETWORK_PHY_TIMESTAMPING`.

## Risks
Page-specific macros can write wrong shared hardware if misused. Optional stubs can hide missing feature support unless capabilities are gated. PTP and MACsec members impose cross-file locking and lifetime constraints.

## Test Signals
Compile all feature combinations, probe single-port and multi-port packages, validate firmware CRC paths, test LED modes, MACsec offload, and PTP timestamping.
