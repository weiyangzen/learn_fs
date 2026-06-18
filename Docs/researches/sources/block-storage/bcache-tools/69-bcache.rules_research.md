# File Research: sources/block-storage/bcache-tools/69-bcache.rules

This udev rule file auto-registers bcache block devices. It exits early for non-block events, removals, device-mapper-disabled rule processing, and floppy/CD style kernels, then uses existing `ID_FS_TYPE=bcache` from blkid when available. If blkid has not identified a filesystem, it imports metadata from `probe-bcache -o udev $tempnode`.

For backing devices, it loads the `bcache` kernel module and runs `bcache-register $tempnode`. For cached `/dev/bcacheN` devices, it imports `bcache-export-cached` output and creates `bcache/by-uuid` and `bcache/by-label` symlinks. This is the early device-discovery bridge between userspace metadata probing and `/sys/fs/bcache/register`.
