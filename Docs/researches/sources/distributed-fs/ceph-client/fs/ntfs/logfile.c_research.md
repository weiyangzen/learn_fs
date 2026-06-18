# sources/distributed-fs/ceph-client/fs/ntfs/logfile.c

## Purpose
`logfile.c` validates the NTFS `$LogFile` journal restart pages during mount and can empty a clean log by overwriting its allocated clusters with `0xff`. The implementation focuses on restart-page consistency rather than full log replay; it verifies page geometry, update sequence array placement, restart-area bounds, log-client lists, and selects the newest valid restart page.

## Important APIs, Types, and Functions
The exported functions are `ntfs_check_logfile()` and `ntfs_empty_logfile()`. Internal validators include `ntfs_check_restart_page_header()`, `ntfs_check_restart_area()`, `ntfs_check_log_client_array()`, and `ntfs_check_and_load_restart_page()`.

`ntfs_check_restart_page_header()` validates page sizes, restart-page position, LogFile version 1.1, USA count/offset when present, restart-area offset, and `chkdsk_lsn` rules. `ntfs_check_restart_area()` validates client-array offset, restart-area length, free/in-use list heads, sequence-number bits derived from file size, and alignment of log-record and page-data offsets. `ntfs_check_log_client_array()` traverses free and in-use client linked lists to detect out-of-range indices and loops. `ntfs_check_and_load_restart_page()` copies the full restart page, applies MST fixups when needed, optionally validates clients, and returns a deprotected page plus its LSN.

## Control Flow and State
`ntfs_check_logfile()` first treats `NVolLogFileEmpty()` as already clean, caps the size to `MaxLogFileSize`, chooses a log page size, checks the file is large enough for two restart pages plus minimum log records, then scans candidate page boundaries. It distinguishes empty `0xff` pages, log-record pages, restart pages (`RSTR`), and chkdsk-modified pages (`CHKD`). It loads up to two valid restart pages and returns the one with the newer LSN. If the whole file is empty, it sets `NVolLogFileEmpty()`.

`ntfs_empty_logfile()` requires a previously checked clean log. It truncates `$LogFile` page cache, maps the `$LogFile` runlist, allocates a cluster-sized `0xff` buffer, writes it to each real cluster in initialized size, waits for the first write range to catch serious I/O errors, skips holes, and marks the volume log empty on success. On runlist or I/O errors it sets the volume error flag and asks for chkdsk.

## State and Persistence Behavior
Validation itself reads `$LogFile` pages and returns a heap copy of the selected restart page to the caller. Emptying mutates persistent journal storage by overwriting allocated clusters with `0xff`, invalidates page cache before and after, and sets the in-memory `NVolLogFileEmpty` flag. Errors can set persistent-volume error state through `NVolSetErrors()`.

## Dependencies and Integration Points
The file depends on Linux block/page-cache APIs plus NTFS `attrib.h`, `logfile.h`, and `ntfs.h`. It uses layout magic helpers for `RSTR`, `RCRD`, `CHKD`, and empty records, MST fixup through `post_read_mst_fixup()`, runlist mapping through `ntfs_map_runlist_nolock()`, and low-level block writes through `ntfs_bdev_write()`. It is part of mount-time journal/volume-cleanliness handling.

## Risks
The code supports only LogFile version 1.1, so newer or unusual versions are rejected unless handled elsewhere. It intentionally ignores log record pages beyond restart-page checks, so it does not provide full journal replay. Restart-page scanning depends on page-size assumptions and candidate offsets; malformed files could exercise bounds-sensitive paths. `ntfs_empty_logfile()` performs raw block writes while mounting, so runlist corruption or partial I/O failure risks metadata inconsistency and correctly escalates to volume errors.

## Test Signals
Useful tests include clean and dirty LogFile images, two restart pages with differing LSNs, CHKD restart pages without USA, unsupported page sizes or versions, corrupt client lists with loops, MST fixup failure, empty log detection, emptying logs with fragmented runlists, holes in `$LogFile`, and injected write failures that set volume errors.
