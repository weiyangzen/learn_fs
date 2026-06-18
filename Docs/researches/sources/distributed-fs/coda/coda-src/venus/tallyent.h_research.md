# sources/distributed-fs/coda/coda-src/venus/tallyent.h

## Purpose
This header declares the tally entry structure and tally-list API for summarizing available/unavailable work or cache quantities by priority and user.

## Important APIs, Types, and Functions
`TallyStatus` has `TSavailable`, `TSunavailable`, and `TSunknown`. `tallyent` stores a dlist link, priority, uid, available/unavailable block/file counts, and an incomplete flag. It declares `InitTally`, `Find`, `Tally`, `TallyPrint`, `TallySum`, and global `TallyList`.

## Control Flow
The intended lifecycle is initialize the global list, feed entries with `Tally()`, optionally print or sum, then reset by calling `InitTally()` again.

## State and Persistence Behavior
The declared state is transient and process-local. Counts are derived summaries and do not persist across Venus restarts.

## Dependencies and Integration Points
It depends on `dlist.h`. Friend declarations show integration with tally functions and user task notification code that inspects private counters.

## Risks and Test Signals
Risks are the exposed global pointer and private-data friend coupling. Tests should compile all consumers, verify initialization before use, and validate that `TallySum()` and `TallyPrint()` remain consistent with field semantics.
