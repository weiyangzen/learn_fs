# sources/distributed-fs/openafs/src/WINNT/tests/netrpc/enumrpc.c

## Purpose

`enumrpc.c` is a Unicode Windows NetAPI diagnostic that queries workstation, server, and share information for a specified `\\ServerName`. It enumerates shares and then retrieves detailed information for each share, useful for checking SMB/RPC visibility of AFS-related servers or Windows hosts.

## Important APIs, Types, and Functions

- Forces `UNICODE` and includes `windows.h` and `lm.h`.
- `CallNetWkstaGetInfo()` calls `NetWkstaGetInfo()` level 102 and prints platform, computer name, version, domain, LAN root, and logged-on users.
- `CallNetServerGetInfo()` calls `NetServerGetInfo()` level 101 and classifies the target as server or workstation from `sv101_type`.
- `CallNetShareEnum()` calls `NetShareEnum()` level 2 in a resume loop, prints share rows, and calls `CallNetShareGetInfo()` for each share.
- `CallNetShareGetInfo()` calls `NetShareGetInfo()` level 2 and prints net name, local path, and remark.
- `wmain()` validates the single server argument and invokes all reports.

## Control Flow

After argument validation, the program performs workstation info, server info, and share enumeration in sequence. Share enumeration handles `ERROR_MORE_DATA` by looping with the resume handle. Each successful enumeration buffer is traversed twice: once to print summary rows and again to call per-share detail queries. NetAPI-allocated buffers are freed with `NetApiBufferFree()`.

## State and Persistence

There is no persistent state. All data is returned by NetAPI calls and printed to stdout/stderr.

## Dependencies and Integration Points

The program depends on Windows LAN Manager NetAPI and links against the appropriate NetAPI library. It is a standalone test/diagnostic, not an OpenAFS library consumer, but can be used against OpenAFS SMB gateway/server scenarios.

## Risks and Edge Cases

- `BufPtr` is not initialized before `NetShareEnum()` and is freed only on success/more-data paths.
- The comments mention level 502 for `NetShareGetInfo()` but the code uses level 2.
- Mixed `printf`, `wprintf`, `%S`, and `%s` formatting relies on Microsoft CRT semantics under `UNICODE`.
- The program requires server-name syntax and permissions sufficient for NetAPI queries.

## Test Signals

Successful output includes workstation metadata, server/workstation classification, share summary rows, and per-share details. Failures print NetAPI status codes for the relevant call.
