# File Research: sources/block-storage/lvm2/lib/filters/filter-fwraid.c

This Linux-only filter rejects firmware RAID component devices when firmware RAID filtering is enabled. With udev support, `_udev_dev_is_fwraid` checks the udev blkid type property and treats non-software RAID values with a RAID suffix as firmware RAID components. Without udev, native detection logs that firmware RAID detection is unsupported and passes the device.

`_ignore_fwraid` skips data-dependent checks when `cmd->filter_nodata_only` is set, clears `DEV_FILTERED_FWRAID`, checks the global `fwraid_filtering()` setting, and rejects detected components while recording the filtered flag.

`fwraid_filter_create` returns a filter named `fwraid` on Linux and `NULL` on non-Linux builds. The implementation relies on external device info when available, especially udev, and logs an internal error if an unsupported external info source reaches the detector.
