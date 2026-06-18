# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Kconfig

## Purpose
Defines staging Direct Digital Synthesis driver options.

## Important Entries and Integration
`AD9832` enables AD9832/AD9835 SPI DDS support. `AD9834` enables AD9833/AD9834/AD9837/AD9838 SPI DDS support. Both are tristate and depend on `SPI`; both expose direct access through sysfs.

## Risks and Test Signals
Dependencies match the SPI-only drivers. Kconfig tests should verify symbols appear under the DDS menu and modules are named `ad9832` and `ad9834`.
