# Group Research: group_180_9front_sources_os_plan9_9front_sys_src_cmd_spred_win_c_sources_os_pl_3ed94fabb972

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/win.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/spred/win.c

`win.c` implements window lifecycle and focus management for `spred`, using Plan 9 draw/mouse/frame primitives and the local `Wintab` type dispatch table.

Key responsibilities:
- Allocates the backing `Screen`, per-window color images, inverse-color image, and initial command window in `initwin`.
- Creates windows with `newwin`, links them into the global `wlist`, optionally links them into a file’s window list, initializes type-specific state via `w->tab->init`, and draws through `w->tab->draw`.
- Supports mouse-created windows (`newwinsel`), zero-copy/clone-like window duplication (`winzerox`), close (`winclose`), focus/top-window ordering (`setfocus`), point hit-testing (`winpoint`), click dispatch (`winclick`), and button-selected target windows (`winsel`).
- Handles explicit window resize and global screen resize, scaling all window rectangles proportionally after `getwindow`.

Important state:
- Global `scr`, `wlist`, `flist`, `actw`, `actf`, `cmdw`, `invcol`.
- `tabs[]` maps `CMD`, `PAL`, and `SPR` to external `cmdtab`, `paltab`, and `sprtab`.

Integration notes:
- File windows hold references to `File`; `winclose` refuses to close dirty last references once, setting `change = -1`.
- Most behavior is delegated through `Wintab` callbacks, so this file owns geometry/focus and leaves window content semantics elsewhere.

Risks:
- Uses intrusive linked lists and manual image lifetime management; incorrect `File` reference/list invariants could leak or use freed windows.
- `resize` rescales by old screen dimensions and assumes nonzero dimensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/spred/win.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/srv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/srv.c

`srv.c` implements the Plan 9 `srv` command: connect to a 9P service by dialing a network address or running a command, post the connection in `/srv`, and optionally mount it.

Key functions:
- `usage` documents `srv [-abcCmnNq] [net!]host [srvname [mtpt]]` and `srv -e ...`.
- `ignore` handles alarm timeout and closed-pipe notes.
- `connectcmd` forks `/bin/rc -c cmd` with a pipe connected to stdin/stdout.
- `main` parses mount flags, auth options, command execution, retry/sleep options, derives `/srv/name` and `/n/name`, dials `netmkaddr(..., "9fs")` or runs a command, posts the fd, and mounts via `mount` or `amount`.
- `post` creates the service file and writes the connected fd number.
- `error` reports contextual failures.

Behavior:
- Supports `-a`, `-b`, `-c`, `-C`, `-m`, `-q` mount variations.
- `-n` disables authentication; `-N` also becomes user `none` before mounting.
- Retries once if mount fails with hangup/timeout after removing the srv file.

Risks:
- Command mode trusts the supplied shell command.
- Derived `/srv` and mount names depend on string parsing of host paths and `!`.
- `post` writes the fd but does not close the created srv file before exit; process exit handles cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/srvfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/srvfs.c

`srvfs.c` is a small helper that posts an `exportfs` instance into `/srv` for a path.

Behavior:
- Usage: `srvfs [-dR] [-p perm] [-P patternfile] [-e exportfs] srvname path`.
- Builds an argument vector for `/bin/exportfs` or a replacement specified with `-e`.
- Supports exportfs flags:
  - `-d`
  - `-R`
  - `-P patternfile`
  - Always adds `-r path`.
- Creates a pipe, posts one end into `/srv/<srvname>` or an absolute service path with `ORCLOSE`, then forks a child that dup’s the other pipe end to stdin/stdout and execs exportfs.
- `-p` controls service file permissions, default `0600`.

Integration:
- Uses Plan 9 service-file convention: writing an fd number to `/srv/...`.
- Uses `rfork(RFPROC|RFNOWAIT|RFNOTEG|RFFDG)` so the exportfs child persists independently.

Risks:
- Fixed `arglist[16]` is adequate for current options but not dynamically checked.
- `buf[64]` bounds service path expansion; long service names are truncated by `snprint`/`strecpy` behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/srvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ssh.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ssh.c

`ssh.c` is a compact SSH-2 client for 9front. It handles transport, key exchange, authentication, session/direct-tcp channels, terminal mode, and a raw mux mode used by companion tools.

Core protocol pieces:
- Defines SSH message numbers for transport, userauth, global requests, and channel operations.
- `vpack`/`vunpack`, `pack`, and `unpack` encode/decode SSH byte, uint32, string, raw buffer, and mpint fields.
- `sendpkt` and `recvpkt` implement packet framing, padding, sequence numbers, and optional `chacha20-poly1305@openssh.com` encryption/MAC after key exchange.
- `kex` performs Curve25519 key exchange, verifies RSA SHA-256 host signatures, checks host thumbprints, derives Chacha keys, and schedules rekeying.
- RSA helpers convert between Plan 9 `RSApub`/`mpint` and SSH wire formats.

Authentication:
- `noneauth`, `pubkeyauth`, `passauth`, and `kbintauth` try supported SSH userauth methods.
- Public-key auth uses factotum `/mnt/factotum/rpc`.
- Password auth uses `auth_getuserpasswd`; keyboard-interactive prompts on `/dev/cons`.

Channel handling:
- `dispatch` handles global messages, disconnect/debug/banner, rekey, channel data, extended data, flow-control window adjustments, EOF/close, and exit status/signal.
- Main opens either a session channel or `direct-tcpip` channel via `-W`.
- Supports pty/shell, exec, subsystem command beginning with `#`, raw terminal mode, window-change notes, and `-X` mux passthrough.

Important risks:
- This client intentionally supports a narrow algorithm set: Curve25519, RSA SHA-256 host key/signature, Chacha20-Poly1305, no compression.
- Several fatal paths abort the process on malformed protocol input.
- A likely typo sets `recv.chan = send.win = 0` where `send.chan` was probably intended, though later channel confirmation overwrites channel ids for normal operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sshfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sshfs.c

`sshfs.c` implements a Plan 9 9P filesystem backed by SFTP v3 over an SSH subprocess or supplied stdin/stdout.

Architecture:
- Defines SFTP v3 packet types, open flags, attribute flags, and status codes.
- `SFid` stores remote path, SFTP handle, qid, and buffered directory entries per 9P fid.
- `SReq` wraps queued 9P requests and close-handle work.
- Request IDs are allocated from a bounded `MAXREQID` table; `sendproc` serializes queued SFTP writes, while `recvproc` matches replies back to pending requests.

Major behavior:
- `sshfsattach` maps attach names to root-relative, absolute, or home-relative paths.
- `sshfswalk` computes path candidates and issues remote `STAT`.
- `sendproc` maps 9P attach/walk/open/create/read/write/stat/wstat/remove to SFTP `STAT`, `OPEN`, `OPENDIR`, `READDIR`, `READ`, `WRITE`, `SETSTAT`, `RENAME`, `REMOVE`, and `RMDIR`.
- `recvproc` translates SFTP `STATUS`, `HANDLE`, `DATA`, `NAME`, and `ATTRS` into 9P responses.
- Directory reads buffer `Dir` records, skip `.` and `..`, and synthesize stable qid paths by SHA-1 hashing remote path strings.
- `readfile` fetches `/etc/passwd` and `/etc/group`-style files for uid/gid name maps.

Mount/startup:
- `threadmain` supports read-only mode, debug, post-only `-p`, command mode `-c`, service/mount options, uid/gid map files, and root path.
- Normally spawns `/bin/ssh ... #sftp`; `-p` uses existing fds.

Risks:
- SFTP v3 has weaker metadata semantics than 9P; qids are synthesized and may not track remote file identity across rename/recreate.
- `dir2attrib` notes deliberate spec violation for `-1` uid/gid “don’t change” behavior used by OpenSSH.
- The request-id limit bounds concurrency to 32 outstanding SFTP operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sshfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sshnet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sshnet.c

`sshnet.c` exposes a remote SSH TCP forwarding session as a Plan 9 `/net`-style filesystem.

Filesystem model:
- Serves root entries `cs` and `tcp`.
- Under `tcp`, exposes `clone` and per-client numbered directories.
- Per-client files include `ctl`, `data`, `local`, `remote`, `status`, and `listen`.
- Qid path encodes entry type and client number with `PATH`, `TYPE`, and `NUM`.

Client/protocol state:
- `Client` tracks local/remote endpoints, state (`Closed`, `Dialing`, `Listen`, `Established`, `Teardown`, `Finished`), SSH channel ids, windows, packet limits, queued 9P read/write requests, and queued incoming data messages.
- `Msg` is a bounded SSH packet/message buffer.
- `pack`/`unpack` encode SSH channel/global request messages.

Operations:
- `ctlwrite connect host!port` opens SSH `direct-tcpip`.
- `ctlwrite announce host!port` sends `tcpip-forward`; `listen` waits for incoming `forwarded-tcpip`.
- `cswrite` translates `tcp!host!service` into `/net/tcp/clone host!port`, using `/lib/ndb/common`; `!`-prefixed writes delegate to a real `/net/cs`.
- `dataread` and `datawrite` bridge 9P reads/writes to SSH channel data with window accounting.
- `handlemsg` handles SSH channel open confirmation/failure, remote open, data, window adjust, EOF, and close.

Startup:
- Spawns `/bin/ssh -X ...`, opens a dummy session channel to confirm the mux is live, then posts/mounts the 9P service.

Risks:
- Single event loop serializes fs requests and SSH messages, simplifying state but making blocking mistakes costly.
- Flow control depends on correct send/receive window bookkeeping.
- Only TCP forwarding semantics are represented; unsupported channel open types are rejected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sshnet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/stats.c

`stats.c` is a graphical Plan 9 system monitor. It displays scrolling graphs for one or more machines, reading local or imported `/dev` and `/net` statistics.

Data model:
- `Graph` stores color, rectangle, data history, label, value callback, owning `Machine`, overflow state, and high-water mark.
- `Machine` stores system name, process info, fds for `dev/sysstat`, `dev/swap`, ethernet stats, battery, temperature, previous/current counters, and a read buffer.

Metrics:
- Memory, swap, reclaim, kernel malloc, draw memory from `/dev/swap`.
- Context switches, interrupts, syscalls, faults, TLB faults/purges, load, idle, in-interrupt from `/dev/sysstat`.
- Ethernet in/out/errors/overflows from `/net/ether*/stats`.
- Battery and CPU temperature from several possible device paths.

Rendering:
- Initializes a small palette in `colinit`.
- `resize` lays out a grid of machines by graphs, titles columns, allocates history arrays, draws labels, and redraws existing data.
- `update1` scrolls graph image left, draws the newest datum, and handles overflow labels/high-water rescaling.
- Optional log scale and y-axis labels are supported.

Remote handling:
- `initmach` imports remote roots with `rimport machine / /n/<name>/` when the target name differs from `$sysname`.
- A supervisor process restarts per-machine worker processes when they exit with `restart`.

UI:
- Button 3 menu toggles graphs between add/drop.
- Keyboard `q` or Del exits.

Risks:
- Parser logic assumes current textual formats of Plan 9 stats files.
- Remote import failures intentionally exit with `restart`.
- Drawing and sampling share memory via `rfork(RFMEM)` and use display locks around UI access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/strings.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/strings.c

`strings.c` implements a Unicode-aware `strings` utility.

Behavior:
- Usage: `strings [-m min] [file...]`.
- Default minimum span is 6 printable runes.
- Reads from stdin when no files are supplied.
- For multiple files, prints a `filename:` header before each file’s strings.
- Uses `Bgetrune` to scan runes rather than raw bytes.
- Once a printable run reaches `minspan`, prints the byte-ish `Boffset(&fin)-minspan` offset followed by the accumulated string, then streams further printable runes until a non-printable rune terminates the string.

Printability:
- `isprint` rejects `Runeerror`.
- Accepts ASCII space through `~` and runes above `0xA0`.

Risks:
- Offset calculation subtracts rune count, not encoded byte length, so offsets for non-ASCII UTF input may be approximate relative to bytes.
- Function name `isprint` shadows the libc/ctype concept, but signature uses `Rune`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/strip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/strip.c

`strip.c` removes symbol/debug tail data from recognized Plan 9 executable binaries.

Key behavior:
- Usage supports in-place stripping of one or more files, or `-o ofile file` for one output file.
- Uses `crackhdr` from `<mach.h>` to identify executable header and text/data layout.
- Accepts magic values in Plan 9 `_MAGIC` ranges.
- Computes stripped length as `fhdr.datoff + fhdr.datsz`.
- Reads exactly that prefix, zeroes `Exec` fields `syms`, `spsz`, and `pcsz`, then writes it back.
- In-place mode removes the original before recreating it with the original mode.

Error handling:
- `error` formats to stderr without immediate exit; `strip` returns status per file.
- Already stripped files are reported but not treated as fatal in in-place mode.

Risks:
- In-place remove-then-create can lose the original if create/write fails after removal.
- Assumes the executable header begins with `Exec` and that zeroing those fields is correct for recognized formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/strip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sum.c

`sum.c` implements checksum variants compatible with Plan 9 historical `sum`.

Modes:
- Default: 32-bit CRC using `crc_table`.
- `-r`: old research Unix rotating 16-bit sum with 1024-byte block count.
- `-5`: System V-style additive 16-bit sum with 512-byte block count.

Flow:
- `main` selects a `Sumfn`, then processes each file or stdin.
- `sumfile` reads in 8 KiB chunks, accumulates file size and checksum, calls the selected function with `buf == 0` to finalize/print, then appends the file name when present.
- Errors set `exitstr` and continue with remaining files.

Algorithms:
- `sum5` adds bytes and folds high bits into 16 bits at finalization.
- `sumr` rotates right through bit 15 before adding each byte.
- `sum32` updates CRC per byte and, at finalization, incorporates a length-derived four-byte value before printing CRC and size.

Risks:
- Final `sum32` length encoding casts the full `uvlong` size to `int n`, so very large files lose high size bits in the final length mix, matching existing behavior but worth noting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/swap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/swap.c

`swap.c` configures a file as Plan 9 swap backing.

Behavior:
- Usage: `swap file`.
- If the argument is a directory, creates a temporary file named from `$sysname` or `swap` under that directory with `mktemp`.
- If the argument is an existing non-directory, opens it read/write.
- If needed, creates the swap file with `ORDWR|ORCLOSE`, mode `0600`, and marks it `DMTMP|0600`.
- Resolves the path with `fd2path`, stores it in environment variable `swap`, prints it, then writes the file descriptor number to `/dev/swap`.

Integration:
- `/dev/swap` accepts an fd number for the kernel/device swap setup.
- `ORCLOSE` and `DMTMP` make directory-created swap files temporary.

Risks:
- Uses `mktemp`-style name generation, consistent with Plan 9 but traditionally race-prone in other environments.
- Only accepts one argument and exits fatally on most failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/syscall/mktab.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/syscall/mktab.awk

`mktab.awk` generates syscall dispatch metadata for `syscall.c`.

Behavior:
- For each input row, appends the second field as an enum name and emits a `struct Call tab[]` entry indexed by that enum.
- Entry names are lowercased strings and function symbols are also lowercased, cast to `int(*)(...)`.
- The `END` block appends special `READ`, `WRITE`, and `NTAB` enum values plus table entries for libc `read`, `write`, and the terminator `{nil, 0}`.

Output shape:
- Emits an `enum{ ... };`.
- Emits `struct Call tab[] = { ... };`.

Risks:
- Assumes the second input field is a valid enum/function token.
- Generated casts bypass type checking by design so arbitrary syscall signatures can be invoked through a uniform varargs-like call site.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/syscall/mktab.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/syscall/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/syscall/syscall.c

`syscall.c` is a diagnostic command for invoking named system calls directly from the command line.

Key pieces:
- Defines a 1 MiB global `buf` and up to five parsed uintptr arguments.
- Declares syscall wrappers not exposed by libc headers.
- Includes generated `tab.h`, built from `mktab.awk`, mapping names to function pointers.
- `parse` maps arguments beginning with `buf` to the global buffer, parses numeric constants with `strtoull`, or otherwise passes the string pointer.
- `main` locates the syscall name, installs a note handler, calls the function, and reports return value/error.

Options:
- `-o` writes `buf` to stdout after the syscall, using the return value as byte count except for `_ERRSTR`, `ERRSTR`, and `FD2PATH`, where it uses `strlen(buf)`.
- `-s` decodes `buf` as a stat message with `convM2D` and prints `%D`.

Special handling:
- `seek`, `pread`, and `pwrite` use `strtoll` for vlong offset arguments because the generic uintptr path cannot safely represent those call signatures.

Risks:
- Intentionally unsafe: arbitrary syscalls with arbitrary pointers/integers can crash or mutate process/kernel-visible state.
- Buffer output count uses syscall return value and can be invalid if the invoked call does not return a byte count.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/syscall/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tail.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tail.c

`tail.c` implements POSIX-style `tail` plus V10 `-r` reverse mode.

Options/semantics:
- Supports `-n N`, `-c N`, `-f`, `-r`, and old `+-N[bc][fr]` suffix syntax.
- `origin` selects beginning/end, `units` selects characters/lines, and `dir` selects forward/reverse output.
- Default count is 10 lines, or effectively unlimited for reverse mode.
- Rejects incompatible reverse combinations with chars, follow, or beginning-origin.

Implementation:
- Detects seekability with `seek(fd, 0, 2)` and resets to start.
- For non-seekable input from end, `keep` buffers and trims to the desired tail.
- For non-seekable beginning-origin, `skip` discards count then copies.
- For seekable char tails, seeks directly.
- For seekable line tails, `reverse` scans backward by `Bsize` blocks to find line boundaries.
- `-f` repeatedly checks truncation with `dirfstat`, copies new data, and sleeps 5 seconds.

Risks:
- `keep` is documented as quadratic in file length times tail length.
- `count` is `long`, with explicit range checks but still constrained by platform long size.
- Reverse path uses dynamic buffers and manual line-boundary logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/32vfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/32vfs.c

`32vfs.c` is a `tapefs` backend for VAX 32V Unix filesystems, also noting pre-FFS Berkeley compatibility.

Format support:
- Disk inode has 13 three-byte block addresses, 16-bit ids/mode, 32-bit size and times.
- Directory entries are 2-byte inode plus 14-byte name.
- Default block size is 512; `-b 1024` supports 4.1BSD-style block size.

Backend callbacks:
- `populate` opens the image, reads root inode 2, and initializes root `ram`.
- `popdir` lazily reads directory entries and creates child `Ram` nodes with `popfile`.
- `doread` maps file offsets through logical block numbers and static block buffer.
- `iget` reads an inode and converts it into `Fileinf`.
- `bmap` handles direct blocks and singly indirect blocks only.
- Write/truncate/create callbacks are no-ops; `dopermw` denies writes.

Risks:
- Explicitly lacks deeper indirect block support.
- Minimal sanity checking; bad images can trigger fatal reads or odd metadata.
- Uses static read buffer, so concurrent reads would not be reentrant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/32vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/cpiofs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/cpiofs.c

`cpiofs.c` is a read-only `tapefs` backend for several cpio archive variants.

Supported headers:
- Binary PWB 1.1 magic `0xc7 0x71`.
- ASCII `070707` sysiii-style octal headers.
- ASCII `070701` newc hex headers.

Parsing:
- Low-level readers `egetc`, `rd16le`, `rd3211`, `rdasc`, and `rdascx`.
- Header readers populate `Fileinf` with mode, uid/gid, mtime, size, and a static name buffer.
- `rdmagic` detects the header type and rejects mixed header formats in one archive.
- `populate` scans until `TRAILER!!!`, strips leading slashes, normalizes mode to directory/file/symlink/other, records file data offset, inserts into the `Ram` tree, and skips padded file contents.

Runtime:
- `doread` seeks to `r->addr + off` and reads into a static `dblock` buffer.
- Directories are fully populated during `populate`; `popdir` is a no-op.
- Writes are denied.

Risks:
- Header name buffers are limited to 256 bytes, matching historical implementation notes.
- Alignment handling differs by header flavor and is fatal on malformed archives.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/cpiofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/fs.c

`fs.c` is the common 9P server core for `tapefs` archive/filesystem backends.

Responsibilities:
- Parses generic options for mountpoint, passwd/group maps, verbosity, old/new tap time handling, and block size.
- Creates the root `Ram`, calls backend `populate`, then forks an IO process and mounts a pipe-backed 9P service at `/n/tapefs` by default.
- Implements 9P handlers for version, auth, attach, walk, open, create, read, write, clunk, remove, stat, and wstat.
- Dispatches requests through `fcalls[]` and `io`, using `convM2S`/`convS2M`.

Semantics:
- Authentication is not required.
- Create/remove/wstat are denied by default.
- `perm` allows all non-write permissions and denies writes globally.
- Directory reads lazily call backend `popdir` if not replete and encode child `Ram` nodes with `ramstat`.
- File reads call backend `doread`; writes call backend `dowrite` only if `dopermw` permits.

Important structures:
- `Fid` tracks 9P fid state and current `Ram`.
- `Ram` represents in-memory tree nodes populated by backend adapters.

Risks:
- Manual fid reuse has a likely bug: `newfid` finds reusable `ff` but still allocates a new fid because it does not return after reinitializing `ff`.
- `blocksize` is declared twice in this file.
- The server is mostly read-only by policy; backend write hooks are present but unused for these adapters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tapefs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tapefs.h

`tapefs.h` defines the shared ABI between the common `tapefs` 9P server and format-specific backends.

Contents:
- Endian helpers: little-endian `g2byte`, `g3byte`, `g4byte`; big-endian `b4byte`, `b8byte`.
- Common constants: open permission mask `OPERM` and max IO buffer `Maxbuf`.
- `Fid`: busy/open/remove-on-close state, fid number, user, current `Ram`.
- `Ram`: in-memory filesystem node with tree links, qid, mode, name, times, owner/group, archive address, data pointer, and size.
- Permission bit constants used by `perm`.
- `Idmap` maps numeric ids to names.
- `Fileinf` is the backend-neutral metadata record used to populate `Ram` nodes.

Externals/prototypes:
- Shared globals: root `ram`, current `user`, uid/gid maps, lazy directory flag `replete`, `blocksize`, and global qid path counter.
- Backend-required functions: `populate`, `dotrunc`, `docreate`, `doread`, `dowrite`, `dopermw`, `popdir`.
- Common helpers: allocation, id mapping, `poppath`, `popfile`, and lookup.

Risks:
- Backend interface assumes static/simple data lifetimes for `Fileinf` fields.
- `Ram.data` is untyped and backend-specific, so misuse is unchecked by the compiler.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tapefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tapfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tapfs.c

`tapfs.c` is a read-only `tapefs` backend for old `tap` tape archives.

Format:
- Reads a fixed directory area of 192 entries.
- Each entry includes 32-byte name, one-byte mode, one-byte uid, two-byte size, four-byte timestamp, two-byte tape address, and checksum.
- Starts scanning at `dir[8]`, matching historical layout.

Behavior:
- `populate` opens the image, reads the directory, verifies each entry checksum, skips empty/zero-address entries, strips leading slash, converts metadata to `Fileinf`, and inserts with `poppath`.
- `cvtime` converts old tap timestamps; unless `newtap` is set, it divides by 60 and adds a three-year offset.
- `doread` seeks to `512 * r->addr + off` and reads into a static buffer.
- Directory population is eager; `popdir` is a no-op.
- Writes/truncates/creates are no-ops and `dopermw` denies writes.

Risks:
- Directory entry names are used directly from the on-disk directory buffer.
- Bad checksum entries are reported and skipped, not fatal.
- Static read buffer is not reentrant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tapfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tarfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tarfs.c

`tarfs.c` is a read-only `tapefs` backend for tar archives.

Format support:
- Handles 512-byte tar headers, old-style names, POSIX ustar prefix/name, GNU long-name records, directory flags, symlink/hardlink flags, and big binary size marker `0x80`.
- `tarname` reconstructs full ustar paths.
- `checksum` validates each header by treating checksum bytes as spaces.

Population:
- `populate` scans archive blocks, computes metadata, normalizes unsafe paths by stripping leading `/`, `cleanname`, and removing leading `../`.
- Directories are detected by tar linkflag, mode, or trailing `/`.
- Link records are skipped as zero-sized entries.
- GNU long-name records set `nextname` for the following real record.
- Accepted entries are inserted via `poppath`.

Reads:
- `doread` seeks to `512 * r->addr + off`, reads with `readn`, and zero-fills short reads.
- Directories are eager; `popdir` is a no-op.
- Writes are denied.

Risks:
- Does not materialize symlink targets; links are effectively skipped/zero-sized.
- Only a subset of modern tar extensions is supported compared with `cmd/tar.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tarfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tpfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tpfs.c

`tpfs.c` is a read-only `tapefs` backend for old `tp` tape archives.

Format:
- Directory array contains 496 entries plus 8 leading reserved entries.
- Entry fields include 32-byte name, two-byte mode, uid, gid, three-byte size, four-byte modified time, two-byte address, and checksum.
- The code treats DECtape and magtape similarly by scanning all entries and ignoring bad checksums.

Behavior:
- `populate` opens the image, reads the directory, counts bad/good checksums, skips empty/zero-address entries, strips leading `/`, fills `Fileinf`, and inserts entries with `poppath`.
- Prints checksum summary to stderr.
- `doread` seeks to `512 * r->addr + off` and reads into a static buffer.
- Directory population is eager; writes are denied.

Risks:
- Mode uses only `tpp->mode[0] & 0777`, ignoring the second mode byte.
- Static read buffer and minimal validation match the historical/simple backend style.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/tpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/util.c

`util.c` provides shared helper routines for `tapefs` backends.

Functions:
- `getpass` parses passwd/group-style files into a dynamically grown `Idmap` array using colon-delimited fields, storing field 0 as name and field 2 as numeric id.
- `mapid` maps numeric ids through an `Idmap`, falling back to decimal string.
- `poppath` inserts a `Fileinf` path into the `Ram` tree, recursively creating parent directories when path components contain `/`, handling trailing slash as directory, resolving `.` to root, and updating existing entries when `new` is true.
- `popfile` allocates and links a `Ram` node under a directory.
- `lookup` finds an existing active child by name.

Behavioral notes:
- `poppath` forces at least user-read bit on modes.
- If an existing node changes file-vs-directory type, it warns and ignores the replacement.
- Owner/group names are derived with `mapid`.

Risks:
- `getpass` uses `strdup` directly for names while other allocation uses tapefs helpers.
- Path insertion mutates `fi.name` while preserving a duplicate for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/v10fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/v10fs.c

`v10fs.c` is a `tapefs` backend for 10th Edition Unix 4K filesystems.

Format:
- Uses 4096-byte blocks.
- Disk inode resembles 32V with 13 three-byte addresses and 14-byte directory names.
- Root inode is 2; superblock offset constant is 1.
- Captures image length with `dirfstat` to guard against reads past EOF.

Behavior:
- `populate` opens the image, records length, reads root inode, and seeds root `Ram`.
- `popdir` lazily reads directory entries, skips `.`/`..` and inode 0, converts child inodes through `iget`, and inserts with `popfile`.
- `doread` maps offset to logical blocks and fills a static buffer.
- `iget` reads inode block and converts flags, size, addresses, uid/gid, and mtime.
- `getblk` maps logical block to disk block and zero-fills holes or out-of-image reads.
- `bmap` handles direct and singly indirect blocks.

Risks:
- Only singly indirect mapping is implemented.
- Static read buffer is not reentrant.
- Bad inode reads are fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/v10fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/v6fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/v6fs.c

`v6fs.c` is a `tapefs` backend for old Unix V6 and earlier PDP-11 filesystems.

Format:
- 512-byte blocks.
- Root inode is 1.
- Inode has 8 two-byte addresses, byte uid/gid, split high/low size, and PDP-11-order timestamps.
- Directory entries are two-byte inode plus 14-byte name.
- Uses the V6 large-file flag indirectly by size: if `r->ndata <= V6NADDR * BLSIZE`, direct addresses are used; otherwise indirect blocks are used.

Behavior:
- `populate` opens the image and seeds root metadata from `iget(V6ROOT)`.
- `popdir` lazily enumerates directory entries and inserts child `Ram` nodes.
- `doread` reads mapped blocks into a static buffer.
- `iget` converts V6 inode fields into `Fileinf`.
- `bmap` maps small direct files or singly indirect large files.
- Write callbacks are denied/no-op.

Risks:
- Large-file detection by size is a heuristic.
- No double-indirect support.
- Minimal image validation and static buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/v6fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/zip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/zip.h

`zip.h` defines ZIP constants and the `ZipHead` metadata structure for `zipfs.c`.

Contents:
- Local, central, and end-central-directory magic numbers.
- General-purpose flags such as encryption, data trailer, and patched compression.
- Compression method constant for deflate.
- CRC polynomial.
- Internal/external attribute constants and creator OS ids.
- Header size constants for local, trailer, central, and end-central records.

`ZipHead` fields:
- Creator/extractor OS and version.
- Flags, method, DOS mod time/date.
- CRC, compressed size, uncompressed size.
- Internal/external attributes.
- Local header offset.
- Allocated file name.

Use:
- `zipfs.c` fills `ZipHead` from central and local headers, then uses it to populate `Fileinf` and drive reads/decompression.

Risks:
- ZIP64 is not represented.
- Only legacy 32-bit size/offset fields are modeled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/zip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/zipfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/zipfs.c

`zipfs.c` is a read-only `tapefs` backend for ZIP archives.

Population:
- Initializes CRC table and flate support.
- Opens archive with `Biobuf`.
- `findCDir` scans backward up to 1024 bytes for end-central-directory, then seeks to the central directory.
- `cheader` reads each central directory entry into `ZipHead`.
- `populate` converts central entries into `Fileinf`, deriving directories from zero-size stored entries ending in `/`, lowercasing names, setting readonly mode from DOS attributes, and converting MS-DOS timestamps.

Reads:
- `doread` seeks to the local header offset, reads local `header`, then:
  - method 0: seeks into stored data and reads directly.
  - method 8: inflates the whole file into a cached buffer when qid changes, checks CRC, optionally munges CRLF text, then copies the requested slice.
- `High64` bit in `addr` marks text-file handling.
- `blwrite` is the flate output callback into a bounded block.

Limitations/risks:
- Unsupported methods fatal.
- No ZIP64, encryption, multi-disk, or large comment search beyond 1024 bytes.
- Deflated file cache is one-file-at-a-time and static.
- `trailer` is defined but unused in normal central-directory-driven reads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tapefs/zipfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tar.c

`tar.c` implements Plan 9 `tar`: create/append/list/extract archives with ustar, selected GNU/PAX extensions, compression filters, and Plan 9 metadata handling.

Major features:
- Modes: `c`, `r`, `t`, `x`; archive file via `-f`; compression via `-z` or suffix detection.
- Optional resync on bad checksums, ignore read errors, keep existing files, relative path protection, set extracted times/metadata, POSIX toggle, uid/gid override.
- Compression uses child filters (`gzip`, `compress`, `bzip2` families) through `push`/`pushclose`.

Archive reading:
- Block buffering with configurable `nblock` based on `IOUNIT`.
- `readhdrblk` validates header checksum and supports resync.
- `readhdr` handles PAX per-file headers, PAX global headers, GNU long-name headers, and standard headers.
- `parsepax` recognizes `path`, `linkpath`, `uname`, `gname`, `atime`, `mtime`, and `size`.
- Supports GNU/base-256 large size encoding.

Archive writing:
- `addtoar` stats files, emits PAX path headers for long names, writes headers through `mkhdr`, recursively descends directories, and writes file data in tar blocks.
- `replace` creates or appends archives and writes two zero end markers.

Extraction/listing:
- `match` selects requested prefixes.
- `extract1` protects absolute paths and Plan 9 `#` names when relative mode is enabled, creates files/dirs, skips unsupported links/fifos, copies data, and optionally writes metadata.
- Table mode prints either plain names or verbose `%M` mode/size/time/name.

Risks:
- Link and FIFO extraction is not implemented.
- Directory metadata is applied immediately, not after all children.
- `parsehdr` appears to fill `hdr->gid` from `bp->uname` instead of `bp->gname`, likely a bug.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t.h

`t.h` is the shared header for the Plan 9 `tbl` troff preprocessor implementation.

Contents:
- Includes `<u.h>`, `<libc.h>`, `<bio.h>`, and `<ctype.h>`.
- Defines table sizing constants: max lines, header/spec rows, columns, character storage, line length, repeats, and column width string length.
- Declares global table parser/rendering state: row/column counts, styles, fonts, sizes, vertical sizes, flags, lines, table cells, storage arenas, active input/output buffers, file/line tracking, and formatting flags.
- Defines style/flag constants such as `ZEROW`, `HALFUP`, `CTOP`, `CDOWN`, column alignment constants, register numbers, and line-position constants.
- Declares `struct colstr` for split table cell storage.
- Provides prototypes for all tbl compilation units from `t1.c` through later helper files (`t8.c`, `t9.c`, `tb.c`, etc.).

Role:
- This header is the cross-file contract for a highly global, historical C program. Most state is shared mutable global data rather than passed explicitly.

Risks:
- Many extern globals and macro constants make ordering and memory ownership fragile.
- `MAXCOL` warning notes it must stay coordinated with register allocation in `tr.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t0.c

`t0.c` defines storage for the global variables declared in `t.h`.

Key state initialized here:
- Formatting flags: expand, center, box/doublebox/allbox, tab character, line size, delimiters, even columns, text/left/right flags.
- Table storage: `table`, `stynum`, `fullbot`, `instead`, `linestop`, style/font/size/line arrays, column spacing/usage arrays, and numeric split helpers.
- Input/output state: `leftover`, `last`, `ifile`, `iline`, `linstart`, `tabin`, and `tabout`.
- Troff register/name state: `texname`, `texct`, and `texstr`.

Role:
- No functions are defined; this is the allocation/definition unit required so other tbl modules can use `extern` declarations from `t.h`.

Risks:
- Global state is reset only by higher-level flow; stale values between tables are possible if cleanup paths are missed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t1.c

`t1.c` contains main control and input-file switching for `tbl`.

Flow:
- `main` exits with `"error"` if `tbl` returns nonzero.
- `tbl` initializes `tabout`, sets input, copies ordinary lines to output, and invokes `tableput` when a line begins with `.TS`.
- `setinp` prepares the first input file or stdin.
- `swapin` processes argument list entries, handling macro shorthands:
  - `-ms` maps to `/sys/lib/tmac/tmac.s`
  - `-mm` maps to `/sys/lib/tmac/tmac.m`
  - `-TX` sets `pr1403`
  - `-` means stdin
- Emits `.ds f.` and `.lf` directives when switching inputs.

Integration:
- Uses `gets1`, `prefix`, `match`, `getcore`, and `error` from other tbl modules.
- The comment notes file closing is done by the GCOS troff preprocessor, reflecting historical lineage.

Risks:
- Argument parsing is old-style and only loosely validates flags.
- `swapin` mutates `sargv` entries for macro expansion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t2.c

`t2.c` provides `tableput`, the top-level processing pipeline for one `.TS` table.

Pipeline:
1. Save current input line and fill state.
2. Handle diversions and field-cleanup setup.
3. `getcomm` parses table-wide options.
4. `getspec` parses column/row format specification.
5. `gettbl` reads table data.
6. `getstop`, `checkuse`, and `choochar` prepare rendering details.
7. `maktab` computes tab stops.
8. `runout` emits troff output.
9. Release memory and restore saved fill/line state.
10. `freearr` releases spec arrays and `restline` restores remaining input.

Role:
- This file is glue only; it defines the exact sequencing contract among the tbl phases.

Risks:
- Correct cleanup depends on every phase completing normally; historical code uses `error` rather than structured unwinding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t3.c

`t3.c` parses table-wide option commands immediately after `.TS`.

Supported options include:
- `expand`, `center`, `box`, `allbox`, `doublebox`
- aliases `frame`, `doubleframe`
- `tab(...)`
- `linesize(...)`
- `delim(...)`
- Uppercase variants for all named options.

Behavior:
- `getcomm` resets all option targets, resets table character naming, default tab, emits the saved point-size register, and reads the next line.
- If the line lacks `;`, it is pushed back with `backrest` and treated as part of the table spec.
- Otherwise it scans options up to `;`, validates spelling, parses optional parenthesized arguments, and updates globals.
- `backrest` pushes a string plus newline back into the tbl input stream with `un1getc`.

Risks:
- Parsing is permissive and character-by-character; malformed parenthesized options can run until `)`.
- Uses global option storage and pushback rather than returning a parsed structure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t4.c

`t4.c` reads and allocates the table format specification.

Major functions:
- `getspec` determines column count with `findcol`, allocates arrays via `garray`, initializes defaults, calls `readspec`, and removes old right-edge registers.
- `readspec` parses the tbl format language: column styles, spans, horizontal rules, font/point/vertical size modifiers, widths, even columns, zero-width, half-up, top/down flags, spacing, and vertical bars.
- `findcol` peeks ahead to count format columns while respecting parenthesized arguments, then pushes the line back.
- `garray` allocates all per-column/per-format arrays.
- `getcore` wraps `calloc`.
- `freearr` frees allocated arrays, including decrementing `sep` because it was intentionally incremented to make `sep[-1]` valid.

Notable validation:
- First column cannot be span type.
- First row cannot contain vertical span.
- Too many columns/spec lines are fatal.
- `.T&` cannot widen the table beyond a small allowance.

Risks:
- Heavy reliance on global mutable arrays and input pushback.
- `sep[-1]` trick is intentional but fragile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t5.c

`t5.c` reads table data rows after the format specification.

Behavior:
- `gettbl` allocates character storage, then reads lines until `.TE`, `.TC`, `.T&`, storage exhaustion, or max rows.
- Troff control lines beginning with `.` followed by non-digit are stored in `instead`.
- Full-width horizontal rules `_` and `=` are recorded in `fullbot`.
- For each row, allocates `struct colstr` cells, splits fields by the configured tab character, handles text blocks beginning `T{`, and converts numeric/alpha columns through `maknew` or split `rcol` handling.
- Column spans consume following `s` columns with empty cells.
- `permute` moves vertically spanned content to the bottom of the span and inserts `\^` markers above.

Helpers:
- `nodata` detects format rows with no data-bearing columns.
- `oneh` identifies rows made entirely of one horizontal-rule style.
- `vspand`/`vspen` detect vertical span markers.

Risks:
- Uses fixed-size shared character storage and resets when nearly full.
- Text-block and span handling depends on helper modules outside this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t6.c

`t6.c` computes troff number registers for table column widths and tab stops.

Core function:
- `maktab` iterates columns and rows, measuring cell content with troff `\w` expressions, updating right-edge and middle registers, handling numeric split columns, alpha cases, text blocks, zero-width cells, spans, explicit column widths, even-width columns, expand mode, left/right borders, and total table width `TW`.

Supporting functions:
- `wide` emits a width expression for literal text, applying font and size overrides when present, or references an existing text-block register.
- `filler` identifies filler register references beginning `\R`.

Important behavior:
- Runs two passes for normal text and text-block registers.
- Handles `n` and `a` styles with separate left/right numeric parts.
- Adjusts spanned columns by distributing excess width across covered columns.
- Emits a warning if table width exceeds a troff page threshold.

Risks:
- Generates troff source directly; correctness depends on exact register names from `reg`.
- Integer register arithmetic tries to avoid overflow but remains historically constrained.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t7.c

`t7.c` emits the main troff control stream for a parsed table.

Functions:
- `runout` emits preamble setup, optional centering indentation, field character setup, tail macro definition, each table row via `putline`, continuation handling via `yetmore`, cleanup, and final `T#` macro invocation.
- `runtabs` emits `.ta` tab stops for a given format/data row, respecting spans and numeric split columns.
- `ifline` detects one-character horizontal rule cells `_` or `=`.
- `need` emits a `.ne` request estimating required vertical space from text and horizontal-rule rows.
- `deftail` defines troff macro `T#` to draw bottom borders and vertical lines at table end, including box/doublebox/right-hand rules.

Integration:
- Relies on later helper files for row output, horizontal/vertical line drawing, span calculations, and continuation.
- Uses global table arrays and register names.

Risks:
- Output is tightly coupled to troff macro/register semantics.
- Box/line rendering depends on saved line-stop state from other modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t7.c -->