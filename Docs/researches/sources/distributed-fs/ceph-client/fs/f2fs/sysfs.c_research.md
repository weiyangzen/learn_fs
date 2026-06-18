# sources/distributed-fs/ceph-client/fs/f2fs/sysfs.c

## Purpose
`sysfs.c` implements F2FS runtime observability and tuning through `/sys/fs/f2fs`, per-mount sysfs directories, feature-list kobjects, and `/proc/fs/f2fs/<device>` debug files. It exposes mount and allocator state, GC controls, discard controls, node-manager settings, checkpoint-thread priority, compression counters, atomic-write counters, age extent cache tuning, zoned-device knobs, and feature capability reporting.

## Important APIs, Types, And Functions
The main local descriptors are `struct f2fs_attr` for per-superblock attributes and `struct f2fs_base_attr` for global base attributes. `__struct_ptr()` maps an attribute's `struct_type` to the live object that stores the value: GC thread, segment manager, discard command control, node manager, `f2fs_sb_info`, fault-injection state, stat info, checkpoint request control, or ATGC state.

Generic show/store helpers include `f2fs_sbi_show()`, `__sbi_show_value()`, `f2fs_sbi_store()`, `__sbi_store()`, `f2fs_attr_show()`, `f2fs_attr_store()`, `f2fs_base_attr_show()`, and `f2fs_base_attr_store()`. Registration is handled by `f2fs_init_sysfs()`, `f2fs_exit_sysfs()`, `f2fs_register_sysfs()`, and `f2fs_unregister_sysfs()`. Procfs seq emitters include `segment_info_seq_show()`, `segment_bits_seq_show()`, `victim_bits_seq_show()`, `discard_plist_seq_show()`, `disk_map_seq_show()`, `donation_list_seq_show()`, and optional `inject_stats_seq_show()`.

## Control Flow
At module initialization, `f2fs_init_sysfs()` registers the `f2fs` kset under `fs_kobj`, adds global `features` and `tuning` kobjects, and creates `/proc/fs/f2fs`. At mount time, `f2fs_register_sysfs()` adds a per-superblock kobject named after `sb->s_id`, creates `stat` and `feature_list` child kobjects, and creates procfs diagnostic files bound to the mounted superblock. Unregistration removes the proc subtree first, then drops child and parent kobjects and waits for completion callbacks.

Attribute definitions are generated through macros such as `F2FS_RW_ATTR`, `F2FS_RO_ATTR`, `F2FS_GENERAL_RO_ATTR`, `F2FS_FEATURE_RO_ATTR`, and `F2FS_SB_FEATURE_RO_ATTR`. Most simple attributes are offset-based reads or writes into live structs. Special cases in `f2fs_sbi_show()` and `__sbi_store()` handle extension lists, checkpoint-thread I/O priority, compression counters, GC modes, current and peak atomic write counters, fault injection, reserved blocks, discard policy bounds, iostat controls, compression watermarks, ATGC ratios, file donation, allocation hints, and scheduling priorities.

## State And Persistence Behavior
Most sysfs writes mutate only live in-memory mount state. A notable exception is `extension_list`: writes update the raw superblock extension list under `sb_lock` and call `f2fs_commit_super()`, rolling back the in-memory list if persistence fails. Counter reset attributes such as compression and atomic-write counters require a zero write. Feature attributes are read-only and report either kernel-supported capabilities or per-filesystem on-disk feature flags.

Some writes immediately affect background work. `gc_urgent` wakes the GC thread and discard thread for urgent modes. `ckpt_thread_ioprio` updates the checkpoint thread task if checkpoint merging is active. `critical_task_priority` requires `CAP_SYS_NICE` and updates checkpoint and GC task niceness. Procfs views read live SIT, dirty segment, discard, disk-map, donation, and fault-injection state without persisting data.

## Dependencies And Integration Points
This file depends on F2FS internals from `f2fs.h`, `segment.h`, `gc.h`, and `iostat.h`, plus kernel sysfs, procfs, seq_file, Unicode, and I/O priority APIs. It integrates with `super.c` through module-level sysfs init/exit and per-mount register/unregister calls. It also integrates with GC/discard threads, the checkpoint request control, segment/node managers, compression accounting, iostat processing, fault injection, and optional zoned-block-device support.

## Risks
The main risk is unsafe mutation of live kernel state from sysfs. Many stores validate ranges, feature modes, and capabilities, but they still alter scheduling, GC, discard, allocation, and cache behavior on a mounted filesystem. Kobject lifetime ordering is important because per-mount sysfs/procfs entries reference `struct f2fs_sb_info`; unregistering early during unmount avoids users racing teardown. Offset-based attributes are compact but fragile if a macro points to the wrong struct or field size. Procfs debug views can be expensive on large filesystems because they iterate all segments or sections.

## Test Signals
Test signals include sysfs file presence after mount and removal after unmount, read/write permission checks, invalid value rejection, GC wakeup behavior after `gc_urgent`, extension-list persistence across remount, feature-list accuracy for images with different mkfs features, procfs output smoke tests, fault-injection counters when enabled, lockdep around unmount races, and KASAN/KCSAN coverage for concurrent sysfs reads and teardown.
