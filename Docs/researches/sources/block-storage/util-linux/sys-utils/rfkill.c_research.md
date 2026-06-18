# File Research: sources/block-storage/util-linux/sys-utils/rfkill.c

This file implements the `/dev/rfkill` control utility. It supports listing devices, streaming events, blocking, unblocking, and toggling rfkill state by numeric index, type name, or `all`. Type aliases include `wifi` for WLAN and `ultrawideband` for UWB, with compatibility definitions for older kernel headers.

Device state is read by opening `/dev/rfkill` and consuming `struct rfkill_event` records, while sysfs under `/sys/class/rfkill/rfkill<N>/` supplies names and type strings for output. Modern list output uses libsmartcols with optional JSON/raw/no-heading/custom columns. Explicit `list` without custom output preserves the deprecated historical multi-line format.

Block and unblock write `RFKILL_OP_CHANGE` or `RFKILL_OP_CHANGE_ALL` events to `/dev/rfkill` and log the change through syslog. Toggle reads current add events, matches the selected device or type, and writes the opposite soft-block value. Event mode polls indefinitely and prints timestamped raw event fields until polling or stdout fails.
