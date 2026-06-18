# sources/control-plane/mayastor/io-engine/src/lvs/lvol_iter.rs

## Purpose
This file provides iterators over SPDK lvols globally and within one LVS pool.

## Important APIs, types, and functions
`LvolIter(BdevIter<()>)` scans all bdevs and returns only those convertible to `Lvol`. `LvsLvolIter` walks the raw SPDK tail queue of `spdk_lvol` objects for a specific `Lvs`.

## Control flow
`LvolIter::next` loops over `BdevIter` until `Lvol::ok_from` succeeds or iteration ends. `LvsLvolIter::new` stores the first `tqh_first` pointer from the store. Its `next` returns the current lvol and advances to `link.tqe_next`.

## State and persistence behavior
The iterators hold raw or wrapper iteration state only. They do not persist. `LvsLvolIter` is explicitly safe only while the underlying list is not modified.

## Dependencies and integration points
It depends on `crate::core::BdevIter`, `super::Lvol`, and SPDK lvol tail queue layout. `Lvs::lvols()` uses `LvsLvolIter`; global clone/snapshot listing often scans through bdevs.

## Risks and test signals
Raw pointer iteration can become invalid if async work or reactor activity mutates the lvol list during iteration. The comments warn callers not to run async code while holding the iterator. Tests should cover filtering non-lvol bdevs and pool-local iteration under stable lists; concurrency hazards require integration discipline.
