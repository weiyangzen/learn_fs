# File Research: sources/block-storage/bcache-tools/zoned.h

This header declares `check_data_offset_for_zoned_device(char *devname, uint64_t *data_offset)` and `is_zoned_device(char *devname)` behind `__ZONED_H`. It expects `uint64_t` to be available from prior includes.
