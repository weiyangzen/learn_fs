# sources/distributed-fs/coda/coda-src/util/bstree.cc

## Purpose
Implements an intrusive binary search tree where user objects derive from `bsnode` and ordering is supplied by a callback.

## Important APIs, Types, And Functions
`bstree` implements `insert`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `IsOrdered`, and printing. `bsnode` tracks its tree, parent, and children. `bstree_iterator` traverses ascending or descending.

## Control Flow
Insertion rejects nodes already in a tree, walks from the root using `CmpFn`, and breaks equal-key ties by object address. Removal uses standard BST splice logic, promoting the minimum node from the right subtree for two-child removals. `get()` removes min or max. Iteration starts at first/last and follows successor/predecessor links.

## State And Persistence
State is entirely intrusive: the tree owns only topology pointers and counters, not object memory. Statistics count inserts, removes, and gets. No persistence exists.

## Dependencies And Integration Points
Depends on `bstree.h`, C stdio/unistd/string, and caller-provided comparison functions. It is a base utility for sorted object registries in older Coda code.

## Risks
The tree is unbalanced, so sorted insertion can degrade to linear depth. Iterators are unsafe if the current node is deleted. Address tie-breaking makes ordering process-address-dependent. Destruction calls `clear()` and silently detaches nodes rather than deleting derived objects.

## Test Signals
Insert unique and duplicate-key nodes, remove leaf/one-child/two-child/root nodes, iterate in both orders, check `IsOrdered()`, clear populated trees, and run mutation-during-iteration tests to document unsafe cases.
