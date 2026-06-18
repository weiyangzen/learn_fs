# sources/distributed-fs/coda/coda-src/venus/tallyent.cc

## Purpose
This file implements a priority/user tally list used to accumulate available, unavailable, and unknown cache/task quantities. It groups counts by `(priority, uid)` in sorted order.

## Important APIs, Types, and Functions
`TallyList` is the global sorted `dlist`. `tallyent` stores priority, uid, available/unavailable block and file counts, and an incomplete flag. `tallyentPriorityFN()` orders entries by priority then uid. `InitTally()` resets the list and deletes existing entries. `Find()` locates an entry. `Tally()` creates or updates an entry for a status. `TallyPrint()` logs per-uid entries, and `TallySum()` aggregates total blocks/files across the list.

## Control Flow
Callers must initialize `TallyList` with `InitTally()`. Each `Tally()` call finds an existing `(priority, uid)` entry or inserts a new one, then increments counts depending on `TSavailable`, `TSunavailable`, or `TSunknown`. Deleting a `tallyent` removes its dlist link. The `TESTING` block provides a standalone exerciser.

## State and Persistence Behavior
All state is transient. The tally does not write RVM or filesystem state; it summarizes availability information for later reporting or notification. `TSunknown` preserves incomplete state without adding block/file counts.

## Dependencies and Integration Points
It depends on `dlist`, Coda assertions, `vcrcommon`, and Venus logging when not under `TESTING`. The header exposes `NotifyUsersTaskAvailability()` as a friend, indicating task availability notification code reads private fields.

## Risks and Test Signals
Risks include global mutable state, no synchronization, mandatory initialization, destructor assertions when `TallyList` is null, and a likely logging typo in `TallySum()` where pointer values are printed for total size/unknown fields. Tests should cover sorted insertion, repeated updates, unknown status, list reset deletion, sum accuracy, and per-uid print filtering.
