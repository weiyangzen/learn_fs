# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.h

## Purpose
`sun4i-emac.h` defines the Allwinner A10 EMAC register offsets and bitfields used by `sun4i-emac.c`.

## Important APIs, types, and constants
- Register offsets cover controller control, TX mode/flow/control/FIFO/status, RX control/hash/status/FIFO/count, interrupts, MAC control/timing/frame length, MII clock, MAC address, and source-address filters.
- Bitfields define reset/TX/RX enable, DMA enable, RX acceptance/filter modes, interrupt enable/status bits, MAC duplex/CRC/padding/flow control, 100M speed selection, and MII clock divider.
- Helper macros `EMAC_RX_IO_DATA_LEN()` and `EMAC_RX_IO_DATA_STATUS()` extract RX FIFO header fields.
- `EMAC_EEPROM_MAGIC` and `EMAC_UNDOCUMENTED_MAGIC` document magic values used by legacy hardware/FIFO handling.

## Control flow and integration
The header has no executable control flow. The platform driver uses these constants for MMIO reads/writes in setup, TX, RX, IRQ, link updates, and power management.

## State and persistence behavior
All state is hardware register state and volatile FIFO/header data. The header itself stores no runtime state.

## Dependencies and integration points
It is a private companion to `sun4i-emac.c` and has no external dependencies beyond basic C preprocessing.

## Risks and edge cases
Incorrect register offsets or bit definitions affect hardware directly. The undocumented magic value is central to the RX FIFO resynchronization path; changing it would break recovery from FIFO desynchronization. Frame-length and RX status masks must match hardware encoding.

## Test signals
Compile the driver, validate register programming during probe/open/link changes, confirm RX header decoding, exercise interrupt status bits, and test FIFO flush behavior when the magic header is absent.
