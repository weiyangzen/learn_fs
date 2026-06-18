# Group Research: illumos STREAMS stream head and string extensions

Scope: `Docs/research_subset_a.md`

Files read completely:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/os/streamio.c` (8,751 lines)
- `sources/os/illumos/illumos-gate/usr/src/uts/common/os/strext.c` (170 lines)

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/streamio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/streamio.c

## Purpose

`streamio.c` is the illumos STREAMS stream-head implementation for stream open/close, read/write, `ioctl(2)`, `getmsg(2)`, `putmsg(2)`, polling, signal delivery, module plumbing, descriptor passing, and pipe/FIFO stream mating. It is not filesystem code directly, but it is in subset A because STREAMS-backed character devices, FIFOs, pipes, terminals, sockets, and multiplexors sit at the vnode/VFS boundary and rely on this file for vnode-to-stream lifecycle and I/O semantics.

The file owns the default read and write queue procedures for stream heads:
- `strdata` / `stwdata` for normal stream heads.
- `fifo_strdata` / `fifo_stwdata` for FIFO/pipe stream heads.
- `strrput()` as the read-side put procedure.
- `strwsrv()` as the write-side service procedure.

## Major Entry Points

- `stropen(vnode_t *vp, dev_t *devp, int flag, cred_t *crp)`: creates a stream head for a vnode or reopens an existing stream. It initializes `stdata`, attaches the driver, handles clone opens, DLD/per-driver autopush, optional `drcompat`, FIFO defaults, stream anchors, XPG4 PTY fixups, and cached downstream packet-size limits.
- `strclose(struct vnode *vp, int flag, cred_t *crp)`: last-close teardown. It marks hangup, removes remaining signal registrations, unlinks multiplexor links, drains downstream queues according to close timeout, detaches modules/driver, handles half-closed pipes/twisted streams, flushes queues, tears down poll state, clears vnode stream pointers, and frees stream state.
- `strclean()` / `strcleanall()` / `str_cn_clean()`: remove per-process or stale signal registrations from `sd_siglist`.
- `strread()`: implements byte-stream and message-mode read semantics, including `RD_MSGDIS`, `RD_MSGNODIS`, `RD_PROTDAT`, `RD_PROTDIS`, zero-length EOF behavior, mark/delimiter handling, `M_SIG`, `M_PASSFP`, `M_PROTO`, and `M_PCPROTO` handling.
- `strwrite()` / `strwrite_common()`: split writes according to downstream min/max packet sizes, enforce flow control and job-control access, honor `OLDNDELAY`, `STRDELIM`, `SW_RECHECK_ERR`, and map allocation failures back to historic `EAGAIN`.
- `strioctl()`: the large STREAMS ioctl dispatcher. It handles native stream ioctls, terminal/keyboard/mouse transparent-to-`I_STR` conversion, module push/pop/insert/remove/anchor operations, multiplexor link/unlink operations, signal registration, peek/read-count queries, descriptor passing, controlling-terminal operations, and fallback transparent ioctls.
- `strdoioctl()`: sends an `M_IOCTL` downstream, serializes ioctl ownership with `IOCWAIT`/`IOCWAITNE`, waits for `M_IOCACK`/`M_IOCNAK`, services `M_COPYIN`/`M_COPYOUT`, handles transparent ioctls, timeout/interruption, duplicate replies, credentials, and cleanup.
- `strdocmd()`: ptools-oriented `M_CMD` request/reply path that avoids normal ioctl copyin/copyout and flow-control behavior.
- `strgetmsg()` / `kstrgetmsg()`: user and kernel message receive APIs, including priority/band selection, partial control/data returns, mark preservation, peek/discard-tail/private flags, synchronous stream integration, and wakeup/signal recalculation after dequeue.
- `strputmsg()` / `kstrputmsg()`: user and kernel message send APIs, including control/data construction, priority validation, flow-control waits, `MSG_IGNFLOW`, `MSG_IGNERROR`, `MSG_HOLDSIG`, and `SW_SIGPIPE` behavior.
- `strpoll()`: computes STREAMS poll readiness for read/write/band/priority/hangup/error events, sets backenable/wakeup flags, supports `POLLNOERR`, `POLLRDDATA`, and edge-trigger registration.
- `do_sendfp()` and `free_passfp()`: implement file-descriptor passing with `M_PASSFP`, including file reference ownership and custom message free routine.
- `strq2vp()`, `strvp2wq()`, `strpollwakeup()`, and `strmate()`: helper APIs for queue/vnode conversion, external poll wakeups, and mating two stream heads for pipes/FIFOs.

## Internal Flow And Semantics

Open and plumbing paths use `STWOPEN`, `STRCLOSE`, and `STRPLUMB` as stream-head monitors. `stropen()` serializes initial stream creation through `v_lock`, initializes `sd_*` fields, attaches queue info, opens drivers/modules through `qattach()`/`qreopen()`, and updates cached downstream `q_minpsz`/`q_maxpsz`. `I_PUSH`, `I_POP`, `_I_INSERT`, and `_I_REMOVE` use `strstartplumb()`/`strendplumb()` plus `sd_anchor`/`sd_anchorzone` checks to serialize and constrain module stack mutations.

Read-side handling is split between `strrput()`/`strrput_nondata()` arrival processing and `strread()`/`strgetmsg()`/`kstrgetmsg()` consumption. Data and protocol messages are queued with signal and poll metadata; control messages such as `M_ERROR`, `M_HANGUP`, `M_FLUSH`, `M_IOCACK`, `M_IOCNAK`, `M_COPYIN`, `M_COPYOUT`, `M_SETOPTS`, and `M_CMD` update stream state or wake blocked callers. Mark tracking uses `MSGMARK`, `MSGMARKNEXT`, `MSGNOTMARKNEXT`, `sd_mark`, `STRATMARK`, and `STRNOTATMARK`; tail putback must preserve these flags across partial reads.

Write-side handling uses `strwriteable()` for hangup/error/plex checks and optional `SIGPIPE`, then `strput()` to build and deliver messages. `strput()` chooses between normal `canputnext()`/`strmakedata()`/`putnext()` and synchronous-stream `rwnext()` paths. `strwsrv()` handles writer wakeups, normal and banded poll wakeups, and signal delivery when downstream flow control clears.

The ioctl path has several layers. `strioctl()` classifies job-control behavior, applies stream-head checks, handles hardcoded STREAMS ioctls directly, wraps many legacy terminal/keyboard/mouse ioctls into `struct strioctl`, and sends unknown commands as transparent ioctls. `strdoioctl()` owns the downstream `M_IOCTL` transaction and intermediate copy requests. It also treats `STR_NOERROR` internal ioctls specially so link/unlink paths can recover from lost ioctl replies.

Descriptor passing uses `M_PASSFP` messages on the peer stream-head read queue. `do_sendfp()` locates the peer queue for mated or twisted streams, allocates an external-buffer message containing `struct k_strrecvfd`, increments the sent file reference, and relies on `free_passfp()` to close the reference when the message is freed. `I_RECVFD`/`I_E_RECVFD` allocate a new fd, copy old or extended receive metadata to the caller, increment the file reference for the fd table, and free the message.

## State, Locking, And Data Dependencies

Primary mutable state lives in `struct stdata`: `sd_flag`, `sd_read_opt`, `sd_wput_opt`, `sd_rput_opt`, `sd_copyflag`, `sd_wrq`, `sd_vnode`, `sd_mate`, `sd_siglist`, `sd_pollist`, `sd_iocblk`, `sd_cmdblk`, `sd_iocid`, `sd_mark`, `sd_qn_minpsz`, `sd_qn_maxpsz`, `sd_maxblk`, `sd_wroff`, `sd_tail`, `sd_anchor`, `sd_anchorzone`, `sd_closetime`, controlling-terminal pids, and synchronous-stream hooks/queues.

Important locks and wait objects:
- `vp->v_lock` protects vnode-to-stream association during open/close.
- `stp->sd_lock` protects stream-head flags, monitors, signals, ioctl/cmd state, marks, and most state transitions.
- Queue locks via `QLOCK(q)` protect queue contents, watermarks, bands, and flow-control flags.
- `claimstr()`/`releasestr()` stabilize stream plumbing while walking queues.
- `strresources` protects global `ioc_id`.
- `muxifier` serializes multiplexor link lookup/mutation.
- `pidlock` protects process/session/process-group pid structures.
- `sd_monitor`, `sd_iocmonitor`, queue wait CVs, `str_cv_wait()`, and `strwaitq()` provide blocking semantics for reads, writes, ioctls, command replies, and plumbing/open/close waits.

## External Dependencies

This file depends on the core illumos STREAMS substrate: queues, sync queues, message blocks, queue bands, `qattach()`, `qdetach()`, `qreopen()`, `putnext()`, `putq()`, `getq_noenab()`, `flushq_common()`, `canputnext()`, `bcanputnext()`, `rwnext()`, `infonext()`, `strmakedata()`, `strmakemsg()`, `strmakectl()`, `putiocd()`, `getiocd()`, `strwaitq()`, `strwaitbuf()`, `straccess()`, `strgeterr()`, and STREAMS signal/poll helpers.

It also integrates with vnode/specfs state, FIFOs, sockfs/synchronous streams, terminal/session/job-control code, process and pid management, DLD/autopush/netstack state, STREAMS administrative autopush (`sad`), file descriptor tables, auditing, privilege policy checks, LDI multiplexor linking, and legacy terminal/keyboard/mouse ioctl ABIs.

## Risks And Maintenance Notes

The highest-risk behavior is concurrency around stream plumbing, read/write flow control, ioctl ownership, and mark handling. `sd_lock`, queue locks, and stream claims are intentionally interleaved; changing lock order or dropping locks around copyin/copyout can introduce missed wakeups, stale queue pointers, duplicate ioctl replies, or deadlocks.

The stream-head message semantics are compatibility-sensitive. Zero-length `M_DATA`, `M_PASSFP`, `M_PROTO`/`M_PCPROTO`, `M_SIG`, `M_FLUSH`, `M_ERROR`, `M_HANGUP`, mark/delimiter flags, banded messages, and high-priority protocol messages all have legacy-visible behavior. Small changes can affect terminals, sockets, pipes, FIFOs, multiplexors, and third-party STREAMS modules.

The ioctl dispatcher contains intentionally hardcoded legacy command knowledge. Comments explicitly warn against adding new transparent-to-`I_STR` conversions and against casually removing old ones, because existing drivers/modules may rely on stream-head conversion behavior.

`strdoioctl()` and `strdocmd()` are sensitive to message ownership and credential reference management. Every path that changes a message type, detaches `b_cont`, times out, or replies with `M_IOCDATA` must preserve downstream expectations and avoid leaking credentials, file references, or message blocks.

Pipe/FIFO and mated-stream behavior is special. `strclose()`, `strmate()`, and `do_sendfp()` must distinguish single-vnode FIFO twists, two-ended pipes, half-closed pipe dead ends, and normal driver-backed streams.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/streamio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strext.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strext.c

## Purpose

`strext.c` provides small SunOS-specific kernel string/formatting helpers that are not part of the shared standalone/libc string implementation. The file is compact and self-contained, relying mainly on `vsnprintf()`, kernel allocation, and simple character scanning.

## Entry Points

- `vsprintf_len(size_t buflen, char *buf, const char *fmt, va_list args)`: historical bounded formatting wrapper. It calls `vsnprintf(buf, buflen, fmt, args)` and returns `buf`.
- `sprintf_len(size_t buflen, char *buf, const char *fmt, ...)`: variadic companion to `vsprintf_len()`, also returning `buf`.
- `numtos(unsigned long num, char *s)`: converts an unsigned long to a decimal NUL-terminated string. It uses a local reverse buffer and assumes the caller provided enough output space.
- `stoi(char **str)`: parses decimal digits from `*str`, returns the integer value, and updates `*str` to the first non-digit. It performs no overflow checking.
- `strnrchr(const char *sp, int c, size_t n)`: bounded reverse character search over at most `n` non-NUL characters. Unlike a raw bounded memory search, a terminating NUL stops the scan and is not itself considered part of the searchable string.
- `sprintf(char *buf, const char *fmt, ...)`: kernel DDI-compatible `sprintf()` that returns `buf`, implemented via `vsnprintf(buf, INT_MAX, ...)`.
- `vsprintf(char *buf, const char *fmt, va_list args)`: `vsprintf()` variant with the same return convention and effectively unbounded `INT_MAX` limit.
- `kmem_asprintf(const char *fmt, ...)`: allocates a formatted string with `kmem_alloc(KM_SLEEP)`, sizing it through a first `vsnprintf(NULL, 0, ...)` pass. The comment states callers must free the exact returned string with `strfree()`.

## Dependencies

Headers used are `sys/types.h`, `sys/cmn_err.h`, `sys/systm.h`, and `sys/varargs.h`. Runtime dependencies are kernel `vsnprintf()`, `kmem_alloc()`, `KM_SLEEP`, `INT_MAX`, and the corresponding string-freeing convention for `kmem_asprintf()` callers.

## Risks And Maintenance Notes

The historical formatting helpers return the destination buffer rather than the formatted length. Callers may depend on this DDI/SunOS behavior, so replacing them with standard libc-like return values would be ABI-visible.

`numtos()` and `stoi()` are intentionally minimal. `numtos()` has no output-size parameter, and `stoi()` does no overflow detection and accepts only decimal digits. They should only be used where callers already bound inputs and storage.

`sprintf()` and `vsprintf()` pass `INT_MAX` to `vsnprintf()`, so safety depends on the caller supplying a sufficiently large buffer. New code should prefer bounded helpers where practical.

`kmem_asprintf()` performs two formatting passes and allocates with sleeping semantics. It is unsuitable for contexts that cannot sleep, and callers must use the expected freeing path rather than assuming a normal static or stack buffer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/strext.c -->