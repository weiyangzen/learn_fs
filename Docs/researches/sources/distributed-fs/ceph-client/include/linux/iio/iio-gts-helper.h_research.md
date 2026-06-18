<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h

Purpose: Defines helper data structures and APIs for IIO drivers that expose coupled gain, integration-time, and scale settings.

Important APIs/types/functions: `struct iio_gain_sel_pair` maps gain to hardware selector; `struct iio_itime_sel_mul` maps integration time to selector and multiplier; `struct iio_gts` stores max scale and sorted lookup tables. Macros `GAIN_SCALE_GAIN()` and `GAIN_SCALE_ITIME_US()` build tables. Helpers find gain/time selectors, validate gains/times, convert total gain to scale, choose replacement gains when integration time changes, and expose available times/scales.

Control flow: Drivers initialize `iio_gts` with `devm_iio_init_iio_gts()`, then call lookup/conversion helpers in `read_raw`, `write_raw`, and `read_avail` paths.

State/persistence: Helper state is immutable table metadata after initialization; actual hardware gain/time remains driver-owned.

Dependencies/integration: Uses device-managed lifetime and standard IIO value formats.

Risks: Tables must be sorted/consistent or scale selection can choose wrong hardware settings.

Test signals: Boundary gains/times, unavailable scale lists, nearest-low gain selection, and scale preservation across integration-time changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h -->
