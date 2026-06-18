# sources/distributed-fs/ceph-client/rust/kernel/ptr.rs

## Purpose
Provides pointer and address utility types: validated power-of-two alignments, alignment operations on unsigned integers, compile-time/dynamic-size helpers, const alignment, and re-export of raw pointer projection support.

## APIs, Types, and Functions
`Alignment` wraps `NonZero<usize>` and exposes const `new`, `new_checked`, `of<T>`, `as_usize`, `as_nonzero`, `log2`, and `mask`. `Alignable` defines `align_down` and overflow-checked `align_up`, implemented for `u8`, `u16`, `u32`, `u64`, and `usize`. `KnownSize` generalizes `size_of` for sized types and slices. `const_align_up` is a const-compatible `usize` alignment helper. The module exports `projection` and aliases `project_pointer!` as `ptr::project!`.

## Control Flow, State, and Persistence
Construction of `Alignment` validates the power-of-two invariant. Alignment operations compute masks, handle alignments larger than the target integer by aligning down to zero, and return `None` when aligning up would overflow or the alignment does not fit in the target type. There is no persistent state.

## Dependencies and Integration
Depends on `core::mem`, `NonZero`, and crate build assertions. It supports allocator, MMIO, DMA, and raw-pointer code that needs explicit alignment reasoning.

## Risks and Test Signals
Risks include callers assuming `align_up` succeeds for alignments wider than the integer type, arithmetic overflow regressions in const and runtime paths, and unsafely relying on `KnownSize` for invalid DST metadata. Test signals include power-of-two validation tests, integer-width edge tests, `usize::MAX` overflow checks, slice-size tests, and compile tests for `Alignment::of`.
