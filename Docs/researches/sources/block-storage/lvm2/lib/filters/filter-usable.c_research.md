# File Research: sources/block-storage/lvm2/lib/filters/filter-usable.c

This filter rejects block devices that are too small or unusable as PV scan candidates. `_check_pv_min_size` reads the device size and requires it to be at least `pv_min_size()`, logging a specific "too small" reason on failure.

`_passes_usable_filter` clears minsize/unusable/LV flags. For device-mapper devices it calls `dm_device_is_usable` with parameters stored in `private`; unusable devices are marked as either `DEV_FILTERED_IS_LV` or `DEV_FILTERED_UNUSABLE`. If the DM usability checks pass, it applies the PV minimum size check and marks `DEV_FILTERED_MINSIZE` on failure.

`usable_filter_create` builds a `dev_usable_check_params` object with checks for empty, blocked, suspended, error-target, reserved, and LV devices. The LV check is disabled when `devices/scan_lvs` is enabled. The filter is named `usable` and owns both the filter and parameter allocation.
