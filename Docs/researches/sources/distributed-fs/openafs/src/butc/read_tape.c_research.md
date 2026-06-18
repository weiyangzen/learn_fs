# sources/distributed-fs/openafs/src/butc/read_tape.c

## Purpose
`read_tape.c` is a standalone utility that scans OpenAFS backup tapes and optionally restores volume dump payloads to local files by reading the low-level file-tape block format directly through `usd`.

## Important APIs, Types, and Functions
It defines local tape/filemark wrappers matching `file_tm.c` and constants `TAPE_MAGIC`, `BLOCK_MAGIC`, and `FILE_MAGIC`. `readblock()` reads 16 KiB blocks and handles hardware filemarks. `printLabel()` and `printHeader()` display byte-swapped label/header metadata. `openOutFile()`, `writeData()`, `writeLastBlocks()`, and `closeOutFile()` control local extraction. `WorkerBee()` parses command options, opens the tape, classifies blocks, delays trailing blocks so trailers can be stripped, and performs scan/restore behavior.

## Control Flow
`main()` dispatches to `WorkerBee()`. The worker opens the tape read-only, allocates three 16 KiB buffers, reads blocks until requested skip/restore counts are satisfied or reads fail, and treats data, filemark, label, and unknown blocks differently. Volume headers open output, ordinary data is buffered, and any non-data block closes the output after stripping the volume trailer.

## State and Persistence Behavior
The utility does not modify tape media or BUDB. It writes local files with `usd_Open`, `USD_IOCTL_SETSIZE`, and `USD_WRITE`. It mutates parsed in-memory label/header fields while converting network order to host order.

## Dependencies and Integration Points
Depends on `afs/cmd.h`, `afs/usd.h`, `afs/tcdata.h`, and the same block/header/trailer format produced by `dump.c` and consumed by `lwps.c`/`recoverDb.c`.

## Risks and Test Signals
Risks include `filename[100]` overflow, heuristic trailer stripping, weak header validation, unusual hardware filemark behavior, and confusing `-noask` semantics. Test scan-only images, restore/skip/count options, trailer spanning one or two blocks, malformed magic/header data, repeated filemarks, and compare extracted payloads to normal restore output.
