# sources/distributed-fs/coda/coda-src/util/olist.h

## Purpose
Declares the intrusive circular singly-linked list utility.

## Important APIs, Types, And Functions
`otagcompare_t` supports tag matching. `olist`, `olist_iterator`, and `olink` provide list operations, traversal, embedded link state, and tag matching.

## Control Flow
Objects derive from `olink`, enter one list with `insert()` or `append()`, leave through `remove()` or `get()`, and are scanned with `olist_iterator`.

## State And Persistence
Only in-memory next pointers and a tail pointer are stored. Derived object lifetime remains external.

## Dependencies And Integration Points
Includes `stdio.h`; used by `ohash` and recoverable-list analogues.

## Risks
No compile-time prevention of copying, no locking, and no safe-delete iterator guarantee.

## Test Signals
Compile derived users and run list membership, tag matching, and iterator reset tests.
