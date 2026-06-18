# sources/distributed-fs/coda/coda-src/util/dict.h

## Purpose
Declares an abstract reference-counted dictionary framework.

## Important APIs, Types, And Functions
Core classes are `dictionary`, `assockey`, `assocval`, `assoc`, `assocrefs`, and `assocrefs_iterator`. `dictionary` inherits privately from the intrusive list implementation through its public base and uses `assoc` entries that privately derive from `dlink`.

## Control Flow
Derived assoc objects provide concrete keys/values, insert themselves into a dictionary at construction, are held by lookups and reference arrays, and are physically deleted only after suicide plus final release.

## State And Persistence
The declarations define in-memory object relationships only. Persistence, locking, and key storage are left to derived users.

## Dependencies And Integration Points
Depends on `coda_assert` and `dlist.h`. It is a reusable base for typed dictionaries elsewhere in Coda.

## Risks
Many required operations are enforced by runtime assertions instead of compile-time abstract pure virtuals. Users must respect the hold/release protocol exactly to avoid leaks or premature deletion.

## Test Signals
Compile concrete subclasses, check key equality dispatch, reference count transitions, iterator index reporting, and dictionary removal on last release.
