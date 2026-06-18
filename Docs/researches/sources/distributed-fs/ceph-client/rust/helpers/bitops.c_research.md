# sources/distributed-fs/ceph-client/rust/helpers/bitops.c

## Purpose
Provides Rust-callable bit manipulation and fallback find-bit helpers.

## APIs, Types, and Functions
Exports `rust_helper___set_bit()`, `rust_helper___clear_bit()`, `rust_helper_set_bit()`, `rust_helper_clear_bit()`, and conditional `_find_first_zero_bit`, `_find_next_zero_bit`, `_find_first_bit`, `_find_next_bit` wrappers when those are macros.

## Control Flow, State, and Persistence
Bit set/clear operations mutate caller-provided bitmaps; find helpers scan immutable bitmaps. Local state is absent and atomicity follows the wrapped C primitive.

## Dependencies and Integration
Depends on `linux/bitops.h` and `linux/find.h`. It integrates with bindgen because macro-only find helpers otherwise lack callable symbols.

## Risks and Test Signals
Risks include mixing atomic and non-atomic bit operations, volatile pointer expectations, and missing conditional symbols on some architectures. Test signals are Rust bitmap tests, concurrent bit operation stress, and cross-architecture builds.
