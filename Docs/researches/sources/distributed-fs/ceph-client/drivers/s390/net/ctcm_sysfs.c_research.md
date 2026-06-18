# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_sysfs.c

## Purpose
`ctcm_sysfs.c` defines the ccwgroup device sysfs attributes for CTCM. It exposes buffer size, protocol, channel type, and a stats trigger/reset interface through the `ctcm_attr_groups` attribute group consumed by `ctcm_main.c`.

## Important APIs, Types, And Functions
- `ctcm_buffer_show()` and `ctcm_buffer_write()` expose and update `priv->buffer_size` and both channels' `max_bufsize`.
- `ctcm_print_statistics()` formats current device/channel FSM states and write-channel profiling counters to the kernel log.
- `stats_show()` triggers statistics printing and returns `0`; `stats_write()` clears write-channel profiling counters.
- `ctcm_proto_show()` and `ctcm_proto_store()` expose and set the protocol field.
- `ctcm_type_show()` reports the ccw channel type based on `driver_info`.
- Defines `DEVICE_ATTR(buffer)`, `DEVICE_ATTR(protocol)`, `DEVICE_ATTR(type)`, `DEVICE_ATTR(stats)`, and exports `ctcm_attr_groups`.

## Control Flow
The sysfs group is attached through the `ctcm_devtype` in `ctcm_main.c`. Reads validate that private data and, for stats, online state exist before reporting. Buffer writes parse an unsigned integer, validate maximum and minimum classic CTC buffer sizes, reject running devices if the requested buffer is smaller than the current MTU plus header overhead, update both channel max buffer sizes, and mark both channels with `CHANNEL_FLAGS_BUFSIZE_CHANGED` so the next buffer check reallocates safely. Protocol writes accept S390, Linux, MPC, or OS390 protocol values and update `priv->protocol`.

## State And Persistence Behavior
All sysfs writes update live in-memory driver state. Buffer changes affect `priv->buffer_size`, both channel `max_bufsize` values, current netdev MTU if the interface is down, and the buffer-size-changed flags. Stats writes clear only `priv->channel[WRITE]->prof`. Values are lost when the device is removed or module unloaded.

## Dependencies And Integration Points
The file depends on `ctcm_main.h` for `struct ctcm_priv`, channel constants, buffer limits, protocol values, debug macros, and FSM helpers. It integrates with Linux device attributes and ccwgroup device state. Statistics output depends on FSM instances being valid and channels being present.

## Risks
- `ctcm_proto_store()` does not check whether the device is already online/running, so protocol changes after setup may not reinitialize existing channel state consistently.
- Buffer validation is classic-header based and does not use MPC TH/PDU overhead; MPC buffer changes should be treated cautiously.
- `stats_show()` logs details to the kernel log rather than returning them through sysfs, which can surprise tests and users.
- The code uses `WRITE` in a few `priv->channel[WRITE]` references; correctness depends on local/global constants resolving as intended.

## Test Signals
- Sysfs tests should verify accepted and rejected buffer sizes, including running vs stopped interface behavior.
- Protocol tests should verify valid protocol numbers and invalid values.
- Stats tests should verify show logs FSM/profile information only for online devices and write clears profiling counters.
- Type tests should verify ccw `driver_info` indexes map to expected strings.
