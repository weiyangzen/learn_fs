# sources/distributed-fs/moosefs/mfsmaster/storageclass.c

## Purpose
`storageclass.c` owns MooseFS master storage-class policy. It maps class ids to names/descriptions and create/keep/archive/trash placement modes, validates label expressions and erasure-coding settings, changelogs policy changes, serves class info/list packets, persists class definitions, and supplies chunk-placement policy to filesystem/chunk code.

## Important APIs, Types, And Functions
The private `storageclass` struct contains name/description, priority, export group, admin-only flag, archive mode/delay/min-size, min trash retention, global labels mode, four `storagemode` values, and file/directory reference counters.

Important public functions include class CRUD (`sclass_create_entry`, `sclass_change_entry`, duplicate/rename/delete variants and `sclass_mr_*` replay variants), class lookup/accessors, reference counters, placement-mode getters, storage-size/goal-equivalent helpers, joining-priority calculation, info/list serializers, store/load, new/default initialization, cleanup, reload, and init.

Compatibility helpers convert old mask-or-group label masks to expression bytecode and back. EC compatibility is tracked by `ec_current_version`, checked through `sclass_check_ec()`, and replayed through `sclass_mr_ec_version()`.

## Control Flow
Create/change validate names, labels, EC compatibility, archive mode, and count limits before updating `sclasstab`. Normal mutations write `SCSET`, `SCDUP`, `SCREN`, `SCDEL`, or `SCECVERSION` changelog records. Metadata-replay mutations validate expected ids and increment metadata version without writing new changelog entries.

Placement lookup chooses a create mode or keep/archive/trash mode depending on file flags. When runtime `MaxECRedundancyLevel` is lower than a stored EC redundancy count, getters return a temporary adjusted `storagemode`.

Info/list serializers are versioned. Older formats convert label expressions back to mask-or-group representation when possible and mask incompatible classes with `*` names. Newer formats include ids, descriptions, priorities, export groups, archive options, per-mode label modes, EC byte fields, unique masks, label expressions, fulfillment flags, and chunk counters.

`sclass_fix_matching_servers_fields()` periodically refreshes label-expression matching-server counters by calling chunk labelset helpers.

## State, Persistence, And Dependencies
The main state is `sclasstab[MAXSCLASS]`, `firstneverused`, `ec_current_version`, `MaxECRedundancyLevel`, `DefaultECMODE`, and a reusable `tmp_storagemode`.

`sclass_store()` writes expression size, EC version, then one variable-size record per active class with id, name/description, priority/export/admin/label/archive fields, four modes, and label expressions. A zero id terminates the stream.

`sclass_load()` supports pre-expression 3.x formats and newer expression formats from metadata versions `0x17` through `0x1C`. It skips old label descriptions, converts old mask groups, repairs or rejects malformed EC data depending on `ignoreflag`, derives missing defaults, clamps/normalizes older archive modes, and updates `firstneverused`.

`sclass_new()` creates default classes `2CP`, `3CP`, `EC4+1`, and `EC8+1` and enables EC version 2. `sclass_reload()` reads `DEFAULT_EC_DATA_PARTS`, allowing only 4 or 8.

Dependencies include `MFSCommunication.h` for constants and packet limits, `patterns.h` for class deletion side effects, `matocsserv.h`/`matoclserv.h` for EC feature compatibility and label matching, `chunks.h` indirectly through chunk labelset and counters, metadata/changelog/bio/datapack/config/main utilities, and logging/assertions.

## Integration Points
Filesystem code stores a storage-class id on files/directories and calls reference, permission, and policy getters. Chunk replication/placement code consumes `storagemode`, goal-equivalent, EC, label, and priority helpers. Client/admin code consumes `sclass_list_entries()` and `sclass_info()`. Export/session permission uses export groups through `sessions_check_sclass()`. Restore parses `SC*` changelog records into the `sclass_mr_*` functions.

## Risks
This file encodes many versioned wire and metadata formats. Any change to `storagemode`, label expression size, EC byte semantics, or changelog syntax must update store/load, list/info, restore parsing, and compatibility conversions together.

`tmp_storagemode` is a shared static returned by getter functions when EC redundancy is clamped. Callers must not retain it across later calls.

Reference counters are simple increments/decrements with no underflow checks. Incorrect filesystem integration could allow deletion of in-use classes or counter wrap.

`storageclass.h` declares `sclass_is_predefined()`, but this C file does not implement it.

## Test Signals
Tests should cover class create/change/delete/rename/duplicate, in-use delete rejection, changelog/replay id mismatch, EC version gating with simulated client/chunkserver minimum versions, `DEFAULT_EC_DATA_PARTS` reload, old metadata load conversions, malformed EC repair under ignore mode, store/load round trips, list/info packet size agreement for every format version, label-expression conversion compatibility, reference counters, and placement-mode selection for normal/archive/trash flags.
