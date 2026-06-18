# sources/distributed-fs/ceph-client/drivers/android/Kconfig

### Purpose
This Kconfig menu exposes Android Binder IPC, the Rust Binder implementation, BinderFS, binder device naming, and Binder allocator KUnit tests.

### Important APIs, Types, And Functions
There are no runtime functions in this file. Symbols are `ANDROID_BINDER_IPC`, `ANDROID_BINDER_IPC_RUST`, `ANDROID_BINDERFS`, `ANDROID_BINDER_DEVICES`, and `ANDROID_BINDER_ALLOC_KUNIT_TEST`.

### Control Flow
Configuration dependencies ensure C Binder requires `MMU` and `NET`, Rust Binder requires `RUST`, `MMU`, and not C Binder, BinderFS depends on C Binder, device-name string is available for either Binder implementation, and allocator KUnit tests depend on C Binder plus KUnit.

### State, Persistence, And Dependencies
Kernel configuration persists chosen Binder implementation and default device names. The default Binder devices string is `binder,hwbinder,vndbinder`.

### Integration Points
The menu controls build inclusion for Android IPC drivers and testing support. BinderFS enables per-IPC-namespace Binder device allocation through a pseudo filesystem, while `ANDROID_BINDER_DEVICES` feeds binder device creation parameters.

### Risks
Selecting Rust Binder excludes C Binder, and BinderFS currently depends only on the C implementation. Misconfigured device names can break Android userspace expectations. KUnit test selection pulls test code into builds when enabled.

### Test Signals
Kconfig/build tests should cover C Binder, Rust Binder, BinderFS dependency behavior, custom `ANDROID_BINDER_DEVICES`, and KUnit test module inclusion.
