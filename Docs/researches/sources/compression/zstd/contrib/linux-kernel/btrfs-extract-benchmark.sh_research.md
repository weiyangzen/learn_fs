# sources/compression/zstd/contrib/linux-kernel/btrfs-extract-benchmark.sh

Purpose: manual benchmark script for Btrfs compression behavior while copying, extracting, and reading a Linux kernel tarball.

Important behavior: uses `$HOME/linux-4.11.6.tar`, remounts `/mnt/btrfs` on `/dev/sda3` with supplied compression options, clears the filesystem, times copying the tarball, estimates tarball ratio, remounts, times extraction, removes the tarball, remounts again, estimates extracted-tree ratio, times reading via tar, then cleans and unmounts. Commented historical results compare none, lzo, zlib, and zstd level 1.

State, dependencies, and integration: destructively modifies `/mnt/btrfs` and requires sudo, btrfs, tar, df/du, and the benchmark tarball.

Risks and test signals: high risk if run on the wrong block device. It is documentation/manual benchmarking, not CI. Useful signals are elapsed copy/extract/read times and approximate disk-usage ratios.
