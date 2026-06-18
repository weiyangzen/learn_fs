# Group Research: group_1517_plan9_sources_os_plan9_plan9_sys_src_cmd_disk_kfs_9p1_c_sources_os__dd64421b8ff5

Scope verified against `Docs/research_subset_a.md`: all files are under the included `sources/os/plan9/plan9` source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.c

This is the 9P1 request implementation for KFS. It provides old-protocol handlers for session, attach, clone, walk, open, create, read, write, clunk, remove, stat, wstat, flush, and the `clwalk` macro operation.

Key behavior:
- Maintains fid state through `File` objects from `filep`, including current dentry address/slot, qid, open mode, walk path, uid, and optional exclusive lock.
- Uses `mkqid`, `mkqidcmp`, `mkqid9p1`, and `mkqid9p2` to bridge KFS on-disk `Qid9p1` values and Plan 9 `Qid` values, including special “dump fs” fake qids for top dump directories.
- Enforces permissions through `iaccess`, `ingroup`, `leadgroup`, `writeallow`, `wstatallow`, `writegroup`, `isro`, and console-channel bypasses.
- Implements directory traversal by scanning `Dentry` arrays in directory data blocks via `dnodebuf`, preserving parent chains in `Wpath`.
- Implements file I/O over direct, single-indirect, and double-indirect blocks through `dnodebuf`, `dnodebuf1`, `balloc`, `bfree`, and `dtrunc`.

Important dependencies:
- Wire conversion: `9p1lib.c`, `9p1.h`.
- Metadata and block layout: `portdat.h`, `dentry.c`, `sub.c`, `iobuf.c`.
- Auth: `auth.c` via `authorize`.
- Dispatch entry: `serve9p1`.

Notable details:
- `f_flush` temporarily drops and reacquires the channel reference lock to serialize with in-flight requests.
- `f_clunk` handles remove-on-close and releases `Tlock` state.
- `doremove` is shared with 9P2 and console code; it verifies parent write permission, refuses non-empty directories, truncates contents, then clears the dentry.
- `f_wstat` supports rename, chmod, chown, chgrp, and time changes with old 9P1 stat encoding.
- The final `serve9p1` loop reads messages, dispatches through `call9p1`, converts errors to `Rerror9p1`, and writes replies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.h

This header defines the old 9P1 wire-facing structures and message numbers used by KFS.

Key contents:
- `DIRREC`, `ERRREC`, and `MAXMSG` fixed-size record constants.
- `Oldfcall`, a packed in-memory representation of all old 9P1 message variants using overlapping anonymous structs.
- Message type enum from `Tnop9p1` through `Tattach9p1`, plus `MAXSYSCALL`.
- Prototypes for 9P1 conversion and dispatch helpers: `convD2M9p1`, `convM2D9p1`, `convM2S9p1`, `convS2M9p1`, `fcall9p1`, `authorize`.
- Global dispatch vector `call9p1` and NVRAM auth state `nvr`.

Role in the system:
- Shared by network serving (`9p1.c`), console self-calls (`console.c`), formatting (`ofcallfmt.c`), auth (`auth.c`), and conversion (`9p1lib.c`).
- The fixed-size names, stat records, and 32-bit qid fields constrain compatibility with the older protocol.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p12.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p12.c

This file is the protocol sniffer and launcher for KFS service channels. It reads the first incoming message, decides whether it is 9P1 or 9P2000, and starts the appropriate server loop.

Key behavior:
- `readmsg` reads enough header bytes to distinguish old 9P1 message forms from 9P2000 length-prefixed messages.
- For 9P1 it assumes message boundaries and reads the rest with one `read`.
- For 9P2000 it reads the full length-prefixed frame.
- `startserveproc` forks additional worker processes sharing memory.
- `serve` chooses `serve9p1` or `serve9p2`, starts `conf.nserve - 1` sibling server processes, runs one server loop in the current process, then waits for workers.

Dependencies:
- Calls `serve9p1` from `9p1.c` and `serve9p2` from `9p2.c`.
- Uses `Chan` locks for serialized message reads.
- Uses `conf.nserve` from global KFS configuration.

Notable details:
- The protocol detector has old-protocol special cases for message types 50-87 and `Tattach`.
- All workers share the same `Chan`, so read and write serialization depends on the per-channel locks used by the individual protocol servers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p12.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1lib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1lib.c

This file implements 9P1 serialization/deserialization and old directory stat conversion.

Key behavior:
- `convS2M9p1` converts an `Oldfcall` into old 9P1 wire bytes.
- `convM2S9p1` parses wire bytes into `Oldfcall`, including in-buffer data pointers for read/write payloads.
- `convD2M9p1` converts a KFS `Dentry` into a fixed 116-byte old stat record.
- `convM2D9p1` parses the old stat record back into `Dentry`.
- `fakeqid9p1` mirrors the dump-fs qid workaround used in `9p1.c`.

Important details:
- Uses little-endian 16-bit and 32-bit field macros matching old Plan 9 wire format.
- Old stat records encode uid/gid as fixed `NAMELEN` strings and length as low/high 32-bit words, though KFS `Dentry.size` is a `long`.
- Mode conversion maps between old create/stat flags `PDIR`, `PAPND`, `PLOCK` and dentry flags `DDIR`, `DAPND`, `DLOCK`.

Dependencies:
- Requires `uidtostr` and `strtouid` from `uid.c`.
- Uses `Dentry`, `Qid9p1`, and mode constants from `portdat.h`/`dat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p2.c

This is the KFS 9P2000 server implementation. It mirrors the old 9P1 filesystem operations while using modern `Fcall`, variable message sizes, auth fids, and 9P2000 directory/stat encoding.

Key behavior:
- `fsversion` negotiates `VERSION9P` and caps message size at `MAXDAT+128`.
- `fsauth`, `authread`, and `authwrite` implement factotum-backed 9P auth fids.
- `fsattach` validates auth and attaches a fid to a named KFS filesystem root.
- `fswalk`, `walkname`, and `clone` implement multi-element 9P2000 walk semantics, including partial walk success.
- `fsopen`, `fscreate`, `fsread`, `fswrite`, `fsclunk`, `fsremove`, `fsstat`, and `fswstat` implement normal file operations.
- `serve9p2` receives length-prefixed 9P2000 messages, dispatches by type, converts errors to `Rerror`, and sends replies.

Important dependencies:
- Shared metadata operations: `mkqid`, `mkqidcmp`, `dnodebuf`, `dnodebuf1`, `dtrunc`, `doremove`, `accessdir`.
- Auth state extends `File` with `AuthRpc *rpc` and `cuid`.
- Uses standard Plan 9 `convM2S`, `convS2M`, `convD2M`, `convM2D`, and `fcallfmt`.

Notable details:
- Directory reads cache scan position in `File.doffset`, `dslot`, and `dvers`.
- `mkqid9p1` and `mkqid9p2` bridge old on-disk qids with 9P2000 qid types.
- `fswstat` is stricter than 9P1 about qid type/mode consistency and refuses length changes.
- There is a likely typo in `fswstat`: the rename check compares `strcmp(xd.name, "..")` even though the 9P2000 stat path uses `dir.name`; `xd` is otherwise unused there.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/all.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/all.h

This is the umbrella include for KFS source files.

Contents:
- Includes Plan 9 base headers `u.h` and `libc.h`.
- Includes local `dat.h` and `fns.h`.
- Includes system protocol/auth headers `<fcall.h>`, `<auth.h>`, and `<authsrv.h>`.

Role:
- Centralizes the dependency set for KFS implementation files.
- Pulls in both local disk/server data structures and Plan 9 9P/auth APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/auth.c

This file implements old 9P1 challenge/response authentication and shared auth policy flags.

Key behavior:
- Defines `allownone`, `nvr`, and `didread`.
- `mkchallenge` lazily reads NVRAM auth data, seeds randomness, fills `Chan.chal`, and resets authenticator replay state.
- `authorize` validates old 9P1 tickets and authenticators using authsrv conversion helpers.
- Allows local console service channels and boot-time `wstatallow`.
- Handles `none` attach policy using `allownone` or prior channel authentication.
- Checks ticket type, authenticator type, challenge match, replay id bitmap, and ticket names.
- On success, rewrites `in->uname` to the server uid and creates the response authenticator in `ou->rauth`.

Dependencies:
- `Chan` challenge/replay fields from `dat.h`.
- `Oldfcall` from `9p1.h`.
- `Nvrsafe`, `Ticket`, `Authenticator`, and conversion routines from auth headers.

Notable detail:
- `Nvrsafe nvr;` appears twice in the file text; in this old Plan 9 build context that may have compiled historically, but in modern C this duplicate definition would be suspect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/chk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/chk.c

This file implements the KFS consistency checker and repair logic used by the `check` console command.

Key behavior:
- `check` takes a `Filsys` and check flags, locks the filesystem, reads the superblock, allocates bitmaps for block and qid tracking, walks from the root, optionally rebuilds the free list, and reports summary counts.
- `fsck` recursively validates dentries, names, qids, direct blocks, indirect blocks, and double-indirect blocks.
- `checkdir` scans directory blocks and recurses into allocated entries.
- `checkindir` validates single-indirect blocks and either recurses into directory data or reads file blocks.
- `ckfreelist` walks the on-disk free list and marks free blocks.
- `mkfreelist` rebuilds the free list from unmarked blocks.
- `xtag` reads a block and validates or repairs its tag depending on flags.
- `amark`, `fmark`, and `qmark` detect out-of-range, duplicate, used, free, and qid conflicts.

Repair flags:
- `Cfree`: rebuild freelist.
- `Ctag`: repair tags.
- `Cream`: zero and retag bad blocks.
- `Cbad`: delete redundant block references.
- `Ctouch`: rewrite touched old blocks.
- `Crdall`, `Cpdir`, `Cpfile`, `Cquiet`: read/print/report modifiers.

Dependencies:
- Relies on `getbuf`, `putbuf`, `checktag`, `settag`, `getdir`, `addfree`, and global block-size variables.
- Uses `cprint` so output goes to the KFS command channel.

Notable detail:
- Uses a fixed-depth dentry scratch allocator with `MAXDEPTH`; overly deep trees are reported and not fully traversed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/con.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/con.c

This file implements the KFS command language served through the `.cmd` service file.

Key behavior:
- `consserve` initializes the console session, attaches the default filesystem, and loads users.
- `cmd_exec` dispatches text commands through the `command[]` table.
- Implements operator commands: `allow`, `allowoff`, `atime`, `cfs`, `chat`, `check`, `clri`, `create`, `halt`, `help`, `listen`, `newuser`, `noneattach`, `nowritegroup`, `remove`, `rename`, `start`, `stats`, `sync`, `user`.
- `cmd_check` translates single-letter options into checker flags and invokes `check`.
- `cmd_create`, `cmd_remove`, `cmd_rename`, and `cmd_clri` use console 9P calls to modify the filesystem.
- `cmd_newuser` appends to `/adm/users` and creates a default home tree.
- `cmd_listen` starts network service, defaulting to `tcp!*!564`.

Parsing helpers:
- `skipbl`, `cname`, `_cname`, `nextelem`, and `number` parse command arguments, names, paths, and numbers.

Dependencies:
- Uses console 9P wrappers from `console.c`.
- Uses old stat conversion from `9p1lib.c`.
- Uses uid/group state from `uid.c`.
- Uses checker from `chk.c`.

Notable detail:
- Some console operations bypass normal user identity by using `cons.uid` and `cons.gid`, explicitly described in comments as a botch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/con.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/console.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/console.c

This file lets internal KFS commands invoke filesystem operations through the same 9P1 handler path used by clients.

Key behavior:
- `fcall9p1` wraps a 9P1 operation with `mainlock` and channel `reflock`, dispatching via `call9p1`.
- Provides wrappers: `con_session`, `con_attach`, `con_clone`, `con_path`, `con_walk`, `con_stat`, `con_wstat`, `con_open`, `con_read`, `con_write`, `con_remove`, `con_create`.
- `con_create` sets `cons.uid` and `cons.gid` before calling `Tcreate9p1`, enabling console-selected ownership.
- Implements `doclri`, `f_clri`, and `con_clri` to clear a directory entry without normal truncation/removal semantics.
- `con_swap` swaps two dentries’ contents while preserving their names, used by cross-directory rename logic in `con.c`.

Dependencies:
- Uses `Oldfcall`, `call9p1`, and 9P1 message constants.
- Calls core metadata helpers `getbuf`, `getdir`, `mkqid`, `freewp`, `freefp`, and `accessdir`.

Notable details:
- Console operations intentionally reuse server code paths, reducing duplicate permission and metadata behavior.
- `clri` is more dangerous than regular remove because it clears a dentry directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/console.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.c

This file defines KFS global variables, default filesystem/device tables, tag names, and error strings.

Key contents:
- Global uid/gid storage, main lock, boot time, lock table, config, console state, active channel, service name, process names, and block-size globals.
- `filesys` default array with one filesystem named `main` on `Devwren`.
- `devnone` sentinel device.
- `devcall` dispatch table mapping `Devwren` to `wren*` operations.
- `tagnames` for block tag diagnostics.
- `errstring` mapping KFS internal error codes to protocol error strings.

Role:
- Central registry for the single-device KFS build.
- Used by nearly every KFS source file via extern declarations in `dat.h`.

Notable details:
- `writeallow`, `wstatallow`, `allownone`, `noatime`, and `writegroup` are declared elsewhere but exposed through `dat.h`.
- Error strings are shared by 9P1, 9P2, console, and command output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.h

This header defines KFS runtime structures layered above the on-disk structures in `portdat.h`.

Key contents:
- Includes `portdat.h`.
- Defines `Chan`, the per-connection state: fd, read/write locks, fid list, flush/ref lock, negotiated msize, auth state, and old 9P1 challenge/replay fields.
- Defines `Cons`, the console state: flags, temporary create uid/gid, argument cursor, console channels, and load/stat filters.
- Defines `Conf`, runtime sizing parameters.
- Defines `Command`, command-table entries.
- Defines `Devcall`, the device method table.
- Defines device and filesystem constants, qid compatibility constants, old create mode flags, fid constants, time macros, and `CHAT`.
- Declares global state from `dat.c` and other modules.

Role:
- Main shared runtime ABI for the KFS server.
- Bridges protocol, console, device, auth, and block-cache code.

Notable detail:
- `CHAT(cp)` ignores its argument and expands to global `chat`, which is why some code can call `CHAT` with non-existent local names after macro expansion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dentry.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dentry.c

This file implements dentry/block mapping helpers for KFS file data and directories.

Key behavior:
- `getdir` returns a `Dentry*` within a directory block by slot.
- `accessdir` updates atime, mtime, qid version, and buffer dirty flags unless read-only or `noatime`.
- `dbufread` is a no-op placeholder for read-ahead.
- `rel2abs` maps a file-relative block number to a disk block through direct, single-indirect, or double-indirect pointers, allocating blocks when a nonzero tag is requested.
- `dnodebuf` returns a locked data block without releasing the parent buffer.
- `dnodebuf1` releases the parent buffer before returning the child block to reduce lock interference.
- `indfetch` reads/allocates indirect entries.
- `dtrunc` frees double-indirect, single-indirect, and direct blocks, clears size, marks the dentry dirty, and updates write metadata.

Dependencies:
- Uses `balloc`, `bfree`, `getbuf`, `putbuf`, `checktag`, and `settag`.
- Depends on block-size globals `BUFSIZE`, `INDPERBUF`, and `INDPERBUF2`.

Notable detail:
- Tags carry qid path identity, so indirect/data block lookups validate both block type and owning qid path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devmulti.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devmulti.c

This file implements a multi-file “wren” block device backend for KFS.

Key behavior:
- Supports up to `MAXWREN` component files.
- `wrenpartinit` opens each backing file, reads stat length using an old stat-buffer parser, checks per-part magic, and establishes `RBUFSIZE`.
- `wreninit` initializes all component files and switches to multi-wren magic if `nwren > 0`.
- `wrenpartream` writes the magic and block size into each component.
- `wrencheck` validates magic, superblock tag, root directory tag, and root allocation.
- `wrensize` sums component block counts.
- `wrenread` and `wrenwrite` map a logical KFS block across component files, skipping the magic block in later parts.

Dependencies:
- Device dispatch from `dat.c`.
- Uses `ialloc`, `panic`, KFS tags, and `Dentry`.

Notable detail:
- This is an older or alternate backend to `devwren.c`; both define similar `wren*` symbols, so builds select one, not both.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devmulti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devwren.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devwren.c

This file implements the normal single-file “wren” block device backend for KFS.

Key behavior:
- `wreninit` opens `wrenfile`, reads the first block, detects KFS magic and block size, records backing file size, and stores the fd.
- `wrenream` writes KFS magic and selected block size to the first block.
- `wrentag` checks the tag trailer at `BUFSIZE`.
- `wrencheck` validates magic, superblock tag, root directory tag, and root allocation.
- `wrensize` reports backing file size divided by `RBUFSIZE`.
- `wrensuper` returns block 1 and `wrenroot` returns block 2.
- `wrenread` and `wrenwrite` seek and transfer exactly one KFS raw block.

Dependencies:
- Uses KFS block sizing and tag layout.
- Device dispatch table in `dat.c` calls these functions for `Devwren`.

Notable details:
- Magic is stored at offset 256 in the first block as `"kfs wren device\n"` followed by block size.
- Read/write failures are printed and returned as nonzero status.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/devwren.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/errno.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/errno.h

This header defines a small enum of kernel-style error identifiers.

Role:
- Provides symbolic names such as `Efidinuse`, `Eperm`, `Eio`, `Enotdir`, `Eisdir`, and mount/device errors.
- It is distinct from KFS protocol error codes in `portdat.h`.

Notable detail:
- The file is not part of the main KFS error-string table in `dat.c`; KFS protocol-facing errors use the `Ebadspc` through `Esystem` enum from `portdat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/fns.h

This header declares KFS top-level functions and device macros.

Key contents:
- Includes `portfns.h`, which declares most filesystem internals.
- Declares startup/config helpers: `chaninit`, `confinit`, `fsinit`, `iobufinit`, `startproc`, `syncproc`, `syncall`.
- Declares console/parser helpers such as `cmd_exec`, `nextelem`, `number`, `skipbl`.
- Declares wren device functions.
- Defines compatibility macros: `localfs`, `devgrow`, `nofree`, `isro`.
- Defines device method dispatch macros: `superaddr`, `getraddr`, `devsize`, `devwrite`, `devread`.

Notable detail:
- `isro(d)` is hardcoded to `0` here, so read-only enforcement hooks exist but this KFS build treats devices as writable unless other policy blocks writes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ialloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ialloc.c

This file defines one allocation helper.

Behavior:
- `ialloc(ulong n)` calls `malloc(n)` and zeroes the allocation with `memset` if successful.
- Returns `nil`/`0` on allocation failure.

Role:
- Used throughout KFS startup and device initialization for zero-initialized global/runtime allocations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/iobuf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/iobuf.c

This file implements the KFS buffer cache.

Key behavior:
- Maintains hash buckets of `Iobuf` entries through `Hiob.link` and per-bucket locks.
- `getbuf` looks up an active block by device/address, moves hits to the front of an LRU ring, locks the buffer, sets requested flags, and reads or initializes on misses.
- On eviction, dirty buffers are written through `devwrite`; reserved buffers are skipped.
- `syncblock` writes at most one dirty block per hash bucket and reports whether work remains.
- `sync` repeatedly calls `syncblock`.
- `putbuf` checks lock state, writes immediate buffers (`Bimm`) synchronously, deactivates `iobuf`, and unlocks.
- `checktag` validates block trailer tag and qid path.
- `settag` writes a block tag and marks the buffer dirty.

Dependencies:
- Device methods from `fns.h`.
- Global stats filters in `cons`.
- Block tag layout from `portdat.h`.

Notable details:
- `Bimm` forces writeback on `putbuf`; this is used for metadata that should become durable quickly.
- `checktag` tolerates an old qid-path bug where the stored path includes `QPDIR`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/main.c

This file is the KFS program entry point and process orchestration layer.

Startup flow:
- Parses options for block size, no-check, filesystem file, multi-wren count, service name, command mode, ream, stdin/stdout service mode, buffer count, and chat.
- Insulates namespace/environment with `rfork`, disables swapping through `/proc`, checks access to `wrenfile`.
- Initializes formatting, allocator locks, service name, service channel, console channel, lock tables, uid/gid tables, and `mainlock`.
- Calls `fsinit`, `iobufinit`, `rootream`, and `superream` as needed.
- Runs console bootstrap commands via `consserve`.
- Marks filesystem not-ok while running via `superok`; optionally runs `check fq` after unclean shutdown.
- Starts `forkserve` and `syncproc`.

Runtime services:
- `syncproc` creates `/srv/<service>.cmd`, periodically flushes dirty blocks, reads operator commands, and updates load filters.
- `netserve` announces a network address and forks a server per accepted connection.
- `chaninit` registers the main `/srv/kfs` service fd.
- `consinit` creates the internal console channel and registers stats filters.
- `fsinit` initializes devices, decides ream/check behavior, computes block-size-dependent constants.
- `iobufinit` sizes and initializes the buffer cache.

Notable details:
- `memsize` estimates memory from `/dev/swap` and uses about one tenth for buffer cache if `-B` is not supplied.
- `fsok` is cleared on startup and restored by `halt`; this lets the next startup detect unclean shutdown.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/misc.c

This file contains small numeric, endian, panic, and output helpers.

Key behavior:
- `famd` and `fdf` implement fixed-point filter arithmetic used by throughput/load stats.
- `belong` reads a big-endian 32-bit value from bytes.
- `panic` formats process context, writes to fd 2, calls `abort`, then exits.
- `cprint` writes formatted console-command output to `cmdfd`.
- `print` redirects formatted output to fd 2 because fd 1 may be used for service mode.

Dependencies:
- Uses global `progname`, `procname`, and `cmdfd`.
- Formatting support comes from Plan 9 `vseprint`/`vfprint`.

Role:
- Shared by diagnostics, command output, and fatal paths across KFS.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ofcallfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ofcallfmt.c

This file implements `%O` formatting for old 9P1 `Oldfcall` messages.

Key behavior:
- `ofcallfmt` switches on the 9P1 message type and formats a human-readable summary with tag, fid, qid, names, modes, counts, errors, or stat data.
- `fdirconv` formats decoded old stat records as dentry-like metadata.
- `dumpsome` prints up to 24 bytes of read/write payload as printable text or hex.

Dependencies:
- Uses `Oldfcall` definitions from `9p1.h`.
- Uses `convM2D9p1` to decode stat buffers.
- Registered by `formatinit` in `sub.c`.

Role:
- Debug/trace support for `chat` mode in 9P1 serving and console dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ofcallfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portdat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portdat.h

This header defines KFS on-disk structures, in-memory core structures, constants, and error codes.

Key on-disk structures:
- `Qid9p1`: 32-bit path plus version.
- `Dentry`: fixed 28-byte name, uid/gid, mode flags, qid, size, direct blocks, indirect blocks, atime, mtime.
- `Tag`: block trailer tag and owner path.
- `Super1`, `Fbuf`, and `Superb`: superblock and freelist state.

Key in-memory structures:
- `Device`, `Filter`, `Filta`, `Tlock`, `File`, `Filsys`, `Hiob`, `Iobuf`, `Uid`, and `Wpath`.

Constants:
- `NAMELEN`, `NDBLOCK`, `MAXDAT`, `NTLOCK`.
- Dentry flags `DALLOC`, `DDIR`, `DAPND`, `DLOCK`, permission bits.
- KFS error enum and max error.
- Block tags `Tsuper`, `Tdir`, `Tind1`, `Tind2`, `Tfile`, `Tfree`, etc.
- Buffer flags `Bread`, `Bprobe`, `Bmod`, `Bimm`, `Bres`.
- Old open modes and checker flags.
- Extern declarations for block-size-derived globals.

Role:
- The most important KFS ABI file: changing its “DONT TOUCH” structures changes disk format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portfns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portfns.h

This header declares most KFS internal functions and vararg format checks.

Key areas:
- Metadata/block helpers: `accessdir`, `balloc`, `bfree`, `checktag`, `dnodebuf`, `dtrunc`, `getbuf`, `putbuf`, `settag`.
- Fid/path helpers: `fileinit`, `filep`, `newfp`, `freefp`, `newwp`, `freewp`, `putwp`.
- Protocol helpers: `mkqid`, `mkqidcmp`, `mkqid9p1`, `mkqid9p2`, `serve9p1`, `serve9p2`.
- Console helpers: `con_*`, `cmd_user`, `cprint`.
- Auth/user helpers: `authfree`, `mkchallenge`, `ingroup`, `leadgroup`, `strtouid`, `uidtostr`.
- Formatting helpers and `#pragma varargck` declarations for custom formats.

Role:
- Shared prototype surface for the old C codebase, compensating for pre-ANSI style definitions and cross-file dependencies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/portfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/porttime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/porttime.c

This file provides local time formatting and dump scheduling helpers.

Key behavior:
- Implements simplified `kgmtime` and `klocaltime`.
- Uses a hardcoded timezone of 5 hours west of Greenwich with DST rules from `daytab`.
- `datestr` formats a timestamp as `YYYYMMDD`.
- `Tfmt` formats timestamps for KFS custom `%T` output, returning `"The Epoch"` for zero.
- `nextime` computes the next timestamp at a requested hour, skipping days represented by a bitmask.

Dependencies:
- Uses `Tm` from Plan 9 libc headers.
- `Tfmt` is registered by `formatinit`.

Notable detail:
- Leap-year logic is simple `year % 4`, matching old Plan 9 assumptions rather than full Gregorian century rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/porttime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/print.c

This file implements an older local printf-style formatter.

Key behavior:
- Defines formatter state `Op`-based conversion dispatch through `fmtinstall`, `doprint`, and converter functions.
- Supports base conversions `%c`, `%d`, `%h`, `%l`, `%o`, `%s`, `%u`, `%x`, and `%%`.
- `numbconv` handles signed/unsigned, short/long, width, precision, and bases 8/10/16.
- `strconv` applies width and precision to string output.

Role:
- Portability/compatibility formatting layer for old KFS/Plan 9 code.
- Separate from the Plan 9 `Fmt` system used elsewhere in current files.

Notable detail:
- The file relies on types/macros such as `Op`, `FLONG`, `FSHORT`, and `FUNSIGN` that are expected from the broader historical build environment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/sub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/sub.c

This file contains central KFS support logic for fid allocation, path references, permissions, locks, block allocation, formatting, and filesystem initialization helpers.

Key behavior:
- `fsstr` resolves filesystem names.
- `fileinit` clears all fids on a channel, handles remove-on-close, and releases locks/paths.
- `filep`, `newfp`, and `freefp` manage locked fid structures from a global free list.
- `newwp`, `getwp`, `freewp`, and `putwp` manage shared parent walk paths with reference counts.
- `iaccess` implements owner/group/other permission checks plus special handling for group 9999 and directory execute.
- `tlocked` implements `DLOCK` exclusive lock allocation/renewal over `Tlock`.
- `newqid` and `qidpathgen` increment the superblock qid generator.
- `checkname` validates fixed-length names.
- `bfree`, `balloc`, and `addfree` manage block free lists and tag initialization.
- Formatting helpers register `%C`, `%D`, `%A`, `%G`, `%T`, and `%O`.
- `rootream`, `superream`, and `superok` initialize and mark filesystem metadata.
- `prime` and `hexdump` are utility helpers.

Dependencies:
- Core partner files are `iobuf.c`, `dentry.c`, `uid.c`, `dat.c`, and `portdat.h`.

Notable details:
- File and path structures are allocated in chunks with hard caps (`Fmax`, `Wmax`).
- `bfree` recursively frees indirect blocks, cancels dirty cached copies, and returns blocks to the superblock freelist.
- `balloc` pulls blocks from the superblock freelist and tags newly allocated blocks immediately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/uid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/uid.c

This file manages KFS user, group, and membership tables, loaded primarily from `/adm/users`.

Key behavior:
- `cmd_user` reads `/adm/users` through console 9P calls and builds `uid`, `uidspace`, and `gidspace`.
- If `/adm/users` cannot be read, initializes a minimal built-in table with users/groups such as `adm`, `none`, `glenda`, `sys`, `upas`, and `bootes`.
- `fname` and `fchar` stream and tokenize `/adm/users`.
- `uidtostr`/`uidtostr1` map numeric ids to names.
- `strtouid`/`strtouid1` map names to numeric ids.
- `ingroup` tests group membership using flattened `gidspace`.
- `leadgroup` checks group leader authority.

Data handling:
- Uses `uidgc.uidlock` to protect user/group state.
- Sorts by uid and by name to report duplicates.
- Sets global `writegroup` to the uid of group/user name `"write"`.

Notable detail:
- `strtouid1` returns `0` both for unknown names and for `none`, so callers often treat `0` as “unknown/none” carefully.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/uid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfscmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfscmd.c

This standalone utility sends commands to a running KFS command service.

Key behavior:
- Parses optional `-n server` to select `/srv/kfs.<name>.cmd`; otherwise opens `/srv/kfs.cmd`.
- Writes each command argument to the command fd.
- Reads command output until it sees `done`, `success`, or `unknown command`.
- Prints command output to stdout and tracks command errors.
- Exits with `"errors"` if any command failed.

Role:
- Operator-facing client for the command channel implemented by `main.c`/`con.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/kfscmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mbr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mbr.c

This standalone disk utility installs or replaces PC master boot record boot code.

Key behavior:
- Defines DOS partition-table entry layout `Tentry`.
- Contains a built-in default MBR boot block that prints an error and reboots.
- `writechs` encodes CHS values, saturating cylinders at 1023.
- `wrtentry` writes an active partition entry with CHS and LBA fields.
- Opens a disk with `opendisk`, refuses floppies, reads the existing boot sector, and preserves the partition table unless `-9` rebuilds it.
- `-m mbrfile` uses external MBR code; otherwise uses the built-in default.
- `-9` creates one active Plan 9 partition of type `0x39`.
- Writes boot signature `0x55AA` and writes the MBR back.

Notable details:
- Assumes a 512-byte MBR area even on disks with larger sectors, relying on `/dev/sd` read-modify-write behavior.
- Writes whole-sector-rounded data length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mkext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mkext.c

This standalone utility extracts or transforms mkfs-style archive streams.

Key behavior:
- Reads archive headers with fields: filename, mode, uid, gid, mtime, bytes.
- Stops on `end of archive`.
- Options support destination prefix (`-d`), header-only output (`-h`), uid/gid restoration (`-u`), time restoration (`-T`), and verbose mode (`-v`).
- `selected` filters extraction to requested file prefixes.
- `mkdirs` creates parent directories for selected extraction.
- `mkdir` creates directories and applies mode, uid/gid, and mtime as requested.
- `extract` writes file contents and then applies metadata.
- `seekpast` skips unselected file payloads.
- `warn` reports recoverable metadata/write issues; `error` exits on fatal archive errors.

Role:
- Companion to `mkfs -a` archive output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mkext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mkfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mkfs.c

This standalone utility populates a filesystem, directory tree, or archive from proto files.

Key behavior:
- Supports output modes: mounted KFS (`Kfs`), local filesystem destination (`Fs` via `-d`), and archive (`Archive` via `-a`).
- Mounts KFS under `/n/kfs`, sends `allow`, creates/updates `/adm/users`, processes proto files, then sends `disallow` and `sync`.
- Parses indented proto entries into `File` records with destination path, source path, uid, gid, and mode.
- `mkfs` recursively processes proto hierarchy; `mktree` expands `+`/`*` entries from source directories.
- `copyfile` decides metadata, uid/gid behavior, mode overrides, archive output, and whether destination is up-to-date.
- `copy` copies file data, preserving sparse zero ranges by seeking over zero buffers, then atomically renames the temp file through `dirfwstat`.
- `mkdir` creates or updates directories.
- `arch` emits archive headers.
- `setusers` specially handles `/adm` and `/adm/users` before normal population.
- `kfscmd` sends commands to the KFS command channel.

Notable options:
- `-a`: write archive.
- `-d root`: populate ordinary filesystem tree.
- `-n name`: select KFS service name.
- `-p`: update modes even if files are up to date.
- `-r`: force copy as if reaming.
- `-s source`: source root prefix.
- `-u users`: alternate users file.
- `-U`: set uid/gid on ordinary filesystem destination.
- `-x`: emit path/mtime/length listing.
- `-z n`: set copy buffer size.

Notable details:
- `error` attempts to disallow and sync KFS before exiting.
- Environment-variable expansion is supported for proto names beginning with `$`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/partfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/partfs.c

This file implements a userspace 9P server exposing partitions over an underlying disk image or sd-style directory.

Key behavior:
- Maintains up to 64 `Part` records with name, mode, version, sector offset, and sector length.
- Exposes a root containing one device directory named by `sdname`; inside are `ctl` and partition files.
- `ctlstring` reports inquiry, geometry, and partition lines.
- `ctlwrite` supports `part`, `delpart`, `inquiry`, and `geometry`; unknown control messages pass through to an underlying ctl fd if present.
- `addpart` and `delpart` manage partition table state and qid versions.
- `rdwrpart` bounds-checks reads/writes and maps partition-relative byte offsets to the underlying file.
- Implements lib9p handlers: attach, walk1, open, read, write, stat.
- `addparts` imports boot-style partition specs like `name start end/name start end`.
- `main` opens a file or sd directory, creates a default `data` partition, optionally imports `-p` parts, and posts/mounts the server.

Options:
- `-D`: chatty 9P.
- `-d sdname`: device directory name.
- `-m mtpt`: mount point, default `/dev`.
- `-p 9parts`: initial partition string.
- `-r`: read-only open of backing file.
- `-s srvname`: post service name.

Notable detail:
- `rdonly` changes how the backing file is opened, but partition file modes are still initialized from `ctlmode`; write attempts fail at underlying fd/write behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/partfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/calc.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/calc.y

This yacc grammar parses arithmetic expressions used by the disk partition editors.

Language:
- Numeric literals with optional units: `k`, `m`, `g`, `t`; units convert to sectors with `k` multiplying by 2 and larger units chaining by 1024.
- Special symbols `.` for current dot and `$` for current limit/end.
- Operators: `+`, `-`, `*`, `/`, unary `-`, parentheses, and postfix `%`.
- Postfix `%` evaluates as a percentage of the current size.

Key functions:
- `mkNUM` and `mkOP` build expression nodes.
- `yylex` tokenizes numbers, units, symbols, and operators.
- `eval` recursively evaluates expression trees and checks division by zero.
- `parseexpr` sets parser context (`dot`, `dollar`, `size`), invokes `yyparse`, and returns either an error string or result.

Role:
- Shared by `prep/edit.c` commands for partition start/end expressions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/calc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.c

This file implements the generic interactive partition-editing command framework used by `fdisk` and `prep`.

Key behavior:
- `getline` reads commands and warns on EOF if changes are unwritten.
- `findpart`, `addpart`, and `delpart` manage sorted `Part` arrays and change flags.
- Base commands:
  - `.`: show/set dot.
  - `a`: add partition using parsed start/end expressions.
  - `d`: delete partition.
  - `h`/`?`: help.
  - `p`: print partition table through caller callback.
  - `P`: print/update sd ctl commands.
  - `w`: write partition table through caller callback.
  - `q`: quit, warning once on unwritten changes.
- `runcmd` tokenizes and dispatches commands, falling back to an editor-specific extension callback.
- `rdctlpart` reads current kernel sd partition lines from the disk ctl fd.
- `ctldiff` compares desired partitions with current ctl partitions, emits `delpart` and `part` commands to reconcile them.
- `emalloc` and `estrdup` are fatal allocation helpers.

Callback model:
- The `Edit` struct supplies disk pointer, partition arrays, and callbacks for add/delete/extra commands/name validation/printing/writing/control printing.

Notable detail:
- Overlap detection builds a warning string but the return is commented out, so overlapping partitions are not rejected by the generic layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.h

This header defines the shared partition editor data model.

Key structures:
- `Part`: partition name, ctl name, start/end, ctl start/end overrides, and changed flag.
- `Edit`: disk pointer, current ctl partitions, desired partitions, callbacks, unit name, auxiliary pointer, dot/end values, and internal changed/warning/last-command state.

Key declarations:
- Generic editor functions: `getline`, `runcmd`, `findpart`, `addpart`, `delpart`.
- Expression parser: `parseexpr`.
- Kernel ctl reconciliation: `ctldiff`.
- Allocation helpers: `emalloc`, `estrdup`.

Role:
- Shared ABI for `edit.c`, `fdisk.c`, `prep.c`, and `calc.y`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/edit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/fdisk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/fdisk.c

This file implements an interactive and scriptable DOS/MBR partition table editor.

Key behavior:
- Opens a disk with `opendisk`, computes cylinders from heads/sectors, finds MBR offset including Disk Manager overlay handling, reads primary and extended partition tables, and populates generic `Edit` partitions.
- Supports blanking, auto-adding a Plan 9 partition, writing, printing ctl commands, read-only mode, alternate sector size, and treating input as plain file.
- Defines MBR `Tentry`, `Table`, DOS partition type constants, type-name mapping, and `Dospart`.
- `rdpart` recursively reads extended partition chains and records original tables for recovery.
- `recover` restores original tables and kernel ctl partitions after write failures/fatal exits.
- `autopart` finds the largest suitable free gap and creates an active Plan 9 type `0x39` partition if none exists.
- `plan9print` maps DOS partition types to Plan 9 ctl partition names, deduplicating names.
- Editor extensions:
  - `A name`: set active primary partition.
  - `t name [type]`: set partition type.
  - `R`: restore and exit.
- `wrpart` writes primary and extended partition tables and updates kernel sd ctl state through `ctldiff`.

Safety details:
- Overrides `sysfatal` and `abort` to attempt recovery if writes already happened.
- Tracks original partition tables in `rtab`.
- CHS fields are regenerated and saturated at cylinder 1023.
- Extended partitions are written recursively with `wrextend`.

Notable details:
- Partition editing unit is cylinder; actual MBR fields are sector/LBA.
- New non-primary partitions reserve the first track/sector offset similarly to historical DOS extended layout rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/fdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/prep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/prep.c

This file implements the Plan 9 partition-table editor for partitions inside a Plan 9 disk partition.

Key behavior:
- Opens a disk/partition with `opendisk`, optionally overrides sector size, checks for a FAT boot sector where the Plan 9 table would be, reads the Plan 9 partition table from sector 1, and enters generic edit mode.
- Partition table format is text lines: `part name start end`.
- `cmdadd` rejects non-`9fat` partitions starting before sector 2 to avoid the PBS/table area.
- `cmdokname` rejects control characters, space, slash, and DEL.
- `rdpart` parses the sector-1 table into `Part` records.
- `wrpart` writes the text table back to sector 1 and reconciles kernel sd ctl partitions through `ctldiff`.
- `restore` rewrites the saved old sector and attempts to restore ctl partitions after a failed write.
- `checkfat` refuses to overwrite a FAT boot sector signature at sector 1.
- `autoxpart` automatically allocates requested partition types according to min/max/weight rules.

Automatic partition names:
- `9fat`, `nvram`, `fscfg`, `fs`, `fossil`, `arenas`, `isect`, `bloom`, `other`, `swap`, `cache`.

Options:
- `-a partname`: request automatic partition.
- `-b`: blank existing table.
- `-c`, `-n`: accepted flags for cache/nvram mode state, though not otherwise used in the read code.
- `-f`: disk is a file.
- `-p`: print ctl commands read-only.
- `-r`: read-only.
- `-s sectorsize`: override sector size.
- `-w`: write after setup.

Notable detail:
- Editing unit is sector, unlike `fdisk.c` where unit is cylinder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/prep/prep.c -->