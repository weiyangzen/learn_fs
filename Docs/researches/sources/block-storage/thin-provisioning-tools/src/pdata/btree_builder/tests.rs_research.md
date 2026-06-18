# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/tests.rs

Exercises `NodeBuilder` balancing and shared-node import behavior. Tests verify empty, underfull-root, full-root, two-leaf, balanced, and three-leaf construction; pushing regular shared nodes; unpacking first regular shared node when buffered entries are insufficient; handling underfull shared roots; and unshifting regular/underfull previous nodes.

It also validates residency with `EntriesCounter`, verifies serialized leaf contents, checks reused block numbers for shared leaves, expects panic for multiple underfull nodes pushed at once, allows underfull roots one by one, and rejects unordered keys.
