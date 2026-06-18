# sources/distributed-fs/ceph-client/rust/kernel/gpu.rs

## Purpose
`gpu.rs` is the top-level GPU subsystem module for Rust kernel abstractions.

## Important APIs, Types, and Functions
It conditionally exposes `pub mod buddy` when `CONFIG_GPU_BUDDY = "y"`.

## Control Flow
There is no runtime control flow. Module availability follows kernel configuration.

## State and Persistence
No state is defined. GPU allocator state is in `gpu/buddy.rs` when compiled in.

## Dependencies and Integration Points
The file integrates the Rust GPU buddy allocator wrapper into the public `kernel::gpu` namespace and respects Kconfig gating.

## Risks
Users must guard imports or feature use by configuration. Missing `CONFIG_GPU_BUDDY` means `kernel::gpu::buddy` is unavailable.

## Test Signals
Build matrix coverage should include configurations with and without `CONFIG_GPU_BUDDY`.
