# File Research: sources/block-storage/lvm2/lib/filters/filter.h

This header declares the LVM device filter constructors and filtered-reason bit flags. It includes device cache and device-type definitions because filters operate on `struct device`, `struct dev_types`, and command contexts.

Constructors cover composite, type, md, firmware RAID, multipath, partitioned, persistent cache, sysfs, signature, deviceid, regex, and usable filters. The regex comment documents pattern grammar: strings begin with accept/reject (`a`/`r`) and use a delimiter around the regex.

The `DEV_FILTERED_*` constants are bit flags stored in `device->filtered_flags` to explain why a device was rejected, including md/mpath components, partition tables, regex rejection, signatures, missing sysfs, unrecognized type, too-small devices, unusable DM devices, devices-file/list mismatch, and LV scanning exclusion.
