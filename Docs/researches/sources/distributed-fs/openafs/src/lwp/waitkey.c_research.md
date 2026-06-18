# sources/distributed-fs/openafs/src/lwp/waitkey.c

Purpose: cross-platform keyboard-input wait helpers for LWP tools and tests.

Important APIs/types/functions: exports `LWP_WaitForKeystroke`, `LWP_GetLine`, and `LWP_GetResponseKey`. The NT implementation uses `_kbhit`, `getch/getche`, and either `Sleep` or `IOMGR_Select`; the Unix implementation inspects stdio buffers then uses `select` or `IOMGR_Select`.

Control flow: `LWP_WaitForKeystroke` returns immediately if buffered data exists, waits indefinitely for negative seconds, polls for zero seconds, or waits up to the timeout. `LWP_GetLine` waits for input then reads a full line, with NT manually handling carriage return and backspace. `LWP_GetResponseKey` flushes stdin, waits, then reads one character if available.

State and persistence: only stdin buffering and transient timeout state. No persistent storage.

Dependencies/integration: depends on platform stdio internals (`__fbufsize`, `_IO_read_ptr`, BSD `_bf`, or `_cnt`) where available; uses IOMGR unless pthread mode is selected.

Risks and test signals: direct access to libc `FILE` internals is fragile across libc versions. `fflush(stdin)` is non-portable but used historically. `test_key` is the direct behavioral test.
