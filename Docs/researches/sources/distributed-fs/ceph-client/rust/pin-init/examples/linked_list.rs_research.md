# sources/distributed-fs/ceph-client/rust/pin-init/examples/linked_list.rs

## Purpose
This example implements an intrusive circular doubly linked list node that must not move after insertion. It demonstrates `#[pin_data(PinnedDrop)]`, self-referential initialization with `&this in`, and pinned drop unlinking.

## Important APIs, Types, And Functions
`ListHead` has `next`, `prev`, and a pinned `PhantomPinned` field. `ListHead::new()`, `insert_next()`, and `insert_prev()` return `impl PinInit<Self>`. `next()` returns the next node unless the list is self-referential, and `size()` walks the circular list. `PinnedDrop for ListHead` unlinks a node on drop. `Link(Cell<NonNull<ListHead>>)` stores mutable raw links and provides `next`, `prev`, `replace`, `set`, and pointer access helpers.

## Control Flow
Initialization uses `pin_init!(&this in Self { ... })` to create self-links or splice a new node next to an existing list node. Insertion updates neighboring links by replacing `Cell` contents while creating the new node fields. Drop checks whether the node is linked to another node and, if so, updates adjacent `prev`/`next` links to bypass the dropped node.

## State And Persistence
State is in per-node `Cell<NonNull<ListHead>>` pointers. The list exists only in memory and relies on pinning to keep stored addresses valid. Dropping a node mutates neighboring nodes to maintain the circular list invariant.

## Dependencies And Integration Points
It depends on `pin_init`, `NonNull`, `Cell`, `PhantomPinned`, and the example `Error` type. Other examples, especially `mutex.rs`, reuse `ListHead` as a wait-list primitive.

## Risks And Edge Cases
The linked list uses unsafe raw pointers and assumes all nodes remain pinned and alive while linked. Incorrect insertion or premature drop can corrupt neighbors. `Cell` allows mutation through shared references, so external synchronization is the caller's responsibility. `size()` can loop forever if the circular invariant is broken.

## Test Signals
Signals include inserting stack- and heap-pinned nodes in several positions, dropping middle nodes, walking list order, validating `size()`, and running under Miri or sanitizers to catch dangling links.
