# Group Research: group_1622_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_kern_devaudi_3110505fd2fa

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-unix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-unix.c

Implements the Unix/BSD backend for drawterm audio using OSS-style `/dev/dsp` and `/dev/mixer`.

Key behavior:
- Opens `/dev/dsp` for output and `/dev/mixer` for mixer control.
- Configures 16-bit stereo output at 44100 Hz through `SNDCTL_DSP_*` ioctls.
- Maps Plan 9 volume IDs to OSS mixer IDs for audio, bass, treble, line, pcm, synth, cd, mic, and speaker.
- Implements volume get/set and speed get/set.
- Implements audio writes as a full-write loop.
- Does not implement recording; `audiodevread` always errors with `"no reading"`.

Dependencies:
- `devaudio.h` supplies the abstract audio operations and volume IDs.
- Uses host OSS headers: Linux `<linux/soundcard.h>` or BSD `<sys/soundcard.h>`.
- Reports host errors through `oserror()`.

Notable risks:
- The backend assumes legacy OSS devices exist.
- `audiodevsetvol` writes `-1` into one channel when the higher layer asks for left-only or right-only changes; the OSS packed mixer value path does not preserve the existing opposite channel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.c

Implements Plan 9 device `#A/audio`, exposing `audio` and `volume` files above a platform-specific backend.

Key behavior:
- Provides directory entries `.`, `audio`, and `volume`.
- Serializes `/audio` use through `audio.amode`; only one active reader or writer is allowed.
- Opens the backend on `/audio` open and closes it on final close.
- Reads from `volume` by querying every known control and formatting Plan 9-style volume lines.
- Writes to `volume` by parsing commands such as volume names, `reset`, `in`, `out`, `left`, `right`, and numeric values.
- Writes to `audio` call `audiodevwrite`; reads call `audiodevread`.
- Registers `audiodevtab` as device character `A`.

Important interfaces:
- `audiodevopen`, `audiodevclose`, `audiodevread`, `audiodevwrite`, `audiodevgetvol`, `audiodevsetvol`.
- `parsecmd` is used for textual volume commands.
- `audioswab` provides 32-bit byte swapping, though it is not used in this file.

Notable risks:
- The generic device accepts read mode for `/audio`, but the Unix backend does not support reads.
- Volume parsing has no explicit range checks before backend calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.h

Defines shared audio constants and the backend function contract for `devaudio.c`.

Contents:
- Flags: `Fmono`, `Fin`, `Fout`.
- Volume IDs: `Vaudio`, `Vsynth`, `Vcd`, `Vline`, `Vmic`, `Vspeaker`, `Vtreb`, `Vbass`, `Vspeed`, `Vpcm`, and `Nvol`.
- Backend prototypes for open, close, read, write, get volume, and set volume.

Role:
- Separates the Plan 9 `#A` device implementation from host-specific audio implementations such as `devaudio-unix.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devcons.c

Implements the Plan 9 console device `#c`, including console I/O, keyboard processing, time files, random/zero/null, host identity files, reboot control, clipboard bridge, and diagnostic output.

Key behavior:
- Initializes `kbdq` and `lineq` queues for raw and cooked keyboard input.
- Implements `print`, `panic`, `pprint`, `iprint`, console flushing, and `/dev/kprint`.
- Handles cooked console editing for backspace, line kill, newline, and EOF.
- Supports raw mode and `ctlpoff`/`ctlpon` through `consctl`.
- Handles keyboard compose sequences through `latin1`.
- Exposes files such as `cons`, `consctl`, `time`, `bintime`, `random`, `zero`, `null`, `drivers`, `hostowner`, `hostdomain`, `sysname`, `snarf`, `secstore`, and `reboot`.
- Reads textual and binary time using `todget`, `fastticks`, and little-endian packing helpers.
- Allows privileged writes to `time`, `bintime`, and `reboot`.

Important interfaces:
- `readnum` and `readstr` are general helpers used across other devices.
- `kbdputc` and `kbdcr2nl` are input entry points.
- `consdevtab` registers device character `c`.

Notable risks:
- Several control files are simplified drawterm adaptations; `sysstat` and `swap` are mostly stubs.
- `secstorebuf` is a fixed 64 KiB in-memory buffer.
- `snarf` bridges to host clipboard via `clipread` and `clipwrite`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devdraw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devdraw.c

Implements the Plan 9 draw device `#i/draw`, mapping draw protocol messages onto drawterm’s host-backed `memdraw` screen.

Key behavior:
- Maintains global draw state in `sdraw`: clients, named images, screen image, flush rectangles, blanking state, and color map backup.
- Exposes top-level `draw`, `new`, per-client directories, and client files `ctl`, `data`, `refresh`, and `colormap`.
- Allocates clients through `new`; each client owns image hash tables, screens, refresh queues, and pending read data.
- Initializes the real screen with `attachscreen` and wraps it as a `Memimage`.
- Implements image install/uninstall, named image management, screen/window allocation, reference counting, and refresh notifications.
- Parses packed draw messages for image allocation, screen allocation, draw, line, polygon, ellipse, font, string, readimage, writeimage, window ordering, clip/repl, named images, and flush.
- Batches screen flushing with rectangle coalescing through `addflush`, `dstflush`, and `drawflush`.
- Provides colormap read/write and default 8-bit colormap loading.

Important interfaces:
- `drawmesg` is the protocol command dispatcher.
- `drawread` returns control info, colormap text, pending image data, or refresh rectangles.
- `drawwrite` handles control IDs, colormap updates, and draw protocol data.
- `drawdevtab` registers device character `i`.

Notable risks:
- This is stateful and relies heavily on correct reference counts for images, named-image aliases, and screens.
- `drawhasclients` intentionally prevents framebuffer resize after any draw client has ever existed.
- Debug printing is mostly disabled by constant conditions in `printmesg`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-posix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-posix.c

Implements host POSIX filesystem access as Plan 9 device `#U/fs`.

Key behavior:
- Uses `base = "/"` and builds host paths from Plan 9 channel names.
- Supports attach, clone, walk, stat, open, create, close, read, write, remove, and wstat.
- Uses POSIX `stat`, `open`, `read`, `write`, `lseek`, `mkdir`, `chmod`, `chown`, `opendir`, `readdir`, `closedir`, `rmdir`, `remove`, and `rename`.
- Tracks per-channel host metadata and open state in `Ufsinfo`.
- Packs directory entries into Plan 9 `Dir` records with owner/group set to `"unknown"`.
- Computes synthetic qids from host device plus a simple path hash, with version from `st_mtime`.

Important interfaces:
- `fsqid` maps host stat/path data to Plan 9 qids.
- `fspath` creates cleaned host paths.
- `fsdirread` implements directory enumeration with offset discipline and one-entry carryover.

Notable risks:
- Uses fixed `MAXPATH` and `NAME_MAX` buffers with `strcpy`/`strcat`.
- Qid path hashing is weak and path-derived, not inode-derived.
- Directory seeking only supports offset reset to zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-posix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-win32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-win32.c

Implements the Windows variant of host filesystem device `#U/fs`.

Key behavior:
- Disables Windows Unicode APIs and uses narrow-character `FindFirstFile`/`FindNextFile`.
- Uses `base = "c:/."`.
- Mirrors the POSIX implementation’s Plan 9 device operations: attach, walk, stat, open, create, read, write, remove, and wstat.
- Opens regular files in binary mode with `_O_BINARY`.
- Provides a local `DIR` abstraction around Windows file enumeration.
- Implements no-op `chown`.
- Packs directory entries into Plan 9 `Dir` records with owner/group set to `"unknown"`.

Important interfaces:
- Same `fsqid`, `fspath`, `fsdirread`, and `fsomode` structure as POSIX variant.
- Custom `opendir`, `readdir`, `rewinddir`, and `closedir`.

Notable risks:
- Narrow-character Windows API use means non-ASCII paths are not represented correctly.
- `opendir` appends `*.*`, matching Windows-era conventions.
- Uses fixed-size path buffers and simple string concatenation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-posix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-posix.c

Provides the POSIX socket backend used by `devip.c`.

Key behavior:
- Chooses `AF_INET` for v4-mapped Plan 9 addresses and `AF_INET6` otherwise.
- Implements socket creation for TCP and UDP.
- Sets `TCP_NODELAY` on sockets.
- Implements connect, bind, listen, accept, send, receive, getsockname, service lookup, and host lookup.
- Converts between Plan 9 16-byte IP addresses and POSIX IPv4/IPv6 socket structures.
- Initializes `sysname` from `gethostname`.

Important interfaces:
- Implements all `so_*` functions declared in `devip.h`.
- `hostlookup` uses `gethostbyname` first and falls back to `getaddrinfo`.

Notable risks:
- The privileged-bind path writes port `i` directly into sockaddr fields without `hnputs`, unlike the normal bind path.
- `so_gethostbyname` only formats IPv4 hostent results.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-posix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-win32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-win32.c

Provides the Windows Winsock backend used by `devip.c`.

Key behavior:
- Initializes Winsock with `WSAStartup`.
- Initializes `sysname` from `gethostname`.
- Implements the same `so_*` socket abstraction as the POSIX backend.
- Supports TCP and UDP sockets, connect, bind, listen, accept, send, receive, service lookup, and host lookup.
- Converts Plan 9 IP addresses to IPv4/IPv6 socket addresses.

Notable differences from POSIX:
- Uses `int` for socket address lengths.
- `hostlookup` returns the original host string when resolution fails, rather than returning `nil`.
- Uses Winsock headers and optional MSVC library pragma.

Notable risks:
- Same privileged-bind byte-order issue as POSIX.
- Host lookup is mostly IPv4-oriented in the `gethostbyname` path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.c

Implements Plan 9 network device `#I` with `/net/cs`, `/net/udp`, and `/net/tcp` style conversation directories.

Key behavior:
- Creates `udp` and `tcp` protocols with fixed maximum conversation counts.
- Exposes protocol directories, `clone`, conversation directories, and files `data`, `ctl`, `status`, `remote`, `local`, and `listen`.
- Allocates and reuses `Conv` objects with reference counts, owner, permissions, local/remote addresses, ports, state, and host socket fd.
- `ctl` accepts `connect`, `announce`, and `bind`.
- `listen` accepts on a listening socket and returns a new conversation.
- `data` reads and writes through backend `so_recv`/`so_send`.
- `cs` translates `net!host!service` into `/net/proto/clone ip!port`.

Important interfaces:
- Relies on `devip.h` backend functions for OS sockets.
- Uses Plan 9 IP helpers from `ip.h`.
- `ipdevtab` registers device character `I`.

Notable risks:
- `announce` calls `so_listen` after `setladdrport`, which creates/binds the socket; TCP listen semantics are assumed by backend.
- `ipread`/`ipwrite` call `nexterror()` after socket errors without a local `waserror` frame in those branches, relying on caller context.
- Conversation counts are small: UDP 10, TCP 30.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.h

Defines the OS socket abstraction used by `devip.c`.

Contents:
- Protocol identifiers `S_TCP` and `S_UDP`.
- Prototypes for socket create/connect/bind/listen/accept/send/recv/getsockname.
- Prototypes for service and host lookup helpers.
- `hostlookup` returns a string representation suitable for Plan 9 IP parsing.

Role:
- Keeps core Plan 9 network device logic independent of POSIX vs Winsock details.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devlfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devlfd.c

Wraps an existing host file descriptor as a Plan 9 `Chan` under device `#L`.

Key behavior:
- `lfdchan` creates a new channel whose `aux` holds the host fd.
- `lfdfd` installs such a channel into the Plan 9 fd table.
- Attach, walk, stat, and open are invalid and return `Egreg`.
- Close closes the underlying host fd.
- Read and write call host `read`/`write`; offsets are ignored because descriptors may be pipes.

Role:
- Provides a bridge for host descriptors used by drawterm internals, mount channels, or exports.

Notable risks:
- Always sets channel mode to `ORDWR`.
- Has no stat metadata and no seek support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devlfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmnt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmnt.c

Implements Plan 9 mount device `#M`, the 9P client and RPC multiplexer for mounted remote file servers.

Key behavior:
- Negotiates `Tversion/Rversion` once per server channel and creates an `Mnt` mux object.
- Implements attach/auth, walk, stat, open, create, clunk, remove, wstat, read, and write by building 9P `Fcall` requests.
- Allocates RPC tags from a bitmap and reuses `Mntrpc` objects.
- Queues outstanding RPCs on a mount connection and matches replies by tag.
- Gates transport reads so only one process reads from the shared server channel at a time.
- Supports flush allocation and cleanup for interrupted RPCs.
- Fixes returned directory entries to use local device type/dev numbers.
- Supports optional cache integration through `CCACHE`, `cread`, `cwrite`, and `cupdate`.

Important interfaces:
- `mntversion`, `mntauth`, and `mntchan` are callable outside the devtab methods.
- `mountrpc`, `mountio`, `mntrpcread`, and `mountmux` are the core RPC path.
- `mntdevtab` registers device character `M`.

Notable risks:
- Correctness depends on tag lifecycle and serialized shared-channel reads.
- `mntchk` panics on inconsistent channel/mount state.
- Reply message sizes greater than negotiated `msize` cause queue discard and mount RPC failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmnt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmouse.c

Implements mouse and cursor device `#m`.

Key behavior:
- Exposes `.`, `cursor`, and `mouse`.
- Allows only one open of `mouse`.
- Reading `cursor` returns cursor offset, clear mask, and set mask.
- Writing `cursor` installs a supplied cursor, or resets to arrow if the payload is too short.
- Reading `mouse` blocks until queued mouse movement/button data or a screen reshape event is available.
- Mouse events are returned in Plan 9 textual format beginning with `m`; reshape events begin with `t`.
- Writing `mouse` can reposition the host pointer through `mouseset`.

Dependencies:
- Uses global `mouse`, `cursor`, `screen`, `gscreen`, and screen cursor hooks from drawterm screen code.

Notable risks:
- Single-reader mouse model matches Plan 9 semantics but limits concurrent consumers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devpipe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devpipe.c

Implements Plan 9 pipe device `#|`.

Key behavior:
- A pipe has two queues and exposes `data` and `data1`.
- Writes to one end are read from the other end.
- Queue size defaults to 256 KiB on multiprocessor configurations, 32 KiB otherwise.
- Tracks references to the pipe and per-end open counts.
- Closing the final open reference on either side hangs up the opposite queue.
- Reopens queues when both ends are closed, making the pipe reusable until final channel references drop.
- Supports block read/write through `qbread` and `qbwrite`.

Important interfaces:
- Uses `NETQID`, `NETID`, and `NETTYPE` macros from `netif.h` for qid layout.
- `pipedevtab` registers device character `|`.

Notable risks:
- Write errors post a user note `"sys: write on closed pipe"` unless the channel is a mounted message channel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devroot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devroot.c

Implements the synthetic root device `#/`.

Key behavior:
- Builds static root, boot, and mnt directory lists.
- Root initially contains `boot`, `mnt`, plus directories added in `rootreset`: `bin`, `dev`, `env`, `fd`, `net`, `net.alt`, `proc`, `root`, and `srv`.
- `mnt` contains `factotum`.
- `addbootfile` adds in-memory files under `boot`.
- Directory reads use `rootgen`; regular boot/mnt file reads copy from stored in-memory data.
- Writes are rejected.

Important interfaces:
- `addbootfile` is an external helper for boot-time synthetic files.
- `rootdevtab` registers device character `/`.

Notable risks:
- Directory capacities are fixed (`Nrootfiles`, `Nbootfiles`, `Nmntfiles`).
- Some fallback logic in `rootread` defaults non-boot/non-mnt files to `bootlist`, but normal access should be constrained by generated qids.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devssl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devssl.c

Implements old Plan 9 `#D/ssl`, a record wrapper providing SSL-style framing, optional digesting, and optional encryption over an existing channel.

Key behavior:
- Exposes `ssl`, `clone`, per-connection directories, `ctl`, `data`, `secretin`, `secretout`, `encalgs`, and `hashalgs`.
- Creates up to 128 `Dstate` records.
- `ctl` accepts an fd binding and algorithm configuration.
- Secrets are written directly or base64-decoded through control commands.
- Supports clear, digest-only, encryption-only, or digest+encryption states.
- Implements SSL-style record headers with optional padding.
- Maintains independent input/output secrets, crypto states, and message sequence IDs.
- Reads parse records, decrypt, verify digest, remove padding, and return application data.
- Writes split data into records, add digest, add padding, encrypt, and write to the wrapped channel.

Algorithms:
- Hashes: MD4, MD5, SHA1/SHA.
- Encryption: DES CBC/ECB and RC4 variants, including 40-bit compatibility variants.

Notable risks:
- This is legacy SSL-style crypto, not modern TLS.
- It permits weak algorithms by design.
- It explicitly refuses to wrap another `#D/ssl` file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devssl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtab.c

Defines the drawterm kernel device table.

Registered devices, in order:
- `rootdevtab` (`#/`)
- `consdevtab` (`#c`)
- `pipedevtab` (`#|`)
- `ssldevtab` (`#D`)
- `tlsdevtab` (`#a`)
- `mousedevtab` (`#m`)
- `drawdevtab` (`#i`)
- `ipdevtab` (`#I`)
- `fsdevtab` (`#U`)
- `mntdevtab` (`#M`)
- `lfddevtab` (`#L`)
- `audiodevtab` (`#A`)

Role:
- Central dispatch table used by `devno`, `devtab[c->type]`, and namespace/device resolution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtls.c

Implements Plan 9 TLS device `#a/tls`, a TLS 1.0 / SSL 3.0 record-layer engine over an existing channel.

Key behavior:
- Exposes `tls`, `clone`, `encalgs`, `hashalgs`, and per-connection `ctl`, `data`, `hand`, `status`, and `stats`.
- Separates handshake traffic (`hand`) from application data (`data`).
- Supports state transitions for closed, handshaking, open, remote/local close, alerting, and errored states.
- Reads TLS records from the wrapped channel, validates version and length, decrypts, checks MAC, handles alerts, queues handshake records, and exposes application records.
- Writes handshake/application records with headers, MAC, optional encryption, and change-cipher handling.
- Supports SSL2-format initial ClientHello compatibility for handshakers.
- `ctl` supports `fd`, `version`, `secret`, `changecipher`, `opened`, `alert`, and `debug`.
- Tracks byte counters for data and handshake input/output.

Algorithms:
- Hashes: clear, MD5, SHA1.
- Encryption: clear, RC4-128, 3DES-EDE-CBC.
- Uses SSL3-specific MAC packing for SSL3 and HMAC-style packing for TLS1.0.

Important interfaces:
- Handshake policy and certificate logic are outside this file; this is the record layer.
- `tlsdevtab` registers device character `a`.

Notable risks:
- Maximum TLS devices grow from 128 to 1024.
- Only old SSL3/TLS1.0-era algorithms are implemented.
- Error handling sends TLS alerts and wakes the handshake queue with textual errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devtls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.c

Defines global error string objects used throughout the drawterm kernel device and namespace code.

Contents:
- Common namespace/device errors such as `Enonexist`, `Eexist`, `Enotdir`, `Eisdir`, `Ebadsharp`, and `Eperm`.
- I/O and resource errors such as `Eio`, `Ehungup`, `Etimedout`, `Enomem`, and `Enofd`.
- Mount and union errors such as `Emount`, `Eunmount`, `Eunion`, and `Emountrpc`.
- Control and stat errors such as `Ebadctl`, `Ebadarg`, `Eshortstat`, `Ebadstat`, and `Ecmdargs`.

Role:
- Provides stable string addresses and text for `error()` calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.h

Declares the global error strings defined in `error.c`.

Role:
- Lets device and kernel code refer to shared error constants as extern `char[]`.
- Keeps error spellings centralized while allowing direct pointer/string use in `error()` and comparisons.

Notable detail:
- Comments mirror the human-readable meaning of each error constant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/exportfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/exportfs.c

Implements a local exportfs server: it serves the current namespace over a 9P-like stream.

Key behavior:
- `sysexport(fd)` wraps an open fd as the transport, captures the current process group and root, and enters `exportproc`.
- Reads incoming messages, handles partial message carryover, decodes `Fcall`s, and dispatches them to worker threads.
- Maintains `Export` state with root channel, io channel, process group, active fid hash, and work queue.
- Handles `Tflush` by removing queued work or interrupting in-progress work and sending `Rflush`.
- Worker threads run requests in the exported process group, dispatch through the `fcalls` table, and serialize replies.
- Tracks `Fid` objects with reference counts, attached state, and underlying `Chan`.

Implemented operations:
- `Tversion`, `Tauth`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- Authentication is not required.
- Reads and writes dispatch to the underlying device operations on the local channel.

Notable risks:
- `Nfidhash` is 1, so all fids share one hash bucket.
- The file contains older protocol assumptions such as `DIRLEN` alignment for directory reads.
- Some shutdown interruption logic is commented or diagnostic-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/fns.h

Central function prototype header for the drawterm kernel runtime.

Major API groups:
- Channel/device operations: `devattach`, `devwalk`, `devopen`, `devstat`, `devdirread`, `cclose`, `fdtochan`, `namec`, `mntversion`, `mntauth`.
- Queue/block operations: `qopen`, `qread`, `qwrite`, `qbread`, `qbwrite`, `allocb`, `freeb`, `pullupblock`, `padblock`, `trimblock`.
- Process/scheduler operations: `newproc`, `ready`, `sched`, `sleep`, `wakeup`, `postnote`, `pexit`.
- Memory/page/segment operations: `newpage`, `putpage`, `segattach`, `fault`, `flushmmu`, `malloc`, `smalloc`.
- Console/input/draw support: `printinit`, `kbdputc`, `readstr`, `readnum`, `drawactive`, `screeninit`.
- Time/random/system helpers: `todget`, `todset`, `fastticks`, `randomread`.
- Command parsing: `parsecmd`, `lookupcmd`, `cmderror`.
- Host integration: `oserrstr`, `oserror`, `osproc`, `osnewproc`, `osinit`.

Notable details:
- Defines `malloc` as `kmalloc`.
- Defines `waserror()`/`poperror()` using the drawterm setjmp-based error stack.
- Defines `islo()` as `0`, reflecting drawterm’s simplified interrupt-level model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/netif.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/netif.h

Defines shared structures and qid helpers for multiplexed network-style devices.

Contents:
- Qid type constants for clone, address, data, ctl, stat, type, and interface-stat files.
- `NETTYPE`, `NETID`, and `NETQID` macros for packing multiplexed qids.
- `Netfile` state for a per-open network endpoint: owner, permissions, mode, queue, multicast/promiscuous flags, scan settings.
- `Netaddr` for tracked network addresses with hash and allocation chains.
- `Netif` for an interface: file table, address metadata, multicast state, statistics, and hardware callback hooks.
- Ethernet constants and `Etherpkt` layout.

Role:
- Used by `devpipe.c` for qid packing and intended for network interface device implementations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/netif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/parse.c

Implements common control-message parsing helpers.

Key behavior:
- `parsecmd` counts whitespace-separated fields, allocates one `Cmdbuf` containing metadata, field pointer array, and a NUL-terminated copy of the input.
- Strips a trailing newline before tokenization.
- Uses `tokenize` to populate `cb->f` and `cb->nf`.
- `cmderror` reconstructs a quoted command for diagnostics and raises an error.
- `lookupcmd` matches a parsed command against a `Cmdtab`, validates argument count, supports wildcard command `"*"`, and reports unknown commands.

Used by:
- `devcons.c` for reboot control.
- `devaudio.c` for volume control.
- `devtls.c` and other control-file parsers.

Notable risks:
- Parsing is whitespace-only; quoting is not preserved as command syntax, only used in reconstructed error text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/parse.c -->