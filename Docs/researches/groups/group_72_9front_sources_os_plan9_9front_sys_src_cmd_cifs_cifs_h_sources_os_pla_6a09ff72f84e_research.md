# Group Research: group_72_9front_sources_os_plan9_9front_sys_src_cmd_cifs_cifs_h_sources_os_pla_6a09ff72f84e

Scope checked against `Docs/research_subset_a.md`: all files are under the included `sources/os/plan9/9front` source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.h

Defines the shared protocol vocabulary and cross-module API for the Plan 9 CIFS client/server bridge. It contains SMB command IDs, Trans2/NT transaction subcommands, negotiated flags/capabilities, DFS flags, share types, file attribute/access/create constants, and info-level constants.

Core data structures include `Auth`, `Session`, `Pkt`, `Share`, `FInfo`, RAP result structs, DFS `Refer`, workstation/file info structs, and global state declarations such as `Sess`, `Shares`, `Nshares`, `Ipc`, `Host`, `Debug`, and `Active`.

The `Session` struct captures negotiated transport/authentication state, server capabilities, packet-signing state, timing, locks, and remote identity. `Pkt` is the mutable packet cursor object used by all SMB/transaction pack/unpack code.

The header also declares the functional boundaries across the CIFS implementation: authentication, SMB core RPCs, DFS mapping, info-file generation, NetBIOS transport, byte packing, ping/RTT support, RAP enumeration, Trans2 file/FS operations, NT security descriptor query, and SID-to-name augmentation.

Notable implementation context: this is an SMB1/CIFS-era client with optional NetBIOS transport, NT SMB capabilities, DFS support, RAP administrative queries, Unicode path support, and Plan 9 9P-facing synthetic filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/dfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/dfs.c

Implements DFS referral caching and path/share remapping for the CIFS 9P server. The introductory comment documents pragmatic limitations: no AD/Kerberos/LDAP DNS referral lookup, reliance on NetBIOS names matching DNS hostnames, no spawning additional CIFS instances for other DFS servers, and special behavior around DFS reparse points.

Maintains a linked `Dfscache` table mapping source paths to selected target host/share/path with expiry and measured RTT. `dfscacheinfo` renders this cache for the synthetic info filesystem.

`mapfile` rewrites a Plan 9 path into the target share-relative CIFS path. `mapshare` maps a path to an existing connected share or auto-connects to the referred share, trying both plain and `$` hidden-share variants.

`redirect` is the main entry point for resolving or refreshing DFS referrals. It uses `T2getdfsreferral`, recursively follows non-storage referral levels via `redir1`, pings candidate targets, and chooses usable mappings with a tolerance that biases toward earlier Active Directory referral ordering.

Important dependencies: `T2getdfsreferral` from `trans2.c`, `CIFStreeconnect`, `ping`, global `Shares/Nshares/Sess`, and `Checkcase/Debug/Dfstout`.

Risk notes: cache mutation is global and not visibly synchronized; case checking has a `Badmatch` enum but lookup only sets exact/no match; behavior is heavily based on observed Windows/Samba quirks rather than a complete DFS/AD implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/doserrstr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/doserrstr.c

Provides translation from legacy DOS/SMB error class/code values to human-readable strings. The table is derived from Samba `nterr.h` material and includes GPL notice text.

`DOSerrs` stores combined keys as `(code << 16) | class`, covering DOS, server/network, and hardware error classes. Examples include access denied, file not found, share conflict, invalid TID, pipe errors, disk full, and authentication failure.

`doserrstr(uint err)` identifies the SMB error class from the low byte, scans for a full table match, and returns a static formatted string. Unknown errors are formatted with class plus numeric code.

Used by debug/packet reporting and likely core CIFS RPC error formatting when negotiated packets are not using NT status codes.

Implementation note: returns a static buffer, so callers must consume/copy immediately if reentrancy is a concern.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/doserrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/fs.c

Generates textual contents for the CIFS synthetic info files exposed at the mounted root. It is not the 9P server itself; it supplies report functions registered by `info.c`.

`shareinfo`, `openfileinfo`, `sessioninfo`, `userinfo`, `groupinfo`, `domaininfo`, and `workstationinfo` query the remote server using Trans2 and RAP calls, then format the results into a `Fmt`.

`conninfo` prints current session identity, server name/domain/OS, clock slip, MTU, guest status, negotiated capabilities, security mode bits, and transport type.

`dfsrootinfo` recursively calls DFS referrals beginning at the domain root path `""` and prints DFS root/domain entries. `nodelist` backs domain/workstation browsing via server enumeration RAP calls.

Important dependencies: `T2fsdeviceinfo`, `T2fssizeinfo`, `RAPshareinfo`, `RAPsessionenum`, `RAPuserenum*`, `RAPgroup*`, `RAPServerenum*`, `RAPFileenum2`, `T2getdfsreferral`, and global `Sess`, `Ipc`, `Shares`.

Resource behavior: functions generally free per-entry strings after formatting, making these generators single-pass snapshots for `info.c` caching.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/info.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/info.c

Defines the synthetic info directory entries exposed by the CIFS mount. `Infdir` maps names such as `Users`, `Groups`, `Shares`, `Connection`, `Sessions`, `Dfsroot`, `Dfscache`, `Domains`, `Openfiles`, `Workstations`, and `Filetable` to generator functions.

`walkinfo` resolves a top-level info filename to its slot. `numinfo` reports the number of info entries. `dirgeninfo` fills a Plan 9 `Dir` for an info file using `mkqid`.

`makeinfo` lazily materializes an info file by running its generator into a string buffer. `readinfo` serves slices from that cached buffer. `freeinfo` releases the cached buffer when the fid is destroyed.

The file is the bridge between 9P directory walking in `main.c` and the live server-reporting functions in `fs.c`.

Boundary note: range checks use `path > nelem(Infdir)` rather than `>=`, which means `path == nelem(Infdir)` passes in several functions and would index past the table if reached.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/main.c

Implements the Plan 9 9P filesystem front end for a remote CIFS/SMB server. It mounts remote shares and synthetic info files into a namespace, handling attach, walk, stat, open/create, read/write, remove, wstat, fid cloning/destruction, and server shutdown.

`Aux` tracks per-fid state: current path, share pointer, directory search handle/resume state, file handle, cached directory entries, cache bounds/expiry, and synthetic mtime override for open files. `Openfiles` is a circular list used for diagnostics and coordinated close/remove behavior.

Path walking integrates root info files, top-level shares, case validation, DFS share/path remapping, Trans2 metadata queries, and DFS reparse-point redirection. Directory reads use `T2findfirst/T2findnext`, cache batches briefly, remove `.`/`..`, and convert `FInfo` into Plan 9 `Dir`.

File open/create supports both classic SMB open/create and NT create paths depending on server capabilities. Reads and writes are chunked by negotiated MTU. Wstat implements rename, length changes, mtime/atime update, readonly attribute handling, and flushes open files for Win95-style metadata cache issues.

`main` handles CLI flags, dials with NetBIOS called-name discovery fallbacks, negotiates protocol, authenticates via factotum/auth helpers, connects `IPC$`, enumerates or connects requested shares, starts a keepalive process, and calls `postmountsrv`.

Important dependencies: almost every CIFS subsystem: `cifsdial`, `CIFSnegotiate`, `CIFSsession`, `CIFStreeconnect`, `RAPshareenum`, Trans2 metadata/directory operations, DFS mapping, SID update, packet auth, and Plan 9 lib9p.

Behavioral notes: the implementation is explicitly tuned for Windows/Samba SMB1 quirks, uses global session/share state, and exposes administrative/server information as ordinary readable files at the mount root.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/misc.c

Contains two in-place ASCII case conversion helpers: `strupr` and `strlwr`.

Each walks a mutable C string and applies `toupper`/`tolower` only after checking the byte is non-negative and currently lower/upper case.

Used by CIFS command setup and name normalization, notably share names from command-line arguments in `main.c`.

Scope is intentionally tiny; no allocation, locale, or Unicode handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/netbios.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/netbios.c

Implements NetBIOS name service/session support and packet debugging for CIFS over NetBIOS. It includes local byte-get/put helpers, NetBIOS name encoding, called-name discovery, TCP session setup, NetBIOS-framed RPC I/O, and hex/protocol dumps.

`calledname` sends a UDP/137 adapter status query for `*`, parses returned NetBIOS names, and selects a non-group workstation/service name. `nbtdial` opens TCP/139, performs NetBIOS session request, handles positive/negative/keepalive/retarget packets, and returns a connected fd.

`nbthdr` initializes a packet with a NetBIOS session header. `nbtrpc` fills payload length, writes the full packet, reads and validates response headers, skips keepalives, enforces MTU, and returns packet length.

`xd` is a debugging dumper. It can append raw bytes to `pkt.log`, decode SMB header fields, print Trans2 request/response header fields, and translate SMB errors through `nterrstr` or `doserrstr`.

Important dependencies: packet packing helpers from `pack.c`, global `Debug`, constants from `cifs.h`, and Plan 9 networking via `netmkaddr`, `dial`, `readn`, `alarm`.

Risk notes: low-level parsing assumes packet layouts and uses fixed buffers; debugging code decodes selected SMB forms rather than a complete protocol parser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/netbios.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/nterrstr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/nterrstr.c

Large NTSTATUS-to-string mapping table plus formatter. The table includes success/warning/error statuses across core NT, filesystem, network, DFS, Kerberos, smart card, cluster, ACPI, Side-by-Side, Terminal Services, and related facilities.

Several entries are adjusted to match Plan 9/APE-style user-facing errors, for example mapping access/object path failures to messages like `permission denied`, `does not exist`, or `file name syntax`.

`nterrstr(uint err)` derives the NTSTATUS facility from bits 16..26, maps selected facility names, scans the table for an exact status code, prefixes non-error statuses with `warning, `, and returns a static formatted string.

Used for CIFS packet/RPC error reporting when the server negotiates NT error codes (`FL2_NT_ERRCODES`).

Implementation note: linear lookup over a large static table is simple and acceptable for error paths/debug output; return storage is static and not reentrant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/nterrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/pack.c

Provides all primitive packet cursor serialization/deserialization helpers for CIFS packets. The functions operate directly on `Pkt->pos`, `Pkt->buf`, and `Pkt->eop`.

Packing functions write bytes, little/big-endian integers, 64-bit values, NetBIOS names, DOS date/time, Windows FILETIME, ASCII strings, Unicode strings, and path strings with `/` converted to `\`. Unicode packing enforces the Windows 16-bit codepoint limit.

Unpacking functions read bounded memory, ASCII/Unicode strings, offset-based DFS/transaction strings, big/little-endian integers, DOS date/time, and Windows FILETIME. String reading includes alignment handling and compatibility hacks for Windows Unicode terminators.

`gconv` handles RAP-style converted pointer offsets relative to transaction data. `goff` handles DFS referral string heaps with unaligned Unicode behavior.

Important dependencies: `Pkt` state from `cifs.h`, Plan 9 rune conversion, server flags/caps, and transaction code in `trans.c`, `trans2.c`, and `transnt.c`.

Risk notes: this is a manual cursor parser; it has some bounds checks for numeric reads but string routines rely on protocol shape and pointer validity in places.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/ping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/ping.c

Implements ICMP echo RTT probing for DFS referral target selection. It caches both successful and failed host results for 60 seconds in a linked `Pingcache`.

`ping(host, timeout)` first checks cache, then opens an ICMP dial to the host and sends eight echo requests with a small payload. It validates type/code, sequence bytes, and payload contents on replies.

The first RTT is effectively smoothed into the rolling `rtt` calculation; the comment says the first result is ignored because route setup may skew it, but the arithmetic initializes `rtt` at `-1` and averages each observed interval.

Failures return `-1` and are cached too, which avoids repeatedly probing down DFS targets.

Used by `dfs.c` to choose among DFS referral target servers, with optional debug logging under the `dfs` debug flag.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/raperrstr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/raperrstr.c

Maps Microsoft Remote Administration Protocol/LANMAN API error numbers to readable messages. The table covers generic access/password errors, service, print, logon, user/group, share, DFS, remoteboot, browser, UPS, and domain join/account policy errors.

`raperrstr(uint err)` scans the table for an exact match and returns `rap: <message>` or a numeric unknown-error string in a static buffer.

Used by RAP wrapper functions in `trans.c` to turn remote API status words into Plan 9 error strings via `werrstr`.

Implementation is intentionally simple: static table, linear search, static return buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/raperrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/remsmb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/remsmb.h

Microsoft-origin header defining descriptor strings for SMB transaction remote API calls. It is guarded by `_REMDEF_` and primarily consists of `#define` constants.

Descriptors cover share, session, connection, file, server, group, user, workstation, use, print queue/job/destination, profile, statistics, time-of-day, NetBIOS, config, domain controller, account sync/update, path/name, RPL, and miscellaneous LANMAN API layouts.

The CIFS implementation uses selected descriptors from this header in `trans.c`, especially for share enumeration/info, sessions, users/groups, server enumeration, and open file enumeration.

This file is protocol metadata rather than executable logic. The comments explain descriptor naming conventions and the remote API assumption that return parameter length must not exceed send parameter length.

Research relevance: it shows the CIFS client depends on old RAP/LANMAN descriptor-string encoding for administrative queries, not only file-oriented SMB operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/remsmb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/sid2name.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/sid2name.c

Adds minimal Windows SID-to-name mapping for Plan 9 directory uid/gid display. The static `known` table maps common well-known local users/groups, domain users/groups, and aliases to short names.

`sid2name` handles nil/malformed SIDs as `-`, exact SID matches, and prefix-plus-RID matches for domain-relative identities. Unknown SIDs are represented by their final RID component.

`upd_names` opens a file with `READ_CONTROL`, queries owner/group security descriptors via `TNTquerysecurity`, converts SIDs, and replaces the `Dir` uid/gid fields. On open failure it uses `unknown`.

Used from `main.c` directory/stat conversion when the `Billtrog` toggle requests real owner/group lookup.

Limitations: no domain controller lookup or SID name service; the mapping is mostly built-in well-known identifiers plus fallback RID display.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/sid2name.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/trans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/trans.c

Implements SMB `SMB_COM_TRANSACTION` wrappers for RAP/LANMAN remote administration calls over `\PIPE\LANMAN`.

Internal helpers build transaction headers (`thdr`), fill parameter/data offsets/counts (`ptparam`, `ptdata`), dispatch through `cifsrpc` (`trpc`), and move packet cursors to returned parameter/data sections.

Public RAP functions enumerate and query shares, sessions, groups, group users, users, user info, servers/domains/workstations, and open remote files. They use API numbers from `apinums.h` and descriptor strings from `remsmb.h`.

Parsing relies on fixed-width RAP records plus converted string offsets via `gconv`. Multi-page APIs use returned resume keys or follow-up enumeration calls; several comments document Windows/Samba quirks and permission limitations.

Important consumers: `fs.c` info-file generators, `main.c` initial share enumeration, and open-file/session/domain/user/group synthetic views.

Risk notes: buffers are sized from server MTU and parsed manually; several functions trust `navail` for allocation and tolerate servers lying about entry counts by stopping at packet end.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/trans2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/trans2.c

Implements SMB `SMB_COM_TRANSACTION2` helpers and file/filesystem/DFS Trans2 calls.

Internal helpers build Trans2 headers (`t2hdr`), set parameter/data offsets and counts (`pt2param`, `pt2data`), run the RPC (`t2rpc`), and position cursors on returned parameter/data blocks.

Directory enumeration is implemented by `T2findfirst` and `T2findnext`, parsing `SMB_FIND_FILE_FULL_DIRECTORY_INFO` into `FInfo` arrays and handling Windows quirks such as bad reported directory entry counts and Win95 timing sensitivity.

Metadata functions query path info in NT all-info or older standard formats, set path info, set file length through file information, and query filesystem volume/device/size information.

`T2getdfsreferral` sends DFS referral requests and parses referral versions 1, 2, and 3, including path/address string heaps, TTL defaults, flags, and domain-root versus normal referral forms.

Used by `main.c` for walk/stat/dirread/wstat, by `fs.c` for info files, and by `dfs.c` for DFS cache resolution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/trans2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/transnt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/transnt.c

Implements the SMB `SMB_COM_NT_TRANSACT` subset needed by this CIFS client: querying owner/group security descriptors.

Internal helpers construct NT transaction headers, fill parameter/data counts and offsets, dispatch via `cifsrpc`, and position returned cursors.

`TNTquerysecurity` sends `NT_TRANSACT_QUERY_SECURITY_DESC` for owner and group security information on an open file handle. It parses the returned security descriptor offsets and formats Windows SIDs as strings like `S-1-5-...`.

The function is consumed by `sid2name.c` to update Plan 9 `Dir` uid/gid fields for remote files.

Scope is intentionally narrow: no DACL/SACL parsing, no security descriptor mutation, and no generalized NT transaction framework beyond the single query operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/transnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cleanname.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cleanname.c

Small command-line wrapper around Plan 9 `cleanname`. It normalizes pathnames and prints the cleaned results.

Supports `-d pwd`; relative input names are prefixed with that directory before cleaning, while absolute names or no `-d` are cleaned in place.

Allocates a temporary combined path for `-d` relative cases and exits on allocation failure.

Usage: `cleanname [-d pwd] name...`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cleanname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/clock.c

Graphical analog clock for Plan 9 draw/event. It opens a draw window, allocates simple color images, and redraws hour/minute hands plus twelve dots.

`circlept` computes positions by angle. `redraw` recalculates only when time or window rectangle changes, centers the clock, derives radius from window size, draws background/dots/hands, and flushes the image.

`eresized` reattaches on window resize and triggers redraw. `main` initializes draw/event, starts a 30-second timer, and provides a right-click menu with `exit`.

No filesystem logic; included as a small Plan 9 user command in the same source tree batch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cmp.c

Implements Plan 9 `cmp` for bytewise file comparison with optional offsets.

Flags: `-s` silent status-only, `-l` list all differing bytes with hex values, and `-L` include line number in first-difference output/counting. Usage accepts `file1 file2 [offset1 [offset2]]`.

`seekoff` validates numeric offset arguments and seeks each file. The main loop reads both files into 64 KiB buffers, compares common spans with `memcmp`, then scans byte-by-byte on mismatch to report differences and track newline counts.

Exit status distinguishes identical, differ, EOF difference, read/open/seek errors through Plan 9 `exits` strings.

Implementation note: it reports EOF on the shorter file after the number of equal bytes processed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/col.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/col.c

Implements `col`, a filter that eliminates reverse line feeds and handles half-line motion for terminal output streams.

It reads runes through `bio`, tracks current horizontal position and logical line/half-line position, stores a rolling page buffer of lines, and emits reordered output once lines are safe to flush.

Handles newline, NUL, escape sequences `ESC 7/8/9`, reverse line feed, carriage return, tab, backspace, space, and printable runes. `-b` changes overstrike behavior, `-f` treats half-line feeds as full movements, and `-x` suppresses tab compression on output.

The output path reconstructs spacing/tabs, backspaces, and half-line movement as needed.

Core data structures are fixed-size: `PL` page slots and `LINELN` line buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/col.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/colors.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/colors.c

Graphical color-map viewer for Plan 9 draw/event. It displays the screen color map or a grayscale ramp in a grid and reports color values under mouse selection.

Flags: `-r` shows a grey ramp instead of `cmap2rgb`, and `-x` formats displayed values in hex.

`eresized` lays out color rectangles based on screen depth: up to 256 colors, 16 columns for depth > 8, or a depth-derived grid for lower depths. It redraws all swatches after resize.

For grayscale on `CMAP8`, it builds a dithered 4x4 image using a Bayer-like threshold table to approximate finer grey levels.

Left mouse drag prints selected index and RGBA-derived value at the top of the window. Right mouse menu supports exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/colors.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/comm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/comm.c

Implements `comm`, comparing two sorted text files and printing three columns: lines only in file1, only in file2, and common lines.

Flags `-1`, `-2`, and `-3` suppress the corresponding output columns while adjusting tab leaders.

Uses `Biobuf` input and fixed 2048-byte line buffers. `rd` reads one line, terminates at newline or near buffer capacity, and strips the newline by replacing it with NUL. `compare` performs lexical byte comparison.

The main loop reads one current line from each file, compares, writes the appropriate column through `wr`, and advances the relevant file. `copy` drains the remaining file when the other reaches EOF.

Supports `-` as stdin through `/fd/0`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/comm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/compress/compress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/compress/compress.c

Historical Unix `compress`/`uncompress`/`zcat` implementation using LZW compression, adapted for Plan 9 APE via `_PLAN9_SOURCE` and standard C/POSIX headers.

Command behavior is selected by program name or flags. Supports compression, decompression, stdout mode, force overwrite, max bits via `-b`, no-magic legacy mode, quiet/verbose stats, and optional debug table/code dumping when compiled with `DEBUG`.

Compression uses variable-width LZW codes from 9 up to `maxbits` default 16, open-addressed double hashing over prefix+character pairs, optional block compression with `CLEAR`, adaptive table reset when compression ratio worsens, and file-size-tuned hash table sizes.

Decompression reconstructs the LZW string table on the fly using overlaid memory: compression hash table storage doubles as decompression prefix/suffix/stack storage.

File lifecycle: for named files it writes `.Z` output or strips `.Z` on decompression, prompts before overwrite in foreground, copies mode/owner/timestamps to output, and unlinks unsuccessful output. The input unlink is commented out in this 9front copy, so successful compression does not remove the source.

Important caveats: old C style in debug helpers, many globals, fixed output filename buffer, legacy signal handling, and classic `compress` format constraints rather than modern compression/container design.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/compress/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/con.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/con/con.c

Implements `con`, an interactive terminal/network connection tool. It can connect to a device path, simple dialed byte stream, or BSD rlogin-style service, then shuttle bytes between local terminal and remote endpoint.

Options control baud, cooked/raw console mode, command execution over the connection, debugging, limited rlogin mode/user, keyboard suppression, carriage-return filtering/conversion, parity stripping, `/srv` posting, verbose dialing, and newline-to-carriage-return translation.

`simple`, `rlogin`, and `device` establish the three connection modes. `stdcon` forks two processes sharing memory: one handles keyboard-to-network (`fromkbd`), the other network-to-screen (`fromnet`).

Interactive control is entered with control-backslash (`0x1c`), offering break, quit, interrupt, return-filter toggle, continue, or local shell command execution. Raw mode is managed through `/dev/consctl`.

`system` runs `/bin/rc` with the network connection as stdout and a pipe for stdin, allowing local command output to be sent to the remote side.

Reliability behavior includes interrupt-tolerant `iread/iwrite`, first-error capture for dial fallback, notification handling for pipe/hangup/interrupt, and cleanup of posted `/srv` entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/con.c -->