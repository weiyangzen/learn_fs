# subset-b-008298 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.h -->
# sources/security-integrity/audit-userspace/auparse/expression.h

## Purpose
Declares auparse search-expression internals: boolean expression nodes, comparison operators, virtual timestamp/type fields, regular-expression support, constructors, destruction, parsing, and evaluation against an `rnode` in the current `auparse_state_t`.

## Important APIs, types, and functions
`struct expr` is a tagged union keyed by `EO_*` operators. `field_id` covers virtual fields `EF_TIMESTAMP`, `EF_RECORD_TYPE`, and `EF_TIMESTAMP_EX`. Public hidden-library entry points are `expr_parse`, `expr_create_comparison`, timestamp constructors, `expr_create_field_exists`, `expr_create_regexp_expression`, `expr_create_binary`, `expr_eval`, and `expr_free`.

## Control flow
Callers either parse a user expression string or build expression trees directly, then `expr_eval` applies the tree to the parser event/record. Boolean nodes recurse through `v.sub`; comparison nodes hold field/value metadata; regexp nodes own compiled `regex_t`.

## State and persistence behavior
Expressions are heap-owned transient filters. They store copied field names, string values, numeric/timestamp precomputations, and compiled regex objects, but do not persist to disk.

## Dependencies and integration points
Depends on POSIX regex, `internal.h`, `auparse_state_t`, and `rnode`. It plugs into auparse searching through `opaque.expr` and record traversal.

## Risks and test signals
Risks are ownership leaks in unions, timestamp/numeric comparison mismatches, invalid regex cleanup, and false negatives because evaluation treats invalid terms as false. Test signals should cover parsed and constructed expressions, virtual fields, regex matches, missing fields, and negated invalid terms.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/famtab.h -->
# sources/security-integrity/audit-userspace/auparse/famtab.h

## Purpose
Maps Linux address-family constants to short audit strings for socket-domain and sockaddr interpretation.

## Important APIs, types, and functions
The file is an `_S(value, "name")` include table consumed by generated lookup helpers such as `fam_i2s`. It covers common families from `AF_LOCAL`, `AF_INET`, and `AF_INET6` through newer numeric entries such as `vsock`, `xdp`, and `mctp`.

## Control flow
No runtime control flow lives here. `interpret.c` includes the generated family lookup and calls it from `print_socket_domain` and `print_sockaddr`.

## State and persistence behavior
Static compile-time data only; no mutable or persistent state.

## Dependencies and integration points
Values come from Linux socket headers. Integration is through `gen_tables` generated lookup code and auparse field types for socket domains and sockaddr families.

## Risks and test signals
Risk is kernel header drift or missing families causing `unknown-family(...)` output. Tests should exercise known IPv4/IPv6/local/netlink values and at least one unknown numeric family.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/famtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h -->
# sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h

## Purpose
Provides `fcntl` command number to symbolic-name mappings for interpreting `fcntl*` syscall arguments.

## Important APIs, types, and functions
The `_S` table maps classic commands `F_DUPFD` through `F_GETOWNER_UIDS` and Linux commands from `F_SETLEASE` through read/write hint operations.

## Control flow
Generated lookup code feeds `fcntl_i2s`; `interpret.c:print_fcntl_cmd` parses a hex command and returns the symbol or `unknown-fcntl-command`.

## State and persistence behavior
Compile-time lookup data only.

## Dependencies and integration points
Depends on Linux/uapi fcntl command numbering. Used by syscall argument interpretation for `a1` on `fcntl` variants and downstream `a2` behavior decisions in `print_a2`.

## Risks and test signals
Risks are incomplete coverage for newer commands and architecture-specific numbering. Tests should confirm known command rendering, unknown fallback, and `F_SETOWN`/`F_SETFD` follow-on argument interpretation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fcntl-cmdtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fsconfig.h -->
# sources/security-integrity/audit-userspace/auparse/fsconfig.h

## Purpose
Maps `fsconfig(2)` command ids to names for new mount API audit records.

## Important APIs, types, and functions
The `_S` table covers `FSCONFIG_SET_FLAG`, string/binary/path/fd setting operations, and create/reconfigure/create-exclusive commands.

## Control flow
Generated `fsconfig_i2s` is called by `interpret.c:print_fsconfig`, which interprets `fsconfig` argument `a1`.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks `include/uapi/linux/mount.h`. It integrates with `normalize_syscall_map.h`, where `fsconfig` is classified as a filesystem mount operation.

## Risks and test signals
Risk is new mount API command drift. Tests should include known command ids, unknown id fallback, and a normalized `fsconfig` syscall showing mount-related action/object classification.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/fsconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/icmptypetab.h -->
# sources/security-integrity/audit-userspace/auparse/icmptypetab.h

## Purpose
Maps ICMP type numbers to human-readable audit strings for netfilter packet records.

## Important APIs, types, and functions
The `_S` table includes echo, unreachable, redirect, time-exceeded, parameter-problem, timestamp, information, and address-mask ICMP types.

## Control flow
Generated `icmptype_i2s` is called by `interpret.c:print_icmptype`, which parses decimal values.

## State and persistence behavior
Static compile-time data only.

## Dependencies and integration points
Based on `include/uapi/linux/icmp.h`; integrated with field type `AUPARSE_TYPE_ICMPTYPE`.

## Risks and test signals
Risk is partial ICMP coverage, especially uncommon or newer types. Tests should verify common type output and `unknown-icmp-type` fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/icmptypetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/inethooktab.h -->
# sources/security-integrity/audit-userspace/auparse/inethooktab.h

## Purpose
Names IPv4/IPv6 netfilter hook numbers for audit packet records.

## Important APIs, types, and functions
The `_S` table maps `0..5` to `PREROUTING`, `INPUT`, `FORWARD`, `OUTPUT`, `POSTROUTING`, and `BROUTING`.

## Control flow
Generated `inethook_i2s` is selected by `interpret.c:print_hook` unless the current record family is ARP, in which case ARP hook lookup is used.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Integrates with `NFPROTO_*` family parsing and netfilter audit fields `hook` and `family`.

## Risks and test signals
Risks are wrong family selection and missing hook constants. Tests should preserve cursor position after `print_hook`, check inet and ARP family paths, and verify unknown hook fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/inethooktab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/internal.h -->
# sources/security-integrity/audit-userspace/auparse/internal.h

## Purpose
Defines auparse private state, event accumulation structures, normalization state containers, and hidden internal helper prototypes shared across the auparse implementation.

## Important APIs, types, and functions
Important types include `auparser_state_t`, `au_lol_t`, `au_lolnode`, `au_lol`, `nv_pair`, `value_t`, `subject`, `object`, `normalize_data`, and `struct opaque`. Hidden functions include config loading/freeing, `lookup_uid_from_name`, `init_normalizer`, and `clear_normalizer`.

## Control flow
This header has no executable flow, but it models the parser lifecycle: source input feeds `opaque.databuf`, records accumulate in `event_list_t` or list-of-lists state, search expressions and cursor fields guide matching, callbacks report parser events, and normalization/interpretation caches hang off the parser state.

## State and persistence behavior
`struct opaque` holds nearly all parser runtime state: input source descriptors, buffers, current event list, search expression, callbacks, list-of-lists event cache, escape/message modes, normalization data, per-parser interpretation list, and UID/GID LRUs. State is in-memory and per parser.

## Dependencies and integration points
Pulls in auparse definitions, event-list and data-buffer types, auditd config, normalize list support, DSO visibility, nvlist, lru, and standard I/O. It is the central integration point for parsing, searching, interpreting, normalization, callbacks, and config.

## Risks and test signals
Risks are lifetime coupling across buffers, event-list nodes, cached interpretation strings, and callback user data. List-of-lists handling must tolerate interleaved events and timeout completion. Tests should stress multi-record interleaving, callback cleanup, cache destruction, normalization reset, and source switching.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.c -->
# sources/security-integrity/audit-userspace/auparse/interpret.c

## Purpose
Implements auparse field interpretation: raw audit field values are converted to user-facing names, paths, flags, socket addresses, syscall argument meanings, identities, TTY data, netfilter metadata, seccomp results, and other typed strings.

## Important APIs, types, and functions
Public hidden entry points include `init_interpretation_list`, `load_interpretation_list`, `free_interpretation_list`, `interpretation_list_cnt`, `lookup_type`, `do_interpret`, UID/GID cache cleanup/metrics, `lookup_uid_from_name`, `au_unescape`, `auparse_interp_adjust_type`, and `auparse_do_interpretation`. Internals include many `print_*` converters, UID/GID lookup via `lru.c`, escaped string handling, `path_norm`, `print_sockaddr`, syscall argument dispatchers `print_a0`..`print_a3`, and generated table lookups.

## Control flow
`auparse_interpret_field` reaches `nvlist_interp_cur_val`, then `do_interpret`. `do_interpret` builds an `idata` snapshot from the current `rnode`, adjusts the field type using record type/name/value rules, then calls `auparse_do_interpretation`. That function first honors an auditd-supplied interpretation list unless it is unknown, then switches on `AUPARSE_TYPE_*` and applies escaping. Syscall argument fields branch by resolved syscall name and sometimes by other arguments, for example `setsockopt` level determines option-name table selection.

## State and persistence behavior
State is per parser except for static helper data. `au->interpretations` caches precomputed auditd interpretations, `au->uid_cache` and `au->gid_cache` cache identity lookups, and `last_type` tracks fanotify `fan_type` for the subsequent `fan_info` field. Returned interpretation strings are heap allocations cached in `nvnode.interp_val` and later freed by nvlist clearing.

## Dependencies and integration points
Depends on libaudit syscall/error/name helpers, generated tables from many `*tab.h` files, Linux network/capability/prctl/personality headers, libc password/group/protocol databases, auparse cursor helpers for contextual fields, and `nvlist`/`lru` ownership rules.

## Risks and test signals
Risks include table drift from kernel headers, argument-context mistakes, unchecked global `last_type` ordering, path normalization edge cases, conversion overflow/errno handling, buffer sizing in flag joins, identity lookup cache collisions, and cursor movement during contextual lookups such as netfilter hook family. Test signals should cover common field types, unknown fallbacks, escaped path/cwd joining, uid/gid caching and flushing, SOCKADDR decoding, syscall-argument dependent output, auditd interpretation list override, and shell/TTY escaping modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.h -->
# sources/security-integrity/audit-userspace/auparse/interpret.h

## Purpose
Declares hidden auparse interpretation APIs shared between field parsing, nvlist handling, ausearch lookup code, and cache lifecycle code.

## Important APIs, types, and functions
Defines `NEVER_LOADED` sentinel and prototypes for interpretation-list lifecycle, type lookup, `do_interpret`, UID/GID cache destruction/metrics, and `au_unescape`.

## Control flow
Consumers initialize the interpretation list when parser state is created, optionally load auditd-provided interpreted text, call `do_interpret` lazily for current fields, and free caches/lists during parser teardown.

## State and persistence behavior
The sentinel distinguishes never-loaded interpretation lists from empty loaded lists. The header exposes no persistence; all state lives in `auparse_state_t`.

## Dependencies and integration points
Depends on `config.h`, DSO visibility, `rnode.h`, time definitions, and GCC attributes. It integrates `interpret.c` with `nvlist.c`, parser teardown, and external ausearch support.

## Risks and test signals
Risks are mismatched ownership expectations for malloc-returning functions and misuse of `NEVER_LOADED`. Tests should check list counts before/after load/free and that interpreted field values are cached and released correctly.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h -->
# sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h

## Purpose
Provides a curated mapping of ioctl request numbers to names for audit syscall interpretation.

## Important APIs, types, and functions
The `_S` table covers selected keyboard/display, CD-ROM, terminal, socket/interface, pseudo-terminal, and DRM ioctls. It is explicitly not comprehensive.

## Control flow
Generated `ioctlreq_i2s` feeds `interpret.c:print_ioctl_req`; unknown requests are rendered as hex.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Values reference Linux kd, cdrom, asm-generic ioctl, and DRM headers. Used when `print_a1` sees `ioctl`.

## Risks and test signals
Risk is sparse coverage and arch-specific ioctl encoding. Tests should assert known request names and hex fallback for unknown requests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ioctlreqtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ip6optnametab.h -->
# sources/security-integrity/audit-userspace/auparse/ip6optnametab.h

## Purpose
Maps IPv6 socket option numbers to symbolic names for `getsockopt`/`setsockopt` interpretation.

## Important APIs, types, and functions
The `_S` table includes legacy `IPV6_2292*`, multicast membership controls, packet info/hop/destination/routing options, firewall revision constants, flowlabel, transparency, and original-destination options.

## Control flow
Generated `ip6optname_i2s` is called by `interpret.c:print_ip6_opt_name` when syscall context says socket level is `IPPROTO_IPV6`.

## State and persistence behavior
Static lookup table only.

## Dependencies and integration points
Tracks Linux IPv6, netfilter IPv6, and multicast route headers. Integration depends on `print_a2` correctly reading `id->a1` socket option level.

## Risks and test signals
Risks are Linux header drift and context misclassification. Tests should cover known IPv6 options, unknown fallback, and end-to-end `setsockopt` with level `IPPROTO_IPV6`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ip6optnametab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipccmdtab.h -->
# sources/security-integrity/audit-userspace/auparse/ipccmdtab.h

## Purpose
Maps System V IPC flag bits to names used when interpreting shared-memory creation flags.

## Important APIs, types, and functions
The `_S` entries cover `IPC_CREAT`, `IPC_EXCL`, and `IPC_NOWAIT`.

## Control flow
Generated table data is used by `interpret.c:print_shmflags`, which combines IPC command flags, SHM mode flags, and permission bits.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Based on Linux IPC headers; integrated with `shm_modetab.h` and mode rendering.

## Risks and test signals
Risks are missing IPC flags or octal-mask mistakes. Tests should validate combined flag and permission output for `shmget`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipccmdtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipctab.h -->
# sources/security-integrity/audit-userspace/auparse/ipctab.h

## Purpose
Maps multiplexed `ipc` syscall operation numbers to operation names.

## Important APIs, types, and functions
The `_S` table names semaphore, message queue, shared memory, and DIPC operation ids such as `semop`, `msgsnd`, `shmat`, and `shmctl`.

## Control flow
Generated `ipc_i2s` is called by `print_ipccall` and `print_syscall` when interpreting legacy `ipc` syscall records.

## State and persistence behavior
Static compile-time data only.

## Dependencies and integration points
Uses constants duplicated in `interpret.c` because some platform headers are unreliable. Integrated with libaudit syscall-name resolution.

## Risks and test signals
Risks are architecture/header mismatches and legacy multiplexing differences. Tests should check named IPC operations and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipctab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/ipoptnametab.h

## Purpose
Maps IPv4 socket option ids to symbolic names.

## Important APIs, types, and functions
The `_S` table covers IP TOS/TTL/options/MTU/error/multicast controls, transparent/freebind, local port range, protocol selection, and iptables socket option constants.

## Control flow
Generated `ipoptname_i2s` is called by `interpret.c:print_ip_opt_name` when `print_a2` sees a socket option level of `IPPROTO_IP`.

## State and persistence behavior
Static lookup table only.

## Dependencies and integration points
Tracks Linux IPv4 and netfilter headers. Integrated with `getsockopt`/`setsockopt` argument interpretation.

## Risks and test signals
Risks are missing newer options and wrong socket level context. Tests should cover common option names, netfilter option ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipoptnametab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.c -->
# sources/security-integrity/audit-userspace/auparse/lru.c

## Purpose
Implements a small dual-key least-recently-used cache used by auparse UID/GID name resolution.

## Important APIs, types, and functions
Exported hidden functions are `init_lru`, `destroy_lru`, `check_lru_uid`, and `check_lru_name`. Internals allocate `Queue`, `Hash`, and `QNode` objects, maintain a doubly linked recency list, hash names using djb2, evict tail nodes, and update parallel UID/name hash slots.

## Control flow
`check_lru_uid` or `check_lru_name` indexes the relevant hash array. A matching node is moved to the front and counted as a hit. A miss frees a colliding node or evicts the list tail when full, allocates a new node, inserts it at the front, and stores it in the hash. Destruction repeatedly dequeues all nodes before freeing hash arrays.

## State and persistence behavior
`Queue` tracks count, total size, hit/miss/eviction counters, front/end list pointers, hash arrays, a debug name, and an unused cleanup callback. State is in-memory and parser-owned.

## Dependencies and integration points
Depends on libc allocation/string functions, `lru.h`, and optional syslog debug logging. `interpret.c` uses it for per-parser UID and GID caches.

## Risks and test signals
Risks include direct-mapped hash collision eviction reducing cache quality, `qsize == 0` division, stale parallel hash links if node identity changes, and currently unused cleanup callbacks. Tests should cover hit promotion, collision replacement, capacity eviction, destroy after mixed uid/name entries, and cache metrics.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.h -->
# sources/security-integrity/audit-userspace/auparse/lru.h

## Purpose
Declares auparse's internal LRU cache data structures and lookup lifecycle functions.

## Important APIs, types, and functions
Defines `QNode` with recency links, use count, uid, and name; `Hash` with an array of node pointers; and `Queue` with cache counters, recency endpoints, UID/name hash tables, label, and cleanup callback. Declares `init_lru`, `destroy_lru`, `check_lru_uid`, and `check_lru_name`.

## Control flow
Callers create a fixed-size queue, request nodes by UID or name, fill missing counterpart fields after NSS lookup, and destroy the queue during parser cleanup.

## State and persistence behavior
All cache state is in-memory and explicitly destroyed. No file persistence exists.

## Dependencies and integration points
Uses DSO visibility and `uid_t`. Consumed by `internal.h` and `interpret.c` for identity translation caches.

## Risks and test signals
Risks are external mutation of exposed structs and ownership assumptions for `name`. Tests should validate both lookup APIs and ensure parser teardown releases caches without leaks.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/lru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/message.c -->
# sources/security-integrity/audit-userspace/auparse/message.c

## Purpose
Implements auparse internal message routing to stderr, syslog, or quiet mode.

## Important APIs, types, and functions
`set_aumessage_mode` stores `message_t` and debug settings on `auparse_state_t`. `audit_msg` checks quiet/debug suppression, then emits formatted output through `vsyslog` or `vfprintf(stderr)`.

## Control flow
Message mode is set on parser state, then every `audit_msg` call first exits for quiet mode or disabled debug messages. Otherwise it initializes a `va_list`, routes to syslog or stderr, appends a newline for stderr, and ends the varargs.

## State and persistence behavior
State is limited to two fields in parser state. Messages may persist externally only if syslog captures them.

## Dependencies and integration points
Depends on `libaudit.h`, `private.h`, and `internal.h`. It backs private aliases `audit_msg`/`set_aumessage_mode` used throughout auparse code.

## Risks and test signals
Risks are null parser pointers, format-string misuse by callers, and debug messages leaking when disabled. Tests should cover quiet suppression, stderr output, syslog mode via mocks if available, and debug filtering.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mmaptab.h -->
# sources/security-integrity/audit-userspace/auparse/mmaptab.h

## Purpose
Maps `mmap` flag bits to names for syscall argument interpretation.

## Important APIs, types, and functions
The `_S` table includes sharing/fixed/anonymous flags plus grow, denywrite, executable, locked, noreserve, populate, stack, huge page, sync, fixed-noreplace, and uninitialized bits.

## Control flow
Generated `mmap_table` and `mmap_strings` are scanned by `interpret.c:print_mmap`, which joins matching flag names with `|`.

## State and persistence behavior
Static generated table data only.

## Dependencies and integration points
Tracks Linux mman headers. Used for `mmap` `a3` and normalization of memory allocation events.

## Risks and test signals
Risks are missing arch-specific flags and output buffer assumptions. Tests should verify zero handling as `MAP_FILE`, multi-flag joins, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mmaptab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mounttab.h -->
# sources/security-integrity/audit-userspace/auparse/mounttab.h

## Purpose
Maps mount flag bits to names for `mount`, `fsmount`, and related audit interpretation.

## Important APIs, types, and functions
The `_S` table includes common `MS_*` flags and newer literal bit entries such as strict-atime, lazytime, submount, snap-stable, nosec, and born.

## Control flow
Generated mount table data is scanned by `interpret.c:print_mount`, which joins all matching flag names.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks `include/uapi/linux/mount.h` and must stay synchronized with `print_mount` buffer sizing. Integrated with syscall argument interpretation and normalization of mount actions.

## Risks and test signals
Risks are table/print buffer mismatch and Linux mount API drift. Tests should cover common flags, combined recursive/bind output, zero/unknown fallback, and new mount syscalls.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mounttab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/netactiontab.h -->
# sources/security-integrity/audit-userspace/auparse/netactiontab.h

## Purpose
Maps netfilter audit target action ids to action names.

## Important APIs, types, and functions
The `_S` entries map `0`, `1`, and `2` to `ACCEPT`, `DROP`, and `REJECT`.

## Control flow
Generated `netaction_i2s` is used by `interpret.c:print_netaction` for `AUPARSE_TYPE_NETACTION`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Based on `xt_AUDIT.h`, integrated with netfilter packet/config audit records.

## Risks and test signals
Risks are new actions not represented and decimal/hex interpretation mistakes. Tests should cover all known values and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/netactiontab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nfprototab.h -->
# sources/security-integrity/audit-userspace/auparse/nfprototab.h

## Purpose
Names netfilter protocol-family ids for packet audit records.

## Important APIs, types, and functions
The `_S` table maps families such as unspecified, inet, ipv4, arp, netdev, bridge, ipv6, and decnet.

## Control flow
Generated `nfproto_i2s` is used by `interpret.c:print_nfproto`, which parses decimal field values.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux netfilter headers and feeds `AUPARSE_TYPE_NFPROTO`. It also affects hook-table selection in contextual hook interpretation.

## Risks and test signals
Risks are missing protocol families and mismatched family/hook semantics. Tests should include ARP versus inet families and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nfprototab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-internal.h -->
# sources/security-integrity/audit-userspace/auparse/normalize-internal.h

## Purpose
Defines internal numeric constants used by auparse event normalization for account classes, syscall object/action classes, object kinds, and event kinds.

## Important APIs, types, and functions
Constants include account thresholds (`NORM_ACCT_*`), syscall/object action classes (`NORM_FILE`, `NORM_EXEC`, `NORM_SOCKET_*`, `NORM_SECURITY_*`, etc.), object kind ids (`NORM_WHAT_*`), and event kind ids (`NORM_EVTYPE_*`).

## Control flow
No execution occurs here. `normalize.c` assigns these constants while analyzing events, and generated map helpers convert them to strings.

## State and persistence behavior
Static compile-time constants only.

## Dependencies and integration points
Used by `normalize.c`, `normalize_*_map.h`, and the generated table layer. Values must stay stable relative to map entries.

## Risks and test signals
Risks are adding constants without map entries, reusing ids, or changing numeric values without regenerating tables. Tests should verify every emitted object/event kind has a string mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.c -->
# sources/security-integrity/audit-userspace/auparse/normalize-llist.c

## Purpose
Implements a minimal singly linked list used by normalization to store subject and object attribute field coordinates.

## Important APIs, types, and functions
Functions are `cllist_create`, `cllist_clear`, `cllist_next`, and `cllist_append`. Nodes store a numeric coordinate and optional data pointer.

## Control flow
Create initializes empty head/current/tail pointers. Append allocates a node, links it at tail, makes it current, and increments count. Iteration starts with inline `cllist_first` from the header, then `cllist_next`. Clear walks nodes, optionally calls the list cleanup callback on node data, frees nodes, and resets the list.

## State and persistence behavior
State is in-memory list ownership inside `normalize_data.actor.attr` and `normalize_data.thing.attr`.

## Dependencies and integration points
Depends on `normalize-llist.h` and libc allocation. `normalize.c` appends encoded record/field locations for later getter iteration.

## Risks and test signals
Risks are allocation failure propagation, callback misuse, and stale current pointers after clear. Tests should cover append order, iteration, cleanup callback invocation, and clear on null/empty lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.h -->
# sources/security-integrity/audit-userspace/auparse/normalize-llist.h

## Purpose
Declares the lightweight list type used by auparse normalization to hold variable-length attributes.

## Important APIs, types, and functions
Defines `data_node` with `num`, `data`, and `next`; `cllist` with head/current/tail, cleanup callback, and count. Inline helpers are `cllist_first` and `cllist_get_cur`; hidden functions cover create, clear, next, and append.

## Control flow
Normalization creates lists during parser initialization, appends record/field coordinates as attributes are discovered, then getter APIs iterate from first to next.

## State and persistence behavior
Per-normalization in-memory list state only.

## Dependencies and integration points
Included by `internal.h` for `normalize_data` and by `normalize.c` for attribute management.

## Risks and test signals
Risks are exposed mutable structs and callers forgetting to clear before reuse. Tests should validate normalization reset clears both subject and object attribute lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize.c -->
# sources/security-integrity/audit-userspace/auparse/normalize.c

## Purpose
Implements auparse event normalization: it analyzes the current audit event and identifies event kind, session, subject, action, object, results, execution method, key, and subject/object attributes through stable getter APIs.

## Important APIs, types, and functions
Lifecycle helpers are `init_normalizer` and `clear_normalizer`. Main entry point is `auparse_normalize`. Getter APIs include `auparse_normalize_get_event_kind`, session/subject/object/result/key cursor seekers, attribute iterators, subject/object kind getters, action, and how. Internals include field-coordinate encoding macros, `normalize_simple`, `normalize_compound`, `normalize_syscall`, object/subject setters, file/socket/program object collectors, event-kind classification, and simple-object finders.

## Control flow
`auparse_normalize` resets state and chooses compound normalization for multi-record events or simple normalization for single-record events. Compound events locate a syscall record, interpret syscall name and success, collect subject/session/how/key, and delegate action/object inference to syscall or record maps. Simple events use record-type-specific branches for config, login, daemon, AVC, BPF, listener, MAC, user, crypto, virt, TTY, and anomaly events. Getters later call `seek_field` to reposition the parser cursor to stored record/field coordinates.

## State and persistence behavior
Normalized state is held in `au->norm_data`. Field references are encoded as 32-bit record/field coordinates with `UNSET` sentinels; strings like action/how/subject-kind are heap-owned; attribute coordinates live in `cllist`. `syscall_success` is file-static and reset with the normalizer.

## Dependencies and integration points
Depends on libaudit record constants, auparse cursor and interpretation APIs, UID lookup, `normalize-llist`, generated normalization maps, and Linux file-mode macros. It is the semantic bridge between raw auparse records and higher-level reporting APIs.

## Risks and test signals
Risks include cursor side effects, hard-coded record ordering for PATH/CWD/SOCKADDR records, global `syscall_success`, incomplete syscall/record maps, interpreter command special casing, and object-kind ambiguity for AVC/MAC/security events. Tests should cover simple and compound events, failed syscalls, path parent fallback, rename/mount/link record ordering, attribute iteration, no-attribute mode, cursor reset after normalization, and every getter return state.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h

## Purpose
Maps internal normalized event-kind constants to public string labels.

## Important APIs, types, and functions
The `_S` table maps `NORM_EVTYPE_*` values to strings such as `user-space`, `configuration`, `audit-daemon`, `mac-decision`, `audit-rule`, `dac-decision`, and `bpf-program`.

## Control flow
Generated `evtype_i2s` is called by `normalize_determine_evkind` in `normalize.c`.

## State and persistence behavior
Static map data only.

## Dependencies and integration points
Depends on `normalize-internal.h`. Integrated with `auparse_normalize_get_event_kind`.

## Risks and test signals
Risks are unmapped event-type constants and user-visible label churn. Tests should validate representative audit record types return expected event-kind strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_evtypetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h

## Purpose
Maps internal normalized object-kind constants to public object-kind strings.

## Important APIs, types, and functions
The `_S` entries cover unknown, filesystem objects, sockets, process/process-group, firewall, service, account, user session, VM, printer, system, audit config/rule, security policy/modules, memory, device, software, and integrity policy.

## Control flow
Generated `normalize_obj_kind_map_i2s` is returned by `auparse_normalize_object_kind`.

## State and persistence behavior
Static map data only.

## Dependencies and integration points
Depends on `normalize-internal.h` values assigned by `normalize.c`.

## Risks and test signals
Risks are missing mappings and semantically misleading labels for broad classes like `unknown` or `system`. Tests should assert object-kind strings for file, socket, account, service, and process events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_record_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_record_map.h

## Purpose
Maps audit record types to normalized action phrases for non-syscall or record-driven events.

## Important APIs, types, and functions
The `_S` table maps many `AUDIT_*` constants to phrases such as `authenticated`, `started-session`, `changed-audit-configuration`, `typed`, `accessed-mac-policy-controlled-object`, `loaded-selinux-policy`, `crashed-program`, and virtualization/crypto actions.

## Control flow
Generated `normalize_record_map_i2s` is called throughout `normalize_simple` and for special compound cases when action derives from record type rather than syscall.

## State and persistence behavior
Static mapping only.

## Dependencies and integration points
Depends on `libaudit.h` record constants and integrates with normalization action selection.

## Risks and test signals
Risks are incomplete mappings returning null action, typo/stability issues in user-facing phrases, and new audit record types falling to unknown behavior. Tests should cover user, daemon, MAC, anomaly, crypto, virt, and config record actions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_record_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h

## Purpose
Classifies syscall names into internal normalized object/action categories.

## Important APIs, types, and functions
The `_S` table maps syscall strings to `NORM_*` classes for file access/stat/chmod/chown/xattr/mount/rename/delete/time/exec, sockets, process signaling, UID/GID changes, time/system-name/device/memory/scheduler changes, and newer security module syscalls.

## Control flow
Generated `normalize_syscall_map_s2i` is called by `normalize_syscall` after resolving the syscall name. The resulting class drives action phrases, object selection, and attribute collection.

## State and persistence behavior
Static string-to-id table only.

## Dependencies and integration points
Depends on `normalize-internal.h` and libaudit syscall naming. It must stay aligned with `interpret.c` argument decoding and Linux syscall additions.

## Risks and test signals
Risks are missing new syscalls, classifying a syscall into the wrong object model, and arch-specific syscall-name differences. Tests should verify representative syscalls in each class and fallback behavior for unclassified syscalls with audit keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.c -->
# sources/security-integrity/audit-userspace/auparse/nvlist.c

## Purpose
Implements dynamic arrays of parsed name/value fields for each audit record and for preloaded interpretation lists.

## Important APIs, types, and functions
Functions include `nvlist_create`, `nvlist_next`, `nvlist_append`, `nvlist_interp_fixup`, `nvlist_goto_rec`, `nvlist_find_name`, `nvlist_get_cur_type`, `nvlist_interp_cur_val`, and `nvlist_clear`. `alloc_array` starts with `NFIELDS` entries and append doubles capacity.

## Control flow
Creation initializes fields and allocates the first array. Append validates name/value pointers, expands as needed, copies pointers into the next slot, makes it current, and increments count. Interpretation is lazy: `nvlist_interp_cur_val` returns cached `interp_val` or calls `do_interpret`. Clear releases interpreted values, optionally frees duplicated fields outside the original record buffer, frees the record buffer and array, and resets counters.

## State and persistence behavior
State is per `nvlist`: array, current index, count, capacity, original parsed record buffer, and end pointer. Field name/value pointers often alias the record buffer, so `not_in_rec_buf` protects against freeing non-owned memory.

## Dependencies and integration points
Depends on `rnode.h`, `interpret.h`, and `auparse-idata.h`. `rnode.nv` stores parsed record fields, and `interpret.c` also uses `nvlist` to hold auditd-supplied interpretations.

## Risks and test signals
Risks include ownership mistakes for aliased versus duplicated strings, ASAN pointer-pair concerns in `not_in_rec_buf`, `NEVER_LOADED` sentinel interaction, and realloc growth failures. Tests should cover parsing more than `NFIELDS`, lazy interpretation caching, find from current cursor, clear with and without `free_interp`, and interpretation-list fixups.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.h -->
# sources/security-integrity/audit-userspace/auparse/nvlist.h

## Purpose
Declares the internal name/value list API used for parsed audit record fields and interpretation lists.

## Important APIs, types, and functions
Inline helpers expose count, reset-to-first, current node/name/value/interpreted value access. Hidden functions create, clear, iterate, append, find, type-adjust, interpret, and move by index.

## Control flow
Parser code appends fields as it tokenizes a record, then callers move through fields or search by name. Interpreted values are requested lazily through the API.

## State and persistence behavior
The header operates on `nvlist` and `nvnode` definitions from `rnode.h`; state is stored inside records or parser interpretation lists.

## Dependencies and integration points
Depends on config, private auparse messaging, `rnode.h`, and event list definitions. It integrates parsing, interpretation, and normalization cursor operations.

## Risks and test signals
Risks are unsafe inline access when `cnt == 0` or `cur` is invalid. Tests should cover empty list accessors, cursor movement, and name lookup after partial iteration.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/open-flagtab.h -->
# sources/security-integrity/audit-userspace/auparse/open-flagtab.h

## Purpose
Maps file open flag bits to names for `open`, `openat`, `openat2`, and `mq_open` argument interpretation.

## Important APIs, types, and functions
The `_S` table includes write/read-write, create/exclusive/truncate/append, nonblocking/sync/direct/directory/nofollow/noatime/cloexec/path/tmpfile bits. `O_RDONLY` is handled specially in code because it is zero.

## Control flow
Generated table data is scanned by `interpret.c:print_open_flags`, which adds `O_RDONLY` when the access mode is zero and joins set bits.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks asm-generic fcntl flags and feeds syscall argument interpretation plus normalization of file-open operations.

## Risks and test signals
Risks are architecture-specific flag differences and zero-valued flag handling. Tests should cover read-only, combined create/truncate/cloexec, tmpfile/path flags, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/open-flagtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h -->
# sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h

## Purpose
Maps `openat2` resolve constraint bits to names.

## Important APIs, types, and functions
The `_S` table covers `RESOLVE_NO_XDEV`, `NO_MAGICLINKS`, `NO_SYMLINKS`, `BENEATH`, `IN_ROOT`, and `CACHED`.

## Control flow
Generated table data is scanned by `interpret.c:print_openat2_resolve` for `AUPARSE_TYPE_RESOLVE`.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks `include/uapi/linux/openat2.h`. Integrated with audit record type handling for `AUDIT_OPENAT2`.

## Risks and test signals
Risks are missing new resolve flags and buffer sizing if table grows. Tests should verify single and combined flags plus zero/unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/openat2-resolvetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/persontab.h -->
# sources/security-integrity/audit-userspace/auparse/persontab.h

## Purpose
Maps Linux process personality values to symbolic names.

## Important APIs, types, and functions
The `_S` table covers `PER_LINUX`, SVR/SCOSVR/OSR/WYSE/XENIX variants, Linux32 variants, IRIX, RISCOS, Solaris, UW7, OSF4, and HPUX personalities.

## Control flow
Generated `person_i2s` is called by `interpret.c:print_personality`, which masks with `PER_MASK` and appends `~ADDR_NO_RANDOMIZE` when set.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Depends on Linux personality constants and local fallback for `ADDR_NO_RANDOMIZE`. Used for `personality` syscall argument decoding.

## Risks and test signals
Risks are personality flag combinations outside the base mask and header drift. Tests should cover base personality, address-randomization flag, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/persontab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/pktoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/pktoptnametab.h

## Purpose
Maps packet socket option names for `SOL_PACKET` socket option interpretation.

## Important APIs, types, and functions
The `_S` table includes packet membership, rings, statistics, auxdata, versioning, reserve, loss, fanout, qdisc bypass, rollover stats, ignore outgoing, and VNET header size options.

## Control flow
Generated `pktoptname_i2s` is called by `interpret.c:print_pkt_opt_name` when syscall context indicates `SOL_PACKET`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks `include/uapi/linux/if_packet.h`; selected from `print_a2` based on socket option level.

## Risks and test signals
Risks are missing newer packet options and wrong level detection. Tests should exercise known packet options and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/pktoptnametab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h -->
# sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h

## Purpose
Maps `prctl` option numbers to symbolic names for audit syscall interpretation.

## Important APIs, types, and functions
The `_S` table covers legacy options through newer controls for SVE/SME, speculation, pointer auth, tagged addresses, syscall user dispatch, scheduler core, memory deny-write-execute, memory merge, and RISC-V vector control.

## Control flow
Generated `prctl_opt_i2s` is called by `interpret.c:print_prctl_opt`; other `prctl` argument decoding uses the option value to interpret capabilities and death signals.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks `include/uapi/linux/prctl.h`. Integrated with `print_a0` and `print_a1` syscall argument dispatch.

## Risks and test signals
Risks are rapid kernel option growth and secondary-argument context mistakes. Tests should cover known options, unknown fallback, and capability/death-signal dependent argument decoding.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/private.h -->
# sources/security-integrity/audit-userspace/auparse/private.h

## Purpose
Declares private auparse messaging aliases and hidden message-mode functions.

## Important APIs, types, and functions
Defines `audit_msg` as `auparse_msg` and `set_aumessage_mode` as `set_aup_message_mode`. Declares `auparse_msg` with printf-format checking and `set_aup_message_mode`.

## Control flow
Callers use the audit-style aliases; implementation in `message.c` routes messages according to parser state.

## State and persistence behavior
No state in the header; message mode/debug fields live in `auparse_state_t`.

## Dependencies and integration points
Depends on public `auparse.h`, common definitions, and DSO visibility. Used by internal auparse modules needing diagnostics without exporting generic symbol names.

## Risks and test signals
Risks are macro alias confusion and mismatched format strings. Compile-time format warnings and mode-routing tests in `message.c` are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prottab.h -->
# sources/security-integrity/audit-userspace/auparse/prottab.h

## Purpose
Maps memory protection bits to names for `mmap` and `mprotect` interpretation.

## Important APIs, types, and functions
The `_S` table includes read, write, exec, sem, growsdown, and growsup protection bits.

## Control flow
Generated data is scanned by `interpret.c:print_prot`, with special handling for `PROT_NONE` when low permission bits are zero.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks asm-generic mman constants and feeds syscall argument interpretation for memory events.

## Risks and test signals
Risks are arch-specific flags and missing protection bits. Tests should cover `PROT_NONE`, combined protections, mmap-specific `PROT_SEM`, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prottab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ptracetab.h -->
# sources/security-integrity/audit-userspace/auparse/ptracetab.h

## Purpose
Maps `ptrace` request numbers to symbolic names.

## Important APIs, types, and functions
The `_S` table includes classic ptrace operations plus extended `0x4200+` requests such as set options, get/set siginfo, regsets, seize, interrupt, seccomp filter/metadata, syscall info, rseq config, and syscall user dispatch config.

## Control flow
Generated `ptrace_i2s` is called by `interpret.c:print_ptrace` for `ptrace` syscall argument `a0`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux ptrace and x86 ptrace ABI headers. Integrated with syscall argument interpretation.

## Risks and test signals
Risks are arch-specific request values and new kernel requests. Tests should cover classic and extended requests plus unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ptracetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/recvtab.h -->
# sources/security-integrity/audit-userspace/auparse/recvtab.h

## Purpose
Maps socket send/receive message flag bits to names.

## Important APIs, types, and functions
The `_S` table includes `MSG_OOB`, `MSG_PEEK`, routing/truncation/wait flags, connection flags, error queue, nosignal/more, batch, fastopen, cmsg cloexec, and compat bits.

## Control flow
Generated data is scanned by `interpret.c:print_recv` for send/receive syscall arguments.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks Linux socket headers. Used by `print_a2`/`print_a3` for recv/send variants.

## Risks and test signals
Risks are flag drift and signed/high-bit parsing. Tests should cover low and high bit flags, combined output, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/recvtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rlimittab.h -->
# sources/security-integrity/audit-userspace/auparse/rlimittab.h

## Purpose
Maps resource limit ids to names for `setrlimit`/`getrlimit`-family interpretation.

## Important APIs, types, and functions
The `_S` table maps ids `0..15` to CPU, file size, data, stack, core, RSS, process count, file descriptor, memory lock, address space, locks, pending signals, message queue, nice, real-time priority, and real-time time limits.

## Control flow
Generated `rlimit_i2s` is called by `interpret.c:print_rlimit` for matching syscall arguments.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks asm-generic resource headers. Integrated via `print_a0` for `*etrlimit` syscall names.

## Risks and test signals
Risks are missing `RLIMIT_RTTIME`-adjacent additions and fixed `i < 17` bound mismatch. Tests should verify each known id and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rlimittab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rnode.h -->
# sources/security-integrity/audit-userspace/auparse/rnode.h

## Purpose
Defines parsed audit record nodes and their field-array structure.

## Important APIs, types, and functions
`NFIELDS` sets the initial field allocation. `nvnode` holds field name, raw value, interpreted value, and item index. `nvlist` stores a dynamic array plus cursor/count/size and record-buffer ownership markers. `rnode` stores raw record text, interpretation text, cwd, record type, machine/syscall/a0/a1 context, parsed field list, event item index, source location, and next pointer.

## Control flow
Parser code builds `rnode` linked lists for event records, populates `nvlist`, and later interpretation/normalization traverse fields and records through cursor APIs.

## State and persistence behavior
All state is in-memory per parsed event. `record` and `interp` strings are owned by the record lifecycle; `nvlist.record/end` track the parsed buffer for safe cleanup.

## Dependencies and integration points
Used by `nvlist`, `interpret`, expression evaluation, event-list code, and normalization.

## Risks and test signals
Risks include ownership confusion between `rnode.record`, `nvlist.record`, and field pointers, plus stale syscall context. Tests should parse records with many fields, multi-record events, interpreted fields, and source location metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/schedtab.h -->
# sources/security-integrity/audit-userspace/auparse/schedtab.h

## Purpose
Maps Linux scheduler policy ids to names.

## Important APIs, types, and functions
The `_S` table covers `SCHED_OTHER`, `FIFO`, `RR`, `BATCH`, `IDLE`, and `DEADLINE`.

## Control flow
Generated `sched_i2s` is used by `interpret.c:print_sched`, which masks policy bits and appends `SCHED_RESET_ON_FORK` when set.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux sched headers and supports normalization of scheduler-related syscalls.

## Risks and test signals
Risks are missing policies and flag masking mistakes. Tests should cover policy names, reset-on-fork combination, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/schedtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seccomptab.h -->
# sources/security-integrity/audit-userspace/auparse/seccomptab.h

## Purpose
Maps seccomp return action bits to normalized strings.

## Important APIs, types, and functions
The `_S` table maps seccomp action masks to `kill-process`, `kill-thread`, `trap`, `errno`, `user-notify`, `trace`, `log`, and `allow`.

## Control flow
Generated `seccomp_i2s` is called by `interpret.c:print_seccomp_code` after masking with `SECCOMP_RET_ACTION`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks `include/uapi/linux/seccomp.h` and feeds `AUPARSE_TYPE_SECCOMP`; normalization treats seccomp as DAC-decision style event.

## Risks and test signals
Risks are missing future actions and incorrect masking of data bits. Tests should include action values with lower data bits set and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seccomptab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seektab.h -->
# sources/security-integrity/audit-userspace/auparse/seektab.h

## Purpose
Maps `lseek` whence values to names.

## Important APIs, types, and functions
The `_S` table covers `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`.

## Control flow
Generated `seek_i2s` is used by `interpret.c:print_seek` for `lseek` argument interpretation.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux fs headers and feeds syscall argument `a2` handling for `lseek`.

## Risks and test signals
Risks are new whence constants and masking to `0xFF`. Tests should verify known whence values and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seektab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/shm_modetab.h -->
# sources/security-integrity/audit-userspace/auparse/shm_modetab.h

## Purpose
Maps shared-memory mode flag bits to names.

## Important APIs, types, and functions
The `_S` table includes `SHM_DEST`, `SHM_LOCKED`, `SHM_HUGETLB`, and `SHM_NORESERVE`.

## Control flow
Generated data is combined by `interpret.c:print_shmflags` with IPC command flags and permission bits.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux SHM headers and integrates with `ipccmdtab.h` and mode-short rendering.

## Risks and test signals
Risks are missing SHM flags and octal-mask collisions. Tests should validate combined SHM flags and permission formatting.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/shm_modetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/signaltab.h -->
# sources/security-integrity/audit-userspace/auparse/signaltab.h

## Purpose
Maps signal numbers to signal names for syscall argument and clone flag interpretation.

## Important APIs, types, and functions
The `_S` table covers signals `0..31`, including standard POSIX signals and Linux-specific names.

## Control flow
Generated `signal_i2s` is called by `interpret.c:print_signals` and `print_clone_flags`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks asm-generic signal numbering. Integrated with kill/tkill/tgkill, `rt_sigaction`, `prctl`, and clone signal decoding.

## Risks and test signals
Risks are architecture-specific signal numbering and missing realtime signals. Tests should cover common signals, signal zero, clone low-byte signal output, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/signaltab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockleveltab.h -->
# sources/security-integrity/audit-userspace/auparse/sockleveltab.h

## Purpose
Maps socket option level numbers to symbolic `SOL_*` names.

## Important APIs, types, and functions
The `_S` table covers IP/TCP/UDP/IPV6/ICMPV6 and many protocol levels including packet, netlink, Bluetooth, TLS, XDP, MPTCP, MCTP, SMC, and VSOCK.

## Control flow
Generated `socklevel_i2s` is a fallback in `interpret.c:print_sock_opt_level` when libc protocol lookup does not provide a name and the level is not `SOL_SOCKET`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux socket headers and complements `getprotobynumber`. It feeds `getsockopt`/`setsockopt` level interpretation.

## Risks and test signals
Risks are overlap with protocol database names, new levels, and platform differences. Tests should cover `SOL_SOCKET`, protocol-db levels, table-only levels, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockleveltab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/sockoptnametab.h

## Purpose
Maps `SOL_SOCKET` option ids to symbolic option names.

## Important APIs, types, and functions
The `_S` table covers classic socket options, timestamping, BPF attach/detach, busy poll, cookies, buffer locks, memory reservation, PIDFD options, and PPC-specific remapped entries.

## Control flow
Generated `sockoptname_i2s` is called by `interpret.c:print_sock_opt_name`; PPC/PPC64 values in a specific range are adjusted by adding 100 before lookup.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks asm-generic socket headers and architecture differences. Selected by `print_a2` when socket option level is `SOL_SOCKET`.

## Risks and test signals
Risks are architecture remap errors, new socket options, and level confusion. Tests should cover common options, PPC-adjusted values, new high ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockoptnametab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktab.h -->
# sources/security-integrity/audit-userspace/auparse/socktab.h

## Purpose
Maps legacy multiplexed `socketcall` operation ids to socket operation names.

## Important APIs, types, and functions
The `_S` table names operations such as socket, bind, connect, listen, accept, send/recv variants, shutdown, getsockopt/setsockopt, accept4, recvmmsg, and sendmmsg.

## Control flow
Generated `sock_i2s` is used by `print_socketcall` and `print_syscall` for legacy `socketcall` syscall records.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Uses Linux net syscall constants and integrates with libaudit syscall-name resolution.

## Risks and test signals
Risks are legacy architecture differences and missing multiplexed operations. Tests should verify common operation names and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktypetab.h -->
# sources/security-integrity/audit-userspace/auparse/socktypetab.h

## Purpose
Maps socket type ids to symbolic socket type names.

## Important APIs, types, and functions
The `_S` table includes stream, datagram, raw, RDM, seqpacket, DCCP, and packet socket types.

## Control flow
Generated `sock_type_i2s` is called by `interpret.c:print_socket_type`, which masks low bits before lookup.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux net/socket headers. Used for `socket` syscall argument `a1`.

## Risks and test signals
Risks are masked-out modifier flags and new socket types. Tests should cover known types, type values with flags, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktypetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h

## Purpose
Maps TCP socket option ids to names.

## Important APIs, types, and functions
The `_S` table covers no-delay, max segment, cork, keepalive settings, sync/defer/window/info/congestion, MD5, repair, fast open, not-sent low-water, zero-copy receive, TCP-AO, and related options.

## Control flow
Generated `tcpoptname_i2s` is used by `interpret.c:print_tcp_opt_name` when socket option level is `IPPROTO_TCP`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux TCP headers and is selected by `print_a2` for socket option syscalls.

## Risks and test signals
Risks are new TCP option drift and platform availability differences. Tests should cover common options, newer TCP-AO ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/Makefile.am -->
# sources/security-integrity/audit-userspace/auparse/test/Makefile.am

## Purpose
Defines Automake build, distribution, and test targets for auparse's C, shell, Python, static-link, diff, and memory tests.

## Important APIs, types, and functions
Declares `noinst_PROGRAMS`, `TESTS`, distributed scripts/reference logs, compiler/linker flags including ASAN and static variants, program sources/LDADD dependencies, and convenience targets `diffcheck`, `memcheck`, `pycheck`, `pydiffcheck`, and `pymemcheck`.

## Control flow
Normal `make check` runs shell and binary tests. Static builds add data buffer, LRU, and UID/name wrapper tests. Diff targets compare generated output with references; Python targets set `PYTHONPATH`, `LD_LIBRARY_PATH`, and `srcdir`; cleanup removes generated outputs and copied logs for out-of-tree builds.

## State and persistence behavior
Build artifacts, generated scripts, `.cur` comparison files, raw transformed logs, and copied test logs are transient and removed by clean rules.

## Dependencies and integration points
Links tests against `libauparse`, `libaudit`, and `libaucommon`. Integrates optional ASAN/static/Python3 build configuration and uses `auditd_raw.sed` for raw output normalization.

## Risks and test signals
Risks are stale references, missing static-only tests when dynamic builds are used, environment-sensitive Python paths, and brittle sed normalization. Test signals are `make check`, `diffcheck`, valgrind targets, Python diff output, and explicit `lru_cache_test`/`uid_name_wrap_test` under static builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed -->
# sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed

## Purpose
Normalizes raw auditd log text into the same comparison shape as `auparselol_test --check` output for diff testing.

## Important APIs, types, and functions
This is a sed script of substitution commands. It removes or rewrites formatting differences around `cwd`, `comm`, `msg`, hostname, success, exe, terminal, SELinux AVC text, auid/session/login wording, policy/load messages, PAM phrases, and permission strings.

## Control flow
`Makefile.am:diffcheck` pipes `test3.log` through this sed script, sorts the result, and compares it against sorted auparselol parsed output.

## State and persistence behavior
No internal state. It produces transient normalized text for comparison.

## Dependencies and integration points
Depends on sed regex behavior and the exact audit log phrasing emitted by auditd/kernel/libaudit. Integrated only with auparse test targets.

## Risks and test signals
Risks are brittle substitutions as audit message wording changes, regex portability, and hiding meaningful parser differences by over-normalizing. The key signal is a clean `diffcheck`; new audit samples should add or adjust substitutions deliberately.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auditd_raw.sed -->
