<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h

Purpose: shared private header for Honeywell HSC/SSC common core and bus adapters.

Important APIs, types, and functions: defines `HSC_REG_MEASUREMENT_RD_SIZE`, `HSC_RESP_TIME_MS`, callback type `hsc_recv_fn`, `struct hsc_data`, `struct hsc_chip_data`, `enum hsc_func_id`, and exported `hsc_common_probe()`. `struct hsc_data` contains device pointer, chip metadata, receive callback, validity flag, pressure conversion fields, scan buffer, and DMA-aligned raw buffer.

Control flow: bus adapters implement only the receive callback and call `hsc_common_probe()`. The core uses `hsc_chip_data` to validate measurements and expose channels.

State and persistence: describes in-memory runtime state only. There is no persistent storage. Buffer alignment supports DMA-capable buses.

Dependencies and integration points: depends on Linux types and IIO declarations. It is consumed by common, I2C, and SPI HSC driver files; exported namespace must match bus module imports.

Risks: shared state has no lock field, so bus/core users must account for concurrency elsewhere. The measurement size and scan layout are hard-coded for this sensor family. Conversion field types mix `s64` values with `s32` decimal remainders, so precision changes need ABI review.

Test signals: compile I2C/SPI/common together, validate callback prototype compatibility, static checking for buffer-size assumptions, and namespace import/export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h -->
