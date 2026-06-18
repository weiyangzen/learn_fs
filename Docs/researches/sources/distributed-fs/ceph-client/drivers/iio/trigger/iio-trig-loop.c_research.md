# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-loop.c

Purpose: Experimental IIO software trigger that polls continuously from a kthread as fast as possible.

Important APIs/types/functions: `struct iio_loop_info` embeds `iio_sw_trigger` and the active task pointer. Core functions are `iio_loop_thread()`, `iio_loop_trigger_set_state()`, `iio_trig_loop_probe()`, and remove.

Control flow: probe allocates and registers a software trigger. Enabling starts a freezable kthread that repeatedly calls `iio_trigger_poll_nested()` until stopped. Disabling stops the task. Remove unregisters and frees the trigger state.

State and persistence: task pointer exists only while enabled. No persisted configuration.

Dependencies/integration: IIO software trigger framework, kthreads, freezer support, and platform alias `iio-trig-loop`.

Risks: intentionally high CPU usage; unsafe for consumers needing top-half behavior. Disable assumes a valid task exists. Remove does not explicitly stop an active task, relying on trigger disable ordering.

Test signals: create loop trigger, attach a lower-half-only buffered device, observe high-rate sampling, freeze/thaw behavior, and clean disable/remove.
