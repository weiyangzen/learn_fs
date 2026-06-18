# sources/distributed-fs/ceph-client/rust/kernel/generated_arch_warn_asm.rs.S

## Purpose
This generated template extracts architecture-specific warning assembly into Rust-accessible literal form.

## Important APIs, Types, and Functions
The file includes `<linux/bug.h>` and calls `::kernel::concat_literals!(ARCH_WARN_ASM("{file}", "{line}", "{flags}", "{size}"))`. It defines no runtime functions.

## Control Flow
The build preprocesses the file, expands `ARCH_WARN_ASM` with placeholder file, line, flags, and size arguments, and converts the expansion into concatenated Rust literals.

## State and Persistence
There is no runtime state. Generated assembly strings persist as build output.

## Dependencies and Integration Points
The file is tied to C `ARCH_WARN_ASM` macro definitions and Rust-side generated warning support.

## Risks
The macro's argument shape must stay synchronized with the template. Any architecture-specific syntax not representable in the concatenation path can break Rust warning generation.

## Test Signals
Architecture build coverage should verify successful preprocessing and correct generated warning assembly for normal Rust warning sites.
