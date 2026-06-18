# sources/cloud-native/moby/internal/iterutil/iterutil.go

## Purpose
Provides small generic helpers for Go 1.23-style iterators: unordered multiset comparison, pointer dereferencing, sequence concatenation, and mapping for one- and two-value iterators.

## Important APIs, Types, And Functions
- `SameValues[T comparable]` counts yielded values from two `iter.Seq[T]` sequences and compares count maps.
- `Deref[T any, P *T]` converts `iter.Seq[P]` to `iter.Seq[T]` by dereferencing pointers.
- `Chain[T]` concatenates multiple `iter.Seq[T]` values.
- `Chain2[K,V]` concatenates multiple `iter.Seq2[K,V]` values.
- `Map[T,U]` and `Map2` apply mapping functions lazily.

## Control Flow
All helpers return lazy iterator functions except `SameValues`, which eagerly consumes both inputs into maps. Lazy helpers stop immediately when downstream `yield` returns false.

## State And Persistence
No persistent state. `SameValues` allocates temporary maps; mapping/chaining helpers keep only closure-captured inputs and functions.

## Dependencies And Integration Points
Uses standard `iter` and `maps` packages. Intended as internal glue for code using Go iterators.

## Risks And Edge Cases
`Deref` panics on nil pointers. `SameValues` requires comparable values and consumes entire sequences, which can be expensive or nonterminating for infinite iterators. Map helpers propagate mapper panics.

## Test Signals
Unit tests validate duplicate-aware comparison, dereferencing, chaining, map collection, and two-value map iteration transformations.
