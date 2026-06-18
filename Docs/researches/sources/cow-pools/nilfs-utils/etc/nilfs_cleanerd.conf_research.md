# File Research: sources/cow-pools/nilfs-utils/etc/nilfs_cleanerd.conf

Default configuration for the NILFS cleaner daemon. It defines protection period, clean segment thresholds, cleaning intervals, retry interval, segment selection policy, segment batch sizes, minimum reclaimable block thresholds, and logging priority.

Defaults include a 3600 second protection period, 10 percent minimum clean segments, 20 percent maximum clean segments, timestamp selection, two segments per normal clean, four under minimum-clean pressure, and enabled `use_set_suinfo` and `use_mmap`.

The comments document numeric suffix parsing for sizes and percent handling for capacity or per-segment block ratios.
