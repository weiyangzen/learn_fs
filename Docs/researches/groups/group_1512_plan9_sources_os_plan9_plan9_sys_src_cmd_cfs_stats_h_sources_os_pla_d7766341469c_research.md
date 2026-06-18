# Group Research: group_1512_plan9_sources_os_plan9_plan9_sys_src_cmd_cfs_stats_h_sources_os_pla_d7766341469c

Scope: `Docs/research_subset_a.md`; source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/stats.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/stats.h

Defines CFS statistics data structures. `Cfsmsg` tracks per-message count, accumulated time, and last-call start time. `Cfsstat` keeps 128 client and 128 server message buckets plus cache, directory-read, and byte-flow counters. Exports global current/previous stats (`cfsstat`, `cfsprev`) and `statson` toggle.

Key role: shared instrumentation schema for the Plan 9 cache filesystem command, not behavior itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/chgrp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/chgrp.c

Implements Plan 9 `chgrp`. It parses `-u` and `-o` as aliases for changing `uid` instead of `gid`, then calls `dirwstat` on each file with only the requested owner/group field set in a `nulldir`.

Behavior is intentionally small: `argv[0]` is the new group/user, remaining args are targets. Failures are printed per file and the process exits with `"can't wstat"` if any failed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/chgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/chmod.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/chmod.c

Implements Plan 9 `chmod` for octal modes and symbolic modes. Octal input is parsed with base 8 and applied against read/write/execute permission bits. Symbolic parsing supports `u`, `g`, `o`, `a`, operators `+`, `-`, `=`, and mode letters `r`, `w`, `x`, `a` append, `l` exclusive, `t` temporary.

For each target it reads the current `Dir`, computes `(old & ~mask) | (mode & mask)`, and writes back with `dirwstat`. It reports individual stat/wstat failures but always exits success unless usage or mode parsing fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/chmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/apinums.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/apinums.h

Header of LAN Manager / RAP API numeric identifiers. It maps remote administration APIs such as share, session, file, server, group, user, workstation, print, DFS, and account operations to stable integer call numbers.

Used by `trans.c` to construct `\\PIPE\\LANMAN` transaction requests. The file is data-only; no logic. `MAX_API` is `215`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/apinums.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/auth-testcase.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/auth-testcase.c

Authentication test variant for CIFS. It duplicates the auth logic but enables `NTLMV2_TEST`, forcing deterministic server challenge, user/domain, timestamp, nonce, and expected debug dumps for NTLMv2 vectors.

Implements `plain`, `lm+ntlm`, `ntlm`, and `ntlmv2` methods, selected by `getauth`. It derives NTLMv2 hashes from the UTF-16LE password MD4 hash plus HMAC-MD5 over uppercased user/domain material, builds LMv2 and NTLMv2 responses, and prepares MAC keys.

The `macsign` here is diagnostic: it tries nearby sequence numbers and zero/LM/NT keys before writing a signature. It differs from production `auth.c` and appears intended as a standalone testcase/debug copy rather than the normal build path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/auth-testcase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/auth.c

Production CIFS authentication implementation. Supports `plain`, `lm+ntlm`, `ntlm`, and default `ntlmv2`; plaintext is rejected unless explicitly selected when the server requires it.

Uses Plan 9 auth/factotum APIs for password or MS-CHAP responses. NTLMv2 derives v1 and v2 hashes, emits LMv2/NTLMv2 challenge responses, and builds MAC keys for SMB signing. `macsign(Pkt*, int)` computes or verifies the 8-byte SMB signature at SMB header offset 14, using `BSRSPYL ` before sequence running starts and the negotiated auth MAC key afterward.

Security note: comments explicitly warn LM/NTLM are weak and Kerberos would be preferred, but Kerberos is not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.c

Core SMB1/CIFS protocol client. `cifsdial` tries direct TCP CIFS first, then NetBIOS-over-TCP fallback. `cifshdr`, `pbytes`, and `cifsrpc` build SMB packets, apply signing when enabled, serialize RPC access, validate magic, parse returned IDs/status, and translate NT/DOS errors.

Implements negotiate, session setup, tree connect/disconnect, logoff, file/directory create/delete/rename, NT and legacy open/create, read/write-andX, flush, close, find-close, echo, and basic set-info. It negotiates only `NT LM 0.12`, tracks server capabilities, challenge, timezone, MTU, UID/TID, and optional Unicode/large-file support.

This file is the protocol bridge used by the 9P filesystem in `main.c` and higher-level transaction helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.h

Central CIFS header. Defines SMB command IDs, transaction subcommands, flags/capabilities, DFS flags, share/security/file attribute constants, info levels, server enumeration masks, and core structs.

Important structs: `Auth`, `Session`, `Pkt`, `Share`, `FInfo`, RAP info records, `Refer`, and `Fileinfo`. It also declares global runtime state (`Sess`, `Shares`, `Ipc`, `Debug`, etc.) and every cross-file function prototype for auth, packet packing, NetBIOS, RAP, Trans2, NT transactions, DFS, info files, and ping.

This is the subsystem contract; most implementation files depend on it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/dfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/dfs.c

DFS referral and path remapping layer. Maintains a linked `Dfscache` from client-visible source path to target host/share/path, with expiry, proximity, and RTT. `mapfile` converts Plan 9 path to current target path; `mapshare` resolves or autoconnects the target share, trying both normal and `$` hidden variants.

`redirect` obtains referrals via `T2getdfsreferral`, recursively follows non-storage referrals, pings candidate hosts, and chooses a target based on proximity plus RTT tolerance. The comments document deliberate limitations: it does not spawn separate CIFS client instances for other servers, relies on NetBIOS-style hostnames, and treats many DFS/AD behaviors empirically.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/doserrstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/doserrstr.c

Maps classic SMB DOS/server/hardware error-class codes to readable Plan 9 error strings. The packed key is `(code << 16) | class`. `doserrstr` classifies low-byte error class, searches the static table, and returns either `"class, message"` or an unknown-code string.

Used by `cifsrpc` when the server did not negotiate NT status codes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/doserrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/fs.c

Generates textual diagnostic/info files exposed by the CIFS 9P root. Functions format shares, open files, connection/capability/security state, active sessions, DFS roots, users, groups, domains, and workstations.

Most data comes from RAP calls over `IPC$`; DFS root data comes from Trans2 DFS referrals. The code frees nested strings returned by RAP helpers as it formats them. `period` formats session durations. These functions are registered in `info.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/info.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/info.c

Defines the virtual info-file directory entries: `Users`, `Groups`, `Shares`, `Connection`, `Sessions`, `Dfsroot`, `Dfscache`, `Domains`, `Openfiles`, `Workstations`, and `Filetable`.

Provides lookup (`walkinfo`), count (`numinfo`), directory synthesis (`dirgeninfo`), lazy content generation (`makeinfo`), reads from cached generated buffers (`readinfo`), and cleanup (`freeinfo`). It uses `mkqid` to align info files with the 9P namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/main.c

Main 9P server for mounting remote CIFS shares. It maintains per-fid `Aux` state: current path/share, open file handle, search handle, directory cache window, and linked-list tracking for diagnostics/cleanup.

Implements 9P attach, clone, walk, stat, open, create, read, write, remove, wstat, destroyfid, and server end. Directory reads use Trans2 find-first/find-next with a short cache. Walk/stat convert SMB metadata to Plan 9 `Dir` via `FInfo`; Qids are SHA1-derived from paths plus subtype bits for root/info/share nodes. Open/create choose NT SMBs when available, otherwise legacy SMBs.

`main` parses options, discovers/dials the server, negotiates, authenticates, connects `IPC$`, enumerates or connects requested shares, starts a keepalive process, and posts/mounts the 9P service. Wstat handles rename, length, times, readonly bit, and flushes open files to work around old Windows caching behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/misc.c

Tiny ASCII case-conversion helpers. `strupr` uppercases in place; `strlwr` lowercases in place. Both skip negative `char` values before calling ctype macros.

Used for share/path normalization in the CIFS client.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/netbios.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/netbios.c

NetBIOS support for CIFS fallback and debugging. Provides endian helpers, NetBIOS name encoding, adapter-status lookup for the called name (`calledname`), session establishment on TCP/139 (`nbtdial`), NetBIOS session packet headers (`nbthdr`), and RPC send/read framing (`nbtrpc`).

Handles positive/negative session responses, retarget packets, keepalives, MTU checks, alarms/timeouts, and packet hex dumps. `xd` can dump raw packets, decode SMB/Trans2 headers, and log to `pkt.log` when debugging requests it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/netbios.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/nterrstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/nterrstr.c

Large NTSTATUS-to-string table plus `nterrstr`. Some messages are intentionally changed to match Plan 9/APE error phrasing, for example permission/not-found style errors.

`nterrstr` derives the NT facility from status bits, labels warnings when the high error bit is not set, searches the table, and returns a formatted message or unknown-code fallback. Used by `cifsrpc` for servers negotiating `FL2_NT_ERRCODES`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/nterrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/pack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/pack.c

Packet marshaling/unmarshaling library for CIFS. Provides byte/memory appenders, little/big-endian integer writers/readers, NetBIOS name packing, SMB path/string packing with Unicode support, ASCII-only packing, and DOS/NT time conversions.

Unpacking functions bound reads by `p->eop` and handle Unicode string termination quirks. `gconv` and `goff` resolve RAP/SMB offset-based strings relative to transaction data or a base pointer. This file is heavily used by all SMB command builders and parsers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/ping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/ping.c

ICMP echo helper used by DFS target selection. Sends eight ICMP echo requests with payload validation, ignores the first result in the running RTT average, applies an alarm timeout, and caches both successes and failures for 60 seconds per host.

Returned RTT is used by `dfs.c` to prefer nearby referral targets. Debug output is emitted for DFS debugging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/raperrstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/raperrstr.c

Remote Administration Protocol error-code table and formatter. Covers common LAN Manager, share, user/group, print, service, DFS, domain, and remoteboot errors. `raperrstr` returns `"rap: message"` or an unknown-code fallback.

Used by `trans.c` when RAP calls over `\\PIPE\\LANMAN` return nonzero status other than allowed “more data”.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/raperrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/remsmb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/remsmb.h

Microsoft-derived descriptor string definitions for LAN Manager remote API calls. Defines structure descriptors and parameter descriptors for share, session, file, server, group, user, workstation, print, service, audit, config, account, and related APIs.

Used by `trans.c` to tell RAP servers how parameters and returned structures are encoded. Data-only header with include guard `_REMDEF_`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/remsmb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/sid2name.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/sid2name.c

Maps Windows SIDs to shorter owner/group names for Plan 9 `Dir` fields. Contains well-known local user/group, domain user/group, and alias RID mappings.

`upd_names` opens a file with `READ_CONTROL`, queries owner/group SIDs via `TNTquerysecurity`, maps them through `sid2name`, and updates `Dir.uid`/`Dir.gid`; failures fall back to `"unknown"`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/sid2name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/trans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/trans.c

Implements SMB_COM_TRANSACTION wrappers for RAP/LANMAN calls through `\\PIPE\\LANMAN`. Local helpers build transaction headers, fill parameter/data offsets and counts, dispatch via `cifsrpc`, and position packet cursors on returned parameter/data blocks.

Exposes RAP helpers for share enumeration/info, sessions, groups and group users, users and user info, server/domain/workstation enumeration, and open-file enumeration. It uses `apinums.h`, `remsmb.h`, `raperrstr`, and `pack.c` offset-string conversion.

The code handles partial/more-info responses imperfectly but includes resume loops for `NetUserEnum2`, `NetServerEnum3`, and `NetFileEnum2`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/trans2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/trans2.c

Implements SMB_COM_TRANSACTION2 helpers. Local header/offset helpers mirror `trans.c` but for Trans2 setup words. Exported operations include find-first/find-next directory enumeration, NT and standard path metadata queries, path metadata updates, file length update by handle, filesystem volume/size queries, and DFS referral retrieval.

Directory parsing fills `FInfo` records, including timestamps, size, attributes, resume key, and filename. It contains compatibility workarounds for Windows lying about directory entry counts and old Win9x needing a delay between find-next requests.

Notable defect: `T2fssizeinfo` checks `if(free)` instead of `if(unused)`, so the free-space output pointer guard is wrong.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/trans2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/transnt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/transnt.c

Implements SMB_COM_NT_TRANSACT for security descriptor queries. Helpers build NT transaction headers, fill 32-bit parameter/data counts and offsets, dispatch via `cifsrpc`, and position returned data.

`TNTquerysecurity` requests owner and group security information for a file handle, parses the returned security descriptor, converts binary SID fields to textual `S-...` form, and returns allocated owner/group SID strings. Used by `sid2name.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cifs/transnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cleanname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cleanname.c

Small command wrapper around Plan 9 `cleanname`. Optional `-d pwd` prefixes relative names with a supplied directory before cleaning; absolute paths or no `-d` are cleaned in place. Prints one normalized path per argument.

Handles allocation failure for prefixed names and exits usage on missing args or malformed options.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cleanname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/clock.c

Graphical analog clock using Plan 9 draw/event libraries. Allocates simple color images for background, hands, and hour dots. `redraw` computes center/radius, hour/minute angles from local time, redraws only when time or window rectangle changes, and flushes display.

Main loop listens for mouse events and timer ticks; right-button menu contains only `exit`. `eresized` reattaches the window and redraws.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cmp.c

Implements `cmp` with options `-s` silent, `-l` list all differing bytes, and `-L` include line number for first difference. Accepts optional seek offsets for each file. Reads both files in 64 KiB buffers, compares overlapping spans, tracks byte offset and optionally line count.

Reports seek/open/read errors, first difference, all differences, or EOF mismatch. Silent mode exits with status only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/col.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/col.c

Implements `col`, eliminating reverse line feeds and handling terminal-style overstrikes. It reads runes from stdin, tracks current column and logical half-lines, stores up to 256 line buffers in a ring, and emits output in forward order.

Options: `-b` suppresses overstrike/backspace composition, `-f` treats half-line feeds as full movement, `-x` disables tab compression. It supports ESC `7/8/9`, vertical reverse line feed, CR, tab, backspace, spaces, printable runes, and buffered emission with tabs/backspaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/col.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/colors.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/colors.c

Graphical color-map viewer. Displays available color cells as a grid sized to screen depth; for true-color displays it shows 256 entries. Options: `-x` prints selected values in hex, `-r` displays a grey ramp instead of Plan 9 color-map colors.

In ramp mode on `CMAP8`, it dithers 4x4 grey cells with a Bayer-like matrix. Left mouse drag over a cell updates text with index and RGB/ARGB value. Right-button menu exits. Resizing recomputes grid rectangles and redraws.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/colors.c -->