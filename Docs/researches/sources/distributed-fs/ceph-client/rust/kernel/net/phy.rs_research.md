# sources/distributed-fs/ceph-client/rust/kernel/net/phy.rs

Purpose: wraps Linux PHYLIB for Rust PHY drivers. It exposes a typed `Device`, driver trait/vtable generation, registration RAII, PHY IDs, and a `module_phy_driver!` macro.

Important APIs/types/functions: `DeviceState`, `DuplexMode`, `Device`, `flags`, `Adapter<T>`, `DriverVTable`, `create_phy_driver<T>`, `Driver`, `Registration`, `DeviceId`, `DeviceMask`, and `module_phy_driver!`. Device methods cover PHY ID/state/link/autoneg, speed/duplex mutation, register read/write, paged reads, generic PHY reset/init/aneg/suspend/resume/status helpers, and link/ability helpers.

Control flow: PHYLIB invokes C callbacks in `DriverVTable`; each callback casts `phy_device` into `Device` under PHYLIB locking/exclusivity assumptions and calls the corresponding Rust `Driver` method, converting `Result` into errno. `create_phy_driver` builds a C `phy_driver` with function pointers only for trait methods implemented according to `#[vtable]` `HAS_*` constants. `Registration::register` registers a pinned static slice of vtables; drop unregisters it. `module_phy_driver!` generates a module wrapper, static driver array, registration in `Module::init`, and MDIO device table.

State and persistence behavior: PHY device state is kernel-owned `phy_device` memory. Driver vtables and device tables are static module data. `Registration` owns the fact that the driver slice is registered and unregisters on drop. No durable persistence is written.

Dependencies and integration points: depends on PHYLIB bindings, `RawDeviceId`, `Device` wrappers, register abstractions in `net/phy/reg.rs`, module macros, and kernel device ID table generation. It is the Rust entry point for MDIO/PHY drivers.

Risks: `Device::from_raw` is private and unsafe because method safety depends on PHYLIB callback context and locking. Bitfield offsets for link/autoneg are manually hard-coded pending bindgen support. Callback coverage must match `Driver` optional method flags exactly. `module_phy_driver!` uses `static mut DRIVERS`; safety relies on anonymous-constant encapsulation and C-only use after pinning.

Test signals: build tests for a sample PHY driver using `module_phy_driver!`, callback invocation tests for implemented and omitted vtable entries, registration failure for empty slices, ID/mask generation tests, and integration tests reading/writing both C22/C45 registers through `Device`.
