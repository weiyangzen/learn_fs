# `sources/distributed-fs/ceph-client/include/linux/iio/buffer.h`

Purpose: public in-kernel IIO buffer API for pushing/popping scans, timestamp injection, scan-mask validation, and buffer attachment.

Important APIs/types/functions: `enum iio_buffer_direction`, `iio_push_to_buffers`, `iio_pop_from_buffer`, deprecated `iio_push_to_buffers_with_timestamp`, `iio_push_to_buffers_with_ts`, unaligned timestamp variant, `iio_validate_scan_mask_onehot`, and `iio_device_attach_buffer`.

Control flow and state: timestamp helpers check whether the IIO device scan includes a timestamp and write it to the final aligned slot before pushing. The safer `_with_ts` helper validates supplied storage length against `indio_dev->scan_bytes`.

Dependencies/integration: depends on IIO core, sysfs, device logging, and buffer implementations. Used by sensor drivers and triggered handlers.

Risks: undersized stack/sample buffers can corrupt memory if deprecated helper is used directly; timestamp offset assumes scan layout ending with `s64`; push/pop context requirements depend on buffer implementation.

Test signals: timestamp-enabled and disabled scans, undersized storage returning `-ENOSPC`, unaligned data path, one-hot scan mask validation, attached-buffer lifecycle, and triggered-buffer sample alignment.
