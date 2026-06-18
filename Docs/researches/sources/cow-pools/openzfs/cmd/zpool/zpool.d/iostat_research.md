# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat

Shell helper for per-vdev iostat columns.

Behavior:
- `-h` prints helper-specific help.
- Uses `VDEV_UPATH` when it is a block device, otherwise `VDEV_PATH`.
- Exits without output for file-based vdevs.
- On FreeBSD, runs `iostat -dKx`.
- On other systems, runs `iostat -kx`.
- For basename `iostat`, reports since-boot summary stats.
- Parses the final header/data pair and prints every metric except the device-name column as `column=value`.

Role:
- Provides broad iostat bandwidth/latency/utilization metrics as custom zpool columns.
