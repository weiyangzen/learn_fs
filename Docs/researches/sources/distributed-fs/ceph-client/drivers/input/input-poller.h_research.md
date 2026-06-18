# sources/distributed-fs/ceph-client/drivers/input/input-poller.h

`input-poller.h` is the internal header for input polling support. It forward-declares `struct input_dev_poller`, declares lifecycle helpers `input_dev_poller_finalize()`, `input_dev_poller_start()`, and `input_dev_poller_stop()`, and exposes `input_poller_attribute_group` for inclusion in the input device's sysfs groups.

The public-facing driver APIs (`input_setup_polling()` and interval setters) live in public input headers; this private header is for `input.c` and `input-poller.c` coordination. There is no state in the header. Its integration point is `input_dev_attr_groups` in `input.c`, which includes the attribute group unconditionally but relies on the group's visibility callback to hide attributes for non-polled devices.

Risks are prototype drift and accidental exposure of internals. Test signals are compile coverage and sysfs visibility: non-polled devices must not show polling attributes, while polled devices should show `poll`, `min`, and `max`.
