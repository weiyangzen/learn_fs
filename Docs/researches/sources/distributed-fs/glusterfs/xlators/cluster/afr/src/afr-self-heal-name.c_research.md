# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-self-heal-name.c

## Purpose

`afr-self-heal-name.c` implements narrow self-heal for a single basename under a parent GFID. It repairs divergent lookup results, missing GFIDs, absent entries, stale entries, and compatible GFID differences for one name without crawling the entire directory.

This file is used by full self-heald tree walks and by callers that need to heal a specific name. It complements entry heal, which repairs directory contents in bulk.

## Important APIs, Types, and Functions

`afr_selfheal_name()` is the public entry point. It finds the parent inode, creates a self-heal frame, performs an unlocked inspection, and runs the locked name heal only if needed.

`afr_selfheal_name_unlocked_inspect()` does a cross-child lookup of the basename and sets `need_heal` when replies differ, `ENODATA` appears, or GFIDs differ.

`afr_selfheal_name_do()` takes an entry lock for the specific name, prepares parent source/sink state, performs a GFID-less lookup of the basename, and calls `__afr_selfheal_name_do()`.

`__afr_selfheal_name_prepare()` discovers parent entry changelogs and uses `afr_selfheal_find_direction()` for `AFR_ENTRY_TRANSACTION` to decide whether there is a clear source or a conservative merge.

`__afr_selfheal_name_do()` decides the single-name action: no-op, expunge if the source side is empty, type mismatch failure, GFID mismatch resolution, missing-GFID assignment, and impunge/recreate.

`afr_selfheal_name_type_mismatch_check()` detects incompatible file types among source candidates and emits split-brain events.

`afr_selfheal_name_gfid_mismatch_check()` detects divergent non-null GFIDs and calls `afr_gfid_split_brain_source()` to select or reject a source.

`__afr_selfheal_assign_gfid()` delegates missing GFID repair to `afr_lookup_and_heal_gfid()`, requiring all bricks up and locked if no GFID exists anywhere and the caller supplied `gfid_req`.

`__afr_selfheal_name_impunge()` recreates the chosen GFID on bricks that do not have it, using `afr_selfheal_recreate_entry()`. `__afr_selfheal_name_expunge()` deletes all existing copies when the source side is empty.

## Control Flow

The public path first checks whether a heal is necessary with unlocked lookups. If all observed replies agree, it returns success without taking locks. Otherwise, it locks the specific basename in the xlator domain.

Under the name lock, the code prepares parent direction from parent entry changelog xattrs. If there is no clear source or witnesses exist, it sets all locked non-sources as healed sinks and uses conservative merge.

The basename lookup uses `GF_GFIDLESS_LOOKUP` so divergent or absent GFIDs can be observed. The action step first rechecks whether the name actually needs repair. If all sources are `ENOENT`, it expunges existing copies. Otherwise it rejects type mismatch, resolves GFID mismatch or missing GFID, assigns a GFID where needed, and recreates the selected object on non-source bricks.

When GFID is completely absent, all children must be up and locked before assignment. This prevents assigning a caller-provided GFID while a down brick may already contain a conflicting GFID.

## State and Persistence Behavior

Persistent effects are limited to the single name: entry deletion, recreation, GFID assignment by `gfid-req`, and new-entry pending xattrs set indirectly by `afr_selfheal_recreate_entry()`.

Name heal does not perform data or metadata copy itself. Recreated entries may still require later data or metadata heal according to pending xattrs.

Request/response dictionaries can carry CLI GFID split-brain resolution inputs and outputs. `heal-op`, `child-name`, and `gfid-heal-msg` are passed through to common split-brain handling.

The function uses transient `sources`, `sinks`, `healed_sinks`, `locked_on`, and reply arrays, and wipes reply xdata before returning.

## Dependencies and Integration Points

This file depends heavily on entry/common helpers: `afr_selfheal_recreate_entry()`, `afr_selfheal_entry_delete()`, `afr_lookup_and_heal_gfid()`, `afr_gfid_split_brain_source()`, `afr_selfheal_find_direction()`, and entry locks.

It integrates with `afr-self-heald.c` full crawl through `afr_shd_selfheal_name()`, and with CLI split-brain resolution through request/response dicts.

It also depends on Gluster inode lookup semantics, `GF_GFIDLESS_LOOKUP`, and AFR parent pending xattrs to determine whether conservative merge is appropriate.

## Risks and Edge Cases

Single-name healing can recreate namespace entries without copying data or metadata immediately. Correct pending xattr marking is therefore essential for follow-up heals.

Missing-GFID assignment is dangerous if any brick is down; the all-up/all-locked guard must be preserved.

Source-empty detection treats source candidates with `ENOENT` as empty. Wrong source selection can turn a legitimate entry into an expunge operation.

GFID and type mismatch checks only consider valid successful replies. Error handling around `ENODATA`, `ENOENT`, and stale replies must remain precise to avoid false split-brain or missed repair.

## Test Signals

Tests should cover no-op matching replies, `ENODATA` needing heal, source-empty expunge, missing GFID with all bricks up, missing GFID with a down brick, GFID mismatch resolved by CLI source, unresolved GFID split brain, type mismatch split brain, conservative merge without clear source, recreate on absent sink, and response dict messages for GFID heal.

Runtime signals include type/GFID split-brain events, `gfid-heal-msg`, `sh-fail-msg` from common policy code, entry recreate/expunge warnings from entry helpers, and successful return from `afr_selfheal_name()` after previously divergent lookups.
