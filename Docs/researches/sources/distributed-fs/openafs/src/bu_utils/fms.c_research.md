# sources/distributed-fs/openafs/src/bu_utils/fms.c

`fms.c` implements the `fms` utility, which estimates tape capacity and filemark size by writing data blocks and file marks until the tape reports an error/end condition. It is operational tooling for configuring backup tape characteristics.

Important APIs include `main`, `tt_fileMarkSize`, `fileMarkSize`, `rewindTape`, `fileMark`, `dataBlock`, and `quitFms`. It uses the OpenAFS `cmd` package for `-tape`, USD device handles for open/write/ioctl/close, and writes progress plus `fms.log`.

Control flow opens the tape read/write with write lock, rewinds, writes 16 KiB data blocks until failure to estimate capacity, closes/reopens/rewinds, then alternates data blocks and file marks until failure to estimate filemark cost. `dataBlock` caches a static zeroed buffer sized to the requested block and stores an incrementing integer at its start.

State and persistence include tape device contents, `fms.log` in the current directory, static data buffer/count, and global `eotEnabled`/`tapeDevice` values that are mostly unused. Dependencies are `afs/cmd.h`, `afs/usd.h`, tape ioctls (`USDTAPE_REW`, `USDTAPE_WEOF`), signals, and component version generation. Risks are destructive writes to the target tape, simplistic error handling where any write failure ends loops, possible division by zero if no file marks are written, SIGINT exiting without explicit cleanup beyond process teardown, and assumptions about 16 KiB block behavior. Test signals are hard to automate without a tape/mock USD layer; practical checks are command parsing, mocked USD write/ioctl behavior, log creation, and handling open/rewind/write failures.
