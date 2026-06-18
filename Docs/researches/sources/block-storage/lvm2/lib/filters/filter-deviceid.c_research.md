# File Research: sources/block-storage/lvm2/lib/filters/filter-deviceid.c

This file implements the devices-file/devices-list admission filter. `_passes_deviceid_filter` clears deviceid-related filtered flags, then passes all devices when both devices file and devices list are disabled, or when the command has set `filter_deviceid_skip`.

When device matching is enabled, only devices with `DEV_MATCHED_USE_ID` pass. Non-matching devices are marked with `DEV_FILTERED_DEVICES_FILE` or `DEV_FILTERED_DEVICES_LIST` depending on which mechanism is active, then rejected with a debug message.

`deviceid_filter_create` allocates a simple `dev_filter` named `deviceid`; destruction only checks use count and frees the filter. The filter depends on `cmd_context` policy flags populated elsewhere by device-id discovery.
