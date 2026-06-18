## sources/distributed-fs/ceph-client/rust/kernel/soc.rs

Purpose: wraps Linux SoC device registration so Rust drivers can publish SoC identity attributes under `/sys/devices/socX` and keep the backing strings alive for the registration lifetime.

Important APIs/types/functions: `Attributes` contains optional `CString` fields for `machine`, `family`, `revision`, `serial_number`, and `soc_id`. `BuiltAttributes` owns the backing attributes and an opaque `soc_device_attribute` populated with C string pointers. `Registration` is a pinned drop handle whose `new` registers with `soc_device_register` and whose drop unregisters.

Control flow: `Attributes::build` converts optional CStrings to nullable C pointers and stores the owned strings alongside the C attribute struct. `Registration::new` pin-initializes built attributes, passes their mutable pointer to `soc_device_register`, wraps the returned non-null `soc_device`, and unregisters on pinned drop.

State/persistence: state is in-memory registration plus sysfs-visible SoC attributes managed by the kernel. `Registration` lifetime controls visibility.

Dependencies/integration: uses `CString`, `Opaque`, `NonNull`, pin-init, `from_err_ptr`, and C `include/linux/sys_soc.h` bindings.

Risks: pointers inside `soc_device_attribute` must always point into still-owned `CString` buffers. Pinning matters because external kernel code may retain the attribute pointer. Registration returns are both error-pointer checked and null-checked. Dropping unregisters; leaking the handle leaves the SoC device registered.

Test signals: no local tests. Useful tests register sample attributes, inspect sysfs fields, and verify unregister on drop with optional fields omitted.
