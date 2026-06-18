# sources/distributed-fs/coda/coda-src/librepair/predicate.cc

## Purpose
Conflict-classification predicates for replicated directory resolution. Each predicate decides whether a grouped directory entry set is strongly equal, weakly equal, all-present, renamed, subset-created, subset-removed, or maybe subset-removed.

## APIs, Types, and Functions
Defines predicate functions matching `PtrFuncInt`: `ObjectOK()`, `WeaklyEqual()`, `AllPresent()`, `Renamed()`, `SubsetCreate()`, `SubsetRemove()`, and `MaybeSubsetRemove()`, plus helpers `Equal()`, `nObjectSites()`, and `nlinks()`. Exports `Predicates[]` and `nPredicates`.

## Control Flow, State, and Persistence
Predicates inspect entry counts, version-vector equality, StoreId equality, version-vector site coverage, hard-link count from `lstat()`, directory-vnode status, and parent lookup through `GetParent()`. Some cases prompt the user via `Parser_getbool()` when automation is uncertain, especially hard-link and subset-remove decisions. No persistent state is changed; results steer later cure generation.

## Dependencies and Integration
Depends on resolver structures, Vice version-vector helpers (`InitVV()`, `AddVVs()`, `VV_Cmp()`), parser prompting, filesystem metadata, and inconsistency definitions. Predicate array ordering must match constants in `predicate.h`.

## Risks and Test Signals
Risks include heuristic classification when replica-to-version-vector slots are unknown, interactive prompts in classification, hard-link path construction assumptions, fixed `MAXHOSTS`, and reliance on `GetParent()` availability. Test signals are correct predicate index for known conflict scenarios, no automation for hard-link ambiguous cases unless confirmed, and matching array length/order with header constants.
