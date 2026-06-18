
# sources/distributed-fs/openafs/src/update/update_internal.h

`update_internal.h` is the small private header shared within the update directory. It declares list helpers from `utils.c` and the server-side generated RPC entry points `UPDATE_FetchFile` and `UPDATE_FetchInfo`.

The file has no runtime control flow or persistence. Its integration role is to keep `client.c`, `server.c`, and `utils.c` prototypes consistent without exposing them as a broader installed API.

Dependencies are `struct filestr` from `global.h` and `struct rx_call` from Rx headers included by consumers. Risks are limited to prototype drift if generated RPC signatures or utility ownership semantics change. Test signals are build coverage for both upclient and upserver.
