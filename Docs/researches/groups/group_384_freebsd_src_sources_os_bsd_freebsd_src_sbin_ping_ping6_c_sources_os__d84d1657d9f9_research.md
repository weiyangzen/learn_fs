# Group Research: group_384_freebsd_src_sources_os_bsd_freebsd_src_sbin_ping_ping6_c_sources_os__d84d1657d9f9

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`, so every file below is in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping6.c

FreeBSD `ping6` implementation for IPv6 ICMP echo and IPv6 Node Information queries.

Key elements:
- `ping6(int argc, char *argv[])` parses IPv6 ping options, resolves target/source/gateway addresses through Casper DNS, opens raw ICMPv6 send/receive sockets, configures socket options, drops privilege, enters Capsicum capability mode, sends probes, receives replies with `recvmsg`, and exits with ping-compatible status.
- Supports echo request/reply, flood mode, quiet mode, audible/missed-packet indicators, source address/interface selection, hop limit, traffic class, VLAN PCP, no-fragment, wait timeout, preload, route headers, minimum MTU/path MTU options, and optional IPsec policy handling.
- Node Information modes include FQDN, old FQDN draft format, node address, supported query types, and multicast NI group address generation via MD5 in `nigroup`.
- `pingerlen` and `pinger` compose either ICMPv6 echo requests or ICMPv6 NI queries. Echo timing stores a compact 32-bit seconds/nanoseconds timestamp in the payload.
- `pr_pack` validates received sockaddr/control data, extracts hop limit and packet info, recognizes this process’s echo or NI replies, updates packet counters/timing stats, detects duplicates through `rcvd_tbl`, checks returned payload bytes, and prints normal or verbose output.
- Packet printers cover extension headers, hop-by-hop/destination options, routing headers, supported NI qtype bitmaps, NI node addresses, ICMPv6 error classes, returned IPv6 headers, TCP/UDP quoted ports, and DNS name decoding.
- `capdns_setup` opens `system.dns` through Casper and limits DNS operations to IPv6 name/address lookups when built with Casper support.

Dependencies:
- Shares global ping state and helpers from `main.h`, including `options`, `hostname`, counters, timing accumulators, signal flags, `usage`, `onsignal`, and `pr_summary`.
- Uses FreeBSD-specific Capsicum/Casper APIs, raw IPv6 socket options, ICMPv6/Node Information definitions, routing header helpers, and optional IPsec APIs.
- Uses `<md5.h>` for NI multicast group generation.

Research notes:
- The program does privileged setup first, then drops uid/euid and further restricts descriptors under Capsicum; later DNS is limited to reverse lookups.
- Receive-side validation depends on `IPV6_HOPLIMIT` and `IPV6_PKTINFO` control messages being delivered; missing ancillary data makes a packet unusable.
- `setpolicy(int so __unused, char *policy)` ignores its `so` argument and applies policy to the global send socket.
- Exit codes distinguish at least one reply (`0`), transmitted but no replies (`2`), and send/open/system failure (`EX_OSERR` or `err` path).
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping6.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping6.h

Small public header for the IPv6 ping entry point.

Key elements:
- Include guard `PING6_H`.
- Declares `int ping6(int argc, char *argv[]);`.

Dependencies:
- Consumed by the ping main program and implemented in `ping6.c`.

Research notes:
- No structs, macros, or shared state are exposed; the header intentionally keeps IPv6 ping integration to one function.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/ping6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/Makefile

ATF test build file for ping tests.

Key elements:
- Builds C ATF test `in_cksum_test` from `in_cksum_test.c` plus parent-directory `utils.c`.
- Registers pytest test `test_ping.py` and shell ATF test `ping_test`.
- Marks `ping_test` exclusive because injection cases reuse fixed IP addresses.
- Installs expected-output fixtures and `injection.py`.

Dependencies:
- Uses FreeBSD `bsd.test.mk`.
- Depends on parent `utils.c` for checksum test coverage.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/in_cksum_test.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/in_cksum_test.c

ATF-C unit tests for the Internet checksum helper.

Key elements:
- Four test cases cover aligned even length, aligned odd length, unaligned even length, and unaligned odd length inputs.
- Each test calls `in_cksum` and asserts expected checksum bytes.
- Registers all test cases through `ATF_TP_ADD_TCS`.

Dependencies:
- Includes `../utils.h`.
- Uses ATF-C and FreeBSD `nitems`.

Research notes:
- The tests explicitly exercise unaligned input by offsetting an aligned byte array by one byte, matching the implementation’s `memcpy`-based unaligned-safe reads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/in_cksum_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/injection.py -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/injection.py

Scapy helper for shell ATF packet-injection tests.

Key elements:
- Creates a tun interface, records its name in `tun.txt`, configures RFC 5737 test addresses, starts `/sbin/ping -v -c1 -t1`, receives the echo request, and injects a crafted response.
- Modes:
  - `opts`: echo reply containing 40 NOP IP options.
  - `pip`: ICMP host-unreachable packet quoting an inner packet with options.
  - `reply`: normal echo reply.
- Exits with the child ping process return code.

Dependencies:
- Requires root privileges, `python3`, Scapy, `ifconfig`, tun/tap support, and `/sbin/ping`.

Research notes:
- Cleanup is external in `ping_test.sh`; this script only writes `tun.txt` so the ATF cleanup hook can destroy the created tun interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/injection.py -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/ping_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/ping_test.sh

ATF shell smoke and regression tests for `ping` and `ping6`.

Key elements:
- `require_ipv4` and `require_ipv6` skip tests when localhost address families are unavailable.
- Covers basic IPv4/IPv6 one-packet pings, source-address selection with `-S`, invocation through `ping6`, option parsing for `-t4`/`-t6`, mutually exclusive `-4`/`-6`, nonexistent host failures, and `ping6 -4` rejection.
- Packet injection tests run `injection.py` in `opts`, `pip`, and `reply` modes and destroy the tun interface in cleanup hooks.
- `timestamp_origin` enables `net.inet.icmp.tstamprepl`, runs `ping -Mt`, extracts originate/receive timestamps, allows a two-second difference, and restores the sysctl.
- `check_ping_statistics` normalizes timing, address, `ttl`, and `hlim` fields before diffing fixture output.

Dependencies:
- ATF shell framework, `getaddrinfo`, `ping`, `ping6`, `sysctl`, `date`, and optional Scapy for injection cases.

Research notes:
- Tests with mutable network state are either root-only or require `allow_sysctl_side_effects`.
- Injection tests are exclusive at Makefile metadata level because fixed addresses and `tun.txt` would otherwise conflict.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/ping_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/test_ping.py -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/test_ping.py

Pytest/Scapy ping regression harness using a single vnet and tun interfaces.

Key elements:
- Provides a Scapy fallback shim so tests can be enumerated even when Scapy is absent.
- `build_response_packet` mutates the captured echo request into echo replies or ICMP error packets, including special cases for no payload, TCP/UDP quoted packets, timestamp warp, wrong payload byte, and not-this-process identifiers.
- `generate_ip_options` constructs EOL/NOP/RR/LSRR/SSRR/unknown IP options and disables kernel IP option processing when necessary.
- `pinger` creates/configures a tun interface, runs `/sbin/ping`, receives outbound echo packets, injects crafted replies/errors, optionally sends duplicates, and returns a `CompletedProcess`.
- `redact` normalizes dynamic output such as addresses, hop limits, TTL, timings, hex dumps, and negative time deltas.
- `TestPing` sets IPv4/IPv6 test prefixes, validates many direct ping command outputs, validates common `ping -4`/`ping -6` argument errors, and parametrically tests crafted ICMP/IP edge cases.

Dependencies:
- `atf_python.sys.net.vnet`, `IfaceFactory`, `SingleVnetTestTemplate`, `ToolsHelper`, pytest markers, Scapy, tun interfaces, root privileges for packet injection.

Research notes:
- The test matrix exercises normal replies, no-reply exits, quiet mode, audible missed packets, source address output, malformed IP options, truncated quoted packets, DF flags, wrong payload reporting, and time-warp clamping.
- Expected outputs are mostly exact strings, with redaction applied only for fields that are intentionally variable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/tests/test_ping.py -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/utils.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/utils.c

Shared checksum helper for ping.

Key elements:
- Implements `u_short in_cksum(u_char *addr, int len)`.
- Adds 16-bit words into a 32-bit accumulator, handles odd trailing byte through a union, folds carries, and returns one’s complement.
- Uses `memcpy` for each 16-bit word to avoid unaligned access faults.

Dependencies:
- Declared by `utils.h`.
- Used by ping code/tests for Internet Protocol family checksum calculation.

Research notes:
- The odd-byte behavior is endian-sensitive in the same way as traditional BSD checksum implementations; tests assert byte-level expected results on the target platform.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/utils.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ping/utils.h

Header for ping utility helpers.

Key elements:
- Include guard `UTILS_H`.
- Includes `<sys/types.h>`.
- Declares `u_short in_cksum(u_char *, int);`.

Dependencies:
- Included by checksum tests and checksum users.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ping/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/Makefile

Build file for the `quotacheck` utility.

Key elements:
- Builds program `quotacheck` in package `quotacheck`.
- Sources are `quotacheck.c`, `preen.c`, plus shared `fsutil.c` and `utilities.c` from fsck paths.
- Links `libutil` and `libufs`.
- Installs `quotacheck.8`.

Dependencies:
- `.PATH` pulls sources from sibling `fsck` and `fsck_ffs`.
- Uses `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/preen.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/preen.c

`quotacheck -a` preen scheduler that processes fstab entries by pass number and disk.

Key elements:
- Defines `partentry` for a filesystem/quota pair and `diskentry` for a disk base name with a partition queue and child pid.
- `checkfstab` walks `/etc/fstab` by pass number, opens user/group quota files as requested, checks pass-1 filesystems directly, queues later passes by disk, forks one child per disk, waits, records failures, and starts the next partition on a disk when the previous child exits.
- `finddisk` groups device names by base disk name, stopping after the first numeric unit sequence.
- `addpart` converts the fstab spec through `blockcheck`, stores mountpoint/quota handles, and rejects duplicate device entries within a disk queue.
- `startdisk` forks and runs `chkquota` for the first queued partition.

Dependencies:
- Uses `quotacheck.h`, libutil quota APIs, fstab APIs, `TAILQ`, and `emalloc`/`estrdup` helpers supplied by linked fsck utilities.

Research notes:
- Failed partitions are retained in `badh` for a final “unexpected inconsistency” summary.
- Successful child completion closes quota files in the parent; failed entries remain allocated until process exit for summary reporting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/preen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.c

Main UFS quota checker and quota usage reconciler.

Key elements:
- `main` parses `-a`, `-c 32|64`, `-g`, `-u`, `-v`, and deprecated `-l`; preloads passwd/group ids into hash tables; dispatches either all-fstab checking via `checkfstab` or selected filesystem checking.
- `chkquota` optionally converts quota format, opens the raw filesystem, reads the UFS superblock through `sbget`, scans cylinder groups and allocated inodes, skips invalid negative-looking IDs, snapshot files, and quota files themselves, accumulates per-user/per-group inode and block usage, then updates quota files.
- `update` compares accumulated usage to existing `dqblk` records, writes changed usage with `quota_write_usage`, handles ids beyond current quota file max id, and truncates stale tail records when safe.
- `lookup`/`addid` maintain per-quota-type hash tables of `fileusage` records.
- `setinodebuf`, `getnextinode`, and `freeinodebuf` implement buffered sequential inode reads per cylinder group.
- `blkread` seeks and reads raw filesystem blocks using the filesystem device block size.
- `printchanges` reports verbose before/after usage fixes.

Dependencies:
- UFS/FFS headers, libufs, libutil quota APIs, fstab/passwd/group databases, shared `blockcheck`, and `checkfstab`.

Research notes:
- The scanner has separate UFS1/UFS2 inode field access through the `DIP` macro.
- Soft updates filesystems use cylinder group inode allocation maps to reduce scanning.
- Some early error returns after opening the device do not close `fi`; the process is short-lived, but it is still a cleanup asymmetry.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.h

Shared declarations for `quotacheck`.

Key elements:
- Declares `blockcheck`, `checkfstab`, and `chkquota`.

Dependencies:
- `chkquota` uses `struct quotafile *`, so consumers must include quota definitions before or alongside this header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/quotacheck/quotacheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/Makefile

Build file for `rcorder`.

Key elements:
- Builds `rcorder` from `ealloc.c`, `hash.c`, and `rcorder.c`.
- Links `libutil`.
- Defines `ORDER` in `CFLAGS`, enabling `Hash_GetKey` support.
- Installs `rcorder.8`.

Dependencies:
- Uses `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.c

Fatal-on-failure allocation wrappers used by rcorder.

Key elements:
- `enomem` exits with `errx(2, "Cannot allocate memory.")`.
- `emalloc`, `estrdup`, `erealloc`, and `ecalloc` wrap standard allocation functions and abort on failure.

Dependencies:
- Declared by `ealloc.h`.
- Used by `hash.c` and `rcorder.c`.

Research notes:
- These helpers simplify rcorder graph code by making allocation failure nonrecoverable and avoiding repeated null checks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.h

Allocation wrapper declarations for rcorder.

Key elements:
- Declares `emalloc`, `estrdup`, `erealloc`, and `ecalloc`.

Dependencies:
- Requires `size_t` to be visible from the including translation unit.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/hash.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/hash.c

String-key hash table implementation imported from BSD/Sprite lineage.

Key elements:
- `Hash_InitTable` creates a power-of-two bucket table, defaulting to 16 buckets.
- `Hash_FindEntry` hashes strings with `h = (h << 5) - h + c` and searches the bucket chain by cached hash plus strcmp.
- `Hash_CreateEntry` returns an existing entry or allocates a flexible key-sized entry, rebuilding when entries reach eight times bucket count.
- `Hash_DeleteEntry`, `Hash_DeleteTable`, `Hash_EnumFirst`, and `Hash_EnumNext` provide deletion and full-table enumeration.
- `RebuildTable` doubles bucket count and relinks all entries by cached hash.

Dependencies:
- Uses `sprite.h` for `Boolean`/`ClientData`, `hash.h` for structures/macros, and `ealloc.h` for fatal allocation.

Research notes:
- `Hash_DeleteEntry` aborts on an entry that is not in the expected bucket, treating misuse as programmer error.
- Entries store key text inline through `char name[1]` plus over-allocation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/hash.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/hash.h

Public interface and types for rcorder’s hash table.

Key elements:
- Defines `Hash_Entry`, `Hash_Table`, and `Hash_Search`.
- Provides `Hash_GetValue`, `Hash_SetValue`, and, under `ORDER`, `Hash_GetKey`.
- Declares initialization, deletion, lookup, creation, entry deletion, and enumeration functions.
- `Hash_Size` converts byte counts to word counts.

Dependencies:
- Requires `ClientData` and `Boolean` from `sprite.h`.

Research notes:
- This is generic infrastructure but tightly used by `rcorder.c` to map provision names to provider lists.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder-visualize.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder-visualize.sh

Small shell helper to emit Graphviz dot for rc script dependency comments.

Key elements:
- Defaults input files to `/etc/rc.d/*` or accepts file arguments.
- Emits `digraph { ... }`.
- For each file, awk extracts one `# PROVIDE:` token, all `# REQUIRE:` tokens, and all `# BEFORE:` tokens.
- Prints provider nodes, provider-to-requirement edges, and before-to-provider edges.

Dependencies:
- POSIX shell, awk, and Graphviz for optional rendering.

Research notes:
- This is a lightweight visualizer, not a full `rcorder` equivalent; it does not implement keyword filtering, multiline parsing, duplicate providers, fake provisions, or cycle handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder-visualize.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder.c

Dependency sorter for rc-style scripts.

Key elements:
- Parses options `-d`, `-g`, `-k keyword`, `-p`, and `-s keyword`.
- `crunch_file` reads regular files using `fparseln`, scans initial dependency comment block, and records `# REQUIRE:`, `# REQUIRES:`, `# PROVIDE:`, `# PROVIDES:`, `# BEFORE:`, `# KEYWORD:`, and `# KEYWORDS:`.
- `add_provide` maps provision names to provider lists in `provide_hash`; duplicate providers are allowed.
- `add_before` stores `BEFORE` constraints, and `insert_before` converts each into a fake provision required by files that provide the target.
- `satisfy_req` recursively satisfies requirement providers, detects missing providers and circular provision dependencies, and emits Graphviz edges when requested.
- `do_file` recursively processes requirements, assigns sequence numbers, removes satisfied providers from provision lists, tracks circular-dependency issues, and queues printable files if keyword filters allow.
- `generate_ordering` drives the traversal, sorts by sequence, and prints one file per line or same-sequence files on one line with `-p`.
- Graphviz mode emits provider nodes, dependency edges, missing-provider nodes, and red highlighting for cycle participants.

Dependencies:
- Uses `libutil` `fparseln`, `basename`, local `ealloc`, `sprite`, and `hash` infrastructure.

Research notes:
- Keyword filters are post-ordering output filters: `-s` suppresses matching files, `-k` keeps only matching files unless no keep list exists.
- Fake provision names are prefixed `fake_prov_` and hidden from normal Graphviz edge labels.
- Circular dependency handling continues after warnings and pushes involved files toward the tail by sequence.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/sprite.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/sprite.h

Compatibility type header from Sprite/BSD lineage.

Key elements:
- Defines integer `Boolean`, `TRUE`, `FALSE`, `ReturnStatus`, `SUCCESS`, `FAILURE`, `NIL`, `USER_NIL`, `NULL`, `Address`, and `ClientData`.
- `ClientData` is `void *`.

Dependencies:
- Used by `hash.h`/`hash.c`.

Research notes:
- The header exists to support imported generic hash code rather than FreeBSD-wide conventions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rcorder/sprite.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/reboot/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/reboot/Makefile

Build file for reboot-family commands.

Key elements:
- Builds `reboot` in package `runtime`.
- Installs manpages `reboot.8` and `nextboot.8`, plus architecture boot manpages when present.
- Creates hard links/symlinks from `reboot` to `halt`, `fastboot`, `fasthalt`, and `nextboot`.

Dependencies:
- Uses machine-specific manpage conditionals and `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/reboot/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/reboot/reboot.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/reboot/reboot.c

Implementation shared by `reboot`, `halt`, `fastboot`, `fasthalt`, and `nextboot`.

Key elements:
- Program behavior is selected from `getprogname`: `fast*` enables fast shutdown, `halt` sets halt mode, `nextboot` switches to nextboot option parsing.
- `zfsbootcfg` invokes `zfsbootcfg` to set `nextboot_enable=YES` in ZFS nvstore.
- `write_nextboot` atomically writes `/boot/nextboot.conf`, optionally preserving old content, writing `nextboot_enable` for UFS, adding kernel/env settings, fsyncing, and renaming the temp file.
- `split_kv` parses `name=value` option strings, including quoted values.
- `add_env` appends boot environment assignments to a generated buffer.
- `shutdown` signals init with the signal corresponding to reboot/halt/poweroff/powercycle/reroot.
- `main` validates option combinations, handles nextboot deletion/writes, checks root permissions for reboot modes, logs shutdown intent, writes utmpx shutdown time, syncs, signals init/processes, waits for paging activity to settle, sends SIGKILL if needed, and calls `reboot`.
- `get_pageins` reads `vm.stats.vm.v_swappgsin` to decide whether to wait longer before SIGKILL/reboot.

Dependencies:
- FreeBSD reboot flags, boottrace, sysctl, syslog, utmpx, process signals, `/boot/nextboot.conf`, optional `zfsbootcfg`.

Research notes:
- `nextboot` does not require root until actual reboot paths; it writes nextboot configuration and exits.
- `-D` only deletes existing nextboot config and refuses combination with other actions.
- `add_env` checks `env == NULL` after `asprintf`, but `env` is the address of the caller pointer; the intended failure check is likely `*env == NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/reboot/reboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/recoverdisk/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/recoverdisk/Makefile

Build file for `recoverdisk`.

Key elements:
- Builds `recoverdisk` in package `runtime`.
- Adds `-lm` for math functions.
- Provides a simple local `test` target running `./recoverdisk /dev/ad0`.

Dependencies:
- Uses `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/recoverdisk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/recoverdisk/recoverdisk.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/recoverdisk/recoverdisk.c

Disk/file recovery utility that copies readable ranges and retries failures at smaller block sizes.

Key elements:
- Tracks pending byte ranges as `struct lump { start, len, pass }` in a TAILQ.
- Tracks throughput per minute, quarter-hour, hour, and day for verbose reporting.
- `report` prints progress, pending count, success ratio, duration, histogram, and recent-period read totals.
- `new_lump` appends unread/retry work.
- `save_worklist` fsyncs destination, writes pending lumps to a temp worklist, and renames atomically.
- `read_worklist` restores pending ranges from a saved worklist.
- `write_buf` writes recovered or unreadable-pattern bytes at the original offset and saves the worklist on write errors.
- `attempt_one_lump` reads the first pending range using big/medium/small size by pass, writes successes, logs successes, accounts progress, and on read error writes the unreadable pattern, creates a smaller retry lump, and advances/removes the current lump.
- `determine_total_size` uses explicit `-t`, device media size, or regular file size.
- `determine_read_sizes` chooses small/medium/big read sizes from ioctl sector/stripe/firmware geometry or defaults, enforcing multiples.
- `monitor_read_sizes` adapts to repeated failures by shrinking big/medium reads.
- `main` parses read size, interval, log, pause, worklist, total size, unreadable pattern, and verbose options; opens source/destination; initializes buffers and worklist; loops until complete or SIGINT; saves worklist and reports final status.

Dependencies:
- FreeBSD disk ioctls, `TAILQ`, `pread`/`pwrite`, `fdatasync`, `ftruncate`, terminal size/ioctl, math `round`, and POSIX signals.

Research notes:
- The destination is pre-sized with `ftruncate`; unreadable regions can be filled with `_UNREAD_` or a user pattern.
- SIGINT is only specially handled when a write worklist is requested.
- The hour/day TAILQ initializers name `quarter` instead of their own heads in the static declarations, which is unusual and worth checking if modifying this code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/recoverdisk/recoverdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/resolvconf/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/resolvconf/Makefile

Build/install file for imported openresolv scripts and support files.

Key elements:
- Uses `${SRCTOP}/contrib/openresolv` as source path.
- Installs script `resolvconf`.
- Installs support files `libc`, `dnsmasq`, `named`, `pdnsd`, `pdns_recursor`, and `unbound` under `/libexec/resolvconf`.
- Generates scripts/files/manpages from `.in` templates with `sed` substitutions for sysconf, libexec, var, rc, sbin paths, restart command, and FreeBSD VPN interface pattern handling.
- Defines restart command through `/usr/sbin/service ... onestatus && ... restart`.

Dependencies:
- `bsd.prog.mk`, openresolv template files, and FreeBSD service layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/resolvconf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/restore/Makefile

Build file for the UFS dump restore utility.

Key elements:
- Builds `restore` from sources in sibling `dump` directory.
- Creates `rrestore` link and manpage alias.
- Source list includes `main.c`, `interactive.c`, `restore.c`, `dirs.c`, `symtab.c`, `tape.c`, `utilities.c`, and `dumprmt.c`.
- Adds `-DRRESTORE` and `-D_ACL_PRIVATE`; warning level is set to 2.

Dependencies:
- Uses `.PATH` to reuse dump/restore source files and `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/restore/Makefile -->