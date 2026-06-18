# subset-b-007764 OpenAFS aklog/audit/auth research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/aklog.c -->
# sources/distributed-fs/openafs/src/aklog/aklog.c

## Purpose
`aklog.c` implements the `aklog` command that obtains Kerberos 5 credentials for AFS cells and installs AFS token sets into the cache manager. It supports direct cell login, path-based discovery of AFS mount points, linked cells, optional Zephyr/host reporting, optional PAG creation, weak-DES compatibility knobs, and a keytab/client-principal impersonation path.

## Important APIs, types, and functions
The local `cellinfo_t` carries a cell and realm pair for command-line batching. Global state tracks flags such as `dflag`, `noauth`, `noprdb`, `linked`, `afssetpag`, `force`, `do524`, plus `keytab`, `client`, `zsublist`, `hostlist`, and `authedcells`.

Core functions are `main`, `auth_to_cell`, `auth_to_path`, `rxkad_get_ticket`, `rxkad_get_token`, `rxkad_build_native_token`, `rxkad_get_converted_token`, `get_credv5`, `get_credv5_akimpersonate`, `get_user_realm`, `get_cellconfig`, `get_afs_mountpoint`, `next_path`, `add_hosts`, and `redirect_errors`. The file also provides a compatibility `krb5_encrypt_tkt_part` when libkrb5 lacks it but exposes lower-level encoding/encryption calls.

## Control flow
`main` initializes Kerberos, OpenAFS error tables, linked lists, and command-line state. It parses mode switches into either a cells list or paths list. With no explicit targets it authenticates to the local cell and optionally reads `$HOME/.xlog` for extra cells. In cell mode it calls `auth_to_cell`; in path mode it calls `auth_to_path`, which walks each path component through `next_path`, detects mount points through `pioctl(VIOC_AFS_STAT_MT_PT)`, derives the cell from the mountpoint, and authenticates to each encountered cell.

`auth_to_cell` resolves the target cell with `afsconf_Open`, `afsconf_GetCellInfo`, and `afsconf_GetLocalCell`, records the cell in `authedcells` before network work to avoid repeated failures, builds a `ktc_setTokenData` jar, obtains an rxkad token, optionally resolves the PTS id, writes the ViceId into the token, sets the PAG flag, and finally calls `ktc_SetTokenEx`. `rxkad_get_ticket` tries service principals in a deliberate order: command-line realm, user realm, host-realm from cell DB server, fallback uppercase DNS domain, and `afs@REALM` only when the cell/realm match. `get_credv5` either pulls service creds from the default ccache or synthesizes a ticket from a keytab through `get_credv5_akimpersonate`.

## State and persistence
Persistent effects are mostly outside the process: it reads AFS client config, Kerberos ccaches, optional `krb5-weak.conf`, optional `.xlog`, and stores tokens in the cache manager through `ktc_SetTokenEx`. It may set a PAG via token metadata. Process-local state includes the Kerberos ccache handle `_krb425_ccache`, static principal cache in `get_user_realm`, linked lists of already attempted cells, Zephyr subscriptions, and host addresses.

## Dependencies and integration points
The file bridges Kerberos libraries, OpenAFS auth/token APIs, PTS lookup, Venus pioctls, `cellconfig`, `linked_list`, rxkad ticket/token helpers, and platform compatibility macros for MIT/Heimdal differences. It depends on `afs_realm_of_cell` from `krb_util.c` and the linked-list helpers in `linked_list.c`.

## Risks
There is extensive legacy string and buffer handling with fixed-size arrays; most copies use `strlcpy`/`strlcat`, but some paths still use `strcpy`, `strncpy`, and manual concatenation. `ll_string` allocations are never reclaimed before exit, which is acceptable for a command but important for reuse. `Parse`-like command handling is interleaved with side effects, so option ordering is observable. Keytab impersonation constructs tickets locally and is security-sensitive; lifetime bounds, enctype compatibility, and keytab principal validation are critical. The path walker uses static buffers and is not reentrant. The code intentionally supports weak DES modes for old deployments, which must stay opt-in.

## Test signals
Useful tests cover no-argument local-cell login, explicit `-cell/-k`, path traversal across nested mount points, linked-cell behavior, duplicate-token skip versus `-force`, `-noprdb`, `-noauth`, `-setpag`, missing/ambiguous cell config, DNS/realm fallback, MIT and Heimdal builds, no-524 and 524 builds, keytab impersonation with bounded and unlimited lifetimes, and malformed symlink/path loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/aklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/aklog.h -->
# sources/distributed-fs/openafs/src/aklog/aklog.h

## Purpose
`aklog.h` is the small public/local header for the `aklog` family. It declares `aklog(int, char *[])`, includes Kerberos 5 and the local linked-list header, and supplies a Kerberos 4 `CREDENTIALS` compatibility definition when the system lacks `<kerberosIV/krb.h>`.

## Important APIs, types, and functions
The exported function declaration is `void aklog(int, char *[])`, although this source tree's `aklog.c` provides a `main` entry point. The fallback `struct ktext` and `struct credentials` mirror the K4 fields needed by 524 conversion code: service, instance, realm, session key, lifetime, kvno, ticket, issue date, principal name, and principal instance. `CREDENTIALS` aliases `struct credentials`.

## Control flow
There is no runtime control flow. The header conditionally selects either the platform Kerberos IV definition or the local compatibility layout.

## State and persistence
No state is stored here. The fallback struct definitions describe in-memory ticket conversion data used by `aklog.c`.

## Dependencies and integration points
It depends on `afsconfig.h`, `<krb5.h>`, and `linked_list.h`. It is included by `aklog.c`, `krb_util.c`, and `skipwrap.c`, giving those files the Kerberos compatibility constants such as `REALM_SZ` when native K4 headers are absent.

## Risks
The compatibility layout must match the expectations of the Kerberos 524 APIs closely enough for builds without Kerberos IV headers. The local `u_int32_t` macro fallback is invasive if a platform has unusual typedef behavior. Since fixed sizes such as `ANAME_SZ` and `REALM_SZ` are legacy K4 limits, callers must still avoid assuming modern unbounded Kerberos principal lengths.

## Test signals
Build coverage should include platforms with and without `HAVE_KERBEROSIV_KRB_H`, MIT and Heimdal Kerberos headers, and code paths that compile 524 conversion support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/aklog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/asetkey.c -->
# sources/distributed-fs/openafs/src/aklog/asetkey.c

## Purpose
`asetkey.c` implements the `asetkey` administrative command for adding, deleting, listing, and randomly generating OpenAFS server keys in the server configuration directory. It supports legacy rxkad DES keys, rxkad Kerberos 5 typed keys, and rxgk typed keys.

## Important APIs, types, and functions
The command verbs are dispatched in `main` to `addKey`, `deleteKey`, `listKey`, and `addRandomKey`. Key construction helpers include `stringToType`, `keyFromCommandLine`, `keyFromKeytab`, and `random_key`; display helpers include `printKey`. It uses `afsconf_typedKey_new`, `afsconf_AddTypedKey`, `afsconf_DeleteKey`, `afsconf_DeleteKeyByType`, `afsconf_DeleteKeyBySubType`, `afsconf_GetAllKeys`, and `afsconf_typedKey_values`.

## Control flow
`main` opens `AFSDIR_SERVER_ETC_DIRPATH` with `afsconf_Open`, validates a verb, and delegates. `addKey` supports old forms (`add <kvno> <hexkey>` and `add <kvno> <keytab> <principal>`) plus typed forms (`add <type> <kvno> <subtype> <hexkey>` and keytab equivalents). `keyFromKeytab` initializes Kerberos, parses the principal, reads the requested service key from a keytab, and wraps the bytes in an `afsconf_typedKey`. For rxkad it tries DES-CBC-CRC, MD5, then MD4. `addRandomKey` generates a Kerberos random keyblock, defaulting to AES128 CTS HMAC SHA1 unless a subtype is specified. `listKey` iterates all typed keys and prints key type, kvno, enctype/subtype, and hex material.

## State and persistence
The persistent state is the server KeyFile/KeyFileExt material managed through the `afsconf` key APIs under the server config directory. Commands overwrite existing keys when adding (`afsconf_AddTypedKey(..., 1)`). The process holds transient Kerberos contexts, parsed principals, keyblocks, and typed-key references.

## Dependencies and integration points
The file integrates with OpenAFS `cellconfig` and `keys` APIs, Kerberos keytab and random-key APIs, rx opaque buffers, and com_err reporting. It is an administrative producer for the keys later consumed by `authcon.c` and server-side rxkad/rxgk authentication.

## Risks
`char2hex` returns `-1` for invalid characters, but `keyFromCommandLine` does not reject that before combining nibbles, so malformed hex can become unintended key bytes. The command prints key material in full during `list`, which is expected for a key management tool but sensitive in logs. Several failure paths exit immediately; that is normal for a CLI but leaves no structured error recovery. Keytab extraction must match kvno/enctype precisely, especially for typed rxgk/rxkad_krb5 keys.

## Test signals
Tests should add/list/delete rxkad hex keys, typed rxkad_krb5/rxgk keys, random keys with default and explicit enctypes, keytab imports for found and missing principals, malformed key lengths, invalid key types, and persistence visible to `afsconf_GetAllKeys`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/asetkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/klog.c -->
# sources/distributed-fs/openafs/src/aklog/klog.c

## Purpose
`klog.c` implements a Kerberos 5 based `klog` command that accepts a username/password, obtains initial Kerberos credentials, derives an AFS service credential, and stores an AFS token. It preserves compatibility with older klog options while using Kerberos 5 and rxkad, with optional rxk5 support behind `AFS_RXK5`.

## Important APIs, types, and functions
`main` registers command syntax with the OpenAFS `cmd` package. `CommandProc` performs almost all work. Helpers include `getpipepass`, `silent_errors`, `whoami`, and `k5_to_k4_name`. The code uses `afs_krb5_skip_ticket_wrapper` for 524-style encrypted-part extraction, `tkt_DeriveDesKey`, `ktc_SetToken`, optional `ktc_SetK5Token`, `afsconf_GetCellInfo`, `pr_SNameToId`, and Kerberos ccache/credential APIs.

## Control flow
`main` defines parameters such as `-principal`, `-password`, `-cell`, `-k`, `-pipe`, `-silent`, `-setpag`, `-tmp`, `-noprdb`, `-unwrap`, `-k5`, `-k4`, and `-insecure_des`, then dispatches to `CommandProc`. `CommandProc` wipes command-line arguments, initializes Kerberos, rx, error tables, and cell config, selects a realm from `-k` or host realm lookup, parses the user principal, reads a password from the option, stdin, or Kerberos prompter, gets initial credentials, writes them to either the default ccache or an in-memory ccache, requests an AFS service ticket, and stores a token. The rxkad path either stores the full Kerberos 5 ticket or, with `-unwrap`, stores only the encrypted ticket part.

## State and persistence
Persistent effects include optional writing of a Kerberos ticket cache via `-tmp` and storing AFS tokens through `ktc_SetToken`/`ktc_SetK5Token`, optionally in a new PAG. Sensitive password buffers and command-line password arguments are zeroed. Process-global state holds `k5context`, `tdir`, and saved argv/argc for scrubbing.

## Dependencies and integration points
The command sits between OpenAFS cmd parsing, Kerberos initial-credential APIs, rx initialization, `cellconfig`, PTS lookups, `ktc` token storage, rxkad token formats, and `skipwrap`. It integrates with optional rxk5 support when compiled.

## Risks
Password-in-argv support is inherently risky despite scrubbing. The `always_evil` default makes encrypted-part-only handling active unless build/runtime conditions override through the `evil` calculation, so compatibility assumptions are important. Fixed-size principal buffers can truncate names. The service-ticket fallback from `afs/<cell>` to `afs` is intentional but must be covered for realms where both exist. Error handling exits immediately through `KLOGEXIT`, finalizing rx.

## Test signals
Cover interactive, `-pipe`, and explicit-password flows; `-silent` error suppression; `-tmp` ccache writing and fallback to memory cache; realm override and host-realm discovery; `-noprdb`; `-setpag`; `-unwrap` with valid and malformed tickets; rxk5/rxkad selection in `AFS_RXK5` builds; and invalid cell/principal/password cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/klog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/krb_util.c -->
# sources/distributed-fs/openafs/src/aklog/krb_util.c

## Purpose
`krb_util.c` provides `afs_realm_of_cell`, a small Kerberos realm inference helper used by `aklog` when deciding where to request AFS service tickets.

## Important APIs, types, and functions
The only function is `char *afs_realm_of_cell(krb5_context context, struct afsconf_cell *cellconfig, int fallback)`. It returns a pointer to a static `REALM_SZ + 1` buffer.

## Control flow
If `cellconfig` is null, it returns null. In fallback mode, it takes the domain portion of the first cell DB server hostname, or the cell name if no dot exists, and uppercases it. In normal mode it calls `krb5_get_host_realm` for `cellconfig->hostName[0]`, copies the first returned realm into the static buffer, frees the realm list, and returns the buffer.

## State and persistence
The function has no persistent external effects. It stores the result in a static buffer, so each call overwrites the previous value and the function is not thread-safe or reentrant.

## Dependencies and integration points
It depends on Kerberos realm lookup, `struct afsconf_cell`, K4 realm-size constants from `aklog.h`, and C character classification. `aklog.c` uses it in its ticket-acquisition fallback sequence.

## Risks
The static fixed-size buffer is copied into with `strcpy`, so unusually long host realms from Kerberos could overflow if not bounded by the Kerberos library or configuration. Returning null without freeing `hrealms` when `hrealms[0]` is null is a small leak. Fallback realm derivation is heuristic and can produce wrong realms for non-DNS-style deployments.

## Test signals
Test host-realm success, empty host-realm result, fallback from dotted hostname, fallback from undotted hostname, lowercase-to-uppercase conversion, null cell input, and repeated-call overwrite behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/krb_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/linked_list.c -->
# sources/distributed-fs/openafs/src/aklog/linked_list.c

## Purpose
`linked_list.c` implements a minimal doubly linked list package used by the `aklog` command to track cells, paths, host strings, and Zephyr subscription strings.

## Important APIs, types, and functions
The implementation exports `ll_init`, `ll_add_node`, `ll_delete_node`, and `ll_string`. `ll_add_data` is a macro in the header. `ll_string` supports `ll_s_check` and `ll_s_add` for duplicate-suppressed string lists.

## Control flow
`ll_init` aborts on null and zeroes the list. `ll_add_node` allocates a node and inserts it at the head or tail, maintaining `first`, `last`, and `nelements`; an invalid end selector aborts. `ll_delete_node` linearly scans for the node, relinks neighbors, frees the node, and decrements count. `ll_string` checks for string equality or appends a newly allocated string if absent.

## State and persistence
The list state is fully caller-owned in memory. Nodes are heap allocated; `ll_delete_node` frees only the node, not `node->data`. `ll_string(ll_s_add)` allocates duplicate string storage, so callers need a separate cleanup strategy if used outside short-lived commands.

## Dependencies and integration points
It uses roken/C library memory and string routines and the local `linked_list.h` types. `aklog.c` relies on this to preserve option order and avoid duplicate cells/hosts/subscriptions.

## Risks
`ll_string(ll_s_check)` initializes `status` to `LL_SUCCESS`, which is `0`, and uses it as a boolean false until a match; callers must understand that check returns true/1 on found and 0 on not found, not strictly `LL_SUCCESS`/`LL_FAILURE`. The API stores `char *` rather than `void *`, encouraging casts. No full-list free helper exists.

## Test signals
Cover head/tail insertion into empty and non-empty lists, deletion of first/middle/last/missing nodes, string duplicate suppression, allocation failure behavior, and caller-managed data freeing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/linked_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/linked_list.h -->
# sources/distributed-fs/openafs/src/aklog/linked_list.h

## Purpose
`linked_list.h` declares the simple list data structures and operations used by `aklog`.

## Important APIs, types, and functions
It defines `LL_SUCCESS`, `LL_FAILURE`, `ll_node`, `linked_list`, `ll_end` (`ll_head`, `ll_tail`), and `ll_s_action` (`ll_s_add`, `ll_s_check`). The `ll_add_data(n, d)` macro casts and assigns node data. Prototypes cover `ll_init`, `ll_add_node`, `ll_delete_node`, and `ll_string`, with K&R fallbacks for non-ANSI C.

## Control flow
There is no runtime control flow beyond macro expansion.

## State and persistence
The header defines the in-memory shape: a list keeps first/last pointers and element count; each node keeps prev/next/data.

## Dependencies and integration points
Included by `aklog.h`, `aklog.c`, and `linked_list.c`. The data pointer is typed as `char *`, matching the string-heavy use in `aklog`.

## Risks
The macro does not validate node pointers or ownership and erases data type information. The API does not encode whether data should be freed by the list. Compatibility K&R prototypes obscure type checking on very old compiler paths.

## Test signals
Compile consumers with strict warnings and exercise all list operations through `linked_list.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/linked_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/skipwrap.c -->
# sources/distributed-fs/openafs/src/aklog/skipwrap.c

## Purpose
`skipwrap.c` extracts the encrypted ticket portion from a DER-encoded Kerberos 5 ticket by manually walking the expected ASN.1 wrapper. `klog` uses it for encrypted-part-only rxkad token compatibility.

## Important APIs, types, and functions
The exported function is `afs_krb5_skip_ticket_wrapper(char *tix, size_t tixlen, char **enc, size_t *enclen)`. Internal `skip_get_number` reads ASN.1 short or long-form lengths and advances a pointer/remaining-length pair. Tag constants define SEQUENCE, CONSTRUCTED, APPLICATION, and CONTEXT_SPECIFIC bits.

## Control flow
`afs_krb5_skip_ticket_wrapper` validates the outer application ticket tag, outer length, sequence tag, and context-specific fields 0, 1, and 2, skipping their contents. It then requires context-specific field 3 to consume the remaining data and returns a pointer/length to that encrypted ticket data. Any malformed tag, length mismatch, or truncation returns `-1` or the helper error.

## State and persistence
No persistent state exists. Returned pointers alias the caller-provided ticket buffer; no allocation is performed.

## Dependencies and integration points
It includes `aklog.h`, Kerberos headers, and `skipwrap.h`. The main integration is `klog.c` when constructing `RXKAD_TKT_TYPE_KERBEROS_V5_ENCPART_ONLY` tokens.

## Risks
This is intentionally a narrow parser, not a general ASN.1 decoder. It assumes definite lengths and exact field order. Lengths are read into `int`, so extremely large encodings are not meaningful. Because returned memory aliases input, callers must keep the original credential buffer alive.

## Test signals
Use known-good Kerberos tickets, truncated buffers at every boundary, wrong tags, long-form lengths, mismatched lengths, missing field 3, and caller lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/skipwrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/skipwrap.h -->
# sources/distributed-fs/openafs/src/aklog/skipwrap.h

## Purpose
`skipwrap.h` declares the ticket wrapper extraction helper used by `klog`.

## Important APIs, types, and functions
The single API is `int afs_krb5_skip_ticket_wrapper(char *tix, size_t tixlen, char **enc, size_t *enclen)`, returning zero on success and nonzero on parse failure.

## Control flow
There is no control flow in the header.

## State and persistence
No state is defined. The API contract implies output aliases into the input buffer.

## Dependencies and integration points
The header is included by `skipwrap.c` and `klog.c`.

## Risks
The declaration uses mutable `char *` for DER data even though parsing does not modify it, so const-correctness is weak. Callers must not free or overwrite the ticket before using the returned encrypted-part pointer.

## Test signals
Compile-time coverage is enough for the header; behavioral tests belong to `skipwrap.c` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/skipwrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/Makefile.in -->
# sources/distributed-fs/openafs/src/audit/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS audit support libraries and public `afs/audit.h` header.

## Important APIs, types, and functions
Build products are `liboafs_audit.la`, `libaudit_pic.la`, `libaudit.a`, `${TOP_LIBDIR}/libaudit.a`, and `${TOP_INCDIR}/afs/audit.h`. Object inputs are `audit.lo`, `audit-file.lo`, and `audit-sysvmq.lo`. Shared-library dependencies include rxkad and util libraries.

## Control flow
The `all` target builds shared, PIC, static, installed-library, and installed-header outputs. Object dependency rules tie audit sources to `audit.h` and `audit-api.h`. `install` and `dest` copy library/header files into package or destination trees. `dest` conditionally installs AIX audit sample files for `rs_aix*`. `clean` removes libtool outputs and generated component files.

## State and persistence
The makefile writes build artifacts under the object tree and install artifacts under `${TOP_LIBDIR}`, `${TOP_INCDIR}`, `${DESTDIR}`, or `${DEST}`. It does not modify source configuration.

## Dependencies and integration points
It includes OpenAFS config, LWP, and lwptool make fragments and participates in the larger libtool build. `liboafs_audit.la` is consumed by auth and server components that emit audit events.

## Risks
The comment says auditing was historically AIX-focused, but the makefile now builds file and SysV MQ backends when available. Install coverage for backend-specific runtime assets is mostly AIX sample oriented. Missing `HAVE_SYS_IPC_H` changes symbols compiled into `audit-sysvmq.lo`.

## Test signals
Run configure/build on Unix with and without SysV IPC headers, verify static/shared/PIC libraries, install and dest targets, AIX sample conditional paths, and clean idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-api.h -->
# sources/distributed-fs/openafs/src/audit/audit-api.h

## Purpose
`audit-api.h` defines the private plugin interface used by audit output backends.

## Important APIs, types, and functions
It defines `OSI_AUDIT_MAXMSG` as 2048 and `struct osi_audit_ops`. Required callbacks are `send_msg`, `open_file`, `print_interface_stats`, `create_interface`, and `close_interface`. Optional callbacks are `set_option` and `open_interface`.

## Control flow
No runtime control flow is present. `audit.c` invokes callbacks in a documented sequence: create/open during option processing, optional open after daemon thread setup, send during events, stats on request, and close at shutdown.

## State and persistence
The interface is explicitly context-based: each backend returns a `rock` from `create_interface`, persists backend-specific state there, and releases it through `close_interface`.

## Dependencies and integration points
Implemented by `audit-file.c` and `audit-sysvmq.c`; consumed by `audit.c`. Backends are selected by name from `audit_interfaces`.

## Risks
Callback contracts rely on discipline rather than type-enforced ownership. `send_msg` receives a truncation flag and a length, so backends must not assume NUL-termination unless they add it. Optional `set_option` must be checked before parsing options.

## Test signals
Backend contract tests should verify create/open/send/stats/close ordering, option parsing only when `set_option` exists, max message handling, and cleanup after partial open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-file.c -->
# sources/distributed-fs/openafs/src/audit/audit-file.c

## Purpose
`audit-file.c` implements the file audit backend. It writes formatted audit records to a file or FIFO.

## Important APIs, types, and functions
`struct file_context` holds `FILE *auditout`. Backend callbacks are `send_msg`, `open_file`, `print_interface_stats`, `create_interface`, and `close_interface`, collected in `audit_file_ops`.

## Control flow
`create_interface` allocates context. `open_file` detects FIFOs with `lstat`; FIFOs are opened write-only/nonblocking, while regular paths are rotated to `<name>.old` with `rk_rename` and reopened with truncate/create. It then wraps the fd with `fdopen("a")`. `send_msg` writes the message bytes, appends newline, and flushes. `close_interface` closes the stream and frees context.

## State and persistence
Persistent effects are audit log file rotation and appending audit records. FIFO mode does not rotate. The context owns the open stream until shutdown.

## Dependencies and integration points
Used by `audit.c` through `audit_file_ops` and is the default audit interface. It depends on roken portability wrappers and standard file APIs.

## Risks
If `fdopen` fails, the opened fd is not closed in that branch. Regular-file open mode uses `0666`, relying on umask. Rotation unconditionally renames an existing file and can overwrite the `.old` target depending on platform rename semantics. FIFO nonblocking open can fail when no reader exists, disabling that audit sink.

## Test signals
Cover regular-file rotation, FIFO open with and without reader, unwritable paths, `fdopen` failure injection, message newline/flush behavior, and close idempotence with null context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-sysvmq.c -->
# sources/distributed-fs/openafs/src/audit/audit-sysvmq.c

## Purpose
`audit-sysvmq.c` implements a SysV message queue audit backend when `HAVE_SYS_IPC_H` is available.

## Important APIs, types, and functions
`struct my_msgbuf` matches `msgsnd` layout with `mtype` and `mtext[OSI_AUDIT_MAXMSG]`. `struct mqaudit_stats` tracks total, truncated, and lost messages. `struct sysvmq_context` stores the queue id, reusable message buffer, and stats. Callback implementations are exported as `audit_sysvmq_ops`.

## Control flow
`open_file` creates a filesystem token for `ftok`, opens or creates the message queue, and attempts to raise `msg_qbytes` to 2 MiB. `send_msg` truncates overlarge records, copies a NUL-terminated payload into the queue buffer, and calls `msgsnd(..., IPC_NOWAIT)`, incrementing lost or truncated stats. `print_interface_stats` reports counters. `close_interface` frees only the local context, not the system message queue.

## State and persistence
The backend persists messages in a kernel SysV message queue keyed by `ftok(fileName, 1)`. The ftok file may be created with owner read/write mode. Queue lifetime is not removed on backend close.

## Dependencies and integration points
It is conditionally compiled and registered in `audit.c` when SysV IPC headers exist. Consumers can select it via `-audit-interface sysvmq` or `sysvmq:<filespec>` auditlog syntax.

## Risks
`ftok` key collisions are possible. Queue size changes may fail silently if permissions are insufficient. Nonblocking sends can drop messages under load; stats expose this but callers do not retry. The persistent queue may outlive the daemon and require external cleanup.

## Test signals
Test queue creation, existing queue reuse, permission failures, message truncation, full-queue loss accounting, stat output, and builds without `HAVE_SYS_IPC_H`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit-sysvmq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit.c -->
# sources/distributed-fs/openafs/src/audit/audit.c

## Purpose
`audit.c` is the central audit formatter, dispatcher, and command-option parser for OpenAFS server audit events. It turns typed variadic audit arguments into text records and sends them to all configured audit interfaces; on AIX it can also use native audit records.

## Important APIs, types, and functions
Public functions from `audit.h` include `osi_audit`, `osi_auditU`, `osi_audit_cmd_Options`, `osi_audit_file`, `osi_audit_init`, `osi_audit_interface`, `osi_audit_set_user_check`, `audit_PrintStats`, `osi_audit_open`, and `osi_audit_close`. Important internal pieces are `struct audit_log`, `struct audit_msg`, `audit_interfaces`, `audit_logs`, `multi_send_msg`, `append_msg`, `printbuf`, `osi_audit_internal`, `osi_audit_check`, `parse_file_options`, and `parse_option_string`.

## Control flow
Callers configure auditing through `osi_audit_interface` and `osi_audit_file`, often via `osi_audit_cmd_Options`. `osi_audit_file` parses `[interface:]filespec[:options]`, creates a backend context, applies optional comma-separated options, opens the sink, and appends it to `audit_logs`. `osi_audit` and `osi_auditU` lazily call `osi_audit_check`, skip work when no audit mode/output is active, then format event data. `osi_auditU` extracts authenticated rxkad user and peer host information from an `rx_call`, emitting secondary audit events for unauthenticated, missing-name, unknown-security, or null-call cases. `printbuf` walks the variadic AUD_* stream and appends textual fields for strings, ids, hosts, FIDs, arrays, and butc tape structures before sending under the audit mutex.

## State and persistence
Process-global state includes the active backend queue, default interface index, audit enabled state from `AFSDIR_SERVER_AUDIT_FILEPATH`, a boolean indicating any open sink, and an optional local-user callback. Persistent output is backend-specific: files, FIFOs, SysV queues, or AIX audit logs. `osi_audit_check` reads the server `Audit` file and enables all-event auditing only when `AFS_AUDIT_AllEvents` appears.

## Dependencies and integration points
This file integrates rx/rxkad identity extraction, OpenAFS queue primitives, pthread mutex initialization, butc and AFS wire structures, audit backends via `audit-api.h`, and server command-line processing via `cmd_item`. Event names and AUD_* type tags are defined in `audit.h`.

## Risks
The API is variadic and depends on each AUD_* tag matching the following argument type exactly. Recursion is possible because `osi_auditU` emits audit events while auditing another event; `printbuf` suppresses timestamp/thread only when explicitly told but most paths use `rec == 0`. `parse_file_options` mutates its duplicated input and has custom handling for empty fields that should be preserved carefully. `auditout_open` is not reset in `osi_audit_close`, so post-close behavior depends on an empty backend list. Formatting truncation is tracked, but not all backends visibly mark truncated text.

## Test signals
Cover audit-on/off file detection, no-output fast path, all AUD_* format tags including null values, maximum-message truncation, multiple backends fanout, command option parsing for one/two/three-field forms, invalid interfaces/options, `osi_auditU` for null/rxnull/rxkad/unknown security classes, local realm callback behavior, close/open lifecycle, and pthread builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit.h -->
# sources/distributed-fs/openafs/src/audit/audit.h

## Purpose
`audit.h` is the public audit event and argument-type header. It gives OpenAFS servers stable event-name strings and declares the audit API.

## Important APIs, types, and functions
The header defines AUD argument tags such as `AUD_END`, `AUD_STR`, `AUD_INT`, `AUD_LST`, `AUD_HOST`, `AUD_LONG`, `AUD_DATE`, `AUD_FID`, `AUD_FIDS`, `AUD_NAME`, `AUD_ID`, `AUD_ACL`, MR-AFS residency tags, and butc tape tags. It hardcodes selected authorization error constants to avoid build cycles. It defines many event-name macros for volserver, ptserver, budb, kauth, fileserver, bosserver, vlserver, MR-AFS, remio, and tape-controller operations. Function prototypes expose audit emission, configuration, lifecycle, user-locality checks, and stats.

## Control flow
No runtime control flow exists in the header, but the AUD tags control how `audit.c` consumes variadic arguments.

## State and persistence
The header defines no state. Its event names become persistent audit log vocabulary, so changing them affects downstream log processing.

## Dependencies and integration points
It includes `<afs/cmd.h>` for command option integration and is included by audit emitters across server code as well as `audit.c`. The prototypes connect server startup option parsing, daemon open/close lifecycle, and runtime audit events.

## Risks
The large macro list is a compatibility contract; typos or renames can break external audit tooling. Hardcoded error constants can drift from `.et` definitions if upstream values ever change. The variadic API has no compile-time type checking for AUD tag/argument pairs.

## Test signals
Compile representative audit emitters, verify event names in generated logs, exercise each AUD tag through `audit.c`, and compare hardcoded error constants against generated error headers during maintenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/audit/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/Makefile.in -->
# sources/distributed-fs/openafs/src/auth/Makefile.in

## Purpose
This makefile builds the OpenAFS authentication libraries, generated headers, XDR token code, and the `setkey` utility.

## Important APIs, types, and functions
Primary object groups are `BASE_objs`, `LT_objs`, and `KRB_objs`. Outputs include `libauth.a`, `libauth.krb.a`, `liboafs_auth.la`, `liboafs_auth_krb.la`, `libauth_pic.la`, `libpam_auth.la`, installed headers, generated `auth.h`, `cellconfig.h`, `token.h`, and generated XDR C files. `setkey` links against rxkad, afsrfc3961, rx, sys, lwp, and util libraries.

## Control flow
The `all` target builds shared/static/PIC/PAM auth variants and runs `depinstall`. Error-table inputs generate C and headers through `COMPILE_ET_C/H`. `token.xg` is processed by `RXGEN` for normal and kernel XDR variants. Special rules compile `ktc.krb.lo` with `AFS_KERBEROS_ENV` and `authcon.lo` with nodeprecated declarations. `install` and `dest` copy libraries and headers; `test` delegates into `test`; `clean` removes generated artifacts.

## State and persistence
Generated files are written into the build tree and installed include/lib directories. The makefile defines how public headers are generated from `.p.h` templates plus error tables.

## Dependencies and integration points
The auth library depends on opr, comerr, rx, rxkad, audit, util, sys, and optionally rxgk. It builds core modules including `cellconfig`, `keys`, `userok`, `authcon`, `ktc`, `token`, `realms`, and `netrestrict`. Other OpenAFS components consume these libraries for cell config, token, key, and security object handling.

## Risks
Generated header ordering matters: sources depend on `cellconfig.h` and `auth.h` produced from templates. Optional rxgk substitution changes link dependencies. Multiple object variants from the same `ktc.c` must stay compiler-flag isolated. Build/install drift could expose stale generated headers.

## Test signals
Run full build, generated target, install/dest, clean/rebuild, `make test`, rxgk-enabled and disabled configurations, Kerberos-enabled `libauth.krb.a`, and out-of-tree builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/auth.p.h -->
# sources/distributed-fs/openafs/src/auth/auth.p.h

## Purpose
`auth.p.h` is the template portion for generated `auth.h`. It defines token-related public types and ktc token APIs.

## Important APIs, types, and functions
It defines `AUTH_SUPERUSER` as `"afs"` and `struct ktc_token`, containing token start/end times, session key, kvno, ticket length, and ticket bytes. It declares `ktc_SetToken`, `ktc_GetToken`, extended token-set APIs (`ktc_SetTokenEx`, `ktc_GetTokenEx`, `ktc_ListTokensEx`), legacy list/forget APIs, `ktc_curpag`, and optionally `ktc_newpag`. It defines token flags `AFS_SETTOK_SETPAG`, `AFS_SETTOK_LOGON`, and Windows `PIOCTL_LOGON`.

## Control flow
No runtime control flow exists. The file is combined with generated error-table output to produce a public header.

## State and persistence
The types describe tokens stored in or retrieved from the cache manager/PAG. The header itself has no state.

## Dependencies and integration points
It includes `rx/rxkad.h` for ticket constants and encryption key types. `aklog.c`, `klog.c`, auth code, and cache-manager token code rely on these declarations.

## Risks
`struct ktc_token` contains legacy fixed-size buffers and an explicitly unaligned `short kvno`; ABI/layout compatibility is important. Ticket length must be validated by implementations before copying into `ticket`. Generated-header flow means direct edits to generated `auth.h` would be lost.

## Test signals
ABI/layout checks, token set/get round trips, extended token-set APIs, PAG behavior, Windows logon flags, and generated header regeneration from `ktc_errors.et`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/auth.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/authcon.c -->
# sources/distributed-fs/openafs/src/auth/authcon.c

## Purpose
`authcon.c` builds RX security classes for OpenAFS client and server connections from local keys, current tokens, or rxgk key material. It centralizes fallback-to-null behavior and server security object construction.

## Important APIs, types, and functions
Public functions include `afsconf_ServerAuth`, `afsconf_ClientAuth`, `afsconf_ClientAuthSecure`, `afsconf_ClientAuthRXGKClear`, `afsconf_ClientAuthRXGKAuth`, `afsconf_ClientAuthRXGKCrypt`, `afsconf_ClientAuthToken`, `afsconf_SetSecurityFlags`, `afsconf_BuildServerSecurityObjects`, `afsconf_BuildServerSecurityObjects_int`, `afsconf_PickClientSecObj`, and `afsconf_PickClientLocalSecObj`. Internal helpers include `QuickAuth`, `_afsconf_GetRxkadKrb5Key`, `GenericAuth`, `_ClientAuthRXGK`, `LogDesWarning`, `LogNoKeysWarning`, and `PickClientSecObj`.

## Control flow
Server authentication uses `rxkad_NewKrb5ServerSecurityObject` with callbacks for rxkad DES and rxkad_krb5 typed keys. Client local-auth flow goes through `GenericAuth`, which prefers rxkad_krb5 typed keys by enctype list, falls back to latest DES rxkad key, generates a DES session key, makes a ticket for `afs` or an explicit rx identity, and returns an rxkad client security object. Token-auth flow reads current tokens with `ktc_GetTokenEx`, extracts rxkad material, and creates a client security object at clear or crypt level. rxgk local-auth flow prints a token/key from the latest rxgk cell key when compiled. `PickClientSecObj` selects among noauth, localauth, rxgk, current-token, and fallback-null modes.

## State and persistence
The file does not persist state itself. It reads keys from `struct afsconf_dir`, reads tokens from the cache manager, writes security flags into `dir->securityFlags`, and returns heap-allocated RX security objects owned by callers. It logs warnings when server key state is absent or only DES keys are present.

## Dependencies and integration points
It integrates `cellconfig`, `keys`, `ktc`, rx/rxkad, optional rxgk, hcrypto DES/random APIs, global pthread locking, and rx identity handling. `asetkey` produces the typed keys this file consumes; servers use `afsconf_BuildServerSecurityObjects_int` during RX service setup.

## Risks
Several failure paths intentionally fall back to rxnull through `QuickAuth`; callers must inspect `scIndex` or avoid `AFSCONF_SECOPTS_FALLBACK_NULL` when anonymous fallback is not acceptable. DES remains involved for rxkad session keys even when long-term keys are stronger. The code notes a leak when localauth requested but fallback null is rejected. Enctype preference is hardcoded. Local-auth identity support is limited to superuser and KRB4-style identities.

## Test signals
Cover server class arrays with no keys, DES keys, rxkad_krb5 keys, always-encrypt flags, and rxgk builds; client local-auth clear/crypt; current-token auth with and without tokens; fallback-null rejection; local identities; rxgk clear/auth/crypt; and key callback buffer-size failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/authcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/authcon.h -->
# sources/distributed-fs/openafs/src/auth/authcon.h

## Purpose
`authcon.h` declares internal auth-connection helpers that are not part of the external OpenAFS API.

## Important APIs, types, and functions
It defines `struct afsconf_bsso_info`, carrying an `afsconf_dir *` and optional logger callback for server-security-object construction. It declares `afsconf_BuildServerSecurityObjects_int`.

## Control flow
No runtime control flow is present.

## State and persistence
No state is stored. The struct passes context and logging behavior into `authcon.c`.

## Dependencies and integration points
It includes `<afs/cellconfig.h>` and is used by in-tree callers that want the enhanced server-security-object builder with logging. The older public wrapper still exists in `authcon.c`.

## Risks
The logger uses printf-style varargs but the type cannot enforce format correctness. The header is explicitly internal, so external consumers should not rely on ABI stability.

## Test signals
Compile in-tree callers and verify logged warnings from `afsconf_BuildServerSecurityObjects_int` with and without logger callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/authcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/cellconfig.c -->
# sources/distributed-fs/openafs/src/auth/cellconfig.c

## Purpose
`cellconfig.c` implements OpenAFS cell configuration loading, lookup, DNS fallback, alias handling, local-cell discovery, update detection, and writing of single-cell server config. It is the core implementation behind the `afsconf_*` APIs declared by `cellconfig.p.h`.

## Important APIs, types, and functions
Public APIs implemented here include `afsconf_FindService`, `afsconf_FindIANAName`, `afsconf_Open`, `afsconf_UpToDate`, `_afsconf_Check`, `_afsconf_Touch`, `_afsconf_IsClientConfigDirectory`, `afsconf_CellApply`, `afsconf_CellAliasApply`, `afsconf_GetExtendedCellInfo`, `afsconf_GetAfsdbInfo`, `afsconf_GetCellInfo`, `afsconf_GetCellName`, `_afsconf_GetLocalCell`, `afsconf_GetLocalCell`, `afsconf_Close`, `afsconf_SetCellInfo`, and `afsconf_SetExtendedCellInfo`. Important internals are `LoadConfig`, `UnloadConfig`, `afsconf_Reopen`, `GetCellUnix`, Windows `GetCellNT`/registry enumeration, `ParseHostLine`, `ParseCellLine`, `VerifyEntries`, `GetAlternatePath`, and DNS `afsconf_LookupServer`.

## Control flow
`afsconf_Open` allocates a directory object, sets `name`, and calls `LoadConfig`; if loading fails, it tries an alternate config path from `AFSCONF`, `$HOME/.AFSCONF`, or `/.AFSCONF`. `LoadConfig` initializes key storage, reads `ThisCell`, computes the `CellServDB` path, parses cell entries and host lines into a linked list, merges Windows registry cells when relevant, loads `CellAlias`, then delegates to key and realm loaders. `_GetCellInfo` lowercases requested cells, honors aliases, supports unambiguous abbreviations, applies service ports, expands client-config hostnames through DNS, or falls back to AFSDB/SRV DNS lookups. The DNS path tries SRV and AFSDB variants with and without trailing dots and returns servers, ports, ranks, TTL-derived timeout, and real cell names. Setters write `ThisCell`, verify host address/name pairs, rewrite `CellServDB`, and invalidate cached mtime.

## State and persistence
`struct afsconf_dir` persists loaded config in memory: directory path, local cell, CellServDB path, cell entries, alias entries, key list, mtime/check timestamps, security flags, realms, and exclusions. Persistent files read include `ThisCell`, `CellServDB`, `CellAlias`, key files, and realm files; writes affect `ThisCell` and `CellServDB`. `_afsconf_Touch` updates CellServDB mtime so other users of the cache notice key/config changes. `afsconf_SawCell` is global process state that makes explicit cell arguments override `AFSCELL` for later local-cell calls.

## Dependencies and integration points
The file integrates platform path differences, Windows registry/DNS helpers, resolver APIs, rx address utilities, pthread global locking, key management from `keys.c`, realm management from `realms.c`, and directory path macros. It is consumed by `aklog`, `klog`, auth connection setup, server tools, and administrative commands.

## Risks
Parsing uses fixed-size buffers and `sscanf` without width limits in `ParseHostLine` and `ParseCellLine`; comments note unknown destination lengths. DNS parsing is manual and IPv4-only. `_GetCellInfo` mutates the caller's `acellName` by lowercasing it. Cache invalidation is mtime-based and throttled to one stat per second, which can miss rapid changes on coarse filesystems. Global locking protects shared config operations but resolver calls and callbacks need scrutiny. Some Windows code has a likely no-op truncation line (`name[MAXCELLCHARS-1];`) that relies on prior strncpy behavior.

## Test signals
Cover load success/failure, alternate path discovery, empty/missing `ThisCell`, CellServDB parsing including clones/linked cells/too many hosts/syntax errors, aliases, abbreviation ambiguity, service-port mapping, DNS SRV and AFSDB fallback, client hostname expansion, AFSCELL override and `afsconf_SawCell`, mtime reopen behavior, writes with host lookup, and platform-specific Windows/Solaris wrappers where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/cellconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/cellconfig.p.h -->
# sources/distributed-fs/openafs/src/auth/cellconfig.p.h

## Purpose
`cellconfig.p.h` is the template for generated `cellconfig.h`. It declares OpenAFS cell configuration structures, security-option flags, key APIs, auth connection APIs, superuser checks, realm checks, net restriction parsers, and well-known service constants.

## Important APIs, types, and functions
Key data types include `struct afsconf_cell`, `struct afsconf_cellalias`, `struct afsconf_entry`, `struct afsconf_aliasentry`, `afsconf_secflags`, `struct afsconf_dir`, `struct afsconf_typedKeyList`, and `afsconf_keyType` (`afsconf_rxkad`, `afsconf_rxgk`, `afsconf_rxkad_krb5`). Function declarations cover service/cell lookup, open/close/reload, key get/add/delete/enumeration, typed-key reference management, client/server RX security object selection, user/superuser management, realm matching, and netrestrict parsing.

## Control flow
No executable control flow exists, but the declarations define the control surface implemented across `cellconfig.c`, `keys.c`, `authcon.c`, `userok.c`, `realms.c`, and `netrestrict.c`.

## State and persistence
`struct afsconf_dir` is the central in-memory persistent configuration handle. Its fields mirror source files and runtime settings: config path, cell name, CellServDB path, cells, key list, timestamps, aliases, security flags, local realms, and exclusions. Key APIs persist to server key files through implementation modules.

## Dependencies and integration points
The header includes socket types, rx opaque buffers, opr queues, and rxgk key types. It is used broadly by OpenAFS clients, servers, tools, and authentication code. Generated error definitions from `acfg_errors.et` are combined with this template.

## Risks
The structures expose internal linked-list fields and fixed-size arrays, so ABI compatibility and direct field access constrain future changes. Security flag combinations can be invalid or meaningful only for certain mechanisms, requiring implementation-side validation. Generated-header workflow means this template, not generated `cellconfig.h`, is the maintainable source.

## Test signals
ABI checks for public structs, generated header regeneration, typed-key lifecycle tests, security flag matrix tests through `authcon.c`, userok and realm integration tests, and service constant consistency with `cellconfig.c` service table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/cellconfig.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/internal.h -->
# sources/distributed-fs/openafs/src/auth/internal.h

## Purpose
`internal.h` declares private auth/cellconfig helper functions shared between implementation files in `src/auth`.

## Important APIs, types, and functions
It declares `_afsconf_Check`, `_afsconf_Touch`, `_afsconf_IntGetKeys`, `_afsconf_IsClientConfigDirectory`, `_afsconf_LoadKeys`, `_afsconf_InitKeys`, `_afsconf_FreeAllKeys`, `_afsconf_GetLocalCell`, `_afsconf_LoadRealms`, and `_afsconf_FreeRealms`.

## Control flow
No runtime control flow is present. The declarations enable `cellconfig.c`, `keys.c`, and `realms.c` to call each other's internal routines.

## State and persistence
The declared functions operate on `struct afsconf_dir`, especially config reload state, CellServDB mtimes, key queues, and realm lists.

## Dependencies and integration points
It is included by `cellconfig.c` and related auth implementation files. It intentionally avoids being a public installed API.

## Risks
Because these helpers are private, external code should not depend on them. Callers must respect locking expectations, especially `_afsconf_Check` and `_afsconf_GetLocalCell`, which are used under the global afsconf lock in `cellconfig.c`.

## Test signals
Compile all auth objects together, exercise reload/touch/key/realm lifecycle through public APIs, and use static analysis for lock-order assumptions around internal calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/auth/internal.h -->
