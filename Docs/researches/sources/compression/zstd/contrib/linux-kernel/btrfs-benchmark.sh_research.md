# sources/compression/zstd/contrib/linux-kernel/btrfs-benchmark.sh

Purpose: manual benchmark script comparing Btrfs compression modes using the Silesia corpus.

Important behavior: sets `BENCHMARK_DIR=$HOME/silesia/` and `N=10`, unmounts/remounts `/mnt/btrfs` on `/dev/sda3` with user-supplied mount options, clears the filesystem, copies the corpus ten times while timing compression, estimates ratio from `df` and `du`, remounts to reduce cache effects, times a tar read for decompression, then cleans and unmounts. Historical result comments compare none, lzo, zlib, and zstd levels.

State, dependencies, and integration: it mutates `/mnt/btrfs` and `/dev/sda3` data destructively. It depends on sudo, btrfs, coreutils, tar, Silesia corpus, and a specific benchmark environment.

Risks and test signals: this is dangerous outside a prepared VM because it deletes filesystem contents. It is not automated CI; results are manual performance signals.
