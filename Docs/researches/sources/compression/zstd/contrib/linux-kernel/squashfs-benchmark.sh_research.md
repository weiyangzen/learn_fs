# sources/compression/zstd/contrib/linux-kernel/squashfs-benchmark.sh

Purpose: manual benchmark script for SquashFS compression/decompression using a prepared Ubuntu filesystem tree.

Important behavior: defines `BENCHMARK_DIR=$HOME/squashfs-root/` and `BENCHMARK_FS=$HOME/filesystem.squashfs`, removes prior filesystem output and unmounts `/mnt/squashfs`, runs `sudo mksquashfs` with user-supplied options while timing compression, estimates ratio using `du`, mounts the generated SquashFS, times reading it through tar, and unmounts.

State, dependencies, and integration: writes/removes `$HOME/filesystem.squashfs` and mounts `/mnt/squashfs`. Depends on sudo, squashfs-tools, tar, du, and a pre-extracted benchmark directory.

Risks and test signals: manual only, and mount/remove operations require care. Useful outputs are compression time, approximate ratio, and decompression read time for comparing SquashFS compressor choices.
