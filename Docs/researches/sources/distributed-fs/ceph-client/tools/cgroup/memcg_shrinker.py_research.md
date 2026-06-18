# sources/distributed-fs/ceph-client/tools/cgroup/memcg_shrinker.py

Purpose: Reports the largest per-memcg shrinker counts by correlating debugfs shrinker entries with cgroup inode numbers.

Important APIs, types, and functions: `scan_cgroups()` walks `/sys/fs/cgroup/` and maps inode to path. `scan_shrinkers()` walks `/sys/kernel/debug/shrinker/`, reads each `count` file, and records count, shrinker name, and memcg inode. `main()` sorts and prints nonzero entries with optional line limit.

Control flow: Parse `--lines`, build cgroup map, collect shrinker counts, sort descending by count, map inode 0/1 to root, map unknown inodes to `unknown (<ino>)`, print until zero count or limit.

State and persistence: Read-only. No persistent state.

Dependencies and integration points: Depends on cgroup filesystem and shrinker debugfs layout. Intended for kernel memory reclaim diagnostics.

Risks: Assumes count file lines split into inode and count. Permission or missing debugfs will raise exceptions. Inode-to-path mapping may race with cgroup creation/removal.

Test signals: Run with debugfs mounted, `-n` limits, no shrinker entries, and cgroups removed while scanning.
