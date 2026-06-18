# sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.cpp

## Purpose
`pagesize.cpp` reads configured Windows paging-file sizes and converts them into a kilobyte total, presumably for cache-size guidance.

## Important APIs, Types, and Functions
It exports `ExtractPageSize` and `GetPagingSpace`. `ExtractPageSize` pulls the trailing numeric size from a paging-file string. `GetPagingSpace` reads the `PagingFiles` `REG_MULTI_SZ` value under `SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management`.

## Control Flow
`GetPagingSpace` opens the Memory Management key, queries `PagingFiles`, iterates each null-terminated entry in the multi-string, sums `ExtractPageSize`, closes the key, and returns the sum multiplied by 1024.

## State and Persistence Behavior
No state is mutated. The function reads system registry state and returns zero if the key or value cannot be read.

## Dependencies and Integration Points
The file depends on Win32 registry APIs and `pagesize.h`. `tab_advanced.cpp` includes `pagesize.h`, though current cache bounds use fixed constants rather than calling `GetPagingSpace`.

## Risks and Edge Cases
`ExtractPageSize` assumes the final numeric run is the desired page-file maximum/minimum value. The returned unit is named `ckPageSpace` but multiplies by 1024, so callers must understand the expected units. Buffer size is fixed at 1024 TCHARs and may truncate unusually large multi-string values.

## Test Signals
Tests should cover standard `PagingFiles` entries, multiple entries, missing registry values, entries with no trailing digits, and unit expectations against cache-size UI limits.
