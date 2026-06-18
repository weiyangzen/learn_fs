# sources/distributed-fs/ceph-client/rust/proc-macro2/rcvec.rs

## Purpose

This file provides a small copy-on-write vector abstraction used by the fallback token stream implementation to share token storage cheaply while allowing mutation when necessary.

## Important APIs, types, and functions

`RcVec<T>` wraps `Rc<Vec<T>>`. `RcVecBuilder<T>` owns a mutable `Vec<T>` during construction. `RcVecMut<'a, T>` wraps a mutable vector borrow. `RcVecIntoIter<T>` owns a `vec::IntoIter<T>`. `RcVec` exposes `is_empty`, `len`, `iter`, `make_mut`, `get_mut`, and `make_owned`. Builders expose `new`, `with_capacity`, `push`, `extend`, `len`, `is_empty`, and `build`. Mutable views expose `push`, `extend`, and `truncate`.

## Control flow

Mutation either uses `Rc::make_mut` to clone-on-write, `Rc::get_mut` to mutate only unique storage, or `make_owned` to take the vector if uniquely held and clone otherwise. Iteration is delegated to the inner vector iterator.

## State and persistence behavior

The persistent state is reference-counted token storage. Clones share the same vector until mutation. `make_owned` can drain unique storage with `mem::take`, which avoids unnecessary allocation when extending or rebuilding token streams.

## Dependencies and integration points

It depends on `alloc::rc::Rc`, `alloc::vec`, `core::mem`, and slices. Fallback `TokenStream` and `TokenStreamBuilder` use it to support cheap token stream cloning and mutable building.

## Risks and test signals

Risks are clone-on-write aliasing bugs, accidental mutation of shared vectors, capacity/length mistakes during builder conversion, and unwind-safety trait drift. Tests should clone streams, mutate one clone, verify the other is unchanged, iterate builder-owned vectors, and run `quote` workloads that repeatedly extend fallback streams.
