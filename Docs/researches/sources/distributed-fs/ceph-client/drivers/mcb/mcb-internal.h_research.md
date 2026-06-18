# sources/distributed-fs/ceph-client/drivers/mcb/mcb-internal.h

## Purpose
`mcb-internal.h` defines shared private constants and Chameleon descriptor layouts used by the MCB parser and carrier drivers.

## Important APIs, Types, and Functions
It defines MEN/Altera PCI IDs, `CHAMELEONV2_MAGIC`, `CHAM_HEADER_SIZE`, descriptor type and bus type enums, packed `chameleon_fpga_header`, `chameleon_gdd`, `chameleon_bdd`, and `chameleon_bar` structures, field extraction macros such as `GDD_IRQ()`, `GDD_DEV()`, `GDD_BAR()`, and `BAR_CNT()`, plus the parser prototype `chameleon_parse_cells()`.

## Control Flow, State, and Persistence
The header has no executable flow. Its layouts describe on-device FPGA Chameleon tables and therefore define how persistent hardware metadata is interpreted into runtime `mcb_bus` and `mcb_device` objects.

## Dependencies and Integration Points
It depends on Linux types and `linux/mcb.h` definitions such as `CHAMELEON_FILENAME_LEN`. It is included by `mcb-parse.c`, `mcb-pci.c`, and `mcb-lpc.c`.

## Risks and Test Signals
Risks include packed bitfield portability in `chameleon_bdd`, endian mistakes for GDD fields, incorrect BAR count sizing, and format drift if newer Chameleon versions appear. Tests should parse known descriptor blobs, validate little-endian extraction on non-x86 architectures, and build both PCI and LPC carriers.
