<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/events.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/events.h

Purpose: Defines kernel-side helpers for packing Industrial I/O event identity into the u64 event code consumed by `iio_push_event()` and userspace event readers.

Important APIs/types/functions: `_IIO_EVENT_CODE()` is the common bit-packer; `IIO_MOD_EVENT_CODE()`, `IIO_UNMOD_EVENT_CODE()`, and `IIO_DIFF_EVENT_CODE()` specialize modified, unmodified, and differential channels. It depends on UAPI event bit positions and `enum iio_chan_type`.

Control flow: There is no runtime control flow; callers build stable event codes at event-report sites.

State/persistence: No state is owned. The generated code encodes channel type, index, modifier or differential pair, event type, and direction into a persistent ABI value.

Dependencies/integration: Integrates `linux/iio/types.h`, `uapi/linux/iio/events.h`, and IIO event callbacks declared in `iio.h`.

Risks: Incorrect modified/differential flags or channel numbering silently changes userspace-visible event identity.

Test signals: Compile users using all three macros and exercise threshold/event sysfs paths; verify decoded event codes match expected channel, type, and direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/events.h -->
