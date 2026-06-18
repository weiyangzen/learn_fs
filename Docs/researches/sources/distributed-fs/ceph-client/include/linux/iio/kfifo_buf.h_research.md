<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h

Purpose: Declares IIO kfifo buffer allocation and managed setup helpers for software-visible buffered capture.

Important APIs/types/functions: `iio_kfifo_allocate()`, `iio_kfifo_free()`, `devm_iio_kfifo_buffer_setup_ext()`, and the shorter `devm_iio_kfifo_buffer_setup()` macro.

Control flow: Drivers allocate or devm-attach a kfifo buffer during probe; IIO core then uses setup ops and optional buffer attributes during buffer enable/disable and reads.

State/persistence: The actual FIFO buffer state is opaque and persists for the IIO device lifetime or until freed.

Dependencies/integration: Integrates IIO buffer core, device-managed cleanup, `iio_dev_attr` buffer attributes, and `iio_buffer_setup_ops`.

Risks: Wrong setup ops or scan configuration can mismatch FIFO sample layout.

Test signals: Probe/remove cleanup, buffer enable/disable callbacks, scan data ordering, and optional buffer attribute exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h -->
