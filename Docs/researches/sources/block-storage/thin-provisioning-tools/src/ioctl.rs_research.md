# File Research: sources/block-storage/thin-provisioning-tools/src/ioctl.rs

This file ports Linux asm-generic ioctl request-code construction to Rust.

Important behavior:
- Defines `RequestType` as `c_int` on musl and `c_ulong` otherwise.
- Defines architecture-dependent direction and size bit constants for MIPS/PowerPC/SPARC versus common architectures.
- Exposes masks and shifts for ioctl fields.
- Exports macros:
  - `ioc!`
  - `request_code_none!`
  - `request_code_read!`
  - `request_code_write!`
  - `request_code_readwrite!`

Integration points:
- Used by `file_utils.rs` to define `BLKGETSIZE64`.
- Available crate-wide through macro export.

Risks and notes:
- Mirrors Linux ABI details; correctness depends on target architecture cfgs matching kernel expectations.
