# sources/distributed-fs/ceph-client/fs/ntfs/logfile.h

## Purpose
`logfile.h` defines the NTFS `$LogFile` restart-page and restart-area structures, log-client records, constants, flags, and exported journal validation/emptying APIs used by `logfile.c` and mount code.

## Important APIs, Types, and Functions
Constants include `MaxLogFileSize`, `DefaultLogPageSize`, and `MinLogRecordPages`. `struct restart_page_header` models the `RSTR`/`CHKD` page header, including USA fields, page sizes, version, and restart-area offset. `LOGFILE_NO_CLIENT` and `LOGFILE_NO_CLIENT_CPU` mark absent log-client list links. `RESTART_VOLUME_IS_CLEAN` records clean shutdown state. `struct restart_area` stores current LSN, client-list heads, flags, sequence-number bits, restart-area length, client-array offset, file size, and log-page data geometry. `struct log_client_record` stores oldest/restart LSNs, linked-list pointers, sequence number, and client name. The exported APIs are `ntfs_check_logfile()` and `ntfs_empty_logfile()`.

## Control Flow and State
The header describes the two-restart-page layout followed by circular log-record pages. It does not implement flow, but `logfile.c` reads these structures in order: restart page header, restart area, then client records if the log is open and not chkdsk-modified.

## State and Persistence Behavior
All structures are packed persistent on-disk records in `$LogFile`. They encode whether the volume was shut down cleanly, where clients should restart, and the usable size and geometry of the log. The clean/dirty interpretation depends on both client-list state and `RESTART_VOLUME_IS_CLEAN`.

## Dependencies and Integration Points
The header includes `layout.h` for magic values and packed NTFS types. It is consumed by mount-time journal checking and by any code deciding whether the log can be emptied or the volume must be considered dirty.

## Risks
The documented compatibility note says the driver targets LogFile version 1.1; older or newer formats may not be safely interpreted. Any mismatch in packed layout or endian handling would break mount-time journal checks. Cleanliness logic is version- and Windows-behavior-sensitive, especially because Windows XP and later may keep the logfile open even after clean shutdown.

## Test Signals
Compile checks cover structure availability. Runtime image tests should include version 1.1 restart areas, clean and dirty flags, Win2k-style closed clients, XP-style open clean logs, CHKD-modified logs, and boundary values for page size, file size, and client-array offsets.
