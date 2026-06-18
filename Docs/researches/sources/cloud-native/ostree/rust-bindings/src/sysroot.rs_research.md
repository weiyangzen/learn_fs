# sources/cloud-native/ostree/rust-bindings/src/sysroot.rs

## sources/cloud-native/ostree/rust-bindings/src/sysroot.rs

Handwritten builder and file-descriptor helpers for `Sysroot`. `SysrootBuilder` can be configured with `path`, `mount_namespace`, and `flags`, then opened through `open` using newer libostree APIs. `Sysroot` also gets helpers such as `new_for_path`, `fd_as_file`, and `fd_borrow`.

Control flow constructs `gio::File` paths, calls the generated or FFI sysroot open/initialize path, and duplicates or borrows the sysroot directory fd safely enough for Rust callers. State and persistence are the sysroot's on-disk deployment repository and boot state; builder flags influence how libostree opens it.

Dependencies include `gio`, `Sysroot`, `BorrowedFd`, and `PathBuf`. Risks are raw fd ownership boundaries, feature availability, and opening/mount-namespace semantics that affect host system state. Local tests focus on builder defaults and path configuration rather than full sysroot mutation.
