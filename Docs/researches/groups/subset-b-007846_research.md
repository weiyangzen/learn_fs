# subset-b-007846 Research

Grouped research for the assigned OrangeFS common misc, quickhash, quicklist, security, statecomp, and token-utils files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.c -->
# sources/distributed-fs/orangefs/src/common/misc/tcache.c

## Purpose
Implements OrangeFS's generic timeout cache. It stores caller-owned payloads behind opaque keys, combines `quickhash` lookup with a least-recently-used `quicklist`, supports entry expiration, and provides soft/hard limit reclamation for higher-level caches such as client capability caching.

## Important APIs, Types, And Functions
The public API is `PINT_tcache_initialize`, `PINT_tcache_finalize`, `PINT_tcache_get_info`, `PINT_tcache_set_info`, `PINT_tcache_insert_entry`, `PINT_tcache_insert_entry_ex`, `PINT_tcache_lookup`, `PINT_tcache_reclaim`, `PINT_tcache_delete`, and `PINT_tcache_refresh_entry`. Internal helpers are `check_expiration` and `tcache_lookup_oldest`. Callers provide key comparison, key hashing, and payload cleanup callbacks.

## Control Flow
Initialization allocates a `PINT_tcache`, installs callbacks, sets defaults, creates the hash table, and initializes the LRU list. Inserts optionally reclaim expired entries once the soft limit is reached, evict the oldest entry at the hard limit, allocate a cache entry, set an explicit or refreshed expiration time, add it to both hash and LRU structures, and increment `num_entries`. Lookup searches the hash table, reports expiration status, and moves the entry to the LRU tail. Reclaim walks the LRU head forward, deleting expired entries until it reaches a live entry or the reclaim percentage cap.

## State And Persistence
All state is in memory: timeout options, entry counts, hash buckets, and LRU links. Payload ownership transfers to the cache at insert time and `free_payload` is called on disabled inserts, deletes, evictions, reclaim, and finalize. No disk or configuration persistence is performed here.

## Dependencies And Integration Points
Depends on `pvfs2-internal.h` error codes/time helpers, `quickhash`, `quicklist`, and `gossip` for diagnostics. The cache is deliberately not thread-safe; wrappers such as `client-capcache.c` provide their own mutexes.

## Risks And Test Signals
Risks include no duplicate-key rejection, caller-after-lookup lifetime hazards, no internal locking, option combinations where `soft_limit` exceeds `hard_limit`, null pointer assumptions for `purged` and `tcache`, and time arithmetic edge cases. Tests should cover disabled-cache insert cleanup, expiration status, refresh behavior, soft-limit reclaim, hard-limit LRU replacement, explicit expiration insertion, finalize freeing all payloads, and invalid option handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.h -->
# sources/distributed-fs/orangefs/src/common/misc/tcache.h

## Purpose
Declares the generic timeout cache interface and data structures used by OrangeFS components that need keyed, expiring, in-memory objects.

## Important APIs, Types, And Functions
Defines `enum PINT_tcache_replace_algorithms`, currently `LEAST_RECENTLY_USED`; `struct PINT_tcache_entry`, containing payload, expiration, hash link, and LRU link; `struct PINT_tcache`, containing callbacks, options, hash table, and LRU list; and `enum PINT_tcache_options` for timeout, entry count, hard/soft limits, enable flags, reclaim percentage, replacement algorithm, and expiration enablement. It declares all `PINT_tcache_*` entry points implemented in `tcache.c`.

## Control Flow
The header documents the expected lifecycle: initialize with callbacks, insert payloads, lookup entries and copy payload data before later cache calls if needed, optionally refresh or delete entries, and finalize to free all owned payloads.

## State And Persistence
The structures describe only process memory. The comments define ownership rules: keys are immutable after insertion, payload memory is caller allocated but cache owned after insertion, and callers must provide synchronization.

## Dependencies And Integration Points
Includes `pvfs2-internal.h`, `sys/time.h` or `wincommon.h`, `pvfs2-types.h`, `quicklist.h`, and `quickhash.h`. It is consumed by client capability caching and any other higher-level OrangeFS cache requiring timeout/LRU semantics.

## Risks And Test Signals
Risks are contract drift between comments and implementation, enum option values reused directly by wrappers, and portability differences around `struct timeval`. Compile tests should include Unix and Windows paths; behavioral tests should validate the ownership and non-thread-safe assumptions through wrapper-level locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/tcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c -->
# sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c

## Purpose
Provides a compatibility fallback for `fgetxattr` on platforms where the function is not available at build time.

## Important APIs, Types, And Functions
Conditionally defines `fgetxattr` with either the standard four-argument form or the extra-argument form selected by `HAVE_FGETXATTR_EXTRA_ARGS`. The fallback sets `errno = ENOSYS` and returns `-1`.

## Control Flow
Compilation is entirely feature-macro driven. If `HAVE_FGETXATTR` is absent, this file supplies the function body declared by `xattr-utils.h`; otherwise it contributes no runtime behavior.

## State And Persistence
No persistent state exists. The only state change is setting process-local `errno` when the stub is called.

## Dependencies And Integration Points
Includes standard C headers and `xattr-utils.h`. It lets code link on systems without native extended attribute support while preserving normal failure semantics.

## Risks And Test Signals
The main risk is configure macro mismatch causing a signature conflict with system headers. Tests should compile with and without `HAVE_FGETXATTR`, and runtime tests on unsupported platforms should observe `-1` plus `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h

## Purpose
Normalizes extended-attribute header inclusion and `fgetxattr` prototype availability across Unix and Windows builds.

## Important APIs, Types, And Functions
Includes `<sys/xattr.h>` or `<attr/xattr.h>` when configured. On Windows it defines `ssize_t` as `size_t`. If no prototype is detected, it declares `fgetxattr` in either standard or extra-argument form.

## Control Flow
There is no runtime flow; preprocessor checks select the correct declaration path.

## State And Persistence
No state is defined. The header only affects compile-time API visibility.

## Dependencies And Integration Points
Depends on `pvfs2-internal.h` and configure macros. It is included by `xattr-utils.c` and any code needing portable `fgetxattr` access.

## Risks And Test Signals
Risks include platform ABI mismatches when configure probes are wrong and the Windows `ssize_t` typedef differing from signed POSIX semantics. Test signals are successful compilation on Linux xattr variants, macOS/BSD-like extra-argument configurations, and Windows builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/quickhash/module.mk.in

## Purpose
Declares the build directory variable for the `quickhash` common component.

## Important APIs, Types, And Functions
The only assignment is `DIR := src/common/quickhash`.

## Control Flow
Included by the OrangeFS make system to establish the current module path before collecting sources or generated artifacts.

## State And Persistence
No runtime state exists. Build state is limited to the make variable value.

## Dependencies And Integration Points
Integrates `src/common/quickhash` with surrounding make include files. Since `quickhash.h` is header-only, no source files are appended here.

## Risks And Test Signals
Risks are limited to build path drift. A successful full build and inclusion of `quickhash.h` users are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h -->
# sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h

## Purpose
Implements a small chained hash table as static inline functions and macros, usable in user-space OrangeFS code and Linux kernel contexts.

## Important APIs, Types, And Functions
Defines `struct qhash_table`, `qhash_init`, `qhash_finalize`, `qhash_add`, `qhash_search`, indexed search/remove helpers, `qhash_destroy_and_finalize`, and hash helpers `quickhash_32bit_hash`, `quickhash_64bit_hash`, and `quickhash_string_hash`. It maps allocation, list, and locking primitives to kernel APIs under `__KERNEL__` and to `quicklist`/malloc/free in user space.

## Control Flow
Initialization allocates a table header and an array of list heads. Add hashes the key and appends to the target bucket. Search locks the table, scans the bucket with the caller-provided compare function, unlocks, and returns the embedded link. Removal variants unlink the matching item before returning it. The destroy macro drains every bucket and invokes a caller-supplied destructor.

## State And Persistence
Hash state is in memory: bucket array, table size, callbacks, and a kernel spinlock when compiled in kernel mode. User-space lock macros are no-ops, so concurrency must be provided externally.

## Dependencies And Integration Points
Used by `tcache`, `security-hash`, and statecomp code generation. It depends on `quicklist.h`, `pvfs2-internal.h`, and kernel list/spinlock APIs in kernel builds.

## Risks And Test Signals
The integer and string hash helpers mask with `table_size - 1`, which distributes correctly for power-of-two sizes but conflicts with comments and users that pass primes such as 1009. Search returns pointers after unlocking, making concurrent mutation unsafe. Tests should cover add/search/remove, duplicate replacement users, all destroy paths, kernel/user compilation, and hash distribution for the table sizes actually used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quickhash/quickhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/quicklist/module.mk.in

## Purpose
Declares the build directory variable for the `quicklist` common component.

## Important APIs, Types, And Functions
The file contains `DIR := src/common/quicklist`.

## Control Flow
It is read by the make include hierarchy to identify the module path.

## State And Persistence
No runtime state exists. The only state is the make variable assignment.

## Dependencies And Integration Points
`quicklist.h` is header-only, so this build fragment does not add a compilation unit.

## Risks And Test Signals
Risks are limited to path drift or omitted inclusion from parent makefiles. A successful build of `quickhash`, `tcache`, and statecomp users validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h -->
# sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h

## Purpose
Provides OrangeFS's lightweight doubly linked list primitive, derived from Linux list-style intrusive links.

## Important APIs, Types, And Functions
Defines `struct qlist_head`, initialization macros, `qlist_add`, `qlist_add_tail`, `qlist_del`, `qlist_del_init`, `qlist_empty`, `qlist_pop`, `qlist_splice`, `qlist_entry`, iteration macros, `qlist_exists`, `qlist_count`, and `qlist_find`. Windows-specific iterator macros avoid GNU `typeof`.

## Control Flow
List heads point to themselves when empty. Add inserts between known neighbors; delete stitches neighbors around the removed link; pop removes the first item; splice moves all entries from one list into another position; iteration macros traverse raw links or containing entries.

## State And Persistence
All state is embedded in caller-owned structures via `qlist_head` fields. There is no allocation, locking, or persistence in this header.

## Dependencies And Integration Points
Used by `quickhash`, `tcache`, security key tables, and statecomp. Windows builds include `wincommon.h`; Unix builds use GNU `typeof` for typed entry iteration.

## Risks And Test Signals
Risks are typical intrusive-list hazards: deleting unlinked entries, mutating during non-safe iteration, no locking, and portability around `typeof`. Tests should cover empty, add, tail ordering, delete-init, pop, splice, safe removal during iteration, and Windows macro compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.c -->
# sources/distributed-fs/orangefs/src/common/security/capcache.c

## Purpose
Implements the server-side capability cache when `ENABLE_CAPCACHE` is defined. It stores signed `PVFS_capability` objects in the generic `seccache` framework and supports a quick-sign path that reuses a cached signature for an equivalent capability.

## Important APIs, Types, And Functions
Exports `PINT_capcache_init`, `PINT_capcache_finalize`, `PINT_capcache_lookup`, `PINT_capcache_insert`, and `PINT_capcache_quick_sign`. Internal methods implement expiration clamped to capability timeout, Murmur3 hashing over issuer/fsid/op mask/handles, signature-based compare, cleanup, debug output, and field-based quick compare.

## Control Flow
Initialization creates a global `capcache` with a method table and sets its timeout from server configuration. Insert deep-copies the capability then passes it to `PINT_seccache_insert`. Lookup delegates to `PINT_seccache_lookup`. Quick-sign hashes the unsigned or partially populated capability, locks the cache, searches the bucket by stable capability fields, and if a non-expired cached capability is found copies timeout and signature back to the caller.

## State And Persistence
State is process-local in the global `seccache_t *capcache`; entries own duplicated capability memory and are freed by `PINT_cleanup_capability`. No disk persistence exists.

## Dependencies And Integration Points
Depends on `seccache`, `security-util`, Murmur3, server configuration, `pint-util`, `gossip`, and PVFS security types. It is selected by `security/module.mk.in` under `ENABLE_CAPCACHE`.

## Risks And Test Signals
Risks include dereferencing `capcache` before initialization, stale duplicate entries because insertion does not replace existing equivalent capabilities, hash/compare mismatch because the normal compare is signature-based while the hash is field-based, and quick-sign behavior around expired entries. Tests should cover init/finalize, insert/lookup by signature, null capability handling, quick-sign hit/miss/expired paths, and timeout clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.h -->
# sources/distributed-fs/orangefs/src/common/security/capcache.h

## Purpose
Declares the server-side capability cache API and default timeout when `ENABLE_CAPCACHE` is enabled.

## Important APIs, Types, And Functions
Defines `CAPCACHE_TIMEOUT` defaulting to 10 seconds and declares `PINT_capcache_init`, `PINT_capcache_finalize`, `PINT_capcache_lookup`, `PINT_capcache_insert`, and `PINT_capcache_quick_sign`.

## Control Flow
Callers initialize the cache during server security setup, insert verified or newly signed capabilities, lookup by capability, optionally reuse signatures through quick-sign, and finalize on shutdown.

## State And Persistence
The header defines no state directly; the implementation owns the global `capcache` and entry memory.

## Dependencies And Integration Points
Includes `pvfs2-config.h`, standard integer/time headers, and `seccache.h`. All declarations are hidden unless `ENABLE_CAPCACHE` is set.

## Risks And Test Signals
Risks are build-mode drift and callers assuming these symbols exist in non-capcache builds. Compile tests should cover enabled and disabled configurations; runtime tests should validate each declared function through the server security lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.c -->
# sources/distributed-fs/orangefs/src/common/security/cert-util.c

## Purpose
Provides OpenSSL utility functions for loading, saving, converting, copying, and cleaning OrangeFS certificate and key structures.

## Important APIs, Types, And Functions
Exports `PINT_load_cert_from_file`, `PINT_load_key_from_file`, `PINT_save_cert_to_file`, `PINT_save_pubkey_to_file`, `PINT_save_privkey_to_file`, `PINT_cert_to_X509`, `PINT_X509_to_cert`, `PINT_copy_cert`, `PINT_copy_key`, `PINT_cleanup_cert`, and `PINT_cleanup_key`. `PINT_save_key_to_file` is the internal common save helper.

## Control Flow
Load/save functions open PEM files and call OpenSSL PEM read/write APIs. Conversion from internal certificate to X509 creates a memory BIO over DER bytes and decodes it; conversion from X509 writes DER into a memory BIO, allocates a `PVFS_certificate`, and copies pending BIO bytes. Copy helpers allocate destination buffers and deep-copy byte arrays. Cleanup frees internal buffers and zeroes sizes.

## State And Persistence
The file reads and writes certificate/key files, including unencrypted private keys. In-memory allocations are transferred to callers, who must free with OpenSSL APIs or the provided cleanup helpers as appropriate.

## Dependencies And Integration Points
Depends on OpenSSL PEM/BIO/X509/EVP APIs and PVFS security types. Used by certificate-mode security initialization, credential verification, LDAP mapping, certificate cache, and trust-store setup.

## Risks And Test Signals
Risks include mixed positive `errno` returns versus negative PVFS error codes, unencrypted private-key output, partial cleanup on allocation failures, and API drift across OpenSSL versions. Tests should load/save valid and invalid PEM files, round-trip X509/internal certificates, copy empty and non-empty buffers, and verify cleanup can be called repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.h -->
# sources/distributed-fs/orangefs/src/common/security/cert-util.h

## Purpose
Declares certificate and key utility functions used by OrangeFS security code.

## Important APIs, Types, And Functions
The header exposes file load/save helpers for X509 certificates and EVP keys, conversion helpers between `PVFS_certificate` and `X509`, deep-copy helpers for `PVFS_certificate` and `PVFS_security_key`, and cleanup functions for those internal structures.

## Control Flow
Consumers call these helpers while initializing trust, converting credentials for verification, caching certificate identity mappings, or persisting generated keys/certificates.

## State And Persistence
No state is declared. Persistence is implied by the file path arguments used by the implementation.

## Dependencies And Integration Points
Includes OpenSSL `evp.h`/`x509.h`, `pvfs2-config.h`, and `pvfs2-types.h`. It is compiled into library and server builds when certificate security is enabled.

## Risks And Test Signals
Risks are declaration drift against OpenSSL API changes and unclear ownership transfer for allocated output parameters. Compile coverage plus conversion/load/save round-trip tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/cert-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.c -->
# sources/distributed-fs/orangefs/src/common/security/certcache.c

## Purpose
Implements a server-side certificate-to-identity cache under `ENABLE_CERTCACHE`. It maps certificate subjects to resolved uid and group arrays, reducing repeated LDAP or trust-store mapping work.

## Important APIs, Types, And Functions
Exports `PINT_certcache_init`, `PINT_certcache_finalize`, `PINT_certcache_lookup`, and `PINT_certcache_insert`. Internal helpers extract X509 subject strings, duplicate certificate expiration time, allocate `certcache_data_t`, hash by subject with Murmur3, compare subjects, free ASN1/group data, and print debug information.

## Control Flow
Insert converts the internal certificate to X509, copies its subject, uid, groups, and notAfter timestamp into a `certcache_data_t`, then inserts that data into `seccache`. Lookup builds a temporary `certcache_data_t` from the queried certificate, searches `seccache` by subject, then frees the temporary data. Expiration is set to now plus cache timeout but forced to expired if the certificate expires before that time.

## State And Persistence
Runtime state is the global `seccache_t *certcache`. Entries own duplicated group arrays and ASN1 expiration strings. No disk persistence occurs.

## Dependencies And Integration Points
Depends on OpenSSL X509/ASN1 APIs, `cert-util`, `seccache`, Murmur3, server config, and `gossip`. `pint-uid-map.c` uses it to cache LDAP mapping results; `pint-security.c` can cache the CA certificate as root.

## Risks And Test Signals
`certcache_data_t` is allocated with `malloc` and in the zero-group path `group_array` is not explicitly initialized before cleanup checks it, which is a memory-safety risk. Other risks include subject-string collisions or non-canonical subject forms, ASN1 time handling, and duplicate entries. Tests should cover zero-group inserts, lookup hit/miss, certificate-expiration clamping, CA-root cache insertion, and repeated finalize after populated cache use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.h -->
# sources/distributed-fs/orangefs/src/common/security/certcache.h

## Purpose
Declares the certificate cache API and the cached identity data structure when `ENABLE_CERTCACHE` is enabled.

## Important APIs, Types, And Functions
Defines `CERTCACHE_SUBJECT_SIZE` and `certcache_data_t`, which stores ASN1 expiration, subject, uid, group count, and group array. Declares `PINT_certcache_init`, `PINT_certcache_finalize`, `PINT_certcache_lookup`, and `PINT_certcache_insert`.

## Control Flow
Callers initialize the cache during security startup, insert certificate identity mappings after LDAP/trust resolution, lookup mappings before repeating LDAP work, and finalize on shutdown.

## State And Persistence
No global state is declared here, but the struct defines the per-entry memory owned by the implementation.

## Dependencies And Integration Points
Includes OpenSSL ASN1, `seccache.h`, and PVFS types. It is used only in certificate-cache builds.

## Risks And Test Signals
Risks include consumers depending on mutable `seccache_entry_t` internals and mismatched group-array ownership. Compile tests for enabled/disabled feature modes and runtime mapping-cache tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.c -->
# sources/distributed-fs/orangefs/src/common/security/client-capcache.c

## Purpose
Implements the client-side capability cache. It stores per-object, per-user capabilities in `PINT_tcache`, synchronizes access with a mutex, and publishes performance counters for cache occupancy and hit/miss/update behavior.

## Important APIs, Types, And Functions
Exports `PINT_client_capcache_initialize`, `PINT_client_capcache_finalize`, `PINT_client_capcache_get_info`, `PINT_client_capcache_set_info`, `PINT_client_capcache_get_cached_entry`, `PINT_client_capcache_update`, `PINT_client_capcache_invalidate`, and `PINT_client_capcache_get_pc`. Internal types are `client_capcache_payload` and `client_capcache_key`; internal callbacks compare keys, hash by handle plus uid, free payloads, and set defaults.

## Control Flow
Initialization creates the underlying tcache, sets hard/soft/reclaim defaults, and initializes perf counters. Lookup checks enablement, searches by object reference and uid, counts hit or miss, invalidates timed-out entries, and deep-copies the cached capability for the caller. Update refuses soon-expiring capabilities, computes an expiration bounded by capability timeout minus a buffer, deletes an old entry if present, deep-copies the new capability into a payload, inserts it, and updates performance counters. Invalidate looks up and deletes one entry.

## State And Persistence
State is process-local: global tcache pointer, mutex, timeout flag, performance counter pointer, and entry payloads. No persistence exists; entries own copied capability internals.

## Dependencies And Integration Points
Depends on `tcache`, `quickhash`, `quicklist`, `gen-locks`, `pint-perf-counter`, `pint-util`, `security-util`, client sysint utilities, and gossip debug. It is included in `LIBSRC` by the security module makefile.

## Risks And Test Signals
Risks include dereferencing `client_capcache` before initialization, ignored or partially handled `PINT_copy_capability` failures on new inserts, leaks after update-copy failures, simple hash distribution and integer overflow, and an unused `client_capcache_timeout_flag`. Tests should cover init/finalize, disabled mode, hit/miss counters, timeout invalidation, replacement and purge counters, update of existing entries, soon-expiring capabilities, and copy-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.h -->
# sources/distributed-fs/orangefs/src/common/security/client-capcache.h

## Purpose
Declares the client-side capability cache API and performance counter identifiers.

## Important APIs, Types, And Functions
Aliases `PINT_client_capcache_options` to `PINT_tcache_options`, defines client cache option macros, declares performance counter indexes, exposes `client_capcache_keys`, and declares lifecycle, get/set, lookup, update, invalidate, and perf-counter access functions.

## Control Flow
Client code initializes the cache, optionally adjusts tcache options, looks up cached capabilities before RPCs, updates the cache from server responses, invalidates stale object/user pairs, and finalizes during shutdown.

## State And Persistence
The header exposes no state except the external performance key table. Implementation state is in memory only.

## Dependencies And Integration Points
Includes PVFS types, locking, quicklist/quickhash, tcache, and performance counter headers. It bridges generic tcache behavior into client security and instrumentation.

## Risks And Test Signals
Risks are option alias drift if `PINT_tcache_options` changes and callers assuming thread safety beyond the wrapper API. Tests should compile against all option macros and validate performance counter names/ids remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.c -->
# sources/distributed-fs/orangefs/src/common/security/credcache.c

## Purpose
Implements a server-side credential cache under `ENABLE_CREDCACHE`, storing duplicated `PVFS_credential` objects in `seccache` to avoid repeated signature verification work.

## Important APIs, Types, And Functions
Exports `PINT_credcache_init`, `PINT_credcache_finalize`, `PINT_credcache_lookup`, and `PINT_credcache_insert`. Internal seccache methods set expiration clamped to credential timeout, hash issuer and signature with Murmur3, compare signatures, cleanup duplicated credentials, and emit debug logs.

## Control Flow
Initialization creates a global `credcache` and configures timeout from server configuration. Insert deep-copies the credential and inserts it into `seccache`. Lookup delegates to `PINT_seccache_lookup`, which checks expiration and refreshes live entries. Finalize cleans the generic cache.

## State And Persistence
State is the global in-memory `seccache_t *credcache`; each entry owns a deep copy of the credential and its issuer/signature/group/certificate buffers.

## Dependencies And Integration Points
Depends on `seccache`, `security-util`, Murmur3, server config, `pint-util`, and gossip. It is selected in `security/module.mk.in` when a real security mode and `ENABLE_CREDCACHE` are active.

## Risks And Test Signals
The header declares `PINT_credcache_remove`, but this file does not implement it. Other risks include null global usage before init, duplicate entries, signature-size mismatch handling, and config timeout units. Tests should cover insert/lookup/null credential behavior, expiration, duplicate signatures, finalize cleanup, and link checks for the declared remove symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.h -->
# sources/distributed-fs/orangefs/src/common/security/credcache.h

## Purpose
Declares the server-side credential cache API under `ENABLE_CREDCACHE`.

## Important APIs, Types, And Functions
Defines `CREDCACHE_TIMEOUT` defaulting to 300 seconds and declares `PINT_credcache_init`, `PINT_credcache_finalize`, `PINT_credcache_lookup`, `PINT_credcache_insert`, and `PINT_credcache_remove`.

## Control Flow
Callers initialize the cache, insert verified credentials, lookup by credential, optionally remove entries, and finalize on shutdown.

## State And Persistence
No state is defined here; implementation state is a global `seccache_t`.

## Dependencies And Integration Points
Includes `pvfs2-config.h`, PVFS types, and `seccache.h`. It is visible only for `ENABLE_CREDCACHE` builds.

## Risks And Test Signals
The declared remove function lacks a matching implementation in `credcache.c`, creating a possible link-time failure if used. Compile and link tests in credential-cache builds are the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/security/module.mk.in

## Purpose
Controls which OrangeFS security source files are compiled into server and library builds based on feature macros.

## Important APIs, Types, And Functions
Adds `security-util.c` and `pint-uid-map.c` to `SERVERSRC`, adds `security-util.c` and `client-capcache.c` to `LIBSRC`, conditionally adds `seccache.c`, `capcache.c`, `pint-security.c`, `security-hash.c`, `pint-cert.c`, `cert-util.c`, `pint-ldap-map.c`, `credcache.c`, `certcache.c`, or `security-stubs.c`, and sets `MODCFLAGS_...pint-ldap-map.c := -DLDAP_DEPRECATED=1`.

## Control Flow
If key security is enabled, the build includes OpenSSL key-mode signing and optional credential cache. If certificate security is enabled, it includes certificate, LDAP, cache, and utility sources. If neither real mode is enabled, the server uses `security-stubs.c`.

## State And Persistence
No runtime state exists, but this file determines which security behavior is present in a binary.

## Dependencies And Integration Points
Integrates security code with the OrangeFS make system, server configuration, OpenSSL, LDAP, and optional caches.

## Risks And Test Signals
`NEEDCACHE = $(or ENABLE_CAPCACHE, ENABLE_CERTCACHE, ENABLE_CERTCACHE)` repeats `ENABLE_CERTCACHE` and omits `ENABLE_CREDCACHE`, so a credcache-only build may miss `seccache.c`. Build-matrix tests across key/cert/stub/cache combinations are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-cert.c

## Purpose
Manages the global OpenSSL X509 trust store used by certificate-mode OrangeFS security and verifies peer certificates against that store.

## Important APIs, Types, And Functions
Exports `PINT_init_trust_store`, `PINT_add_trusted_certificate`, `PINT_cleanup_trust_store`, and `PINT_verify_certificate`. Internal `verify_certificate_cb` logs X509 verification errors with subject, error depth, and OpenSSL error text.

## Control Flow
Initialization creates an `X509_STORE`. Trusted certificates are added with `X509_STORE_add_cert`. Verification creates an `X509_STORE_CTX`, installs the logging callback, initializes it with the global store and target certificate, calls `X509_verify_cert`, cleans up the context, and returns `0` or `-PVFS_ESECURITY`.

## State And Persistence
State is the global `X509_STORE *trust_store`; it is in memory only and is freed on cleanup. Trusted certificate contents originate from configuration-driven files loaded elsewhere.

## Dependencies And Integration Points
Depends on OpenSSL X509 store APIs, `pint-security` error logging, gossip, and PVFS errors. Used by certificate security initialization, credential verification, and UID mapping.

## Risks And Test Signals
Risks include global store lifetime, repeated initialization without cleanup, OpenSSL API differences, and callback installation on the shared store. Tests should verify CA load, trusted/untrusted certificate outcomes, cleanup/reinitialize, and logged diagnostics for expired or wrong-chain certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-cert.h

## Purpose
Declares the certificate trust-store API for certificate-mode OrangeFS security.

## Important APIs, Types, And Functions
Declares `PINT_init_trust_store`, `PINT_add_trusted_certificate`, `PINT_cleanup_trust_store`, and `PINT_verify_certificate` over OpenSSL `X509` objects.

## Control Flow
Security initialization creates the store, adds configured CA material, verification checks peer certificates, and finalization frees the store.

## State And Persistence
No state is declared in the header, though `pint-cert.c` owns a global trust store.

## Dependencies And Integration Points
Includes OpenSSL `x509.h`; used by `pint-security.c`, `pint-uid-map.c`, and certificate-mode verification paths.

## Risks And Test Signals
Risks are header availability in non-certificate builds and OpenSSL API compatibility. Compile coverage and trusted/untrusted certificate verification tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-cert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c

## Purpose
Implements LDAP integration for certificate-mode identity mapping and user/password authentication. It maps X509 certificate subjects to PVFS uid/gid values and authenticates users when retrieving certificates.

## Important APIs, Types, And Functions
Exports `PINT_ldap_initialize`, `PINT_ldap_map_credential`, `PINT_ldap_authenticate`, and `PINT_ldap_finalize`. Internal helpers log LDAP errors, load bind passwords from files, validate numeric attributes, parse certificate CNs, and convert OpenSSL slash-style subjects into LDAP DNs.

## Control Flow
Initialization opens the configured LDAP URI list, sets LDAPv3, loads an optional bind password, and binds as configured or anonymously. Mapping converts the credential certificate to X509, reads its subject, builds either a CN search filter or direct DN lookup, requests uid/gid attributes, retries searches after reconnect on LDAP failures, and returns mapped uid/group data or access denial. Authentication searches for a user DN, then creates a second LDAP handle and binds as that DN with the supplied password.

## State And Persistence
State is the global LDAP handle protected only during initialize/finalize. Passwords may be read from disk via `file:` configuration. No mapping results are persisted here; `certcache` may cache them.

## Dependencies And Integration Points
Depends on OpenLDAP, OpenSSL X509, server configuration, `cert-util`, `pint-security` error macros, `gen-locks`, and gossip. It is compiled with `LDAP_DEPRECATED=1` in certificate-security builds.

## Risks And Test Signals
`PINT_ldap_initialize` has early error returns that do not release `ldap_mutex`, LDAP searches use the global handle without locking, filters are built without escaping user/CN text, and DN conversion is simplistic. Tests should cover anonymous and bound init, password-file permissions, CN and DN search modes, retry/reconnect behavior, missing/non-numeric attributes, multi-entry warnings, authentication success/failure, and finalize after failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h

## Purpose
Declares LDAP identity-mapping and authentication functions used by certificate-mode OrangeFS security.

## Important APIs, Types, And Functions
Defines `PVFS2_LDAP_SEARCH_CN`, `PVFS2_LDAP_SEARCH_DN`, and `PVFS2_LDAP_RETRIES`, and declares `PINT_ldap_initialize`, `PINT_ldap_map_credential`, `PINT_ldap_authenticate`, and `PINT_ldap_finalize`.

## Control Flow
The lifecycle is initialize connection, map certificate credentials during request validation, authenticate users for certificate retrieval, and finalize the LDAP connection.

## State And Persistence
No state is declared in the header; the implementation owns a global LDAP connection handle.

## Dependencies And Integration Points
Includes PVFS config and types. It is consumed by `pint-security.c` and `pint-uid-map.c`.

## Risks And Test Signals
Risks are feature-mode exposure and fixed retry semantics. Compile tests for certificate builds and LDAP integration tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-security.c

## Purpose
Implements real OrangeFS security initialization, OpenSSL threading setup, capability signing/verification, credential signing/verification, and key/certificate loading for key-based or certificate-based security modes.

## Important APIs, Types, And Functions
Exports `PINT_security_initialize`, `PINT_security_finalize`, optional `PINT_security_cache_ca_cert`, `PINT_init_capability`, `PINT_sign_capability`, `PINT_verify_capability`, `PINT_server_to_server_capability`, `PINT_init_credential`, `PINT_sign_credential`, `PINT_verify_credential`, and `PINT_security_error`. Internal helpers set up OpenSSL thread callbacks, dynamic locks, load private keys, and load public-key keystores.

## Control Flow
Initialization is guarded by `security_init_mutex`, configures OpenSSL algorithms/errors/threading, initializes the public-key hash, requires server key config, then either loads private/public key files and validates host aliases or initializes the certificate trust store, loads CA/private key material, extracts the CA public key, and initializes LDAP. Capability signing sets issuer-provided fields, computes timeout, signs issuer/fsid/timeout/op mask/handle list with SHA1/RSA, and records signature size. Capability verification checks null and timeout cases, finds the public key from CA or keystore, and verifies the same field sequence. Credential signing allocates an `S:` issuer, sets timeout, signs uid/groups/issuer/timeout, and verification checks timeout, optional certificate trust/cache, and signature with the issuer public key.

## State And Persistence
Global state includes initialization status, OpenSSL mutex array, private key, certificate-mode CA cert/public key, and the security public-key hash table. Persistent inputs are server configuration, key files, keystore files, CA files, and LDAP settings. The module does not itself persist generated signatures beyond returned structures.

## Dependencies And Integration Points
Depends on OpenSSL EVP/X509/ERR/PEM APIs, server config manager, `security-hash`, `security-util`, certificate utilities, LDAP mapping, optional certificate cache, gossip, and generated PVFS request/security types. It is the real implementation selected by `security/module.mk.in`.

## Risks And Test Signals
Risks include SHA1/RSA-only support, complex OpenSSL-version conditionals, global lifetime leaks on some error paths, unsigned credentials accepted in certificate mode for limited operations, key/cert config hard failures, and timeout bypass configuration. Tests should cover idempotent initialize/finalize, missing/invalid key files, keystore parsing, host alias validation, capability and credential sign/verify success/failure, expired timeout behavior, cert-cache hit/miss verification, LDAP initialization errors, and OpenSSL threaded use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-security.h

## Purpose
Declares the OrangeFS security API, capability permission bits, and common error-checking macros.

## Important APIs, Types, And Functions
Defines permission bits `PINT_CAP_EXEC`, `PINT_CAP_WRITE`, `PINT_CAP_READ`, `PINT_CAP_SETATTR`, `PINT_CAP_CREATE`, `PINT_CAP_ADMIN`, `PINT_CAP_REMOVE`, `PINT_CAP_BATCH_CREATE`, and `PINT_CAP_BATCH_REMOVE`. Declares lifecycle, capability, credential, server-to-server capability, optional CA-cache, and error logging functions. Provides variadic `PINT_SECURITY_CHECK*` macros with Windows and GNU forms.

## Control Flow
Callers use initialization/finalization around security operations, initialize and sign outbound capability/credential structures, verify inbound structures, and use macros for common error-to-goto or error-to-return paths.

## State And Persistence
The header declares no state, but the APIs operate on signed PVFS structures and global security state initialized by the implementation.

## Dependencies And Integration Points
Includes PVFS config and types. It is used by real security, stubs, LDAP, UID mapping, certificate helpers, and server request validation code.

## Risks And Test Signals
Risks include macro behavior differences across compilers and permission-bit drift against server authorization logic. Tests should compile under Windows/GNU paths and verify each permission bit maps to expected access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c

## Purpose
Maps verified `PVFS_credential` objects to server-side uid and group arrays, using certificate cache/LDAP in certificate mode or direct credential fields in key mode.

## Important APIs, Types, And Functions
Exports `PINT_map_credential`. When certificate security is enabled without certcache, internal `check_ca_cert` detects whether a credential contains the trusted CA certificate for root mapping.

## Control Flow
The function validates required pointers, treats unsigned certificate-mode credentials as unmapped maximum uid/gid placeholders, then in certificate mode tries `certcache` first if available, falls back to LDAP mapping and caches successful results, or maps the CA certificate to root when certcache is disabled. In non-certificate mode it simply copies `userid`, `num_groups`, and `group_array` from the credential.

## State And Persistence
No state is owned here. It reads trust-store state, certificate cache state, LDAP configuration, and credential fields. Successful certificate-mode mappings may be persisted in memory through `certcache`.

## Dependencies And Integration Points
Depends on `pint-security`, `security-util`, optional OpenSSL trust store, `cert-util`, `pint-ldap-map`, and `certcache`. It is compiled into server builds by `security/module.mk.in`.

## Risks And Test Signals
The final no-groups check compares the `num_groups` pointer rather than `*num_groups`, so zero groups may not be rejected as intended. `group_array` is not null-checked before writes. Tests should cover unsigned credentials, certcache hit/miss, LDAP failure, CA root mapping, non-certificate direct copy, zero-group results, and group array bounds supplied by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h

## Purpose
Declares the credential-to-uid/group mapping API.

## Important APIs, Types, And Functions
Declares `PINT_map_credential(PVFS_credential *cred, PVFS_uid *uid, uint32_t *num_groups, PVFS_gid *group_array)`.

## Control Flow
Server authorization paths call this after credential verification to obtain POSIX-style identity information used by permission checks and request processing.

## State And Persistence
No state is declared. Mapping may consult caches or LDAP in the implementation depending on build mode.

## Dependencies And Integration Points
Includes PVFS config and types. Integrated with `pint-security`, LDAP mapping, and certificate cache code.

## Risks And Test Signals
Risks are caller-provided buffer sizing and feature-mode differences. Tests should validate key-mode and cert-mode mapping outputs and failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.c -->
# sources/distributed-fs/orangefs/src/common/security/seccache.c

## Purpose
Implements a generic locked security cache used by capability, credential, and certificate caches. It provides chained hash buckets, per-entry expiration, configurable properties, statistics, and implementation-specific callbacks.

## Important APIs, Types, And Functions
Exports `PINT_seccache_new`, `PINT_seccache_set`, `PINT_seccache_get`, `PINT_seccache_expired_default`, `PINT_seccache_lock`, `PINT_seccache_unlock`, `PINT_seccache_reset_stats`, `PINT_seccache_cleanup`, `PINT_seccache_lookup`, `PINT_seccache_lookup_cmp`, `PINT_seccache_insert`, and `PINT_seccache_remove`. Internal helpers print stats, wrap generic mutex calls, and remove expired entries from one or all chains.

## Control Flow
New cache allocation initializes a lock, method table, defaults, a hash-table array, one linked list per bucket, and a sentinel entry for each chain. Lookup computes the method-defined index, searches under lock, unlocks, checks expiration, removes expired hits, refreshes live hits, updates stats, and returns the entry. Insert allocates an entry, removes expired entries in the target chain, sets expiration, locks, adds to the list head, unlocks, and updates stats. Remove locks, searches/removes by entry data, unlocks, and calls the cache-specific cleanup method.

## State And Persistence
All state is in memory: description, callbacks, lock, property values, stats, and linked-list hash buckets. No entry or size limits are actually enforced by insertion despite stored properties.

## Dependencies And Integration Points
Depends on `llist`, `gen-locks`, PVFS types/errors, and gossip. Specialized caches provide hash, compare, expiration, cleanup, and debug methods.

## Risks And Test Signals
`PINT_seccache_set` locks `cache->lock` before checking `cache` for NULL, insert failure can return while still holding the lock, stats are updated partly outside locks, lookup returns mutable entry pointers after unlocking, and configured entry/size limits are unused. Tests should cover allocation failure cleanup, lookup hit/miss/expired, property get/set, insert failure paths, concurrent lookup/remove stress, sentinel handling, and stats frequency output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.h -->
# sources/distributed-fs/orangefs/src/common/security/seccache.h

## Purpose
Declares the generic security cache data model, callback table, properties, stats, locking type, and public API.

## Important APIs, Types, And Functions
Defines default entry, size, hash, timeout, and stats-frequency values; `seccache_prop_t`; `seccache_entry_t`; `seccache_methods_t`; `seccache_stats_t`; and `seccache_t`. Declares all `PINT_seccache_*` operations and debug enter/exit macros.

## Control Flow
Specialized caches instantiate a `seccache_methods_t`, create a cache with `PINT_seccache_new`, configure timeout or stats, insert and lookup entries, and clean up at shutdown.

## State And Persistence
The header defines the layout of in-memory cache state and per-entry data. No disk persistence or serialization is described.

## Dependencies And Integration Points
Includes PVFS types, `llist.h`, and `gen-locks.h`. It is the shared substrate for `capcache`, `certcache`, and `credcache`.

## Risks And Test Signals
Risks include exposing internals to callers, callback contract mismatch, and units confusion around timeout comments versus use as seconds in cache clients. Compile tests for all specialized caches and runtime tests for callback edge cases are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.c -->
# sources/distributed-fs/orangefs/src/common/security/security-hash.c

## Purpose
Maintains the key-mode security public-key lookup table, mapping issuer strings to OpenSSL `EVP_PKEY` objects.

## Important APIs, Types, And Functions
Exports `SECURITY_hash_initialize`, `SECURITY_hash_finalize`, `SECURITY_add_pubkey`, and `SECURITY_lookup_pubkey`. Internal `pubkey_entry_t` embeds a qhash link, issuer hash key, and owned public key. Helpers compare issuer strings and free entries.

## Control Flow
Initialization creates a global qhash table under `hash_mutex`. Adding a key allocates an entry, duplicates the issuer string, removes and frees any existing entry for that issuer, and inserts the new entry. Lookup searches by issuer and returns the stored `EVP_PKEY *`. Finalize drains and frees the table.

## State And Persistence
State is global and in memory: `pubkey_table`, initialization flag, and mutex. Public keys are loaded from the configured keystore by `pint-security.c` and freed when removed/finalized.

## Dependencies And Integration Points
Depends on OpenSSL EVP, `quickhash`, `quicklist`, `gen-locks`, and gossip. Used by capability and credential verification in key security mode.

## Risks And Test Signals
`SECURITY_lookup_pubkey` does not take `hash_mutex`, qhash's string hash is mask-based despite the prime table size, `SECURITY_add_pubkey` leaks the entry if `strdup` fails, and returned key pointers have no lifetime protection. Tests should cover initialize idempotence, duplicate replacement, lookup miss/hit, finalize cleanup, concurrent add/lookup, and distribution/collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.h -->
# sources/distributed-fs/orangefs/src/common/security/security-hash.h

## Purpose
Declares the issuer-to-public-key hash API used by key-based OrangeFS security.

## Important APIs, Types, And Functions
Declares `SECURITY_hash_initialize`, `SECURITY_hash_finalize`, `SECURITY_add_pubkey`, and `SECURITY_lookup_pubkey` over OpenSSL `EVP_PKEY` pointers.

## Control Flow
Security initialization creates the table, loads keystore entries with `SECURITY_add_pubkey`, verification paths call `SECURITY_lookup_pubkey`, and finalization frees all keys.

## State And Persistence
The header declares no state, but the implementation owns global in-memory key table state.

## Dependencies And Integration Points
Includes OpenSSL `evp.h`; used by `pint-security.c`.

## Risks And Test Signals
Risks are ownership ambiguity for `EVP_PKEY *` passed to add and returned from lookup. Link and lifecycle tests around keystore loading validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-stubs.c -->
# sources/distributed-fs/orangefs/src/common/security/security-stubs.c

## Purpose
Provides the non-secure implementation used when OrangeFS is built without real security. It preserves API shape and timeout behavior without cryptographic signing or verification.

## Important APIs, Types, And Functions
Implements the same lifecycle, capability, credential, and error-facing functions declared by `pint-security.h`: `PINT_security_initialize`, `PINT_security_finalize`, `PINT_init_capability`, `PINT_sign_capability`, `PINT_server_to_server_capability`, `PINT_verify_capability`, `PINT_init_credential`, `PINT_sign_credential`, and `PINT_verify_credential`.

## Control Flow
Initialize/finalize return success. Capability signing sets timeout and null signature fields. Capability verification accepts null capabilities and otherwise only checks timeout unless bypassed. Server-to-server capability builds an all-ops `S:` issuer and calls stub signing. Credential signing sets issuer, timeout, null signature, and verification checks timeout only.

## State And Persistence
No global state or persistent key material is used. The functions mutate caller-provided capability and credential structures.

## Dependencies And Integration Points
Depends on server configuration, PVFS types, `pint-util`, `security-util`, and `pint-security.h`. It is selected by `security/module.mk.in` when neither key nor certificate security is enabled.

## Risks And Test Signals
This intentionally provides no cryptographic trust. `PINT_sign_credential` assumes `cred->issuer` already points to writable storage, unlike the real implementation that allocates it. Tests should cover timeout accept/reject behavior, issuer buffer sizing, null capability acceptance, server-to-server capability construction, and build selection in no-security configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.c -->
# sources/distributed-fs/orangefs/src/common/security/security-util.c

## Purpose
Provides common helpers for formatting, copying, debugging, and cleaning `PVFS_capability`, `PVFS_credential`, and Windows security path data.

## Important APIs, Types, And Functions
Exports `PINT_print_op_mask`, `PINT_null_capability`, `PINT_capability_is_null`, `PINT_dup_capability`, `PINT_copy_capability`, `PINT_debug_capability`, `PINT_cleanup_capability`, `PINT_dup_credential`, `PINT_copy_credential`, `PINT_debug_credential`, `PINT_cleanup_credential`, and Windows-only `PINT_get_security_path`.

## Control Flow
Copy helpers first value-copy the structure, clear owned pointer fields, then deep-copy issuer, signatures, handle arrays, groups, and certificate buffers as applicable. Cleanup helpers free owned internals and clear or zero fields. Debug helpers emit issuer, ids, signatures, timeouts, masks, handles, groups, and certificate summaries. Windows path substitution replaces `%USERNAME%` tokens after checking output length.

## State And Persistence
No global state is owned. Functions allocate and free memory inside caller-provided structures and write debug logs. Windows path substitution is purely string processing.

## Dependencies And Integration Points
Depends on PVFS types/errors, gossip, `pint-util`, server config for declarations, and certificate-mode compile flags. Used by all security caches, signing/verification code, stubs, and client capability cache.

## Risks And Test Signals
Risks include assert-based issuer assumptions, cleanup setting credentials partially rather than full `memset`, copy failure cleanup paths, handling of the static `PVFS2_BLANK_ISSUER`, and Windows substitution edge cases. Tests should cover deep-copy independence, empty/null signatures, zero handles/groups, certificate-mode credential copies, repeated cleanup, op-mask formatting, and `%USERNAME%` path expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.h -->
# sources/distributed-fs/orangefs/src/common/security/security-util.h

## Purpose
Declares shared security utility functions and the unsigned-credential test macro.

## Important APIs, Types, And Functions
Defines `IS_UNSIGNED_CRED(cred)` as `sig_size == 0` and declares capability formatting/null/copy/debug/cleanup helpers, credential copy/debug/cleanup helpers, and Windows path substitution.

## Control Flow
Security code uses these declarations for object lifetime management around signing, verification, caching, and debug logging.

## State And Persistence
No state is declared. The functions operate on caller-owned PVFS security structures.

## Dependencies And Integration Points
Relies on PVFS security types being visible before inclusion. It is included broadly by security modules and client capability caching.

## Risks And Test Signals
Risks are implicit include-order requirements for `uint32_t`, `PVFS_*` types, and Windows-only declarations. Compile coverage in all security feature modes is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/codegen.c -->
# sources/distributed-fs/orangefs/src/common/statecomp/codegen.c

## Purpose
Generates C declarations and state-machine tables from the parsed statecomp abstract syntax tree.

## Important APIs, Types, And Functions
Exports `gen_machine`. Internal generators emit state declarations, unique run-function prototypes, state starts, action fields, transition tables, parallel-jump tables, return-code rows, next-state/return/terminate targets, and state endings. A qhash table de-duplicates run function declarations.

## Control Flow
`gen_machine` checks that states exist, emits forward declarations and the machine object, then for each state emits the action, optional PJMP table entries, transition table entries, and closing syntax. It sets `terminate_path_flag` when return or terminate transitions are generated. After generation it frees tasks, transitions, and states and resets the global state list for the next machine.

## State And Persistence
Uses global parser state `states`, `out_file`, and `terminate_path_flag`; static `runfunc_table` persists across machines to avoid duplicate declarations. Output is written to the generated C file.

## Dependencies And Integration Points
Depends on `statecomp.h`, `quickhash`, `quicklist`, and `pvfs2-internal.h` with malloc redefinition disabled. It is built into the compile-time `statecomp` translator.

## Risks And Test Signals
Risks include leaked `runfunc_table`, generated C syntax differences between Windows and designated-initializer builds, no semantic validation that transition target states exist, and abrupt asserts on allocation failures. Tests should run statecomp on `.sm` files with run/jump/pjmp, duplicate run functions, missing terminate paths, duplicate transition codes, and Windows-compatible output mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/codegen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in

## Purpose
Defines the make variables and generated-file relationships for building the `statecomp` source-to-source translator.

## Important APIs, Types, And Functions
Sets `STATECOMP`, `STATECOMPSRC`, and `STATECOMPGEN`; lists `statecomp.c`, `codegen.c`, generated `parser.c`, and generated `scanner.c`; records generated `scanner.c`, `parser.c`, and `parser.h`; and declares `scanner.c` depends on `parser.h` with generated files marked secondary.

## Control Flow
The build system uses this fragment to generate parser/scanner artifacts, compile statecomp, and preserve generated intermediates long enough for dependent rules.

## State And Persistence
No runtime state exists. Build artifacts are parser/scanner generated C and header files.

## Dependencies And Integration Points
Integrates flex/bison output with the OrangeFS build and the `.sm` state-machine compilation pipeline.

## Risks And Test Signals
Risks include stale generated parser/scanner files and missing generator dependencies. A clean build from no generated files and an incremental rebuild after `parser.y` or `scanner.l` changes are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/parser.y -->
# sources/distributed-fs/orangefs/src/common/statecomp/parser.y

## Purpose
Defines the yacc/bison grammar for statecomp's `.sm` machine-description language.

## Important APIs, Types, And Functions
Tokens include `machine`, `nested`, `state`, `run`, `pjmp`, `jump`, `return`, `terminate`, `success`, `default`, braces, semicolons, arrows, and identifiers. Grammar actions call `new_state`, `new_transition`, `new_task`, and `gen_machine`.

## Control Flow
The parser accepts one or more machines. Each machine contains state definitions. Each state has one action (`run`, `jump`, or `pjmp`) plus transitions. `success` becomes return code `0`, `default` becomes `-1`, and identifiers are copied with `estrdup`. PJMP actions collect task return-code-to-machine mappings before normal transitions.

## State And Persistence
Parser actions mutate static current pointers and the global state list declared in `statecomp.h`. Generated C output is produced when a complete machine is reduced.

## Dependencies And Integration Points
Depends on scanner tokens from `scanner.l`, allocation and AST helpers from `statecomp.c`, and code generation in `codegen.c`.

## Risks And Test Signals
Risks include no declared precedence needs but limited syntax diagnostics, no semantic target-state validation, and memory ownership split between parser strings and codegen cleanup. Tests should parse valid multi-machine files, nested machines, PJMP task lists, default/success transitions, duplicate states/transitions, and malformed syntax with correct line numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/scanner.l -->
# sources/distributed-fs/orangefs/src/common/statecomp/scanner.l

## Purpose
Defines the flex scanner for statecomp, copying normal C text through and tokenizing state-machine blocks delimited by `%%`.

## Important APIs, Types, And Functions
Recognizes identifiers, statecomp keywords, braces, semicolons, `=>`, C comments inside code mode, and bad-character errors. Exports `yywrap` and relies on `yylex` generated by flex.

## Control Flow
Outside code mode, most input is echoed to `out_file` and line numbers are tracked. On `%%`, the scanner enters `CODE` mode and returns parser tokens. On the closing `%%`, it emits a `#line` directive for non-Windows builds and returns to copying text. Comments in code mode are consumed while preserving line counts.

## State And Persistence
Uses scanner start conditions, global `line`, `out_file`, and `in_file_name`. It writes pass-through and generated-position output to the target C file.

## Dependencies And Integration Points
Includes `statecomp.h` and generated `parser.h`. It is generated into `scanner.c` by the build rules in `module.mk.in`.

## Risks And Test Signals
Risks include fixed-size bad-character buffer formatting, no nested comment handling, `yytext` pointer lifetime requiring parser-side duplication, and line directive behavior differences on Windows. Tests should cover pass-through C, multiple `%%` blocks, comments, invalid characters, keyword/identifier boundaries, and line-numbered parse errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/scanner.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c -->
# sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c

## Purpose
Provides the `statecomp` executable entry point, argument handling, output-file setup, parser invocation, final validation, diagnostics, and AST construction helpers.

## Important APIs, Types, And Functions
Defines globals `states`, `terminate_path_flag`, `line`, `out_file`, and `in_file_name`. Implements `main`, `parse_args`, `finalize`, `yyerror`, `emalloc`, `estrdup`, `new_state`, `new_transition`, and `new_task`.

## Control Flow
`main` parses arguments, opens input and output, writes a generated-file banner, calls `yyparse`, reports parser return class, and finalizes. Argument parsing requires an `.sm` input and optional output; absent output changes the extension to `.c`. Finalize deletes the output and exits if no generated transition set `terminate_path_flag`. AST helpers append unique states and unique transition return codes, while PJMP tasks are appended in order.

## State And Persistence
State is process-global while compiling one input file. Persistent output is the generated C file; error paths unlink it. Memory is mostly freed by `gen_machine` after each machine.

## Dependencies And Integration Points
Depends on `statecomp.h`, generated parser/scanner functions, standard I/O, Unix `unlink` or Windows `_unlink`, and `pvfs2-internal.h` with malloc redefinition disabled.

## Risks And Test Signals
Risks include process exit from helper functions, only extension-based input validation, output deletion on errors, and target-state validation deferred or absent. Tests should cover default output naming, explicit output naming, non-`.sm` rejection, syntax errors unlinking output, no-terminate validation, duplicate states/transitions, and multi-machine files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h -->
# sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h

## Purpose
Defines the statecomp AST structures, transition/action enums, global parser/codegen variables, and helper prototypes.

## Important APIs, Types, And Functions
Defines `enum transition_type`, `enum state_action`, `struct task`, `struct transition`, and `struct state`. Declares globals `states`, `terminate_path_flag`, `line`, `out_file`, and `in_file_name`, plus `yyerror`, `emalloc`, `estrdup`, `new_state`, `new_transition`, `new_task`, and `gen_machine`.

## Control Flow
Parser actions allocate and link these AST objects; code generation consumes and frees them machine by machine.

## State And Persistence
The header exposes mutable global state for the translator process. No runtime OrangeFS server state is involved.

## Dependencies And Integration Points
Requires `FILE` to be visible through including translation units. Used by `statecomp.c`, `parser.y`, `scanner.l`, and `codegen.c`.

## Risks And Test Signals
Risks include broad global coupling and lack of namespace isolation. Compile tests across generated parser/scanner/codegen units and parser behavior tests validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/statecomp/statecomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in

## Purpose
Adds the token utility implementation to OrangeFS library and server builds.

## Important APIs, Types, And Functions
Sets `DIR := src/common/token-utils` and appends `$(DIR)/token-utils.c` to both `LIBSRC` and `SERVERSRC`.

## Control Flow
The build system includes `token-utils.c` in shared client/library code and server code.

## State And Persistence
No runtime state exists in this make fragment.

## Dependencies And Integration Points
Integrates `token-utils` with code that needs delimiter-based token iteration.

## Risks And Test Signals
Risks are duplicate object inclusion or missing linkage if parent makefiles handle `LIBSRC`/`SERVERSRC` unexpectedly. Full client and server builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c -->
# sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c

## Purpose
Implements reusable delimiter tokenization helpers, primarily an allocation-free in-place iterator with optional heap-allocating token APIs behind `TOKEN_ENABLE_HEAP_VERSION`.

## Important APIs, Types, And Functions
Always compiled functions are `iterate_tokens_inplace`, `no_op_inplace`, `dump_token_inplace`, and `dump_tokens_inplace`. Optional heap functions include `iterate_tokens`, `free_token`, `free_tokens`, `dump_token`, `dump_tokens`, `get_token_count`, and `get_tokens`.

## Control Flow
The in-place iterator validates inputs, copies the input into caller-provided scratch storage with `strncpy`, treats token limit `0` as unlimited, then repeatedly calls `strtok_r`/`strtok_s`. For each token it optionally copies token text to caller-provided output buffers and optionally invokes an action callback, stopping on callback failure or token limit. The heap version first counts tokens, allocates a vector, duplicates each token, and frees partial results on allocation failure.

## State And Persistence
No global state is used. The functions mutate caller-provided scratch buffers and optionally allocate heap token arrays in the disabled-by-default heap variant.

## Dependencies And Integration Points
Depends on standard C string/stdio/limits headers and `token-utils.h`; Windows maps `strtok_r` to `strtok_s`. Included in both library and server builds.

## Risks And Test Signals
Callers must zero-initialize scratch buffers because `strncpy` may not terminate at `input_limit`; copy-out token buffers have the same truncation risk; heap `get_token_count` prints debug messages; and callback failure returns `-1` while count reports successful actions. Tests should cover null inputs, empty strings, repeated delimiters, token limits, copy-out truncation, callback failures, Windows tokenization, and optional heap build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h -->
# sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h

## Purpose
Declares token utility constants and tokenizer APIs.

## Important APIs, Types, And Functions
Defines `TOKEN_UTILS_DEFAULT_MAX_INPUT_STRLEN`, `PLUS_ONE(IN)`, and a disabled `TOKEN_ENABLE_HEAP_VERSION` switch. Declares the in-place iterator and debug/no-op helpers, plus heap token APIs when the feature macro is enabled.

## Control Flow
Callers allocate scratch storage, usually with `PLUS_ONE(max_len)`, then call `iterate_tokens_inplace` directly or through `dump_tokens_inplace`. Optional heap callers must free arrays with `free_tokens`.

## State And Persistence
No state is declared. The API contract relies on caller-owned buffers and optional caller-managed heap results.

## Dependencies And Integration Points
Used by server and library code that needs lightweight token parsing without bringing in additional parser dependencies.

## Risks And Test Signals
Risks include the macro name `PLUS_ONE` not matching comments that mention `LEN_PLUS_ONE`, disabled heap declarations being untested by default, and missing explicit include of integer types because only basic C types are used. Compile tests with and without `TOKEN_ENABLE_HEAP_VERSION` and tokenizer edge-case tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/token-utils.h -->
