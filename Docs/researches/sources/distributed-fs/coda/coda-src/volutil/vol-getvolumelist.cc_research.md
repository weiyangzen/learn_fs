## sources/distributed-fs/coda/coda-src/volutil/vol-getvolumelist.cc

Purpose: `vol-getvolumelist.cc` returns the server's in-RVM volume list to a volutil client using an RPC2 SMARTFTP side effect.

Important APIs/types/functions: `S_GetVolumeList` calls `VListVolumes(&buf, &buflen)`, prepares an `SE_Descriptor` with `FILEINVM`, sends the memory buffer to the client with `RPC2_InitSideEffect` and `RPC2_CheckSideEffect`, frees the buffer, and returns the RPC result.

Control flow: collect list, configure side effect as server-to-client memory transfer, initialize transfer, wait for local completion, log result, free memory.

State and persistence behavior: read-only with respect to volume state. It allocates a heap buffer for the list and transfers it over RPC; no server file is written.

Dependencies/integration points: depends on `VListVolumes`, RPC2 SMARTFTP descriptors, volutil RPC service, and Coda logging. It is likely used by administrative clients to enumerate volumes.

Risks: it does not call `VInitVolUtil`, so correctness depends on server context already having volume state initialized. If `RPC2_InitSideEffect` returns a positive nonzero code, the `!rc` guard can skip `CheckSideEffect`, depending on RPC2 return conventions. Large volume lists require a contiguous memory buffer.

Test signals: empty and populated volume lists, large lists, side-effect failures, client disconnects, and leak checks around `free(buf)`.
