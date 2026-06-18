# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.c

Purpose: provides brcmsmac debugfs files and logging wrappers that also emit tracepoints.

Important APIs and functions: `brcms_debugfs_init()`/`exit()` create/remove the module root. `brcms_debugfs_attach()`/`detach()` create/remove per-device debugfs directories. `brcms_debugfs_create_files()` adds `hardware` and `macstat` read-only files. `brcms_debugfs_hardware_read()` prints chip, board, ucode, radio, PHY, and NVRAM metadata. `brcms_debugfs_macstat_read()` snapshots and prints many ucode MAC counters. The `__brcms_info/warn/err/crit` wrappers call device logging and tracepoints; `__brcms_dbg()` conditionally emits debug logs and trace events.

Control flow: attach creates directory, create-files allocates `brcms_debugfs_entry` with device-managed memory and binds `single_open()` seq readers. `macstat` takes `wl->lock` while copying the snapshot, then prints without holding the lock.

State and persistence: debugfs dentries exist while module/device is active. Entries reference driver state but do not persist data. Trace/log records are transient.

Dependencies and integration: depends on debugfs, seq_file, mac80211 private state, D11/macstat definitions, Broadcom utility formatting, and trace events.

Risks and test signals: readers must not dereference freed driver state after detach; debugfs removal ordering matters. Macstat snapshot locking must match writers. Test mounting debugfs, reading hardware/macstat during traffic, device detach while readers exist, and tracing/debug-level combinations.
