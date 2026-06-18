# sources/distributed-fs/ceph-client/rust/kernel/debugfs/callback_adapters.rs

## Purpose
`callback_adapters.rs` lets debugfs files use function items or non-capturing closures for read and write behavior without requiring the backing data type itself to implement `Writer` or `Reader`. It does this with transparent wrapper types that have the same representation as the wrapped data.

## Important APIs, Types, and Functions
The unsafe `Adapter` trait exposes the original `Inner` type for transmuting `FileOps<AdapterType>` back to `FileOps<Inner>`. `WritableAdapter<D, W>` implements `Reader` with a callback `W` while delegating `Writer` to `D`. `FormatAdapter<D, F>` implements `Writer` with a formatting callback `F` and dereferences to `D`. `NoWriter<D>` is a transparent passthrough used for write-only callback files. `materialize_zst<F>()` creates a static reference to an inhabited zero-sized function item/closure.

## Control Flow
The top-level debugfs constructors instantiate `FileOps` for an adapter stack, then call `.adapt()` one or more times to expose the operations as if they were for the original data type. At read or write time, the adapter implementation materializes the zero-sized callback type and invokes it against the underlying data reference.

## State and Persistence
The adapters contain only the wrapped data plus `PhantomData` for the callback type. They do not persist callback values; the callback type itself is the value, which is why only zero-sized function items and non-capturing closures are valid.

## Dependencies and Integration Points
This module depends on `debugfs::traits::{Reader, Writer}`, `fmt`, `UserSliceReader`, `Deref`, and the debugfs `FileOps::adapt` path. It is used by both owned `Dir` files and borrowed `ScopedDir` files for callback-based debugfs exports.

## Risks
The unsafe contract is narrow but important: the transparent adapter must be layout-compatible with the inner type, and `materialize_zst` assumes the callback type is inhabited and zero-sized. Accidentally accepting capturing closures would break this model. Adapter stacking also makes it easy to pick the wrong operation mode if the `.adapt()` chain is changed incorrectly.

## Test Signals
Compile-time tests should reject capturing closures, non-`Send`/`Sync` callbacks, and callbacks with wrong signatures. Runtime tests should exercise read-only, write-only, and read-write callback files and confirm the underlying data address is preserved through adapter casts.
