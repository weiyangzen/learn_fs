# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/nova_core.rs

Purpose: top-level Rust module entry for the Nova Core GPU driver. It wires submodules, PCI registration, debugfs root lifetime, firmware module metadata, and kernel module metadata.

Important APIs and types: `NovaCoreModule` implements `InPlaceModule`; `DebugfsRootGuard` clears the global debugfs root on drop; `MODULE_NAME` exposes kernel module metadata. Submodules include driver, falcon, firmware, gfw, gpu, gsp, regs, sbuffer, and vbios.

Control flow: module initialization creates `debugfs::Dir("nova_core")`, stores it in the global `DEBUGFS_ROOT`, then registers `driver::NovaCore` as a PCI adapter. Drop order unregisters the driver before clearing debugfs state.

State and persistence: uses a mutable static `DEBUGFS_ROOT` as temporary per-module global state. Driver registration persists for module lifetime and is released automatically by field drop order.

Dependencies and integration: integrates with the Rust kernel module system, PCI adapter registration, debugfs, firmware metadata builder, and all Nova-Core submodules.

Risks: `DEBUGFS_ROOT` is a `static mut` guarded only by initialization/drop ordering assumptions. Future concurrent probe or per-module data support changes should revisit this. Firmware list is supplied through `kernel::module_firmware!(firmware::ModInfoBuilder)`.

Test signals: build/module-load tests, PCI probe/unprobe behavior, debugfs directory lifetime checks, and firmware metadata generation are the relevant signals.
