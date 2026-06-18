# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.h

## Purpose
This header is the main LAN743x hardware and driver-state contract. It defines PCI IDs, CSR offsets and bit fields for MAC/RFE/DMAC/interrupt/PTP/SGMII/OTP/EEPROM/statistics blocks, channel counts, descriptor formats, ring state structures, adapter state, and cross-file function prototypes.

## Important APIs, Types, and Constants
Major constants include `DRIVER_NAME`, chip IDs for LAN7430/LAN7431/A011/A041, `ID_REV_IS_VALID_CHIP_ID_`, interrupt bits and vector flags, channel counts, max frame size, DMA descriptor spacing, TX/RX descriptor bit fields, and register offsets for all hardware blocks.

Important types are `struct lan743x_csr`, `struct lan743x_vector`, `struct lan743x_intr`, `struct lan743x_tx`, `struct lan743x_rx`, `enum lan743x_sgmii_lsd`, and `struct lan743x_adapter`. The adapter ties together netdev, mdiobus, PCI device, CSR state, interrupts, GPIO, PTP, MAC address, TX/RX rings, SGMII/syslock state, feature flags, phylink, and timestamp filter. Prototypes export CSR access, Hearthstone syslock, flow control, SGMII reads, and timestamp mode configuration to ethtool/PTP code.

## Control Flow and State
The header has no executable control flow, but it defines the state machine inputs used by `lan743x_main.c`: DMAC channel states, interrupt vector semantics, TX frame assembly flags, RX process results, and SGMII link-speed-duplex states. Ring structures store DMA-coherent descriptor bases, writeback head pointers, last head/tail indexes, NAPI instances, and skb bookkeeping.

## Dependencies and Integration Points
It includes phylink, phy, and `lan743x_ptp.h`, so it forms the bridge between the main driver, ethtool, PTP, GPIO, phylink, and MDIO logic. Register definitions must match the hardware manuals and the read/write sequences in `lan743x_main.c` and `lan743x_ethtool.c`.

## Risks
This file centralizes many bit masks and offsets; mistakes can silently program the wrong hardware block. Structure layout changes affect allocation and runtime behavior across multiple C files. `LAN743X_USED_*` compile-time constants limit enabled queues and have build-time guards against max values. Descriptor bit definitions and `DEFAULT_DMA_DESCRIPTOR_SPACING` must stay aligned with hardware requirements.

## Test Signals
Compile coverage catches missing declarations. Runtime validation comes from successful probe across supported device IDs, correct register dumps, working TX/RX ring operation, interrupt mode transitions, PTP and WOL behavior, SGMII mode setup, and statistics reads from the defined offsets.
