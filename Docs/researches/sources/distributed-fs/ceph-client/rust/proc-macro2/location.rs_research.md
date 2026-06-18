# sources/distributed-fs/ceph-client/rust/proc-macro2/location.rs

## Purpose

This small module defines `LineColumn`, the source position pair returned by `Span::start` and `Span::end` when span locations are enabled.

## Important APIs, types, and functions

`LineColumn` has public `line` and `column` fields. Lines are one-indexed and columns are zero-indexed UTF-8 character columns. It derives copy, clone, debug, equality, and hash, and implements `Ord` and `PartialOrd` by comparing `line` first and `column` second.

## Control flow

The only executable logic is ordering. `cmp` chains `self.line.cmp(&other.line)` with `self.column.cmp(&other.column)`, and `partial_cmp` always returns `Some(self.cmp(other))`.

## State and persistence behavior

`LineColumn` is immutable value state. It does not own file data, source maps, or spans; it is a snapshot representation of a position computed elsewhere.

## Dependencies and integration points

It depends only on `core::cmp::Ordering`. `lib.rs` publicly re-exports it behind `span_locations`, and `wrapper.rs` constructs it from compiler span probes or fallback spans.

## Risks and test signals

The key risk is semantic mismatch between compiler and fallback column numbering, especially because compiler line/column APIs may be one-indexed and wrapper code adjusts columns with `saturating_sub(1)`. Tests should compare ordering, start/end values from parsed token streams, Unicode column handling, and fallback vs compiler behavior when the feature is enabled.
