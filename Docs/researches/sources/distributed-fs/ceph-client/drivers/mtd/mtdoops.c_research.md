# sources/distributed-fs/ceph-client/drivers/mtd/mtdoops.c

Purpose: kmsg dumper that stores oops/panic logs in a selected MTD partition as fixed-size circular records. It scans existing records, erases blocks as needed, writes oops records from workqueue context, and writes panic records immediately with `mtd_panic_write()`.

Important APIs/types/functions: module parameters `record_size`, `mtddev`, `dump_oops`; `struct mtdoops_hdr`; `struct mtdoops_context`; `mtdoops_notify_add/remove()`, `find_next_position()`, `mtdoops_do_dump()`, `mtdoops_write()`, `mtdoops_erase()`, `mtdoops_inc_counter()`. It depends on MTD notifiers, `mtd_read/write/panic_write/erase`, bad-block helpers, workqueues, `kmsg_dump_register()`, and vmalloc bitmaps/buffers.

Control flow: init validates parameters, allocates the record buffer, initializes work, and registers an MTD notifier. When the configured MTD appears, it validates size/erasesize/limit, allocates a used-page bitmap, registers a kmsg dumper, scans pages for the highest sequence number, marks free pages, and chooses the next slot. Dump callback copies kernel log into the record buffer; panics write synchronously, oopses schedule work. After each write it marks the page used, advances the counter, and erases the next block immediately or asynchronously if needed.

State and persistence: persistent records contain sequence, magic, timestamp, and log text. Runtime state tracks selected MTD, current page/count, used bitmap, work items, busy bit, and buffer.

Risks and test signals: panic path cannot sleep and depends on driver `panic_write`. Record size must be eraseblock-compatible in practice, though validation only checks 4 KiB multiple and erasesize >= record_size. Tests should cover sequence wrap, empty flash detection, bad blocks, erase failures and markbad fallback, concurrent dumps via busy bit, notifier removal while work is pending, and panic-write unsupported errors.
