# File Research: sources/block-storage/bcache-tools/zoned.c

This file adds zoned block device awareness. It reads `/sys/block/<base>/queue/chunk_sectors` to determine zone size and `/sys/block/<base>/queue/zoned` to detect zoned devices, falling back to nonzero chunk size when `zoned` is absent.

`check_data_offset_for_zoned_device` moves default backing-device data offset to the first full zone when needed, rejects offsets smaller than zone size, and reports unaligned offsets. `is_zoned_device` is used by formatter logic to avoid writeback mode on zoned backing devices.
