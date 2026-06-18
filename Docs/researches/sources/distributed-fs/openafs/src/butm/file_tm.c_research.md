# sources/distributed-fs/openafs/src/butm/file_tm.c

Purpose: implements the backup tape module vtable for a real tape device or file-backed simulated tape. It defines the on-media format: tape labels, software file begin/end/EOD marks, hardware EOF marks, and 16 KiB data blocks with block marks.

Important APIs and types: `butm_file_Instantiate` fills `struct butm_tapeInfo.ops` with mount/dismount/create/readLabel/seek/read/write methods. Helpers include `ForkIoctl`, `ForkOpen`, `ForkClose`, `ForwardSpace`, `BackwardSpace`, `WriteEOF`, `Rewind`, `incSize`, `incPosition`, `readData`, `SeekFile`, `NextFile`, `WriteTapeBlock`, and `ReadTapeBlock`. `struct progress` in `tmRock` tracks `usd_handle_t`, mount id, and read/write sequencing. Static `config` stores device, tape size, filemark size, and port offset.

Control flow: mount opens the configured device with USD, sets read-only fallback, initializes counters, and stores progress state. Create/write-label rewinds or appends, writes a network-order label block, and emits EOF. File writes require `WriteFileBegin`, one or more `WriteFileData` calls, then `WriteFileEnd`; EOD writes a special filemark. Reads validate label/filemark/data block types and return `BUTM_ENDVOLUME`, `BUTM_EOF`, `BUTM_EOD`, or `BUTM_BADBLOCK` according to stream markers.

Persistence and dependencies: durable bytes are on the configured tape device or file. It depends on USD, LWP/IOMGR polling, com_err for config errors, roken, and platform tape ioctls. It uses child processes on non-pthread Unix to avoid blocking the whole process on tape open/ioctl/close.

Risks and tests: static globals (`config`, `tapeBlock`, `TapeBlockSize`) and the external `isafile` make concurrent independent tape instances unsafe. Several fixed 64-byte path buffers can truncate or overflow if upstream config permits long device strings. The read/write state machine is strict and callers must preserve operation order. `butm_test.c` covers bad-operation paths; `test_ftm.c` covers write/readback and append behavior with configured media.
