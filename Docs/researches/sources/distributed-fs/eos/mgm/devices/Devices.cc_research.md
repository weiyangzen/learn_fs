# sources/distributed-fs/eos/mgm/devices/Devices.cc

## Purpose
Implements the MGM devices recorder thread. It periodically extracts SMART/device health information from registered filesystems, decompresses JSON payloads, stores current in-memory maps, and persists per-device records into the EOS proc namespace.

## Important APIs and Functions
- `Start` launches `Recorder`; `Stop` joins it.
- `Recorder` waits for namespace boot, only runs extraction/storage on the master MGM, and sleeps for a configured interval.
- `Extract` walks `FsView` spaces/filesystems, collects `stat.health.z64smart` and `stat.health`, decompresses SMART JSON, updates extraction timestamp, and swaps maps under mutex.
- `Store` parses each JSON payload for `serial_number`, creates or opens `<mDevicesPath>/<serial>.<fsid>`, writes `sys.smart.json` and `sys.smart.status`, and updates mtime.

## Control Flow
The recorder waits 15 seconds after namespace boot, logs with backoff, skips work on non-master nodes, then repeats `Extract` and `Store`. `Extract` uses short `FsView` read locks to collect ids and per-filesystem strings, then decompresses outside the lock. `Store` prefetches file metadata, creates missing proc files, sets birth-time on creation, and updates attributes.

## State and Persistence
Runtime state includes shared maps from fsid to JSON, fsid to space, fsid to SMART status, protected by `fsJsonMutex`, plus `lastExtraction`. Persistent state is namespace proc files named by disk serial and fsid with attributes `sys.smart.json`, `sys.smart.status`, and `sys.eos.btime` on creation.

## Dependencies and Integration Points
Uses `FsView`, global `gOFS`, namespace prefetching/view operations, JSON parsing, `SymKey::ZDeBase64`, MGM stats, assisted threading, and EOS metadata locking. `SetDevicesPath` must be called by the owning MGM setup before storage.

## Risks
- Environment override `EOS_MGM_DEVICES_PUBLISHING_INTERVAL` is parsed into `rtime` but never assigned back to `snoozetime`, so the override has no effect.
- Destructor calls `Stop`; if `Start` was never called, behavior depends on `AssistedThread::join`.
- `Store` writes attributes without an explicit namespace-wide lock in this file, relying on file locks and view APIs.
- Invalid or serial-less JSON is silently skipped after debug/error logs.
- Serial numbers become path components without obvious sanitization.

## Test Signals
Tests should cover interval environment handling, extraction with disappearing filesystems, decompression failures, JSON serial parsing, creation/update of proc files, attribute writes, master-only behavior, and Stop without Start.
