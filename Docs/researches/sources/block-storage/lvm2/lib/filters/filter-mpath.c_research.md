# File Research: sources/block-storage/lvm2/lib/filters/filter-mpath.c

This Linux-only filter rejects multipath component paths so LVM uses the multipath aggregate device. `_ignore_mpath_component` calls `dev_is_mpath_component`, records `DEV_FILTERED_MPATH_COMPONENT` on rejection, and logs the skipped component.

A notable devices-file safeguard warns when a multipath component is explicitly present in the devices file but the corresponding multipath device is missing. It looks up the aggregate devno with `get_du_for_devno` and `dev_cache_get_by_devt`, then emits a one-time suggestion to run `lvmdevices --update` outside the `lvmdevices` command itself.

`mpath_filter_create` requires sysfs to be mounted; without sysfs it logs that the multipath filter is skipped. On non-Linux builds it returns `NULL`.
