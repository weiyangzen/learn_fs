<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h

## Purpose
`hiddev.h` defines the older parsed-HID userspace ABI for `/dev/usb/hiddev*`. It exposes HID applications, collections, reports, fields, usages, string descriptors, and event reads at a higher level than raw HID reports.

## Important APIs, types, and functions
Structures include `hiddev_event`, `hiddev_devinfo`, `hiddev_collection_info`, `hiddev_string_descriptor`, `hiddev_report_info`, `hiddev_field_info`, `hiddev_usage_ref`, and `hiddev_usage_ref_multi`. Constants cover report IDs (`HID_REPORT_ID_UNKNOWN`, `FIRST`, `NEXT`, `MASK`, `MAX`), report types, field flags, `HID_MAX_MULTI_USAGES`, `HID_FIELD_INDEX_NONE`, `HID_VERSION`, and read flags `HIDDEV_FLAG_UREF`/`HIDDEV_FLAG_REPORT`. Ioctls include `HIDIOCGVERSION`, `HIDIOCAPPLICATION`, `HIDIOCGDEVINFO`, `HIDIOCGSTRING`, `HIDIOCINITREPORT`, `HIDIOCGNAME`, `HIDIOCGREPORT`, `HIDIOCSREPORT`, `HIDIOCGREPORTINFO`, `HIDIOCGFIELDINFO`, `HIDIOCGUSAGE`, `HIDIOCSUSAGE`, `HIDIOCGUCODE`, `HIDIOCGFLAG`, `HIDIOCSFLAG`, collection queries, `HIDIOCGPHYS`, and multi-usage gets/sets.

## Control flow
Users enumerate applications and reports, walk fields and usages by repeatedly using `HID_REPORT_ID_FIRST` and `HID_REPORT_ID_NEXT`, get or set usage values, then optionally send output/feature reports. Reads return either events or usage/report records depending on configured flags.

## State and persistence behavior
Report values, flag mode, and initialized report state are per open HID device. Device descriptors and collections are discovered state from the HID parser; output/feature writes can alter device state.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with the HID parser, USB/input devices, hiddev char devices, and legacy tools that need parsed usages rather than raw reports.

## Risks and test signals
Risks include report ID traversal loops, wrong report type numbering, oversized multi-usage arrays, stale field indexes after device reconnect, and using hiddev for devices better served by hidraw. Test signals include descriptor traversal tests, get/set usage round trips, feature report writes, collection lookup, read-flag behavior, disconnect handling, and compat ioctl coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hiddev.h -->
