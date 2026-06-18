# sources/distributed-fs/ipfs-kubo/test/cli/pin_ls_names_test.go

Purpose: validates `ipfs pin ls --names` and name filtering across direct, recursive, indirect, JSON, text, update, removal, GC, concurrency, and restart scenarios. It focuses on pin-name visibility and preservation in local pinning commands.

Important APIs and types: `pinInfo` and `pinLsJSON` model the JSON output shape. `setupTestNode` initializes a node and starts an offline daemon. Assertion helpers check named output, CID-only output, and absent CID/name pairs. Tests use `IPFSAddStr`, `PipeStrToIPFS`, `pin add`, `pin ls`, `pin update`, `pin rm`, `repo gc`, `cat`, and UnixFS/DAG commands.

Control flow: `TestPinLsWithNamesForSpecificCIDs` creates many isolated nodes and exercises named single-CID queries, multi-CID queries, full pin listing, type filters, JSON output, direct plus indirect pin relationships, update preservation, invalid/unpinned errors, special-character names, concurrent pin creation, removal, GC preservation, duplicate names, and daemon restart persistence. `TestPinLsEdgeCases` checks invalid pin types, the non-listable `internal` mode, fake paths, and unpinned CIDs.

State and persistence: pin names are expected to be stored with pin metadata, survive daemon restarts, transfer from old CID to new CID during `pin update`, and disappear when the pin is removed. GC must preserve named and unnamed pins while collecting unpinned blocks.

Dependencies and integration points: depends on the pinner, pin index, MFS/DAG/UnixFS creation, JSON encoding, output formatting, offline daemon operation, and datastore persistence. The tests also exercise concurrent CLI operations against one node.

Risks and test signals: exact text assertions may fail if command formatting changes. Concurrent pin operations can expose pin-index races. Indirect-pin checks depend on directory DAG layout. Critical failure signals include missing names with `--names`, leaked names without `--names`, panic for `--type=internal`, name loss across update/restart, or GC deleting pinned content.
