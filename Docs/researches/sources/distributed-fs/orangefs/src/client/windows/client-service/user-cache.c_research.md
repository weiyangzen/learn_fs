# sources/distributed-fs/orangefs/src/client/windows/client-service/user-cache.c

## Purpose
`user-cache.c` caches OrangeFS credentials by Windows user name so requestor credential lookup does not repeatedly parse certificates, LDAP entries, or configured user lists.

## Important APIs, Types, And Functions
It implements `user_compare`, `add_cache_user`, `get_cache_user`, and `user_cache_thread`. The disabled `remove_user` shows intended explicit removal. Global `user_cache` and `user_cache_mutex` are initialized in `service-main.c`. Entries are `struct user_entry` from `user-cache.h`.

## Control Flow
`add_cache_user` removes an existing entry for the user, allocates a new one, copies the username and `PVFS_credential`, clamps certificate expiration to not exceed the credential timeout, and inserts the entry in the qhash. `get_cache_user` searches by case-insensitive username and copies the credential on hit. `user_cache_thread` sleeps for one minute, scans qhash buckets, and removes entries whose ASN.1 UTC expiration is older than `time(NULL)`.

## State And Persistence
The cache is process-local and lost on restart. Entries hold copied credential data and optional OpenSSL ASN.1 expiration objects. Persistent identity data remains in config/certs/LDAP, not here.

## Dependencies And Integration Points
It depends on Windows sleep, OpenSSL ASN.1, OrangeFS credential helpers, `gen-locks`, `security-util`, `client-service.h`, `user-cache.h`, and `cred.h`. It is used by `dokany-interface.c` during request credential lookup and maintained by the thread started in `service-main.c`.

## Risks And Test Signals
`strncpy(entry->user_name, user_name, 256)` can leave the name unterminated. If `ASN1_UTCTIME_new` fails after freeing the old expiration, `add_cache_user` returns without freeing the allocated entry or cleaning the copied credential. The cache thread scans one qhash head per bucket and may miss chained entries depending on quickhash internals. It runs forever and is stopped with `TerminateThread`, which risks lock/heap corruption. Client tests indirectly exercise cache hits/misses through filesystem operations but do not validate expiration or concurrent credential lookup.
