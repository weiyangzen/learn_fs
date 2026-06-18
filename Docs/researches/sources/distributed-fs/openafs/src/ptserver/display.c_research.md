# sources/distributed-fs/openafs/src/ptserver/display.c

## Purpose
Formats protection database entries and continuation entries for diagnostics and tooling.

## Important APIs, Types, And Functions
Exports `pr_PrintEntry` and `pr_PrintContEntry`. Private `pr_TimeToString` formats timestamps using a shorter current-year format. Macros `PRINT_COMMON_FIELDS` and `PRINT_IDS` print common header fields, reserved fields, IDs, and PRBADID markers while honoring caller-selected host/network byte order through `host(a)`.

## Control Flow
`pr_PrintEntry` detects continuation entries accidentally passed as regular entries and redirects to `pr_PrintContEntry`. Otherwise it prints flags, id, next pointer, create/add/remove/change times, membership IDs, hash chain pointers, owner/creator, quota/count fields, owned/parent/sibling/child pointers, supergroup-specific fields when enabled, and the bounded name. `pr_PrintContEntry` prints common fields, legacy timestamp-like reserved fields, and continuation IDs.

## State And Persistence
Uses static buffers and cached current year in `pr_TimeToString`. Writes formatted output to a caller-supplied `FILE *`; no database state is changed.

## Dependencies And Integration Points
Used by `ptclient` and `prdb_check` for dumping entries. Depends on `ptserver.h`, `contentry`, `prentry`, and byte-order conventions.

## Risks And Test Signals
Risks include static time buffer reuse, assuming `FILE *` is valid, and layout drift with protection database structures. Test signals are readable dumps for regular, continuation, and supergroup entries in both host and network order.
