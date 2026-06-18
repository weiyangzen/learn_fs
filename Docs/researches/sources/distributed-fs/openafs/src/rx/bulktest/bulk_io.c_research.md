# sources/distributed-fs/openafs/src/rx/bulktest/bulk_io.c

Purpose: legacy K&R-style shared bulk streaming helpers.

Important APIs/types/functions: `bulk_SendFile` and `bulk_ReceiveFile`.

Control flow: identical in intent to `bulk.example`: send encodes length then reads file blocks into `rx_Write`; receive decodes length, loops `rx_Read` to a buffer, writes file data, and refreshes status.

State/persistence: local file descriptors and Rx call stream data; updates provided `struct stat` on successful receive.

Dependencies/integration: generated `bulk.h`, XDR over Rx, POSIX I/O, malloc/free.

Risks: uses `long` lengths and K&R declarations; send prints malloc failure to stdout while receive uses stderr; partial I/O handling is weak; short `rx_Read` of zero marks error but negative cases are not distinct. Test signals are file round trips, zero/large files, and induced disk/Rx short reads.
