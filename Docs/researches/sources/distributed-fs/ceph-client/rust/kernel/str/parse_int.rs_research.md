## sources/distributed-fs/ceph-client/rust/kernel/str/parse_int.rs

Purpose: implements kernel-style integer parsing for `BStr`, including optional signs and radix prefixes compatible with `kstrtol`/`kstrtoul` conventions.

Important APIs/types/functions: sealed private `FromStrRadix` abstracts per-integer parsing and negation. `strip_radix` detects `0x`, `0o`, `0b`, and leading-zero octal. Public `ParseInt` exposes `from_str`. `impl_parse_int!` implements the trait for signed/unsigned 8-, 16-, 32-, 64-bit and pointer-sized integer types.

Control flow: `from_str` handles a leading `-` by stripping radix from the rest, parsing digits as `u64`, then calling `from_u64_negated`. Non-negative paths strip radix and use the target type's `from_str_radix` after UTF-8 validation. Negation handles signed minimum exactly using two's-complement wrapping.

State/persistence: no state.

Dependencies/integration: uses `BStr`, `core::str::from_utf8`, Rust integer `from_str_radix`, `TryFrom`, and kernel `EINVAL`.

Risks: parsing requires UTF-8 digit bytes; invalid bytes map to `EINVAL`. Leading `0` means octal, so strings like `09` fail. Negative values for unsigned types fail except the implementation's `ABS_MIN == 0` edge maps `-0` to zero. `u64` is chosen because 128-bit integers are not universally available.

Test signals: doctests cover zero, hex, octal, binary, signed negatives, overflow boundaries, and unsigned overflow. Additional tests should include `+` handling, invalid prefixes, and `-0`.
