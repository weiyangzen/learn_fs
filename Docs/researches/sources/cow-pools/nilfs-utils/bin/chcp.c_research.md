# File Research: sources/cow-pools/nilfs-utils/bin/chcp.c

Implements `chcp`, the checkpoint mode changer. Usage is `chcp cp|ss [DEVICE|NODE] CNO...`, where `cp` converts checkpoints to ordinary checkpoints and `ss` converts them to snapshots.

The command parses optional device/node by testing whether the next argument looks like a checkpoint number. It opens NILFS with `NILFS_OPEN_RDWR | NILFS_OPEN_GCLK | NILFS_OPEN_SRCHDEV`, blocks `SIGINT` and `SIGTERM`, takes the cleaner lock, then calls `nilfs_change_cpmode()` for each checkpoint number.

Input validation rejects malformed checkpoint numbers and reports missing checkpoints via `ENOENT`. The signal-blocking and cleaner-lock sequence prevents interruption during checkpoint metadata mutation.
