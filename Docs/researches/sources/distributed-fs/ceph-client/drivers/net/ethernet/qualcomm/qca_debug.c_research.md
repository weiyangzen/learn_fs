<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c

## Purpose
`qca_debug.c` provides QCA7000 SPI driver debugfs and ethtool support. It exposes runtime SPI/netdev state, driver information, fixed link settings, statistics strings/data, selected SPI registers, and ring-parameter configuration.

## Important APIs, Types, and Functions
- `qcaspi_gstrings_stats[]` must match `struct qcaspi_stats` field order.
- Debugfs, when enabled, provides an `info` file under a directory named after the netdev device.
- Ettool callbacks include driver info, link ksettings, stats, strings, set count, register dump, and ringparam get/set.
- `qcaspi_set_ethtool_ops()` installs the ethtool ops on the netdev.

## Control Flow
Debugfs setup creates a directory and readonly info file; removal recursively deletes it. Ettool register dump reads selected SPI registers with `qcaspi_read_register()`. Ringparam update validates RX settings, parks the SPI thread if running, clamps TX pending between min and max, updates `txr.count`, and unparks the thread.

## State and Persistence
Debugfs state is `qca->device_root`. Ettool stats read `qca->stats` directly. Ring count changes persist in `qca->txr.count` until netdev teardown or another update.

## Dependencies and Integration Points
Depends on debugfs, ethtool, seq_file, `qca_7k.h`, and `qca_spi.h`. It is called from `qcaspi_netdev_setup()`, `qca_spi_probe()`, and `qca_spi_remove()`.

## Risks and Edge Cases
- Stats export relies on exact layout/order matching between strings and `struct qcaspi_stats`.
- Register dumping performs live SPI reads and can disturb error counters if SPI is failing.
- Ringparam update does not reallocate the fixed skb pointer array; it only changes active ring depth.
- Debugfs creation failures are ignored.

## Test Signals
`ethtool -i`, stats, register dump, ringparam get/set, debugfs `info`, and stable operation while changing TX ring size validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c -->
