# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_internal.h

Purpose: provides internal C declarations and structs used by `rust_binderfs.c` to interact with Rust Binder contexts and exported seq-file/file-operation hooks.

Important APIs/types/functions: defines `RUST_BINDERFS_SUPER_MAGIC`, opaque `rust_binder_context`, `struct binder_device`, show callbacks `rust_binder_stats_show`, `rust_binder_state_show`, `rust_binder_transactions_show`, and `rust_binder_proc_show`, exported `rust_binder_fops`, context lifecycle functions `rust_binder_new_context` and `rust_binder_remove_context`, `binderfs_mount_opts`, and `binderfs_info`.

Control flow: the header is declarative. binderfs code stores `binder_device` in inode private data, calls Rust to create/remove contexts, assigns `rust_binder_fops` to Binder character device inodes, and passes seq-file calls back into Rust.

State and persistence: `binder_device` owns a Binder minor and a Rust context reference, except for binder-control where `ctx` is null. `binderfs_info` persists per superblock and tracks namespace, root uid/gid, mount options, device count, control dentry, and proc log directory.

Dependencies and integration points: includes Linux seq-file and Android Binder UAPI headers. It is intentionally not part of the bindgen input for exports from binderfs to Rust; those are declared in `rust_binder.h`/Rust extern blocks.

Risks: ownership comments are part of the ABI contract. Forgetting to call `rust_binder_remove_context` during inode eviction leaks Rust contexts; freeing `binder_device` while Rust file operations still access it would be unsafe. Mount option structs must stay consistent with parser/fill-super code.

Test signals: mount/unmount binderfs repeatedly, create and unlink binder devices, open/close Binder files, and read global/proc log files. Leak checks should show balanced context creation/removal and minor allocation/free.
