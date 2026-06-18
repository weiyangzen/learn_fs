# File Research: sources/cow-pools/nilfs-utils/lib/lookup_device.c

Resolves a filesystem node to its backing block device. If the input is already a block device, it returns 0. Otherwise it stats the node, reads `/sys/dev/block/<maj>:<min>` to obtain the kernel device name, and returns a newly allocated `/dev/<name>` path.

This supports commands that accept either a device or a path inside a mounted NILFS filesystem.
