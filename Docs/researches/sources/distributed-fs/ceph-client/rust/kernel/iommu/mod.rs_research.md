# sources/distributed-fs/ceph-client/rust/kernel/iommu/mod.rs

## Purpose
`iommu/mod.rs` is the Rust IOMMU support namespace.

## Important APIs, Types, and Functions
It exposes `pub mod pgtable`.

## Control Flow
There is no runtime control flow.

## State and Persistence
No state is defined here; page table state is owned by `iommu/pgtable.rs`.

## Dependencies and Integration Points
The module makes Rust IOMMU page table wrappers available under `kernel::iommu::pgtable`.

## Risks
Only page-table support is exposed. Broader IOMMU domain/device APIs are not represented in this facade.

## Test Signals
Build tests should verify `kernel::iommu::pgtable` imports and configuration coverage for users that depend on it.
