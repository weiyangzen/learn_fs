<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/error.c -->
# sources/distributed-fs/ceph-client/net/9p/error.c

This file maps Plan 9 server error strings to Linux errno values. Plan 9 protocols commonly return strings, while Linux callers need negative errno results.

State is a static `errmap[]` table and a hash table `hash_errmap`. `p9_error_init()` computes lengths and jhash values for each static string and inserts them into the hash table. `p9_errstr2errno()` hashes the incoming server string, searches matching length/content, returns `-val` when found, and logs unknown strings before returning `-ESERVERFAULT`.

There is no removal path because the table is static and module lifetime covers the hash entries. Dependencies include Linux errno values, jhash, hash table helpers, and 9P error handling in `client.c`.

Risks include writing `errstr[len] = 0` for unknown errors, which assumes the buffer is writable and has room for a terminator; callers currently pass allocated strings from protocol parsing, but this is an important contract. Duplicate or overly broad string mappings can also change user-visible errors. Tests should cover known mappings, unknown strings with writable buffers, zero-valued non-error strings, case-sensitive fossil/u9fs variants, and initialization before first lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/error.c -->
