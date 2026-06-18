# sources/distributed-fs/openafs/src/butc/lwps.c

## Purpose
`lwps.c` implements worker-side tape coordinator support: logging, exclusive device access, operator and callout prompting, unmounting, restore from tape/XBSA, tape labeling, label reading, expiration checks, and volume-header/trailer parsing.

## Important APIs, Types, and Functions
Logging APIs are `TapeLog`, `TLog`, `ErrorLog`, and `ELog`. Device APIs are `EnterDeviceQueue()` and `LeaveDeviceQueue()`. Prompting/unmount APIs are `FFlushInput()`, `callOutRoutine()`, `PromptForTape()`, and `unmountTape()`. Restore uses `struct restoreParams`, `GetRestoreTape()`, `GetVolumeHead()`, `restoreVolume()`, `restoreVolumeData()`, `xbsaRestoreVolume()`, `xbsaRestoreVolumeData()`, `SkipTape()`, `SkipVolume()`, and `Restorer()`. Labeling uses `GetNewLabel()`, `updateTapeLabel()`, `Labeller()`, `PrintTapeLabel()`, and `ReadLabel()`. Format parsing uses `VolHeaderToHost()`, `ReadVolHeader()`, `ExtractTrailer()`, `FindVolTrailer()`, `FindVolTrailer2()`, and `readVolumeHeader()`.

## Control Flow
Restore workers take the device latch, instantiate tape state unless XBSA, allocate buffers, iterate restore descriptors, mount and seek media, and call `UV_RestoreVolume()` with callbacks that stream tape/XBSA data. Multi-fragment volumes continue across tapes when trailers set `contd`. Label workers prompt/mount, validate permanent-name and expiration rules, write labels, and delete obsolete BUDB records. `ReadLabel()` runs synchronously under the device latch.

## State and Persistence Behavior
Runtime state includes log handles, `lastPass`, `debugLevel`, `autoQuery`, `globalTapeConfig`, `deviceLatch`, `BufferSize`, `dataSize`, `tapeblocks`, `bufferBlock`, and optional `butxInfo`. Persistent effects include restored volume data through volserver calls, optional local `restoretofile`, tape label writes, and BUDB deletion of overwritten dump entries.

## Dependencies and Integration Points
Depends on `butm` tape APIs, `UV_RestoreVolume`, BUDB lookup/deletion, process spawning/waiting for callout scripts, shared status/list helpers, and the tape format emitted by `dump.c`.

## Risks and Test Signals
Risks include fixed-size string copies, long-held device locks during prompts/I/O, callout abort cleanup, trailer-detection fragility, a suspicious version-0 `VolHeaderToHost()` copy direction, skip policy after restore failures, and global `restoretofile`. Test restore across one and multiple fragments, malformed trailers, callout exit codes, label expiration/permanent-name behavior, XBSA server switching, and status/abort propagation.
