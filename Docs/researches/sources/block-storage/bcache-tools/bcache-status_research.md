# File Research: sources/block-storage/bcache-tools/bcache-status

This Python status tool reads live bcache sysfs state from `/sys/fs/bcache`, `/sys/block`, and `/dev/block`. It formats sector counts, maps major:minor device IDs back to device paths, and prints aggregate cache set data plus optional backing/cache subdevice detail.

The script supports stats windows for five-minute, hour, day, total, or all; optional stats reset; optional subdevice status; and optional GC triggering through `internal/trigger_gc`. It computes cache usage from each cache device’s `priority_stats`, reads hit/miss counters from `stats_*` directories, and resets via `clear_stats`. It is read-mostly but can write to sysfs for `--gc` and `--reset-stats`.

Notable operational risk: it uses Python 2 style integer division and an unversioned `#!/usr/bin/env python`, so behavior depends on the system’s default Python.
