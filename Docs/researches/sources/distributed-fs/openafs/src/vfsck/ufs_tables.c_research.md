<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_tables.c -->
# sources/distributed-fs/openafs/src/vfsck/ufs_tables.c

## Purpose
Defines static lookup tables used by UFS fragment accounting and allocation bitmap scans.

## Important APIs, Types, And Functions
Exports `around[9]`, `inside[9]`, `fragtbl124[256]`, `fragtbl8[256]`, and `fragtbl[MAXFRAG + 1]`. There are no functions.

## Control Flow
No runtime control flow is present. `fragacct` indexes these tables to determine which fragment sizes are available in a byte-sized free-fragment map.

## State And Persistence
All state is static read-only table data. It influences how pass 5 rebuilds on-disk fragment summaries but does not itself write.

## Dependencies And Integration Points
`ufs_subr.c` imports these arrays. The tables are inherited from BSD UFS code and must match filesystem bit ordering for supported fragment counts.

## Risks And Test Signals
Risks are accidental table corruption, wrong `MAXFRAG` assumptions, or platform `u_char` differences. Test signals are pass 5 fragment summary consistency across filesystem fragment sizes and allocation bitmap unit tests comparing table-driven results to brute-force fragment scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_tables.c -->
