# sources/distributed-fs/ceph-client/rust/syn/bigint.rs

## Purpose

This helper implements a minimal decimal big integer used by `LitInt` support to expose base-10 digits without depending on a general big integer crate.

## Important APIs, types, and functions

`BigInt` stores decimal digits little-endian in `Vec<u8>`. `new` creates an empty zero value. `to_string` renders digits in normal order while suppressing leading zeroes. `reserve_two_digits` ensures enough capacity for add/multiply by small bases. `AddAssign<u8>` adds an increment less than 16. `MulAssign<u8>` multiplies by a base no greater than 16.

## Control flow

Parsing code elsewhere repeatedly multiplies by the literal base and adds the next digit. Carry propagation walks the digit vector in little-endian order. Rendering reverses digits and starts output at the first nonzero digit, defaulting to `"0"`.

## State and persistence behavior

State is an in-memory vector of decimal digits. It is not persisted beyond the literal conversion operation.

## Dependencies and integration points

It depends only on `std::ops::{AddAssign, MulAssign}`. Syn literal parsing uses it to normalize binary, octal, decimal, or hexadecimal integer literal text into base-10 digit strings.

## Risks and test signals

Risks include carry propagation bugs, incorrect zero rendering, assumptions about increment/base bounds being violated, and inefficient growth for very large literals. Tests should cover huge decimal/hex/binary/octal literals, zero and leading-zero forms, underscore-separated literals via caller logic, and maximum carry chains.
