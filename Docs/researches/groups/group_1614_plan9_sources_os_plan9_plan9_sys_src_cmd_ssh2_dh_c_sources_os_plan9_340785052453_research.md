# Group Research: group_1614_plan9_sources_os_plan9_plan9_sys_src_cmd_ssh2_dh_c_sources_os_plan9_340785052453

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dh.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dh.c

This file implements SSH2 Diffie-Hellman key exchange and RSA/DSA public-key algorithm hooks for Plan 9 `netssh`.

Key behavior:
- Defines Oakley group1 and MODP group14 primes, initializes mp arithmetic, and loads RSA/DSA host keys from environment variables, `rsakey`/`dsskey`, or `/mnt/factotum/ctl`.
- Implements RSA key-serialization, PKCS#1/SHA1 signing locally or through factotum, and factotum-backed RSA verification.
- Implements DSA key serialization/signing; DSA verification is a stub returning failure.
- Implements server-side DH reply generation for group1/group14 and client-side group1 initiation/reply handling.
- Derives SSH IVs, encryption keys, and integrity keys from `K`, exchange hash `H`, and session id.

Important details:
- `VERIFYKEYS` is explicitly undefined and `netssh` defaults to skipping host-key verification, reflecting unfinished verification support.
- RSA private signing can use local `!dk=` material or `/mnt/factotum/rpc`.
- `dh_client14*` support is incomplete: it sends group14 init but does not process the reply.
- Key generation fills 40 bytes per direction/key class by chaining SHA1 as RFC 4253 requires.

Filesystem relevance:
- Indirect: cryptographic transport layer for `/net/ssh`, the synthetic SSH filesystem served by `netssh`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.c

This file provides a parallel Plan 9 `dial` implementation for non-threaded/process-style programs.

Key behavior:
- Parses dial strings of the form `[/net/]proto!dest`, including connection directories with numeric channel components.
- Talks to `/net*/cs` to translate a service into one or more clone/destination lines.
- Attempts multiple translated addresses in parallel using `rfork(RFPROC|RFMEM)`, taking the first successful connection.
- Falls back from `/net` to `/net.alt` unless the original failure was a connection refusal.
- Opens protocol clone files, writes `connect dest [local]`, opens the resulting `data` file, and optionally returns the ctl fd and connection directory.

Important details:
- Parent and children share the heap through `RFMEM`; `Conn`/`Dest` are allocated so the parent can observe child state.
- Outstanding child dials are interrupted with `postnote(..., "alarm")`.
- A two-minute alarm bounds parallel connection attempts when no caller alarm exists.
- Error reporting keeps a non-`does not exist` error as the best diagnostic.

Filesystem relevance:
- Direct: manually drives Plan 9 network filesystem control/data files under `/net`, `/net.alt`, and protocol clone directories.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.thread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.thread.c

This file is the thread-library-safe parallel `dial` implementation used where `rfork(RFMEM|RFPROC)` is unsuitable.

Key behavior:
- Keeps the same dial-string parsing, `/net` to `/net.alt` fallback, `/net/cs` lookup, clone/control write, and data-open behavior as `dial.c`.
- Uses Plan 9 thread procs (`proccreate`) and channels instead of shared-memory rfork children.
- Sends result tuples containing data fd, ctl fd, connection directory, or error back to the parent.
- Interrupts losing connection attempts with `threadint`.

Important details:
- `Dest` owns a bounded `kidthrids[64]` array, so excess translated addresses are ignored.
- The first successful data fd wins; later successes are closed.
- The implementation explicitly initializes returned `cfdp` and `dir` to safe empty values before dialing.
- Shared mutable connection result state is minimized compared with `dial.c`.

Filesystem relevance:
- Direct: provides threaded clients a safe way to operate Plan 9 network namespace files such as `/net/cs`, `clone`, `ctl`, and `data`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/esmprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/esmprint.c

This file provides `esmprint`, an allocating formatted-string helper.

Key behavior:
- Wraps `vsmprint`.
- Calls `sysfatal` on allocation failure.
- Sets the malloc tag to the caller pc for debugging/allocation tracking.

Important details:
- Used by SSH utilities to avoid repetitive out-of-memory checks on formatted path/control strings.

Filesystem relevance:
- Indirect: commonly formats Plan 9 namespace paths such as `/net/ssh/...`, `/srv/...`, and `/proc/...`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/esmprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/funclen -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/funclen

This is an rc/awk utility that reports C function lengths.

Key behavior:
- Scans one or more C files, looking for function declarations using Plan 9/V7 brace style.
- Tracks opening and closing braces to print `linecount file:start,end function()`.
- Emits diagnostics for unclosed functions or unmatched function ends.

Important details:
- It deliberately skips preprocessor/comment-like lines, lines ending in semicolons, macro continuations, and some non-function patterns.
- It tolerates a limited set of return type spellings and identifier characters.
- It is a heuristic source-analysis helper, not a parser.

Filesystem relevance:
- Indirect: development utility in the SSH source directory, not runtime filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/funclen -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/magic -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/magic

This is a small rc pipeline for finding likely magic numbers in source.

Key behavior:
- Uses `g`, `grep -v`, and `sed` to print source lines containing numeric literals.
- Filters out headers, includes, common diagnostic prints, and simple `return 0/1/-1` cases.

Important details:
- It is heuristic and tuned for quick source cleanup/review.
- It assumes Plan 9 command availability and syntax.

Filesystem relevance:
- Indirect: source-maintenance helper only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/magic -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.c

This file implements `/net/ssh`, a synthetic 9P filesystem that exposes SSH connections and channels through Plan 9 network-file conventions.

Key behavior:
- Starts a 9P server mounted under `/net` with top-level `ssh/clone`, `ssh/ctl`, and `ssh/keys`.
- Allocates connection directories containing `clone`, `ctl`, `data`, `listen`, `local`, `remote`, `status`, and `tcp`.
- Allocates per-channel directories containing `ctl`, `data`, `listen`, `request`, `status`, and `tcp`.
- Handles client `connect`, server `accept`/`announce`/`reject`, user authentication, channel open/close, channel data, request queues, and key-confirmation mailbox traffic.
- Performs SSH id exchange, KEXINIT negotiation, cipher/MAC activation, packet reading, authentication, and established-state channel dispatch.

Important details:
- `threadmain` initializes crypto/public-key algorithms with `dh_init`, creates a key mailbox channel, daemonizes with `RFNOTEG`, and posts/mounts the service.
- `stopen`, `stread`, `stwrite`, `stflush`, and `stclunk` map 9P operations onto SSH connection/channel state.
- `reader0` is the main SSH transport state machine: `Initting`, `Negotiating`, `Authing`, and `Established`.
- Channel flow control uses receive queues plus `SSH_MSG_CHANNEL_WINDOW_ADJUST`; transmit writers sleep on `xmtrendez` when remote window is exhausted.
- Server-side password auth uses `auth_userpasswd` or `/mnt/keys`; successful auth can create a Plan 9 capability via `#¤/caphash`.
- Public-key auth and client-side signing use factotum-style RSA key records.
- Host-key verification is disabled by default via `nokeyverify`.

Filesystem relevance:
- Central: this is the `/net/ssh` filesystem service and the main bridge between SSH protocol state and Plan 9 file operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.h

This header defines the shared protocol constants, qid layout, state structures, and function interfaces for `netssh`.

Key contents:
- `MYID`, packet/message constants, SSH disconnect/open reason constants, channel extended-data constants, and connection/channel state names.
- Qid path encoding for top-level, connection-level, and subchannel-level files.
- Core structures: `Conn`, `SSHChan`, `Packet`, `Cipher`, `Kex`, `PKA`, `MBox`, and packet queue `Plist`.
- File pointers for each synthetic 9P node exposed by connections and channels.
- Transport, Diffie-Hellman, public-key, and keyring helper prototypes.

Important details:
- `Conn` stores both current and next cipher/MAC state and derived key material.
- `SSHChan` stores queues for data and request packets plus channel windows and synchronization primitives.
- `MAXCONN` is derived from qid bit allocation and doubles as max channel count.
- `Packet` embeds a fixed `Maxpktpay` payload buffer.

Filesystem relevance:
- Central: defines the data model and qid namespace for `/net/ssh`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/pubkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/pubkey.c

This file reads, matches, appends, and replaces RSA public keys in Plan 9 SSH keyring files.

Key behavior:
- Parses public key lines with optional host alias prefix and RSA exponent/modulus in decimal or hexadecimal.
- Reads keys from a `Biobuf`, skipping comments and warning on unparsable lines.
- Matches comma-separated host aliases against a requested host.
- Finds whether a host key is absent, present and matching, or present but different.
- Appends new keys or rewrites a keyring via a `.new` file and `dirwstat` rename.

Important details:
- `Arbsz` is a minimum-size sanity check for RSA modulus/key sizes.
- Replacing a key removes every matching alias entry and appends the new key.
- Key output uses Plan 9 mp formatting with truncated display precision (`%.10M`).

Filesystem relevance:
- Direct: manages user/system keyring files such as `/sys/lib/ssh/keyring` and `$home/lib/keyring`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/pubkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/rsa2ssh2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/rsa2ssh2.c

This utility converts a Plan 9 RSA key record into an SSH2 public key line.

Key behavior:
- Reads a key record from stdin or one file.
- Extracts `ek=` and `n=` fields.
- Encodes an SSH public-key blob containing `ssh-rsa`, exponent, and modulus.
- Base64-encodes the blob and prints `ssh-rsa <blob> [user]`.

Important details:
- Uses `new_packet`, `add_string`, and `add_mp` from the SSH transport helpers to build the canonical SSH blob.
- Appends `$user` as a comment when available.
- Expects hex Plan 9 factotum-style key fields.

Filesystem relevance:
- Indirect: supports moving Plan 9 key material into SSH-compatible authorized/public key formats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/rsa2ssh2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.c

This file implements the user-facing SSH client command, using `/net/ssh` for protocol work and copying bytes between terminal and channel data files.

Key behavior:
- Parses compatibility flags, user/remote syntax, netdir overrides, key selection, password/public-key disabling, raw/cooked behavior, and CR stripping.
- Ensures an SSH tunnel service is mounted by trying `/srv/netssh`, `/srv/ssh`, `/srv/ssh.$user`, or starting `/bin/netssh`.
- Forks a helper that speaks the `/net/ssh/keys` confirmation protocol through `/dev/cons`.
- Dials a connection under `/net/ssh`, authenticates via ctl messages, dials a session channel, writes a shell or exec request, and performs bidirectional data copying.
- Handles interactive escape command mode triggered by control-backslash at line start.

Important details:
- Authentication first tries public key (`ssh-userauth K`) unless disabled, then password (`ssh-userauth k`) via `auth_getuserpasswd`.
- Terminal raw mode is controlled through `/dev/consctl`.
- Shutdown writes `close` to the request file and sends `kill` to a note group fd.
- Remote command requests quote each argument into a single `exec` request.

Filesystem relevance:
- Direct: client of the `/net/ssh` filesystem plus `/srv`, `/dev/cons`, `/dev/consctl`, `/proc`, and environment files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.h

This small header defines common limits and utility prototypes for the SSH command suite.

Key contents:
- Buffer and path limits including `Maxpayload`, `Maxrpcbuf`, `Copybufsz`, `Blobsz`, `Maxfactotum`, and stack sizes.
- Opaque `Conn` forward declaration for logging signatures.
- Vararg checking pragmas for `esmprint`, `ssdebug`, and `sshlog`.
- Utility prototypes for formatted allocation, logging, pointer freeing, and file reading.

Important details:
- `Maxrpcbuf` is tied to devmnt’s maximum RPC payload.
- `Maxfactotum` bounds reads of `/mnt/factotum/ctl`.

Filesystem relevance:
- Indirect: shared constants shape reads/writes to SSH, factotum, and namespace files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/sshsession.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/sshsession.c

This file implements the server-side session helper that accepts SSH channels from `/net/ssh` and runs shells or commands.

Key behavior:
- Opens a connection clone/data path, consumes an auth capability, optionally enters a new namespace, announces `session`, then listens for session channels.
- For each channel, opens its `request` and `data` files and handles SSH channel requests.
- Starts an interactive shell through `/bin/ip/telnetd -nt` or an exec command through `/bin/rc -lc`.
- Handles supported requests: `shell`, `exec`, `pty-req`, and `window-change`; rejects x11/env/subsystem.
- Closes request/data and interrupts the top process group when the child exits.

Important details:
- Capabilities are written to `#¤/capuse`.
- `-r`/`-R` can set a restricted directory and optionally confine command paths to basenames unless `$sshsession=allow`.
- It can mount the ssh service from `/srv/<srvpt>` if the expected netdir is not visible.
- `newchannel` prevents more than one shell/exec action per channel.

Filesystem relevance:
- Direct: server-side consumer of `/net/ssh/<conn>/<chan>/{listen,request,data}`, `/srv`, namespace setup, and Plan 9 cap devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/sshsession.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/transport.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/transport.c

This file implements SSH binary packet construction, parsing helpers, padding, encryption, MAC generation, and packet dumping.

Key behavior:
- Allocates and initializes fixed-buffer `Packet` objects.
- Appends SSH primitive encodings: byte, uint32, string/block, mpint, and raw packet data.
- Extracts SSH strings, uint32s, and mpints.
- `finish_packet` computes SSH padding, packet length, optional HMAC-SHA1, optional encryption, and sequence advancement.
- `undo_packet` decrypts packet bodies, validates HMAC-SHA1, removes padding, and advances input sequence.

Important details:
- Minimum block size is forced to 8 bytes as SSH requires.
- mpint serialization inserts a leading zero when the high bit would make the integer negative.
- MAC input includes sequence number and packet bytes.
- `dump_packet` is a debug hex dump helper.

Filesystem relevance:
- Indirect: transport layer used by the `/net/ssh` filesystem service and client/server helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/stats.c

This file implements the graphical `stats` monitor for local or remote Plan 9 machines.

Key behavior:
- Samples memory, swap, sysstat counters, Ethernet stats, wireless signal, battery, and CPU temperature.
- Displays one or more scrolling graphs per machine using libdraw/event.
- Can mount remote machines through exportfs/9P to read their `/dev` and `/net` status files.
- Supports graph add/drop through the mouse menu and command-line graph selection flags.
- Handles window resizing, labels, log scaling, y-axis labels, and multiple machine columns.

Important details:
- Local/remote data comes from files including `/dev/swap`, `/dev/sysstat`, `/net/ether0/stats`, `/net/ether0/ifstats`, `/mnt/apm/battery`, `/dev/battery`, and `/dev/cputemp`.
- Remote exportfs setup uses `auth_proxy`, `mount`, and optional old-9P conversion through `srvold9p`.
- Remote reads are alarm-bounded and temporarily disabled after repeated failures.
- Counter graphs compute deltas from previous samples; utilization graphs use current values.
- Mouse handling runs in a shared-memory rfork process.

Filesystem relevance:
- Direct: demonstrates Plan 9’s file-oriented instrumentation model and remote filesystem mounting for monitoring.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/strings.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/strings.c

This file implements the Plan 9 `strings` utility.

Key behavior:
- Reads stdin or named files with `Biobuf`.
- Extracts runs of printable runes, default minimum length 6, configurable with `-m`.
- Prints byte offset and string content.
- Truncates very long runs to `BUFSIZE-1` runes and marks them with `...`.

Important details:
- Printable runes are ASCII space through `~` plus values above `0xA0`, excluding `Runeerror`.
- Uses `Bgetrune`, so offsets are tracked with `Boffset` over rune-decoded input.

Filesystem relevance:
- Indirect: file-inspection utility for arbitrary files/binaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/strip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/strip.c

This file implements the Plan 9 `strip` utility for executable binaries.

Key behavior:
- Opens a binary, uses libmach `crackhdr` to parse executable headers, and validates magic.
- Computes stripped length as data offset plus data size.
- Reads only text/data content, zeroes symbol and pc/sp table sizes in the exec header, and writes back in place or to `-o ofile`.
- Preserves original file mode.

Important details:
- In-place stripping removes the original before recreating it.
- Already stripped files are reported as such unless an output file was requested.
- Rejects unrecognized binaries and strange computed lengths.

Filesystem relevance:
- Direct file mutation utility for executable files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/strip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sum.c

This file implements checksum calculation in three historical formats.

Key behavior:
- Default mode computes a 32-bit CRC with length folded into the final CRC.
- `-r` computes the Research Unix rotating 16-bit checksum with 1024-byte block count.
- `-5` computes the System V-style additive checksum with 512-byte block count.
- Reads stdin or named files and prints checksum, block/size count, and optional filename.

Important details:
- The checksum function is called with `buf == nil` as a finalization/printing step.
- The CRC table is embedded.
- Read/open errors are reported per file and returned via exit status string.

Filesystem relevance:
- Indirect: file integrity utility over arbitrary file contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/swap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/swap.c

This file configures a swap file/device.

Key behavior:
- Takes one path argument.
- If the path is not a kernel device directory, opens it directly for swap.
- If it is a kernel device directory, creates a temporary ORCLOSE file named from `$sysname`.
- Writes the selected path to `/env/swap`.
- Writes the swap file descriptor number to `/dev/swap`.

Important details:
- The command refuses the root path and reports failures through `perror`.
- Temporary swap files are mode `0600`.
- Uses Plan 9’s convention of enabling swap by passing an fd number to `/dev/swap`.

Filesystem relevance:
- Direct: configures virtual memory backing through `/env/swap`, `/dev/swap`, and a file/device path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/syscall/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/syscall/syscall.c

This file implements a command-line syscall exerciser.

Key behavior:
- Dispatches named syscalls from a generated `tab.h` table.
- Parses up to five arguments as integers, strings, or the special 1 MB `buf`.
- Special-cases `seek`, `pread`, and `pwrite` for vlong offsets.
- Prints return value and error state.
- Optional flags print buffer text (`-o`), hex/ascii dump (`-x`), or decode stat messages (`-s`).

Important details:
- Includes prototypes for syscalls not declared in libc.
- `-s` decodes Plan 9 stat buffers via `convM2D` and prints qid/mode/owner/time details.
- Notes are caught and reported before default handling.

Filesystem relevance:
- Direct diagnostic utility for filesystem syscalls such as `stat`, `wstat`, `read`, `write`, `mount`, `pread`, and `pwrite`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/syscall/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tail.c

This file implements `tail`, including POSIX options and V10 reverse mode.

Key behavior:
- Supports `-n`, `-c`, `-f`, `-r`, and legacy `+-N[bc][fr]` syntax.
- Handles seekable and non-seekable inputs differently.
- For seekable files, seeks from beginning/end or scans backward for line tails.
- For pipes, either skips from the beginning or keeps a rolling tail buffer.
- `-f` repeatedly copies appended data and detects truncation.

Important details:
- Reverse mode is incompatible with character units, follow mode, and begin-origin mode.
- Follow mode uses `dirfstat` to detect shrinking files and seek back to start.
- Output is buffered but flushed during forward copy to support pipes.

Filesystem relevance:
- Direct file-reading utility with explicit behavior for pipes, seekable files, and truncating files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/32vfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/32vfs.c

This file implements a read-only tapefs backend for VAX 32V/pre-FFS Berkeley filesystem images.

Key behavior:
- Opens a disk image, reads the root inode, and makes it the tapefs root.
- Lazily populates directories by reading fixed 14-character directory entries.
- Reads inodes from the inode area after the superblock.
- Maps logical file blocks through direct and singly indirect block addresses.
- Reads file data blocks into a static buffer.

Important details:
- Default block size is 512 bytes; `-b 1024` supports 4.1BSD-style images.
- Device special files report zero size.
- Only singly-indirect files are supported.
- Filesystem writes/truncates/creates are disabled.

Filesystem relevance:
- Direct: interprets a historical Unix filesystem image and exports it through tapefs’s 9P server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/32vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/cpiofs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/cpiofs.c

This file implements a read-only tapefs backend for old octal cpio archives.

Key behavior:
- Sequentially scans cpio headers from the archive.
- Parses octal fields for mode, uid, gid, size, mtime, and name length.
- Stops at empty names or `TRAILER!!!`.
- Adds regular files and directories into the shared `Ram` tree.
- Reads file contents from recorded archive offsets.

Important details:
- Absolute pathnames are made relative by skipping the leading slash.
- Unknown/non-regular/non-directory modes are assigned mode 0.
- Header/data offsets are advanced without explicit padding handling beyond the old format fields.

Filesystem relevance:
- Direct: maps a cpio archive into a read-only 9P namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/cpiofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/fs.c

This file is the common tapefs 9P server that serves an archive/image as a mounted read-only filesystem.

Key behavior:
- Builds a root `Ram` tree, calls the selected backend `populate`, forks an I/O server, and mounts it at `/n/tapefs` or `-m mountpoint`.
- Implements core 9P requests: version, attach, walk, open, read, write, clunk, stat, flush, and errors for create/remove/wstat/auth.
- Serves directories by converting `Ram` entries to Plan 9 stat records.
- Serves files by delegating content reads to backend `doread`.
- Lazily populates unreplete directories through backend `popdir`.

Important details:
- The filesystem is effectively read-only: `perm(Pwrite)` returns false and create/remove/wstat return permission errors.
- Fids track open state, user, and current `Ram` node.
- Message size is negotiated by `Tversion` and capped by `Maxbuf+IOHDRSZ`.
- `io()` runs the 9P request loop over a pipe used as the mount fd.

Filesystem relevance:
- Central: generic 9P façade for tape/archive/filesystem-image backends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapefs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapefs.h

This header defines shared tapefs structures, constants, byte-order helpers, globals, and backend hooks.

Key contents:
- Little-endian and big-endian byte extraction macros.
- `Fid`, `Ram`, `Idmap`, and `Fileinf` structures.
- Permission bit aliases used by tapefs permission checks.
- Global state declarations for root ram tree, user/group maps, repletion, block size, and qid path counter.
- Backend/function prototypes for population, directory expansion, reads, writes, truncation, creation, path insertion, and id mapping.

Important details:
- `Ram` nodes store qid, mode, ownership, times, archive address/data, size, tree links, and lazy population state.
- Backends provide archive-specific `populate`, `popdir`, `doread`, and no-op write/truncate/create behavior.

Filesystem relevance:
- Central: shared ABI between the tapefs 9P server and all archive/filesystem backends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapfs.c

This file implements a tapefs backend for old `tap` tape images.

Key behavior:
- Reads a fixed directory table of old tap entries.
- Verifies each entry checksum.
- Extracts file address, size, mode, uid, timestamp, and name.
- Converts absolute names to relative names and inserts entries into the shared tree.
- Reads file data from 512-byte block addresses.

Important details:
- Supports old and “newtap” timestamp interpretation.
- Skips entries with empty names, zero addresses, or checksum failures.
- Does not support directories beyond path-derived parent creation unless entries imply them through names.

Filesystem relevance:
- Direct: exposes historical tap tape archive contents through 9P.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tarfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tarfs.c

This file implements a read-only tapefs backend for tar archives.

Key behavior:
- Scans 512-byte tar headers and stops on an empty name.
- Supports POSIX ustar prefix/name composition and old-style names.
- Parses mode, uid, gid, size, mtime, checksum, and link flag.
- Detects directories by link flag, mode, or trailing slash.
- Sanitizes names by stripping leading slashes, cleaning paths, and dropping leading `../`.
- Reads file payload blocks from archive offsets.

Important details:
- Symlinks and hard links are skipped as content-bearing entries.
- GNU positive binary size encoding is partially supported.
- Header checksums are validated after temporarily replacing the checksum field with spaces.
- Short reads are padded with zeros.

Filesystem relevance:
- Direct: maps tar archives into a safe read-only 9P namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tarfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tpfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tpfs.c

This file implements a tapefs backend for old `tp` tape images.

Key behavior:
- Reads a directory table sized for magtape while tolerating dectape by checksum filtering.
- Validates per-entry checksum.
- Extracts file block address, 24-bit size, timestamp, mode, uid, gid, and name.
- Inserts entries into the tapefs tree and reads data from 512-byte block addresses.

Important details:
- Reports counts of bad and good checksums.
- Absolute paths are made relative.
- Write/create/truncate operations are disabled.

Filesystem relevance:
- Direct: exposes historical `tp` tape contents as a read-only mounted filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/tpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/util.c

This file provides shared tapefs helpers for id maps and tree construction.

Key behavior:
- Reads passwd/group-style files into `Idmap` arrays.
- Maps numeric ids to names, falling back to decimal strings.
- Builds directory paths recursively from `Fileinf` records.
- Creates or updates `Ram` nodes and links them into parent directories.
- Looks up child entries by name.

Important details:
- Parent directories missing from an archive are synthesized with mode `0555|DMDIR`.
- Existing entries can be updated if a “new” record replaces metadata.
- File modes are forced to include at least user-read.
- Duplicate names with changed file/directory type are ignored with a warning.

Filesystem relevance:
- Direct: common metadata/tree layer for all tapefs backends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/v10fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/v10fs.c

This file implements a read-only tapefs backend for 10th Edition Unix 4 KB filesystem images.

Key behavior:
- Opens an image, records its length, reads the root inode, and initializes the tapefs root.
- Lazily reads directory entries and populates child nodes.
- Reads inode metadata and block address arrays.
- Maps direct and singly indirect block numbers to physical blocks.
- Prevents reads past the image length by returning zero-filled blocks.

Important details:
- Uses 4096-byte blocks and 14-character directory names.
- Character/block device files are exposed with zero size.
- Only singly-indirect files are supported.
- `doread` returns `buf+off`, correctly accounting for intra-block offsets.

Filesystem relevance:
- Direct: mounts a historical local filesystem image through the tapefs 9P interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/v10fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/v6fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/v6fs.c

This file implements a read-only tapefs backend for old V6-and-earlier PDP-11 Unix filesystem images.

Key behavior:
- Opens an image and reads root inode 1.
- Lazily populates directories from 14-character V6 directory entries.
- Parses V6 inode flags, size, owner/group, timestamps, and eight block addresses.
- Maps small files through direct addresses and larger files through single-indirect blocks.
- Reads file data from 512-byte blocks.

Important details:
- V6 directory mode is recognized through the V6-specific format bits.
- Large-file handling assumes file size predicts indirect addressing.
- Device special files are treated as zero-length.
- Write/create/truncate operations are disabled.

Filesystem relevance:
- Direct: exposes old Unix filesystem images as a Plan 9 mounted namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/v6fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/zip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/zip.h

This header defines ZIP constants and the parsed `ZipHead` structure used by `zipfs.c`.

Key contents:
- Magic numbers for local headers, central directory headers, and end-of-central-directory.
- General-purpose flag bits, compression method constants, CRC polynomial, and header size constants.
- Creator OS and external attribute constants.
- `ZipHead` fields for creator/extractor versions, flags, method, timestamps, CRC, compressed/uncompressed sizes, attributes, local-header offset, and filename.

Important details:
- The constants cover deflate, data descriptors, encryption flags, and OS-specific attributes, though `zipfs.c` supports only stored and deflated file data.

Filesystem relevance:
- Direct support header for the ZIP tapefs backend.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/zip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/zipfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/zipfs.c

This file implements a read-only tapefs backend for ZIP archives.

Key behavior:
- Initializes flate support and opens the ZIP with `Biobuf`.
- Finds the central directory from the end-of-central-directory record.
- Reads central directory headers, converts metadata into `Fileinf`, and populates the tapefs tree.
- Supports stored files and deflated files.
- Reads local headers on demand and inflates compressed data into a per-file cache.

Important details:
- Filenames are forced to lower case.
- Text files can be marked by setting a high bit in the stored address; CRLF pairs may be munged by replacing `\r` with space.
- Deflated file cache is keyed by qid path and CRC-checked after inflate.
- Directory entries are inferred from zero-size stored names ending in `/`.
- Unsupported compression methods call `sysfatal`.

Filesystem relevance:
- Direct: exposes ZIP archives as read-only Plan 9 filesystem trees through tapefs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tapefs/zipfs.c -->