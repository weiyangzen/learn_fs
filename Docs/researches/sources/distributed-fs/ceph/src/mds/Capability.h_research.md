# sources/distributed-fs/ceph/src/mds/Capability.h

## Purpose

`Capability.h` declares the MDS-side representation of a CephFS client capability on an inode. It models the protocol described in the file comments: MDS issues caps to clients, later updates may grant or revoke bits, clients confirm receipt or flush dirty metadata, and MDS must track enough sequence history to distinguish current releases from stale or racing revocations.

The class is also the migration payload carrier for caps during subtree export/import. `Capability::Export` captures the full transferable cap state, `Capability::Import` captures compact import-side identity and sequence data, and `revoke_info` preserves revocation history while acknowledgments race with new issues.

## Important APIs, Types, And Functions

`Capability` derives from `Counter<Capability>` and uses `MEMPOOL_CLASS_HELPERS`, so object count/increment/decrement signals feed MDS telemetry and allocation comes from the MDS mempool. Its external identity is `(CInode*, Session*, cap_id)`, with client identity resolved from `Session`.

The most important state accessors are `pending()`, `issued()`, `revoking()`, `wanted()`, `get_last_seq()`, `get_last_issue()`, `get_mseq()`, `get_last_issue_stamp()`, and `get_last_revoke_stamp()`. `pending` is what the MDS currently wants the client to retain; `issued` includes caps still believed to be in the client's possession, including revoking bits.

`issue(unsigned c, bool reval=false)` handles grants and revocations. When `c` removes bits from `_pending`, it appends `revoke_info(_pending, last_sent, last_issue)`, replaces `_pending`, keeps `_issued` broad enough to cover in-flight caps, marks the cap notable, increments `last_sent`, and returns the new sequence. Add-only grants OR bits into `_pending` and `_issued` and trim obsolete revocation history. `issue_norevoke()` is the add-only variant that also clears `STATE_NEW`.

`confirm_receipt(ceph_seq_t seq, unsigned caps)` is declared here and implemented in `Capability.cc`; it reconciles client acknowledgments/releases with `_revokes`, clears revoking list membership when `_issued == _pending`, and returns the bit mask that was actually revoked. `clean_revoke_from(ceph_seq_t li)` drops revocation history older than a known last-issue value, recalculates `_issued`, and removes revoking-list items when revocation has ended.

`make_export()`, `merge(const Export&, bool auth_cap)`, and `merge(int otherwanted, int otherissued)` are migration-facing APIs. `make_export()` exports cap ID, wanted/issued/pending bits, `client_follows`, issue sequence, incremented migration sequence, `last_issue_stamp`, and exported state flags. `merge()` combines pending and issued bits, wanted bits, client follow state, selected state flags, and optionally authoritative `mseq`.

The state flags are meaningful protocol and feature gates: `STATE_NOTABLE`, `STATE_NEW`, `STATE_IMPORTING`, `STATE_NEEDSNAPFLUSH`, `STATE_CLIENTWRITEABLE`, `STATE_NOINLINE`, `STATE_NOPOOLNS`, and `STATE_NOQUOTA`. `MASK_STATE_EXPORTED` limits which flags survive migration. `mark_clientwriteable()`, `clear_clientwriteable()`, `set_wanted()`, `mark_notable()`, and `maybe_clear_notable()` drive session LRU placement and inode notable-cap counters.

## Control Flow And Data Flow

Normal issue flow starts with Locker/Server code deciding a cap mask, then calling `issue()` or `issue_norevoke()`. If revocation is involved, `_revokes` records the prior pending bits and sequence. The message sent to the client carries `last_sent`; later client updates call `confirm_receipt()` with a sequence and retained cap mask. Exact-sequence confirmations clear or rebuild revocation history; older confirmations drop only the historical revokes they cover.

Migration flow exports `Capability::Export` from the source MDS and merges it into the destination cap. Import tracking uses `Capability::Import` for `cap_id`, `issue_seq`, and `mseq`. Peer export/import maps appear in `Migrator`, `MDCache`, `Server`, and `Mutation`, so this header defines the cross-rank cap state contract.

Notability flow keeps caps that matter near the active session list. Writable, revoking, and wanted read/write caps mark the cap notable and call `Session::touch_cap`; when those conditions disappear, `maybe_clear_notable()` moves the cap to the bottom with `touch_cap_bottom`. This is central to cap trimming and session pressure behavior.

## State And Persistence Behavior

Persistent/encoded cap state includes `last_sent`, `last_issue_stamp`, `_wanted`, `_pending`, and `_revokes`; decode restores `_pending`/`_revokes` and recalculates `_issued`. Export encoding additionally persists transfer-specific fields including cap ID, issued/pending/wanted, `client_follows`, sequence values, migration sequence, stamp, and exported state flags. Import encoding is intentionally smaller.

In-memory-only fields include raw pointers to `CInode` and `Session`, intrusive list items for session/snaprealm/revoking queues, `lock_caches`, suppress count, last revoke stamp, warning counters, and `lock_cache_allowed`. `cap_gen` couples a cap to the owning session generation; stale sessions make caps invalid until `revalidate()`.

Sequence correctness is the core persistence risk. `_issued` is derived from `_pending` plus `_revokes`, so any lost or misordered revoke history can make the MDS think a client still has or no longer has authority. `mseq` tracks migration ordering, while `last_issue` records the last issue point that clients must have seen for safe release semantics.

## Dependencies And Integration Points

This file depends on CephFS cap bit definitions from `include/ceph_fs.h`, `mdstypes.h`, `snapid_t`, `version_t`, `utime_t`, Ceph buffer encoding, `Counter`, mempool helpers, and intrusive `xlist`/`elist` containers. It forward-declares `CInode`, `Session`, and `MDLockCache`.

Integration points include `Capability.cc` for encoding and state transitions, `CInode` cap maps and export helpers, `SessionMap` and `Session` cap lists, `Locker` cap issue/revoke decisions, `Migrator` subtree export/import, `MDCache` rejoin/import tracking, `Server` client message handling, and `MDSRank`/`MDCache` performance counters that read `Capability::count()`.

## Risks And Edge Cases

Revocation races are the main risk. A release can race with revocation; `clean_revoke_from()` exists specifically to prevent MDS from waiting forever on revokes the client never processed. Older `confirm_receipt()` sequences must not wipe newer revokes. Add-only grants prune historical revokes only when all revoked bits are no longer outside `_pending`.

State flags mix protocol, migration, and client-feature compatibility. Exporting too many flags would leak local state; exporting too few would lose writeability or feature restrictions. `STATE_NOINLINE`, `STATE_NOPOOLNS`, and `STATE_NOQUOTA` are set from session connection feature bits, so sessionless or stale caps have different assumptions.

`maybe_clear_notable()` asserts the cap is notable before clearing; callers must maintain notable state consistently. `mark_notable()` assumes `session` is present. `dec_suppress()` does not guard underflow. `merge()` calls `issue()`, so imports can generate new sequences and revocation history if pending/issued masks are inconsistent.

## Test Signals

Useful tests exercise dencoder round trips for `Capability`, `Export`, `Import`, and `revoke_info`; cap issue/revoke sequences where `confirm_receipt()` is exact, stale, and racing; migration export/import merge preserving wanted, pending, `client_follows`, and exported flags; session staleness/revalidation; and cap trim behavior that moves caps between notable and bottom lists. Runtime signals include MDS cap counters, revoking-cap queues draining, absence of stuck revocation warnings, and correct client behavior after subtree migration.
