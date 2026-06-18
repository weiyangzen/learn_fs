# sources/distributed-fs/coda/coda-src/librepair/predicate.h

## Purpose
Header defining the predicate function type, exported predicate table, and conflict-classification numeric constants.

## APIs, Types, and Functions
Defines `PtrFuncInt` as a pointer to functions receiving replica counts, `resreplica *`, grouped `resdir_entry **`, entry count, and realm string. Declares `Predicates[]` and `nPredicates`. Defines constants `STRONGLY_EQUAL`, `WEAKLY_EQUAL`, `ALL_PRESENT`, `SUBSET_RENAME`, `SUBSET_CREATE`, `SUBSET_REMOVE`, `MAYBESUBSET_REMOVE`, and `UNKNOWN_CONFLICT`.

## Control Flow, State, and Persistence
No runtime flow. The order of constants is the contract for indexing into `Predicates[]`.

## Dependencies and Integration
Requires resolver type declarations to be available before or through inclusion. Used by resolution code to classify grouped entries.

## Risks and Test Signals
Risks include no include guard, no direct includes for dependent types, and tight coupling between enum-like constants and array order. Test signals are compile-time inclusion and classification tests verifying index-to-meaning mapping.
