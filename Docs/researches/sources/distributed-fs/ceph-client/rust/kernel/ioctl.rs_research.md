# sources/distributed-fs/ceph-client/rust/kernel/ioctl.rs

## Purpose
`ioctl.rs` provides Rust const helpers for constructing and decoding Linux ioctl command numbers using the asm-generic bit layout.

## Important APIs, Types, and Functions
Internal `_IOC` builds a command from direction, type, number, and size with `build_assert` bounds checks. Public constructors `_IO`, `_IOR<T>`, `_IOW<T>`, and `_IOWR<T>` encode no-arg, read, write, and read-write commands. Public decoders `_IOC_DIR`, `_IOC_TYPE`, `_IOC_NR`, and `_IOC_SIZE` extract fields.

## Control Flow
All operations are const arithmetic. Constructors validate each field against UAPI masks, shift into the correct positions, and OR the result. Typed constructors use `size_of::<T>()`.

## State and Persistence
No state is stored. The output is a `u32` ioctl number.

## Dependencies and Integration Points
The module depends on generated `uapi` ioctl constants and `build_assert`. Rust drivers can use it to define ioctl command constants matching C macros.

## Risks
The size field uses the Rust type layout; command ABIs must use `#[repr(C)]` or otherwise ABI-stable types. Direction names follow ioctl convention from the user pointer perspective, which can be confusing. Oversized types fail at compile time.

## Test Signals
Compare generated constants against C `_IO*` values for representative types, test field decoders, and verify compile-time rejection of out-of-range type/number/size values.
