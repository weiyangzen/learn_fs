# sources/distributed-fs/ceph/src/mds/Capability.cc

## Purpose
`Capability.cc` implements serialization, diagnostics, test instances, and key state transitions for `Capability`, the per-client capability record attached to a `CInode`. Capabilities track what a client wants, what the MDS has issued, what is pending after revocation, migration sequence numbers, feature compatibility flags, and revocation history.

## Important APIs And Types
Nested wire/state structs implemented here are `Capability::Export`, `Capability::Import`, and `Capability::revoke_info`. `Export` carries cap id, wanted, issued, pending, client snap follow point, issue sequence, migrate sequence, last issue stamp, and state flags. `Import` carries the cap id and issue/migration sequence needed to reattach caps after migration. `revoke_info` records caps held before a revoke, the sequence, and the last issue value.

The `Capability` constructor initializes session list membership, cap generation, stale-session handling, and client feature flags. It sets state bits when the connection lacks inline data, file layout v2 pool namespace, or quota features. `get_client`, `is_stale`, `is_valid`, `revalidate`, `mark_notable`, `maybe_clear_notable`, `set_wanted`, `encode`, `decode`, `dump`, and `generate_test_instances` provide the main behavior in this file.

## Control Flow And State Behavior
`confirm_receipt` is the key update routine. When a client acknowledges the latest sequence, it clears revokes, replaces issued caps with the client-reported caps, and intersects pending caps so the method never adds bits. If revocation is still incomplete, it records a new revoke entry and ensures the cap is notable. For older acknowledgements, it discards obsolete revoke records, updates the matching revoke's `before` field, recalculates issued caps, or reconstructs issued as `caps | pending` if no revoke entry remains. When revocation finishes, it removes the inode/session revoking list entries and may clear notable state. The return value is the set of bits actually revoked.

`set_wanted` keeps inode-level `num_caps_notable` accounting consistent when wanted caps enter or leave notable ranges. It marks the capability notable or attempts to clear it based on issued/pending/client-writeable state. Encode/decode preserve last sent sequence, last issue stamp, wanted bits, pending bits, and revoke list; decode calls `set_wanted` so inode accounting is updated and then recalculates issued caps from revoke state.

## Dependencies And Integration Points
This file depends on `Capability.h`, `CInode.h`, `SessionMap.h`, `Mutation.h`, `BatchOp.h`, Ceph buffer encoding, `Formatter`, debug logging, and capability string helpers. It is integrated with `CInode` cap maps, `Session` cap LRU/list operations, inode notable counters, open-file-table tracking through `CInode::adjust_num_caps_notable`, and migration code that exports/imports cap state.

## Persistence And Compatibility
The encode paths use Ceph versioned encoding macros. `Capability::Export` is encoded at version 3 with legacy compatibility down to version 2; the `state` field is decoded only for struct version 3 and newer. `revoke_info` and `Capability` use legacy-compatible version 2 blocks. The `generate_test_instances` methods are dencoder signals for compatibility and regression coverage.

## Risks
The main risk is incorrect revocation accounting. If `_issued`, `_pending`, `_revokes`, and notable list membership diverge, clients may retain write caps too long or the MDS may wait forever for revokes already completed. `set_wanted` relies on a valid inode pointer for notable accounting; detached or imported capabilities must be careful about when this is called. Feature flags are captured from the session connection at construction, so reconnect and import paths must preserve or refresh compatibility expectations.

## Test Signals
Important tests include dencoder round trips for `Export`, `Import`, `revoke_info`, and `Capability`; cap revoke acknowledgement cases for current and stale sequences; wanted cap transitions that increment and decrement inode notable counts; stale session construction; feature-gated state bits for old clients; and migration export/import preserving sequence and pending state.
