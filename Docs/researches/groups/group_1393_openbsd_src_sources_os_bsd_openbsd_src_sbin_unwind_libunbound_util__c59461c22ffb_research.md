# Group Research: group_1393_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_util__c59461c22ffb

Scope checked against `Docs/research_subset_a.md`: these files are under `sources/os/bsd/openbsd-src`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.h

Header for Unbound's function-pointer whitelist checks. It documents the security goal: before indirect callback invocation, ensure callback pointers match known legitimate functions to reduce exploitability of overwritten function pointers.

Key contents:
- Defines `fptr_ok(x)`, which calls `fatal_exit(...)` on whitelist failure unless `EXPORT_ALL_SYMBOLS` disables it for Windows DLL/exe layouts.
- Declares whitelist checkers for:
  - network callbacks: `comm_point`, raw `comm_point`, timers, signals, accept/stop-accept callbacks, libevent-style callbacks;
  - pending UDP/TCP and serviced-query callbacks;
  - red-black tree comparators and LRU hash callbacks;
  - module environment service callbacks: `send_query`, `attach_sub`, `detach_subs`, `add_sub`, `kill_sub`, `detect_cycle`;
  - module lifecycle and state-machine callbacks: `init`, `deinit`, `startup`, `destartup`, `operate`, `inform_super`, `clear`, `get_mem`;
  - allocation cleanup, tube listen handlers, mesh callbacks, config print callbacks, inplace EDNS/reply/query callbacks, and serve-expired lookup callbacks.
- Includes declarations for test helper comparators (`order_lock_cmp`, `codeline_cmp`, `replay_var_compare`) because the whitelist implementation needs to recognize them.

Dependencies:
- Pulls in callback type definitions from `util/netevent.h`, `util/storage/lruhash.h`, `util/module.h`, `util/tube.h`, and `services/mesh.h`.
- Relies on `fatal_exit` from logging infrastructure.

Research notes:
- This header is an API/security boundary rather than an implementation file; actual whitelist membership lives in `util/fptr_wlist.c`.
- `mini_ev_cmp` from `mini_event.c` is one known consumer-side comparator that is whitelisted in the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/iana_ports.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/iana_ports.inc

Generated numeric include file containing IANA-assigned port numbers.

Key contents:
- 5,507 sorted integer entries.
- Minimum value: `1`.
- Maximum value: `49001`.
- Entries are strictly increasing; no duplicate or non-increasing entry was found.
- Format is a comma-terminated integer per line, intended to be included inside a C initializer.

Use in tree:
- Included by `util/config_file.c` inside `init_outgoing_availports()`:
  - initializes outgoing available ports from `1024` upward;
  - clears `49152..49407` to leave a slice of ephemeral ports available to other programs;
  - clears every port listed by `iana_ports.inc` so Unbound avoids IANA-assigned ports for outgoing random-port selection.

Research notes:
- The file contains data only, no declarations, comments, or code.
- Comment at inclusion site says it is generated with `make iana_update`.
- Because the include is embedded in a C array with an added `-1` sentinel after it, each line intentionally has a trailing comma.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/iana_ports.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.c

Implementation pieces for the portability layer declared in `locks.h`; most lock operations are macros in the header, while this file supplies functions that cannot be macro-only.

Key functions:
- `ub_thread_blocksigs()`: blocks all signals for the current thread or process using `pthread_sigmask`, Solaris `thr_sigsetmask`, or `sigprocmask`.
- `ub_thread_sig_unblock(int sig)`: unblocks one signal using the same platform-dependent APIs.
- No-thread fallback:
  - `ub_thr_fork_create(...)`: simulates thread creation by `fork()`, runs the function in the child, exits child with status 0.
  - `ub_thr_fork_wait(...)`: waits on the child process and logs abnormal exits.
- Solaris:
  - `ub_thread_key_get(...)`: wrapper around `thr_getspecific`.
- Windows:
  - `log_win_err(...)`: formats `GetLastError()`.
  - `lock_basic_init/destroy/lock/unlock(...)`: implements a simple interlocked spin/sleep mutex using `InterlockedExchange` and exponential `Sleep`.
  - TLS key helpers: `ub_thread_key_create`, `ub_thread_key_set`, `ub_thread_key_get`.
  - Thread helpers: `ub_thread_create`, `ub_thread_self`, `ub_thread_join`.

Dependencies:
- Includes `util/locks.h`, `signal.h`, and optionally `sys/wait.h`.
- Uses logging/fatal-exit functions through `LOCKRET`, `log_err`, `log_warn`, and `fatal_exit`.

Research notes:
- The file is highly conditional; OpenBSD/pthread builds primarily use the macro definitions in `locks.h`.
- The no-thread mode has process isolation, so comments explicitly note that no shared data structures or real locking exist in that fallback.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.h

Portable locking and thread abstraction header for Unbound.

Key contents:
- Defines `LOCKRET(func)` unless provided by the includer. It logs nonzero pthread/Solaris-style return codes.
- Supports optional lock-debug mode through `USE_THREAD_DEBUG`, enabled when pthreads, spinlocks, and `ENABLE_LOCK_CHECKS` are present.
- Defines three lock classes:
  - `lock_rw_type`: reader/writer lock, falling back to mutex if rwlocks are unavailable.
  - `lock_basic_type`: ordinary mutex.
  - `lock_quick_type`: spinlock where available, otherwise mutex.
- Defines thread abstraction:
  - pthread: `pthread_t`, `pthread_create`, `pthread_join`, `pthread_key_t`, thread naming variants, and a wrapper that raises stack size to at least 2 MiB.
  - Solaris threads: `thread_t`, `thr_create`, `thr_join`, TLS wrappers.
  - Windows threads: `HANDLE` threads, `DWORD` TLS keys, lock routines implemented in `locks.c`.
  - no threads: `THREADS_DISABLED`, no-op locks, fork-based thread simulation, pid-based self/join.
- Declares:
  - `ub_thread_blocksigs()`
  - `ub_thread_sig_unblock(int sig)`

Important behavior:
- `PTHREADSTACKSIZE` is fixed at `2*1024*1024` to avoid small default stacks on musl/Alpine.
- Thread naming is handled through multiple platform-specific `pthread_setname_np` variants when detected.
- In no-thread mode, locks are all no-ops and `ub_thread_create` maps to fork simulation.

Research notes:
- This header is a portability foundation for logging, networking, caches, and OpenSSL lock callbacks.
- Most users include this file for macros, so changing it has broad compile-time impact.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/locks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.c

Implementation of Unbound's logging service.

Key globals:
- `verbosity`: global verbosity level, default `NO_VERBOSE`.
- `logfile`: active file sink, default unset until `log_init`.
- `logkey`: thread-local key for numeric thread ID in log output.
- `log_lock`: mutex protecting `logfile` when threads are enabled.
- `ident` / `default_ident`: process identity printed in messages.
- `logging_to_syslog`: enabled for syslog or Windows event log builds.
- `log_time_asc`, `log_time_iso`: timestamp formatting controls.

Key functions:
- `log_init(filename, use_syslog, chrootdir)`: initializes TLS key/lock, switches log destination, opens syslog or file/stderr, handles chroot path prefix stripping.
- `log_file(FILE*)`: directly sets the active file sink.
- `log_thread_set`, `log_thread_get`: store and retrieve per-thread numeric log ID.
- Identity controls: `log_ident_set`, `log_ident_set_default`, `log_ident_revert_to_default`, `log_ident_set_or_default`.
- Time controls: `log_set_time_asc`, `log_set_time_iso`.
- `log_get_lock()`: returns log lock pointer if initialized and threads are enabled.
- `log_vmsg(...)`: central formatter and sink dispatcher for syslog, Windows event log, or file logging.
- Public wrappers: `log_info`, `log_err`, `log_warn`, `fatal_exit`, `verbose`, `log_query`, `log_reply`.
- Hex/buffer logging:
  - `log_hex_f(...)` chunks binary data into uppercase hex lines.
  - `log_hex(...)` logs at current verbosity.
  - `log_buf(...)` logs an `sldns_buffer` if verbosity allows.
- Windows-only `wsa_strerror(DWORD err)`: maps many Winsock error constants to strings.

Important behavior:
- File logs include pid and thread ID.
- ISO timestamps include millisecond precision and timezone offset when supported.
- `fatal_exit` logs a critical message then exits with status 1.
- `verbose` maps verbosity levels to notice/info/debug priority classes.

Dependencies:
- Uses `util/locks.h`, `sldns/sbuffer.h`, syslog where available, Windows service event logging where applicable.

Research notes:
- Logging is process-global and lock-protected after initialization.
- `log_vmsg` truncates formatted messages to `MAXSYSLOGMSGLEN`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.h

Public API for Unbound logging.

Key contents:
- Defines `enum verbosity_value`:
  - `NO_VERBOSE`
  - `VERB_OPS`
  - `VERB_DETAIL`
  - `VERB_QUERY`
  - `VERB_ALGO`
  - `VERB_CLIENT`
- Declares global `verbosity`.
- Declares logging lifecycle/configuration:
  - `log_init`
  - `log_file`
  - `log_thread_set`
  - `log_thread_get`
  - identity setters/reverters
  - ASCII/ISO timestamp setters
  - `log_get_lock`
- Declares message functions:
  - `verbose`
  - `log_info`
  - `log_err`
  - `log_warn`
  - `log_query`
  - `log_reply`
  - `fatal_exit`
  - `log_vmsg`
- Declares binary diagnostics:
  - `log_hex`
  - `log_buf`
- Defines `log_assert(x)`:
  - active only under `UNBOUND_DEBUG`;
  - uses `assert(x)` for clang analyzer;
  - otherwise calls `fatal_exit` with file, line, function, and expression.
- Windows-only declaration:
  - `wsa_strerror(DWORD err)` under `USE_WINSOCK`.

Research notes:
- Uses `ATTR_FORMAT` on printf-like APIs and `ATTR_NORETURN` on `fatal_exit`, so callers get compiler checking when configured.
- This is a central dependency for locks, network helpers, module utilities, and diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.c

Minimal libevent-compatible backend using `select(2)`, compiled when `USE_MINI_EVENT` is defined and `USE_WINSOCK` is not.

Key functions:
- `mini_ev_cmp(...)`: comparator for timeout tree entries, ordered by absolute timeout then pointer address for uniqueness.
- `event_init(time_secs, time_tv)`: allocates an `event_base`, initializes current time, creates timeout rbtree, allocates fd and signal arrays, initializes fd sets.
- `event_get_version()`: returns `mini-event-<PACKAGE_VERSION>`.
- `event_get_method()`: returns `"select"`.
- `handle_timeouts(...)`: fires expired timeout callbacks from the rbtree and computes wait duration for the next timeout.
- `handle_select(...)`: copies fd sets, calls `select`, updates current time, and dispatches ready read/write callbacks.
- `event_base_dispatch(...)`: main loop; processes timeouts then select events until `need_to_exit`.
- `event_base_loopexit(...)`: sets exit flag.
- `event_base_free(...)`: frees base-owned arrays/tree/base.
- `event_set(...)`: initializes a single event structure and validates callback with `fptr_ok`.
- `event_base_set(...)`: associates event with base.
- `event_add(...)`: activates fd and/or timeout event, updates fd sets and max fd.
- `event_del(...)`: removes fd and/or timeout event and adjusts max fd.
- `signal_add(...)` / `signal_del(...)`: basic single-event-per-signal handling through `signal(2)` and a global `signal_base`.
- Non-mini-event fallback defines a stub `mini_ev_cmp` returning 0 for non-Winsock builds.

Important constraints:
- One event per fd.
- One handler per signal.
- Limited by `MAX_FDS` and `FD_SETSIZE`.
- Signal handling is global through `signal_base`, so multiple event bases cannot independently own signal dispatch.
- Callback pointers are checked against the function-pointer whitelist before invocation.

Dependencies:
- `util/mini_event.h`, `util/fptr_wlist.h`, rbtree support, `gettimeofday`, `select`, `signal`.

Research notes:
- Despite header comments saying second-level timeout accuracy, implementation stores and compares microseconds.
- The implementation intentionally covers only the subset of libevent API needed by this codebase.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.h

Header for the minimal select-based event API.

Key contents:
- Active only under `USE_MINI_EVENT && !USE_WINSOCK`.
- Renames libevent-style symbols into `minievent_*` / `minisignal_*` namespace with macros to avoid linker crosslinking of private symbols.
- Defines event bit flags:
  - `EV_TIMEOUT`
  - `EV_READ`
  - `EV_WRITE`
  - `EV_SIGNAL`
  - `EV_PERSIST`
- Includes `rbtree.h` for timeout ordering.
- Defines limits:
  - `MAX_FDS 1024`
  - `MAX_SIG 32`
- Defines `struct event_base`:
  - timeout rbtree;
  - fd-to-event array;
  - max/capacity fd tracking;
  - fd sets for reads, writes, ready, content;
  - signal event array;
  - loop-exit flag;
  - pointers to externally stored current time.
- Defines `struct event`:
  - rbtree node;
  - added flag;
  - base pointer;
  - fd/signal number;
  - event interest bits;
  - timeout value;
  - callback and callback argument.
- Declares event and signal functions plus `evtimer_add/del` and `signal_set` convenience macros.
- Declares `mini_ev_cmp` outside the conditional so the comparator symbol remains visible for whitelist/test references.

Research notes:
- This is a compatibility shim, not a full libevent replacement.
- Callers must call `event_base_set` for every event before adding it.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/mini_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.c

Implementation helpers for the DNS module interface declared in `module.h`.

Key functions:
- Debug string helpers:
  - `strextstate(enum module_ext_state)`
  - `strmodulevent(enum module_ev)`
- Validation/servfail error-info collection:
  - `errinf(...)`
  - `errinf_ede(...)`
  - `errinf_origin(...)`
  - `errinf_rrset(...)`
  - `errinf_dname(...)`
  - `errinf_to_str_bogus(...)`
  - `errinf_to_reason_bogus(...)`
  - `errinf_to_str_servfail(...)`
  - `errinf_to_str_misc(...)`
- EDNS known-option management:
  - `edns_known_options_init(...)`
  - `edns_known_options_delete(...)`
  - `edns_register_option(...)`
  - `edns_option_is_known(...)`
  - `edns_bypass_cache_stage(...)`
  - `unique_mesh_state(...)`
  - `log_edns_known_options(...)`
- Inplace callback management:
  - `inplace_cb_register(...)`
  - `inplace_cb_delete(...)`
- Subquery state propagation:
  - `copy_state_to_super(...)` copies `was_ratelimited` upward only when the super state has not already recorded ratelimiting.

Important behavior:
- Error info is stored in the query's regional allocator and appended in order.
- Error-info collection is skipped unless validator log level is high enough or `log_servfail` is enabled.
- `errinf_to_reason_bogus` prefers the latest explicit EDE reason, but does not replace a more specific reason with generic `LDNS_EDE_DNSSEC_BOGUS`.
- EDNS option and inplace callback registration are rejected after workers exist (`env->worker` set), enforcing registration during module initialization.
- `edns_register_option` overwrites flags for an already registered option; otherwise it appends up to `MAX_KNOWN_EDNS_OPTS`.

Dependencies:
- `util/module.h`, `sldns/wire2str.h`, config, regional allocation, dname formatting, and `net_help` address formatting.

Research notes:
- `module.h` declares `inplace_cb_lists_delete`, but this paired implementation file does not define it.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.h

Core interface for Unbound DNS handling modules.

Major concepts:
- Modules are state machines run in sequence.
- The mesh drives query state machines, passes replies back from rightmost modules to leftmost modules, and handles recursive subqueries.
- Per-query allocations generally live in the query `regional`.
- `module_env` provides shared caches, config, services, time, random state, mesh access, and module-specific globals.

Key constants:
- `MAX_MODULE 16`
- `MAX_KNOWN_EDNS_OPTS 256`

Key types:
- `struct errinf_strlist`: linked validation/error explanation strings plus EDE reason.
- `enum inplace_cb_list_type`: reply/cache/local/servfail/query/query-response/EDNS-parsed callback list identifiers.
- `struct edns_known_option`: option code plus cache-bypass and aggregation flags.
- `struct inplace_cb`: linked registered callback entry.
- Callback typedefs:
  - `inplace_cb_reply_func_type`
  - `inplace_cb_query_func_type`
  - `inplace_cb_edns_back_parsed_func_type`
  - `inplace_cb_query_response_func_type`
  - `serve_expired_lookup_func_type`
- `struct module_env`: shared runtime environment with config, caches, infra/key caches, outbound query service, mesh subquery services, scratch memory/buffer, worker/outnet/mesh pointers, validation anchors, auth zones, forwards/hints/views/respip, module info, inplace callback lists, EDNS known options, module stack, cachedb flag, and `unique_mesh`.
- `enum module_ext_state`: initial, wait reply, wait module, restart next, wait subquery, error, finished.
- `enum module_ev`: new, pass, reply, no reply, caps fail, module done, error.
- `struct sock_list`: linked sockaddr list used for origins/blacklists.
- `struct serve_expired_data`: timer plus cached-answer lookup callback.
- `struct module_qstate`: per-query state including qinfo, flags, priming/validation-recursion flags, reply/return data, origins, blacklist, regional allocator, error info, current module, per-module ext states/minfo, mesh info, EDNS option lists, cache-control flags, ratelimit/refetch/cachedb/error-response state, client/respip/RPZ flags, TCP/drop flags.
- `struct module_func_block`: module lifecycle and per-query methods (`startup`, `destartup`, `init`, `deinit`, `operate`, `inform_super`, `clear`, `get_mem`).

Declared helper APIs:
- State/event stringification: `strextstate`, `strmodulevent`.
- Error-info append/format helpers.
- EDNS known-option allocation, registration, lookup, cache-bypass, mesh-uniqueness, and logging.
- Inplace callback registration/deletion/list deletion.
- `copy_state_to_super`.

Research notes:
- This is one of the central contracts of libunbound/unwind's recursive resolver pipeline.
- Function pointers declared here are protected elsewhere by the whitelist layer from `fptr_wlist.h`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.c

Implementation of network helper functions, DNS address utilities, TLS/OpenSSL setup, socket portability helpers, and hex conversion.

Key globals:
- `EDNS_ADVERTISED_SIZE = 4096`
- `MINIMAL_RESPONSES = 0`
- `RRSET_ROUNDROBIN = 1`
- `LOG_TAG_QUERYREPLY = 0`
- TLS session ticket key array under `HAVE_SSL`.

Address and socket helpers:
- `str_is_ip6`: checks for `:`.
- `fd_set_nonblock` / `fd_set_block`: uses `fcntl` or Windows `ioctlsocket`.
- `is_pow2`: treats 0 as true.
- `memdup`: malloc/copy helper.
- `log_addr`, `log_name_addr`, `log_err_addr`: formatted address diagnostics.
- `extstrtoaddr`: parses IP strings with optional `@port`.
- `ipstrtoaddr`: parses IPv4/IPv6, including IPv6 `%scope`.
- `netblockstrtoaddr`: parses `ip/prefix`, validates prefix, masks host bits.
- RPZ helpers:
  - internal `ipdnametoaddr`
  - `netblockdnametoaddr`
- Auth-name parsing:
  - `authextstrtoaddr`: parses IP with optional `@port` and `#tls-auth-name`.
  - `authextstrtodname`: parses domain with optional port/auth name into wire-format dname.
- `sockaddr_store_port`: writes port into IPv4/IPv6 sockaddr.
- DNS query logging:
  - `log_nametypeclass`
  - `log_query_in`
- Sockaddr comparison:
  - `sockaddr_cmp`: address plus port.
  - `sockaddr_cmp_addr`: address only.
  - `sockaddr_cmp_scopeid`: address plus port plus IPv6 scope ID.
- Address predicates/manipulation:
  - `addr_is_ip6`
  - `addr_mask`
  - `addr_in_common`
  - `addr_to_str`
  - `prefixnet_is_nat64`
  - `addr_to_nat64`
  - `addr_is_ip4mapped`
  - `addr_is_ip6linklocal`
  - `addr_is_broadcast`
  - `addr_is_any`
- `sock_list_insert`, `sock_list_prepend`, `sock_list_find`, `sock_list_merge`: regional linked-list utilities for socket origins/blacklists.

Crypto/TLS helpers:
- `log_crypto_err`, `log_crypto_err_code`, `log_crypto_err_io`, `log_crypto_err_io_code`: OpenSSL error reporting with fallbacks when SSL is absent.
- `log_cert`: verbose X509 certificate printing.
- ALPN callbacks:
  - DoT selects `dot`.
  - DoH uses nghttp2 protocol selection when available.
- `listen_sslctx_setup`: disables legacy protocols, optionally disables TLS 1.2/1.3 based on config, disables renegotiation when supported, sets cipher preference, handles OpenSSL 3 unexpected EOF option, and may set security level to 0.
- `listen_sslctx_setup_2`: enables ECDHE setup where needed.
- `listen_sslctx_create`: creates server SSL context, loads certificate/key, optional client CA verification, ciphers/ciphersuites, ticket callback, and ALPN.
- Windows trust-store support through `add_WIN_cacerts_to_openssl_store`.
- `connect_sslctx_create`: creates client SSL context, disables legacy protocols, optionally loads client cert/key and CA/default verification paths.
- `incoming_ssl_fd` / `outgoing_ssl_fd`: wrap accepted/connected fd in SSL object and set accept/connect state.
- `check_auth_name_for_ssl` and `set_auth_name_on_ssl`: enforce or configure TLS hostname authentication and SNI.
- Pre-OpenSSL-1.1 lock callbacks:
  - `ub_openssl_lock_init`
  - `ub_openssl_lock_delete`
- TLS ticket key support:
  - `listen_sslctx_setup_ticket_keys`: reads configured 80-byte key files, respecting chroot prefix stripping.
  - `tls_session_ticket_key_cb`: encrypt/decrypt callback using AES-256-CBC and SHA-256 HMAC/MAC APIs.
  - `listen_sslctx_delete_ticket_keys`: wipes and frees key material.

Portability and conversion:
- `sock_strerror`: `strerror` or `wsa_strerror`.
- `sock_close`: `close` or `closesocket`.
- `hex_ntop`: binary to lowercase hex.
- `hex_pton`: hex string to binary with validation.

Research notes:
- The file is heavily conditional around SSL, OpenSSL version/API variants, Windows, nghttp2, and platform socket features.
- NAT64 prefix lengths are restricted to RFC-compatible byte-aligned forms: 32, 40, 48, 56, 64, and 96.
- TLS ticket setup allocates the key array before reading all files; failure paths return early after logging but do not centrally unwind already stored keys in this function.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.h

Public interface for network helper functions and constants.

Key constants/macros:
- DNS flag bits in host byte order:
  - `BIT_CD`, `BIT_AD`, `BIT_Z`, `BIT_RA`, `BIT_RD`, `BIT_TC`, `BIT_AA`, `BIT_QR`
  - `FLAGS_GET_RCODE`, `FLAGS_SET_RCODE`
- `UDP_AUTH_QUERY_TIMEOUT 3000`
- EDNS:
  - `EDNS_ADVERTISED_VERSION 0`
  - extern `EDNS_ADVERTISED_SIZE`
  - `EDNS_DO`
- Address sizes:
  - `INET_SIZE 4`
  - `INET6_SIZE 16`
- DNSKEY flags:
  - `DNSKEY_BIT_ZSK`
  - `DNSKEY_BIT_SEP`
- `GET_RANDOM_ID(rnd)`
- fallback `MSG_DONTWAIT 0`
- extern config-style globals:
  - `MINIMAL_RESPONSES`
  - `RRSET_ROUNDROBIN`
  - `LOG_TAG_QUERYREPLY`

Declared API groups:
- Generic helpers:
  - IP-family detection, nonblocking/blocking fd setup, power-of-two check, `memdup`.
- Logging helpers:
  - address logging, name/address logging, errno/address logging, name/type/class logging, query logging.
- Parsing/conversion:
  - `extstrtoaddr`
  - `ipstrtoaddr`
  - `netblockstrtoaddr`
  - `authextstrtoaddr`
  - `authextstrtodname`
  - `sockaddr_store_port`
  - `addr_to_str`
  - `netblockdnametoaddr`
- Address comparison/predicates:
  - `sockaddr_cmp`
  - `sockaddr_cmp_addr`
  - `sockaddr_cmp_scopeid`
  - `addr_is_ip6`
  - `addr_mask`
  - `addr_in_common`
  - `prefixnet_is_nat64`
  - `addr_to_nat64`
  - `addr_is_ip4mapped`
  - `addr_is_ip6linklocal`
  - `addr_is_broadcast`
  - `addr_is_any`
- `sock_list` operations:
  - insert, prepend, find, merge.
- Crypto/TLS interface:
  - OpenSSL error logging.
  - certificate logging.
  - listening/client SSL context creation and setup.
  - SSL fd wrapping.
  - TLS auth-name checking/SNI/hostname setup.
  - OpenSSL lock initialization/deletion.
  - TLS session ticket key setup/deletion.
- Socket portability:
  - `sock_strerror`
  - `sock_close`
- Hex conversion:
  - `hex_ntop`
  - `hex_pton`

Research notes:
- This header ties together low-level socket handling, DNS wire/log formatting, EDNS sizing, NAT64 conversion, TLS setup, and portability glue.
- It is a broad utility surface; changes here affect config parsing, outbound networking, listener TLS setup, logging, and DNS module code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/net_help.h -->