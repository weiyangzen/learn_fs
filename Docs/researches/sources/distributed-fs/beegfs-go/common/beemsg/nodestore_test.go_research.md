<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go

Purpose: unit tests for `NodeStore` registration, lookup, and root metadata behavior.

Important APIs/types/functions: `TestAddAndGet`, `TestGetNodes`, and `TestMetaRootNode`.

Control flow: tests build a store, add metadata and storage nodes with overlapping numeric IDs but different node types, verify duplicate UID/alias/legacy ID rejection, resolve by legacy ID and alias, and check root metadata assignment rejects missing or non-meta nodes.

State and persistence: exercises in-memory store maps and connection store setup; no network I/O is performed.

Dependencies and integration points: depends on `testify/assert`, `beegfs` node identity types, and `NewNodeStore`.

Risks: does not cover `RequestTCP`, `RequestUDP`, buddy-group setters/getters, cleanup locking, clone isolation, or concurrent map access.

Test signals: good basic identity mapping coverage; transport and concurrency behavior are left to utility tests or integration usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go -->
