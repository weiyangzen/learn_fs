# Group Research: group_1247_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_common_nfsport_h_so_d7f04a6337f0

Scope checked against `Docs/research_subset_a.md`: every listed file is under `sources/os/bsd/netbsd-src`, which is included in subset A. All 15 listed source files were read completely, totaling 6,703 lines.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsport.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsport.h

This header is the NetBSD porting and compatibility layer for the imported FreeBSD "newnfs" code. It centralizes kernel includes, type aliases, operation/procedure numbering, statistics ABI, memory allocation tags, locking macros, socket-address helpers, vnode helpers, and mount-state flag accessors so the common NFS implementation can mostly use FreeBSD-oriented names while compiling in NetBSD.

Key contents:
- Defines NetBSD-specific NFS type aliases such as `NFSSOCKADDR_T`, `NFSPROC_T`, `NFSDEV_T`, `NFSACL_T`, and VOP argument aliases used by common client/server code.
- Provides mbuf allocation wrappers `NFSMGET`, `NFSMGETHDR`, `NFSMCLGET`, and `NFSMCLGETHDR`, with retry/catnap behavior on allocation failure.
- Defines NFSv4 and NFSv4.1 operation numbers, callback operation numbers, fake operation numbers for statistics, and synthetic NFSv4 procedure numbers used by the implementation.
- Defines `struct nfsstatsv1`, the newer 64-bit stats ABI with per-RPC, server operation, callback, cache, state-object, byte, operation-count, and duration counters. It also preserves `struct ext_nfsstats` for older 32-bit statistics consumers.
- Pulls together common NFS headers when `_KERNEL` is set, including `nfskpiport.h`, `nfsdport.h`, `rpcv2.h`, `nfsproto.h`, client/server state headers, XDR helpers, and mount/node headers.
- Defines NetBSD-facing attribute wrapper `struct nfsvattr`, mapping `na_*` names onto `struct vattr` fields while adding NFSv4 supported-attribute and filesystem identity fields.
- Defines server stable-storage restart structures (`nfsrv_stablefirst`, `nfst_rec`, `nfsrv_stable`) and flags used by NFSv4 reclaim/grace handling.
- Maps common NFS locks to NetBSD mutex calls: state, request, socket, name-id, client-state, nfsd, vnode node, mount, request, data-server, and session locks.
- Declares NetBSD malloc types and maps generic NFS allocation names such as `M_NFSDSTATE`, `M_NFSCLOPEN`, `M_NFSLAYOUT`, and `M_NFSSOCKREQ`.
- Defines NetBSD mount state bits and macros such as `NFSHASWRITEVERF`, `NFSHASPNFS`, `NFSHASNFSV4N`, `NFSSTA_LOCKTIMEO`, `NFSSTA_SESSPERSIST`, and `NFSSTA_PNFS`.
- Provides vnode/cache helpers, directory block sizing, `vn_rdwr` wrapper macro, file-size limits, device number conversion, attribute-cache invalidation, vnode lock wrappers, and NFS request structure definition.

Important behavior:
- This file is not protocol-marshalling code itself; it is the glue that makes common NFS client/server source portable across BSD kernels.
- The stats arrays are sized by protocol constants from the same header. Changes to NFSv4 operation counts, fake ops, or callback operation counts affect the ABI and every stats consumer.
- Locking macros define the expected lock order and concrete mutex types used throughout the NFS common, client, server, pNFS, and NLM paths.
- Mount state bits include pNFS and session flags in high bits of `nm_state`; collisions with NetBSD mount or NFS flags would be serious.
- The file keeps compatibility with imported FreeBSD comments and structures while adding NetBSD-specific replacements such as `time_uptime`, `vfs_statfs(m)`, and `NFS_DIRBLKSIZ`.

Research notes:
- This is the first file to inspect when resolving compile portability, lock primitive, allocator, stat ABI, or NetBSD-vs-FreeBSD semantic mismatches in the new NFS stack.
- Risk areas are macro side effects, duplicated operation/procedure constants also present in `nfsproto.h`, statistics ABI sizing, and lock macros that hide concrete mutex requirements.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsproto.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsproto.h

This header defines the main NFS protocol vocabulary for the new NetBSD NFS stack. It covers NFSv2, NFSv3, NFSv4.0, NFSv4.1, and preparatory NFSv4.2 constants: port/program/version numbers, NFS status codes, wire sizes, procedure numbers, NFSv4 operation constants, access/open/share/ACL flags, attribute bitmaps, pNFS layout flags, type conversion macros, and protocol data structures.

Key contents:
- Defines core constants: `NFS_PORT`, `NFS_PROG`, `NFS_CALLBCKPROG`, protocol versions, maximum path/name sizes, server maximum I/O (`NFS_SRVMAXIO`), packet sizes, and NFSv4 minor/callback versions.
- Lists NFS error/status values from traditional errno-compatible values through NFSv3/v4 extended values, NFSv4.1 session/pNFS errors, fake internal NFS errors, and RPC/auth error marker bits.
- Defines protocol wire sizes for unsigned values, hyper values, NFSv2/v3/v4 file handles, attributes, wcc data, fsinfo, pathconf, stateids, GSS headers, session IDs, and device IDs.
- Defines generic NFS procedure numbers, actual NFSv2 procedure numbers, and NFSv4 COMPOUND/callback procedure numbers.
- Provides NFSv4 open, lock, delegation, share-deny, create, access, fsinfo, ExchangeID, CreateSession, Sequence, LayoutReturn, layout type, I/O mode, device-info, and file-layout utility flags.
- Provides NFSv4 ACE type, supported-type, inherit, and access mask constants plus mappings from mode-like read/write/execute concepts to ACE masks.
- Defines vnode/NFS type conversion macros and file type enum `nfstype`.
- Defines dense wire-facing structs for NFSv2/v3/v4 times, 64-bit protocol quads, NFSv3 special device numbers, v2/v3 file attributes, v2/v3 settable attributes, statfs, fsinfo, pathconf, and NFSv4 stateids.
- Defines NFSv4 attribute bit numbers and 32-bit bitmap masks across three bitmap words, including supported, settable, getattr, write-getattr, wcc, callback-getattr, statfs, pathconf, readdirplus, and referral attribute sets.

Important behavior:
- Many status values below 10000 intentionally match `sys/errno.h`; the file comments warn that if errno values change, explicit mapping would be required.
- Wire structs avoid native 64-bit integer fields where alignment could differ from XDR layout. The code uses arrays of 32-bit words and conversion helpers instead.
- The NFSv4 bitmap constants are positional: names such as `NFSATTRBM_MODE` repeat bit values in different bitmap words, so callers must combine them with the correct word context.
- `NFSATTRBIT_WRITEGETATTR*` deliberately excludes owner and owner-group relative to normal getattr sets, matching client write-path avoidance of name-mapping upcalls.
- pNFS-related constants (`NFSLAYOUT_NFSV4_1_FILES`, `NFSFLAYUTIL_DENSE`, `NFSFLAYUTIL_COMMIT_THRU_MDS`) are consumed by NFSv4.1 layout/device paths.

Research notes:
- This is the authoritative protocol constant header for new NFS. Any operation decoder, XDR marshaller, stats table, or NFSv4 attribute parser should be checked against it.
- High-risk changes include attribute bitmap edits, status-code mappings, packed struct assumptions, and procedure/operation numbering shared with stats and generated RPC logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvcache.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvcache.h

This header defines the server recent-request cache used to detect duplicate NFS RPC requests and either drop, replay, or execute them. It provides cache sizing constants, the cache record layout, result flags, return codes, and bucket structure for fine-grained TCP cache locking.

Key contents:
- Cache sizing constants: `NFSRVCACHE_MAX_SIZE`, `NFSRVCACHE_MIN_SIZE`, and hash size `NFSRVCACHE_HASHSIZE`.
- `struct nfsrvcache`, with hash-chain links, ACK hash-chain links, UDP LRU link, RPC XID, completion timestamp, reply mbuf or reply status, UDP host address or TCP connection metadata, procedure number, and flags.
- Macros mapping union fields to readable names, including `rc_reply`, `rc_status`, `rc_haddr`, `rc_sockref`, `rc_tcpseq`, `rc_refcnt`, `rc_reqlen`, `rc_cksum`, `rc_cachetime`, and `rc_acked`.
- TCP ACK state constants `RC_NO_SEQ`, `RC_NO_ACK`, `RC_ACK`, and `RC_NACK`.
- Cache lookup/action return constants `RC_DROPIT`, `RC_REPLY`, and `RC_DOIT`.
- Entry flags for lock/wait state, reply representation, UDP/IP version, in-progress status, NFS protocol version, refcounting, and same-TCP-connection matching.
- `LIST_HEAD(nfsrvhashhead, nfsrvcache)` and `struct nfsrchash_bucket` with per-bucket mutex and list.

Important behavior:
- Cache entries can store either a full reply mbuf chain or a compact reply status. Callers must honor `RC_REPMBUF` versus `RC_REPSTATUS`.
- The structure handles UDP duplicate suppression and TCP request/ACK tracking in one record, using different union fields depending on transport.
- `RC_INPROG`, `RC_LOCKED`, and `RC_WANTED` support synchronization around duplicate requests while the first instance is still being processed.

Research notes:
- This file is the map for reading `nfs_nfsdcache.c`; the implementation must maintain flags and union interpretation consistently.
- Security and correctness review should focus on XID/address/connection matching, reply mbuf lifetime, refcount handling, and duplicate non-idempotent operation handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvstate.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvstate.h

This header defines the NFSv4 server-side state model: clients, sessions, open owners, opens, lock owners, byte-range locks, delegations, local lock rollback records, per-file state containers, user/group name cache entries, and stable-storage restart records.

Key contents:
- List-head definitions for client hashes, state lists, lock lists, lockfile hashes, session lists, session hashes, and user/group name hashes.
- Hash macros for clients, stateids, user IDs/names, group IDs/names, and sessions.
- `struct nfsclient`, representing an NFSv4 client ID with hash/list linkage, stateid hash table, open/delegation/session lists, expiry and delegation times, client/confirm IDs, callback program/id, state index counters, callback refcount, credential identity, name/principal lengths, callback socket request, flags, verifier, and variable client ID bytes.
- `struct nfsdsession`, representing an NFSv4.1 session with refcount, hash/list links, slot table, associated client, creation flags, fore/back channel limits, session ID, and callback session state.
- `struct nfsstate`, a deliberately overloaded state object used for open owners, open files, lock owners, and delegated files. It carries stateid, sequence, uid, flags, owner data, list/hash/file links, owner/open/delegation-specific union state, back-pointers, and optional operation-cache reference.
- `struct nfslock`, representing byte-range locks linked both by owner and file.
- `struct nfslockconflict`, the returned conflict descriptor with clientid, range, flags, owner length, and owner bytes.
- `struct nfsrollback`, used to track local locks that may need rollback.
- `struct nfslockfile`, the per-file container for opens, delegations, locks, local locks, rollback entries, file handle, local-lock serializer, and usecount.
- `struct nfsusrgrp`, a cached user/group name-to-id entry with hash links, expiry, id, credential, and variable-length name.
- `struct nfsf_rec`, the stable restart file header containing lease duration and number of boot times.
- Kernel prototypes for `nfsrv_cleanclient()` and `nfsrv_freedeleglist()`.

Important behavior:
- The comments specify strict locking rules for `struct nfsdsession`: list modification needs global state lock then session-hash lock; traversal needs one of those locks; refcount manipulation needs global state lock; callback-session fields require the callback session mutex.
- `struct nfsstate` multiplexes several state roles, so its union fields are valid only in specific contexts. Misinterpreting `ls_un` or list membership can corrupt state recovery.
- File locking state is indexed both by owner and by file, enabling conflict detection, cleanup by client, cleanup by file handle, and stateid lookup.
- Stable-storage records in this header tie into NFSv4 grace/reclaim behavior and crash recovery.

Research notes:
- This file is essential for understanding `nfs_nfsdstate.c`, delegation recall, lock conflict handling, reclaim, and NFSv4.1 session cleanup.
- Review risk centers on lock ordering, overloaded state object invariants, stateid hashing, reference counts, and variable-length allocation boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsrvstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfssvc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfssvc.h

This header defines flag bits for the `nfssvc()` system call interface used to configure and run NFS server, client callback, stable-storage, identity-mapping, GSS, statistics, and diagnostic operations.

Key contents:
- Legacy service flags such as `NFSSVC_OLDNFSD`, `NFSSVC_ADDSOCK`, and `NFSSVC_NFSD`.
- NFSv4/newnfs service flags for public file handles, stable restart/backup, nfsd thread/socket setup, ID-name mapping, GSS daemon port management, nfsuserd port management, v4 root export, admin revoke, client/lock dumps, callback daemon/socket setup, stats retrieval/zeroing, nfsd suspend/resume, mount-option dump, and new-structure ABI.
- `struct nfscl_dumpmntopts`, used with `NFSSVC_DUMPMNTOPTS` to pass a filename, buffer length, and buffer pointer.

Important behavior:
- Several flags are operation selectors while others are modifiers, notably `NFSSVC_ZEROCLTSTATS` and `NFSSVC_ZEROSRVSTATS` for `NFSSVC_GETSTATS`.
- These constants form a user/kernel ABI, so bit changes affect mount tools, daemons, and diagnostic utilities.

Research notes:
- This is the syscall-control flag source for `nfs_nfssvc.c` and userland NFS management tools.
- Risk areas are ABI compatibility, flag collisions, and ensuring user-supplied buffers are handled according to the exact operation flag.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfssvc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsv4_errstr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsv4_errstr.h

This small header provides static string descriptions for NFSv4 errors from `NFSERR_BADHANDLE` through `NFSERR_CBPATHDOWN`, plus a helper for mapping an error value to one of those strings.

Key contents:
- Static array `nfsv4_errstr[48]` with human-readable messages for the contiguous NFSv4 error range starting at `NFSERR_BADHANDLE`.
- Static helper `nfsv4_geterrstr(int errval)`, which returns `NULL` if the value is outside `NFSERR_BADHANDLE` through `NFSERR_CBPATHDOWN`, otherwise indexes the array by subtracting `NFSERR_BADHANDLE`.

Important behavior:
- The header intentionally defines static storage directly because it is only expected to be used in a small number of C files.
- The array only covers NFSv4.0-era errors through callback-path-down. NFSv4.1 errors defined later in `nfsproto.h` are not included.
- Correctness depends on the NFSv4 error values being contiguous across this range.

Research notes:
- This is diagnostic/UI support, not core protocol handling.
- If adding new error strings, the range check and array size must be updated together.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsv4_errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/old_xdr_subs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/old_xdr_subs.h

This legacy header defines XDR conversion macros for older NFS code. It covers unsigned 32-bit conversion, NFSv2 time conversion, NFSv3 time conversion, and 64-bit hyper conversion using explicit 32-bit network-order words.

Key contents:
- `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` wrappers around `ntohl` and `htonl`.
- `fxdr_nfsv2time()` and `txdr_nfsv2time()` for converting between NFSv2 seconds/microseconds and `timespec` seconds/nanoseconds, including the legacy `0xffffffff` sentinel behavior.
- `fxdr_nfsv3time()` and `txdr_nfsv3time()` for NFSv3 seconds/nanoseconds.
- `fxdr_hyper()` and `txdr_hyper()` for converting 64-bit protocol quantities to and from two 32-bit words.

Important behavior:
- The macros avoid assuming native alignment for 64-bit values, which is important for XDR buffers.
- The older header lacks the NFSv4 time helpers present in `xdr_subs.h`.

Research notes:
- This file exists because the import script renamed the old FreeBSD `nfs/xdr_subs.h` to `old_xdr_subs.h` before merging old and new NFS directories.
- Use this when reading legacy NFS code; use `xdr_subs.h` for the newer common stack.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/old_xdr_subs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/oldnfsproto.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/oldnfsproto.h

This legacy protocol header preserves older NFSv2/v3 and early NFSv4 definitions from the pre-newnfs import path. It overlaps heavily with `nfsproto.h` but uses older names, smaller maximum data assumptions, older error naming, older NFSv4 operation spellings, and additional legacy structs such as `union nfsfh` and `struct nfsv4_fattr`.

Key contents:
- Defines NFS port/program/version constants, v2/v3 maximum data and packet sizes, path/name limits, and traditional NFS status values.
- Defines older fake/internal status marker bits such as `NFSERR_RETVOID`, `NFSERR_AUTHERR`, and `NFSERR_RETERR`.
- Defines wire sizes for v2/v3 file handles, attributes, writable attributes, cookies, write verifiers, create verifiers, statfs, fsinfo, pathconf, and basic v4 verifier/file-handle/stateid sizes.
- Defines generic NFS procedure numbers, actual NFSv2 procedures, NFSv4 COMPOUND procedure number, and NFSv4 operation numbers through WRITE using older names such as `NFSV4OP_OPEN_CONFIRM`.
- Defines v3 access/write/create/fsinfo constants and v4 access/open-share constants.
- Defines file type enum `nfstype`, NFSv4 claim/stability/open/create/time/delegation enums, `union nfsfh`, v2/v3 time structs, 64-bit protocol quad helpers, NFSv3 special device struct, and NFSv4 bitmap/changeinfo structs.
- Defines v2/v3 file attribute and set-attribute structs, `struct nfsv4_fattr` with valid-field bits, old NFSv4 attribute-number macros, bitmap manipulation macros, statfs, fsinfo, and pathconf structures.

Important behavior:
- This header is not identical to `nfsproto.h`. The newer header has broader NFSv4.1/pNFS coverage and modernized names, while this one preserves old ABI/source expectations.
- `NFS_SMALLFH` defaults to 128 here, and `union nfsfh` stores small file handles directly.
- The older NFSv4 bitmap handling only uses two 32-bit words (`FA4_ZERO` zeros 8 bytes), unlike the newer three-word bitmap model in `nfsproto.h`.

Research notes:
- Treat this as compatibility material for old code, not as the authoritative new NFS protocol header.
- Risk areas are accidental inclusion alongside `nfsproto.h`, conflicting macro names, and stale NFSv4 definitions that do not include v4.1 behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/oldnfsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/rpcv2.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/rpcv2.h

This header defines SunRPC version 2 constants and authentication/GSS support values used by the NFS stack. It covers RPC versioning, auth flavors, AUTH_UNIX sizing, RPCSEC_GSS constants, gssd and nfsuserd private RPC program numbers, selected GSS major status codes, RPC reply/error constants, mount protocol constants, and a simple RPC time struct.

Key contents:
- RPC version constant `RPC_VER2`.
- Authentication flavors for null, UNIX, short, Kerberos, GSS, and Kerberos GSS service variants, plus max credential/verifier sizes.
- AUTH_UNIX minimum size and group count limit.
- RPCSEC_GSS version, procedure numbers, service types, sequence window constants, MIC/WRAP constants, QOP, and token/header sizing.
- Private RPC program definitions for `gssd` and `nfsuserd`, including procedure numbers for server and client credential/name operations.
- GSS major status constants guarded so they do not conflict with system GSS headers.
- Core RPC message, accept/deny, program/procedure, garbage, mismatch, and auth error constants.
- Authentication failure constants.
- RPC call/reply header sizes.
- Mount daemon program/version/procedure/path/name constants and NFS RPC program number.
- `struct rpcv2_time`.

Important behavior:
- This header supplies constants needed by both client/server NFS RPC and auxiliary daemons such as gssd and nfsuserd.
- The GSS status block is conditional to avoid redefining values when a GSSAPI header has already been included.

Research notes:
- Use this when tracing RPC header parsing, authentication flavor selection, mount protocol calls, or kernel-to-gssd/nfsuserd interactions.
- ABI-sensitive areas include auth flavor numeric values, RPC program numbers, and header size assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/rpcv2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/xdr_subs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/xdr_subs.h

This header provides XDR conversion macros for the new NFS stack. It is the modern counterpart to `old_xdr_subs.h`, adding NFSv4 time conversion while retaining unsigned, NFSv2/NFSv3 time, and 64-bit hyper conversion helpers.

Key contents:
- `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` for 32-bit network/native conversion.
- `fxdr_nfsv2time()` and `txdr_nfsv2time()` for v2 seconds/microseconds to `timespec`.
- `fxdr_nfsv3time()` and `txdr_nfsv3time()` for v3 seconds/nanoseconds.
- `fxdr_nfsv4time()` and `txdr_nfsv4time()` for v4 high-seconds/seconds/nanoseconds. The decode macro ignores high seconds and clamps nanoseconds with modulo `1000000000`.
- `fxdr_hyper()` and `txdr_hyper()` for unaligned 64-bit values represented as two 32-bit XDR words.

Important behavior:
- All conversions use `ntohl`/`htonl`, relying on them being optimized away on big-endian systems where appropriate.
- The macros deliberately avoid direct 64-bit loads/stores from XDR buffers because alignment is not guaranteed.
- NFSv4 time encoding sets `nfsv4_highsec` to zero, so it only represents times fitting in the low seconds word.

Research notes:
- This file is used anywhere common NFS code converts between mbuf/XDR words and kernel scalar/time types.
- Review time conversion behavior carefully for overflow, high-second handling, and invalid nanosecond values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/xdr_subs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nfs2netbsd.sh -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nfs2netbsd.sh

This shell script is an import helper for arranging FreeBSD's new NFS source tree into NetBSD's `sys/fs/nfs` layout. It copies selected FreeBSD files, rewrites source-identification tags, moves old and new NFS headers to avoid collisions, rearranges directories, generates a starter `files.newnfs`, and prints the CVS import command to run afterward.

Key steps:
- Validates that exactly one argument is supplied and that it names a FreeBSD `sys` directory.
- Extracts file paths from FreeBSD `conf/files` entries containing `nfscl` or `nfsd`, excluding `rpc/` and `xdr/`.
- Finds additional headers under the selected directories and adds them to the copy list.
- Creates the destination directory hierarchy.
- Copies files with an `awk` filter that strips dollar signs from FreeBSD/NetBSD RCS tags, comments out imported NetBSD/FreeBSD ID macros as needed, and injects a fresh NetBSD tag.
- Renames old `nfs/nfsproto.h` to `nfs/oldnfsproto.h` and old `nfs/xdr_subs.h` to `nfs/old_xdr_subs.h`.
- Checks for filename collisions between `nfs/` and `fs/nfs/` before merging.
- Moves old `nfs` and common `fs/nfs` files into `fs/nfs/common`, renames `fs/nfsserver` to `fs/nfs/server`, `fs/nfsclient` to `fs/nfs/client`, and `nlm` to `fs/nfs/nlm`.
- Generates `fs/nfs/files.newnfs` by translating FreeBSD config tokens such as `nfscl`, `nfsd`, `nfslockd`, `nfs_root`, `bootp`, and `inet` into NetBSD config expressions.
- Moves the staged `fs/nfs/*` contents into the current directory and removes temporary directories.

Important behavior:
- The script expects to run in an empty current directory and copies from an external FreeBSD source tree rather than transforming files in place.
- Section 4 directory rearrangements and section 5 `files.newnfs` path rewrites must stay in sync.
- Generated `files.newnfs` is explicitly described as a starting point, not a finished kernel config file.

Research notes:
- This file explains why the NetBSD tree contains imported FreeBSD layout/provenance markers and renamed `old*` protocol/XDR headers.
- If updating from a newer FreeBSD newnfs tree, collision handling and token translation are the main maintenance points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nfs2netbsd.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm.h

This header declares the kernel-facing Network Lock Manager interface used by NetBSD's imported NFS/NLM implementation. It covers host tracking, RPC client lookup, NSM monitoring, blocking-lock wait registration, server-side NLM operation implementations, recovery hooks, and the VOP advisory-lock bridge.

Key contents:
- Declares malloc type `M_NLM` when available.
- Defines `NLM_SYSID_CLIENT`, an offset added to host system IDs when recording NFS client locks in the local lock manager.
- Declares `struct nlm_host`, `struct vnode`, `nlm_zero_tv`, and global NSM state `nlm_nsm_state`.
- Declares netobj helper functions `nlm_make_netobj()` and `nlm_copy_netobj()`.
- Declares host lookup/reference APIs by caller name or address, host monitor registration, host release, RPC client retrieval, host sysid lookup, and remote NSM state lookup.
- Declares blocking lock wait-list APIs: register, deregister, wait with timeout/signal behavior, and cancel waits by vnode.
- Declares NSM notification handling and server-side NLM operation helpers: test, lock, cancel, unlock, granted, granted-result, free-all, and client recovery.
- Declares VFS-facing entry points `nlm_advlock()` and `nlm_reclaim()`.
- Declares `nlm_acquire_next_sysid()` for remote locks outside normal NLM handling.

Important behavior:
- `nlm_register_wait_lock()` must be called before sending a blocking lock RPC, because a granted callback can arrive at any time.
- `nlm_wait_lock()` removes the wait-list entry on timeout or signal; signal callers must send cancellation to the server.
- Host lookup returns a referenced host object; callers must release it.

Research notes:
- This file is the public contract between NFS client vnode code, NLM server code, host/NSM management, and advisory-lock implementation.
- Concurrency-sensitive areas are host reference lifetime, wait-list ordering, granted callback races, and forced-unmount cancellation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_advlock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_advlock.c

This file implements the NFS client advisory byte-range lock bridge between local `VOP_ADVLOCK` operations and remote NLM RPCs. It handles `F_SETLK`, `F_UNLCK`, and `F_GETLK`, maps local process/file lock ownership to NLM wire SVIDs, performs synchronous and blocking NLM calls, copes with lockd timeouts and server grace periods, records successful remote locks in the local lock manager, and reclaims or frees locks during server reboot and vnode reclaim.

Key entry points:
- `nlm_advlock()` is the VOP-facing wrapper around `nlm_advlock_internal()`.
- `nlm_reclaim()` cancels waits for a vnode and iterates local locks to free remote locks during vnode reclaim.
- `nlm_client_recovery()` reclaims all local locks for a host after server reboot, restarting if the remote NSM state changes mid-recovery.
- `nlm_setlock()`, `nlm_clearlock()`, and `nlm_getlock()` implement remote lock, unlock, and test operations.
- `nlm_record_lock()` mirrors successful remote lock/unlock operations into the local lock manager using an NLM client sysid.
- `nlm_init_lock()` converts `struct flock` ranges, file handles, caller/owner identity, and SVID into an `nlm4_lock`.

Important behavior:
- Before lock or unlock operations, `nlm_advlock_internal()` flushes pending writes and invalidates cached data via the mount's `nm_vinvalbuf()` hook. This preserves expected cross-client file visibility around locks.
- The implementation obtains file handle, server address, NFS version, file size, and timeout from the mount's `nm_getinfo()` hook. NFSv3 mounts use NLM version 4; older mounts use NLM version 1.
- For soft mounts, retry count comes from `nm_retry`; for hard mounts, retries are effectively unbounded via `INT_MAX`.
- The current thread temporarily switches to mount credentials so NLM RPC traffic can use privileged-port credentials, then restores the original credentials and releases the temporary credential reference.
- `F_FLOCK` locks receive per-file synthetic SVIDs from an `unrhdr` allocator. The code tracks active whole-file flock ownership and stores credentials for later recovery.
- Blocking flock upgrades from shared to exclusive are approximated by first attempting a nonblocking write lock, then unlocking and retrying as blocking if denied.
- Blocking locks are registered in the NLM wait list before RPC transmission. If the server returns `nlm4_blocked`, the client waits for a granted callback but periodically retries to handle lost callbacks, broken servers, or server reboots.
- If a blocking wait is interrupted or otherwise fails, the code sends NLM CANCEL and keeps retrying cancellation across transient RPC failures.
- NLM server grace-period replies cause sleeps and exponential retry backoff up to 30 seconds in the lock path; unlock and test paths also sleep/retry on grace.
- `nlm_map_status()` maps NLM results to Unix errors: denied to `EAGAIN`, no locks to `ENOLCK`, deadlock to `EDEADLK`, read-only to `EROFS`, stale file handle to `ESTALE`, file too large to `EFBIG`, failed to `EACCES`, and unknown statuses to `EINVAL`.
- Successful non-reclaim lock operations are recorded locally and the host is registered with NSM monitoring so reboot notifications can trigger recovery.
- During recovery and reclaim, the file uses stored owner credentials where possible, falls back to the recovery thread credential when necessary, and uses `F_REMOTE` to preserve remote SVIDs or avoid local lock-manager updates for vnode teardown.

RPC version bridging:
- The core code uses NLMv4 structures internally, then helper wrappers translate to NLMv1 wire structures for older servers.
- `nlm_test_rpc()`, `nlm_lock_rpc()`, `nlm_cancel_rpc()`, and `nlm_unlock_rpc()` dispatch to `nlm4_*_4()` for version 4 or convert arguments/results for `nlm_*_1()`.
- Conversion helpers map common lock, holder, and result fields between 32-bit NLMv1 offsets/lengths and 64-bit NLMv4 representations. `nlm_init_lock()` rejects ranges that overflow NLMv1.

Concurrency and integration:
- `nlm_client_init()` initializes the SVID mutex, allocator, and hash lists at `SI_SUB_LOCK`.
- SVID records are protected by `nlm_svid_lock`; the allocation path handles races by allocating outside the list, then rechecking under lock before insertion.
- `nlm_record_lock()` may block registering locally even after the remote server granted a lock. It handles local `EDEADLK` by briefly pausing and retrying because remote grant order can differ from local lock graph timing.
- `nlm_feedback()` marks the mount with `NFSSTA_LOCKTIMEO` and emits `VQ_NOTRESPLOCK`/recovery events when lockd stops responding or recovers.

Research notes:
- This is the highest-value NLM client file in the group. It defines the semantics users see for `fcntl`/`flock` locks on NFS mounts.
- Review should focus on credential switching, vnode unlock windows, blocking wait/cancel races, SVID lifetime, local/remote lock divergence, recovery idempotence, and range conversion for negative lengths or `SEEK_END`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_advlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot.h

This rpcgen-generated header defines the NLM RPC protocol surface. It includes NLMv1/v3 and NLMv4 data structures, status enums, share-lock types, NSM notification structures, program/version/procedure numbers, client/server function prototypes, and XDR function prototypes.

Key contents:
- Defines `LM_MAXSTRLEN` and `MAXNAMELEN`.
- Defines NLM status enums `nlm_stats` and `nlm4_stats`, with v4 adding read-only filesystem, stale file handle, file-too-big, and failed statuses.
- Defines v1/v3 lock holder, test reply, stat, result, test result, lock, lock arguments, cancel arguments, test arguments, unlock arguments, share, share arguments, share result, and notify structures.
- Defines v4 equivalents with 64-bit offsets and lengths: `nlm4_holder`, `nlm4_lock`, `nlm4_testres`, `nlm4_lockargs`, `nlm4_cancargs`, `nlm4_unlockargs`, share structures, `nlm_sm_status`, and `nlm4_notify`.
- Defines NLM program `100021`, NSM pseudo-version/procedure, version 1, version 3, and version 4 procedure numbers.
- Declares client stubs and service handlers for synchronous procedures, asynchronous message procedures, asynchronous result procedures, share/unshare, non-monitored lock, free-all, and SM_NOTIFY.
- Declares `nlm_prog_*_freeresult()` helpers.
- Declares all XDR routines for NLM/NLMv4 structures and enums.

Important behavior:
- The file is generated and explicitly says not to edit it manually.
- NLMv1 uses 32-bit offsets and lengths, while NLMv4 uses 64-bit values; callers that bridge versions must validate range.
- Message procedures return `void` and deliver results later through result procedures; synchronous procedures return result structs directly.

Research notes:
- This header is the schema for `nlm_prot_clnt.c`, `nlm_prot_svc.c`, `nlm_prot_xdr.c`, and NLM implementation code.
- Protocol compatibility risks are struct layout changes, enum numeric changes, and accidental manual edits not reflected in the `.x` source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_clnt.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_clnt.c

This rpcgen-generated C file implements NLM client stubs. Each function wraps a single NLM/NSM RPC procedure by calling `CLNT_CALL_EXT()` with the procedure number, argument XDR routine, result XDR routine, RPC client handle, optional `rpc_callextra`, and timeout.

Key contents:
- Includes NetBSD kernel headers, `nlm_prot.h`, and RCS/provenance metadata.
- Implements `nlm_sm_notify_0()` for NSM notification RPCs.
- Implements NLM version 1 synchronous calls: `nlm_test_1()`, `nlm_lock_1()`, `nlm_cancel_1()`, `nlm_unlock_1()`, and `nlm_granted_1()`.
- Implements NLM version 1 asynchronous message calls and result calls, including test/lock/cancel/unlock/granted message and result variants.
- Implements NLM version 3 share/unshare, non-monitored lock, and free-all calls.
- Implements NLM version 4 synchronous calls, asynchronous message calls, result calls, share/unshare, non-monitored lock, and free-all calls.

Important behavior:
- The file contains no lock policy logic. It is transport glue generated from the NLM RPC definition.
- The `struct rpc_callextra *ext` argument lets callers attach auth, feedback callbacks, and other RPC metadata; `nlm_advlock.c` uses this for AUTH_UNIX credentials and lockd responsiveness feedback.
- Result freeing is the caller's responsibility via XDR free helpers where variable-length fields are returned.

Research notes:
- This is useful for tracing exact RPC procedure dispatch from implementation code to wire calls.
- Manual edits should be avoided; changes should come from the RPC protocol source and regeneration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_clnt.c -->