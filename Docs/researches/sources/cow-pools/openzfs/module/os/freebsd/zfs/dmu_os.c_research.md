# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/dmu_os.c

## Scope

FreeBSD DMU page-cache integration. It copies between VM pages and DMU buffers for writes and reads, including read-behind/read-ahead page filling.

## Main Interfaces

- `dmu_write_pages()` writes an array of VM pages into DMU buffers under a transaction.
- `dmu_read_pages()` fills requested VM pages from DMU buffers and opportunistically fills read-behind and read-ahead pages.

## State And Control Flow

`dmu_write_pages()` holds a DMU buffer array for the target object/range, marks each buffer for fill or dirty depending on full/partial coverage, maps each VM page through `zfs_map_page()`, copies into `db_data`, unmaps, and releases the buffer array.

`dmu_read_pages()` holds a buffer array for the page range, optionally grabs backward pages before the first requested page, copies into the primary page array while handling bogus pages and partial final pages, zero-fills the remainder of a partially filled page, then optionally fills forward read-ahead pages. Filled speculative pages are activated if waiters exist, otherwise deactivated.

## Dependencies

Uses DMU buffer hold/release APIs, FreeBSD VM page grab/busy/valid APIs, pmap write-map checks, ZFS page mapping helpers, and ZPL znode/vnops headers.

## Correctness Notes

The code asserts page index/order consistency and that pages being filled are not dirty or write-mapped. Partial DMU writes use `DMU_PARTIAL_FIRST` / `DMU_PARTIAL_MORE` flags for correct dirtying. Reads rely on DMU’s last-block zero-fill behavior and explicitly zero-fill any incomplete VM page.
