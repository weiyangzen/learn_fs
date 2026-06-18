# sources/distributed-fs/coda/coda-src/venus/archive.c

## Purpose
This file writes Coda repair/archive output in old tar, POSIX ustar, old portable cpio, and SVR4 newc cpio formats.

## Important APIs, Types, and Functions
The global `archive_type` defaults to `CPIO_NEWC`. `write_padding()` pads a stream to the selected alignment. `archive_write_entry()` emits one metadata record for regular files, directories, symlinks, and hardlinks, translating path names, mode bits, uid, nlink, mtime, file size, and link targets into the selected archive format. `archive_write_data()` copies a container file to the archive and pads it. `archive_write_trailer()` emits tar zero blocks or a cpio `TRAILER!!!` record and flushes the stream.

## Control Flow
Entry writing first strips a leading slash and calculates name length, then switches on `archive_type`. Tar paths build a 512-byte header and checksum. CPIO ODC writes octal text fields with overflow handling. CPIO newc writes fixed-width hexadecimal fields and 4-byte padding. File data is read in chunks and periodically yields to LWP scheduling.

## State and Persistence Behavior
The output archive is persistent. Source data is read from cache container files. The only module state is the selected archive format.

## Dependencies and Integration Points
It depends on libc IO, Coda assertions, LWP/IOMGR yielding, and `archive.h`. `vol_cml.cc` uses these functions to dump local modification logs or repair archives.

## Risks and Test Signals
Risks include path length limits, tar prefix boundary errors, uid/inode/time truncation, returning without closing the input fd on read/write errors, and assuming only regular/dir/symlink types. Tests should extract all supported formats with standard tools, cover long names, links, large files near format limits, and simulated ENOSPC/EIO failures.
