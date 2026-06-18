# sources/distributed-fs/openafs/src/rx/bulk.example/bulk_io.c

Purpose: shared file streaming helpers for the bulk Rx example.

Important APIs/types/functions: `bulk_SendFile` and `bulk_ReceiveFile`.

Control flow: send encodes file length with `xdrrx_create`/`xdr_long`, reads blocks sized from `st_blksize`, and writes them to the Rx call. Receive decodes length, reads that many bytes from the Rx call, writes to fd, and refreshes file status.

State/persistence: transfers bytes between local file descriptors and Rx call streams; updates caller-provided `struct stat` after receive.

Dependencies/integration: generated `bulk.h`, Rx stream `rx_Read`/`rx_Write`, XDR over Rx, POSIX file I/O, malloc/free.

Risks: uses `long` for file length; block size from `stat` may be zero or unsuitable on unusual files; partial read/write handling is minimal; malloc failure aborts transfer. Test signals are exact-size round-trip files, zero-length files, large files beyond 32-bit `long`, and forced short I/O.
