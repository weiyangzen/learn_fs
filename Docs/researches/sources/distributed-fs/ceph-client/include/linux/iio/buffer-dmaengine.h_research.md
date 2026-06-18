# `sources/distributed-fs/ceph-client/include/linux/iio/buffer-dmaengine.h`

Purpose: convenience API for wiring IIO buffers to DMAengine channels.

Important APIs/types/functions: `iio_dmaengine_buffer_teardown`, `iio_dmaengine_buffer_setup_ext`, `iio_dmaengine_buffer_setup`, `devm_iio_dmaengine_buffer_setup_ext`, `devm_iio_dmaengine_buffer_setup_with_handle`, and `devm_iio_dmaengine_buffer_setup`.

Control flow and state: setup functions allocate/attach DMAengine-backed IIO buffers for input or output direction; devm variants bind teardown to device lifetime.

Dependencies/integration: depends on IIO buffer API, DMAengine channel handles, and device-managed resources.

Risks: wrong buffer direction breaks capture/output semantics; channel name/handle resolution failures must unwind; teardown must not race active DMA.

Test signals: named-channel setup, handle-based setup, IN and OUT directions, devm cleanup on probe failure/remove, and active stream teardown.
