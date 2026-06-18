# sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.h

## Purpose
`user-cache.h` declares the user credential cache shared by service startup, credential resolution, and the maintenance thread.

## Important APIs, Types, And Functions
It defines `USER_CACHE_HIT` and `USER_CACHE_MISS`, `struct user_entry` with qhash linkage, `user_name[256]`, `PVFS_credential`, and optional `ASN1_UTCTIME *expires`, plus functions `user_compare`, `add_cache_user`, `get_cache_user`, and `user_cache_thread`.

## Control Flow
The service initializes the qhash and mutex, credential lookup calls `get_cache_user` and `add_cache_user`, and a background thread periodically expires entries.

## State And Persistence
The declared entry structure stores copied credentials and optional certificate expiration in memory only. It has no persistent backing.

## Dependencies And Integration Points
It includes OpenSSL ASN.1, OrangeFS, and quickhash. It is implemented by `user-cache.c`, initialized by `service-main.c`, and consumed by `dokany-interface.c`.

## Risks And Test Signals
The API exposes mutable `char *user_name` inputs and depends on callers to manage credential cleanup for returned copies. The thread entry point never terminates cooperatively. Tests do not directly target this header’s behavior.
