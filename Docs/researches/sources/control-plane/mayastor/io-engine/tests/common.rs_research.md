# sources/control-plane/mayastor/io-engine/tests/common.rs

Purpose: thin re-export module that exposes the shared `io_engine_tests` harness to integration tests in this directory.

Important APIs/types/functions: `pub use io_engine_tests::*;` makes compose builders, Mayastor test harnesses, file helpers, bdev I/O helpers, fio helpers, macros, and RPC builders available as `common::...`.

Control flow: no runtime logic.

State and persistence: none.

Dependencies and integration points: centralizes the external test support crate import for all sibling tests.

Risks and edge cases: any broad re-export can hide where helpers come from and can make tests sensitive to helper crate API changes.

Test signals: not a test itself; all sibling tests depend on it compiling.
