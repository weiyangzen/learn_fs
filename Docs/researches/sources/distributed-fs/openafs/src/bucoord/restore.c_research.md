# sources/distributed-fs/openafs/src/bucoord/restore.c

## Purpose
Implements restore-job planning and execution. It maps requested volumes to BUDB dump lineages, builds an ordered tape/volume-fragment restore plan, supports dry-run output, and submits grouped restore RPCs to tape coordinators with correct full/incremental sequencing.

## Important APIs, Types, And Functions
Exported functions are `BackupName` and `bc_Restorer`; local helpers are `StripBackup`, `extractTapeSeq`, and `viceName`. Internal planning structures are `dumpinfo`, `volinfo`, `bc_tapeList`, and `bc_tapeItem`, representing dump chains, target volumes, tapes, and ordered restore fragments.

## Control Flow
`bc_Restorer` receives a `bc_dumpTask` slot. For each requested volume it finds the most recent matching dump before the requested date, or a caller-specified dump id, also trying `.backup` names when appropriate. It builds a dump list sorted from newer to older, attaches requested volume targets, then walks each dump’s parent chain back to the full dump. For each volume and each dump level from full to latest incremental, it calls `bcdb_FindVolumes`, sorts returned fragments into a global tape list by dump/tape sequence and tape position, and records restore server/partition and first/last dump flags. Dry-run mode prints either human-readable restore plans or file format suitable for `volsetrestore`. Execution mode converts tape items to `tc_restoreDesc` entries and submits contiguous batches to butc, choosing port offsets by dump level when multiple ports are supplied and waiting for each restore pass to finish before starting the next.

## State And Persistence
The restore plan is entirely in-memory and freed before return. Persistent effects are delegated to butc/volserver restore operations. Destination server/partition can be global for all restored volumes, or per-volume from input/evaluated volume metadata. The task’s `newExt`, `oldFlag`, `fromDate`, `parentDumpID`, `portOffset`, and `dontExecute` fields shape restore behavior.

## Dependencies And Integration Points
Depends on BUDB lookup wrappers in `ubik_db_if.c`, butc restore RPCs, RX connection helpers from `dump.c`, status queue helpers, command-populated `bc_dumpTask` structures, and OpenAFS volume/tape constants. `commands.c` prepares restore tasks and `dump.c` launches this function via `bc_StartDmpRst`.

## Risks And Test Signals
The planning logic is complex and allocation-heavy, with many linked-list insertion cases for appended dumps, fragmented volumes, and multi-level incrementals. Fixed-size volume-name buffers and extension concatenation need boundary coverage. The `viceName` alphabet string appears to omit `g`, which can affect dry-run partition formatting. The dynamic `dlevels` resize path must preserve existing chain data. Test signals include restoring explicit volumes, `.backup` fallback, `-usedump`, full plus incremental chains, fragmented volumes across tapes, appended dump ordering, multi-port restore level routing, dry-run `volsetrestore` output, abort/error status handling while waiting, and cleanup on BUDB or butc failures.
