# Group Research: group_372_freebsd_src_sources_os_bsd_freebsd_src_sbin_init_init_c_sources_os_b_c6ce66f1a0e5

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/init.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/init/init.c

## Purpose
Implements FreeBSD `init(8)`, PID 1. It is the system bootstrap and lifecycle state machine: single-user mode, `/etc/rc`, multi-user getty supervision, shutdown, reboot, and reroot.

## Main Elements
- `main()` validates root/PID 1, handles SysV-compatible runlevel signals when enabled, parses `-d`, `-s`, `-f`, `-r`, installs signal handlers, closes standard fds, processes `kenv` overrides, optionally mounts `devfs`, and starts the state machine.
- State functions: `single_user`, `runcom`, `read_ttys`, `multi_user`, `clean_ttys`, `catatonia`, `death`, `death_single`, `reroot`, and `reroot_phase_two`.
- Signal-driven transitions map `SIGHUP`, `SIGINT`, `SIGEMT`, `SIGTERM`, `SIGTSTP`, `SIGUSR1`, `SIGUSR2`, and `SIGWINCH` to rescans, single-user, reroot, halt, reboot, poweroff, or login blocking.
- `/etc/ttys` processing builds `session_t` records, parses getty/window command arguments, starts gettys, restarts dead sessions, and removes changed/deleted sessions.
- Shutdown paths revoke ttys, run `/etc/rc.shutdown`, kill remaining processes with `SIGTERM`/`SIGKILL`, optionally run `/etc/rc.final`, sync, and call `reboot()`.
- Reroot copies the running init binary to tmpfs at `/dev/reroot/init`, execs that temporary init with `-r`, asks the kernel to mount the new root with `RB_REROOT`, then searches the new root for init.

## Dependencies And Integration
Uses FreeBSD kernel sysctls, `kenv`, boot/shutdown tracing, `nmount`, `reboot`, `libutil` login tty helpers, DB hash storage for pid-to-session lookup, `/etc/ttys`, `/etc/rc`, `/etc/rc.shutdown`, `/etc/rc.final`, and paths from `pathnames.h`.

## Risk Notes
This is critical PID 1 code. Errors can prevent boot, leave no login sessions, or interrupt shutdown. Reroot and shutdown are especially sensitive because they kill processes, revoke terminals, mount/unmount filesystems, and exec replacement init binaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/init/pathnames.h

## Purpose
Defines fixed path constants used by `init(8)`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_INITLOG`, `_PATH_SLOGGER`, `_PATH_RUNCOM`, `_PATH_RUNDOWN`, `_PATH_RUNFINAL`, `_PATH_REROOT`, and `_PATH_REROOT_INIT`.

## Dependencies And Integration
Consumed by `init.c` for fallback logging, startup and shutdown scripts, final shutdown script, and the temporary reroot init location.

## Risk Notes
Changing these paths changes boot, shutdown, and reroot behavior system-wide.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/init/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/Makefile

## Purpose
Top-level build orchestration for FreeBSD `sbin/ipf`.

## Main Elements
- Includes `src.opts.mk`.
- Builds `libipf` first, then `ipf`, `ipfstat`, `ipmon`, `ipnat`, and `ippool`.
- Adds `ipfs` only when `MK_IPFILTER_IPFS != "no"`.
- Leaves `ipftest`, `ipresend`, and `ipsend` temporarily disconnected.
- Enables subdirectory parallelism.

## Dependencies And Integration
Integrates the IPFilter userland programs with the FreeBSD build option framework.

## Risk Notes
Build membership is controlled here; disabling or omitting a subdir silently removes an IPFilter utility from the base build.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/Makefile.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/Makefile.inc

## Purpose
Shared makefile fragment for IPFilter programs.

## Main Elements
- Sets warning level and disables format-warning promotion.
- Adds include paths for kernel headers, IPFilter kernel headers, and common IPF userland headers.
- Defines `STATETOP` and `__UIO_EXPOSE`.
- Defines `USE_INET6` or `NOINET6` based on `MK_INET6_SUPPORT`.
- Links non-`libipf` programs with `libipf`.
- Adds yacc-generated cleanup files and shared `.PATH` entries.
- Includes parent `../Makefile.inc`.

## Dependencies And Integration
Centralizes common compiler flags and generated-file cleanup for `sbin/ipf` subprograms.

## Risk Notes
The IPv6 build knob changes parser and address-handling behavior across the whole IPFilter toolset.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/genmask.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/genmask.c

## Purpose
Converts textual IPv4/IPv6 mask specifications into `i6addr_t` mask storage.

## Main Elements
- `genmask()` accepts a protocol family, mask string, and output address union.
- Parses dotted/hex/colon forms as literal IPv4 or IPv6 addresses.
- Parses numeric prefix lengths for IPv4 `/0` through `/32` and IPv6 `/0` through `/128`.
- Uses `inet_aton`, `inet_pton`, `fill6bits`, and network-byte-order IPv4 mask construction.

## Dependencies And Integration
Shared by IPFilter parsing/helpers via `ipf.h`.

## Risk Notes
Family mismatches or malformed masks return `-1`. IPv6 support depends on `USE_INET6`, but the numeric IPv6 case is still present in the switch.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/genmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf.h

## Purpose
Central userland IPFilter header for shared types, compatibility includes, global variables, and function declarations.

## Main Elements
- Pulls in system socket/IP headers plus IPFilter kernel/user structures such as `ip_fil`, `ip_nat`, `ip_state`, `ip_pool`, `ip_htable`, `ip_dstlist`, and related headers.
- Defines compatibility typedefs and utility macros.
- Defines shared parser/helper structs: `ipopt_names`, `alist_t`, `plist_t`, `fakebpf_t`, `icmptype_t`, `wordtab_t`, `namelist_t`, and `proxyrule_t`.
- Declares common callback types for ioctl, add-rule, and copy operations.
- Exposes parser globals such as `use_inet6`, `lineNum`, and `debuglevel`.
- Declares many shared helper APIs for address parsing, rule parsing, NAT parsing, pool/hash loading, printing, error reporting, lexer variables, debugging, and state/NAT formatting.

## Dependencies And Integration
Included by most IPFilter userland tools and generated parser/lexer sources. It bridges userland utilities to the kernel IPFilter ABI.

## Risk Notes
This header is a broad coupling point. ABI or structure changes in the kernel IPFilter headers can ripple through nearly every IPFilter userland program.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf_y.y

## Purpose
Yacc grammar and semantic actions for parsing IPFilter rule files and applying parsed rules.

## Main Elements
- Defines tokens and grammar for `ipf.conf` syntax: `pass`, `block`, `count`, `auth`, `preauth`, `call`, `skip`, `log`, `quick`, `on`, `dup-to`, `route-to`, `reply-to`, `from`, `to`, `with`, `keep state`, `keep frags`, tags, pools, hashes, BPF, expressions, IPv4/IPv6 options, ICMP types/codes, syslog levels, and tunables.
- Maintains parser state in globals such as `fr`, `frc`, `frtop`, `frold`, `ipffd`, `ipfioctls`, and `ipfaddfunc`.
- Expands list syntax into multiple `frentry_t` rules with `addrule()`.
- Builds normal IPF match data, BPF opcode match data, and expression match data.
- Supports inline anonymous pools/hashes by loading them through lookup ioctls.
- Adds/removes/zeros rules through `ipf_addrule()` and ioctl commands selected from global `opts`.
- Provides keyword dictionaries used by the hand-written lexer.

## Dependencies And Integration
Generated into `ipf_y.c` by `ipf/ipf/Makefile`; paired with the transformed lexer as `ipf_l.c`. Used by `ipf_parsefile()` / `ipf_parsesome()` from the `ipf` command and shared `libipf` paths.

## Risk Notes
The semantic actions directly allocate, clone, mutate, and submit kernel ABI structures. Parser-state globals make the code sensitive to reentrancy assumptions. `do_tuneint()` appears to overwrite its `name=value` buffer with only the numeric value before calling `ipf_dotuning()`, which is a notable maintenance risk.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipmon.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipmon.h

## Purpose
Defines shared structures and flags for IPFilter log monitoring configuration/actions.

## Main Elements
- `ipmon_msg_t` describes a log message plus payload, timestamp, and log level.
- `ipmon_saver_t` defines pluggable storage/output callbacks.
- `ipmon_saver_int_t` and `ipmon_doing_t` link configured saver instances.
- `ipmon_action_t` represents match criteria and actions for log events.
- Defines match flags such as direction, src/dst IP, ports, group, interface, result, type, and log tag.
- Defines runtime flags for syslog, resolving, hex output, tail mode, verbosity, NAT/state/filter logging, and port-number display.
- Declares configuration and action helper functions.

## Dependencies And Integration
Used by `ipmon` parser and runtime code to match log events and route them to configured outputs.

## Risk Notes
The structure mixes matching state, rate counters, and action lists; changes must stay aligned with `ipmon` parser/runtime expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipt.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipt.h

## Purpose
Defines a packet-reader abstraction used by IPFilter testing/replay style code.

## Main Elements
- Declares `struct ipread` with callbacks for open, close, and reading an IP packet into an `mb_t`.
- Defines `R_DO_CKSUM` reader flag.
- Includes `<fcntl.h>` and compatibility `__P` handling.

## Dependencies And Integration
Provides a common interface for packet input modules that feed IPFilter-like processing.

## Risk Notes
The callback API depends on `mb_t` being defined by included IPFilter compatibility headers before use.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/ipt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/kmem.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/kmem.h

## Purpose
Declares helpers for reading kernel memory from IPFilter userland utilities.

## Main Elements
- Declares `openkmem`, `kmemcpy`, and `kstrncpy`.
- Defines `KMEM` as `_PATH_KMEM` when available, otherwise `/dev/kmem`.
- Includes `<paths.h>` for NetBSD/OpenBSD variants.

## Dependencies And Integration
Used by legacy/stat-style IPFilter tooling that reads kernel structures directly.

## Risk Notes
Direct kernel-memory reads are platform-sensitive and privileged. Modern FreeBSD paths may prefer ioctl-based interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/kmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.c

## Purpose
Hand-written lexer used by IPFilter yacc parsers.

## Main Elements
- `yylex()` tokenizes comments, whitespace, continuations, variable references, quoted strings, numbers, hex numbers, comparison/range operators, punctuation, identifiers, and IPv6 addresses.
- Supports dictionary-driven keyword lookup with `yysettab`, `yysetdict`, `yysetfixeddict`, and `yyresetdict`.
- Expands variables via `get_variable()`.
- Tracks parser context through globals such as `yyexpectaddr`, `yybreakondot`, and `yyvarnext`.
- Converts token text into `yylval` for numbers, hex values, strings, and IPv6 addresses.
- `yyerror()` reports the current token and line before exiting.
- Optional `TEST_LEXER` main prints token streams.

## Dependencies And Integration
The `ipf` Makefile transforms this source by renaming `yy` symbols to `ipf_yy` and switching generated header names. It depends on `ipf.h`, `lexer.h`, and yacc token definitions.

## Risk Notes
Global mutable lexer state and fixed-size token buffers make parser behavior sensitive to reset paths. `YYBUFSIZ` protects against overly long tokens by returning `TOOLONG`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.h

## Purpose
Declares lexer token constants and public lexer state/functions.

## Main Elements
- Defines fallback token IDs under `NO_YACC`.
- Defines `YYBUFSIZ` as 8192.
- Declares dictionary management functions, `yylex`, `yyerror`, `yykeytostr`, and `yyresetdict`.
- Exposes `yyin`, `yylineNum`, `yyexpectaddr`, `yybreakondot`, and `yyvarnext`.

## Dependencies And Integration
Included by `lexer.c` and transformed into parser-specific lexer headers such as `ipf_l.h`.

## Risk Notes
The exposed globals are part of parser control flow; callers must reset them correctly between parse sessions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/lexer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/opts.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/opts.h

## Purpose
Defines shared IPFilter command option bit flags and small portability helpers.

## Main Elements
- Detects Solaris builds.
- Defines `OPT_*` flags for remove, debug, raw, log, show/list, verbose, dry-run, counters, line numbers, queues, inactive list, NAT/state views, flush/clear, hex/ascii, no-resolve, purge, and related modes.
- Aliases `OPT_STAT` and `OPT_LIST`.
- Defines `STRERROR()` compatibility.
- Declares global `opts`.

## Dependencies And Integration
Included by `ipf.h`, then shared by many IPFilter utilities and parser actions.

## Risk Notes
`opts` is a process-global behavior switch; conflicting option bits can materially change ioctl targets and side effects.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/opts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/pcap-ipf.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/pcap-ipf.h

## Purpose
Minimal pcap file header definitions used without including full libpcap/BPF headers.

## Main Elements
- Defines `pcaphdr_t` matching pcap file headers.
- Defines `TCPDUMP_MAGIC` and `PCAP_VERSION_MAJ`.
- Defines `pcappkt_t` for per-packet timestamp and lengths.

## Dependencies And Integration
Included by local BPF-related code that needs pcap structures without normal pcap headers.

## Risk Notes
This is a local structural copy; compatibility depends on staying aligned with pcap version 2 layout assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/common/pcap-ipf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/Makefile

## Purpose
Builds the `ipf` command.

## Main Elements
- Sets `PACKAGE=ipf`, `PROG=ipf`, manuals, and manpage links.
- Builds `ipf.c`, `ipfcomp.c`, generated `ipf_y.c`, generated `ipf_l.c`, and `bpf_filter.c`.
- Enables `IPFILTER_BPF` and `HAS_SYS_MD5_H`.
- Generates parser and lexer sources by running yacc and rewriting `yy` symbols to `ipf_yy`.
- Links `libpcap` outside rescue builds.

## Dependencies And Integration
Connects common parser/lexer sources to the `ipf` utility with renamed yacc/lex symbols to avoid collisions.

## Risk Notes
The sed-based symbol rewrite is simple but broad; generated parser/lexer naming depends on these substitutions staying valid.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf-ipf.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf-ipf.h

## Purpose
Local BPF compatibility header for IPFilter.

## Main Elements
- Defines BPF version, alignment, buffer limits, ioctls, `bpf_program`, `bpf_stat`, `bpf_version`, and `bpf_hdr` when system BPF definitions are absent.
- Defines many `DLT_*` link-layer type constants.
- Defines BPF instruction classes, modes, ALU/JMP operations, source/rval helpers, `struct bpf_insn`, and initializer macros.
- Declares `bpf_validate()` and `bpf_filter()`.

## Dependencies And Integration
Used by `bpf_filter.c` and the IPF BPF rule parser path to provide a stable BPF instruction ABI independent of host headers.

## Risk Notes
Local BPF copies can diverge from platform BPF/libpcap definitions. The header is guarded by `BPF_MAJOR_VERSION` to avoid duplicate definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf-ipf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf_filter.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf_filter.c

## Purpose
Implements a classic BPF interpreter and validator for IPFilter BPF rules.

## Main Elements
- `bpf_filter()` executes BPF instructions over a flat packet buffer or an mbuf chain when `buflen == 0`.
- Supports absolute/indirect loads, length loads, immediate loads, scratch memory, jumps, ALU operations, and return instructions.
- `m_xword()` and `m_xhalf()` read words/halves across mbuf boundaries.
- Handles strict-alignment platforms with bytewise extract macros.
- `bpf_validate()` checks program length, memory indexes, jump targets, constant division by zero, and ensures the last instruction is `RET`.

## Dependencies And Integration
Used by the `ipf` command when compiling or validating BPF filter expressions. Includes local `bpf-ipf.h` and `pcap-ipf.h`.

## Risk Notes
The validator has a suspicious fallthrough in the `BPF_ALU` `BPF_DIV` case that can reject division instructions even when not division by zero. Runtime packet bounds checks are essential for safe interpreter behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/bpf_filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipf.c

## Purpose
Main command-line utility for controlling IPFilter filter rules and global filter state.

## Main Elements
- Parses options for IPv4/IPv6 mode, active/inactive list selection, debug, dry-run, load file, flush, packet logging, expression flush matching, auth device, remove mode, swap active lists, tuning, verbosity, version, sync, zero rule stats, and zero global stats.
- `procfile()` opens the device, initializes parser state, and loads rules through `ipf_parsefile()`.
- `ipf_interceptadd()` optionally emits compiled C then submits rules with `ipf_addrule()`.
- `flushfilter()` flushes filter rules or state entries, optionally by parsed expression.
- `packetlogon()` toggles pass/block/nomatch filter log flags and NAT/state logging.
- `showversion()` prints user/kernel version, running status, flags, default policy, active list, and feature mask.
- `zerostats()` clears and prints filter statistics.

## Dependencies And Integration
Uses `/dev/ipl`-style device names from IPFilter headers, parser helpers from common code, and many IPFilter ioctls such as `SIOCFRENB`, `SIOCIPFFL`, `SIOCSWAPA`, `SIOCFRSYN`, `SIOCFRZST`, and `SIOCGETFS`.

## Risk Notes
Most operations mutate live firewall state. Dry-run mode avoids device opens, but option combinations strongly affect whether rules are added, removed, inserted, flushed, or just printed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipfcomp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipfcomp.c

## Purpose
Generates C source/header output for compiled IPFilter rule sets.

## Main Elements
- `printc()` writes `ip_rules.c` rule data for eligible IPv4 normal IPF rules.
- Groups rules by group name and input/output direction.
- Emits serialized `frentry_t` data and optional rule data blocks.
- `printC()`, `printCgroup()`, and `emitGroup()` generate matcher functions with nested comparisons for interface, version, flags, protocol, TTL, TOS, TCP flags, ports, source/destination addresses, options, security, auth, and ICMP fields.
- Orders comparisons based on commonality across following rules using `mc_t` metrics.
- `printhooks()` emits add/remove helper functions that register compiled matchers with IPFilter via `frrequest()`.
- `emittail()` emits aggregate `ipfrule_add()` and `ipfrule_remove()` functions.

## Dependencies And Integration
Called from `ipf.c` when `-cc` output mode is selected. Produces `ip_rules.c` and `ip_rules.h` for kernel compiled-rule integration under `IPFILTER_COMPILED`.

## Risk Notes
Only a subset of rules is eligible: IPv6, non-IPF, BPF/expression, and lookup-address forms are skipped. Generated header text contains suspicious doubled closing parentheses in some prototypes, so this path needs careful build verification.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipfcomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/Makefile

## Purpose
Builds the `ipfs` utility.

## Main Elements
- Sets `PACKAGE=ipf`.
- Builds `PROG=ipfs`.
- Installs `ipfs.8`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Relies on default single-source program rules for `ipfs.c` plus shared IPFilter make settings from parent includes.

## Risk Notes
No special libraries or sources are declared here; behavior is concentrated in `ipfs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/ipfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/ipfs.c

## Purpose
Saves, restores, locks, unlocks, and edits IPFilter NAT/state table snapshots.

## Main Elements
- Command modes include lock/unlock, save/read all, save/read NAT only, save/read state only, dry-run, verbose, directory selection, file selection, and interface-name replacement.
- `changestateif()` and `changenatif()` rewrite saved interface names in state/NAT snapshot files.
- `setlock()` uses `SIOCSTLCK` to lock or unlock IPFilter state during save/restore.
- `writestate()` iterates live state entries with `SIOCSTGET` and writes fixed-size `ipstate_save_t` records.
- `readstate()` reads state records, tracks shared rule pointers, marks first rule references with `SI_NEWFR`, and restores entries with `SIOCSTPUT`.
- `writenat()` obtains NAT save-record sizes with `SIOCSTGSZ`, fetches entries with `SIOCSTGET`, and writes variable-size NAT records.
- `readnat()` reads variable-size NAT records, remaps shared rule references, and restores entries through `SIOCSTPUT`.
- `writeall()` and `readall()` operate in `/var/db/ipf` by default and lock IPFilter while saving/restoring state and NAT files.

## Dependencies And Integration
Uses IPFilter device nodes (`IPL_NAME`, `IPSTATE_NAME`, `IPNAT_NAME`), save ABI structures, and state/NAT ioctls. Default files are `ipstate.ipf` and `ipnat.ipf` under `/var/db/ipf`.

## Risk Notes
Snapshot files contain kernel pointer values that must be remapped during restore. Partial reads, variable-size NAT records, and lock/unlock error paths are important correctness risks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/ipfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/Makefile

## Purpose
Builds the `ipfstat` utility.

## Main Elements
- Defines `NOGCCERROR`.
- Sets `PACKAGE=ipf`, `PROG=ipfstat`, source `ipfstat.c`, and manual `ipfstat.8`.
- Links with `tinfow` and `ncursesw`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
The curses libraries support interactive/stat display modes in `ipfstat`.

## Risk Notes
Build depends on wide-character curses and terminfo libraries being available in the target build environment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/Makefile -->