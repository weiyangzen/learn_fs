# Research Group: subset-b-007765

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/keys.c -->
# sources/distributed-fs/openafs/src/auth/keys.c

## Purpose
Implements OpenAFS configuration-directory key management. It maintains an in-memory typed key store and persists keys to the legacy `KeyFile` for rxkad DES keys and `KeyFileExt` for newer typed keys such as rxgk.

## Important APIs, Types, and Functions
Defines private `afsconf_typedKey`, `keyTypeList`, `kvnoList`, and `subTypeList` structures. Public/key exported routines include `_afsconf_InitKeys`, `_afsconf_LoadKeys`, `_afsconf_FreeAllKeys`, `afsconf_GetKeys`, `afsconf_GetLatestKey`, `afsconf_GetKey`, rxgk lookup helpers, `afsconf_AddKey`, `afsconf_DeleteKey`, `afsconf_GetKeysByType`, `afsconf_GetAllKeys`, `afsconf_GetKeyByTypes`, `afsconf_GetLatestKeysByType`, `afsconf_GetLatestKeyByTypes`, `afsconf_AddTypedKey`, `afsconf_DeleteKeyByType`, `afsconf_DeleteKeyBySubType`, and typed-key reference/value helpers. `addMemoryKey`, `findByType`, `findByKvno`, and `findBySubType` are the sorted-list core.

## Control Flow
Loading clears `dir->keyList`, parses legacy rxkad keys from `AFSDIR_KEY_FILE`, then parses all non-rxkad typed records from `AFSDIR_EXT_KEY_FILE`. Mutations validate constraints, update the in-memory list, save both disk files, and touch the config directory. Lookups call `_afsconf_Check`, find the relevant type/kvno/subtype, and return reference-counted key objects or lists.

## State and Persistence
The authoritative runtime state is `dir->keyList`, a three-level sorted queue by type, kvno, and subtype. On disk, rxkad remains in the old fixed `nkeys + kvno + 8-byte key` format; extended keys are variable-length records with network-byte-order metadata and key material. Typed keys use atomic refcounts and `rx_opaque` ownership.

## Dependencies and Integration Points
Integrates with `cellconfig` configuration directories, global auth locking, OPR queues, RX atomic/opaque helpers, rxgk key conversion when enabled, and the old `struct afsconf_keys` compatibility API consumed by legacy tools.

## Risks and Test Signals
Read errors return `EIO` and clear loaded keys, but writes truncate files directly before completing, so partial write failures can leave damaged key files. Legacy rxkad compatibility assumes 8-byte key material and single subtype. `afsconf_DeleteKeyBySubType` has early `return AFSCONF_NOTFOUND` paths while holding `LOCK_GLOBAL_MUTEX`, a lock-risk worth auditing. Tests should cover malformed KeyFileExt records, duplicate overwrite behavior, rxkad max-8 enforcement, bcrypt kvno 999 latest-key skipping, and lock release on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/keys.h -->
# sources/distributed-fs/openafs/src/auth/keys.h

## Purpose
Declares the legacy server key file structures and limits for OpenAFS rxkad keys.

## Important APIs, Types, and Functions
Defines `AFSCONF_MAXKEYS` as 8, `struct afsconf_key` with a key version number and 8-byte key, `struct afsconf_keys` as a counted fixed array, and `AFSCONF_KEYINUSE` as a local duplicate-key error code.

## Control Flow
There is no executable control flow. The header is consumed by key management code and compatibility callers that retrieve or manage old-style rxkad keys.

## State and Persistence
The structs mirror the legacy `/usr/afs/etc/ServerKeys`/`KeyFile` model: a count followed by kvno/key pairs in network byte order on disk, represented in host memory by the structures here.

## Dependencies and Integration Points
Included by auth key code, `setkey`, and bozo build dependencies. It bridges legacy fixed-size rxkad APIs with the newer typed-key implementation in `keys.c`.

## Risks and Test Signals
The fixed 8-key and 8-byte-key model is intentionally narrow. Code using this header must not assume it can represent rxgk or multiple subtypes. Tests should verify callers handle `AFSCONF_FULL`, `AFSCONF_KEYINUSE`, and conversion from typed-key APIs without overrunning the fixed array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc.c -->
# sources/distributed-fs/openafs/src/auth/ktc.c

## Purpose
Implements Unix-like OpenAFS token cache APIs. It bridges application-facing `ktc_*` calls to kernel/cache-manager pioctls, a small local token cache for non-`afs` services, optional Kerberos ticket-file compatibility, and new XDR token-set pioctls.

## Important APIs, Types, and Functions
Primary APIs are `ktc_SetToken`, `ktc_SetTokenEx`, `ktc_GetToken`, `ktc_GetTokenEx`, `ktc_ListTokens`, `ktc_ListTokensEx`, `ktc_ForgetToken`, `ktc_ForgetAllTokens`, `ktc_curpag`, `ktc_newpag`, `ktc_tkt_string`, and `ktc_set_tkt_string`. Static `SetToken`, `GetToken`, and `ForgetAll` encode/decode old pioctl buffers. Under `AFS_KERBEROS_ENV`, `afs_tf_*` functions implement ticket-file I/O.

## Control Flow
Set-token operations first optionally write Kerberos ticket-file credentials, then encode a `VIOCSETTOK` buffer for old pioctl or an XDR `VIOC_SETTOK2` buffer for the new API. If new pioctls return `EINVAL`, code extracts rxkad data and falls back to old pioctls. Get/list paths similarly prefer new pioctls where available, then iterate old token slots or ticket-file/local-token slots.

## State and Persistence
Runtime state includes `local_tokens[MAXLOCALTOKENS]`, cached local cell `lcell`, the global `krb_ticket_string`, and ticket-file read buffering. Persistent state can be kernel/cache-manager tokens, optional Kerberos ticket files such as `/tmp/tkt<uid>`, and environment variables adjusted by `ktc_newpag`.

## Dependencies and Integration Points
Uses `pioctl`/`call_syscall`, `ViceIoctl`, `venus` ioctl constants, `token.c` XDR helpers, `rxkad` token structures, PAG/keyring behavior on Linux, `afsconf_Open` for local cell discovery, and global auth mutexes.

## Risks and Test Signals
PIOCTL buffer parsing is size-sensitive and partly trusts kernel output. Ticket-file code has legacy locking, uid, and truncation semantics. The local non-AFS cache holds only four entries. Tests should exercise new-pioctl fallback, large ticket rejection, PAG propagation, ticket-file duplicate replacement, token listing index transitions, and error mapping for `ESRCH`, `EINVAL`, `EIO`, and `EDOM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc.h -->
# sources/distributed-fs/openafs/src/auth/ktc.h

## Purpose
Private auth header for ticket cache and token helper entry points shared across Unix/Windows `ktc` implementations and token conversion code.

## Important APIs, Types, and Functions
Declares ticket-file name helpers (`ktc_tkt_string`, `ktc_tkt_string_uid`, `ktc_set_tkt_string`), `ktc_OldPioctl`, token jar functions (`token_buildTokenJar`, `token_addToken`, `token_replaceToken`, `token_SetsEquivalent`, `token_setPag`, free helpers), and rxkad import/extract helpers.

## Control Flow
The header itself has no control flow; it describes the call surface used when `ktc_SetTokenEx` and `ktc_GetTokenEx` need to convert between unified XDR tokens and old rxkad `struct ktc_token`.

## State and Persistence
State is owned by implementations: ticket string storage in `ktc.c`, token set allocations in `token.c`, and pioctl/kernel cache state in platform `ktc` files.

## Dependencies and Integration Points
Forward-declares `ktc_setTokenData`, `ktc_tokenUnion`, `ktc_token`, and `ktc_principal`, allowing implementation files to share prototypes without exposing full generated XDR details here.

## Risks and Test Signals
Ownership is important: token-set and token-union outputs returned by these helpers must be freed with the matching free functions. Tests should verify callers do not mix `free`, `xdr_free`, and token helper ownership incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc_nt.c -->
# sources/distributed-fs/openafs/src/auth/ktc_nt.c

## Purpose
Windows implementation of OpenAFS token cache APIs. It uses SMB pioctls plus a DCE/RPC side channel so session keys are not sent in cleartext through SMB on NT-class systems.

## Important APIs, Types, and Functions
Exports Windows versions of `ktc_SetToken`, `ktc_GetToken`, `ktc_GetTokenEx`, `ktc_SetTokenEx`, `ktc_ListTokens`, `ktc_ListTokensEx`, `ktc_ForgetToken`, `ktc_ForgetAllTokens`, and `ktc_OldPioctl`. Local helpers include `send_key`, `receive_key`, `getservername`, MIDL allocators, and local-token cache functions.

## Control Flow
For `afs` service tokens, `ktc_SetToken` builds an old token buffer with a zeroed session key, sends the real session key through authenticated RPC keyed by a generated UUID, then calls `VIOCSETTOK` while holding a named mutex. `ktc_GetToken` performs `VIOCNEWGETTOK`, then retrieves the session key through RPC using the UUID. Non-`afs` service tokens use the local in-process cache.

## State and Persistence
Maintains `local_tokens[MAXLOCALTOKENS]`, global RPC error text, registry-derived gateway configuration, and named mutexes `Global\AFS_KTC_Mutex`/`AFS_KTC_Mutex`. Persistent token state lives in the Windows AFS cache manager, not this file.

## Dependencies and Integration Points
Depends on Windows registry APIs, RPC runtime, generated `afsrpc` stubs, SMB pioctl headers, `ViceIoctl`, token XDR helpers, and OpenAFS global mutexes. Environment variables `AFS_RPC_ENCRYPT` and `AFS_RPC_PROTSEQ` alter RPC security/transport.

## Risks and Test Signals
`ktc_SetTokenEx` and new `VIOC_GETTOK2` paths are explicitly unimplemented and fall back or fail. `ktc_GetTokenEx` calls `strcpy(server.cell, cellName)` even though the API permits NULL cell names, a null-pointer risk. Tests should cover RPC unavailable paths, mutex acquisition failure, buffer bound checks, integrated logon `smbname`, local token zeroization on forget, and fallback behavior for Ex APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/ktc_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/netrestrict.c -->
# sources/distributed-fs/openafs/src/auth/netrestrict.c

## Purpose
Parses OpenAFS `NetInfo` and `NetRestrict` files to determine which IPv4 interfaces should be advertised or used by clients and servers.

## Important APIs, Types, and Functions
Key functions are `afsconf_ParseNetInfoFile`, `afsconf_ParseNetRestrictFile`, and `afsconf_ParseNetFiles`. Static helpers include `extract_Addr`, `ParseNetInfoFile_int`, `parseNetRestrictFile_int`, and `filterAddrs`.

## Control Flow
`NetInfo` parsing starts with kernel interface data from `rx_getAllAddrMaskMtu`, then filters/augments it with file entries, including optional fake addresses. `NetRestrict` starts with all kernel addresses plus fake NetInfo entries, then removes addresses matching restricted CIDR-like masks. `afsconf_ParseNetFiles` combines both by choosing successful results or intersecting both successful sets.

## State and Persistence
No durable state is stored in memory; persistent inputs are the NetInfo/NetRestrict text files. Outputs are caller-provided address, mask, and MTU arrays in network byte order plus a reason string.

## Dependencies and Integration Points
Integrates with RX interface discovery, `rx_IsLoopbackAddr`, OpenAFS dirpath names, and `cellconfig` APIs. Test code can override `rx_getAllAddrMaskMtu` to simulate interfaces.

## Risks and Test Signals
The parser is IPv4-only and uses fixed `MAXIPADDRS` arrays. `extract_Addr` does not reject octets above 255 before packing. `ParseNetInfoFile_int` checks `count > max`, which allows `count == max` writes and should be reviewed. Tests should cover blank/comment lines, subnet masks, fake addresses, duplicate matching, loopback removal, missing files, and combined NetInfo/NetRestrict outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/netrestrict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/realms.c -->
# sources/distributed-fs/openafs/src/auth/realms.c

## Purpose
Manages configured local Kerberos realms and principal exclusions used to decide whether an authenticated identity belongs to the local AFS cell.

## Important APIs, Types, and Functions
Defines `afsconf_realm_entry` and `afsconf_realms`. Public/internal functions include `_afsconf_LoadRealms`, `_afsconf_FreeRealms`, `afsconf_SetLocalRealm`, and `afsconf_IsLocalRealmMatch`. Helpers parse strings, build/destroy `tsearch` trees, read `krb.conf`, read exclusion files, and format k4-style principal names.

## Control Flow
Load creates realm and exclusion containers, either copies override realms from the process-global `lrealms` list or reads `AFSDIR_KCONF_FILE`, then reads `AFSDIR_KRB_EXCL_FILE`. Matching first treats empty cell as local, compares against the local cell, then searches local realms and finally checks the exclusion tree using a formatted principal.

## State and Persistence
Per-config-dir state is stored in `dir->local_realms` and `dir->exclusions`, with file modification times used to avoid unnecessary reloads. `lrealms` is a process-wide initialization override. Persistent inputs are `krb.conf` and the Kerberos exclusion file.

## Dependencies and Integration Points
Uses OPR queues, libc `tsearch`/`tfind`/`tdestroy`, global auth locking, `_afsconf_GetLocalCell`, and constants from `cellconfig`/`internal` headers. `userok.c` consumes the local-realm decision when authorizing rxkad callers.

## Risks and Test Signals
`add_entry` does not check `strdup` failure after allocating the entry. The cleanup path in `_afsconf_LoadRealms` calls `destroy_tree(dir->exclusions)` instead of the local `exclusions` pointer, which is suspicious. Tests should cover missing optional files, mtime reuse, override realms, case-insensitive realm matching, case-sensitive exclusion matching, and excluded foreign principal formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/realms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/setkey.c -->
# sources/distributed-fs/openafs/src/auth/setkey.c

## Purpose
Command-line utility for listing, adding, and deleting legacy rxkad server keys in the server configuration directory.

## Important APIs, Types, and Functions
`main` parses `add`, `delete`, and `list`. `char2hex` converts input hex digits to nibbles; `hex2char` converts output nibbles for listing. It calls `afsconf_Open`, `afsconf_AddKey`, `afsconf_DeleteKey`, and `afsconf_GetKeys`.

## Control Flow
After opening `AFSDIR_SERVER_ETC_DIRPATH`, `add` validates that the key argument is exactly 16 hex characters, packs it into 8 bytes, and writes with overwrite enabled. `delete` converts kvno with `atoi` and deletes it. `list` fetches legacy keys and prints printable key bytes and hex.

## State and Persistence
The tool mutates the server key files through the `afsconf` key APIs. It does not maintain its own state.

## Dependencies and Integration Points
Depends on auth cell configuration, `keys.h`, `rxkad`, and component version metadata. It is an operator/admin utility and is superseded for non-rxkad typed keys by newer key management paths.

## Risks and Test Signals
Invalid hex characters produce `-1` nibbles but are not rejected, so malformed input can silently generate unintended bytes. `atoi` accepts partial/non-numeric kvnos. Listing prints raw key bytes as a C string, which may contain control characters. Tests should cover invalid hex, kvno parsing, add/list/delete round trips, and error reporting from config open or key API failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/setkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/Makefile.in -->
# sources/distributed-fs/openafs/src/auth/test/Makefile.in

## Purpose
Builds auth subsystem test utilities for cell configuration, token cache behavior, and NetInfo/NetRestrict parsing.

## Important APIs, Types, and Functions
Targets are `testcellconf`, `ktctest`, and `testnetrestrict`. It links against libtool auth, sys, rx, util, opr, and cmd libraries plus roken.

## Control Flow
`tests all` builds all three binaries. Each target links one `.lo` object with shared `LT_deps` and `LT_libs`. `clean` removes libtool outputs, objects, binaries, and core files. `install` and `dest` are intentionally empty.

## State and Persistence
No runtime state. Build outputs are local test binaries and libtool artifacts.

## Dependencies and Integration Points
Includes top-level config, pthread, and libtool make fragments. The tests exercise APIs implemented by the surrounding `src/auth` code and are typically run from the source/build tree.

## Risks and Test Signals
These are utility-style tests rather than an automated assertion suite; several require local AFS configuration or tokens. Build validation should ensure all three targets compile under configured pthread/libtool settings and clean removes generated outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/ktctest.c -->
# sources/distributed-fs/openafs/src/auth/test/ktctest.c

## Purpose
Manual/integration test for `ktc_*Token` routines. It verifies that existing tokens can be listed, fetched, forgotten, restored, and fetched again without content changes.

## Important APIs, Types, and Functions
Uses `ktc_ListTokens`, `ktc_GetToken`, `ktc_SetToken`, and `ktc_ForgetAllTokens`. Helpers `SamePrincipal` and `SameToken` compare identities and token fields.

## Control Flow
The test snapshots up to `MAXCELLS` existing tokens, exits benignly if none exist, clears all tokens, verifies old tokens are gone, reinstalls the snapshot, lists/fetches tokens again, and checks that each original server/client/token tuple appears in the restored set.

## State and Persistence
Temporarily destroys and recreates the caller's token cache. It stores snapshots only in process memory.

## Dependencies and Integration Points
On Windows it initializes winsock because NT pioctls require it. It uses public auth/token APIs and depends on a working AFS client/cache manager and preexisting user tokens.

## Risks and Test Signals
The test is destructive to the caller's token cache if it fails between forget and reinstall. It only keeps the first 20 tokens. Useful signals are successful round-trip token equality, proper `KTC_NOENT` after forget, and no unexpected pioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/ktctest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/testcellconf.c -->
# sources/distributed-fs/openafs/src/auth/test/testcellconf.c

## Purpose
Interactive test utility for cell configuration APIs: local cell discovery, cell database enumeration, service lookup, extended clone information, and reload behavior.

## Important APIs, Types, and Functions
Uses `afsconf_Open`, `afsconf_GetLocalCell`, `afsconf_CellApply`, `afsconf_GetCellInfo`, `afsconf_GetExtendedCellInfo`, `_afsconf_Touch`, and `afsconf_Close`. `PrintOneCell`, `PrintClones`, and `TestCellConfig` structure output.

## Control Flow
Command options select config directory, cell list, and reload test. Without explicit cells it prints all cells plus special service lookups. With cells it prints standard and extended info per cell. `-reload` touches the config and re-queries after a delay.

## State and Persistence
Reads configuration files from a selected directory or `AFSDIR_SERVER_ETC_DIRPATH`. `-reload` mutates configuration metadata through `_afsconf_Touch` to force reload.

## Dependencies and Integration Points
Uses the OpenAFS `cmd` parser, cellconfig library, socket initialization on Windows, and service names such as `afsprot`.

## Risks and Test Signals
This is output-driven and does not assert expected values. Some branches assume service lookups exist and then print results. Test signals are absence of crashes, correct local cell reporting, sane clone flags, and reload causing fresh cell info to be read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/testcellconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/testnetrestrict.c -->
# sources/distributed-fs/openafs/src/auth/test/testnetrestrict.c

## Purpose
Standalone test harness for NetInfo and NetRestrict parsing, using a file-backed fake interface list.

## Important APIs, Types, and Functions
Provides its own `rx_getAllAddrMaskMtu` implementation, then calls `afsconf_ParseNetInfoFile`, `afsconf_ParseNetRestrictFile`, and `afsconf_ParseNetFiles`.

## Control Flow
`main` expects three files: interface list, NetInfo, and NetRestrict. It parses each path, prints return values/reasons, and dumps final address/mask/MTU arrays in host-readable hex/decimal form.

## State and Persistence
All state is local process memory. Persistent inputs are the three text files. It does not write output except stdout/stderr.

## Dependencies and Integration Points
Links with auth/cellconfig code and uses `arpa/inet.h` conversions. The fake `rx_getAllAddrMaskMtu` lets the auth parser run without real kernel interface discovery.

## Risks and Test Signals
The interface-list parser uses simple integer scanning and does not validate octet ranges. It is a diagnostic tool, not a pass/fail suite. Useful signals are parser return codes, reason strings, and expected final address sets for crafted NetInfo/NetRestrict cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/test/testnetrestrict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/token.c -->
# sources/distributed-fs/openafs/src/auth/token.c

## Purpose
Implements helpers for OpenAFS unified XDR token containers used by newer token pioctls and fallback conversion to/from old rxkad `ktc_token` structures.

## Important APIs, Types, and Functions
Public helpers include `token_findByType`, `token_importRxkadViceId`, `token_setRxkadViceId`, `token_extractRxkad`, `token_buildTokenJar`, `token_addToken`, `token_replaceToken`, `token_SetsEquivalent`, `token_setPag`, `token_freeToken`, `token_freeTokenContents`, `token_FreeSet`, and `token_FreeSetContents`. Static helpers decode, encode, compare, and append opaque token entries.

## Control Flow
Token unions are XDR-encoded into opaque byte arrays before being inserted into a `ktc_setTokenData` jar. Lookups peek at the encoded enum to locate a token type, decode the selected entry, and verify it. Rxkad import/export maps kvno, session key, times, ticket bytes, flags, cell, and ViceId-compatible lifetime parity.

## State and Persistence
All state is heap-owned token set data. There is no disk persistence. Sensitive key/ticket buffers are zeroed before XDR/free paths release them.

## Dependencies and Integration Points
Uses generated XDR routines for `ktc_tokenUnion` and `ktc_setTokenData`, `rxkad` token structures, `xdr_alloc`, and `ktc.h` prototypes. `ktc.c` and `ktc_nt.c` use it for Ex APIs and pioctl fallback.

## Risks and Test Signals
`token_buildTokenJar` does not handle NULL `cellname` safely with `strdup`. `token_FreeSet` frees contents and nulls the pointer but does not free the set allocation, which appears leak-prone. Equivalence compares decoded token semantics for known types and raw bytes otherwise. Tests should cover malformed opaque data, multiple same-type entries, replacement, ViceId parity, oversize tickets, sensitive zeroization, and ownership/free behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/userok.c -->
# sources/distributed-fs/openafs/src/auth/userok.c

## Purpose
Implements server authorization checks for OpenAFS configuration directories: UserList management, noauth mode, superuser identity matching, and restricted query checks.

## Important APIs, Types, and Functions
Exports `afsconf_CheckAuth`, `afsconf_GetNoAuthFlag`, `afsconf_SetNoAuthFlag`, `afsconf_AddIdentity`, `afsconf_DeleteIdentity`, `afsconf_GetNthIdentity`, `afsconf_IsSuperIdentity`, `afsconf_SuperIdentity`, `afsconf_SuperUser`, and legacy user wrappers. Static helpers include `ParseLine`, `CompFindUser`, `kerberosSuperUser`, `rxkadSuperUser`, and optional `rxgkSuperUser`.

## Control Flow
Noauth checks look for `AFSDIR_SERVER_NOAUTH_FILEPATH`. UserList add/delete/list operations parse legacy names or extended base64-encoded identities. Superuser checks inspect the RX security class, reject unauthenticated and bcrypt, map rxkad principal data through local-realm logic, and compare against UserList; rxgk checks use RX identity directly.

## State and Persistence
Persistent state is the UserList file and the NoAuth sentinel file. Temporary rewrites use `UserList.NXX` and rename. Identity objects own display/exported-name allocations and must be freed.

## Dependencies and Integration Points
Integrates with RX security classes, rxkad/rxgk server-info APIs, realm matching from `realms.c`, base64 helpers, Bufio, audit logging, file utility rename behavior, and `cellconfig` directory paths.

## Risks and Test Signals
`afsconf_AddIdentity` allocates `tbuffer` without checking NULL. `ParseLine` mutates input and assumes display names are whitespace-delimited. NoAuth file creation uses mode `0666` subject to umask. Tests should cover legacy and extended UserList entries, duplicate prevention, delete preserving unmatched lines and file modes, local vs foreign realm matching, NoAuth identity output, and all RX security-class branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/userok.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/Makefile.in -->
# sources/distributed-fs/openafs/src/bozo/Makefile.in

## Purpose
Builds the OpenAFS bosserver, bos client utilities, generated BOS RPC files, error tables, headers, and `libbos.a`.

## Important APIs, Types, and Functions
Defines generated targets from `bosint.xg` via `RXGEN`, error/header generation from `boserr.et` via `COMPILE_ET_*`, core object list `OBJS`, library dependency ordering `LIBS`, and install/dest/test/clean targets.

## Control Flow
`all` builds `bosserver`, generated headers, `bos`, `libbos.a`, and `bos_util`. Generated RPC C/header files feed object dependencies. Install/dest copy binaries, headers, and libraries, but skip installing server binaries when pthreaded BOS is enabled.

## State and Persistence
Build outputs include generated `.c`/`.h`, objects, binaries, static library, and component version files. Install targets write into configured DESTDIR/DEST trees.

## Dependencies and Integration Points
Includes OpenAFS config and LWP make fragments. Links many subsystem libraries: rx, lwp, cmd, kauth, volser, vldb, auth, rxkad, ubik, audit, util, opr, sys, procmgmt, RFC3961, and hcrypto.

## Risks and Test Signals
Library ordering is significant, including repeated rx/lwp entries. Generated-file dependencies must remain accurate or parallel builds can race. Test signal is successful generation/build/install across LWP and pthread BOS configurations plus `make test` delegation to the test subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode.c -->
# sources/distributed-fs/openafs/src/bozo/bnode.c

## Purpose
Implements the generic BOS bnode process supervisor. It registers bnode types, creates/deletes instances, starts/stops child processes, tracks exits/timeouts/retry state, saves cores, and runs notifier programs.

## Important APIs, Types, and Functions
Public functions include `bnode_Init`, `bnode_Register`, `bnode_Create`, `bnode_Delete`, `bnode_FindInstance`, `bnode_SetStat`, `bnode_SetFileGoal`, `bnode_WaitStatus`, `bnode_WaitAll`, `bnode_SetTimeout`, `bnode_InitBnode`, `bnode_NewProc`, `bnode_StopProc`, `bnode_ParseLine`, and core/status accessors. Static globals are `allBnodes`, `allProcs`, `allTypes`, `bproc_cv`/`bproc_pid`, and `bnode_stats`.

## Control Flow
Initialization starts a detached pthread or LWP manager and registers signal handlers. The manager sleeps until the next timeout or SIGCHLD, calls bnode timeout methods, reaps children with `waitpid`, records exit/signal state, runs notifiers, applies exponential retry delay on rapid failures, invokes `BOP_PROCEXIT`, and wakes waiters.

## State and Persistence
In-memory state lives in global queues and fields in `struct bnode`/`struct bnode_proc`. File-persistent state is written through `WriteBozoFile` when file goals or bnode definitions change. Core dumps are renamed into configured core/log paths. Notifier data is streamed to an external program.

## Dependencies and Integration Points
Uses bnode operation vectors from concrete bnode types, `bnode_internal.h` locking, LWP or pthread/softsig infrastructure, process management `spawnprocve_sig`, audit logging, BOS prototype functions, and AFSDIR path constants.

## Risks and Test Signals
`bnode_ParseLine` leaks already-created tokens if a later token exceeds 256 bytes. `bnode_Register` ignores `anparms` and stores type name pointers without copying. `bnode_NewProc` stores `comLine` and `coreName` pointers without ownership copying. Tests should cover rapid crash backoff, notifier invocation, timeout rescheduling, delete with refcounts, pid-file/core behavior through concrete ops, and signal/shutdown handling in both pthread and LWP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode.p.h -->
# sources/distributed-fs/openafs/src/bozo/bnode.p.h

## Purpose
Small public-template header for generated BOS bnode header content and platform-specific bosserver exit conventions.

## Important APIs, Types, and Functions
Defines `NONOTIFIER` sentinel string, Windows restart exit base `BOSEXIT_RESTART`, `BOSEXIT_DORESTART(code)` macro, and `FSSDTIME` fileserver shutdown wait limit.

## Control Flow
No executable flow. Macros are consumed by bnode creation/control code and Windows service management integration.

## State and Persistence
No state. Values influence runtime configuration semantics: notifier omission and shutdown/restart timing.

## Dependencies and Integration Points
Used by generated `bnode.h` and by BOS code that interprets notifier configuration and service restart exit codes.

## Risks and Test Signals
`NONOTIFIER` is a string protocol value, so config writers/readers must preserve exact spelling. Windows restart code matching masks low bits. Tests should verify notifier-disabled configs round-trip and Windows restart exits are classified as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode_internal.h -->
# sources/distributed-fs/openafs/src/bozo/bnode_internal.h

## Purpose
Internal BOS bnode subsystem definitions: global locking, operation dispatch macros, bnode/process/type structures, flags, statuses, and internal function prototypes.

## Important APIs, Types, and Functions
Defines `BNODE_LOCK`, `BNODE_UNLOCK`, `BNODE_ASSERT_LOCK`, `BOP_*` dispatch macros, `struct bnode_ops`, `struct bnode_type`, `struct bnode_token`, `struct bnode`, `struct bnode_proc`, `struct ezbnode`, and `struct bozo_bosEntryStats`. Declares core bnode callbacks used by concrete bnode implementations.

## Control Flow
The header encodes the dispatch model: generic code calls `BOP_*` macros into type-specific operation vectors. It also establishes that most interactions must occur under `bnode_glock`.

## State and Persistence
Documents and defines the in-memory state protected by `bnode_glock`: all bnodes, processes, types, restart scheduling data, and stats. `fileGoal` is the state intended for bosserver config persistence; `goal` is runtime desired state.

## Dependencies and Integration Points
Depends on OPR queues, locks, condition variables, and public bnode/error headers generated by the build. Included by generic and concrete bnode operation implementations.

## Risks and Test Signals
The single global lock simplifies correctness but makes blocking operations under lock risky. Operation callbacks must respect lock expectations to avoid deadlock. Tests should assert lock use in debug builds, status transitions (`BSTAT_*`), process flags, and delete/refcount interactions across concrete bnode types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/bozo/bnode_internal.h -->
