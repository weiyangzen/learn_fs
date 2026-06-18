# sources/distributed-fs/ceph-client/include/linux/proc_fs.h

Purpose: declares the kernel-facing procfs API for creating, removing, and operating `/proc` entries, including seq-file helpers, network namespace proc entries, mount policy state, BPF iterator integration, pidfd helpers, and disabled-config stubs.

Important APIs and types: `struct proc_ops` is the file-operation table for proc entries, with read/write/seek/poll/ioctl/mmap callbacks and flags such as `PROC_ENTRY_PERMANENT`, `PROC_ENTRY_proc_read_iter`, and `PROC_ENTRY_FORCE_LOOKUP`. `struct proc_fs_info` stores per-superblock pid namespace, `hide_pid`, `pidonly`, and group policy. Creation helpers include `proc_symlink()`, `_proc_mkdir()`, `proc_mkdir*()`, `proc_create*()`, `proc_create_seq*()`, `proc_create_single*()`, and network variants such as `proc_create_net_data()`. Removal and metadata helpers include `proc_remove()`, `remove_proc_entry()`, `remove_proc_subtree()`, `proc_set_size()`, `proc_set_user()`, `pde_data()`, and `proc_get_parent_data()`.

Control flow: subsystems create directories or files under a parent `proc_dir_entry`, optionally attach private data, and supply either `proc_ops`, `seq_operations`, or single-show callbacks. Procfs dispatches VFS operations through `struct proc_ops`; network helpers bind namespace state; cleanup must remove entries before backing data disappears. When procfs is disabled, creation returns `NULL` and removals are no-ops, forcing callers to tolerate absence.

State and persistence: proc entries are in-memory VFS objects tied to procfs lifetime; `proc_fs_info` is per mount/superblock and RCU-freed. The files expose live kernel state rather than persistent storage. Private `pde_data()` state remains owned by the registering subsystem.

Dependencies and integration points: depends on VFS, seq_file, pid namespaces, network namespaces, BPF iterators, architecture `/proc` status hooks, and proc namespace helpers. It is central to diagnostic and control files used by drivers, filesystems, networking, and process introspection.

Risks and test signals: risks include use-after-free when removing proc entries after private data is freed, missing `proc_lseek`, wrong hidepid/pid namespace behavior, callback ABI mismatches, and untested disabled `CONFIG_PROC_FS` stubs. Test creation/removal races, module unload with open files, seq-file iteration, netns teardown, BPF iterator init/fini, pidfd conversion, hidepid mount options, and no-procfs builds.
