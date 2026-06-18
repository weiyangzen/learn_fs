# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_main.rs

Purpose: is the Rust Binder module root. It declares submodules, registers the Binder shrinker and binderfs filesystem, exposes C file operations and debug show callbacks, and defines the common `DeliverToRead` work-item abstraction.

Important APIs/types/functions: `BinderModule::init` initializes global contexts, registers `BINDER_SHRINKER`, and calls C `init_rust_binderfs`. `RUST_BINDER_LAYOUT` exports Rust struct offsets to C. `BinderReturnWriter` writes BR commands/payloads and updates stats. `DeliverToRead`, `DTRWrap`, `DArc`, and `DLArc` are the dynamic work queue foundation. `DeliverCode` emits simple return codes. Exported callbacks include `rust_binder_new_context`, `rust_binder_remove_context`, `rust_binder_open`, `release`, `ioctl`, `mmap`, `poll`, `flush`, and seq-file show functions. `BinderfsProcFile` owns per-pid binderfs log dentries.

Control flow: module initialization prepares global infrastructure. binderfs creates contexts through `rust_binder_new_context`; opening a Binder device creates a `Process`, optionally creates a per-pid proc log file, and stores the process arc in `file.private_data`. C file operations borrow or consume that arc and delegate to `Process`. Seq-file callbacks enumerate contexts and processes to print stats, state, transactions, or one pid.

State and persistence: global state includes the context registry, debug-id counter, shrinker, file operations table, and exported layout. Per-file state is owned by `Process`; per-pid binderfs proc files are removed by `BinderfsProcFile::drop`.

Dependencies and integration points: ties Rust modules to C binderfs (`rust_binderfs.c`), trace/stats, kernel module macros, file/mm/poll/uaccess wrappers, and Android Binder UAPI. `rust_binder_fops` is the C-visible vtable assigned to binderfs Binder device inodes.

Risks: all `unsafe extern "C"` callbacks assume binderfs passed valid pointers and correct private data. Foreign arc ownership must match open/release exactly. The module init path lacks a shown exit/unregister path in this file, so unload semantics depend on kernel module infrastructure elsewhere. Layout exports must track struct changes.

Test signals: module load, binderfs mount, device open/close, ioctl/mmap/poll/flush smoke tests, stats/state/proc/transactions file reads, trace/stats counter increments, and repeated process log creation with duplicate pids returning `EEXIST` as non-fatal.
