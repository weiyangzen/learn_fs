<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/types.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/types.h

Purpose: Defines kernel-side IIO value, event-info, available-value, and channel-info enums layered on top of UAPI channel/event types.

Important APIs/types/functions: `enum iio_event_info` adds event configuration fields such as value, hysteresis, period, high/low pass filters, timeout, enable, reset timeout, and scale. `IIO_VAL_*` macros describe callback return value encoding. `enum iio_available_type` describes list/range availability. `enum iio_chan_info_enum` enumerates raw, processed, scale, offset, sampling frequency, filters, calibration, peak, oversampling, integration time, enable, errors, and label.

Control flow: IIO callbacks return these value-format constants and use enum ids in channel/event masks.

State/persistence: No owned state; values define stable ABI contracts between drivers, core, and userspace formatting.

Dependencies/integration: Includes UAPI IIO types and is used heavily by `iio.h`, drivers, sysfs, and events.

Risks: Masks rely on enum positions; changing order breaks sysfs/event ABI.

Test signals: Compile mask users, sysfs formatting for every `IIO_VAL_*` form, and event attribute generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/types.h -->
