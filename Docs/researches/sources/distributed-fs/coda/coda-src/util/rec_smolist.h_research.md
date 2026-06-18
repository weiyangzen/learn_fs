# sources/distributed-fs/coda/coda-src/util/rec_smolist.h

## Purpose
Declares the compact recoverable singly-linked list and documents its relationship to `rec_olist`.

## Important APIs, Types, And Functions
`rec_smolist` exposes only a `last` pointer internally and public insertion, append, removal, get, empty, and print operations. `rec_smolist_iterator` stores current and next links. `struct rec_smolink` contains a single `next` pointer.

## Control Flow
Callers embed `rec_smolist` as a small persistent list head and `rec_smolink` in list members, then mutate through transaction-annotated methods.

## State And Persistence
The type is designed for RVM persistence with very small per-list overhead. Initialization is caller-managed.

## Dependencies And Integration Points
Includes `coda_tsa.h` for transaction annotations and is used by Coda volume metadata structures.

## Risks
Absence of a count and constructor initialization makes misuse harder to diagnose. Link objects can belong to only one list at a time.

## Test Signals
Validate zero-initialized persistent list heads, safe-delete iteration, and committed recovery behavior.
