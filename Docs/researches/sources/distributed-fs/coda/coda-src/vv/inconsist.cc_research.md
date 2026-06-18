# sources/distributed-fs/coda/coda-src/vv/inconsist.cc

## Purpose

`inconsist.cc` implements Coda version-vector comparison, consistency checking, arithmetic, initialization, invalidation, maximum-vector synthesis, and formatting.

## Important APIs, Types, and Functions

It defines `NullSid`. `VV_Cmp_IgnoreInc()` compares vector slots and returns `VV_EQ`, `VV_DOM`, `VV_SUB`, or `VV_INC`. `VV_Cmp()` treats the `VV_INCON` flag as immediate inconsistency before delegating. `VV_Check()` and `VV_Check_IgnoreInc()` call `VV_Check_Real()` to find a dominant set in a `VSG_MEMBERS` pointer array. `VV_BruteForceCheck()` is a fallback when the fast pass sees conflicting dominance. `AddVVs()`, `SubVVs()`, `InitVV()`, `IsRunt()`, `InvalidateVV()`, `GetMaxVV()`, `SPrintVV()`, and `FPrintVV()` provide manipulation and display helpers.

## Control Flow

Comparison iterates all version sites and tracks whether one vector dominates or submits; mixed directions produce inconsistency. The fast group check chooses the first non-null vector as current dominator, scans forward, removes submissive vectors, updates the dominator when needed, or switches to brute force on inconsistency. The brute-force path searches for a vector that dominates or equals all others, nulling submissive entries when equality is not required.

## State and Persistence Behavior

All functions operate on caller-provided structs and arrays. There is no persistence. Some checks mutate the input pointer array by nulling non-dominant entries, which is part of the API contract.

## Dependencies and Integration Points

It depends on `ViceVersionVector`, `ViceStoreId`, `VSG_MEMBERS`, and flag macros from `inconsist.h`, plus Coda/RPC2 integer layout. It is used by repair/conflict logic and tools such as `cfs` for version-vector display and manipulation.

## Risks

`VV_Check_*` mutates `vvp`, so callers must pass a scratch array if they need the original list. `SPrintVV()` has a compile-time assumption that `VSG_MEMBERS == 8`. Arithmetic helpers do not check overflow or underflow. `GetMaxVV()` picks store ids based on `domindex` conventions that callers must understand. `IsRunt()` treats an inconsistency-only zero vector as runt, which is deliberate but subtle.

## Test Signals

Tests should cover equality, dominance, submission, mixed inconsistency, explicit incon flags, ignore-incon behavior, equality-required checks, null vector slots, dominant-set mutation, brute-force fallback cases, max-vector store-id selection for `-1`, `-2`, and explicit indices, runt detection, invalidation, and formatted output.
