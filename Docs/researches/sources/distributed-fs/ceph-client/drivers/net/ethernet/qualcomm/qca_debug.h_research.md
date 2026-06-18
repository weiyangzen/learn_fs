<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h

## Purpose
`qca_debug.h` declares the debugfs and ethtool setup hooks for the QCA7000 SPI driver.

## Important APIs, Types, and Functions
- Includes `qca_spi.h` for `struct qcaspi`.
- Declares `qcaspi_init_device_debugfs()`, `qcaspi_remove_device_debugfs()`, and `qcaspi_set_ethtool_ops()`.

## Control Flow
No runtime flow exists in the header.

## State and Persistence
No state is owned here. The implementation uses `struct qcaspi` fields for debugfs and statistics.

## Dependencies and Integration Points
Used by `qca_spi.c` to install observability during netdev setup/probe and remove it during device removal.

## Risks and Edge Cases
The header includes the full SPI private header, tying debug declarations to SPI implementation details. Any future non-SPI QCA debug reuse would need a narrower interface.

## Test Signals
Successful QCA SPI build/link and installed ethtool ops on the netdev validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h -->
