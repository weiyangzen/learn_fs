# sources/cloud-native/ostree/rust-bindings/src/auto/sysroot.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/sysroot.rs

Generated GObject binding for `OstreeSysroot`, the object managing bootable OSTree deployment state under a sysroot. Constructors include `new` and `new_default`. APIs cover initialization/loading (`ensure_initialized`, `initialize`, `initialize_with_mount_namespace`, `load`, `load_if_changed`, `unload`), locking (`lock`, `try_lock`, `unlock`, `lock_async`, `lock_future`), cleanup, repository access, deployment creation/staging/writing, kernel argument mutation, mutable/unlocked/pinned states, boot metadata, origin files, soft reboot and kexec features, and a `journal-msg` signal.

Control flow mirrors libostree sysroot operations and uses GLib main-context checks for async locking. State and persistence are central: methods read and mutate deployment directories, bootloader configuration, origin files, staged/pending/rollback deployment records, and cleanup state. This wrapper converts `Deployment`, `Repo`, `SysrootDeployTreeOpts`, `SysrootWriteDeploymentsOpts`, `glib::KeyFile`, and string arrays.

Risks are high because operations change bootable system state; callers must lock where required, respect cancellables, and handle feature-gated behavior. Some GIR-unhandled prune options remain commented. Tests are indirect through `sysroot.rs` builder tests and option-struct tests rather than this generated file itself.
