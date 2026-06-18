# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.h

## Purpose
`ste_dma40_ll.h` is the DMA40 low-level hardware definition header. It defines DMA40 register offsets, bit positions and masks for physical and logical standard channel parameters, LCPA/LCLA memory layout structures, physical and logical LLI structures, and prototypes for the LLI/register packing helpers implemented in `ste_dma40_ll.c`.

## Important APIs, Types, And Functions
Key definitions include global DMA register offsets such as `D40_DREG_GCC`, interrupt status/clear registers, logical channel status/clear registers, revision-specific extended registers, PrimeCell ID offsets, and per-channel standard register offsets (`D40_CHAN_REG_SSCFG`, `D40_CHAN_REG_SSELT`, `D40_CHAN_REG_SSPTR`, `D40_CHAN_REG_SSLNK`, destination equivalents). It also defines event grouping macros such as `D40_TYPE_TO_GROUP`, `D40_TYPE_TO_EVENT`, and `D40_PHYS_TO_GROUP`.

Important hardware-mapped structures are `struct d40_phy_lli`, `struct d40_phy_lli_bidir`, `struct d40_log_lli`, `struct d40_log_lli_bidir`, `struct d40_log_lli_full`, and `struct d40_def_lcsp`. `enum d40_lli_flags` defines address-increment, terminal-interrupt, cyclic, and last-link controls. Function prototypes expose physical/logical config and SG-to-LLI conversion plus LCPA/LCLA write helpers.

## Control Flow
There is no executable control flow. The macros directly shape control flow in the main driver: interrupt tables select registers from this header, allocation maps event groups and lines using its macros, channel command code reads/writes active and link registers using its offsets, and LLI writers use the bit masks to set next-link and element-count fields.

## State And Persistence
The header describes hardware and DMA-visible memory layouts. The structures are intentionally minimal and aligned because hardware reads them directly. State exists when instances are allocated by the main driver as descriptor LLIs or mapped to LCPA/LCLA memory; this header itself stores no state.

## Dependencies And Integration Points
It depends on `ste_dma40.h` through function prototypes using `stedma40_chan_cfg` and `stedma40_half_channel_info`, and on Linux scatterlist/DMA address types through prototypes. It is the integration point between C structures and DMA40 silicon register layout; changes here can affect probe initialization, interrupt handling, descriptor loading, power-management backup, and event-line control.

## Risks
Most constants are hardware contract values, so off-by-one or wrong mask changes are severe. The same bit positions are reused with different meanings in physical and logical modes, which increases maintenance risk. The logical `d40_log_lli` and full LCPA structures must remain exactly hardware-shaped; adding fields or changing alignment would corrupt DMA-visible layout. The many revision-specific register blocks require careful pairing with revision selection in `ste_dma40.c`.

## Test Signals
Validation should include compile-time structure-size/alignment expectations, register write/read traces from probe and descriptor load, interrupt status decoding on v4a and v4b tables, LCPA/LCLA layout checks, and hardware or emulated DMA tests that verify event group mapping and link traversal for physical and logical channels.
