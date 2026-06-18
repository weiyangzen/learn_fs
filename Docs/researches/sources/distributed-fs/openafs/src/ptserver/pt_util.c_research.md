# sources/distributed-fs/openafs/src/ptserver/pt_util.c

## Purpose
Implements `pt_util`, an offline dump/load utility for the OpenAFS protection database. It reads the Ubik database file directly and can dump users, groups, and memberships to text or rebuild/update the database from text input.

## Important APIs, Types, And Functions
Key routines are `main`, `CommandProc`, `display_entry`, `add_group`, `display_groups`, `display_group`, `fix_pre`, `id_to_name`, `checkin`, and `check_core`. Globals include database file descriptor, data stream, cached `prheader`, `ubik_version`, hash table `hat`, group/user lists, `nflag`, `wflag`, and display flags (`DO_USR`, `DO_GRP`, `DO_MEM`, `DO_SYS`, `DO_OTR`).

## Control Flow
Command options choose write mode, display classes, hash traversal by name or id, prdb file, and data file. The utility opens `<prdb>.DB0` by default, reads the Ubik header and protection header, warns on bad magic, initializes ptserver database helpers, and either imports records or dumps chains. In write mode it parses base records and indented membership records, creates entries via ptutils helpers, fixes group counts/flags, and handles deferred foreign users. In dump mode it walks hash chains, prints selected users, accumulates groups, then prints group base records and optionally continuation-block members.

## State And Persistence
Read mode writes only text output. Write mode opens the database read-write/create, may initialize a zero Ubik version to epoch 2, and mutates protection entries through direct ptserver utility calls. It caches ID-to-name mappings in memory.

## Dependencies And Integration Points
Depends on Ubik internals, protection database structures, ptserver utility functions (`Initdb`, `FindByID`, `CreateEntry`, `AddToEntry`, `pr_ReadEntry`, `pr_WriteEntry`), command parsing, and pterror tables.

## Risks And Test Signals
Risks are direct database access while ptserver is active, text format parsing fragility, destructive write mode, memory leaks in helper lists, and version-change warning only after work is done. Test signals include stable dumps of known databases, import into disposable databases, version-change detection, name/id hash traversal parity, and member continuation handling.
