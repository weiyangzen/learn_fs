# sources/distributed-fs/openafs/src/WINNT/client_config/pagesize.h

## Purpose
`pagesize.h` declares helpers for extracting and summing Windows paging-file sizes.

## Important APIs, Types, and Functions
It declares `ULONG ExtractPageSize(LPCTSTR psz)` and `ULONG GetPagingSpace(void)`.

## Control Flow
The intended flow is to parse individual paging-file strings with `ExtractPageSize` or call `GetPagingSpace` to read all configured paging files.

## State and Persistence Behavior
There is no state in the header or implementation; only registry reads occur in `pagesize.cpp`.

## Dependencies and Integration Points
The header is included by `tab_advanced.cpp`, making paging-space information available for cache sizing even though the current UI uses fixed min/max constants.

## Risks and Edge Cases
The header assumes Windows types such as `ULONG` and `LPCTSTR` are already in scope. It does not document units, which is important because `GetPagingSpace` multiplies parsed values by 1024.

## Test Signals
Compile inclusion from `tab_advanced.cpp` and unit coverage of `pagesize.cpp` parsing/units are the relevant signals.
