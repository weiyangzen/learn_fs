# sources/distributed-fs/eos/unit_tests/mgm/QuarkDBConfigTests.cc

## Purpose
Tests cleanup behavior in the QuarkDB-backed MGM configuration engine. It verifies when unused node configuration entries should or should not be removed.

## Important APIs, types, and functions
The test includes `QuarkDBConfigEngine` under `IN_TEST_HARNESS`, mutates `sConfigDefinitions`, sets `EOS_MGM_CONFIG_CLEANUP`, and calls `RemoveUnusedNodes()`.

## Control flow
It starts with empty and space-only config maps, then adds node status/stat entries. A node with status `on` is retained, a node with status `off` and no filesystems is removed, and a node with filesystem config entries is retained even if off. Extra space config entries do not trigger node removal.

## State and persistence
State is the in-memory config definition map, modeling QuarkDB-stored config keys. The test mutates process environment and unsets it at the end.

## Dependencies and integration points
Depends on Google Test and MGM QuarkDB config engine internals. It integrates with configuration maintenance and stale node cleanup.

## Risks and test signals
The test protects cleanup gating but mutates environment globally. Missing coverage includes multiple nodes, malformed fs keys, cleanup disabled behavior after unset, and verifying exact keys removed rather than only boolean return.
