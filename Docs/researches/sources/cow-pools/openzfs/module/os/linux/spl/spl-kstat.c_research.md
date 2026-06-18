# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-kstat.c

Read completely: 769 lines.

This implements Solaris-style kstats on Linux procfs under `/proc/spl/kstat`. It creates kstat objects, formats their data through `seq_file`, manages module/submodule directories, and installs/removes proc entries.

Key responsibilities:
- Defines global kstat module list and monotonically increasing kstat IDs.
- Supports raw, named, interrupt, I/O, and timer kstat types.
- Provides seq_file show/start/next/stop operations for kstat reads.
- Provides write support by invoking the kstat update callback with `KSTAT_WRITE`.
- Creates/deletes nested proc directories for kstat module paths.
- Detects some namespace collisions between file names and module directory names.
- Exports kstat create/install/delete and raw operation setup APIs.

Important implementation details:
- Raw kstats allocate a temporary buffer at read start and resize it up to `KSTAT_RAW_MAX` if raw callbacks return `ENOMEM`.
- `kstat_seq_start()` locks the kstat, refreshes it through `ks_update(KSTAT_READ)`, sets snapshot time, optionally prints headers, and then returns the record for the current position.
- `kstat_create_module()` walks slash-separated module names, creating proc directories and parent-child bookkeeping.
- Installing an entry with an existing name in the same module removes the older proc entry from visibility while leaving the older kstat object alive.
- The `dbufs` kstat is installed mode `0600`; others default to `0644`.
- Finalization asserts all kstat modules have been removed.

Dependencies and interactions:
- Depends on procfs root `proc_spl_kstat` created by `spl-proc.c`.
- Procfs-list helpers install non-kstat list files through the same `kstat_proc_entry_install()` namespace.
- Used broadly for OpenZFS observability.

Reliability notes:
- Lifetime is guarded by `kstat_module_lock` for namespace structures and per-kstat locks for data snapshots.
- The collision detection only covers particular parent/file conflicts; consumers still need consistent module/name choices.
