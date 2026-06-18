# sources/distributed-fs/ceph-client/drivers/platform/x86/wmi-bmof.c

Purpose: exposes WMI embedded Binary MOF data through a binary sysfs attribute for devices advertising GUID `05901221-D566-11D1-B2F0-00A0C9062910`.

Important APIs and control flow: probe allocates `struct wmi_buffer`, calls `wmidev_query_block()` for instance 0, and stores the buffer as driver data. The `bmof` binary attribute is admin-readable, reports size from `buffer->length`, and serves reads through `memory_read_from_buffer()`. Remove frees `buffer->data` allocated by the WMI query.

State and dependencies: per-WMI-device state is the queried binary buffer. Integration is with WMI block query APIs and sysfs binary attributes attached through driver `dev_groups`.

Risks and test signals: ownership of `buffer->data` is split from devm allocation and must be freed exactly once. Tests should verify sysfs size/read behavior, partial reads and offsets, no data exposure to unprivileged users, multiple WMI devices with `no_singleton`, query failure handling, and remove cleanup.
