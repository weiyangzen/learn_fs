# sources/cloud-native/nydus/rafs/src/mock/mod.rs

## Purpose
`mock/mod.rs` is the module index and re-export surface for RAFS test mocks.

## Important APIs, Types, And Functions
It declares `pub mod mock_chunk`, `pub mod mock_inode`, and `pub mod mock_super`, then publicly re-exports all items from those modules with `pub use mock_chunk::*`, `pub use mock_inode::*`, and `pub use mock_super::*`.

## Control Flow
There is no runtime control flow. The file controls compile-time module wiring and import ergonomics for tests and other internal code that use `crate::mock::*`.

## State And Persistence
No state is stored and no persistent data is read or written.

## Dependencies And Integration Points
This module integrates the three mock implementations into a single namespace. `mock_inode.rs` references `super::mock_chunk::MockChunkInfo` and `super::mock_super::CHUNK_SIZE`; external tests can import `MockChunkInfo`, `MockInode`, `MockSuperBlock`, and `CHUNK_SIZE` through `crate::mock`.

## Risks
The main risk is namespace churn: changing re-exports or module names can break tests that depend on broad `crate::mock::*` imports. Because the mocks are partial implementations, this convenient export surface can also make it easy to use them in tests that need stronger production fidelity.

## Test Signals
There are no direct tests for this module. Successful compilation and the unit tests in `mock_chunk.rs`, `mock_inode.rs`, and `mock_super.rs` validate the module wiring.
