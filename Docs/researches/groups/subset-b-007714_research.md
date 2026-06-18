# subset-b-007714 Research

Grouped research for OpenAFS Windows SMB, pioctl, named-pipe RPC, symlink tooling, afslegal UI, afsd tests, and redirector user/kernel ABI headers. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb3.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb3.h

## Purpose
`smb3.h` defines the Windows afsd SMB dialect-3/NT transaction interface: transaction packet state, dispatch table entries, on-wire packed response structures, and prototypes for SMB_COM_TRANSACTION, SMB_COM_TRANSACTION2, RAP, NT transact, AndX read/write/open/lock, notify, and extended-security helper routines. It is the shared contract between the SMB packet decoder/encoder and higher cache-manager operations.

## Important APIs, Types, And Functions
The central type is `smb_tran2Packet_t`, which accumulates multi-part transaction parameters/data, connection identity (`vcp`, `tid`, `uid`, `pid`, `mid`), sub-opcode, named-pipe metadata, decoded strings, and response/error state. `smb_tran2Dispatch_t` maps a sub-opcode to a handler and flags. Packed structures include `smb_tran2QFSInfo_t`, `smb_tran2QPathInfo_t`, `smb_tran2QFileInfo_t`, `smb_tran2Find_t`, and short/long file attribute records. Exported handlers cover session setup, tree connect, transaction parsing, RAP share/workstation/server info, file/directory search, FS/path/file info get/set, FSCTL/IOCTL, DFS referral, NT create/transact/cancel/rename, and change notification.

## Control Flow
Runtime flow is declaration-only here: SMB receive code builds or extends `smb_tran2Packet_t`, dispatches through `smb_tran2DispatchTable` or `smb_rapDispatchTable`, obtains response packets with `smb_GetTran2ResponsePacket`, sends them via `smb_SendTran2Packet`, then frees state with `smb_FreeTran2Packet`. The packed unions are written directly into SMB response buffers, so layout is part of the protocol.

## State And Persistence
This header declares transient per-request state only. Durable effects occur in the implementation handlers, which can open files, mutate attributes, enumerate directories, or register notifications. `smb_tran2Packet_t` tracks partial request assembly across SMB fragments.

## Dependencies And Integration Points
It depends on SMB connection types (`smb_vc_t`, `smb_packet_t`), cache scache types, Windows `FILETIME`, `LARGE_INTEGER`, `HANDLE`, `PSID`, and client string abstractions. It integrates with `smb3.c`, `smb.c`, named-pipe RPC, DFS behavior, directory enumeration, and cache-manager metadata conversion.

## Risks
The packed wire structs are sensitive to compiler packing, character width, and byte counts. Buffer fields such as 512-byte names require caller-side bounds checks. Multi-part transaction accounting (`totalData`, `curData`, `maxReturnData`) is a truncation and overflow risk. Dispatch-table opcode bounds must remain synchronized with `SMB_TRAN2_NOPCODES` and `SMB_RAP_NOPCODES`.

## Test Signals
Useful tests include SMB1/NT dialect clients querying file/path/FS info, long Unicode names, find-first/find-next pagination, named-pipe transactions, NTCreateX and locking flows, DFS referral responses, and notification delivery after file changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_iocons.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb_iocons.h

## Purpose
`smb_iocons.h` is the shared constant header for Windows AFS pioctl operations used by afsd and command-line tools such as `fs` and `symlink`. It assigns stable VIOC opcode numbers, common payload structures, the magic ioctl pseudo-file name, and maximum pioctl buffer/procedure counts.

## Important APIs, Types, And Functions
The file defines wire structs `chservinfo_t`, `gaginfo`, `ClearToken`, and `sbstruct`; flags such as `GAGUSER`, `GAGCONSOLE`, `CM_SETCELLFLAG_SUID`, and `VIOC_NEWCELL2_FLAG_*`; VIOC opcodes from `VIOC_FILE_CELL_NAME` through `VIOC_GETCALLERACCESS`; and the test-only `VIOC_VOLSTAT_TEST`. It also defines `CM_IOCTL_FILENAME`, wide and no-slash variants, `CM_IOCTL_MAXDATA` as 16 KiB, and `CM_IOCTL_MAXPROCS` as 64.

## Control Flow
There is no executable code. Clients write a request to the magic SMB file with an opcode followed by operation-specific data. `smb_ioctl.c` uses these numbers as indexes into `smb_ioctlProcsp`, so every opcode must be less than `CM_IOCTL_MAXPROCS`.

## State And Persistence
The header stores no state, but its constants gate stateful operations: token install/delete, ACL changes, cache flushes, cell config, symlink and mount point creation, rxkad settings, ownership/mode updates, and caller access queries.

## Dependencies And Integration Points
It includes AFS integer types through consumers and is included by `smb_ioctl.h`, afsd code, and user commands. It must stay synchronized with cache-manager `cm_Ioctl*` handlers and userland pioctl encoders.

## Risks
Opcode ABI drift can break existing Windows tools. Duplicate or out-of-range opcode assignment will either dispatch the wrong handler or be rejected. Structs are C ABI payloads and are not self-describing; size or endian assumptions matter when data is copied from request buffers.

## Test Signals
Regression signals include every `fs`/`symlink` pioctl command reaching the intended handler, invalid opcodes returning errors, token commands accepting valid `ClearToken` payloads, and maximum-size payload tests around the 16 KiB limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_iocons.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.c

## Purpose
`smb_ioctl.c` implements the legacy SMB pseudo-file pioctl transport for the Windows OpenAFS client. It turns opens of `_._AFS_IOCTL_._` into special FIDs, accumulates write data, dispatches the embedded VIOC opcode on the first read, translates SMB users/TIDs/paths into cache-manager objects, and streams the resulting status/data back to the client.

## Important APIs, Types, And Functions
`smb_InitIoctl` initializes the `smb_ioctlProcsp[SMB_IOCTL_MAXPROCS]` dispatch table for ACL, volume, cache, cell, token, symlink, mountpoint, rxstat, uuid, Unicode, Unix mode, owner/group, verify-data, and caller-access operations. `smb_SetupIoctlFid` marks a FID as `SMB_FID_IOCTL`, attaches `cm_data.fakeSCache`, allocates `smb_ioctl_t`, and copies subst-drive prefix state. Request transport functions are `smb_IoctlPrepareWrite`, `smb_IoctlWrite`, `smb_IoctlV3Write`, `smb_IoctlPrepareRead`, `smb_IoctlRead`, `smb_IoctlV3Read`, and `smb_IoctlReadRaw`. Path helpers `smb_ParseIoctlPath` and `smb_ParseIoctlParent` convert UTF-8/ANSI/OEM input, handle UNC paths through NetBIOS share lookup or `/cell/` reconstruction, support literal no-mount-chase mode, and return `cm_scache_t` objects. Handler wrappers mostly call matching `cm_Ioctl*` functions.

## Control Flow
Writes allocate and zero input/output buffers, set `CM_IOCTLFLAG_DATAIN`, append request bytes, and enforce `SMB_IOCTL_MAXDATA`. Reads resolve the SMB UID to `cm_user_t`, detect LocalSystem, map TID to a base path, then call `smb_IoctlPrepareRead`. That function consumes the first 32-bit opcode, validates dispatch bounds, reserves output space for the return code, calls the selected handler, and writes the handler status at the front of the output buffer. Subsequent reads stream remaining output bytes until `outCopied` catches `outDatap`.

## State And Persistence
Per-FID state lives in `smb_ioctl_t`: active UID, tree path, subst prefix, and `cm_ioctl_t` buffer pointers/counters/flags. Persistent side effects are delegated: token state in `cm_user_t/cm_ucell_t`, cache and ACL state, volume/cell preferences, symlink/mountpoint mutations, Unix mode and owner/group updates, trace settings, and validation data. Token setup is especially stateful: `smb_IoctlSetToken` validates Kerberos ticket and clear token sizes, resolves cell/user/SMB name, validates token-event UUID/session key, restricts logon-token install to LocalSystem/RPC SID context, stores ticket/session key/kvno/expiration under `userp->mx`, bumps token generation, and resets ACL cache.

## Dependencies And Integration Points
The file depends on Windows security APIs (`LookupAccountNameW`, SID conversion), SMB UID/TID/share APIs, `cm_NameI`, scache synchronization, pioctl query options, logging, NetBIOS raw send, and the broad `cm_Ioctl*` cache-manager surface. It integrates command-line tools, Explorer shell calls, logon token flows, SMB tree connections, and the Windows redirector compatibility path.

## Risks
This is security-sensitive. Risks include path parsing confusion between UTF-8, ANSI, OEM, UNC share names, and cell names; unchecked path component copies into fixed arrays; stale `userp`/`uidp` lifetime handling; opcode-table drift; output buffer overflow if `cm_Ioctl*` handlers overrun `SMB_IOCTL_MAXDATA`; and privilege errors around LocalSystem logon token installation. The code contains repeated handler patterns where missing query options can leave `scp` uninitialized in set-owner/group/mode style functions if options are absent, though callers are expected to provide them.

## Test Signals
Test with SMB core and AndX reads/writes, fragmented pioctl writes, raw read responses, invalid and unassigned opcodes, UTF-8-prefixed and OEM paths, UNC share and `\\afs\all` forms, query-by-FID options, literal mountpoint handling, LocalSystem and non-LocalSystem token logon flows, symlink/mountpoint create/list/delete, and cache/volume/cell operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.h

## Purpose
`smb_ioctl.h` declares the SMB pioctl transport interface and the `smb_ioctl_t` per-FID state used by `smb_ioctl.c`. It bridges SMB FIDs, users, virtual circuits, cache-manager ioctl buffers, and named VIOC handlers.

## Important APIs, Types, And Functions
`smb_ioctl_t` stores the owning `smb_fid`, current `smb_user`, TID path, subst prefix, and embedded `cm_ioctl_t`. `smb_ioctlProc_t` is the dispatch signature for pioctl handlers. Public entry points cover initialization, FID setup, SMB core/V3/raw reads and writes, read preparation, path and parent parsing, token install, SMB name lookup, and a large handler set for ACLs, cache flushes, cells, sysname, server prefs, mountpoints, symlinks, rxkad, trace, ownership, Unix mode, verify data, and caller access.

## Control Flow
Callers identify an ioctl pseudo-file open, call `smb_SetupIoctlFid`, then route SMB read/write operations to the declared functions while ordinary file FIDs go through normal SMB file I/O. Individual handler declarations are loaded into the dispatch table by `smb_InitIoctl`.

## State And Persistence
The header defines only pointers and buffer state; persistence happens in implementations and delegated cache-manager handlers. Prefix and TID path fields are crucial because pioctl path payloads are interpreted relative to SMB tree state.

## Dependencies And Integration Points
It includes `cm_ioctl.h` and `smb_iocons.h`, forward-declares SMB structures, and exposes some cache-manager flush helpers used across SMB/cache code. It is included by SMB receive paths and handlers that need to recognize ioctl FIDs.

## Risks
The declaration list must remain synchronized with `smb_InitIoctl`; missing prototypes can hide ABI drift. `smb_ioctl_t` owns multiple borrowed and allocated pointers, so cleanup code must release prefix/path/user references consistently. Handler signatures pass raw mutable buffers, so all implementers need strict length discipline.

## Test Signals
Compiler warnings for signature mismatches, successful dispatch of each registered opcode, leak checks for repeated open/write/read/close cycles, and path-relative pioctl tests all validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.c

## Purpose
`smb_rpc.c` implements SMB named-pipe RPC support for the Windows afsd service. It maps selected pipe endpoint names onto internal MSRPC connections, marks SMB FIDs as RPC pipes, serializes per-FID RPC calls, and implements SMB core, AndX, and transaction read/write/transceive paths.

## Important APIs, Types, And Functions
`smb_RPC_SetupEndpointByname` accepts only `wkssvc` and `srvsvc`, mapping them to `.\\PIPE\\wkssvc` and `.\\PIPE\\srvsvc` for `MSRPC_InitConn`. `smb_SetupRPCFid` strips any leading path component, marks `SMB_FID_RPC`, attaches `fakeSCache`, allocates `smb_rpc_t`, initializes the endpoint, and returns message-mode pipe file type/device-state flags. `smb_CleanupRPCFid` frees the MSRPC connection. I/O helpers wrap `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`, and `MSRPC_WriteMessage`. `smb_RPCRead`, `smb_RPCWrite`, `smb_RPCV3Read`, `smb_RPCV3Write`, and `smb_RPCNmpipeTransact` implement the SMB-facing protocol.

## Control Flow
Before each RPC operation, callers lock the FID and call `smb_RPC_BeginOp`; if another request is active, it sleeps until `SMB_FID_RPC_INCALL` clears. Writes obtain the SMB user, parse the SMB data block or AndX data offset, and pass the request bytes to MSRPC. Reads prepare a response, cap the message length by client count/max return data, fill SMB response parameters, and copy MSRPC bytes into the SMB output buffer. Transaction named-pipe transceive writes request data, reads the response, wraps it in a transaction response packet, and sends it, preserving `CM_ERROR_RPC_MOREDATA` as a transaction error status when needed.

## State And Persistence
`smb_rpc_t` stores the owning FID and `msrpc_conn`. Persistent state is the MSRPC conversation per open pipe. `SMB_FID_RPC_INCALL` is a concurrency gate and is cleared by `smb_RPC_EndOp`, which wakes sleepers.

## Dependencies And Integration Points
The file depends on `msrpc.h`, SMB FID/packet/user APIs, `smb3.h` transaction helpers, Windows/NT status headers, and cache-manager users. It integrates with the SMB named-pipe open path and with generated/handwritten RPC service implementations for workstation and server service calls.

## Risks
Only two endpoints are accepted; adding endpoints requires explicit mapping. Serialization is per FID, so missed `smb_RPC_EndOp` calls can deadlock a pipe. Length handling depends on MSRPC message length checks and SMB client-provided counts. User lookup failure must abort writes/reads to prevent unauthenticated pipe processing.

## Test Signals
Exercise `wkssvc` and `srvsvc` named-pipe opens, core and AndX read/write, transaction transceive with multi-fragment/more-data responses, concurrent requests on one FID, invalid endpoint names, and disconnect/cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.h

## Purpose
`smb_rpc.h` declares the SMB named-pipe RPC interface used by afsd. Under `SMB_RPC_IMPL` it also defines `smb_rpc_t`, the per-FID wrapper around `msrpc_conn`.

## Important APIs, Types, And Functions
The public functions are `smb_SetupRPCFid`, `smb_CleanupRPCFid`, `smb_RPCRead`, `smb_RPCWrite`, `smb_RPCV3Read`, `smb_RPCV3Write`, and `smb_RPCNmpipeTransact`. The setup call returns SMB pipe metadata through `file_type` and `device_state`.

## Control Flow
SMB open code calls setup when an opened path resolves to a supported pipe endpoint. Later SMB read/write and transaction receive paths branch on `SMB_FID_RPC` and call these functions rather than normal file I/O.

## State And Persistence
The header exposes no global state. The implementation-owned `smb_rpc_t` persists with the FID until close and contains MSRPC connection state.

## Dependencies And Integration Points
It depends on SMB FID/VC/packet types and `smb_tran2Packet_t`; the concrete struct depends on `msrpc.h`. It connects SMB named pipes to MSRPC service dispatch.

## Risks
Consumers that include the header without `SMB_RPC_IMPL` see an opaque `struct smb_rpc`, which is intentional. Function signatures must remain aligned with the SMB receive code. Cleanup must be called while respecting the documented FID lock expectations.

## Test Signals
Build tests should cover both opaque and implementation includes. Runtime signals include correct device-state flags on pipe open, successful core/V3 pipe I/O, and no leaks after repeated pipe closes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/symlink.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/symlink.c

## Purpose
`symlink.c` is the Windows command-line utility for listing, creating, and removing AFS symlinks. Since Windows lacks a native AFS symlink syscall, the utility packages operations as pioctls (`VIOC_LISTSYMLINK`, `VIOC_SYMLINK`, `VIOC_DELSYMLINK`) against parent directories.

## Important APIs, Types, And Functions
`ListLinkCmd` validates each path, derives parent and leaf names, fetches FID/file type with query options, verifies the object is `AFS_FILE_TYPE_SYMLINK` (`3`), and prints the target. `MakeLinkCmd` verifies the parent is in AFS, restricts freelance root modifications to administrators, normalizes UNC targets under the AFS NetBIOS name into Unix-style paths, and issues `VIOC_SYMLINK`. `RemoveLinkCmd` verifies the link by listing it first, applies the freelance admin guard, and issues `VIOC_DELSYMLINK`. `wmain` initializes Winsock, command parsing, UTF-8 argv conversion, and registers `list`, `make`, `remove`, and `rm`.

## Control Flow
The command framework dispatches subcommands. Each subcommand performs local string/path checks, adapts `\\afs\` roots to `\\afs\all\` when needed, prepares a `ViceIoctl` blob, and calls `pioctl_utf8`. Errors are reported with `fs_Die` or explicit stderr messages, and per-item loops continue where possible.

## State And Persistence
The tool has no persistent local state except process-wide command globals and the static output buffer. Persistent effects are AFS symlink creation/deletion and any root.afs freelance changes mediated by the server/cache manager.

## Dependencies And Integration Points
It depends on Windows APIs, Winsock startup, OpenAFS `fs_utils`, command parser, `cm_ioctl.h`, pioctl UTF-8 support, file type query options, and NetBIOS-name helpers. It integrates directly with `smb_ioctl.c`/cache-manager symlink handlers.

## Risks
Path buffers are fixed at 1024 bytes and rely on `StringCb*` for most, but not all, copies. UNC conversion logic is subtle around trailing slashes and drive-letter stripping. File type value `3` is hard-coded in one check. Admin checks are local policy and must match server-side enforcement.

## Test Signals
Test list/make/remove on normal paths, drive-relative paths, `\\afs\cell` and `\\afs\all\cell`, non-AFS parents, non-symlink targets, freelance root with admin and non-admin users, long paths, and UTF-8 link/target names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/btreetest.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/test/btreetest.c

## Purpose
`btreetest.c` is a standalone Windows test harness for the OpenAFS B+ directory tree and filename normalization lookup behavior. It fakes enough cache-manager/logging state to insert normalized directory entries and verify exact, inexact, and ambiguous filename matching.

## Important APIs, Types, And Functions
The harness defines fake `cm_SetFid`, `cm_FindSCache`, `cm_ReleaseSCache`, `cm_ApplyDir`, and `afsi_log` implementations. `initialize_tests` calls `osi_Init`, `cm_InitNormalization`, `cm_InitBPlusDir`, and creates a fake log. `simple_test` builds a tree with `initBtree`, inserts normalized long names and generated 8.3 aliases when needed, then uses `bplus_Lookup`, `getSlot`, data-node iteration, and `comparekeys(..., EXACT_MATCH)` to classify results.

## Control Flow
`wmain` initializes the test environment and runs `simple_test` through `RUNTEST`. Each row inserts a filesystem string converted to normalized/client forms, then looks up a provided client string. Exact matches return success, one non-exact candidate returns `CM_ERROR_INEXACT_MATCH`, multiple candidates would return `CM_ERROR_AMBIGUOUS_FILENAME`, and missing entries return `ENOENT`.

## State And Persistence
State is in-memory only: B+ tree nodes, fake scache/fid values, and test counters. There is no disk or cache persistence.

## Dependencies And Integration Points
The test includes `afsd.h` and uses normalization, 8.3 generation, directory B+ tree, lock, and OSI log primitives. It is a targeted signal for directory lookup semantics used by the Windows cache manager.

## Risks
The fake functions may mask integration issues in real directory/scache code. The test mostly prints failures and has limited process exit rigor. Unicode cases cover important ligatures and composed/decomposed Hebrew-style examples but are not exhaustive.

## Test Signals
Expected output is zero failed tests and matching vnode values for expected successful/inexact lookups. Adding cases for ambiguity, deletion, duplicate short names, and real directory enumeration would broaden coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/btreetest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/convtest.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/test/convtest.c

## Purpose
`convtest.c` is a standalone test program for OpenAFS Windows Unicode normalization and UTF-8/UTF-16 conversion helpers in `cm_nls.h`.

## Important APIs, Types, And Functions
It tests `cm_NormalizeStringAlloc`, `cm_Utf16ToUtf8Alloc`, `cm_Utf16ToUtf8`, `cm_Utf8ToUtf16Alloc`, and `cm_Utf8ToUtf16`. It uses fixture arrays for normalization pairs, external Unicode normalization conformance data (`norm_tests`, `n_norm_tests`), and UTF-8/UTF-16 pairs including BMP private-use, replacement character, and surrogate-pair code points. `dumputf8` and `dumpunicode` format failures.

## Control Flow
`main` initializes normalization, then runs each test macro in sequence. Each test loops fixtures, converts or normalizes, validates non-null/nonzero return, checks returned length includes the NUL terminator, compares exact byte/wchar output, prints `PASS`, and aborts on first hard failure for most conversion cases.

## State And Persistence
There is no persistent state. The normalization subsystem may initialize process-global tables, and each allocation test frees returned buffers.

## Dependencies And Integration Points
The test depends on `cm_nls.h`, C runtime string functions, and external normalization fixtures. It validates low-level functions used by SMB path parsing, directory lookup, case folding, and pioctl string conversion.

## Risks
The tests focus on valid input and do not deeply exercise malformed UTF-8, insufficient destination buffers, embedded NULs, or locale edge cases. `cm_NormalizeStringTest` returns success even after printing failed count, which can hide conformance failures from automation.

## Test Signals
A good run prints `PASS` for allocation/conversion fixtures and zero normalization mismatch messages. CI should treat any printed failure count as failure and add negative/bounds tests for truncation and invalid sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/convtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/stricmptest.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/test/stricmptest.c

## Purpose
`stricmptest.c` is a diagnostic test program for UTF-8 case-insensitive comparison, UTF-8 character navigation, and UTF-8 uppercase conversion helpers.

## Important APIs, Types, And Functions
The main tested helpers are `cm_stricmp_utf8`, `char_next_utf8`, `char_prev_utf8`, and `strupr_utf8`. Fixture arrays compare ASCII and non-ASCII pairs such as AE/ae, accented Latin letters, and mixed-case strings with expected comparison results.

## Control Flow
`wmain` prints comparisons using standard `strcmp`, CRT `stricmp`, and `cm_stricmp_utf8`, then walks a mixed ASCII/non-ASCII UTF-8 string forward and backward printing character offsets, then uppercases fixture strings in fixed buffers.

## State And Persistence
No state persists. All operations are local buffers and string literals.

## Dependencies And Integration Points
It includes Windows headers, `strsafe.h`, and `cm_nls.h`. These helpers are used by Windows afsd filename comparison, normalization, and directory search behavior.

## Risks
The program is mostly observational: it does not increment failure counters or return nonzero on mismatch. Fixed `MAX_PATH` buffers are acceptable for fixtures but do not test long-string behavior. Invalid UTF-8 navigation is not covered.

## Test Signals
Useful automation would assert expected comparison values, forward/backward character counts and offsets, and uppercase outputs. Current manual signal is printed mismatch visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/test/stricmptest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afslegal/afslegal.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afslegal/afslegal.cpp

## Purpose
`afslegal.cpp` implements a small Windows GUI that displays the OpenAFS legal notice for a fixed interval. It is a localized, modeless dialog wrapper around string resources.

## Important APIs, Types, And Functions
`Lawyer_OnInitDialog` bolds the title control font, formats the message from `IDS_MESSAGE_1`, sets `IDC_MESSAGE`, and frees the formatted string. `Lawyer_DlgProc` handles `WM_INITDIALOG`, `WM_TIMER`, `WM_DESTROY`, `WM_CTLCOLORSTATIC`, and cancel commands. `WinMain` loads the corresponding locale module, creates `IDD_LAWYER`, positions it at the bottom of the Z order, and runs a standard message loop.

## Control Flow
On startup, the dialog is created and shown without activation. Initialization populates controls and starts a 5000 ms timer. The timer destroys the window and kills the timer; destroy posts quit, ending the message loop.

## State And Persistence
State is transient GUI state: dialog handle, timer, generated bold font, and a static background brush. No configuration or disk state is written.

## Dependencies And Integration Points
The file depends on Win32 GUI APIs, `WINNT/talocale.h` localization helpers, and resource IDs from `resource.h` plus localized `.rc` files. It is likely launched by installer/startup flows that need to show license/legal text.

## Risks
Created GDI font and static brush are not explicitly deleted, though process lifetime is short. The message formatter assumes localized resource availability. The dialog silently exits after 5 seconds, so accessibility and slow-reader concerns depend on surrounding product requirements.

## Test Signals
Tests should verify localized resource loading, visible title/message controls, timer auto-close, cancel close, no activation stealing beyond intended behavior, and absence of GDI growth under repeated launch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afslegal/afslegal.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afslegal/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afslegal/resource.h

## Purpose
`resource.h` assigns numeric IDs for the afslegal dialog, legal-message string resources, and controls. It is consumed by `afslegal.cpp` and localized resource scripts.

## Important APIs, Types, And Functions
The constants are `IDS_MESSAGE_1` through `IDS_MESSAGE_5`, `IDD_LAWYER`, `IDC_TITLE`, `IDC_MESSAGE`, and `IDC_STATIC`. The `APSTUDIO_INVOKED` block carries Visual Studio resource editor defaults.

## Control Flow
There is no runtime flow. At compile time, RC scripts bind these IDs to strings/dialog templates; at runtime `afslegal.cpp` uses them to load and set UI text.

## State And Persistence
No state is stored. The IDs are ABI-like resource contracts across source, `.rc`, and localized modules.

## Dependencies And Integration Points
It integrates with `afslegal.cpp`, `afslegal_stub.rc`, and language-specific `afslegal.rc` files.

## Risks
Changing IDs without updating RC files breaks localization or dialog control lookup. Message IDs start at zero, which is valid but can surprise tooling that treats zero specially.

## Test Signals
Resource compilation, successful localized dialog creation, and correct text in `IDC_TITLE`/`IDC_MESSAGE` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afslegal/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSProvider.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSProvider.h

## Purpose
`AFSProvider.h` defines the user/kernel IOCTL and packed data contract for the OpenAFS Windows network provider interface. It allows provider code to add, cancel, query, list, and inspect redirector connections.

## Important APIs, Types, And Functions
It defines the redirector device name `\\Device\\AFSRedirector`, provider IOCTLs `IOCTL_AFS_ADD_CONNECTION`, `IOCTL_AFS_CANCEL_CONNECTION`, `IOCTL_AFS_GET_CONNECTION`, `IOCTL_AFS_LIST_CONNECTIONS`, and `IOCTL_AFS_GET_CONNECTION_INFORMATION`, and interface version `AFS_NETWORKPROVIDER_INTERFACE_VERSION_1`. Packed structs are `AFSNetworkProviderConnectionCB` and `AFSCancelConnectionResultCB`.

## Control Flow
Provider callers open the redirector device and send buffered IOCTLs with these control blocks. Enumeration uses `CurrentIndex` and returned connection metadata; cancel returns a status and local drive name.

## State And Persistence
The header stores no state. The IOCTLs affect redirector provider connection lists, local drive mappings, authentication IDs, comments, remaining path, and remote name metadata.

## Dependencies And Integration Points
It depends on Windows `CTL_CODE`, `FILE_DEVICE_DISK_FILE_SYSTEM`, `LARGE_INTEGER`, and `WCHAR`. It integrates with the Windows network provider DLL/service and redirector connection management in the kernel driver.

## Risks
Packed variable-length structs require exact offset and length validation. `LocalName` followed by `RemoteName[1]` is a flexible-array pattern that can be overrun if callers miscompute buffer size. Versioning must be checked before interpreting fields.

## Test Signals
Map/unmap/list network provider connections, validate enumeration indexes, long remote/comment strings, authentication ID propagation, and malformed buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSProvider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonDefines.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonDefines.h

## Purpose
`AFSRedirCommonDefines.h` centralizes constants and debug helpers shared by OpenAFS Windows redirector components. It covers pool tags, FCB/object type IDs, debug flags, volume/authgroup/device flags, library device names, and trace/assert wrappers.

## Important APIs, Types, And Functions
Important groups are memory tags (`AFS_GENERIC_MEMORY_*`, `AFS_FCB_ALLOCATION_TAG`, extent/name/provider tags), object type constants (`AFS_FILE_FCB`, `AFS_DIRECTORY_FCB`, `AFS_IOCTL_FCB`, symlink/mountpoint/special share types), debug flags (`AFS_DBG_*`), pool states, volume flags, authgroup reparse policy flags, and device flags (`AFS_DEVICE_FLAG_HIDE_DOT_NAMES`, shutdown, short-name disable, direct service I/O). Inline helpers include `AFS_ASSERT` and `AFSBreakPoint`; macros include `try_return`, `AFSPrint`, and `AFSDbgTrace`.

## Control Flow
There is no domain algorithm. Allocation and object initialization code stamps tags/types from this file; debug code calls trace/breakpoint macros depending on checked-build state and debugger presence.

## State And Persistence
No state is stored here except external function pointers declared elsewhere (`AFSDumpTraceFilesFnc`, `AFSDebugTraceFnc` via macro use). Constants influence kernel pool diagnostics, runtime flags, and service-device identity.

## Dependencies And Integration Points
It depends on Windows kernel types and build macros such as `DBG`, `NTDDI_VERSION`, and debugger-presence symbols. It integrates with redirector FCB/VCB/CCB allocation, library control device setup, trace logging, and reparse policy.

## Risks
Pool tag reuse reduces diagnostic value. Calling `AFS_ASSERT` assumes `AFSDumpTraceFilesFnc` is valid. Debug macros compile differently between checked/free builds, so behavior can diverge. Device path constants are ABI-sensitive.

## Test Signals
Driver verifier/poolmon should show expected tags. Checked builds should break only when a debugger is attached. Initialization should create/open `\\Device\\AFSLibraryControlDevice`, and debug trace configuration should route through `AFSDbgTrace`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonDefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonStructs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonStructs.h

## Purpose
`AFSRedirCommonStructs.h` defines internal kernel/library redirector structures for trees, queues, FCBs, extents, device extensions, provider connections, framework callbacks, and library initialization. It is the in-memory control-plane/data-plane schema for afsredir and its service library.

## Important APIs, Types, And Functions
Core data structures include `AFSBTreeEntry`, `AFSListEntry`, `AFSTreeHdr`, `AFSCommSrvcCB`, `AFSPoolEntry`, `AFSNonPagedFcb`, `AFSExtent`, `AFSFcb`, `AFSDeviceExt`, and packed `AFSProviderConnectionCB`. Callback typedefs define framework hooks for processing requests, logging, adding provider connections, pool allocation/free, authgroup retrieval, and trace dumps. `AFSLibraryInitCB` passes device objects, server/mount root names, debug flags, global root FID, cache manager callbacks, cache memory mapping, and callback table into the library.

## Control Flow
The header describes objects used by runtime flows: request/result pools queue IRP work to the service; FCB/NPFCB locks serialize file, paging, section, extent, dirty-list, and CCB state; device extensions split control, redirector, and library-specific state; worker queues process async work; provider connection lists support network-provider enumeration; library init wires callback functions from framework to loaded library.

## State And Persistence
Most fields are live kernel state. FCBs track open counts, share access, object information, dirty extents, locks, purge points, section-create file objects, and queued flush counts. Device extensions track cache file mapping, volume/root-cell trees, provider lists, sysname lists, process/authgroup trees, library state, outstanding service requests, memory pressure, and worker queues. Persistent filesystem state is represented indirectly through cached metadata and extents, not stored by this header itself.

## Dependencies And Integration Points
It depends on Windows kernel primitives (`ERESOURCE`, `KEVENT`, `FAST_MUTEX`, `SECTION_OBJECT_POINTERS`, `FSRTL_ADVANCED_FCB_HEADER`, `FILE_LOCK`, device/file/cache manager types), plus user ABI structs such as `AFSFileID`, `AFSRequestExtentsCB`, and `AFSFileExtentCB`. It integrates the redirector driver, service communication layer, library module, network provider, cache manager, and authgroup subsystem.

## Risks
This is concurrency-dense. Lock ranking comments must be followed to avoid deadlocks. Many list/tree pointers are intrusive and require lifetime discipline. Control/RDR/Library union fields must be interpreted only for the matching device role. Packed provider connection structs contain `UNICODE_STRING` fields and pointers, so they are internal, not raw user ABI. Extent counters and events can cause leaks or hangs if not updated atomically.

## Test Signals
Driver verifier, checked-lock assertions, open/close stress, byte-range lock tests, cache extent request/release/dirty flush cycles, provider connection enumeration, library load/unload, network status transitions, and memory-pressure simulations are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSRedirCommonStructs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserDefines.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserDefines.h

## Purpose
`AFSUserDefines.h` defines the user-visible constants for the Windows AFS redirector service interface: symbolic link/device names, request type numbers, request flags, trace subsystem bits, invalidation reasons, extent flags, file type values, sysname constants, access modes, and reparse policy controls.

## Important APIs, Types, And Functions
Key constants include `AFS_SYMLINK(_W)`, `AFS_PIOCTL_FILE_INTERFACE_NAME`, `AFS_GLOBAL_ROOT_SHARE_NAME`, `AFS_PAYLOAD_BUFFER_SIZE`, request types `AFS_REQUEST_TYPE_DIR_ENUM` through direct read/write processing, request flags such as synchronous, case-sensitive, WOW64, fast request, hold FID, cleanup flush/delete/unlock, LocalSystem PAG, cache bypass, and last-component. It also defines trace levels/subsystems, invalidation reasons, extent flags (`DIRTY`, `RELEASE`, `CLEAN`, `FLUSH`, `IN_USE`, `UNKNOWN`, `MD5_SET`), AFS file types, Windows special file types, and reparse-point policy flags/scopes.

## Control Flow
There is no code flow. The redirector sends `AFS_REQUEST_TYPE_*` work items to the service, which interprets the corresponding control block from `AFSUserStructs.h` and responds through result IOCTLs. Flags alter service and driver behavior.

## State And Persistence
No state is stored, but the constants govern persistent/cache-affecting operations such as directory enumeration, file creation/update/delete, extent caching, pioctl pipe operations, authgroup behavior, invalidation, and reparse policy.

## Dependencies And Integration Points
It is shared by kernel and user-mode builds. Conditional definitions provide NT status, file attributes, and filesystem attributes when not in kernel mode. It integrates with `AFSUserIoctl.h`, `AFSUserStructs.h`, afsd_service, and afsredir.sys.

## Risks
Request type and flag numbers are ABI. Renumbering breaks service/driver compatibility. Some comments document required response behavior, such as synchronous requests needing `IOCTL_AFS_PROCESS_IRP_RESULT`; violating those contracts causes hangs or lost completions. Typos in subsystem names/comments do not affect ABI but can confuse diagnostics.

## Test Signals
Cross-version service/driver tests, unknown request rejection, trace mask filtering, invalidation reason handling, extent flag combinations, cache-bypass reads/writes, and reparse policy IOCTLs validate the constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserDefines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserIoctl.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserIoctl.h

## Purpose
`AFSUserIoctl.h` assigns the buffered device IOCTL codes used between user-mode OpenAFS components and the Windows AFS redirector/library devices.

## Important APIs, Types, And Functions
The header defines `IOCTL_AFS_INITIALIZE_CONTROL_DEVICE`, `INITIALIZE_REDIRECTOR_DEVICE`, `PROCESS_IRP_REQUEST`, `PROCESS_IRP_RESULT`, extent set/release/failure, cache invalidation, network/volume status, shutdown, sysname notification, status request, byte-range locks, debug trace configuration/retrieval, force crash, library device initialization, object information, authgroup create/query/set/reset/SID/logon operations, library trace config, and reparse policy get/set.

## Control Flow
User-mode service code calls `DeviceIoControl` with these `CTL_CODE(FILE_DEVICE_DISK_FILE_SYSTEM, function, METHOD_BUFFERED, FILE_ANY_ACCESS)` values and the matching structs from `AFSUserStructs.h`. Some IOCTLs initialize devices, some pull work from the driver, and others push results or notifications back down.

## State And Persistence
The header stores no state. IOCTLs mutate driver/service state: initialization, extent ownership, cache invalidation, online/offline state, sysname lists, authgroups, trace settings, and reparse policy.

## Dependencies And Integration Points
It requires Windows `CTL_CODE` definitions and is paired with `AFSUserDefines.h` and `AFSUserStructs.h`. It is an ABI boundary between afsd_service/library code and afsredir.sys.

## Risks
Function code collisions or access/method changes break compatibility. `FILE_ANY_ACCESS` puts validation burden on driver-side security checks. Buffered IOCTLs require strict size checks for variable-length trailing arrays.

## Test Signals
DeviceIoControl tests should verify each IOCTL accepts correct buffer sizes, rejects malformed sizes, enforces caller authorization for dangerous operations like force crash/authgroup/logon, and remains compatible across service/driver versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserIoctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserPrototypes.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserPrototypes.h

## Purpose
`AFSUserPrototypes.h` declares user/cache-manager side functions that notify or service the Windows AFS redirector. These functions are implemented elsewhere and are the call surface from afsd/cache-manager logic into redirector coordination.

## Important APIs, Types, And Functions
Exports include `RDR_Initialize`, shutdown notify/final, network and address change notifications, volume status/invalidation, object status invalidation, file status setting, sysname notification, background fetch, suspend/resume, and `RDR_RequestExtentRelease` for returning held extents.

## Control Flow
Higher-level cache-manager code calls these functions when redirector state must be initialized, invalidated, updated, or drained. Extent release callbacks send file extent lists to the redirector; sysname and volume/network notifications update kernel-visible state.

## State And Persistence
The header stores no state. Implementations affect redirector state, cache extent state, volume/object validity, and service lifecycle state.

## Dependencies And Integration Points
It depends on `cm_fid_t`, `cm_scache_t`, `cm_user_t`, `cm_req_t`, `AFSFileExtentCB`, `GUID`, and Windows `DWORD/BOOLEAN/ULONG`. It integrates cache-manager events with afsredir.sys.

## Risks
The functions return Windows `DWORD` or AFS integer status inconsistently, so callers must interpret return values correctly. Passing stale FIDs or authgroups can invalidate wrong objects. Background fetch is async and must respect scache/user lifetimes.

## Test Signals
Driver/service initialization, network up/down, cell volume online/offline, object invalidation, sysname changes, extent release under cache pressure, suspend/resume, and shutdown sequencing validate the prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserPrototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserStructs.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserStructs.h

## Purpose
`AFSUserStructs.h` defines the user/kernel ABI payloads for the Windows AFS redirector service channel. It covers generic request/result framing, redirector initialization, directory and volume data, create/open/update/delete/rename/link operations, extents, pioctl and pipe I/O, invalidation, locks, FID hold/release, cleanup, debug trace, object status, authgroups, AFS reparse tags, direct file I/O, and reparse policy.

## Important APIs, Types, And Functions
Foundational structs are `AFSFileID`, `AFSCommRequest`, and `AFSCommResult`. Initialization uses `AFSRedirectorInitInfo`. Directory/volume structs include `AFSDirQueryCB`, `AFSDirEnumEntry`, `AFSDirEnumResp`, `AFSVolumeInfoCB`, and `AFSVolumeSizeInfoCB`. File operation structs include create/open/access-release, extent request/set/release/failure, update/delete/rename/hardlink/symlink/eval, cleanup, and direct `AFSFileIOCB`/result. Service interfaces include pioctl and pipe open/read/write/info control blocks. Locking uses byte-range request/result structs. Status/auth/reparse structs include invalidation, network/volume status, sysname notification, driver status, object status, authgroup request, `AFSReparseTagInfo`, and reparse policy get/set.

## Control Flow
The driver queues an `AFSCommRequest` with request type, flags, authgroup, file ID, name, and operation-specific data. The service reads it through `IOCTL_AFS_PROCESS_IRP_REQUEST`, performs cache/server work, and returns `AFSCommResult` or separate IOCTL payloads such as extent and lock results. Variable-length structures use trailing one-element arrays and offsets/lengths to pack names, targets, EAs, extents, and result arrays.

## State And Persistence
The structs represent and mutate live redirector/cache state: FID identity, directory snapshots, data versions, extents and dirty ranges, file times/sizes/attributes, lock ownership, authgroup membership, sysname lists, object status, cache invalidation, and reparse behavior. They do not persist independently but encode changes that may affect AFS server state or local cache persistence.

## Dependencies And Integration Points
It depends on Windows scalar types, `GUID`, `LARGE_INTEGER`, `BOOLEAN`, and constants from `AFSUserDefines.h`. It is paired with IOCTL codes in `AFSUserIoctl.h` and internal structures in `AFSRedirCommonStructs.h`. Both user-mode service and kernel-mode redirector must compile compatible layouts.

## Risks
This is the highest ABI-risk header in the group. Flexible-array patterns require exact buffer-size validation and alignment, especially directory entries, extents, target names, EAs, lock arrays, and reparse buffers. Pointers such as mapped buffers are meaningful only in the expected address/context and must not be trusted across boundaries. Time/data-version/expiration fields must be kept coherent to prevent stale cache exposure. Authgroup and LocalSystem-related requests require strict authorization.

## Test Signals
ABI tests should verify structure sizes/offsets for 32-bit, 64-bit, and WOW64; fuzz malformed lengths/offsets/counts; run directory enumeration with symlinks/mountpoints; create/update/delete/rename/hardlink/symlink files; request/release dirty and clean extents; exercise pioctl and pipe paths; validate byte-range lock conflict reporting; test authgroup inheritance/query/set/reset; and verify reparse tag policy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserStructs.h -->
