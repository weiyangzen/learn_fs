# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/ravb.h

## Purpose
This header defines the Renesas Ethernet AVB driver's register map, descriptor ABI, queue constants, PTP state, hardware-variant capability table, private netdev state, MMIO helpers, and cross-file prototypes shared by `ravb_main.c` and `ravb_ptp.c`.

## Important APIs, Types, And Functions
- Register ABI: `enum ravb_reg` names AVB-DMAC, E-MAC, gPTP, interrupt, MDIO, GbEth checksum, and counter registers.
- Bit definitions: enums such as `CCC_BIT`, `CSR_BIT`, `GCCR_BIT`, `ECMR_BIT`, `RIS*_BIT`, `TIS_BIT`, `ECSR_BIT`, `CSR0/1/2_BIT`, and many queue/interrupt masks encode hardware operations.
- Descriptor types: `struct ravb_desc`, `struct ravb_rx_desc`, `struct ravb_ex_rx_desc`, and `struct ravb_tx_desc` model base, normal Rx, timestamped Rx, and Tx descriptors.
- Queue and timestamp state: `enum RAVB_QUEUE`, `struct ravb_tstamp_skb`, `struct ravb_ptp_perout`, and `struct ravb_ptp` track BE/NC queues, pending Tx timestamp skbs, and PHC state.
- Variant table: `struct ravb_hw_info` carries function pointers and feature flags for receive path, rate setting, feature programming, DMAC/EMAC init, stats strings, descriptor sizes, maximum frame sizes, queue support, gPTP support, interrupt layout, WoL, internal delay, and GbEth checksum behavior.
- Main state: `struct ravb_private` stores platform/netdev pointers, clocks, MDIO bitbang control, descriptor base table, Tx/Rx rings, page pools, stats, timestamp controls, NAPI structs, work item, PHY state, feature flags, reset control, and computed GTI increment.
- Inline helpers and prototypes: `ravb_read()`, `ravb_write()`, `ravb_modify()`, `ravb_wait()`, `ravb_ptp_interrupt()`, `ravb_ptp_init()`, and `ravb_ptp_stop()`.

## Control Flow
The header itself is declarative, but it sets the contracts that drive AVB control flow. `ravb_main.c` selects a `ravb_hw_info` entry from the device-tree compatible string, then calls through its function pointers for variant-specific DMAC, EMAC, receive, rate, and feature operations. Descriptor definitions and `NUM_RX_QUEUE`/`NUM_TX_QUEUE` guide ring allocation, while PTP structures are initialized and consumed by `ravb_ptp.c`.

## State And Persistence
All state is runtime state. `ravb_private` persists for the lifetime of the registered netdev and carries hardware state mirrors such as ring indices, timestamp mode, speed/duplex/link, WoL enablement, delay-mode booleans, and computed `gti_tiv`. Hardware register writes persist only until reset or reconfiguration. No file-backed persistence is present.

## Dependencies And Integration Points
The header depends on Linux netdevice, interrupt, IO, MDIO bitbang, PHY, platform device, PTP clock, and page-pool types. It is the internal integration point between `ravb_main.c` and `ravb_ptp.c`, and between AVB netdev operations and Renesas hardware variants such as R-Car Gen2/Gen3/Gen4, RZ/V2M, and RZ/G2L GbEth.

## Risks And Edge Cases
- Register and bit definitions are hardware ABI; incorrect offsets or reserved-bit masks can break multiple SoC generations.
- `struct ravb_hw_info` flags must match descriptor format and interrupt layout; mixing GbEth normal descriptors with R-Car extended timestamp descriptors would corrupt DMA handling.
- Descriptor DMA addresses are stored in 32-bit descriptor fields, so DMA mask/platform assumptions must remain aligned with hardware capability.
- PTP and timestamp controls share `priv->lock` and descriptor state with data path code; changes must preserve locking and memory barriers.
- The `rx_1st_skb` field is global in `ravb_private`, so multi-fragment receive assumptions are sensitive to queue concurrency and currently used only by the GbEth receive path.

## Test Signals
Compile all compatible variants, verify `sizeof()` descriptor expectations, exercise BE-only and BE+NC queue paths, validate gPTP and non-gPTP builds, confirm register writes through `ravb_read()`/`ravb_write()`, test internal delay DT parsing on Gen3/Gen4, and run traffic with timestamp, checksum, ring-size, WoL, and PM operations enabled.
