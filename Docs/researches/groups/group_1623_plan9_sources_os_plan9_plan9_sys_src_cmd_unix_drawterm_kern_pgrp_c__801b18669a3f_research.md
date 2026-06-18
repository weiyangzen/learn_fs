# Group Research: group_1623_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_kern_pgrp_c__801b18669a3f

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/pgrp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/pgrp.c

This file implements hosted drawterm process-resource groups: process groups, rendezvous groups, file-descriptor groups, and mount records.

Key behavior:
- `newpgrp`, `closepgrp`, `pgrpcpy`, `pgrpinsert` manage namespace/mount group allocation, ordered mount insertion, and cloning.
- `newrgrp`, `closergrp` allocate and release rendezvous groups.
- `dupfgrp`, `closefgrp` duplicate and close file descriptor tables with channel refcount handling.
- `newmount`, `mountfree` allocate mount objects and release mounted channels/spec strings.
- `pgrpnote` is compiled out under `NOTDEF`; `resrcwait` prints exhaustion diagnostics.

Important details:
- `pgrpcpy` deep-copies mount headers and mount lists while incrementing mounted channel refs.
- `dupfgrp` copies only live descriptors and increments channel refs, preserving `maxfd`.
- File-descriptor table growth and syscall wrappers are in `sysfile.c`; this file owns the group lifetime pieces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/pgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/posix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/posix.c

This file is the POSIX host runtime shim for drawterm's Plan 9-like kernel process model.

Key behavior:
- Stores the current `Proc*` in a pthread key via `_getproc` and `_setproc`.
- `osinit` initializes TLS and installs a `SIGPIPE` ignore handler.
- `osnewproc`, `osproc`, and `tramp` create pthread-backed kernel processes and run `Proc.kpfun`.
- `procsleep` and `procwakeup` block/wake a hosted process using `pthread_cond_t`.
- `oserror`/`oserrstr` translate host `errno` into Plan 9 error strings.
- `randomread`, `seconds`, `ticks`, `osmsleep`, and `osyield` provide host services.

Important details:
- `osnewproc` initializes each `Proc` with a private mutex and condition variable.
- Random data comes from `/dev/urandom` unless `USE_RANDOM` forces libc `random()`.
- `showfilewrite` is a no-op stub for hosted control files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/posix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/procinit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/procinit.c

This file initializes the hosted drawterm process table and creates kernel processes.

Key behavior:
- `procinit0` allocates initial `Proc` state for the main host thread, including `pgrp`, `rgrp`, `fgrp`, `egrp`, error buffers, and default name.
- `newproc` allocates and initializes a new `Proc`.
- `kproc` names a process, assigns its function/argument, wires shared groups from `up`, and starts it through `osnewproc`.

Important details:
- New kernel processes share the current process's namespace, rendezvous group, file group, and environment group by pointer/refcount convention.
- Host-specific thread creation is delegated to `posix.c` or `win32.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/procinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qio.c

This file implements Plan 9-style block queues used by drawterm devices, pipes, network paths, and stream-like kernel components.

Key behavior:
- Block helpers include `freeblist`, `padblock`, `blocklen`, `blockalloclen`, `concatblock`, `pullupblock`, `pullupqueue`, `trimblock`, `copyblock`, `adjustblock`, `pullblock`, `packblock`, `bl2mem`, and `mem2bl`.
- Queue producers use `qpass`, `qpassnolim`, `qproduce`, `qbwrite`, `qwrite`, and interrupt-level `qiwrite`.
- Queue consumers use `qget`, `qconsume`, `qdiscard`, `qcopy`, `qbread`, and `qread`.
- Lifecycle/control functions include `qopen`, `qbypass`, `qfree`, `qclose`, `qhangup`, `qreopen`, `qflush`, `qsetlimit`, `qnoblock`, `qlen`, `qwindow`, `qcanread`, `qfull`, `qstate`, and `qisclosed`.

Important details:
- `Queue` tracks allocated bytes (`len`), payload bytes (`dlen`), limit, state flags, EOF count, optional kick callback, optional bypass callback, reader/writer locks, rendezvous points, and an error string.
- Flow control is based on `limit`; writers set `Qflow` and sleep on `wr`, readers wake writers once the queue drains.
- `Qmsg` preserves message boundaries; non-message queues may split/coalesce blocks.
- `qclose` discards buffered blocks and marks `Ehungup`; `qhangup` marks closed but leaves queued blocks readable.
- `Maxatomic`/`qiomaxatomic` limit atomic write chunking to 64 KiB.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qlock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qlock.c

This file implements sleepable queued locks for hosted drawterm kernel code.

Key behavior:
- `qlock` acquires a `QLock`, queues the current process if busy, and sleeps it.
- `canqlock` attempts a non-blocking acquire.
- `qunlock` releases the lock or wakes the next queued process.
- `holdqlock` reports whether the current process owns the lock.
- Private `queue`/`dequeue` maintain FIFO `Proc` wait lists.

Important details:
- Waiting processes are marked `Queueing` and resumed with `procwakeup`.
- Ownership is tracked in `q->owner`, allowing `holdqlock` checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rendez.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rendez.c

This file implements Plan 9-style sleep/wakeup on `Rendez` wait queues.

Key behavior:
- `sleep` evaluates a predicate under the rendezvous lock, queues `up` if false, unlocks, and blocks through `procsleep`.
- `wakeup` removes one process from the rendezvous wait queue and wakes it.

Important details:
- The predicate is rechecked before queuing, matching the standard Plan 9 sleep protocol.
- Processes are linked through `Proc.rnext`.
- `sleep.c` contains a duplicate implementation in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rendez.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rwlock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rwlock.c

This file implements a simple reader-writer lock by layering counters on `QLock`.

Key behavior:
- `rlock` serializes against `x` and increments reader count.
- `runlock` decrements reader count and releases writer exclusion when the last reader exits.
- `wlock` takes writer exclusion.
- `wunlock` releases writer exclusion.

Important details:
- The implementation favors simplicity over advanced fairness.
- The `QLock` fields inside `RWlock` provide sleeping behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/screen.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/screen.h

This header defines shared screen, mouse, and cursor state for drawterm's hosted GUI backends.

Key contents:
- `Mousestate` stores buttons, point, and event timestamp.
- `Mouseinfo` stores a small ring buffer, lock, open/translation state, and rendezvous for mouse readers.
- `Cursorinfo` stores cursor offset plus clear/set masks.
- `Screeninfo` stores screen lock, pending soft screen image, reshape flag, depth, and DIB type.
- Declares global `gscreen`, `mouse`, `cursor`, and `screen`.
- Declares screen, cursor, mouse, color, flush, and draw-lock APIs.

Important details:
- Mouse queue capacity is fixed at `Mousequeue` 16, with one slot unused by ring-buffer convention.
- This header connects kernel draw device logic with platform GUI files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sleep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sleep.c

This file duplicates the `Rendez` sleep/wakeup implementation also present in `rendez.c`.

Key behavior:
- `sleep` queues the current process on a `Rendez` until a predicate becomes true.
- `wakeup` removes and wakes one waiter.

Important details:
- Uses the same lock, `Proc.rnext`, `procsleep`, and `procwakeup` protocol as `rendez.c`.
- Build selection determines whether this or `rendez.c` supplies the symbols.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sleep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/smalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/smalloc.c

This file provides minimal allocation wrappers for drawterm kernel code.

Key behavior:
- `smalloc` calls `malloc`, zeroes the returned memory, and raises `Enomem` on failure.
- `malloc` wraps `calloc(n, 1)`.

Important details:
- Both paths zero memory, so `smalloc` redundantly clears allocations from this local `malloc`.
- This hosted kernel uses fatal/error-style allocation behavior rather than propagating `NULL` in many call sites.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/smalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/stub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/stub.c

This file supplies hosted-kernel stubs for Plan 9 kernel services that drawterm does not implement fully.

Key behavior:
- No-op or diagnostic stubs: `mallocsummary`, `setswapchan`, `splx`, `splhi`, `spllo`, `procdump`, `kickpager`, `todset`, `todsetfreq`, `todinit`, `hostdomainwrite`, `hostownerwrite`, `postnote`.
- `todget` returns host nanoseconds via `nsec`.
- `exhausted` calls `panic`.
- `fastticks` derives a fast tick value from `nsec`.

Important details:
- Interrupt priority routines are placeholders in hosted drawterm.
- `postnote` always reports failure, reflecting limited signal/note emulation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysfile.c

This file implements drawterm's hosted Plan 9 file, namespace, descriptor, error-string, and rendezvous syscall layer.

Key behavior:
- Descriptor management: `growfd`, `findfreefd`, `newfd`, `newfd2`, `fdtochan`, `fdclose`.
- File syscalls: open/create/close/dup/pipe/read/pread/write/pwrite/seek/stat/fstat/wstat/fwstat/remove/chdir.
- Namespace syscalls: `bindmount`, `_sysbind`, `_sysmount`, `_sysunmount`.
- Public wrappers convert `waserror` exceptions into `-1` returns and swap `errstr`/`syserrstr`.
- Error APIs: `werrstr`, `__errfmt`, `errstr`, `rerrstr`.
- `_sysrendezvous`/`sysrendezvous` implement Plan 9 rendezvous value exchange by tag.

Important details:
- File-descriptor tables grow by `DELTAFD` but cap around 5000 descriptors.
- `kread` supports union directory reads through `unionread`, advancing mounted union elements when one returns no data.
- `kwrite` reserves channel offset before writing and rolls it back on partial writes/errors.
- `validstat` checks packed 9P stat buffers and validates rewritten names.
- `bindmount` handles both bind and mount paths, including mount device attach with optional auth channel.
- The code contains visible duplicated lines in `_syspipe`, `_sysseek`, and `syschdir`, but semantics are mostly unaffected because the duplicates repeat checks/returns.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysproc.c

This file provides the minimal process-exit syscall for drawterm.

Key behavior:
- `sysexits` optionally prints an exit status string and terminates the host process with `exit(0)`.

Important details:
- It ignores Plan 9 wait status propagation; drawterm runs as a hosted application.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/term.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/term.c

This file implements a tiny graphical console renderer for drawterm kernel messages.

Key behavior:
- `terminit` initializes font, colors, cursor, and screen window bounds.
- `screenputc` renders characters, handles newline, tab, backspace, carriage return, and scrolls as needed.
- `termscreenputs` writes strings while holding the draw lock.
- `addflush`/`screenflush` accumulate and flush dirty rectangles.

Important details:
- Uses `Memimage`, `memimagedraw`, `memimagestring`, and `flushmemscreen`.
- The terminal window is derived from the current screen rectangle with small margins.
- Output is white background with black text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/term.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/uart.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/uart.c

This file is a UART output stub.

Key behavior:
- `uartputs` writes bytes to host file descriptor 2 unless `panicking` is set.

Important details:
- This gives hosted kernel code a serial-console-like diagnostic sink.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/uart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/unused/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/unused/syscall.c

This file is an older unused syscall implementation covering files, namespace, directories, and network dial helpers.

Key behavior:
- Implements alternate versions of descriptor handling, close/create/dup/open/read/write/seek/stat/wstat/remove/chdir/bind/mount/unmount.
- Adds directory helpers `sysdirstat`, `sysdirfstat`, `sysdirwstat`, `sysdirfwstat`, and `sysdirread`.
- Implements network helpers `sysdial`, `sysannounce`, `syslisten`, plus internal `call`, `identtrans`, and `nettrans`.

Important details:
- This file is under `kern/unused`, and active syscall logic lives in `sysfile.c` plus libc `dial.c`.
- It shows older Plan 9 namespace and `/net/cs` calling conventions retained for reference.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/unused/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/waserror.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/waserror.c

This file implements the core hosted Plan 9 error unwinding helpers.

Key behavior:
- `pwaserror` returns a new error label slot and increments `up->nerrlab`.
- `nexterror` long-jumps to the most recent saved label.
- `error` stores an error string in `up->errstr` and unwinds.

Important details:
- Callers use Plan 9's `waserror` macro around these helpers.
- `ERRMAX` bounds copied error text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/waserror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/win32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/win32.c

This file is the Windows host runtime shim for drawterm.

Key behavior:
- Implements `_getproc`/`_setproc` using Windows TLS.
- `osinit`, `osnewproc`, `osproc`, `tramp`, `procsleep`, and `procwakeup` map hosted `Proc` execution to Windows threads/events.
- Provides random data through CryptoAPI in `random20`/`randominit`.
- Provides `seconds`, `ticks`, `fastticks`, sleep/yield, and Windows error-string conversion.
- `WinMain` converts the Windows command line to UTF-8 argv and calls `main`.

Important details:
- Includes UTF-16/Rune conversion helpers `wstrutflen`, `wstrtoutf`, `wstrlen`, and Unicode capability detection.
- `osrerrstr` formats `GetLastError` messages and maps Winsock errors.
- Console argv parsing handles quotes and whitespace manually.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/latin1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/latin1.c

This file implements Plan 9 compose-key translation for Latin-1 and extended runes.

Key behavior:
- Static `cvlist` table maps compose sequences to Unicode rune values.
- `unicode` accepts explicit hexadecimal Unicode entry.
- `latin1` resolves a sequence of runes to a composed rune or reports partial/no match.

Important details:
- The table supports accents, symbols, Greek, arrows, math, ligatures, and punctuation used by Plan 9 keyboard input.
- Return values distinguish complete match, partial prefix, and failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/latin1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/Makefile

This Makefile builds drawterm's `libauth.a`.

Key contents:
- Includes `../Make.config`.
- Archives auth object files: attribute parsing, challenge/response, proxy, RPC, user/password, and auth attribute support.
- Uses `$(CC) $(CFLAGS)` for `.c` compilation and `$(AR)`/`$(RANLIB)` for archive creation.

Important details:
- `httpauth.c` exists in the directory but is not included in this archive's `OFILES`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/attr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/attr.c

This file implements auth attribute list formatting, parsing, lookup, copying, and cleanup.

Key behavior:
- `_attrfmt` formats linked `Attr` lists with quoting for query attributes.
- `_mkattr`, `_copyattr`, `_delattr`, `_findattr`, `_strfindattr`, and `_freeattr` manage attribute lists.
- `_parseattr` parses `name=value` and query-style attributes from a string.
- `cleanattr` removes duplicate attributes by keeping later entries.

Important details:
- Attribute values are parsed with Plan 9 tokenization/quoting rules.
- `Attr.type` controls plain versus query attribute output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_attr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_attr.c

This file exposes parsed attributes from an auth RPC conversation.

Key behavior:
- `auth_attr` returns `_parseattr(rpc->arg)`.

Important details:
- Attribute parsing is delegated entirely to `attr.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_challenge.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_challenge.c

This file implements challenge/response auth setup and completion.

Key behavior:
- `auth_challenge` opens `/mnt/factotum/rpc`, starts an auth RPC, sends formatted parameters, and requests a challenge.
- `auth_response` sends a response and retrieves `AuthInfo`.
- `auth_freechal` releases the challenge state and associated RPC.

Important details:
- Uses `AuthRpc` verbs such as `start`, `read`, and `write`.
- Challenge bytes and user strings are copied into a `Chalstate`.
- On failure it closes RPC state and records errors through `werrstr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_challenge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_getuserpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_getuserpasswd.c

This file obtains username/password credentials through factotum-style auth RPC.

Key behavior:
- `auth_getuserpasswd` starts an RPC with formatted parameters, repeatedly handles RPC phases, and returns `UserPasswd`.
- Internal `dorpc` sends one verb/value pair and invokes `getkey` when the RPC asks for keys.

Important details:
- Copies `user` and `password` attributes out of the returned RPC data.
- Handles `ARneedkey` by calling the supplied key-acquisition callback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_getuserpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_proxy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_proxy.c

This file proxies an authentication protocol between a connection and an `AuthRpc`.

Key behavior:
- `auth_proxy` opens `/mnt/factotum/rpc`, starts an RPC, and delegates to `fauth_proxy`.
- `fauth_proxy` loops over RPC states, reading/writing protocol bytes on the supplied fd.
- `auth_getinfo` retrieves and decodes final `AuthInfo`.
- `auth_freeAI` releases decoded auth info.
- `convM2AI`, `gstring`, and `gcarray` decode factotum's packed auth-info reply.

Important details:
- Handles `ARdone`, `ARok`, `ARphase`, `ARneedkey`, `ARtoosmall`, and error states.
- Returns peer credential data including `cuid`, `suid`, capability, secret, and auth domain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_proxy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_respond.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_respond.c

This file performs a one-shot challenge response through factotum.

Key behavior:
- `auth_respond` opens `/mnt/factotum/rpc`, starts an auth RPC, writes challenge bytes, reads response bytes, and returns response length.
- Internal `dorpc` handles RPC verb dispatch and key callback requests.

Important details:
- Copies returned user text into the caller's buffer when available.
- Enforces caller-provided response buffer length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_respond.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_rpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_rpc.c

This file implements the low-level factotum RPC client.

Key behavior:
- `auth_allocrpc` allocates an `AuthRpc` bound to an fd.
- `auth_freerpc` closes and releases it.
- `auth_rpc` sends `verb[ data]` requests and reads/classifies replies.
- `classify` maps reply text to `ARok`, `ARdone`, `ARerror`, `ARneedkey`, `ARbadkey`, `ARtoosmall`, and `ARphase`.

Important details:
- RPC data is stored in `rpc->arg` with `rpc->narg`.
- Reply classification is string-prefix based and preserves returned payload after the status word.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_userpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_userpasswd.c

This file implements legacy Plan 9 user/password authentication.

Key behavior:
- `auth_userpasswd` builds an `AuthInfo` from username/password by requesting a ticket from the auth server.
- `netresp` creates the DES-based response for a challenge.

Important details:
- Uses `passtokey`, `authdial`, ticket request/reply conversion, and authenticator conversion routines from `libauthsrv`.
- Produces `AuthInfo` fields from the returned ticket/authenticator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_userpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/authlocal.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/authlocal.h

This header contains one internal auth declaration.

Key contents:
- Declares `_fauth_proxy(int fd, AuthRpc *rpc, AuthGetkey *getkey, char *params)` returning `AuthInfo*`.

Important details:
- The visible implementation in this tree is named `fauth_proxy`, so this declaration reflects an internal/compatibility naming convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/authlocal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/httpauth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/httpauth.c

This file implements HTTP-style password checking against Plan 9 auth tickets.

Key behavior:
- `httpauth` dials the auth server, requests a ticket for the named user, derives a key from the supplied password, and decrypts/validates the ticket.

Important details:
- Returns success/failure rather than an `AuthInfo`.
- Not listed in `libauth/Makefile`, so it may be unused in this drawterm build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/httpauth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/Makefile

This Makefile builds drawterm's `libauthsrv.a`.

Key contents:
- Includes `../Make.config`.
- Archives ticket/authenticator conversion files, NVRAM checksum, and password-to-key helpers.
- Uses `$(CC) $(CFLAGS)`, `$(AR)`, and `$(RANLIB)`.

Important details:
- `authdial.c` and `readnvram.c` are present in the directory but not included in this archive's `OFILES`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asgetticket.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asgetticket.c

This file reads ticket and authenticator material from an auth-server fd.

Key behavior:
- `_asgetticket` reads a ticket reply buffer and a ticket buffer using fixed auth protocol sizes.

Important details:
- Returns `-1` if either fixed-size read fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asgetticket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asrdresp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asrdresp.c

This file reads variable-length auth-server responses.

Key behavior:
- `_asrdresp` reads the decimal byte-count prefix, validates it, then reads the requested response bytes.

Important details:
- Handles malformed size fields and oversize responses by setting error strings.
- Used by auth-server protocol helpers that need counted replies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asrdresp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/authdial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/authdial.c

This file locates and dials a Plan 9 auth server.

Key behavior:
- `authdial` looks up auth server information with NDB helpers and dials the selected service.

Important details:
- Uses network database and Biobuf interfaces.
- Present source is not included in `libauthsrv/Makefile`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/authdial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convA2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convA2M.c

This file packs an `Authenticator` into auth protocol bytes.

Key behavior:
- `convA2M` serializes numeric fields and strings, then encrypts the payload with the supplied DES key.

Important details:
- Uses local macros for little-endian field emission.
- Returns the fixed authenticator message size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convA2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2A.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2A.c

This file unpacks encrypted auth protocol bytes into an `Authenticator`.

Key behavior:
- `convM2A` decrypts with the supplied key and decodes fields into an `Authenticator`.

Important details:
- Uses little-endian extraction macros matching `convA2M`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2A.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2PR.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2PR.c

This file unpacks encrypted auth protocol bytes into a `Passwordreq`.

Key behavior:
- `convM2PR` decrypts the message and extracts password-change request fields.

Important details:
- Uses fixed authsrv field layout and little-endian macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2PR.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2T.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2T.c

This file unpacks encrypted auth protocol bytes into a `Ticket`.

Key behavior:
- `convM2T` decrypts the ticket and extracts ticket fields.

Important details:
- Complements `convT2M`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2T.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2TR.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2TR.c

This file unpacks plain auth protocol bytes into a `Ticketreq`.

Key behavior:
- `convM2TR` decodes request type, auth ids, challenge, host id, uid, and auth domain.

Important details:
- Ticket requests are not encrypted by this conversion routine.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convM2TR.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convPR2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convPR2M.c

This file packs a `Passwordreq` into encrypted auth protocol bytes.

Key behavior:
- `convPR2M` serializes password request fields and encrypts them with the supplied key.

Important details:
- Complements `convM2PR`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convPR2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convT2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convT2M.c

This file packs a `Ticket` into encrypted auth protocol bytes.

Key behavior:
- `convT2M` serializes ticket fields and encrypts with the supplied key.

Important details:
- Complements `convM2T`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convT2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convTR2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convTR2M.c

This file packs a `Ticketreq` into plain auth protocol bytes.

Key behavior:
- `convTR2M` serializes ticket request fields without encryption.

Important details:
- Complements `convM2TR`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/convTR2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/nvcsum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/nvcsum.c

This file implements the Plan 9 NVRAM checksum.

Key behavior:
- `nvcsum` rotates and adds bytes to produce an 8-bit checksum.

Important details:
- Used by `readnvram.c` to validate stored auth secrets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/nvcsum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/opasstokey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/opasstokey.c

This file implements the older password-to-DES-key derivation.

Key behavior:
- `opasstokey` folds password bytes into a DES key buffer using the original Plan 9 algorithm.

Important details:
- Kept for compatibility with older auth material.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/opasstokey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/passtokey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/passtokey.c

This file derives a DES key from a password.

Key behavior:
- `passtokey` processes password bytes into a fixed key and sets DES parity/format expected by Plan 9 auth.

Important details:
- Used by ticket decrypt/encrypt paths such as `auth_userpasswd`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/passtokey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/readnvram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/readnvram.c

This file reads Plan 9 auth secrets from NVRAM-like storage or asks interactively.

Key behavior:
- `readnvram` searches configured platform storage paths, optional `nvram`, `nvrlen`, and `nvroff` environment overrides, and fills `Nvrsafe`.
- `check` validates checksums and zeroes bad data.
- `readcons` prompts on `/dev/cons`, optionally in raw mode for secrets.
- `finddosfile` and `dosparse` locate an NVRAM file inside DOS/FAT-style storage when offset is `-1`.

Important details:
- Built-in table covers `sparc`, `pc`, `mips`, `power`, and `debug` paths.
- If storage cannot be read or validation fails, interactive prompts collect auth id, auth domain, and password-derived key material.
- Present source is not listed in `libauthsrv/Makefile`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/readnvram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/Makefile

This Makefile builds drawterm's bundled `libc.a`.

Key contents:
- Includes `../Make.config`.
- Archives Plan 9 libc compatibility objects for formatting, 9P packing, directory helpers, UTF/rune handling, networking helpers, random/time, TLS/SSL push helpers, and encoders.
- Uses `$(CC) $(CFLAGS)` and standard archive commands.

Important details:
- Some source files in the directory are not in `OFILES` and therefore are optional/unused for this build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/charstod.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/charstod.c

This file converts a character stream callback into a double.

Key behavior:
- `fmtcharstod` reads characters through a callback, buffers a numeric token, and calls `fmtstrtod`.

Important details:
- Supports the formatting library's float parsing needs.
- Handles sign, decimal point, and exponent scanning before delegating exact conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/charstod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/cleanname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/cleanname.c

This file canonicalizes Plan 9 path strings in place.

Key behavior:
- `cleanname` removes repeated slashes, `.` components, and collapses `..` where possible.
- Preserves rooted versus relative path semantics.

Important details:
- Empty results become `"."`.
- It treats `/` and NUL as path separators through `SEP`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/cleanname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convD2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convD2M.c

This file serializes `Dir` structures into 9P stat message format.

Key behavior:
- `sizeD2M` computes packed stat size.
- `convD2M` writes fixed fields, qid, mode/times/length, and counted strings for name, uid, gid, and muid.

Important details:
- Writes the size field before returning `BIT16SZ` for too-small buffers, allowing callers to discover needed size.
- Uses little-endian 9P `PBIT*` macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convD2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2D.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2D.c

This file validates and decodes 9P stat message bytes into `Dir`.

Key behavior:
- `statcheck` verifies total size and counted string layout.
- `convM2D` extracts fixed fields and optionally copies strings into caller-provided storage.

Important details:
- If no string storage is supplied, string fields point to a static empty string.
- Complements `convD2M`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2D.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2S.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2S.c

This file decodes 9P protocol messages from bytes into `Fcall`.

Key behavior:
- `convM2S` validates the size/type/tag header, switches on 9P message type, and extracts fields for version, attach, walk, open/create, read/write, clunk/remove, stat/wstat, and replies.
- `gstring` decodes counted strings in-place and NUL-terminates them.
- `gqid` decodes qids.

Important details:
- Returns `0` on malformed sizes, unknown types, overlong name/qid counts, or truncated buffers.
- It verifies decoded byte count matches the declared 9P message size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2S.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convS2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convS2M.c

This file encodes `Fcall` structures into 9P protocol messages.

Key behavior:
- `sizeS2M` computes encoded message size by 9P type.
- `convS2M` writes size/type/tag and all type-specific fields, qids, strings, data payloads, and stat payloads.
- `pstring` and `pqid` encode counted strings and qids.

Important details:
- Rejects unknown message types, oversized walk/qid arrays, and caller buffers smaller than computed size.
- Contains an apparent duplicated `PBIT32(p, f->fid);` in `Topen`; the final size check can detect pointer mismatch if it changes encoded length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convS2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/crypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/crypt.c

This file implements block DES encryption/decryption wrappers for Plan 9 auth data.

Key behavior:
- `encrypt` applies DES encryption over 7-byte chunks expanded into 8-byte DES blocks.
- `decrypt` reverses the operation.

Important details:
- Uses `setupDESstate`, `block_cipher`, and auth key layout expected by Plan 9 ticket code.
- Returns `0` on success and `-1` for invalid lengths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dial.c

This file implements Plan 9-style `dial`.

Key behavior:
- `dial` parses network address strings and either uses `/net/cs` through `csdial` or calls a clone/control/data endpoint directly.
- `call` opens clone, writes connect requests, opens data, and optionally returns control fd/path.
- `_dial_string_parse` decomposes network, address, service, and protocol fields.

Important details:
- Uses Plan 9 `/net` filesystem conventions even inside drawterm's hosted environment.
- Supports optional local address/control handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfstat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfstat.c

This file returns allocated `Dir` data for an open fd.

Key behavior:
- `dirfstat` calls `fstat`, decodes with `convM2D`, allocates enough space for `Dir` plus strings, and returns it.

Important details:
- Uses a stack stat buffer sized for common cases.
- Returns `nil` on syscall or decoding failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfwstat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfwstat.c

This file writes `Dir` metadata to an open fd.

Key behavior:
- `dirfwstat` serializes a `Dir` using `convD2M` and calls `fwstat`.

Important details:
- Allocates exactly `sizeD2M(d)` bytes for the packed stat.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfwstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirmodefmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirmodefmt.c

This file formats Plan 9 directory mode bits.

Key behavior:
- `dirmodefmt` renders type and permission bits as a textual mode string.
- `rwx` fills read/write/execute triples.

Important details:
- Handles Plan 9 mode flags such as directory, append, exclusive, auth, temporary, and device-specific bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirmodefmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirstat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirstat.c

This file returns allocated `Dir` data for a path.

Key behavior:
- `dirstat` calls `stat`, decodes with `convM2D`, and returns allocated `Dir` plus string storage.

Important details:
- Mirrors `dirfstat` for pathname input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirwstat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirwstat.c

This file writes `Dir` metadata to a path.

Key behavior:
- `dirwstat` serializes a `Dir` using `convD2M` and calls `wstat`.

Important details:
- Pathname counterpart to `dirfwstat`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirwstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dofmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dofmt.c

This file is the core byte-string formatter for Plan 9 `Fmt`.

Key behavior:
- `dofmt` parses format strings, flags, width, precision, argument indexes, and dispatches conversions.
- Helper conversions include chars, runes, strings, rune strings, integers, counts, percent, flags, and bad-format output.
- `__fmtflush`, `__fmtpad`, `__rfmtpad`, `__fmtcpy`, and `__fmtrcpy` manage buffered output and padding.

Important details:
- Supports Plan 9 format flags and length modifiers, including `ll`, `l`, `h`, `u`, `#`, width, precision, and left adjustment.
- Conversion dispatch is supplied by `fmt.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dofmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dorfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dorfmt.c

This file is the rune-format-string counterpart to `dofmt`.

Key behavior:
- `dorfmt` parses a `Rune*` format string and dispatches conversions through the same `Fmt` machinery.

Important details:
- Enables `Rune` output formatting APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dorfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/encodefmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/encodefmt.c

This file implements encoded byte formatting.

Key behavior:
- `encodefmt` formats byte arrays in encodings selected by the format verb/flags, including hex and base encodings.

Important details:
- Used by Plan 9 `%.*H`/encoding-style formatting conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/encodefmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/errfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/errfmt.c

This file provides an error-string format conversion.

Key behavior:
- `errfmt` delegates to `__errfmt`.

Important details:
- The active error-string source is implemented in `kern/sysfile.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/errfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fcallfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fcallfmt.c

This file formats 9P `Fcall`, `Qid`, `Dir`, and payload data for diagnostics.

Key behavior:
- `fcallfmt` renders each 9P message type with its relevant fields.
- `dirfmt` and `fdirconv` format `Dir` values.
- `qidtype` formats qid type bits.
- `dumpsome` prints bounded data payload previews.

Important details:
- Useful for tracing filesystem protocol traffic.
- Limits payload dumps to avoid huge diagnostic strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fcallfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fltfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fltfmt.c

This file implements floating-point formatting for Plan 9 `Fmt`.

Key behavior:
- `__efgfmt` handles `%e`, `%f`, and `%g` style conversions.
- `floatfmt`, `xdtoa`, and decimal helpers produce rounded decimal representations.
- Local `pow10`, `xadd`, and `xsub` support decimal digit adjustment.

Important details:
- Handles NaN/Inf through helpers from `nan64.c`.
- Honors formatter width, precision, and flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fltfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmt.c

This file manages the global format-conversion registry and dispatch.

Key behavior:
- `fmtinstall` installs conversion functions by verb.
- `fmtfmt` looks up conversion handlers.
- `__fmtdispatch` calls `dofmt` or `dorfmt` based on byte versus rune format strings.
- Initializes default conversions for integers, strings, chars, runes, floats, quotes, and errors.

Important details:
- Uses a small fixed table plus locking hooks.
- `PLAN9PORT` conditionals support hosted variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtdef.h

This header defines internal formatting-library helpers.

Key contents:
- Declares internal `__fmt*`, quote, NaN/Inf, string, rune, and conversion functions.
- Defines `Quoteinfo`.
- Provides `FMTCHAR`, `FMTRCHAR`, and `FMTRUNE` buffered-output macros.
- Defines `VA_COPY` compatibility and `PLAN9PORT`.

Important details:
- Shared by nearly all formatting implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfd.c

This file initializes `Fmt` output to a file descriptor.

Key behavior:
- `fmtfdinit` configures a `Fmt` with fd, buffer, flush callback, and output pointers.
- `fmtfdflush` flushes buffered bytes by writing to the fd.

Important details:
- Underpins `vfprint`, `fprint`, and related fd-based formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfdflush.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfdflush.c

This file provides an fd flush callback for `Fmt`.

Key behavior:
- `__fmtFdFlush` writes pending bytes to the fd stored in the formatter.

Important details:
- This is a compatibility/internal variant used by the formatting layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfdflush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtlock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtlock.c

This file defines formatting registry lock hooks.

Key behavior:
- `__fmtlock` and `__fmtunlock` are empty.

Important details:
- The hosted drawterm formatting registry is effectively unlocked here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtprint.c

This file prints formatted text into an existing `Fmt`.

Key behavior:
- `fmtprint` wraps `fmtvprint` with varargs.

Important details:
- Useful for custom formatters that append to the current formatter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtquote.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtquote.c

This file implements shell-style quoted string formatting.

Key behavior:
- `__quotesetup` scans byte or rune strings to decide if quoting is needed and compute output lengths.
- `qstrfmt` emits quoted strings with doubled quotes as needed.
- `quotestrfmt`, `quoterunestrfmt`, and `__quotestrfmt` provide formatter conversions.
- `quotefmtinstall` installs quote formatters.
- `__needsquotes` and `__runeneedsquotes` expose quote checks.

Important details:
- Handles byte and rune input/output variants.
- Supports sharp flag behavior for forced quoting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtquote.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtrune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtrune.c

This file appends one rune to a `Fmt`.

Key behavior:
- `fmtrune` emits a rune through the formatter's flush-aware output buffer.

Important details:
- Used by rune/string formatting helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtrune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtstr.c

This file finalizes a dynamically allocated string formatter.

Key behavior:
- `fmtstrflush` terminates and returns the accumulated string.

Important details:
- Used by `vsmprint`/`smprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtvprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtvprint.c

This file formats varargs into an existing `Fmt`.

Key behavior:
- `fmtvprint` copies the `va_list`, calls `__fmtdispatch`, and returns the number of bytes/runes written.

Important details:
- Central bridge between public vararg wrappers and formatter dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtvprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fprint.c

This file implements formatted output to an fd.

Key behavior:
- `fprint` wraps `vfprint` with varargs.

Important details:
- Plan 9 equivalent of `fprintf` for integer file descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/frand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/frand.c

This file returns floating-point pseudo-random values.

Key behavior:
- `frand` scales `lrand()` into the range `[0, 1)`.

Important details:
- Uses a 31-bit mask and normalization constant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/frand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getfields.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getfields.c

This file splits strings into fields.

Key behavior:
- `getfields` tokenizes a string in place using a delimiter set.
- Supports merging adjacent delimiters or returning empty fields depending on `mflag`.

Important details:
- Replaces separators with NUL bytes and fills the caller's `args` array.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getfields.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getpid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getpid.c

This file provides a Plan 9-style process id helper.

Key behavior:
- `getpid` returns a pid derived from the current hosted `Proc`.

Important details:
- Uses drawterm's process model, not necessarily the host OS pid.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getpid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lnrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lnrand.c

This file returns bounded non-negative pseudo-random longs.

Key behavior:
- `lnrand` scales `lrand()` into `[0, n)`.

Important details:
- Uses simple modulo/scaling logic from Plan 9 libc style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lnrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lock.c

This file implements low-level spin/mutex locks for the hosted libc layer.

Key behavior:
- With `PTHREAD`, locks lazily initialize a pthread mutex and use it for `lock`, `canlock`, and `unlock`.
- Without `PTHREAD`, it uses atomic test-and-set style locking with yielding.
- `ilock` and `iunlock` alias to `lock`/`unlock`.

Important details:
- Separate from kernel `QLock`; this is the low-level `Lock` primitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lrand.c

This file implements Plan 9's pseudo-random number generator.

Key behavior:
- `srand` seeds the generator.
- `lrand` returns 31-bit pseudo-random values using a lagged table after initialization.
- `isrand` initializes internal state using Park-Miller constants.

Important details:
- Table length is 607 with tap 273.
- `frand`, `nrand`, `lnrand`, and `rand` build on this generator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/mallocz.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/mallocz.c

This file implements Plan 9's `mallocz`.

Key behavior:
- `mallocz` calls `malloc` and zeroes memory only when `clr` is nonzero.

Important details:
- Returns `nil` if allocation fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/mallocz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan.h

This header declares floating-point special-value helpers.

Key contents:
- `__NaN`, `__Inf`, `__isNaN`, and `__isInf`.

Important details:
- Implemented for this tree in `nan64.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan64.c

This file implements NaN and infinity helpers for 64-bit doubles.

Key behavior:
- `__NaN` constructs a quiet NaN.
- `__Inf` constructs signed infinity.
- `__isNaN` and `__isInf` inspect double bit patterns.

Important details:
- Handles endian/word-order differences with conditional layout logic.
- Used by float parsing/formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/netmkaddr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/netmkaddr.c

This file constructs Plan 9 network address strings.

Key behavior:
- `netmkaddr` combines a linear address with default network and service components when missing.

Important details:
- Understands Plan 9 address separators such as `!`.
- Used by dial/auth networking code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/netmkaddr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nrand.c

This file returns bounded pseudo-random ints.

Key behavior:
- `nrand` scales `lrand()` into `[0, n)`.

Important details:
- Integer counterpart to `lnrand`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nsec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nsec.c

This file returns nanosecond time.

Key behavior:
- `nsec` reads `/dev/bintime`, decodes big-endian seconds/fraction fields, and returns nanoseconds.
- `be2vlong` decodes big-endian 64-bit values.

Important details:
- Caches the opened `/dev/bintime` fd.
- Converts binary time fraction to nanoseconds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nsec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pow10.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pow10.c

This file provides powers of ten for formatting/parsing.

Key behavior:
- `__fmtpow10` returns `10^n` using a static table for common exponents and repeated multiplication for larger values.

Important details:
- Used by floating-point formatting and parsing support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pow10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/print.c

This file implements formatted output to stdout.

Key behavior:
- `print` wraps `vfprint(1, ...)`.

Important details:
- Plan 9 equivalent of printing to fd 1.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushssl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushssl.c

This file pushes Plan 9's SSL device layer over an fd.

Key behavior:
- `pushssl` opens `#D/ssl`, attaches the fd, writes algorithm/secrets to control files, and returns a data fd/control fd.

Important details:
- Uses Plan 9 device-file conventions rather than OpenSSL APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushssl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushtls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushtls.c

This file configures Plan 9 TLS over an fd.

Key behavior:
- `pushtls` opens TLS control/data paths, configures hash/encryption algorithms, role, and secret material.
- `finished` computes TLS finished-label selection for client/server handshakes.

Important details:
- Uses Plan 9 `#a/tls`-style device control rather than a direct TLS library.
- Handles algorithm strings and secret byte formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushtls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rand.c

This file implements libc `rand`.

Key behavior:
- `rand` returns the low 15-bit style value from `lrand`.

Important details:
- Thin compatibility wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/read9pmsg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/read9pmsg.c

This file reads one complete 9P message from an fd.

Key behavior:
- `read9pmsg` reads the 4-byte size prefix, validates it against the caller buffer, then reads the rest with `readn`.

Important details:
- Returns the full message size or `0`/`-1` for EOF/error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/read9pmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/readn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/readn.c

This file implements exact-length reads.

Key behavior:
- `readn` loops until it reads the requested byte count, sees EOF, or gets an error.

Important details:
- Returns bytes actually read.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/readn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rune.c

This file implements UTF-8/Rune conversion primitives.

Key behavior:
- `chartorune` decodes one UTF-8 sequence to a `Rune`.
- `runetochar` encodes one `Rune` as UTF-8.
- `runelen`, `runenlen`, and `fullrune` compute encoded lengths and completeness.

Important details:
- Uses Plan 9 constants such as `Runeself`, `Runeerror`, and `Runemax`.
- Rejects invalid encodings by returning `Runeerror`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runefmtstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runefmtstr.c

This file finalizes dynamically allocated rune-string formatting.

Key behavior:
- `runefmtstrflush` terminates and returns the accumulated `Rune*`.

Important details:
- Rune counterpart to `fmtstrflush`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runefmtstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runeseprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runeseprint.c

This file formats into a bounded rune buffer ending at a pointer.

Key behavior:
- `runeseprint` wraps `runevseprint` with varargs.

Important details:
- Returns the end pointer after formatted output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runeseprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesmprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesmprint.c

This file allocates a formatted rune string.

Key behavior:
- `runesmprint` wraps `runevsmprint` with varargs.

Important details:
- Caller owns the returned allocated buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesmprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesnprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesnprint.c

This file formats into a fixed-length rune buffer.

Key behavior:
- `runesnprint` wraps `runevsnprint` with varargs.

Important details:
- Returns formatted rune count.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesnprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesprint.c

This file formats into an unbounded rune buffer.

Key behavior:
- `runesprint` delegates to `runevsnprint` with a very large bound.

Important details:
- Mirrors Plan 9 `sprint` behavior for rune strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcat.c

This file concatenates rune strings.

Key behavior:
- `runestrcat` appends `s2` to the end of `s1`.

Important details:
- Caller must provide sufficient destination space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrchr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrchr.c

This file searches a rune string forward.

Key behavior:
- `runestrchr` returns the first occurrence of a rune or `nil`.

Important details:
- Can find NUL terminator when searching for zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcmp.c

This file compares rune strings.

Key behavior:
- `runestrcmp` lexicographically compares two NUL-terminated rune strings.

Important details:
- Returns negative, zero, or positive difference.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcpy.c

This file copies rune strings.

Key behavior:
- `runestrcpy` copies `s2` including NUL into `s1`.

Important details:
- Caller must provide enough destination space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrdup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrdup.c

This file duplicates rune strings.

Key behavior:
- `runestrdup` allocates and copies a NUL-terminated rune string.

Important details:
- Returns `nil` on allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrdup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrecpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrecpy.c

This file copies rune strings into a bounded destination.

Key behavior:
- `runestrecpy` copies from `s2` into `[s1, es1)` and NUL-terminates when space allows.

Important details:
- Returns a pointer to the final NUL or end position.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrecpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrlen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrlen.c

This file measures rune strings.

Key behavior:
- `runestrlen` counts runes before the NUL terminator.

Important details:
- Rune counterpart to `strlen`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrlen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncat.c

This file appends a bounded number of runes.

Key behavior:
- `runestrncat` appends up to `n` runes from `s2` to `s1` and terminates.

Important details:
- Caller must provide sufficient destination space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncmp.c

This file compares bounded rune strings.

Key behavior:
- `runestrncmp` compares up to `n` runes from two strings.

Important details:
- Stops at NUL or after `n` runes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncpy.c

This file copies a bounded number of runes.

Key behavior:
- `runestrncpy` copies up to `n` runes and pads with zeroes if source ends early.

Important details:
- Mirrors C `strncpy` semantics for `Rune`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrrchr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrrchr.c

This file searches a rune string backward.

Key behavior:
- `runestrrchr` returns the last occurrence of a rune or `nil`.

Important details:
- Scans forward while remembering the latest match.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrrchr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrstr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrstr.c

This file searches for a rune substring.

Key behavior:
- `runestrstr` returns the first occurrence of `s2` inside `s1`.

Important details:
- Empty needle matches the start of `s1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runetype.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runetype.c

This file contains Unicode rune classification and case-conversion tables.

Key behavior:
- Large static tables define lower/upper/title mappings and alphabetic/space ranges.
- `tolowerrune`, `toupperrune`, and `totitlerune` perform case conversion.
- `islowerrune`, `isupperrune`, `isalpharune`, `istitlerune`, and `isspacerune` classify runes.
- Internal `bsearch` searches range tables.

Important details:
- Data-driven Unicode support for the bundled Plan 9 libc.
- Mostly table payload plus small lookup functions near the end.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runetype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevseprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevseprint.c

This file formats into a bounded rune buffer using a `va_list`.

Key behavior:
- `runevseprint` initializes a rune `Fmt`, dispatches formatting, terminates output, and returns the end pointer.

Important details:
- Pointer-end variant of rune formatted printing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevseprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsmprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsmprint.c

This file allocates formatted rune strings using a `va_list`.

Key behavior:
- `runefmtstrinit` initializes a growable rune formatter.
- `runeFmtStrFlush` grows the buffer when full.
- `runevsmprint` formats, flushes, and returns the allocated rune string.

Important details:
- Rune counterpart to `vsmprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsmprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsnprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsnprint.c

This file formats into a fixed-size rune buffer using a `va_list`.

Key behavior:
- `runevsnprint` initializes a bounded rune `Fmt`, dispatches formatting, and NUL-terminates.

Important details:
- Returns formatted rune count or error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runevsnprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/seprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/seprint.c

This file formats into a bounded byte buffer ending at a pointer.

Key behavior:
- `seprint` wraps `vseprint` with varargs.

Important details:
- Returns the end pointer after formatted output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/seprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/smprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/smprint.c

This file allocates formatted byte strings.

Key behavior:
- `smprint` wraps `vsmprint` with varargs.

Important details:
- Caller owns the returned allocated buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/smprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/snprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/snprint.c

This file formats into a fixed-length byte buffer.

Key behavior:
- `snprint` wraps `vsnprint` with varargs.

Important details:
- Plan 9 equivalent of `snprintf`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/snprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sprint.c

This file formats into an unbounded byte buffer.

Key behavior:
- `sprint` initializes a formatter over the supplied buffer and formats with no practical bound.

Important details:
- Caller must provide enough storage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strecpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strecpy.c

This file copies a C string into a bounded destination.

Key behavior:
- `strecpy` copies from `from` into `[to, e)` and NUL-terminates when possible.

Important details:
- Returns a pointer to the final NUL/end position.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strecpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.c

This file implements decimal string to double conversion for the formatting library.

Key behavior:
- `fmtstrtod` parses sign, decimal digits, exponent, `nan`, and `inf`.
- Helper routines normalize decimal digits, compare against floating representation, and multiply/divide decimal buffers.
- Handles rounding and range errors.

Important details:
- Uses custom arbitrary decimal adjustment rather than delegating to host `strtod`.
- Exposes the Plan 9 formatting-library name `fmtstrtod`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.h

This header declares special floating-point helpers for string-to-double code.

Key contents:
- Declares `__NaN`, `__Inf`, `__isNaN`, and `__isInf`.

Important details:
- The declared return type for `__isNaN`/`__isInf` differs from `nan.h`/`nan64.c`, suggesting an older local header variant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtoll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtoll.c

This file implements signed long long parsing.

Key behavior:
- `strtoll` handles whitespace, sign, base autodetection, digit conversion, and overflow bounds.

Important details:
- Supports base 0, octal, decimal, and hex prefixes.
- Uses `vlong`/`uvlong` Plan 9 integer types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sysfatal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sysfatal.c

This file implements fatal error reporting.

Key behavior:
- `sysfatal` formats an error message, appends current error text for `%r`, writes to fd 2, and exits.
- `_sysfatalimpl` contains the shared `va_list` implementation.

Important details:
- Uses `_exits`/`exits`-style termination.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sysfatal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/time.c

This file implements Plan 9 `time`.

Key behavior:
- `time` reads `/dev/time` and returns seconds.
- `oldtime` is a fallback/helper for older formatted time data.

Important details:
- Caches the time fd where possible.
- Distinct from host POSIX `time`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/tokenize.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/tokenize.c

This file tokenizes strings with Plan 9 shell-like quote handling.

Key behavior:
- `tokenize` splits on whitespace.
- `gettokens` splits on a caller-provided separator set.
- `qtoken` and `etoken` handle quoted strings and doubled quotes.

Important details:
- Tokenization is in-place and NUL-terminates fields.
- Used by auth attribute parsing and command-style inputs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/tokenize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/truerand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/truerand.c

This file returns host-provided random data as an unsigned long.

Key behavior:
- `truerand` calls `randomread` to fill a `ulong`.

Important details:
- Entropy source is provided by the host shim (`posix.c` or `win32.c`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/truerand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u16.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u16.c

This file implements hexadecimal encoding and decoding.

Key behavior:
- `dec16` decodes hex text into bytes.
- `enc16` encodes bytes as lowercase hexadecimal text.

Important details:
- Returns output length or `-1` on invalid input/insufficient output space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u32.c

This file implements base32 encoding and decoding.

Key behavior:
- `dec32` decodes base32 text into bytes.
- `enc32` encodes bytes into base32 text.

Important details:
- Uses Plan 9's base32 alphabet and validates padding/length constraints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u64.c

This file implements base64 encoding and decoding.

Key behavior:
- `dec64` decodes base64 text into bytes.
- `enc64` encodes bytes into base64 text with padding.

Important details:
- Uses a static decode table and standard base64 alphabet.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/u64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utf.h

This header defines Plan 9 UTF/Rune types, constants, and API declarations.

Key contents:
- Defines `Rune` as unsigned int.
- Defines `UTFmax`, `Runesync`, `Runeself`, `Runeerror`, `Runemax`, and `Runemask`.
- Declares UTF conversion/search functions, rune-string functions, and rune classification/case functions.

Important details:
- Shared public header for the bundled UTF/rune implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfdef.h

This header supplies standalone type aliases for UTF code.

Key contents:
- Temporarily maps Plan 9 type names to `_utf*` names and typedefs byte/integer aliases.
- Defines `nelem` and `nil`.

Important details:
- Used to compile UTF components in environments where Plan 9 base headers may conflict.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfecpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfecpy.c

This file copies UTF-8 strings into a bounded buffer without cutting a rune.

Key behavior:
- `utfecpy` copies from source into `[to, e)` and backs off to a valid UTF boundary before NUL-terminating.

Important details:
- Used for safe error-string copying.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfecpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utflen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utflen.c

This file counts runes in a UTF-8 string.

Key behavior:
- `utflen` walks a NUL-terminated UTF-8 string and counts decoded runes.

Important details:
- Uses `chartorune` for multibyte sequences.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utflen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfnlen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfnlen.c

This file counts runes in a bounded UTF-8 byte range.

Key behavior:
- `utfnlen` counts complete runes within at most `m` bytes.

Important details:
- Stops before incomplete trailing UTF sequences.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfnlen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrrune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrrune.c

This file searches a UTF-8 string for the last occurrence of a rune.

Key behavior:
- `utfrrune` scans decoded runes and remembers the most recent match.

Important details:
- Handles ASCII fast paths and multibyte decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrrune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrune.c

This file searches a UTF-8 string for the first occurrence of a rune.

Key behavior:
- `utfrune` returns a pointer to the first matching encoded rune or `nil`.

Important details:
- Handles ASCII fast paths and multibyte decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfutf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfutf.c

This file searches for a UTF-8 substring.

Key behavior:
- `utfutf` finds the first occurrence of `s2` in `s1`.

Important details:
- Uses byte substring search with UTF-aware first-rune positioning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfutf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vfprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vfprint.c

This file formats a `va_list` to an fd.

Key behavior:
- `vfprint` initializes an fd-backed `Fmt`, dispatches formatting, and flushes.

Important details:
- Shared backend for `print` and `fprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vfprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vseprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vseprint.c

This file formats a `va_list` into a bounded byte buffer ending at a pointer.

Key behavior:
- `vseprint` initializes a bounded `Fmt`, dispatches formatting, terminates output, and returns the end pointer.

Important details:
- Pointer-end counterpart to `vsnprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vseprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsmprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsmprint.c

This file allocates formatted byte strings using a `va_list`.

Key behavior:
- `fmtstrinit` initializes a growable byte formatter.
- `fmtStrFlush` grows the buffer when full.
- `vsmprint` formats and returns the allocated NUL-terminated string.

Important details:
- Byte-string counterpart to `runevsmprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsmprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsnprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsnprint.c

This file formats a `va_list` into a fixed-size byte buffer.

Key behavior:
- `vsnprint` initializes a bounded `Fmt`, dispatches formatting, and NUL-terminates.

Important details:
- Returns formatted byte count or error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsnprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/Makefile

This Makefile builds drawterm's `libdraw.a`.

Key contents:
- Includes `../Make.config`.
- Archives a small draw support library: allocation, arithmetic, bytes-per-line, channel parsing, default font, replication drawing, trig helpers, rectangle clipping, and RGB helpers.
- Uses `$(CC) $(CFLAGS)` and archive commands.

Important details:
- The listed sources are not part of this work item, but the Makefile establishes the draw library boundary used by drawterm GUI/kernel code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/Makefile -->