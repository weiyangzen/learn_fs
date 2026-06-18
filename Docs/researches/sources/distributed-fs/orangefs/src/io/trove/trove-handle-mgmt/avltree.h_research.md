# sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/avltree.h

## Purpose
Generic macro-parameterized AVL tree header for handle-management data structures. It requires callers to define datum and key macros before inclusion.

## Important APIs, Types, And Functions
Requires `AVLDATUM`, `AVLKEY_TYPE`, and `AVLKEY`; optionally supports `AVLALTKEY`. Defines `enum AVLSKEW`, `enum AVLRES`, `struct avlnode`, `AVLWORKER`, and prototypes for insert, remove, access, alternate access, highest lookup, depth-first traversal, and post-order traversal.

## Control Flow
Consumers maintain a root `struct avlnode *` and call `avlinsert`/`avlremove` with heap-owned data and keys. Traversal callbacks receive node, caller parameter, and depth.

## State And Persistence
Defines in-memory tree node shape and balancing metadata only. Persistence is outside the AVL layer.

## Dependencies And Integration Points
The preprocessor enforces macro definitions from a domain header such as `trove-extentlist.h`. It is included by `avltree.c` and users that need tree node declarations.

## Risks And Test Signals
Risks include misuse with non-heap payloads, mismatched key macro types, multiple include contexts with incompatible macro definitions, and declaration typo/comments drift. Compile coverage in handle-management modules and generic AVL behavioral tests are the primary signals.
