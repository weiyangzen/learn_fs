# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dump.h

## Purpose
Defines the userspace-visible binary frame dump ABI used by rt2x00 debugfs. It documents the dump stream format and provides stable type and header definitions shared between kernel and userspace tools.

## Important APIs, Types, And Functions
`enum rt2x00_dump_type` identifies RX done, TX queued, TX done, and beacon dump frames. `struct rt2x00dump_hdr` contains version, header/descriptor/data lengths, RT/RF/revision IDs, frame type, queue and entry indexes, and second/usecond timestamp fields. `DUMP_HEADER_VERSION` is currently 3.

## Control Flow
`rt2x00debug_dump_frame()` prepends `rt2x00dump_hdr` to copied descriptor and frame bytes before queueing to the debugfs dump file. Userspace reads records as `[header][hardware descriptor][802.11 frame]` and uses length fields to advance.

## State And Persistence
The header has no runtime state. ABI persistence is explicit: new fields must be appended so older userspace can locate descriptor and data using `header_length`.

## Dependencies And Integration Points
Used by `rt2x00debug.c` and userspace dump readers. Types use fixed-endian Linux integer annotations to keep on-disk/read-stream format stable.

## Risks
Changing existing fields or version semantics breaks userspace tools. Timestamp precision is microsecond derived from `ktime_get_ts64()`. Descriptor format remains hardware-specific, so consumers need chip/queue context.

## Test Signals
Read frame dump from debugfs, validate header lengths/endian fields, parse all dump types, and run old userspace readers against newer headers with appended fields.
