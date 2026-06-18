## sources/distributed-fs/openafs/src/libafscp/afscp_file.c

Purpose: Implements positional read and write operations against AFS file server data RPCs for `libafscp`.

Important APIs and functions: `afscp_PRead` fetches a byte range using `StartRXAFS_FetchData`, RX stream reads, `EndRXAFS_FetchData`, and callback registration. `afscp_PWrite` stores a byte range using `RXAFS_FetchStatus` for current length, `StartRXAFS_StoreData`, RX stream writes, and `EndRXAFS_StoreData`.

Control flow: Both functions resolve the volume from the FID, walk all candidate servers and addresses, create or use an RX call, and return after the first successful transfer. Reads first receive the file-server encoded byte count, then drain the stream into the caller buffer and add a callback if the fetch completes. Writes reject non-RWVOL volumes, fetch current status to calculate final file size, set client modification time, stream the caller buffer, and end the store RPC.

State and persistence: Persistent data changes occur only through successful store RPCs. Local state is temporary RX call state, callback/stat side effects, and `afscp_errno`.

Dependencies and integration: Uses volume/server lookup, RX call streaming, generated AFS RPC stubs, and callback registration. Directory code depends on `afscp_PRead` to read directory files and symlink contents.

Risks: The file notes both paths are not 64-bit clean; `count`, `offset`, stream byte counts, and `int bytesremaining` can truncate large transfers. `rx_Read` and `rx_Write` request all remaining bytes at once, which may be too large after truncation. Writes fetch status but do not add a callback from that status, and do not call `_StatStuff` after successful store. Positive nonzero RPC return handling follows the same failover caveat as other wrappers.

Test signals: Validate short reads, exact reads, large transfer boundaries, partial RX read/write handling, read from replicated volumes, write rejection on RO/BACK volumes, final length calculation for extending writes, and callback/status cache side effects after successful fetch.
