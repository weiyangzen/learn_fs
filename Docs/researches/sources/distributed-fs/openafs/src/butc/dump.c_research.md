# sources/distributed-fs/openafs/src/butc/dump.c

## Purpose
`dump.c` implements the tape-coordinator dump path for OpenAFS Backup: it creates BUDB dump/tape/volume records, streams volume dumps from volservers over Rx, writes volume headers/data/trailers to the configured tape module or XBSA backend, handles multi-pass retry behavior, tape changes, append mode, and XBSA dump deletion. It is the producer side for the tape format later consumed by `lwps.c`, `recoverDb.c`, and `read_tape.c`.

## Important APIs, Types, and Functions
- `struct dumpRock` is the dump worker's private state: current tape sequence/name/label, current volume index/status/start position, BUDB dump/tape entries, counters, and the active `dumpNode`.
- `calcExpirationDate()` converts backup expiration policy into an absolute `Date`.
- `Bind()` caches one Rx volserver connection keyed by server address; `ListOneVolume()` wraps `AFSVolListOneVolume()` and enforces exactly one result.
- `dumpVolume()` is the file/tape dump implementation. It opens a volserver transaction, starts `StartAFSVolDump()`, writes `TC_VOLBEGINMAGIC` and `TC_VOLENDMAGIC` headers, fragments volumes across tapes when near EOT, and queues BUDB volume rows via `addVolume()`.
- `xbsaDumpVolume()` is the XBSA analogue, wrapping `xbsa_BeginTrans()`, `xbsa_WriteObjectBegin/Data/End()`, and recording a single BUDB volume fragment for each volume object.
- `dumpPass()` iterates all volumes for a retry pass, refreshes VLDB location for later passes, decides retry/omit/abort/EOT behavior, and calls `flushSavedEntries()` after each volume action.
- `Dumper()` is the asynchronous worker entry point and owns device latch, buffer allocation, dump/tape finalization, status, and cleanup.
- `getDumpTape()` validates labels, append eligibility, expiration, overwrite risks, relabeling, old BUDB deletion, `useTape()`, and EOT margin setup.
- `makeVolumeHeader()` and `volumeHeader_hton()` define the on-tape volume header/trailer fields and byte order.

## Control Flow
`tcprocs.c` creates a `dumpNode`, status node, and detached `Dumper`. `Dumper()` takes `deviceLatch`, initializes tape or XBSA state, allocates buffers, finds prior dump metadata, creates a BUDB dump, obtains tape metadata, and runs up to `maxpass` dump passes. Each `dumpPass()` walks remaining volumes, optionally revalidates location through VLDB, streams the volume through `dumpVolume()`/`xbsaDumpVolume()`, flushes queued DB entries according to the result, and applies retry or omit policy. Final cleanup writes EOD, finishes tape and dump rows, waits for DB watcher, logs, marks task status, frees the node, and releases the device.

## State and Persistence Behavior
Persistent state is split between physical tape/XBSA objects and BUDB rows. Media is written before BUDB volume entries are flushed, reducing the chance of advertising unwritten data. Tape labels persist dump path/id/use count/expiration/cell/name. Runtime state depends on globals from `tcmain.c` such as `BufferSize`, `statusSize`, `maxpass`, `autoQuery`, `queryoperator`, `isafile`, and `groupId`. DB updates are queued in `savedEntries` and materialized by `flushSavedEntries()`.

## Dependencies and Integration Points
Integrates with Rx/volserver (`AFSVolTransCreate`, `StartAFSVolDump`, `rx_Read`), VLDB and BUDB client helpers, the `butm` tape module, `lwps.c` prompting/unmount/expiration helpers, shared status/list/device helpers, and optional XBSA `butx` APIs. The volume header/trailer contract is consumed by restore, scan, and standalone read utilities.

## Risks and Test Signals
Key risks are unlocked task-node access, fixed-size string copies, subtle EOT/append safety windows, queued DB/media consistency after crashes, partial XBSA object cleanup, and blocking operator prompts. Test with full/incremental dumps, unchanged volumes, EOT fragmentation, final-pass retry/omit/abort, append/relabel safety, BUDB row reconciliation, and XBSA dump/delete/server-switch paths.
