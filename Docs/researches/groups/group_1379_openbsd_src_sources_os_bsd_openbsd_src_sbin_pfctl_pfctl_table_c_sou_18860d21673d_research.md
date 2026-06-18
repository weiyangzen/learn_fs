# Group Research: group_1379_openbsd_src_sources_os_bsd_openbsd_src_sbin_pfctl_pfctl_table_c_sou_18860d21673d

Scope: `Docs/research_subset_a.md`, specifically the listed OpenBSD `sbin` files under `pfctl`, `pflogd`, `ping`, `quotacheck`, `reboot`, `resolvd`, and `restore`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_table.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_table.c

## Purpose

Implements `pfctl` table and interface subcommands for OpenBSD PF. This file is the userland control surface around `pfr_*` and `pfi_*` kernel ioctls: listing, creating, deleting, flushing, replacing, expiring, testing, and zeroing PF tables and table address counters.

## Main Entry Points

- `pfctl_clear_tables()` and `pfctl_show_tables()` are small wrappers around `pfctl_table()` for `-F` and `-s`.
- `pfctl_table()` dispatches string commands such as `-F`, `-s`, `kill`, `flush`, `add`, `delete`, `replace`, `expire`, `show`, `test`, and `zero`.
- `pfctl_define_table()` defines parser-created tables, either directly through `pfr_ina_define()` for root/command tables or by filling a `pfr_uktable` for later non-root anchor loading.
- `pfctl_show_ifaces()` and `print_iface()` list PF interface accounting.

## Control Flow And Behavior

`pfctl_table()` initializes a `pfr_table`, copies the optional table name and anchor with bounds checks, sets `PFR_FLAG_DUMMY` for no-action mode, then uses command-specific pfr operations. Dynamic result retrieval uses grow-and-retry loops: allocate/grow a `pfr_buffer`, set `pfrb_size` to current capacity, call `pfr_get_tables()`, `pfr_get_tstats()`, `pfr_get_addrs()`, `pfr_get_astats()`, or `pfi_get_ifaces()`, and repeat until returned size fits.

Address-changing commands load argv and optional file input with `load_addr()`, which calls `append_addr()` for each argument and `pfr_buf_load()` for files. `add` and `replace` use `CREATE_TABLE`, which warns about duplicate active table names in other anchors, temporarily sets `PFR_TFLAG_PERSIST`, and calls `pfr_add_tables()` unless in syntax-only mode. Verbose operations set `PFR_FLAG_FEEDBACK` and print only changed feedback entries unless very verbose output is requested.

`expire` reads address stats, compares `time(NULL) - pfras_tzero` against a parsed lifetime, builds a second buffer of stale addresses, and deletes them. `test` optionally clones the input address buffer under `PF_OPT_VERBOSE2` so the original query address and returned match address can be printed side by side. `zero` either clears selected address counters or clears table and address stats together with `PFR_FLAG_ADDRSTOO`.

## Output And Formatting

`print_table()` emits compact flag columns for const, persist, active, inactive, referenced, referenced-anchor, and counters. `print_tstats()` and `print_astats()` format clear times, references, evaluations, packets, bytes, active states, weights, and interface names. `print_addrx()` prints PF address feedback markers, negation, CIDR prefix, optional matched address, optional reverse DNS for host addresses, and optional interface suffix.

## Dependencies And State

The file depends on PF userland/kernel APIs from `net/pfvar.h`, shared parser/helper declarations in `pfctl_parser.h` and `pfctl.h`, and buffer helpers such as `pfr_buf_grow()`, `pfr_buf_add()`, `pfr_buf_clear()`, `PFRB_FOREACH`, `append_addr()`, and `pfr_buf_load()`.

## Risks And Invariants

- Table and anchor names must fit `PF_TABLE_NAME_SIZE` and destination buffers; overlong names trigger usage or fatal errors.
- `RVTEST` intentionally suppresses real kernel calls in syntax-only mode unless dummy action is requested; command behavior depends on this macro.
- Buffer grow loops rely on kernel APIs returning the needed element count through `pfrb_size`.
- `print_addrx()` computes `hostnet` from the printed address family; when printing a matched address (`rad`) it assumes compatible family/prefix semantics.
- `pfctl_define_table()` transfers ownership of address buffers into `pfr_uktable` by clearing the source buffer fields after assignment.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_table.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/Makefile

## Purpose

Builds the `pflogd` daemon.

## Build Definition

The program is `pflogd`, with sources `pflogd.c`, `privsep.c`, and `privsep_fdpass.c`, and manual page `pflogd.8`. It adds strict warning flags, includes `../../lib/libpcap` for `pcap-int.h`, and links against `libpcap`.

## Notable Detail

`LDSTATIC=` is explicitly cleared so `pflogd` is not built as a static binary by default.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.c

## Purpose

Main implementation of `pflogd`, the PF log daemon. It captures packets from a `pflog(4)` interface through BPF/libpcap and appends them to a pcap-format log file, using privilege separation for BPF and log-file access.

## Main State

Global capture state includes `hpcap`, output `FILE *dpcap`, configured and current snaplen, signal flags, log filename, interface name, optional pcap filter, flush delay, output buffer state, suspend state, and dropped-packet count. Default configuration is `pflog0`, `/var/log/pflog`, snaplen `DEF_SNAPLEN`, read timeout `PCAP_TO_MS`, and flush delay `FLUSH_DELAY`.

## Capture Setup

`pflog_read_live()` creates a pcap handle but manually opens `/dev/bpf` read-only, verifies BPF version, attaches the requested interface with `BIOCSETIF`, sets datalink type `DLT_PFLOG`, installs timeout and optional promiscuous mode, queries BPF buffer length with `BIOCGBLEN`, allocates the pcap buffer, and marks the handle activated. `init_pcap()` checks the datalink type, installs the compiled filter via `set_pcap_filter()`, and locks the BPF descriptor with `BIOCLOCK`.

## Log File Handling

`reset_dump()` closes any previous pcap output after flushing the local buffer, asks the privileged process to open the log, wraps the fd with `fdopen("a+")`, disables stdio buffering, and either writes a new pcap file header or validates an existing file with `scan_dump()`. Existing logs are scanned end-to-end for header compatibility, packet header integrity, captured length bounds, and exact file-size match before append. If an existing log has a different snaplen, the daemon attempts to switch to that snaplen.

## Packet Writing

`dump_packet()` appends packet headers and payloads into a private `PFLOGD_BUFSIZE` buffer, flushing when needed. Oversized packets or packets larger than current snaplen are dropped. If a packet cannot fit even after flushing, `dump_packet_nobuf()` writes it directly. `flush_buffer()` records the current file offset, writes the buffer, truncates back to the saved offset on failure, suspends logging on errors, and resets buffer cursors on success. `purge_buffer()` drops buffered packets and accounts them as dropped.

## Main Loop

`main()` parses `-D`, `-d`, `-f`, `-i`, internal `-P`, `-s`, and `-x`; validates the interface; optionally daemonizes; builds the optional filter expression; starts privilege separation with `priv_init()`; pledges to `stdio recvfd`; installs signal handlers; initializes pcap through the privileged parent; allocates the output buffer; opens/validates the log; then loops on `pcap_dispatch()`.

Signals are converted into flags after `pcap_breakloop()`: close exits, HUP reopens the log and resumes if possible, and ALRM flushes periodically or triggers reopen if no output file exists. `-x` exits after validating/opening the log path.

## Risks And Invariants

- `scan_dump()` may take a long time on large log files because it validates every packet before append.
- Logging suspension is deliberate: write/open failures stop further log writes but the daemon keeps consuming packets and counting drops.
- Snaplen changes purge buffered packets when shrinking to avoid writing packets incompatible with the new capture length.
- The code reaches into `pcap_t` internals (`pcap-int.h`), so it is coupled to OpenBSD's libpcap layout.
- Direct BPF setup and log opening are intentionally routed through privilege separation; bypassing that would break the daemon's security model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.h

## Purpose

Shared constants and prototypes for `pflogd`.

## Contents

Defines capture and buffering defaults: `DEF_SNAPLEN`, `PCAP_TO_MS`, `PCAP_NUM_PKTS`, `PCAP_OPT_FIL`, `FLUSH_DELAY`, default log file, default interface, maximum snaplen, and output buffer size.

Declares logging, privilege-separation, pcap initialization/filtering, and fd-passing APIs used across `pflogd.c`, `privsep.c`, and `privsep_fdpass.c`. Also declares global `Debug`.

## Coupling

This header includes `pcap.h` and system limits because the public constants and prototypes use pcap-related types and integer bounds.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/privsep.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/privsep.c

## Purpose

Privilege separation for `pflogd`. The privileged parent keeps access to `/dev/bpf` and the log file, while the re-executed child drops privileges, chroots, receives file descriptors, and performs packet processing.

## Process Model

`priv_init()` looks up `_pflogd`. In internal child mode (`-P`), it chroots to the user home, changes to `/`, sets gid/groups/uid to `_pflogd`, assigns fd 3 as the privsep channel, and returns to unprivileged `main()`.

In parent mode, it creates a local socketpair, forks, dup2s the child side to fd 3, re-execs the same program with `-P`, and enters a command loop. The privileged parent forwards ALRM, TERM, HUP, INT, and QUIT signals to the child and sets its process title to `[priv]`.

## Privileged Operations

The command protocol supports:

- `PRIV_INIT_PCAP`: call `init_pcap()`, write BPF buffer size, and pass the BPF fd to the child.
- `PRIV_SET_SNAPLEN`: update the privileged pcap snapshot length and reinstall the filter.
- `PRIV_OPEN_LOG`: open the log file with `O_RDWR|O_CREAT|O_APPEND|O_NONBLOCK|O_NOFOLLOW`, then pass the fd or encoded errno.

Before the loop, the parent unveils resolver config files, `/dev/bpf`, and the selected log file, then locks unveil. A pledge block is present but disabled because BPF ioctls were not pledge-compatible in this code path.

## Child-Side APIs

`priv_init_pcap()` requests BPF initialization, receives the fd, creates a local pcap handle, fills enough internal fields to use the received fd, allocates the pcap buffer, and marks it activated. `priv_set_snaplen()` sends a new snaplen and mirrors it into the child pcap handle on success. `priv_open_log()` requests and receives a log fd.

## IPC Helpers

`may_read()`, `must_read()`, and `must_write()` implement fixed-size blocking transfer loops that retry `EINTR` and `EAGAIN`. The `must_*` functions exit the process on EOF/write failure.

## Risks And Invariants

- The unprivileged child must call these APIs only after `priv_fd` is assigned; the code aborts if called from the privileged side.
- The child reconstructs a pcap handle by assigning libpcap internals directly, which depends on libpcap ABI details.
- The privileged parent exits on unknown commands or pcap initialization failure.
- `unveil(filename, "rwc")` means the selected log path is fixed at startup; later log rotation is handled by reopening that same path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/privsep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/privsep_fdpass.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/privsep_fdpass.c

## Purpose

Small fd-passing utility for `pflogd` privilege separation.

## Behavior

`send_fd()` sends an integer result over a Unix domain socket. If the fd is valid, it attaches the fd using `SCM_RIGHTS`; if invalid, it sends the current `errno` as the result code without ancillary fd data.

`receive_fd()` reads the integer result and optional control message. A zero result requires an `SCM_RIGHTS` control message and returns the received fd. A nonzero result is copied into `errno` and returns `-1`.

## Risks And Invariants

- Both sides expect exactly `sizeof(int)` bytes of normal payload.
- The receiver warns if no control header appears or if the control type is not `SCM_RIGHTS`.
- The code does not validate `cmsg_level`; it checks only `cmsg_type`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pflogd/privsep_fdpass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ping/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ping/Makefile

## Purpose

Builds OpenBSD `ping` and links it as `ping6`.

## Build Definition

The program is `ping`, with manual page `ping.8`. It enables strict warning flags, links with `libm`, installs a hard link from `ping` to `ping6`, and installs owned by root with mode `4555`.

## Notable Detail

The same binary switches IPv4/IPv6 behavior based on the invoked program name (`ping` versus `ping6`).
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ping/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ping/ping.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ping/ping.c

## Purpose

Combined IPv4/IPv6 `ping` implementation. It sends ICMP Echo requests on raw sockets, receives replies and diagnostic ICMP messages, prints per-packet output, tracks duplicates and RTT statistics, and supports legacy IPv4 options plus IPv6 control-message diagnostics.

## Program Setup

The binary chooses IPv6 mode when invoked as `ping6`; otherwise it uses IPv4. It opens the raw ICMP socket before dropping privileges. If initially run as root and `_ping` exists, it later drops to that user and group; otherwise it drops to the real uid/gid. Options configure count, don't-fragment/header inclusion, socket debug, audible notifications, flood mode, show-character mode, hostname resolution, hoplimit/TTL, source address, interval, preload, multicast loop/TTL/min-MTU behavior, payload pattern and size, quiet/verbose mode, record-route, TOS/traffic class, routing table, and max wait.

The program unveils `/` read-only early because name and service resolution may need filesystem access, then pledges to `stdio inet` or `stdio inet dns` after socket setup depending on whether hostname lookup output is enabled.

## Packet Sending

`pinger()` constructs an ICMP or ICMPv6 Echo Request with a random 16-bit identifier and incrementing sequence number. When the payload is large enough, it writes a timing payload containing a monotonic timestamp with a random offset and a SipHash MAC over timestamp, identifier, and sequence. IPv4 computes the ICMP checksum, and when `IP_HDRINCL` is used it also fills the IP header and checksum. Packets are sent with `sendmsg()` using a shared `msghdr`; IPv6 hoplimit can be supplied as a control message.

## Receive Loop

Startup drains pending packets from the raw socket under a one-second timer. Normal operation uses signals as flags: SIGALRM triggers retransmit, SIGINT exits, and SIGINFO prints an interim summary. Non-flood mode uses an interval timer; flood mode sends aggressively until count is exhausted and then waits for late replies. The loop uses `poll()` and `recvmsg()` with room for ancillary data. Zero-length IPv6 reads are treated as control-message notifications, currently path MTU updates.

## Packet Parsing And Statistics

`pr_pack()` validates peer address family and minimum lengths, parses IPv4 IP headers or raw ICMPv6 headers, filters echo replies by identifier, obtains IPv6 hoplimit from control messages, and handles non-echo ICMP output only in verbose mode. Valid echo replies increment `nreceived`; duplicate detection uses a bitset indexed by sequence modulo `MAX_DUP_CHK`.

RTT calculation is accepted only if the SipHash MAC in the returned payload matches. This prevents unrelated, stale, or forged payload bytes from feeding timing statistics. Timing values update min, max, sum, and sum-of-squares for standard deviation. Printed output includes bytes, source address, sequence, TTL/hoplimit, RTT, duplicate/truncation flags, and optional payload mismatch dumps.

## Diagnostic Printers

IPv4 helpers include `pr_ipopt()`, `in_cksum()`, `pr_icmph()`, `pr_iph()`, and `pr_retip()`. They print record-route/LSRR options, ICMP unreachable/redirect/time-exceeded/parameter/timestamp/router/mask messages, returned IP headers, and TCP/UDP ports in embedded packets.

IPv6 helpers include `pr_exthdrs()`, `pr_ip6opt()`, `pr_rthdr()`, `get_hoplim()`, `get_pathmtu()`, `pr_icmph6()`, `pr_iph6()`, and `pr_retip6()`. They print extension headers, hop-by-hop/destination options, routing headers, path MTU notifications, ICMPv6 error/ND messages, and embedded IPv6 packet chains.

## Risks And Invariants

- Raw sockets are opened before privilege drop; later privileged socket options must be set before pledge.
- Non-root users cannot use flood mode, preload, or subsecond intervals.
- Duplicate tracking is modulo a fixed bitset; very long runs can alias old sequence numbers.
- The timing payload requires `datalen >= sizeof(struct payload)`.
- Several diagnostic routines intentionally parse packet bytes from the network; they do length checks in key paths, but older printer code assumes embedded protocol headers are present once reached.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ping/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/quotacheck/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/quotacheck/Makefile

## Purpose

Builds `quotacheck`.

## Build Definition

The program is `quotacheck`, with sources `quotacheck.c`, `preen.c`, and `fsutil.c`. It includes `../fsck`, uses `.PATH` to reuse fsck helper sources, installs `quotacheck.8`, and links against `libutil`.

## Coupling

This utility shares preen/check infrastructure with `fsck` through `preen.c` and `fsutil.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/quotacheck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/quotacheck/quotacheck.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/quotacheck/quotacheck.c

## Purpose

Checks and repairs UFS/FFS quota usage files by scanning raw filesystem inodes and reconciling observed block/inode usage with user and group quota files and active kernel quota state.

## Main Flow

`main()` requires root via `checkroot()`, parses preen/debug/group/user/verbose/maxparallel flags, preloads known group and user ids into hash tables, then either delegates to `checkfstab()` in preen mode or walks `/etc/fstab` manually. It selects read-write `ffs`, `ufs`, and `mfs` filesystems with quota options through `needchk()`, matches explicit arguments by mount realpath or device identity, normalizes devices with `blockcheck()`, and calls `chkquota()`.

## Filesystem Scan

`chkquota()` forks so each filesystem check can run independently or under preen scheduling. The child opens the raw device read-only, syncs, searches known superblock locations, validates UFS1/UFS2 magic and size, computes `maxino`, then scans every cylinder group. It reads cylinder group blocks, determines initialized inode count, streams inode blocks through `getnextinode()`, skips invalid/free/root-below inodes, and accumulates inode and block counts per gid/uid for regular files, directories, and symlinks.

The inode access layer uses an optimized sequential buffer sized around `INOBUFSIZE`, rounded to filesystem block size. `setinodebuf()` prepares per-cylinder-group counters, `getnextinode()` reads the next chunk with `bread()`, and `freeinodebuf()` releases the buffer.

## Quota File Reconciliation

`update()` opens or creates the quota file, sets owner/group/mode on creation, opens a read stream too, tries `quotactl(Q_SYNC)`, then iterates from id zero through the highest known id. For each `dqblk`, it compares stored current inodes/blocks to scanned usage. Differences are printed in debug/verbose mode, grace timers are reset when crossing soft limits from below to above, current usage fields are updated, and non-debug mode writes the quota file and calls `quotactl(Q_SETUSE)`. Finally it truncates the quota file to the highest id plus one record.

## Helpers And Data Structures

Usage data is stored in `struct fileusage` hash tables split by quota type. `hasquota()` parses fstab mount options for `userquota`/`groupquota` names and optional paths. `oneof_realpath()` and `oneof_specname()` match CLI filesystem arguments to fstab entries. `addid()` creates missing usage records and tracks `highid[type]`; unnamed ids are formatted numerically.

## Risks And Invariants

- Only UFS1/UFS2-like filesystems with valid superblocks are processed.
- `done` uses a 64-bit bitset and the source comment notes it supports at most 64 explicit filesystem arguments.
- Quota file iteration runs through `highid`, so unexpectedly large uid/gid values can make update work proportional to the numeric id range.
- The inode soft-limit reset code compares `dqb_curblocks` in both block and inode branches; that mirrors the source and is a behavior to verify before changing.
- In debug mode quota files are read and compared but not written/truncated.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/quotacheck/quotacheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/reboot/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/reboot/Makefile

## Purpose

Builds the `reboot` utility and installs `halt` as a hard link.

## Build Definition

The program is `reboot`, links with `libutil`, installs `reboot.8`, and creates a link from `reboot` to `halt`. Behavior differs based on invocation name.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/reboot/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/reboot/reboot.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/reboot/reboot.c

## Purpose

Implements `reboot` and `halt`, including shutdown logging, optional rc shutdown script execution, process termination, sync ordering, and final `reboot(2)` call.

## Main Behavior

The program checks its invocation name, setting halt mode and `RB_HALT` when invoked as `halt`. Options add dump, no-log, no-sync, powerdown for halt, and quick reboot flags. It requires effective root. Quick mode calls `reboot(howto)` immediately.

Normal mode logs the initiating user through syslog unless `-l` is used, records a wtmp shutdown entry, performs an early `sync()` unless `-n`, sends `SIGTSTP` to init, ignores SIGHUP and SIGPIPE, and runs `/etc/rc shutdown` on the console when present. If the rc script exits with status 2 during halt, powerdown is enabled.

After the point of no return, it blocks all signals, sends SIGTERM to all processes, waits while processes remain, syncs again unless disabled, sends repeated SIGKILL waves with increasing waits, then calls `reboot(howto)`. If process signaling fails unexpectedly, it attempts to restart init with SIGHUP and exits with an error.

## Platform Detail

When `CPU_LIDACTION` exists and powerdown is requested, it disables suspend-on-lid-close through `sysctl` before shutdown.

## Risks And Invariants

- `kill(-1, ...)` is used for broad process signaling; `ESRCH` is treated as success in single-user/exec cases.
- Init is stopped before rc shutdown and process killing; failure to stop init aborts.
- Signal blocking before final termination is intentional to guarantee progress to `reboot(2)`.
- `-p` is honored only when invoked as `halt`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/reboot/reboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/resolvd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/resolvd/Makefile

## Purpose

Builds `resolvd`.

## Build Definition

The program is `resolvd`, with source `resolvd.c` and manual page `resolvd.8`. It enables strict warnings and includes the current directory. `LDSTATIC=` is cleared so the daemon is not built static by default.

## Notable Detail

A commented `DEBUG` assignment documents a local debug build configuration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/resolvd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/resolvd/resolvd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/resolvd/resolvd.c

## Purpose

Daemon that listens for routing-socket DNS proposals and regenerates `/etc/resolv.conf`. It also integrates with `unwind` when available, preferring local resolver use while preserving proposed nameservers as commented fallback lines.

## Main State

`learned[ASR_MAXNS]` stores resolver proposals by interface index, address family, priority, and numeric IP string. `resolvfd` tracks the currently watched `/etc/resolv.conf`; `newkevent` rebuilds kqueue registrations. Non-small builds track whether `unwind` should be checked and whether its control socket is connected.

## Main Loop

`main()` parses debug/verbose flags, requires root, takes an exclusive nonblocking lock on `/dev/resolvd.lock`, daemonizes unless debugging, opens the route socket, filters for `RTM_PROPOSAL` and `RTM_IFANNOUNCE`, solicits current DNS proposals, unveils resolver files and optional unwind socket, pledges to `stdio unix rpath wpath cpath`, creates a kqueue, and enters an event loop.

Events include route socket readability, vnode changes on `/etc/resolv.conf`, and optional unwind socket readability/closure. Delete/rename of resolv.conf causes fd reset and regeneration; truncate/write causes a short sleep then regeneration to accommodate editors. Unwind connection changes also regenerate output.

## Route Message Handling

`route_receive()` reads one route message, validates basic length and version, ignores messages from itself, extracts sockaddr pointers with `get_rtaddrs()`, and calls `handle_route_message()`.

`handle_route_message()` copies current proposals into a local candidate array. Interface departure removes proposals from that interface. `RTM_PROPOSAL` with solicitation priority asks for a future unwind check. DNS proposals validate presence of `RTA_DNS`, address family, sockaddr length alignment, and count, then remove old proposals for the same interface/family and add new numeric IPv4/IPv6 nameserver strings. IPv6 link-local addresses get the route interface scope id before formatting. Proposals are sorted by priority with `mergesort()`, duplicate IPs per interface are zeroed, and a changed set triggers `regen_resolvconf()`.

## File Regeneration

`regen_resolvconf()` writes `/etc/resolv.conf.new`, building an iovec list. If unwind is running, it writes `nameserver 127.0.0.1`; learned nameservers are then emitted, commented out when unwind is active. It replays user-managed lines from the old `/etc/resolv.conf`, skipping lines containing the `# resolvd:` marker. It writes all data, fsyncs, renames into place, updates or replaces `resolvfd`, and asks the kqueue registration to be rebuilt. On error it closes the temp fd and unlinks the temp file.

## Logging

Non-small builds abstract console versus syslog logging through a `struct loggers` table. Debug mode logs to stderr; daemon mode logs through syslog. Verbose console logging is controlled by `-v`.

## Risks And Invariants

- `regen_resolvconf()` is all-or-nothing via temp file, fsync, and rename, but it preserves only user lines that fit within `UIO_MAXIOV` total iov entries.
- Lines containing `# resolvd: ` are considered daemon-managed and are not replayed.
- If proposal slots fill, `findslot()` discards the last slot for new proposals, assuming new data may be more important.
- Route-socket reads handle one buffer-sized message and reject partial messages; unusually large route messages beyond the fixed buffer are not processed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/resolvd/resolvd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/Makefile

## Purpose

Builds `restore` and installs `rrestore` as a hard link.

## Build Definition

The program is `restore`, linked also as `rrestore`. It defines `RRESTORE`, compiles restore sources plus `dumprmt.c` from `../dump`, installs `restore.8`, and uses `.PATH` to find dump-shared code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/dirs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/dirs.c

## Purpose

Directory handling for `restore`. It extracts directory records from dump tapes into temporary files, builds an inode-to-directory table, supports pathname lookup and recursive tree scans, and later restores directory metadata.

## Directory Extraction

`extractdirs()` creates a temporary directory file and optional mode file under `tmpdir`, then reads directory files from the tape while `curfile` is a directory. Each directory gets an `inotab` entry with its seek offset. Directory payload is passed through `getfile(putdir, xtrnull)`, normalized into `struct direct` records, terminated with a synthetic zero-inode `/` record, and sized by the resulting seek offset. If mode generation is enabled, `allocinotab()` writes owner, mode, flags, and access/modify/birth times to the mode file.

`skipdirs()` skips directory entries on tape without extracting them.

## Virtual Directory API

The file defines `RST_DIR`, `rst_opendir()`, `rst_readdir()`, and `rst_closedir()` over the temporary directory file. `rst_seekdir()` and `rst_telldir()` support repeated scans of many directories packed into one file. `rst_readdir()` reads fixed `DIRBLKSIZ` blocks, validates record lengths, treats the synthetic `/` marker as end of directory, rejects out-of-range inode numbers, and returns direct records.

## Lookup And Traversal

`pathsearch()` resolves absolute or relative canonical restore paths starting from `ROOTINO` by repeatedly calling `searchdir()`. `dirlookup()` is declared elsewhere and used by higher layers, while `treescan()` recursively walks the extracted directory hierarchy and calls a callback with `LEAF` or `NODE`. It skips `.` and `..`, guards against path overflow, and seeks back after recursive descent.

## Directory Record Conversion

`putdir()` supports old directory format conversion through `dcvt()` when `cvtflag` is set, byte-swaps fields when `Bcvt` is active, handles old inode format name-length quirks, validates record alignment/size/name length, and writes compacted records through `putent()` and `flushent()`.

## Metadata Restoration

`setdirmodes()` replays the mode file after extraction. It looks up each directory in the symbol table, skips existing interactive/batch directories unless forced, optionally asks before setting root metadata, and applies owner, mode, flags, and times unless `Nflag` dry-run mode is active.

## Other Helpers

`genliteraldir()` writes a literal copy of a dumped directory into a file named by inode when restore is in inode-name mode. `inodetype()` reports whether an inode has an `inotab` entry. `cleanup()` closes tape state and removes temp files.

## Risks And Invariants

- The temporary directory file is central to name-based restore; missing root directory is fatal.
- Path buffers are bounded, but long names may be skipped with warnings during traversal/listing.
- Directory entries from tape are partially trusted only after record-size validation; malformed records are skipped by block.
- `setdirmodes()` depends on symbol table entries created by extraction scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/dirs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/extern.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/extern.h

## Purpose

Cross-file function declarations for the restore program.

## Contents

Declares symbol table, directory, extraction, tape, utility, interactive, and remote tape functions used across `main.c`, `dirs.c`, `interactive.c`, `restore.c`, `symtab.c`, `tape.c`, `utilities.c`, and shared `dumprmt.c`.

## Notable Groups

- Tree/symbol operations: `addentry()`, `lookupino()`, `lookupname()`, `moveentry()`, `freeentry()`, `dumpsymtable()`, `initsymtable()`.
- Directory operations: `extractdirs()`, `treescan()`, `dirlookup()`, `pathsearch()`, `rst_opendir()`, `rst_readdir()`, `rst_closedir()`, `setdirmodes()`.
- Restore actions: `createfiles()`, `createleaves()`, `createlinks()`, `removeoldleaves()`, `removeoldnodes()`, `nodeupdates()`, `verifyfile()`.
- Tape/input operations: `setinput()`, `setup()`, `getfile()`, `getvol()`, `skipfile()`, `skipmaps()`, `newtapebuf()`.
- Remote tape operations are imported from `../dump/dumprmt.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/interactive.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/interactive.c

## Purpose

Interactive restore shell used by `restore -i`. It lets users browse the dump's virtual directory tree, mark files for extraction, unmark them, extract selected files, set modes, inspect dump metadata, and toggle verbosity/debugging.

## Command Loop

`runcmdshell()` initializes a glob context with alternate directory callbacks backed by `RST_DIR`, starts at canonical `/`, and loops reading commands. It handles `add`, `cd`, `delete`, `extract`, `help`/`?`, `ls`, `pwd`, `quit`/`xit`, `verbose`, `setmodes`, `what`, and `Debug`.

`add` resolves a path to an inode, optionally checks paths for restore-by-name mode, and calls `treescan(..., addfile)`. `delete` calls `treescan(..., deletefile)` for marked entries. `extract` runs `createfiles()`, `createlinks()`, `setdirmodes()`, and optional `checkrestore()`.

## Command Parsing

`getcmd()` reads from `terminal`, trims whitespace, splits the command and arguments, defaults missing arguments to the current directory, canonicalizes absolute and relative paths, and uses `glob()` with restore-backed directory/stat functions to expand patterns. Multi-argument commands are returned one path at a time across calls.

`copynext()` supports whitespace tokenization with backslash escaping and single/double quotes. `canon()` normalizes names to restore's `./...` form, collapses repeated/trailing slashes, and removes embedded `.` and `..` components.

## Listing And Globbing

`printlist()` resolves a path, skips files not present on the dump map unless debugging, and lists either a single file or directory contents. It marks selected entries with `*`, absent-debug entries with `^`, and appends type suffixes such as `/`, `@`, `=`, and `#`.

`mkentry()` converts a restore `struct direct` into display metadata. `formatf()` lays out sorted entries in columns and can include inode numbers in verbose mode. `glob_readdir()` and `glob_stat()` adapt restore's virtual directory tree to `glob(3)`.

## Interrupt Handling

`onintr()` longjmps back to the command shell during interactive commands, otherwise asks whether to continue and exits if declined. Source comments note signal/longjmp reentrancy and signal race concerns.

## Risks And Invariants

- Interactive globbing depends on `dumpmap` and the virtual directory file built by `extractdirs()`.
- `canon()` edits paths in fixed buffers; callers must provide `PATH_MAX`-sized destinations.
- The shell can leave partial glob state on interrupts, so `runcmdshell()` explicitly frees it after longjmp.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/interactive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/main.c

## Purpose

Top-level option parsing and mode dispatch for the restore program.

## Global State

Defines restore-wide flags (`bflag`, `cvtflag`, `dflag`, `vflag`, `yflag`, `hflag`, `mflag`, `Nflag`), command mode, dump number, volume number, tape block count, inode maps, max inode, dump times, terminal pointer, and temp directory.

## Main Flow

`main()` sets a restrictive umask for temp files, chooses input tape from `$TAPE` or default, chooses temp directory from `$TMPDIR` or default, accepts obsolete non-dash option syntax through `obsolete()`, parses modern flags, requires exactly one command among interactive, resume, full/incremental restore, table/list, and extract modes, installs interrupt handlers, registers `cleanup()`, and calls `setinput()`.

Mode dispatch:

- `i`: setup, extract directories with modes, initialize a new symbol table, run interactive shell.
- `r`: setup; if incremental, load existing symbol table, extract dirs, remove old leaves, compute node updates, resolve links, remove old nodes; if level zero, initialize fresh state; then extract leaves, create links, set directory modes, check, optionally verify, and checkpoint symbol table.
- `R`: resume from existing symbol table, skip maps/dirs, continue leaf extraction, links, modes, checks, and checkpoint.
- `t`: setup, extract dirs without modes, initialize symbol table, list requested paths.
- `x`: setup, extract dirs with modes, initialize symbol table, mark requested paths, extract files, create links, set modes, optional check.

## Obsolete Syntax

`obsolete()` converts historical compact restore options and ordered arguments into `getopt()`-compatible argv. Options requiring arguments (`b`, `f`, `s`) consume following argv entries and are rewritten as `-xVALUE`; other flags are grouped behind a single dash.

## Risks And Invariants

- Command modes are mutually exclusive and one is required.
- `atexit(cleanup)` is registered before setup proceeds so temporary directory/mode files are removed.
- `Nflag` dry-run mode is global and honored by lower layers for writes/checkpoints.
- The mode switch assumes `setup()` populates maps, tape metadata, and `curfile` for all modes except resume.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/restore.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/restore.c

## Purpose

Core restore algorithms: listing, marking extraction requests, deleting requests, computing incremental restore updates, removing obsolete names, extracting scheduled files, creating links, and validating symbol-table completion.

## Basic Listing And Marking

`listfile()` implements tape listing callbacks and prints entries present in `dumpmap`. `addfile()` marks dump entries for extraction, creating symbol table entries when needed and handling inode-name mode by generating literal directory files. `deletefile()` clears `NEW` on requested entries and frees non-directory entries.

## Incremental Restore State Machine

`removeoldleaves()` walks old symbol table entries and removes leaves whose inode is no longer in `usedinomap`; directories are given temp names, removed from inode lookup, and deferred on `removelist`.

`nodeupdates()` is the main incremental decision table. For each path from the new dump, it derives a key from whether the inode is on tape, inode exists, name exists, and file type changed. It then chooses KEEP, NEW, EXTRACT, LINK, rename, temp-name, remove, or deferred directory deletion behavior. It handles name/inode conflicts, hard links, mode/type changes, deleted hard links to directories, files created during dump, and inconsistent/impossible symbol-table states.

`findunreflinks()` removes unreferenced leaf names after node update processing, including leaves stranded inside removed directories. `removeoldnodes()` repeatedly removes empty deferred directories from `removelist`, reporting any non-empty remainder.

## Extraction Scheduling

`createleaves()` is used by full/incremental restore. It checkpoints before extraction, then walks tape file order against the lower bound of pending inodes, reports missing expected files, skips unexpected files, extracts files through `extractfile(myname(ep))`, clears `NEW|EXTRACT`, and checkpoints after volume changes.

`createfiles()` is used by extract/interactive modes. It rewinds to volume one, skips maps and directories, computes first/last requested inode bounds, skips volumes whose current inode is too high, skips forward to needed inodes, reports missed requested files, extracts matches, and clears `NEW`.

## Link And Verification Passes

`createlinks()` walks all entries and creates pending hard links or symlinks for directory hard-link cases. `checkrestore()` clears transient flags and reports incomplete operations. `verifyfile()` compares the final symbol table against the tape directory tree.

## Risks And Invariants

- Incremental correctness depends on the `nodeupdates()` key table; changing symbol-table flags or entry types can break rename/link semantics.
- Directories cannot be removed immediately when obsolete because live children may still need to be renamed out.
- Extraction assumes tape file order by inode and uses bounds from symbol table helpers (`lowerbnd()`, `upperbnd()`).
- Checkpointing after volume changes is required for `restore -R` resume.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/restore.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/restore.h

## Purpose

Shared global declarations, data structures, flags, and macros for the restore program.

## Key Definitions

Declares global option flags, inode maps, tape/dump metadata, command mode, terminal and temp directory state, old-format/byte-swap flags, and `__progname`.

Defines `struct entry`, the in-memory restore symbol table node. Entries track current name, type, flags, old inode number, checkpoint index, parent, sibling, hard-link chain, directory children, and inode hash chain.

Defines entry types `LEAF`, `NODE`, and synthetic `LINK`, flags such as `EXTRACT`, `NEW`, `KEEP`, `REMOVED`, `TMPNAME`, and `EXISTED`, link kinds, temp-name prefix, current tape-file context `curfile`, and actions `USING`, `SKIP`, and `UNKNOWN`.

Also declares `RST_DIR`, `FORCE` for directory mode restoration, inode bitmap macros `TSTINO`/`SETINO`, debug/verbose print macros, and `GOOD`/`FAIL`.

## Coupling

Every restore implementation file shares these globals and entry semantics. The symbol table, directory traversal, extraction scheduling, and tape reader all coordinate through `curfile`, inode maps, and `struct entry` flags.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/restore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/symtab.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/restore/symtab.c

## Purpose

Maintains restore's in-memory symbol table and checkpoint file format. The table supports lookup by inode and by path, dynamic entry creation/deletion/rename, hard-link tracking, name allocation, and serialization for incremental restore resume.

## Inode And Name Lookup

The inode hash table is allocated based on `maxino / HASHFACTOR`. `lookupino()` returns the primary entry for an inode. `addino()` inserts entries by inode and checks duplicates in debug mode. `deleteino()` removes an inode's primary hash entry and clears its inode field.

`lookupname()` resolves a path by walking from `ROOTINO` through directory children. `lookupparent()` temporarily truncates the path at the final slash, looks up the parent, restores the slash, and verifies the parent is a directory. `myname()` reconstructs the current full pathname by walking parent pointers backward into a static buffer.

## Entry Lifecycle

`addentry()` uses a freelist or allocates a new `struct entry`, sets type, links it into the parent's child list, and either inserts it into the inode table or links it into an existing inode's hard-link chain for synthetic `LINK` entries. Root creation is special: it has itself as parent and must be inode `ROOTINO`.

`freeentry()` requires `REMOVED`, validates directory emptiness, removes the entry from inode or hard-link chains, removes it from the parent child list, frees its name to the string freelist, and places the entry on the entry freelist. `moveentry()` relocates an entry to a new parent/name and updates the `TMPNAME` flag based on `gentempname()`.

## Name Allocation

`savename()` and `freename()` manage variable-length names through size-class freelists indexed by allocation size increments. Freed strings are reused for later names of matching size class.

## Checkpoint Format

`dumpsymtable()` writes a symbol table snapshot unless `Nflag` is set. It assigns each entry an index, writes all names first, writes copies of entries with pointers converted to indexes/offsets, writes the inode hash table as entry indexes, and appends a `symtableheader` containing checkpoint volume, string size, table size, dump times, max inode, and tape block count.

`initsymtable(NULL)` creates a new table and root entry. `initsymtable(filename)` reads a checkpoint, validates incremental/resume tape timing, restores tape position for `R`, sets `maxino`/table size, maps the hash table into the loaded memory block, and converts indexes/offsets back into pointers.

## Risks And Invariants

- `myname()` uses a static buffer; callers must not expect stable results across subsequent calls.
- Checkpoint serialization assumes local pointer-sized placeholder fields can safely store and recover integer indexes through casts within the same architecture/build.
- `entrytblsize = maxino / HASHFACTOR` must be nonzero before creating a fresh table.
- Directory entries must be empty and unlinked before `freeentry()` accepts them.
- Path lookup mutates the input string temporarily in `lookupparent()`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/restore/symtab.c -->