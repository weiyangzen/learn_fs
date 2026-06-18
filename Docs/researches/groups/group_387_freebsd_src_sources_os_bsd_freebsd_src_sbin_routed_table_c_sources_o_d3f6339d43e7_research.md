# Group Research: group_387_freebsd_src_sources_os_bsd_freebsd_src_sbin_routed_table_c_sources_o_d3f6339d43e7

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/table.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/table.c

## Summary
Core routing-table implementation for FreeBSD `routed`. It maintains the daemon’s radix-tree route table, aggregates routes for advertisements/kernel installation, mirrors kernel routing-table state, reacts to routing-socket messages, and ages stale routes/interfaces.

## Main Responsibilities
- Initializes and manages the IPv4 radix tree used by the daemon route table.
- Aggregates compatible routes with `ag_check()` and flushes pending aggregation slots with `ag_flush()`.
- Installs, changes, or deletes kernel routes through routing-socket `RTM_*` messages.
- Keeps a hash-table shadow of kernel routes to avoid unnecessary kernel updates and to detect externally changed routes.
- Imports kernel routing-table state with `sysctl(CTL_NET, PF_ROUTE, NET_RT_DUMP)`.
- Processes routing socket events in `read_rt()`, including route add/change/delete, redirects, packet-loss notices, and interface-address changes.
- Ages RIP routes, remote interfaces, route spares, redirected routes, and poisoned routes.
- Handles route add/change/delete/switch logic for primary and spare route slots.

## Key Elements
- `ag_slots`, `ag_avail`, `ag_corsest`, `ag_finest`: fixed aggregation workspace ordered by mask coarseness.
- `ag_check()`: promotes even/odd route pairs, suppresses redundant finer routes, preserves sequence/tag/next-hop metadata, and punts non-contiguous masks.
- `rtioctl()` / `kern_ioctl()`: build and send routing messages with destination, gateway, mask, metric, and flags.
- `kern_find()` / `kern_add()`: manage the kernel-route mirror hash.
- `flush_kern()` / `fix_kern()`: synchronize the kernel’s routing table with the daemon’s current table.
- `rtm_add()` / `rtm_lose()` / `del_redirects()`: handle kernel-originated route changes and redirects.
- `rtadd()`, `rtchange()`, `rtswitch()`, `rtdelete()`: core daemon-table mutation paths.
- `walk_age()` / `age()`: periodic aging pass for routes, remote interfaces, and kernel synchronization.

## Dependencies And Integration
Depends on `defs.h` for route/interface structures, macros, timers, tracing hooks, RIP/router-discovery state, and global sockets. Uses BSD radix tree APIs, routing sockets, PF_ROUTE sysctl dumps, interface lookup helpers, and RIP/router-discovery callbacks.

## Research Notes
The file’s central invariant is that the daemon table and kernel table are related but not identical: static kernel routes are preserved and imported into the daemon, redirect-created routes are tracked separately, and daemon route aggregation decides what should actually be installed in the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/table.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/trace.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/routed/trace.c

## Summary
Tracing and formatting support for `routed`. It manages trace files/levels, logs daemon actions, dumps route/interface state, formats route names and flag bitfields, and traces RIP packets including authentication and route contents.

## Main Responsibilities
- Opens, reopens, closes, and flushes trace output.
- Raises/lowers trace level from command-line, RIP trace commands, or SIGUSR1/SIGUSR2.
- Restricts remote trace-file names to configured/approved paths.
- Formats IPv4 addresses, route names, interface flags, route state flags, metrics, tags, timers, and spare route slots.
- Dumps current interface and route table state.
- Traces RIP request/response packets and RIP trace-on/trace-off commands.
- Displays RIP password or MD5 authentication metadata in packet traces.

## Key Elements
- `tracelevel`, `new_tracelevel`, `ftrace`: global trace control state.
- `set_tracefile()` and `tracelevel_msg()`: controlled trace-file and level transitions.
- `addrname()`, `rtname()`, `trace_bits()`: reusable formatting helpers.
- `trace_if()`, `trace_change()`, `trace_add_del()`, `trace_upslot()`: route/interface action logging.
- `trace_dump()` and `walk_trace()`: full daemon-state dump.
- `trace_rip()`: RIP packet summary/content decoder.

## Dependencies And Integration
Uses `defs.h`, `pathnames.h`, RIP command names, route/interface structures, radix-tree walking, and daemon time globals. Trace output is consumed by other `routed` modules through `trace_act`, `trace_misc`, `trace_pkt`, and route formatting helpers.

## Research Notes
Trace control is deliberately conservative for network-requested trace files: arbitrary names are rejected unless they match the initial trace path or configured trace directory policy.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/routed/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rtsol/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/rtsol/Makefile

## Summary
Builds the `rtsol` runtime utility from sources shared with `usr.sbin/rtsold`.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/usr.sbin/rtsold`.
- Builds `PROG=rtsol` with no installed man page from this Makefile.
- Reuses `cap_llflags.c`, `cap_script.c`, `cap_sendmsg.c`, `dump.c`, `if.c`, `rtsol.c`, `rtsold.c`, and `rtsock.c`.
- Links `libutil`.
- Conditionally enables Casper support unless dynamic root is disabled, Casper is disabled, or building rescue.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`, `src.opts.mk`, and optional `cap_syslog`, `casper`, and `nv` libraries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/rtsol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/savecore/Makefile

## Summary
Builds the `savecore` runtime utility and installs the default crash-directory `minfree` configuration.

## Main Elements
- Sets `PACKAGE=runtime`.
- Installs `minfree` under `/var/crash` with mode `0750`.
- Builds `PROG=savecore` and `savecore.8`.
- Links `libxo`, `zlib`, and `zstd`.
- Adds zstd include path from the kernel contrib tree.
- Conditionally enables Casper/fileargs/syslog support.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses `bsd.prog.mk`, `src.opts.mk`, libxo, compression libraries, and optional Casper capability libraries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/savecore.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/savecore/savecore.c

## Summary
Implements `savecore`, the crash-dump saver/checker/clearer and live-kernel-dump capture utility. It validates kernel dump headers, copies or decompresses dumps into a crash directory, manages bounds and symlinks, preserves encrypted dump keys, checks free space, and runs in Capsicum capability mode.

## Main Responsibilities
- Parses modes for checking dumps, clearing dumps, saving dumps, preserving headers, forcing bad dumps, live dumps, max dump rotation, verbosity, compression, and decompression.
- Enumerates dump devices from `fstab` swap/dump entries or explicit device arguments.
- Reads and validates first/last kernel dump headers, magic values, versions, parity, and compression metadata.
- Handles regular dumps, compressed dumps, encrypted dumps with key files, text dumps written backward, and live dumps via `MEM_KERNELDUMP`.
- Writes `info.N` metadata using libxo and optionally prints headers to stdout.
- Maintains `bounds`, `*.last` symlinks, and cleanup of existing dump files for reused bounds.
- Checks available crash-directory space against `minfree`.
- Uses sparse writes for uncompressed dump data.
- Supports gzip and zstd decompression of kernel-compressed dumps.
- Enters Capsicum mode with limited directory and device capabilities.

## Key Elements
- `DoFile()`: main dump-device path for normal crash dumps.
- `DoLiveFile()`: invokes live dump creation through `/dev/mem`, validates header, truncates trailing header, and renames the temporary file.
- `DoRegularFile()` / `DoTextdumpFile()`: copy/decompress/sparsify dump payloads.
- `GunzipWrite()` / `ZstdWrite()`: streaming decompression into sparse output.
- `check_space()`: enforces crash-directory free-space policy.
- `write_header_info()`, `printheader()`: libxo dump metadata output.
- `init_caps()`: Casper/fileargs/syslog setup and capability-mode transition.

## Dependencies And Integration
Uses kernel dump ABI headers, disk ioctls, `/etc/fstab`, `/var/crash` files, libxo, zlib, zstd, Casper `fileargs`, Casper syslog, and Capsicum helpers.

## Research Notes
The code treats dump validity and dump preservation separately: bad headers/parity normally stop saving, but `-f` can force some cases; `-k` preserves the dump header, while the default clears it after processing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/savecore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/Makefile

## Summary
Registers the `savecore` ATF shell tests.

## Main Elements
- Sets `ATF_TESTS_SH=livedump_test log_test`.
- Marks `livedump_test` exclusive because loading kernel modules during the test can change live-dump state.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Integrates with FreeBSD ATF/Kyua test infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/livedump_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/livedump_test.sh

## Summary
ATF shell test validating live dump integrity by comparing module-list output from the generated live core with the running system.

## Main Elements
- Requires root and `kgdb`.
- Runs `savecore -L .` and expects live-dump logging on stderr.
- Skips when debug symbols for the running kernel are unavailable.
- Creates a small gdb script that walks `linker_files`.
- Runs `kgdb` against `livecore.0`, filters gdb prompt noise, and compares output with `kldstat`.

## Dependencies And Integration
Uses `savecore`, `sysctl kern.bootfile`, `/usr/lib/debug`, `kgdb`, `kldstat`, `sed`, `diff`, and ATF helpers.

## Research Notes
The test is sensitive to concurrent kernel module loads, which is why the Makefile marks it exclusive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/livedump_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/log_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/log_test.sh

## Summary
ATF shell test for `savecore` stderr/syslog mirroring behavior under `LOG_PERROR`.

## Main Elements
- Runs `savecore -vC /dev/missing` expecting exit status 1.
- Saves stderr to `savecore.err`.
- Verifies stderr contains a syslog-style missing-device error for `/dev/missing`.

## Dependencies And Integration
Uses ATF shell helpers and `grep -qE`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/savecore/tests/log_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/Makefile

## Summary
Builds the `setkey` IPsec PF_KEY utility, including its yacc parser, lex scanner, and embedded libipsec/PF_KEY support sources.

## Main Elements
- Builds `PROG=setkey` and `setkey.8`.
- Compiles `setkey.c`, `parse.y`, and `token.l`.
- Reuses `pfkey.c`, `pfkey_dump.c`, `key_debug.c`, and `ipsec_strerror.c`.
- Generates `y.tab.h` from `parse.y`.
- Enables `IPSEC_DEBUG` and `YY_NO_UNPUT`.
- Conditionally defines `INET` and `INET6`.
- Links `libipsec`.
- Has a disabled `scriptdump` script target generated from `scriptdump.pl`.

## Dependencies And Integration
Uses FreeBSD build options, yacc/lex integration, `lib/libipsec`, and `sys/netipsec` headers/sources.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/parse.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/parse.y

## Summary
Yacc grammar and PF_KEY message builder for `setkey` script input. It parses SAD commands, SPD commands, algorithms, keys, lifetimes, NAT-T options, ESN, hardware offload interface options, address-family flags, ports, and policies.

## Main Responsibilities
- Parses `add`, `delete`, `deleteall`, `get`, `flush`, and `dump` SAD commands.
- Parses `spdadd`, `spddelete`, `spddump`, and `spdflush` SPD commands.
- Parses AH, ESP, IPCOMP, TCP MD5, old AH/ESP syntax, and algorithm/key forms.
- Validates key lengths through `ipsec_check_keylen()`.
- Converts hex and quoted key strings into binary buffers.
- Parses lifetimes, replay windows, reqid, mode, NAT-T endpoints/ports/fragment size, ESN, and hardware offload interface names.
- Parses SPD policy strings through `ipsec_set_policy()`.
- Builds PF_KEY `sadb_msg` buffers with SA, SA2, key, lifetime, address, NAT-T, replay, policy, and hardware-offload extensions.

## Key Elements
- `setkeymsg0()`: initializes base PF_KEY message header.
- `setkeymsg_add()`: builds SADB_ADD messages for source/destination combinations.
- `setkeymsg_addr()`: builds GET/DELETE/DELETEALL messages.
- `setkeymsg_spdaddr()`: builds SPD messages with policy and address extensions.
- `parse_addr()`: resolves addresses with parser-selected family and flags.
- `fix_portstr()`: splits ICMPv6 upper-layer port/type-code syntax.
- `parse_init()`: resets global parser state between commands.

## Dependencies And Integration
Uses PF_KEY v2 structures, FreeBSD netipsec headers, `libpfkey`, `libipsec`, resolver APIs, and tokens supplied by `token.l`.

## Research Notes
The message builders use fixed `BUFSIZ` stack buffers and retain historical comments warning that they do not perform buffer-overrun checks. This is important when analyzing parser robustness.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/scriptdump.pl -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/scriptdump.pl

## Summary
Perl helper that converts `setkey -D` SAD dump output back into `setkey` add/delete script commands.

## Main Elements
- Requires root by checking effective UID.
- Accepts optional `-d` to emit `delete` commands instead of `add`.
- Reads `setkey -D` output from a pipe.
- Captures source/destination, protocol, mode, SPI, reqid, replay, encryption algorithm/key, and authentication algorithm/key.
- Emits semicolon-terminated setkey commands.

## Dependencies And Integration
Depends on stable text formatting from `setkey -D`; intended to be generated with the configured local Perl prefix.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/scriptdump.pl -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/setkey.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/setkey.c

## Summary
Main command-line driver for `setkey`. It opens PF_KEY, loads the IPsec module if needed, dispatches script/dump/flush/promiscuous modes, sends PF_KEY messages, receives replies, and formats SAD/SPD output.

## Main Responsibilities
- Parses command modes: script from stdin/file/string, SAD/SPD dump, SAD/SPD flush, and PF_KEY promiscuous monitor.
- Supports flags for all entries, looping dump, hex dump, policy mode, global/interface policy scope, verbose debug output, and receive-timeout control.
- Loads `ipsec` kernel module when absent.
- Registers supported algorithms before parsing scripts.
- Sends PF_KEY messages and post-processes replies.
- Dumps SAD entries, SPD entries, and short looped SAD summaries.
- Filters dead SAs from normal dumps unless `-a` is used.
- Prints timestamps for promiscuous PF_KEY monitoring.

## Key Elements
- `main()`: option parsing and mode dispatch.
- `sendkeyshort()`: minimal PF_KEY command sender for dump/flush.
- `sendkeymsg()`: common send/receive loop with optional verbose and hex output.
- `postproc()`: formats errors and dump/get replies.
- `promisc()`: subscribes to PF_KEY promiscuous messages.
- `shortdump()` / `shortdump_hdr()`: compact SAD monitoring output.
- `gmt2local()` / `printdate()`: timestamp support.

## Dependencies And Integration
Uses `libpfkey`, netipsec headers, `parse()` from `token.l`/`parse.y`, kernel module loading APIs, and PF_KEY raw sockets.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/setkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/test-pfkey.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/test-pfkey.c

## Summary
Standalone PF_KEY message construction test utility. It builds canned PF_KEY messages for selected message types, sends them to the kernel, and dumps both outgoing and returned messages.

## Main Elements
- Takes a numeric PF_KEY message type.
- Opens a raw PF_KEY v2 socket.
- Builds message buffers in global `m_buf`.
- Provides helpers for SADB message headers, SA, addresses, keys, lifetimes, SPI ranges, identities, sensitivity, and proposals.
- Exercises SAD operations and some SPD operation message forms.
- Uses hard-coded IPv4/IPv6 addresses, SPI, keys, algorithms, and identities.

## Dependencies And Integration
Uses PF_KEY/netipsec structures and `pfkey_sadump()` debug formatting. This is a developer diagnostic program, not part of the normal `setkey` build target.

## Research Notes
The file uses old-style K&R function definitions and fixed global buffers, reflecting its role as a historical/manual PF_KEY exerciser.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/test-pfkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/test-policy.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/test-policy.c

## Summary
Standalone test program for libipsec policy parsing and socket IPsec policy set/get behavior.

## Main Elements
- Defines a list of valid and intentionally invalid policy request strings.
- Converts each request through `ipsec_get_policylen()` and `ipsec_set_policy()`.
- Applies generated policies to IPv4 and IPv6 datagram sockets with `setsockopt()`.
- Reads policies back with `getsockopt()`.
- Dumps returned policies using `ipsec_dump_policy()`.

## Dependencies And Integration
Uses `libipsec`, PF_KEY policy length macros, IPv4/IPv6 IPsec socket options, and direct sockets.

## Research Notes
The tests include malformed policy strings and a very long policy request to exercise parser error handling and policy buffer behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/test-policy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/token.l -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/token.l

## Summary
Lex scanner for `setkey` script syntax. It tokenizes commands, algorithms, protocols, options, address/prefix/port syntax, quoted/hex/decimal/string values, and SPD policy strings.

## Main Elements
- Tracks line numbers for parser diagnostics.
- Defines scanner states for policy strings, authentication algorithms, and encryption algorithms.
- Recognizes SAD commands and SPD commands.
- Recognizes AH/ESP/IPCOMP/TCP protocol names including old AH/ESP forms.
- Maps authentication algorithms such as HMAC-SHA variants, AES-XCBC-MAC, TCP-MD5, CHACHA20-POLY1305, and null.
- Maps encryption algorithms such as null, AES-CBC, AES-CTR, AES-GCM-16, and CHACHA20-POLY1305.
- Recognizes compression algorithms, replay/lifetime/NAT-T/ESN/hardware-interface options, address flags, prefixes, and ports.
- Provides `yyerror()`, `yyfatal()`, and `parse()` entry points.

## Dependencies And Integration
Includes `vchar.h` and generated `y.tab.h`, and supplies tokens consumed by `parse.y`.

## Research Notes
Policy scanning intentionally permits whitespace and newlines inside policy bodies until `;`, incrementing `lineno` for embedded newlines.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/token.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/vchar.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/setkey/vchar.h

## Summary
Small shared value-buffer type for the `setkey` lexer/parser.

## Main Elements
- Defines `vchar_t` with `u_int len` and `caddr_t buf`.
- Used for parsed strings, keys, policy buffers, port strings, address flags, and hardware-interface names.

## Dependencies And Integration
Included by `parse.y` and `token.l`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/setkey/vchar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/shutdown/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/shutdown/Makefile

## Summary
Builds the `shutdown` runtime utility and installs `poweroff` as a hardlink/alias.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=shutdown` and `shutdown.8`.
- Links `${BINDIR}/poweroff` to `shutdown`.
- Adds manual alias `shutdown.8 poweroff.8`.
- Installs as root/operator with mode `4554`.

## Dependencies And Integration
Uses `bsd.prog.mk`; install mode supports privileged shutdown behavior for operator-group users.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/shutdown/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/shutdown/shutdown.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/shutdown/shutdown.c

## Summary
Implements the FreeBSD `shutdown` and `poweroff` command. It parses shutdown time and mode, broadcasts warnings, creates/removes the no-login file, logs the action, and signals init or execs halt/reboot paths.

## Main Responsibilities
- Requires effective root outside `DEBUG`.
- Treats invocation as `poweroff` as `shutdown -p now`.
- Parses shutdown modes: single-user, reboot, halt, poweroff, power-cycle, fake shutdown, fast exec path, no-sync fast path, quiet warning suppression, and ignore-noshutdown.
- Parses time formats: `now`, `+N` with seconds/minutes/hours suffixes, `hhmm`, `hh:mm`, `ddhhmm`, `mmddhhmm`, and `yymmddhhmm`.
- Builds optional warning messages from argv or stdin.
- Refuses shutdown when `_PATH_NOSHUTDOWN` exists unless forced.
- Forks into background, raises priority, starts a new session, and uses syslog.
- Broadcasts warning messages through `wall -n`.
- Creates `_PATH_NOLOGIN` during the final five minutes.
- Signals init for normal shutdown paths or execs `reboot`/`halt` for `-o`.

## Key Elements
- `getoffset()`: shutdown time parser.
- `loop()`: warning/sleep schedule.
- `timewarn()`: `wall` broadcast writer with restricted environment.
- `nolog()`: writes no-login file with shutdown time and message.
- `finish()`: cleanup on termination.
- Final action routine: logs and triggers init signals or fast halt/reboot executables.

## Dependencies And Integration
Uses init signal conventions, `/etc/nologin` path macros, `wall`, `halt`, `reboot`, syslog, boottrace, passwd lookup, and standard daemonization primitives.

## Research Notes
The `-o -n` path bypasses init and can pass no-sync to `halt`/`reboot`; argument validation prevents `-n` without `-o` and requires `-o` to be paired with a terminal power/reboot mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/shutdown/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/swapon/Makefile

## Summary
Builds the `swapon` runtime utility and installs `swapoff` and `swapctl` aliases.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=swapon` and `swapon.8`.
- Adds links for `swapoff` and `swapctl`.
- Adds manual aliases for `swapoff.8` and `swapctl.8`.
- Links `libutil`.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`, `src.opts.mk`, and libutil.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/swapon.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/swapon/swapon.c

## Summary
Implements `swapon`, `swapoff`, and `swapctl`. It activates/deactivates swap devices or files, processes fstab entries, supports md-backed and GELI-encrypted swap setup, optionally trims devices before activation, and lists swap usage through sysctl.

## Main Responsibilities
- Selects behavior from invocation name or `swapctl` options.
- Supports all-fstab activation/deactivation, late swap filtering, quiet mode, forced swapoff, alternate fstab, and human/block-size listing.
- Parses fstab swap entries while skipping `noauto` and honoring `late`.
- Handles plain special files with `swapon()`/`swapoff()`.
- Handles GELI `.eli` devices by running `geli onetime` before activation.
- Handles md-backed swap with `file=` fstab options by running `mdconfig` attach/list/detach.
- Supports md device forms such as `md`, `/dev/md`, `mdN`, `/dev/mdN`, and `.eli` variants.
- Builds GELI arguments from fstab options: `aalgo`, `ealgo`, `keylen`, `sectorsize`, `notrim`, and `trimonce`.
- Implements one-time trim with `DIOCGDELETE` before `swapon()`.
- Lists swap devices and totals using `vm.swap_info` sysctl entries.

## Key Elements
- `swap_on_off()`: dispatches md, GELI, or plain special-file handling.
- `swap_on_off_md()`: creates/finds/destroys vnode-backed md devices around swap activation/deactivation.
- `swap_on_off_geli()` and `swap_on_geli_args()`: one-time encryption setup.
- `run_cmd()`: fork/exec helper for `mdconfig` and `geli`, with optional stdout pipe.
- `swapon_trim()`: trims data area while keeping the device open through swap activation.
- `swaplist()`: implements `swapctl -l/-s` listing.
- `sizetobuf()`: block-size and human-readable formatting helper.

## Dependencies And Integration
Uses `fstab`, `mdconfig`, `geli`, `swapon(2)`, `swapoff(2)`, disk ioctls, `vm.swap_info`, `devname()`, and libutil formatting helpers.

## Research Notes
`run_cmd()` constructs command strings then splits only on spaces, so helper arguments containing spaces are not shell-quoted. The current callers mostly pass device paths and option fragments expected not to contain spaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/swapon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/swapon/tests/Makefile

## Summary
Registers the `swapon_test` ATF shell test.

## Main Elements
- Sets `ATF_TESTS_SH=swapon_test`.
- Marks the test as requiring root.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Root is required because the tests create md devices and activate/deactivate swap.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/tests/swapon_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/swapon/tests/swapon_test.sh

## Summary
ATF shell tests for `swapon` fstab-driven md-backed swap handling, including explicit and automatic md units and GELI-encrypted variants.

## Main Elements
- Creates swapfiles at least two kernel pages for successful attach cases.
- Tests `mdN`, `/dev/mdN`, `md`, and `/dev/md` fstab forms.
- Tests `mdN.eli`, `/dev/mdN.eli`, `md.eli`, and `/dev/md.eli` encrypted forms.
- Uses alternate fstab files with `sw,file=swapfile`.
- Verifies expected `swapon` output for fixed and dynamically allocated md units.
- Cleans up each successful case with `swapoff -F fstab.out -a`.
- Tests too-small swapfile rejection and manually detaches the md unit after failure.

## Dependencies And Integration
Uses ATF shell, `sysctl hw.pagesize`, `truncate`, `swapon`, `swapoff`, and `mdconfig`. Requires root.

## Research Notes
The tests specifically cover name parsing paths added for md-backed fstab swap entries, including both `/dev/`-prefixed and unprefixed names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/swapon/tests/swapon_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/Makefile

## Summary
Builds the `sysctl` runtime utility and installs the default `sysctl.conf` configuration file.

## Main Elements
- Includes `src.opts.mk`.
- Sets `PACKAGE=runtime`.
- Installs `CONFS=sysctl.conf`.
- Builds `PROG=sysctl`, warning level 3, and `sysctl.8`.
- Conditionally enables jail support when `MK_JAIL` is on and not building rescue.
- Links `libjail` when jail support is enabled.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`; optionally integrates with jail APIs via `-DJAIL` and `libjail`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/sysctl/Makefile -->