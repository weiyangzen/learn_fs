# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_buffer.c

Purpose: optional triggered-buffer implementation for the IIO simple dummy driver. It demonstrates how to push sampled data plus timestamps into an IIO buffer.

Important APIs/types/functions: `fakedata[]` maps `DUMMY_INDEX_*` scan indices to constant sample values. `struct dummy_scan` contains a fixed `s16` data array and aligned timestamp. `iio_simple_dummy_trigger_h()` is the threaded poll function handler. `iio_simple_dummy_configure_buffer()` wraps `iio_triggered_buffer_setup()`, and `iio_simple_dummy_unconfigure_buffer()` calls cleanup.

Control flow: when an IIO trigger fires, the handler allocates a DMA-safe scan object, copies values for active channels in scan order using `iio_for_each_active_channel()`, pushes the scan with `iio_push_to_buffers_with_ts()`, frees the allocation, and calls `iio_trigger_notify_done()`. Setup registers the handler without a top-half poll function.

State/persistence: no persistent device state is modified. Sample values are static constants, and each trigger allocates/free a temporary scan buffer.

Dependencies/integration: depends on IIO buffer, trigger consumer, and triggered buffer support. It relies on scan indices from `iio_simple_dummy.h` matching the channel definitions in `iio_simple_dummy.c`.

Risks: per-trigger allocation can fail; the handler silently skips pushing data but still notifies trigger completion. `sizeof(*scan)` is pushed even when fewer channels are active, so consumers rely on IIO scan mask interpretation. Test signals include active scan masks, timestamp alignment, memory allocation failure path, trigger completion, and direct-mode reads returning `-EBUSY` while buffered capture is active.
