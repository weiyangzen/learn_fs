# sources/distributed-fs/ceph-client/rust/kernel/interop.rs

## Purpose
`interop.rs` is the namespace for low-level Rust-to-C kernel interoperability helpers.

## Important APIs, Types, and Functions
It declares `pub mod list`, exposing C intrusive list helpers.

## Control Flow
No runtime logic exists in this facade. It intentionally keeps interop utilities separate from ordinary Rust data structures.

## State and Persistence
No state is held here.

## Dependencies and Integration Points
The module is used by wrappers that must interact with C-owned structures, such as the GPU buddy allocator's list of allocated blocks.

## Risks
The module comment warns that these helpers are not general-purpose Rust collections. Misuse can bypass safer Rust ownership models.

## Test Signals
Build tests should verify `kernel::interop::list` remains available for intended low-level modules and that higher-level code uses safer native collections where possible.
