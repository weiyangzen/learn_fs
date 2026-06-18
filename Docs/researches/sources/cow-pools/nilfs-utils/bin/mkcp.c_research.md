# File Research: sources/cow-pools/nilfs-utils/bin/mkcp.c

Implements `mkcp`, the checkpoint creation command. It opens NILFS read-write with cleaner locking and device lookup, calls `nilfs_sync()` to force a new checkpoint, and optionally prints the created checkpoint number.

With `-s`, it converts the newly created checkpoint to a snapshot using `nilfs_change_cpmode()` under the cleaner lock. Signals are blocked during the snapshot conversion section.
