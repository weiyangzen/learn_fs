# sources/distributed-fs/ceph-client/drivers/android/Makefile

### Purpose
This Makefile maps Android driver configuration symbols to Binder, BinderFS, Binder allocator test, and Rust Binder build targets.

### Important APIs, Types, And Functions
There are no runtime APIs here. It adds `-I$(src)` to `ccflags-y` for trace event includes. Objects are `binderfs.o`, `binder.o`, `binder_alloc.o`, `binder_netlink.o`, `tests/`, and `binder/` for the Rust implementation.

### Control Flow
Kbuild conditionals include BinderFS, C Binder components, allocator KUnit tests, and Rust Binder according to Kconfig symbols.

### State, Persistence, And Dependencies
No runtime state exists. The compile flag is a build-time dependency for local trace headers. Object selection depends on Android Kconfig choices.

### Integration Points
It connects Android IPC sources to the kernel build and separates C Binder from Rust Binder directory builds while sharing the surrounding Android driver menu.

### Risks
Removing the local include flag can break trace-event compilation. Object mapping must remain synchronized with Kconfig dependencies, especially BinderFS and tests depending on C Binder.

### Test Signals
Build tests should verify all Android configuration combinations, trace include resolution, test directory inclusion, and Rust Binder directory build when selected.
