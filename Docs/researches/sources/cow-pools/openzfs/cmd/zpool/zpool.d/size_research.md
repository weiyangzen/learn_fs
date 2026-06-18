# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/size

Symlink to `lsblk`; behavior is selected by invoked basename `size`.

Behavior:
- For file-based vdevs, uses `du -h --apparent-size`.
- For block vdevs, runs `lsblk -dl -n -o size`.
- Prints `size=<capacity>`.

Role:
- Reports vdev capacity for both block and file vdevs.
