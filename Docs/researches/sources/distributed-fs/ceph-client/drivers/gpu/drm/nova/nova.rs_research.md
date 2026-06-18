# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/nova.rs

## Purpose
Defines the Nova Rust module root, submodules, and auxiliary driver registration metadata.

## Important APIs, Types, And Functions
Declares `mod driver`, `mod file`, and `mod gem`, imports `NovaDriver`, and invokes `kernel::module_auxiliary_driver!` with module name, author, description, and GPL v2 license.

## Control Flow
At module load, Rust-for-Linux registration hooks register the auxiliary driver type; probe behavior lives in `driver.rs`.

## State, Persistence, And Dependencies
Module-level state is owned by the kernel module/auxiliary driver registration framework.

## Integration Points
Integrates the Nova Rust source files into a single kernel module.

## Risks
Module metadata must match Kbuild/Kconfig expectations. No feature code exists here beyond registration.

## Test Signals
Signals are module load/unload, auxiliary driver registration, and successful compilation of all declared modules.
