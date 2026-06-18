# sources/cloud-native/moby/internal/sliceutil/sliceutil.go

## Purpose
Provides generic slice helpers for dereferencing pointer slices, deduplicating comparable slices while preserving first occurrence order, mapping slices, and turning a mapper function into a reusable slice mapper.

## Important APIs, Types, And Functions
- `Deref[T]` converts `[]*T` to `[]T`, returns nil for nil input, and skips nil pointers.
- `Dedup[T comparable]` tracks seen values in a map and appends first occurrences.
- `Map[S ~[]In, In, Out]` returns nil for nil input and otherwise maps every element into a same-length `[]Out`.
- `Mapper[In,Out]` returns a closure that applies `Map`.

## Control Flow
All functions are simple linear scans. `Map` preallocates exact output length; `Deref` and `Dedup` preallocate capacity and append conditionally.

## State And Persistence
No persistent state. `Dedup` allocates a temporary key map; other helpers allocate output slices as needed.

## Dependencies And Integration Points
No external dependencies. Intended for internal callers needing concise generic slice transformations.

## Risks And Edge Cases
`Deref` silently drops nil pointers, which may be surprising if callers need positional preservation. `Dedup` uses a map and therefore requires comparable element types. `Map` distinguishes nil input from empty input.

## Test Signals
Companion tests cover mapping values, nil and empty slice behavior, type conversion, and `Mapper` closures.
