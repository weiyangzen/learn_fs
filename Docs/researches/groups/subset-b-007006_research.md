<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/cpasswd.c -->
# sources/distributed-fs/coda/coda-src/auth2/cpasswd.c

## Purpose
Interactive `cpasswd` client for changing a Coda password through auth2 servers. It resolves the target `user[@realm]`, prompts for the old and new passwords, applies local strength checks, and calls the auth RPC helper to update `auth2.pw`.

## APIs, Types, and Functions
The only function is `main()`. It uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, `U_InitRPC()`, `U_GetAuthServers()`, `U_ChangePassword()`, `RPC2_freeaddrinfo()`, `getpwuid()`, `geteuid()`, and `getpass()`. RPC/auth return codes include `AUTH_SUCCESS`, `AUTH_DENIED`, `AUTH_BADKEY`, `AUTH_READONLY`, `AUTH_FAILED`, `RPC2_DEAD`, and `RPC2_NOTAUTHENTICATED`.

## Control Flow, State, and Persistence
Command parsing optionally accepts `-h SCM-host-name`, then extracts username and realm or falls back to the effective uid's passwd entry. It initializes `venus.conf` and `auth2.conf`, prompts once for the old password, then retries weak new passwords up to two times before accepting the user's insistence. After confirmation it fetches auth servers for the realm/host, sends the change request, prints a human-readable result, and exits. Persistent state is modified remotely by the auth server; this program only keeps stack password buffers.

## Dependencies and Integration
Integrates the auth2 user tools with RPC2/LWP, Coda config, realm parsing, and auth-server discovery. It depends on auth2 client helper functions and server-side `PWChangePasswd()` behavior in `pwsupport.c`.

## Risks and Test Signals
Risks include fixed 128-byte password buffers, `strncpy()` without explicit terminator on exact-size input, `getpass()` limitations, username length capped at 20, weak local policy, and returning success even for failed auth outcomes because it always exits `EXIT_SUCCESS` after the switch. Test signals are prompt/validation behavior, realm fallback, auth return-code mapping, and server-side password-file update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/cpasswd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/ctokens.c -->
# sources/distributed-fs/coda/coda-src/auth2/ctokens.c

## Purpose
Command-line token inspector that asks Venus/cache manager for Coda tokens and prints authentication status, Vice user id, and expiration time for a selected realm or all mounted realms.

## APIs, Types, and Functions
`GetTokens()` calls `U_GetLocalTokens()` into `ClearToken` and `EncryptedSecretToken`, checks `clear.EndTimestamp`, and formats `ctime()`. `main()` uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, `opendir()`, `readdir()`, and passwd/getlogin helpers.

## Control Flow, State, and Persistence
With an argument, it extracts a realm and queries only that realm. Without one, it reads the configured Coda mount point from `venus.conf`, enumerates non-dot entries below it, and treats each as a realm. It prints a header for the effective user, calls `GetTokens()` for each realm, and exits failure if the selected realm query failed. It does not persist data; state comes from Venus token storage.

## Dependencies and Integration
Depends on auth2 Venus APIs from `avenus.h`, Coda realm naming under the mount point, passwd APIs, and platform-specific Cygwin mount handling. It complements `clog` and `cunlog`.

## Risks and Test Signals
Risks include assuming realm names are direct mount entries, username may print as null if passwd lookup fails, expiration is checked only against local time, and multi-realm failures are ignored in the no-argument path. Test signals are `Not Authenticated` for `-ENOTCONN`, correct expiration formatting, and successful enumeration of configured mount roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/ctokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/cunlog.c -->
# sources/distributed-fs/coda/coda-src/auth2/cunlog.c

## Purpose
Minimal logout utility that tells Venus to delete locally held Coda tokens for a realm, effectively unauthenticating the user from that realm.

## APIs, Types, and Functions
`main()` uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, and `U_DeleteLocalTokens()`. The auth-facing data is only a realm string.

## Control Flow, State, and Persistence
If one argument is present, the code extracts its realm part; otherwise it starts with an empty realm and then allows `venus.conf`/`auth2.conf` to supply the configured default. It calls `U_DeleteLocalTokens(realm)` and exits success without checking a return value. Persistent effects are in Venus/cache-manager token state, not in this process.

## Dependencies and Integration
Integrates with Coda config files and the auth2 Venus local-token API. It is the inverse of token-acquisition tools and its result is observable through `ctokens`.

## Risks and Test Signals
Risks include silent success if token deletion fails, ambiguous empty/default realm behavior, and no usage diagnostics for extra arguments. Test signals are token disappearance in `ctokens`, correct default realm selection, and Venus-side purge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/cunlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/initpw.c -->
# sources/distributed-fs/coda/coda-src/auth2/initpw.c

## Purpose
One-shot conversion tool for generating initial auth2 password-file records from tab-separated cleartext input. It hex-encodes the fixed-size password key, optionally XOR-encrypting it with a supplied file key.

## APIs, Types, and Functions
`main()` parses `-x debuglevel` and `-k key`, initializes LWP, reads stdin lines, calls `parse()`, optionally invokes `rpc2_Encrypt(..., RPC2_XOR)`, and prints transformed records. `parse()` splits `<ViceId>\t<clear-password>\t<rest>`, zero-pads an `RPC2_EncryptionKey`, and returns the uninterpreted tail.

## Control Flow, State, and Persistence
Input is processed line by line. The first tab is replaced with NUL so the original line buffer becomes the ViceId field printed back by `main()`. The clear password is copied until tab, NUL, or key length, then the remaining tail is preserved. The tool writes only stdout; the caller redirects output to the password database.

## Dependencies and Integration
Depends on RPC2 encryption types, LWP initialization, and the auth2 password-file format consumed by `pwsupport.c`. It exists for bootstrapping `db/auth2.pw`.

## Risks and Test Signals
Risks include cleartext passwords on stdin, fixed 1000-byte input lines, aborting on malformed lines, `strncpy()` of the key without guaranteed full initialization for short values, and the intentionally weak XOR file-key transform. Test signals are stable hex output, unchanged trailing fields, warning when no key is supplied, and successful loading by `InitPW()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/initpw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwdefines.h -->
# sources/distributed-fs/coda/coda-src/auth2/pwdefines.h

## Purpose
Small shared header defining initialization mode constants for the auth2 password support layer.

## APIs, Types, and Functions
Defines `PWFIRSTTIME` as `0` and `PWNOTFIRSTTIME` as `1`, guarded by `_PWDEFINES_H`.

## Control Flow, State, and Persistence
No control flow or runtime state. The constants drive `InitPW()` behavior in `pwsupport.c`: first-time initialization seeds globals and allocates the password array, while later reloads refresh from disk.

## Dependencies and Integration
Included by `pwsupport.c` and any code that needs to call `InitPW()` with the correct mode.

## Risks and Test Signals
Risk is limited to API clarity: raw integer constants make accidental inversion possible. Test signals are successful first auth-server startup and password-file reload when mtime changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwdefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwsupport.c -->
# sources/distributed-fs/coda/coda-src/auth2/pwsupport.c

## Purpose
Server-side auth2 password database support. It loads `auth2.pw`, keeps an indexed in-memory key array by ViceId, validates users, returns login handshake/session keys, and appends password/user changes to the password file.

## APIs, Types, and Functions
Exports `InitPW()`, `PWGetKeys()`, `PWChangePasswd()`, `PWNewUser()`, `PWDeleteUser()`, `PWChangeUser()`, `IsAUser()`, `IsAdministrator()`, and `GetVname()`. Internal helpers include `BuildPWArray()`, `EnlargePW()`, `AppendPW()`, `IsADeletedUser()`, and `BogusKey()`. Important globals are `FileKey`, `NullKey`, `DeleteKey`, `PWFile`, `PWArray`, `PWLen`, `PWCount`, `PWTime`, `AdminID`, and `CheckOnly`.

## Control Flow, State, and Persistence
`InitPW(PWFIRSTTIME)` seeds the default file key, allocates `PWArray`, opens and shared-locks `db/auth2.pw`, forces mode `0600`, reads the full file, resolves the admin group id, initializes the all-ones delete key, and parses records. `PWGetKeys()` resolves a counted identity to a ViceId, reloads the file when mtime changes, rejects missing/deleted users, decrypts the stored key with `FileKey`, and generates a random session key. Mutating RPCs check read-only mode, connection private `UserInfo`, administrator or self privileges, user existence, and bogus-key sentinel collisions before calling `AppendPW()`. `AppendPW()` XOR-encrypts the key, hex-encodes it, appends a timestamped audit line under an exclusive lock, updates `PWArray`, and refreshes `PWTime`.

## Dependencies and Integration
Depends on RPC2 secure compare/encryption/random helpers, Coda file locking, `vice_config_path()`, protection database APIs `AL_NameToId()`, `AL_IdToName()`, `AL_GetInternalCPS()`, `AL_IsAMember()`, and auth2 RPC private connection state. It is the server counterpart to `cpasswd`, user-admin tools, and `initpw`.

## Risks and Test Signals
Risks include append-only growth requiring offline compaction, weak XOR-at-rest protection, abort-heavy error handling, global mutable state without obvious synchronization, a suspicious `otherInfo` validation condition that rejects spaces and non-graph characters, possible buffer truncation in append records, and reliance on mtime for reload detection. Test signals include successful login key retrieval, mtime-triggered reloads, deletion by all-ones key, read-only rejection, administrator enforcement, file mode correction, and password-change audit lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwsupport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwsupport.h -->
# sources/distributed-fs/coda/coda-src/auth2/pwsupport.h

## Purpose
Public declarations for the auth2 password support implementation used by auth server code and related administration paths.

## APIs, Types, and Functions
Declares global `RPC2_EncryptionKey FileKey`, `char *PWFile`, and functions `InitPW()`, `PWGetKeys()`, `PWChangePasswd()`, `PWNewUser()`, `PWDeleteUser()`, and `PWChangeUser()`. Interfaces use RPC2 handles, counted byte strings, ViceIds, encryption keys, and RPC strings.

## Control Flow, State, and Persistence
No runtime control flow in the header. It exposes the persistent password-file lifecycle through `InitPW()` and append-based mutation functions.

## Dependencies and Integration
Requires auth2/RPC2 type definitions to be visible before inclusion. It binds auth RPC handlers to the password-file backend in `pwsupport.c`.

## Risks and Test Signals
Risks include exposing mutable globals and omitting prototypes for some non-static helpers used elsewhere. Test signals are compile-time linkage against auth2 handlers and matching signatures with RPC stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/pwsupport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokenfile.c -->
# sources/distributed-fs/coda/coda-src/auth2/tokenfile.c

## Purpose
Serialization helper for Coda token files. It writes and reads a `ClearToken` plus `EncryptedSecretToken` as base64 with network-byte-order fields.

## APIs, Types, and Functions
Exports `WriteTokenToFile()` and `ReadTokenFromFile()`. Internal `export()` converts `ClearToken` integer fields with `htonl()`, and `import()` converts them back with `ntohl()`. Uses `coda_base64_encode()` and `coda_base64_decode()`.

## Control Flow, State, and Persistence
Writing allocates a combined binary buffer, temporarily converts the caller's clear token to network order, copies clear and secret tokens, restores host order, sets `umask(0177)`, writes a `*** Coda Token ***` marker and base64 payload, then frees the buffer. Reading opens the file, skips the first line, decodes base64, validates the exact combined size, copies data into caller buffers, converts the clear token to host order, and exits on failure. Token files are the persistent artifact.

## Dependencies and Integration
Used by `tokentool.c` and any offline token import/export path. Depends on auth2 token types and base64 utilities.

## Risks and Test Signals
Risks include no `malloc()`/`fopen()` checks on write, process-global `umask()` side effects, fatal `exit()` inside a library helper, and mutating the caller's token during serialization. Test signals are round-trip byte equality, mode restricted by umask, corrupt-size detection, and endian-stable files across hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokenfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokenfile.h -->
# sources/distributed-fs/coda/coda-src/auth2/tokenfile.h

## Purpose
Header for token-file serialization helpers.

## APIs, Types, and Functions
Includes `auth2.h` and declares `WriteTokenToFile(char *filename, ClearToken *cToken, EncryptedSecretToken sToken)` and `ReadTokenFromFile(char *filename, ClearToken *cToken, EncryptedSecretToken sToken)`.

## Control Flow, State, and Persistence
No runtime behavior. The declared functions persist token pairs in a base64 file and read them back.

## Dependencies and Integration
Used by `tokentool.c` and implemented by `tokenfile.c`; requires auth2 token structures.

## Risks and Test Signals
Risks are signature-level: mutable `char *` filenames and array-like token parameters do not express constness or sizes. Test signals are successful compilation and tokenfile round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokenfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokentool.c -->
# sources/distributed-fs/coda/coda-src/auth2/tokentool.c

## Purpose
Interactive utility for generating Coda token files manually from a ViceId, validity duration, shared secret, and output filename.

## APIs, Types, and Functions
Defines input helpers `read_int()`, `read_float()`, and `read_string()`. `main()` uses `rpc2_InitRandom()`, `getauth2key()`, `generate_CodaToken()`, and `WriteTokenToFile()` with `ClearToken`, `EncryptedSecretToken`, `RPC2_EncryptionKey`, and `AUTH2KEYSIZE`.

## Control Flow, State, and Persistence
The program prompts on stdin/stdout, validates only that numeric answers begin with a digit, truncates the shared secret into an RPC2 key, derives an auth2 key, strips the filename newline, generates a token valid for `duration * 3600`, and writes it. Persistence is the generated token file.

## Dependencies and Integration
Depends on RPC2 random initialization, Coda auth token generation, and tokenfile serialization. It is an offline/admin-oriented producer for tokens understood by Venus/auth2.

## Risks and Test Signals
Risks include weak input validation, `fflush(stdin)` undefined behavior, a likely bug using `sizeof(RPC2_KEYSIZE)` instead of `sizeof(token)` in `memset()`, secret truncation, heap strings retaining secrets until free, and no write-error checks. Test signals are generated token readability, expected expiration window, and successful use by token consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/tokentool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/Makefile.am -->
# sources/distributed-fs/coda/coda-src/dir/Makefile.am

## Purpose
Automake definition for the internal Coda directory library.

## APIs, Types, and Functions
Builds `libcodadir.la` from `fid.c`, `codadir.c`, `codadir.h`, `dirbody.c`, `dirbody.h`, `dirinode.c`, and `dhcache.c`. It sets include paths for RPC2/RVM, base, kerndep, util, and vicedep headers.

## Control Flow, State, and Persistence
No runtime flow. Build state is limited to automake target composition and compiler flags.

## Dependencies and Integration
This library is linked by directory-aware tools such as `removeinc` and by server/client code that manipulates Coda directory bodies and DirInodes.

## Risks and Test Signals
Risks are missing test utilities from the build target and tight include coupling to generated vicedep headers. Test signals are successful `libcodadir.la` build and downstream link of consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/coda_dir.h -->
# sources/distributed-fs/coda/coda-src/dir/coda_dir.h

## Purpose
Legacy public directory and buffer interface, mostly exposing old AFS-style directory operations over `long *` file identifiers.

## APIs, Types, and Functions
Declares directory operations `NameBlobs()`, `Create()`, `Delete()`, `MakeDir()`, `Lookup()`, `GetBlob()`, `DirHash()`, `EnumerateDir()`, `DirToNetBuf()`, `FindName()`, `IsEmpty()`, and `Length()`. It defines `struct buffer` and declares buffer-cache routines `DInit()`, `DRead()`, `DRelease()`, `DFlush()`, `DNew()`, `DZap()`, plus salvage APIs `DirOK()` and `DirSalvage()`.

## Control Flow, State, and Persistence
No implementation in this header. The API implies page-buffered persistent directory files addressed by a five-int cache key and page number, with dirty/locker fields for cache state.

## Dependencies and Integration
Used by old salvage code and tests. Newer code primarily uses `codadir.h`/`dirbody.h`, so this header is a compatibility bridge.

## Risks and Test Signals
Risks include K&R-era prototypes, `long *` untyped identifiers, platform-specific `buffer` typedef, and stale declarations that may no longer match modern implementations. Test signals are legacy salvage/test compilation and correct buffer-cache behavior where still linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/coda_dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/codadir.c -->
# sources/distributed-fs/coda/coda-src/dir/codadir.c

## Purpose
Thread-safe `DirHandle` wrapper around low-level `DIR_*` directory-body functions. It handles locking, dirty marking, RVM/VM allocation, and ViceFid/DirFid conversion.

## APIs, Types, and Functions
Exports lock helpers `DH_LockW/R()` and `DH_UnLockW/R()`, lifecycle helpers `DH_Init()`, `DH_Alloc()`, `DH_FreeData()`, `DH_Data()`, and operation wrappers `DH_Length()`, `DH_Convert()`, `DH_Create()`, `DH_IsEmpty()`, `DH_Lookup()`, `DH_LookupByFid()`, `DH_Delete()`, `DH_Print()`, `DH_DirOK()`, `DH_MakeDir()`, and `DH_EnumerateDir()`.

## Control Flow, State, and Persistence
Read operations acquire a read lock, call the corresponding `DIR_*` function, then unlock. Mutations acquire a write lock, set `dh_dirty`, and call `DIR_Create()`, `DIR_Delete()`, or `DIR_MakeDir()`, with transaction checks delegated to lower layers when data is in RVM. Allocation chooses `rvmlib_rec_malloc()` or `malloc()` and zeros the buffer; freeing mirrors that choice.

## Dependencies and Integration
Depends on LWP locks, RVM library helpers, `codadir.h`, `dirbody.h`, and FID conversion routines from `fid.c`. It is the main integration surface for vnode/cache code that should not manipulate directory pages directly.

## Risks and Test Signals
Risks include `DH_FreeData()` returning while still holding the lock if `dh_data` is null, duplicate prototypes in the header, dirty-bit management requiring external commit discipline, and transaction-sensitive calls. Test signals are create/delete/lookup consistency, dirty flag transitions, `DIR_DirOK()` after mutations, and RVM transaction assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/codadir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/codadir.h -->
# sources/distributed-fs/coda/coda-src/dir/codadir.h

## Purpose
Primary public interface for Coda directory handles, directory entries, directory inodes, directory-handle cache entries, and file identifier helpers.

## APIs, Types, and Functions
Defines `DIR_PAGESIZE`, `DIR_MAXPAGES`, data-location constants, `DirHandle`, `DirNFid`, `DirEntry`, and `DirInode`. Declares `DIR_Init()`, all `DH_*` operations, FID helpers (`FID_EQ()`, `FID_Cmp()`, local/disconnected/fake-root makers), `DIR_*` body helpers, `DI_*` inode copy/refcount/page routines, and `DC_*` cache functions.

## Control Flow, State, and Persistence
No implementation, but it describes the split: `DirHandle` owns locked contiguous `DirHeader` data, `DirInode` persists page pointers and refcount, and the `DCEntry` cache bridges the two. Directory data can live in RVM or VM depending on initialization.

## Dependencies and Integration
Depends on LWP locks, Coda kernel/Vice common FID types, doubly linked lists, and transaction annotations. It is included by directory library code, repair tooling, and Coda vnode/server components.

## Risks and Test Signals
Risks include a wide mutable API, duplicate declarations, exposed opaque pointer typedefs without full cache structure, fixed maximum of 128 pages, and macro comparisons assuming same volume. Test signals are clean cross-module compilation and runtime directory operations through handle, inode, and cache layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/codadir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dhcache.c -->
# sources/distributed-fs/coda/coda-src/dir/dhcache.c

## Purpose
Directory-handle cache keyed by `DirInode`, used as a child of the Coda vnode cache. It maps persistent/inode directory pages to mutable `DirHandle` copies and tracks references, dirty state, and copy-on-write handoff.

## APIs, Types, and Functions
Defines internal `struct DCEntry` with hash/list links, counts, `DirHandle`, primary `PDirInode`, and COW inode. Public routines include `DC_HashInit()`, `DC_Get()`, `DC_Put()`, `DC_New()`, `DC_Rehash()`, `DC_Drop()`, `DC_Count()`, `DC_SetCount()`, `DC_Refcount()`, `DC_SetRefcount()`, `DC_DC2DH()`, `DC_DH2DC()`, `DC_DC2DI()`, `DC_SetDI()`, `DC_SetDirh()`, `DC_SetCowpdi()`, `DC_Cowpdi()`, `DC_SetDirty()`, and `DC_Dirty()`. Internal helpers are `dc_Grow()`, `dc_GetFree()`, and `DC_Hash()`.

## Control Flow, State, and Persistence
`DC_HashInit()` initializes the global lock, hash buckets, free list, and new-list. `DC_Get()` looks up by inode, increments `dc_count`, removes first users from the free list, and refreshes flushed handle data with `DI_DiToDh()`; misses allocate a free entry and hash it. `DC_Put()` returns clean zero-user entries to the free list. `DC_New()` creates dirty uncommitted entries on `dnewlist`, and `DC_Rehash()` moves them to the hash table after inode creation.

## Dependencies and Integration
Depends on LWP locking, `dllist`, `DirInode` conversion, and `DH_FreeData()`. It integrates vnode lifetime with directory copy-on-write and commit paths.

## Risks and Test Signals
Risks include pointer-derived hash distribution, global lock granularity, assertions that entries are clean when freed, no freelist destruction path, possible list misuse if counts underflow, and cache data refresh depending on valid `DirInode` pages. Test signals are repeated get/put cycles, cache hit refcounts, COW commit rehashing, dirty-entry exclusion from freelist, and leak checks around `DC_Drop()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dhcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirbody.c -->
# sources/distributed-fs/coda/coda-src/dir/dirbody.c

## Purpose
Core Coda directory body implementation. It manages the 2 KB page format, blob allocation, hash chains, name/FID lookup, create/delete, directory initialization, structural validation, printing, comparison, and conversion to Venus BSD-style directory files.

## APIs, Types, and Functions
Exports `DIR_Init()`, `DIR_rvm()`, `DIR_Length()`, `DIR_Page()`, `DIR_Create()`, `DIR_Delete()`, `DIR_MakeDir()`, `DIR_Setpages()`, `DIR_Free()`, `DIR_Print()`, `DIR_PrintChain()`, `DIR_Lookup()`, `DIR_LookupByFid()`, `DIR_EnumerateDir()`, `DIR_Compare()`, `DIR_IsEmpty()`, `DIR_Hash()`, `DIR_DirOK()`, and `DIR_Convert()`. Important internals are `dir_NameBlobs()`, `dir_FindBlobs()`, `dir_AddPage()`, `dir_New()`, `dir_Extend()`, `dir_FreeBlobs()`, `dir_FindItem()`, network-order FID helpers, and `dir_DirEntry2VDirent()`.

## Control Flow, State, and Persistence
`DIR_Init()` selects RVM or VM allocation globally. Directories store a page header, allocation map, and 128 hash buckets; entries are fixed 32-byte blobs, with long names consuming contiguous blobs. Creation validates name length, rejects duplicates, allocates blobs, writes a network-order FID, and threads the entry into a hash chain. Deletion unlinks from the hash chain and frees blobs. `DIR_MakeDir()` creates one page, reserves header blobs, marks unused pages as fully free, and inserts `.` and `..`. `DIR_Convert()` rewrites entries into a Unix/Venus dirent file with block-boundary padding. `DIR_DirOK()` reconstructs expected allocation maps and verifies magic, page counts, hash bucket placement, flags, and name lengths.

## Dependencies and Integration
Depends on RVM transaction helpers, Coda kernel dirent/FID structures, LWP lock headers, and `codadir.h`/`dirbody.h`. `codadir.c` supplies locking around these routines, and `dirinode.c` persists the page data.

## Risks and Test Signals
Risks include global `dir_data_in_rvm`, transaction aborts outside RVM transactions, maximum 128 pages, fixed hash table and blob layout, case-insensitive lookup lacking correct index/preventry support, possible endian bug in page magic check for non-first pages, assertion-heavy error paths, and mmap/file truncation assumptions in conversion. Test signals are `DIR_DirOK()` after every mutation, long-name blob allocation/freeing, hash-chain lookup/delete, page growth to limits, RVM transaction enforcement, and `dirtest` conversion/listing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirbody.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirbody.h -->
# sources/distributed-fs/coda/coda-src/dir/dirbody.h

## Purpose
Private directory-body layout and function declarations for the Coda directory implementation.

## APIs, Types, and Functions
Defines page/blob constants `LOGPS`, `NHASH`, `EPP`, `LEPP`, `ESZ`, `LESZ`, `DHE`, and `FFIRST`. Defines `DirBlob`, `PageHeader`, and `DirHeader`. Declares `DIR_rvm()`, `DIR_IsEmpty()`, `DIR_Free()`, `DirHash()`, `DirToNetBuf()`, `DIR_MakeDir()`, `DIR_LookupByFid()`, `DIR_Lookup()`, `DIR_EnumerateDir()`, `DIR_Create()`, `DIR_Length()`, `DIR_Delete()`, `DIR_PrintChain()`, `DIR_Hash()`, `DIR_DirOK()`, `DIR_Convert()`, and `DIR_Setpages()`.

## Control Flow, State, and Persistence
No control flow. The structs define the persistent in-memory/RVM representation: a first page containing page header, allocation map, and hash table, followed by additional pages of blob slots.

## Dependencies and Integration
Used by `dirbody.c`, `codadir.c`, and tests. It relies on `DIR_MAXPAGES`, `PDirHeader`, `DirEntry`, `DirFid`, and Coda FID/volume types from `codadir.h`.

## Risks and Test Signals
Risks include layout compatibility sensitivity, magic constants tied to 2 KB pages and 32-byte blobs, and stale legacy declarations. Test signals are binary layout stability and successful `DIR_DirOK()` validation of directories made by current code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirbody.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirinode.c -->
# sources/distributed-fs/coda/coda-src/dir/dirinode.c

## Purpose
Persistence bridge between contiguous `DirHandle` data and page-array `DirInode` objects, including RVM and VM copy/refcount management.

## APIs, Types, and Functions
Exports `DI_DiToDh()`, `DI_DhToDi()`, `DI_Dec()`, `DI_Inc()`, `DI_Count()`, `DI_Pages()`, `DI_Page()`, `DI_Copy()`, `DI_VMCopy()`, `DI_VMDec()`, and `DI_VMFree()`. Internal `DI_New()` allocates a new RVM inode.

## Control Flow, State, and Persistence
`DI_DiToDh()` allocates contiguous VM memory and copies each inode page into it for handle use. `DI_DhToDi()` runs in an RVM transaction, creates an inode if needed, copies each handle page into RVM page slots, updates refcount from the cache entry, and frees no-longer-needed pages. `DI_Dec()` and `DI_Inc()` mutate persistent refcounts, freeing pages and inode when the count reaches zero. Copy routines duplicate page arrays for RVM or VM.

## Dependencies and Integration
Depends on RVM allocation/range APIs, transaction checks, `DIR_Page()`, `DH_Length()`, and `DC_*` cache accessors. It integrates with vnode copy-on-write and commit paths.

## Risks and Test Signals
Risks include transaction requirements, assertion-heavy allocation failures, a likely reversed `memcpy()` in `DI_VMCopy()`, no decrement writeback in `DI_VMDec()` when refcount is above one, and fixed page-array limits. Test signals are page-count preservation, copy independence, refcount free behavior, RVM range coverage, and handle-to-inode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirinode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirtest.c -->
# sources/distributed-fs/coda/coda-src/dir/dirtest.c

## Purpose
Interactive and scriptable test harness for RVM-backed Coda directory operations.

## APIs, Types, and Functions
Registers parser commands for `init`, `ok`, `mdir`, `free`, `bulk`, `create`, `list`, `vdir`, `rdsfree`, `delete`, `empty`, `length`, `compare`, `convert`, `lookup`, `fidlookup`, `hash`, `printchain`, and `quit`. Uses `DH_*`, `DIR_*`, FID helpers, RVM/RDS initialization, and parser APIs.

## Control Flow, State, and Persistence
`main()` validates log/data files, initializes LWP and per-thread RVM data, loads an RDS heap into global `dd`, selects RVM directory mode, and enters an interactive parser or executes commands from a file. Commands begin/end RVM transactions around mutations, operate on up to 100 `DirHandle` slots, and print diagnostics. `dt_bulktest()` repeatedly creates/deletes directories and RVM allocations to stress allocation/free behavior.

## Dependencies and Integration
Depends on RVM/RDS, LWP, parser utilities, and the directory library. It provides manual regression coverage for directory body, handle, conversion, and transaction behavior.

## Risks and Test Signals
Risks include old command parser assumptions, several rough edges in argument strings, possible bad pointer/free behavior in `dt_free all`, and dependence on external RVM log/data setup. Test signals include `ok`/`DIR_DirOK`, create/delete lookup results, converted directory parsing through `vdir`, bulk stress completion, and transaction end status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/dirtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/fid.c -->
# sources/distributed-fs/coda/coda-src/dir/fid.c

## Purpose
Utility functions for comparing, printing, copying, and constructing Coda `ViceFid` and directory-local `DirFid` identifiers, including special local/disconnected/repair FID forms.

## APIs, Types, and Functions
Exports `FID_PrintFid()`, `FID_CpyVol()`, `FID_Int2DFid()`, `FID_NFid2Int()`, `FID_VFid2DFid()`, `FID_DFid2VFid()`, `FID_Cmp()`, `FID_EQ()`, `FID_VolEQ()`, `FID_IsDisco()`, `FID_IsLocalDir()`, `FID_IsLocalFile()`, `FID_MakeDiscoFile()`, `FID_MakeDiscoDir()`, `FID_MakeSubtreeRoot()`, `FID_MakeLocalDir()`, `FID_MakeLocalFile()`, `FID_IsFakeRoot()`, `FID_MakeLocalSubtreeRoot()`, `FID_MakeRoot()`, `FID_IsVolRoot()`, and `FID_()`.

## Control Flow, State, and Persistence
Most functions directly fill or compare fields. Static constants define fake/local volume and vnode sentinel values: local file/dir vnodes, fake subtree root vnode, and root vnode/unique. `FID_()` formats a FID into one of four rotating static buffers.

## Dependencies and Integration
Used by directory handles, repair code, and conflict/disconnected operation paths. Depends on Coda FID type definitions and network byte-order helpers for `DirNFid` conversion.

## Risks and Test Signals
Risks include static buffer reuse in `FID_()`, sentinel collisions if real IDs overlap, no volume assignment in `FID_DFid2VFid()`, and global constants encoded as mutable statics. Test signals are ordering/equality checks, root/local/disconnected detection, and correct directory entry FID conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/fid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/salvage.cc -->
# sources/distributed-fs/coda/coda-src/dir/salvage.cc

## Purpose
Legacy directory salvager that copies apparently valid entries from a suspect directory into a newly made target directory.

## APIs, Types, and Functions
Implements `DirSalvage(long *fromFile, long *toFile)`. Uses legacy `MakeDir()`, `Delete()`, `DRead()`, `GetBlob()`, `Create()`, and `DRelease()` from `coda_dir.h`/old private directory headers.

## Control Flow, State, and Persistence
The function creates an empty target directory, deletes its `.` and `..`, reads the source first page, estimates used pages by scanning the allocation map, then walks each hash chain. For each in-range entry with a readable blob, it calls `Create()` on the target using the entry name and a pointer-adjusted FID representation, then releases buffers. It returns zero after best-effort copying.

## Dependencies and Integration
Depends on old buffer-cache directory APIs and private layout names. It is not aligned with the newer `codadir.h`/`dirbody.h` API and appears mostly historical.

## Risks and Test Signals
Risks are high: comments call out unsafe pointer arithmetic for FID shape, weak page-validity heuristics, best-effort continuation after errors, and legacy type/layout drift. Test signals are limited to salvaged target readability and retained good entries under the old directory implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/salvage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/test.c -->
# sources/distributed-fs/coda/coda-src/dir/test.c

## Purpose
Small legacy command-line driver for checking and optionally salvaging a directory by numeric file id.

## APIs, Types, and Functions
K&R-style `main()` calls `DInit(20)`, `DirOK()`, optional `DirSalvage()`, and `DFlush()`. It parses one or two integer arguments with `atoi()`.

## Control Flow, State, and Persistence
With one argument it checks the source fid; with two it checks and then salvages from source to target. It initializes the old directory buffer cache and flushes it before exit. Persistence occurs through the legacy directory storage touched by `DirSalvage()`.

## Dependencies and Integration
Depends on old `coda_dir.h` buffer/salvage APIs and a working legacy directory backend.

## Risks and Test Signals
Risks include K&R C, missing includes/prototypes in the snippet, a `printf("DirOK returned %d.\n")` bug that omits the value, weak argument validation, and reliance on legacy APIs. Test signals are `DirOK` output, salvage return code, and subsequent readability of the target directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/dir/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/Makefile.am -->
# sources/distributed-fs/coda/coda-src/egasr/Makefile.am

## Purpose
Automake rules for client-side easy graphical ASR/repair utilities.

## APIs, Types, and Functions
When `BUILD_CLIENT` is enabled, builds `filerepair` and `removeinc`, and distributes scripts `xfrepair` and `xaskuser`. `filerepair` links `libkerndep` and `libbase`; `removeinc` also links `libcodadir`.

## Control Flow, State, and Persistence
No runtime behavior. Build metadata wires repair programs to kernel-dependency pioctl support and directory helpers.

## Dependencies and Integration
Depends on base, kerndep, vicedep, dir, and vv include trees. It integrates these utilities into the client installation.

## Risks and Test Signals
Risks include client-only conditional coverage and script/runtime dependencies not represented in link checks. Test signals are successful client build and installed `filerepair`, `removeinc`, `xfrepair`, and `xaskuser`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/filerepair.c -->
# sources/distributed-fs/coda/coda-src/egasr/filerepair.c

## Purpose
Simple file-conflict repair helper that replaces an inconsistent Coda file with the contents of another regular file.

## APIs, Types, and Functions
Defines `getfid()` using `pioctl(..., _VIOC_GETFID)` to read `ViceFid`, `ViceVersionVector`, and realm. `main()` validates arguments and the repair file with `stat()`, builds an `@Volume.Vnode.Unique@realm` repair path when possible, and calls `pioctl(..., _VIOC_REPAIR)`.

## Control Flow, State, and Persistence
The program ensures the second argument exists and is regular, resolves it to a Coda FID if possible, otherwise uses its pathname, submits that as repair input for the inconsistent first argument, tolerates `ETOOMANYREFS`, then stats the repaired object before exiting. Persistent state changes are performed by Venus/server repair logic.

## Dependencies and Integration
Depends on `pioctl()`, Coda ioctl numbers, Vice FID/version-vector structures, and Venus repair semantics. It is invoked by `xaskuser`.

## Risks and Test Signals
Risks include weak regular-file check using `statbuf.st_mode & S_IFREG`, no detailed conflict validation, fixed 2 KB ioctl buffers, and success ambiguity when `ETOOMANYREFS` is returned. Test signals are successful `_VIOC_REPAIR`, repaired object stat success, and `xfrepair` workflows using selected replicas or named files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/filerepair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/removeinc.c -->
# sources/distributed-fs/coda/coda-src/egasr/removeinc.c

## Purpose
Helper for removing an inconsistent file by first repairing it with an empty temporary file and then unlinking it.

## APIs, Types, and Functions
`IsObjInc()` detects conflict state through `stat()`, dangling symlink parsing of `@vol.vnode.unique@realm`, and `_VIOC_GETFID` output. `main()` validates inconsistency, rejects non-local directories with `ISDIR()` and `FID_IsLocalDir()`, creates a temporary file with `mkstemp()`, calls `_VIOC_REPAIR`, unlinks the temp file, then unlinks the target.

## Control Flow, State, and Persistence
If the target is already a dangling repair symlink, the FID is parsed from the symlink. Otherwise Venus supplies FID/version-vector information; an undefined StoreId or directory/file mismatch marks the object inconsistent. The persistent effects are Venus repair state and final filesystem unlink.

## Dependencies and Integration
Depends on `pioctl()`, `codadir.h` FID macros/helpers, Coda ioctl numbers, and local filesystem temp files. It is called by `xfrepair` when the user chooses removal.

## Risks and Test Signals
Risks include `/tmp` temporary-file exposure window, fixed ioctl buffers, broad success exit when the object is not inconsistent, directory conflict limitations, and symlink parsing assumptions. Test signals are detection of repair symlinks, rejection of directories requiring manual removal, successful empty repair, and target unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/removeinc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/xaskuser -->
# sources/distributed-fs/coda/coda-src/egasr/xaskuser

## Purpose
Tk/Wish UI script that asks the user how to repair an inconsistent file: remove it, use a replica, or use another file.

## APIs, Types, and Functions
Defines Tcl procedures `mkbuttons`, `GetIncResp`, `getreplicas`, `makeentries`, `getentries`, `oklistboxcommand`, and `repairwithnamedfile`. It invokes external `filerepair` and uses Tk widgets including radiobuttons, entry, listbox, scrollbar, canvas, and buttons.

## Control Flow, State, and Persistence
The script receives directory and filename, constructs `oname`, lists children under the conflict expansion, and displays replica metadata from `ls -l`. On OK it exits with codes: `0` no action/cancel, `1` remove, `2` repaired from selected replica, `3` repaired from named file. For replica or named-file repair it runs `filerepair` before exit.

## Dependencies and Integration
Depends on Wish/Tk, shell execution, `filerepair`, and the expanded repair directory layout created by `cfs beginrepair`. It is launched by `xfrepair`.

## Risks and Test Signals
Risks include command execution without robust error reporting, path/list handling with whitespace, reliance on X display, old Tk `pack append` syntax, and hidden `filerepair` failures due to `catch`. Test signals are correct exit code, visible replica list, successful `filerepair` invocation, and integration with `xfrepair` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/xaskuser -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/xfrepair -->
# sources/distributed-fs/coda/coda-src/egasr/xfrepair

## Purpose
Shell wrapper for graphical file repair. It authenticates, starts Coda repair mode, delegates user choice to `xaskuser`, ends repair mode, and optionally removes inconsistent files.

## APIs, Types, and Functions
Uses external commands `ctokens`, `cfs`, `xaskuser`, and `removeinc`; shell utilities `dirname` and `basename`; and a trap to run `cfs endrepair`.

## Control Flow, State, and Persistence
The script requires one filename and a valid Coda token. It chooses `xaskuser` only when `$DISPLAY` is set, starts `cfs beginrepair`, rejects local/global conflicts that expose both `local` and `global`, runs the UI with errors tolerated, always calls `cfs endrepair`, then interprets UI exit codes. Removal invokes `removeinc`; replica/named-file repairs are already done by `xaskuser`.

## Dependencies and Integration
Integrates command-line Coda repair (`cfs`) with the Tk UI and C helpers from this directory.

## Risks and Test Signals
Risks include no non-X fallback, hard-coded command names, trap only for selected signals, path whitespace exposure, and comments typo around `xaskuer`. Test signals are begin/endrepair pairing, conflict-type rejection, correct handling of xaskuser exit codes, and token preflight failure when unauthenticated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/egasr/xfrepair -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/Makefile.am -->
# sources/distributed-fs/coda/coda-src/kerndep/Makefile.am

## Purpose
Automake definition for the small kernel-dependency compatibility library.

## APIs, Types, and Functions
Builds `libkerndep.la` from `pioctl.c`, `pioctl.h`, and `coda.h`, with base include path.

## Control Flow, State, and Persistence
No runtime behavior. It packages userland Coda kernel-interface definitions and pioctl implementation for clients/tools.

## Dependencies and Integration
Linked by repair utilities and other code needing `pioctl()` or Coda kernel protocol structures.

## Risks and Test Signals
Risks are ABI drift against kernel/Venus expectations and generated config differences. Test signals are successful library build and pioctl consumers linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/coda.h -->
# sources/distributed-fs/coda/coda-src/kerndep/coda.h

## Purpose
User/kernel ABI header for Coda filesystem communication, shared by userland tools, Venus, and kernel-facing code.

## APIs, Types, and Functions
Defines Coda limits, open/access flags, `venus_dirent`, `CodaFid`, `coda_f2i()`, vnode attribute types, `coda_statfs`, opcode constants, upcall/downcall macros, `CODA_KERNEL_VERSION`, input/output message structs for root/open/store/release/close/ioctl/getattr/setattr/access/lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/vget/statfs/access-intent, unions `inputArgs`, `outputArgs`, `coda_downcalls`, `ViceIoctl`, `PioctlData`, control-file constants, and mount data.

## Control Flow, State, and Persistence
No runtime flow beyond inline `coda_f2i()`, which hashes a four-word Coda FID to an inode number. The structs define persistent ABI layout for messages exchanged with Venus and ioctl/pioctl payloads.

## Dependencies and Integration
Depends on platform type definitions and ioctl macros. It underpins `pioctl.h`, directory conversion to `venus_dirent`, repair tools, and Coda kernel/Venus protocol compatibility.

## Risks and Test Signals
Risks include ABI/layout sensitivity, platform conditional type definitions, fixed max message/data sizes, pointer placeholders in wire structs, and kernel version compatibility. Test signals are kernel/Venus communication success, correct dirent parsing, pioctl payload size compatibility, and cross-platform builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/coda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/pioctl.c -->
# sources/distributed-fs/coda/coda-src/kerndep/pioctl.c

## Purpose
Userland implementation of Coda `pioctl()` using Venus's special pioctl-file protocol under the Coda mount point.

## APIs, Types, and Functions
Exports `pioctl(const char *path, unsigned long com, struct ViceIoctl *vidata, int follow)`. Internal helpers are `getMountPoint()` and `strip_prefix()`. Uses `codaconf_init()`, `CODACONF_STR()`, `_IOC_NR()`, `PIOCTL_PREFIX`, `getrandom()` when available, and C stdio file I/O.

## Control Flow, State, and Persistence
`getMountPoint()` lazily loads `venus.conf` and defaults to `/coda`. `strip_prefix()` turns absolute or relative user paths into paths relative to the Coda mount, handling Cygwin specially. `pioctl()` creates a unique `...PIOCTL.<hex>` file under the mount, writes command id, path length, follow flag, input/output sizes, a NUL separator, the stripped path, and input bytes. Venus processes the file; the function reopens it, parses result code and output size, reads output into the caller buffer, maps nonzero code to `errno`, and returns.

## Dependencies and Integration
Depends on Coda mount semantics, Venus pioctl-file handling, `coda.h`/`pioctl.h`, and config. Repair tools and auth/file utilities use it for `_VICEIOCTL()` calls.

## Risks and Test Signals
Risks include predictable fallback uniqueness from pid, leaked pioctl files if Venus does not clean up, no cleanup on several error paths, returning `EBADF` for diverse failures, path-prefix assumptions, fixed uint16 sizes, and no validation of `vidata` pointers. Test signals are successful `_VIOC_GETFID`/`_VIOC_REPAIR`, relative-path handling inside the mount, response-size rejection, and errno propagation from Venus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/pioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/pioctl.h -->
# sources/distributed-fs/coda/coda-src/kerndep/pioctl.h

## Purpose
Public pioctl interface and ioctl-number helpers for Coda userland tools.

## APIs, Types, and Functions
Declares `pioctl()`, defines `PIOCTL_PREFIX`, `_VICEIOCTL(id)`, `_VALIDVICEIOCTL(com)`, and fallback `_IOC_*` decoding macros for Darwin, Cygwin, NetBSD, and FreeBSD. Includes `coda.h` for `ViceIoctl`.

## Control Flow, State, and Persistence
No runtime flow. The macros encode/decode command numbers and validate the 0-255 Coda pioctl id range.

## Dependencies and Integration
Included by tools that call Venus pioctls, especially repair utilities. Bridges system ioctl macro differences across supported platforms.

## Risks and Test Signals
Risks include platform macro drift, `_VALIDVICEIOCTL` range comparison on encoded command values, and warning that requests must fit Coda max message sizes. Test signals are correct `_VICEIOCTL(_VIOC_*)` values and cross-platform compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/kerndep/pioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/Makefile.am -->
# sources/distributed-fs/coda/coda-src/librepair/Makefile.am

## Purpose
Automake rules for Coda repair libraries.

## APIs, Types, and Functions
Builds `librepio.la` from `repio.cc`/`repio.h` and `libclnrepair.la` from `resolve.cc`, `resolve.h`, `cure.cc`, `cure.h`, `predicate.cc`, `predicate.h`, `repcmds.cc`, `repcmds.h`, `rvol.cc`, and `path.cc`. Include paths cover RPC2, base, kerndep, util, vicedep, al, partition, auth2, vv, and vol.

## Control Flow, State, and Persistence
No runtime flow. It groups repair I/O, conflict resolution, predicate/cure logic, path processing, and volume replica helpers into libraries.

## Dependencies and Integration
Used by repair clients and command tools that need non-interactive repair operations and fix-file processing.

## Risks and Test Signals
Risks include broad include coupling and split libraries whose consumers must link the right one. Test signals are successful build and downstream repair command linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/cure.cc -->
# sources/distributed-fs/coda/coda-src/librepair/cure.cc

## Purpose
Conflict repair-plan generation for inconsistent replicated directories. It decides which per-replica repair operations create, remove, or rename objects.

## APIs, Types, and Functions
Exports `ObjExists()`, `RepairRename()`, `RepairSubsetCreate()`, and `RepairSubsetRemove()`. Uses `resreplica`, `resdir_entry`, `listhdr`, `struct repair`, repair opcodes such as `REPAIR_RENAME`, `REPAIR_CREATED`, `REPAIR_CREATES`, `REPAIR_CREATEF`, `REPAIR_CREATEL`, `REPAIR_REMOVED`, and `REPAIR_REMOVEFSL`, plus `InsertListHdr()`, `InRepairList()`, `IsCreatedEarlier()`, and `GetParent()`.

## Control Flow, State, and Persistence
`RepairRename()` finds parent paths for an object's FID on each replica, warns when renamed on some sites and removed on others, prompts the repairer to choose a preserved path, then inserts rename or removal operations for replicas that differ. `RepairSubsetCreate()` marks replicas missing an object and chooses create opcode based on directory/symlink/file, mount-point flag, hard-link-like existing FIDs, and existing repair list. `RepairSubsetRemove()` inserts remove operations at replicas where the object is present. State is accumulated in per-replica repair lists.

## Dependencies and Integration
Depends on resolution data structures from `resolve.h`, repair file/list helpers from `repio.h`, parser prompting, filesystem `stat/lstat`, and Vice FID conventions. Called by directory resolution code after predicates classify conflicts.

## Risks and Test Signals
Risks include interactive prompts inside library logic, fixed `MAXHOSTS`, path buffer concatenation, incomplete automation for created-parent cases, possible allocation-size off-by-one in path construction, and assumptions about FID/name equivalence across replicas. Test signals are generated repair op lists for subset create/remove/rename cases, warnings for mixed rename/remove, and successful subsequent `dorepair`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/cure.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/cure.h -->
# sources/distributed-fs/coda/coda-src/librepair/cure.h

## Purpose
Header exposing directory conflict repair-plan helpers from `cure.cc`.

## APIs, Types, and Functions
Includes `vcrcommon.h` and declares `ObjExists()`, `RepairRename()`, `RepairSubsetCreate()`, and `RepairSubsetRemove()` over `resreplica`, `resdir_entry`, `listhdr`, `VolumeId`, vnode id, and unique id inputs.

## Control Flow, State, and Persistence
No runtime flow. The declared functions append operations to repair-list state that is later serialized into fix files or applied through Venus repair.

## Dependencies and Integration
Requires repair/resolution type declarations from included or previously included headers. Used by resolution code to invoke cure logic.

## Risks and Test Signals
Risks include missing include guards and depending on external declarations for several types. Test signals are compile-time inclusion from resolver modules and matching signatures with `cure.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/cure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/dir.cc -->
# sources/distributed-fs/coda/coda-src/librepair/dir.cc

## Purpose
Tiny legacy diagnostic program for printing host directory entries as seen by the client-side repair environment.

## APIs, Types, and Functions
K&R-style `main()` calls `opendir()`, `readdir()`, and prints `d_ino`, `d_reclen`, `d_namlen`, and `d_name` from `struct direct`.

## Control Flow, State, and Persistence
It opens the directory named by `argv[1]`, prints each entry, and exits. No persistent state is changed.

## Dependencies and Integration
Depends on old dirent/direct fields and libc directory APIs. It appears to be a standalone test aid rather than part of the repair library build target.

## Risks and Test Signals
Risks include missing argument checks, outdated `struct direct` portability, K&R style, and no `closedir()`. Test signal is successful listing of expanded replica directories during manual debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/dir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/path.cc -->
# sources/distributed-fs/coda/coda-src/librepair/path.cc

## Purpose
Path-processing helpers for the repair tool: detect leftmost conflicts, detect dangling conflict symlinks, and retrieve FID/version-vector metadata through pioctl.

## APIs, Types, and Functions
Exports `repair_isleftmost()`, `repair_getmnt()`, `repair_inconflict()`, and `repair_getfid()`. Internal helpers are `repair_abspath()` and `repair_getvid()`. Uses `pioctl(_VIOC_GETFID)`, `readlink()`, `stat()`, `chdir()`, `getcwd()`, `ViceFid`, and `ViceVersionVector`.

## Control Flow, State, and Persistence
`repair_isleftmost()` simulates pathname traversal component by component, following symlinks up to `CODA_MAXSYMLINK`, and rejects paths where an earlier component is already a conflict. `repair_inconflict()` identifies a conflict by failed `stat()` plus symlink target beginning with `@`, parsing FID and realm. `repair_getfid()` first asks Venus for metadata and falls back to conflict-symlink parsing with undefined version-vector markers. `repair_getmnt()` walks upward to find the last Coda volume mount, but its helper currently asserts. These functions change the current directory temporarily and restore it.

## Dependencies and Integration
Depends on `repcmds.h`, pioctl support, Coda conflict symlink encoding, and filesystem traversal. Used by `BeginRepair()` and volume-replica setup.

## Risks and Test Signals
Risks include process-wide `chdir()` side effects, fixed path buffers, symlink target concatenation overflow, `repair_getvid()` containing `CODA_ASSERT(0)` which makes `repair_getmnt()` unusable, and fragile parsing of `@fid@realm`. Test signals are correct leftmost-conflict rejection, FID retrieval for normal and conflict objects, cwd restoration, and symlink-loop handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/path.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/predicate.cc -->
# sources/distributed-fs/coda/coda-src/librepair/predicate.cc

## Purpose
Conflict-classification predicates for replicated directory resolution. Each predicate decides whether a grouped directory entry set is strongly equal, weakly equal, all-present, renamed, subset-created, subset-removed, or maybe subset-removed.

## APIs, Types, and Functions
Defines predicate functions matching `PtrFuncInt`: `ObjectOK()`, `WeaklyEqual()`, `AllPresent()`, `Renamed()`, `SubsetCreate()`, `SubsetRemove()`, and `MaybeSubsetRemove()`, plus helpers `Equal()`, `nObjectSites()`, and `nlinks()`. Exports `Predicates[]` and `nPredicates`.

## Control Flow, State, and Persistence
Predicates inspect entry counts, version-vector equality, StoreId equality, version-vector site coverage, hard-link count from `lstat()`, directory-vnode status, and parent lookup through `GetParent()`. Some cases prompt the user via `Parser_getbool()` when automation is uncertain, especially hard-link and subset-remove decisions. No persistent state is changed; results steer later cure generation.

## Dependencies and Integration
Depends on resolver structures, Vice version-vector helpers (`InitVV()`, `AddVVs()`, `VV_Cmp()`), parser prompting, filesystem metadata, and inconsistency definitions. Predicate array ordering must match constants in `predicate.h`.

## Risks and Test Signals
Risks include heuristic classification when replica-to-version-vector slots are unknown, interactive prompts in classification, hard-link path construction assumptions, fixed `MAXHOSTS`, and reliance on `GetParent()` availability. Test signals are correct predicate index for known conflict scenarios, no automation for hard-link ambiguous cases unless confirmed, and matching array length/order with header constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/predicate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/predicate.h -->
# sources/distributed-fs/coda/coda-src/librepair/predicate.h

## Purpose
Header defining the predicate function type, exported predicate table, and conflict-classification numeric constants.

## APIs, Types, and Functions
Defines `PtrFuncInt` as a pointer to functions receiving replica counts, `resreplica *`, grouped `resdir_entry **`, entry count, and realm string. Declares `Predicates[]` and `nPredicates`. Defines constants `STRONGLY_EQUAL`, `WEAKLY_EQUAL`, `ALL_PRESENT`, `SUBSET_RENAME`, `SUBSET_CREATE`, `SUBSET_REMOVE`, `MAYBESUBSET_REMOVE`, and `UNKNOWN_CONFLICT`.

## Control Flow, State, and Persistence
No runtime flow. The order of constants is the contract for indexing into `Predicates[]`.

## Dependencies and Integration
Requires resolver type declarations to be available before or through inclusion. Used by resolution code to classify grouped entries.

## Risks and Test Signals
Risks include no include guard, no direct includes for dependent types, and tight coupling between enum-like constants and array order. Test signals are compile-time inclusion and classification tests verifying index-to-meaning mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/predicate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repcmds.cc -->
# sources/distributed-fs/coda/coda-src/librepair/repcmds.cc

## Purpose
Non-interactive repair command library for beginning repair sessions, comparing replicas, applying fix files, ending sessions, clearing inconsistencies, and removing inconsistent objects.

## APIs, Types, and Functions
Implements public functions from `repcmds.h`: `BeginRepair()`, `ClearInc()`, `CompareDirs()`, `DoRepair()`, `EndRepair()`, `RemoveInc()`, `dorep()`, and `makedff()`. Helper functions include `findtype()`, `getremovelists()`, `getVolrepNames()`, `compareFids()`, `compareAcl()`, `compareOwner()`, `compareQuotas()`, `compareStatus()`, `compareVV()`, `isLocal()`, and `printAcl()`. It uses pioctls `_VIOC_ENABLEREPAIR`, `_VIOC_REP_CMD`, `_VIOC_REPAIR`, `_VIOC_DISABLEREPAIR`, `_VIOC_SETVV`, and `_VIOCGETVOLSTAT`.

## Control Flow, State, and Persistence
`BeginRepair()` creates a conflict object, gets FID/VV, enables repair expansion, mounts/records RW replicas, starts Venus repair, classifies local/global/server-server mode, and determines file-vs-directory conflict. `CompareDirs()` gathers replica paths, reads Unix directory reps, runs `dirresolve()`, writes per-replica repair actions and optional ACL/mode/owner actions to a fix file, checks version-vector and quota mismatches, and cleans resolver state. `DoRepair()` converts text fix files to internal binary form for directory conflicts, calls `_VIOC_REPAIR`, and reports per-volume return codes. `EndRepair()` optionally commits local/global sessions, disables repair, and frees conflict state. `ClearInc()` compares replicas, clears inconsistency bits in VVs with `_VIOC_SETVV`, and rejects quota differences. `RemoveInc()` generates remove actions for directory conflicts or chooses a replica file for file conflicts, then repairs/clears as needed.

## Dependencies and Integration
Depends on pioctl/kerndep, Venus repair commands, resolver and repair-file APIs (`getunixdirreps()`, `dirresolve()`, `repair_parsefile()`, `repair_putdfile()`), version-vector helpers, volume status, ACL structures, and path/rvol helpers. This is the main programmatic repair workflow used by higher-level repair commands.

## Risks and Test Signals
Risks include fixed 2 KB buffers, many temp files under `/tmp/REPAIR.XXXXXX`, broad global repair side effects, complex cleanup paths, reliance on textual Venus responses, local-replica heuristics, possible allocation cleanup bug in `getVolrepNames()`, and mixed stdout diagnostics from library code. Test signals are begin/end repair pairing, compare fix-file contents, `_VIOC_REPAIR` per-replica status output, VV inconsistency clearing, quota/ACL/mode/owner mismatch detection, and `NNCONFLICTS` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repcmds.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repcmds.h -->
# sources/distributed-fs/coda/coda-src/librepair/repcmds.h

## Purpose
Public interface and shared data structures for Coda client repair commands.

## APIs, Types, and Functions
Defines constants `MAXVOLNAME`, `MAXHOSTS`, `HOSTNAMLEN`, `DEF_BUF`, and conflict-kind values `LOCAL_GLOBAL`, `SERVER_SERVER`, and `MIXED_CONFLICT`. Defines `struct conflict` with conflict FID/VV, replica list, repair directory, realm, and conflict-type flags; and `struct replica` with RW replica FID/VV, realm/server/component names, and next pointer. Declares repair operations `BeginRepair()`, `ClearInc()`, `CompareDirs()`, `DoRepair()`, `EndRepair()`, `RemoveInc()`, helpers `dorep()`, `makedff()`, rvol helpers, and path helpers. Macros `freeif()` and `strerr()` centralize cleanup and formatted error writing.

## Control Flow, State, and Persistence
No implementation. The structs model repair-session state that persists from `BeginRepair()` until `EndRepair()` frees it; functions declared here mutate Venus repair state and server replica metadata.

## Dependencies and Integration
Includes broad Coda, RPC2, parser, auth, Venus ioctl, copyfile, inconsistency, repio, and resolver headers. It is the main header for repair CLIs or libraries using non-interactive repair.

## Risks and Test Signals
Risks include broad header coupling, fixed host/path sizes, variadic `strerr` macro portability, mutable linked-list ownership rules, and flags stored as `char`. Test signals are compile/link of repair clients and end-to-end repair-session lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/librepair/repcmds.h -->
