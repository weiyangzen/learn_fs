<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block.rs

## Purpose
This small file is the root Rust block-layer module and re-exports the blk-mq submodule.

## Important APIs, Types, and Functions
It declares `pub mod mq` and exposes sector-related constants: `SECTOR_MASK`, `SECTOR_SHIFT`, `SECTOR_SIZE`, and `PAGE_SECTORS_SHIFT`, all sourced from generated kernel bindings.

## Control Flow and State
There is no runtime control flow. The file is a namespace and constant bridge.

## State and Persistence Behavior
The constants are compile-time values reflecting the target kernel configuration and architecture. No mutable state is owned here.

## Dependencies and Integration Points
The file depends on `bindings` and integrates Rust block drivers with the `block::mq` API in child modules. The constants provide shared units for code converting pages, bytes, and sectors.

## Risks
Risks are mainly configuration drift: Rust constants must match C kernel bindings. Incorrect use of sector units by callers can still cause block size/capacity bugs.

## Test Signals
No local tests are present; build-time binding generation and downstream block driver compilation are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block.rs -->
