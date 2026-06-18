# sources/cloud-native/moby/internal/iterutil/iterutil_test.go

## Purpose
Unit tests for iterator utility helpers.

## Important APIs, Types, And Functions
- `TestSameValues` checks order-insensitive but duplicate-sensitive equality.
- `TestDeref` collects dereferenced integer pointers.
- `TestChain` and `TestChain2` verify concatenation for sequences and map iterators.
- `TestMap` and `TestMap2` verify transformation to strings and uppercase map keys.

## Control Flow
Tests build slices/maps, adapt them with `slices.Values` or `maps.All`, call iterutil helpers, collect with `slices.Collect` or `maps.Collect`, and compare expected values.

## State And Persistence
Only in-memory test data.

## Dependencies And Integration Points
Uses standard `maps`, `slices`, `strconv`, `strings`, and gotest assertions. Serves as regression coverage for `internal/iterutil`.

## Risks And Edge Cases
The tests do not cover early-yield cancellation or nil pointers for `Deref`. Map iteration order is irrelevant because maps are compared structurally.

## Test Signals
Passing confirms helper behavior for basic and duplicate cases, chained nested sequences, and one-/two-value mapping.
