# sources/distributed-fs/coda/coda-src/util/bstree.h

## Purpose
Declares the intrusive binary search tree utility.

## Important APIs, Types, And Functions
`BSTCFN` is the comparison callback. `BstGetType` chooses min or max removal. `bstree`, `bsnode`, and `bstree_iterator` define the tree, embedded node base class, and traversal order.

## Control Flow
Callers derive objects from `bsnode`, provide a comparator, insert nodes, remove known nodes or min/max nodes, and scan with `bstree_iterator`.

## State And Persistence
Tree membership is stored inside each `bsnode` through private parent/child/tree pointers. The tree does not own derived objects or persist anything.

## Dependencies And Integration Points
Includes C `stdio.h` for print overloads and is consumed by C++ Coda utilities requiring sorted intrusive storage.

## Risks
Copy construction and assignment abort only at runtime. There is no balancing, locking, or safe-delete iterator contract. Derived destructors must ensure nodes are removed before object destruction.

## Test Signals
Compile derived-node users, validate comparator behavior, and test tree membership and ordering invariants after every operation.
