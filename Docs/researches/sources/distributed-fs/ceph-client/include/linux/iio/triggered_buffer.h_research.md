<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h

Purpose: Declares helpers for IIO devices that use trigger-driven buffered capture.

Important APIs/types/functions: `iio_triggered_buffer_setup_ext()` wires top-half, threaded handler, setup ops, and optional attrs; `iio_triggered_buffer_cleanup()` unwinds it. Shorter macros provide default NULL attrs, and devm variants bind cleanup to a device.

Control flow: Probe calls setup, IIO core enables buffers and attaches poll functions to triggers, threaded handlers push scans, and cleanup runs on remove.

State/persistence: Buffer/poll function state is stored in the `iio_dev` and persists while setup is active.

Dependencies/integration: Depends on IIO buffer core, interrupt handlers, trigger consumer infrastructure, and device-managed resources.

Risks: Handler/sample layout mismatch with channel scan specs corrupts buffered ABI.

Test signals: Probe/remove cleanup, buffer enable with trigger, top/thread handler ordering, scan mask validation, and devm unwind on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h -->
