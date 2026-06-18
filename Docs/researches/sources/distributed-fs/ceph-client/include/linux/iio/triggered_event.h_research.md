<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h

Purpose: Declares helpers for IIO devices that produce events through trigger infrastructure rather than normal buffered samples.

Important APIs/types/functions: `iio_triggered_event_setup()` installs top and threaded IRQ handlers for event triggering; `iio_triggered_event_cleanup()` removes them.

Control flow: Probe sets up event triggering; trigger polls invoke handlers that typically evaluate/report events; remove cleans up.

State/persistence: Event poll function state is attached to the IIO device for the setup lifetime.

Dependencies/integration: Depends on interrupts, IIO trigger consumer/provider code, and event pushing in `iio.h`.

Risks: Event-triggered mode is unusual and close to buffered trigger flow; incorrect cleanup or notify-done handling affects all attached consumers.

Test signals: Event enable/disable, trigger firing, event code delivery, and cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h -->
