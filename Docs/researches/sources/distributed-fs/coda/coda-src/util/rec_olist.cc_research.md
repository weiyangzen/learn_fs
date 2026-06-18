# sources/distributed-fs/coda/coda-src/util/rec_olist.cc

## Purpose
Implements the recoverable singly-linked circular intrusive list.

## Important APIs, Types, And Functions
`rec_olist` supports recoverable allocation, `Init`, `DeInit`, `insert`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, and printing. `rec_olink` has recoverable `Init()` and print helpers. `rec_olist_iterator` scans the list.

## Control Flow
List operations mirror `olist` but log the list, tail, predecessor, and changed node before pointer/count updates. `remove()` walks predecessor links from tail and handles singleton tail removal. `get()` removes the head.

## State And Persistence
`tail`, `cnt`, and each link's `next` pointer can be RVM persistent. No derived objects are freed by the list.

## Dependencies And Integration Points
Depends on `rec_olist.h`, `rvmlib`, and POSIX writes. Used by `rec_ohash` and persistent Coda structures.

## Risks
`DeInit()` aborts if nonempty. Iterator comments claim safe deletion support, but it does not precompute the next link, unlike `rec_smolist_iterator`; deleting current entries can still be risky. All mutations require transactions.

## Test Signals
Transactionally insert/append/remove/get singleton and multi-entry lists, test current-entry deletion behavior, verify abort recovery, and ensure `DeInit()` catches nonempty lists.
