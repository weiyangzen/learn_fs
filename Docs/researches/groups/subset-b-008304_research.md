# subset-b-008304

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/delete_all.c -->
# sources/security-integrity/audit-userspace/src/delete_all.c

Purpose: implements `delete_all_rules`, the auditctl helper that enumerates kernel audit rules and deletes the rules selected by the process-wide `key_match` predicate. It is a small bridge between libaudit netlink rule listing and the local linked-list representation used by auditctl.

Important APIs/functions: exports `delete_all_rules(int fd)`. It calls `audit_request_rules_list_data`, waits with `select`, reads replies with `audit_get_reply`, filters `AUDIT_LIST_RULES` records through external `key_match`, stores copies in `llist` via `list_append`, and deletes them with `audit_send(fd, AUDIT_DEL_RULE, ...)`. It uses `audit_msg` for error reporting and `list_clear` for cleanup.

Control flow: the function requests a rule dump and rejects non-positive sequence ids. It initializes an `llist`, then loops up to 40 tenths of a second, resetting the timeout counter whenever a reply arrives. Replies with a different netlink sequence are ignored. `NLMSG_DONE` ends collection, `NLMSG_ERROR` with a kernel error aborts, non-rule replies are skipped, and matching rules are copied into the list. After collection it iterates the saved list and sends each rule back as an `AUDIT_DEL_RULE` request.

State and persistence: no persistent process state is owned here. It temporarily persists matching rule blobs in an in-memory list so deletion happens after the listing pass, avoiding mutation while the kernel dump is being consumed. Kernel audit rule state is changed only by the final `AUDIT_DEL_RULE` sends.

Dependencies and integration: depends on `libaudit.h`, audit private helpers, `auditctl-llist.h`, POSIX `select`, and netlink reply structures. It is part of audit-userspace command handling and relies on the caller to supply an audit netlink fd and define the active deletion filter through `key_match`.

Risks: `fd_set read_mask` is initialized once before the loop; because `select` can mutate fd sets, reuse without reinitializing could miss readiness on some platforms. The select result is ignored and `audit_get_reply` is attempted nonblocking every iteration, which is deliberate but can make timeout behavior dependent on libaudit nonblocking semantics. Partial deletion failures leave earlier rules deleted and later rules intact. Correctness depends on `list_append` making a deep copy of `rep.ruledata` because the reply buffer is reused.

Test signals: exercise with a fake or test audit netlink endpoint that emits mixed sequence numbers, `NLMSG_DONE`, `NLMSG_ERROR`, and matching/nonmatching `AUDIT_LIST_RULES`. Integration tests should verify that only `key_match` rules are deleted, timeout with no replies returns success with no deletion, and send failures abort with list cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/delete_all.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/Makefile.am -->
# sources/security-integrity/audit-userspace/src/libev/Makefile.am

Purpose: defines the Automake build recipe for the bundled libev convenience library used by audit-userspace. It builds a static, non-installed libtool archive from the libev core and libevent compatibility layer.

Important build variables: `VERSION_INFO = 4:0:0`, `EXTRA_DIST` ships backend source files and `libev.m4`, `AM_CFLAGS` enables PIC, debug info, no strict aliasing, and suppresses unused-value warnings, `noinst_HEADERS` lists `ev.h`, `ev_vars.h`, `ev_wrap.h`, and `event.h`, and `noinst_LTLIBRARIES = libev.la` declares the internal library.

Control flow: Automake consumes this file during configure/make generation. `libev_la_SOURCES = ev.c event.c` compiles the core translation unit and compatibility layer; the backend files are not separate compilation units because `ev.c` includes selected backends directly under compile-time feature macros. `libev_la_LDFLAGS = -no-undefined -static` requests a static libtool archive with resolved symbols.

State and persistence: this file does not manage runtime state. It controls generated build artifacts and distribution contents, including ensuring backend files are included in tarballs even when not separately compiled.

Dependencies and integration: integrates the vendored libev subtree into the audit-userspace Automake/libtool build. The `-fno-strict-aliasing` flag matches libev's watcher-casting style, and `-DPIC -fPIC` supports linking into other audit-userspace objects.

Risks: backend files must remain in `EXTRA_DIST` because they are included by `ev.c`; omitting one can break distribution builds without affecting in-tree builds. `event.h` is listed but not in this work item; compatibility consumers depend on it matching `event.c`. Static linkage and local CFLAGS can diverge from system libev behavior.

Test signals: run `autoreconf`/`configure` and `make` from a clean distribution tree, verify `libev.la` builds from `ev.c` and `event.c`, and run `make distcheck` to catch missing `EXTRA_DIST` files.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev.c -->
# sources/security-integrity/audit-userspace/src/libev/ev.c

Purpose: implements the bundled libev event loop core: configuration detection, backend selection, loop lifecycle, pending queue dispatch, timer heaps, fd watcher reification, signal/async wakeups, stat/inotify support, fork handling, and all public watcher start/stop APIs declared in `ev.h`.

Important APIs/functions: public exports include version/backend queries, `ev_default_loop`, `ev_loop_new`, `ev_loop_destroy`, `ev_loop_fork`, `ev_run`, `ev_break`, `ev_ref`/`ev_unref`, `ev_now_update`, `ev_suspend`/`ev_resume`, `ev_feed_event`, `ev_feed_fd_event`, `ev_invoke_pending`, `ev_clear_pending`, and start/stop operations for `ev_io`, `ev_timer`, `ev_periodic`, `ev_signal`, `ev_child`, `ev_stat`, `ev_idle`, `ev_prepare`, `ev_check`, `ev_embed`, `ev_fork`, `ev_cleanup`, and `ev_async`. Internal anchors include `loop_init`, `fd_reify`, `fd_change`, `fd_kill`, heap helpers, `time_update`, `timers_reify`, `periodics_reify`, `evpipe_init`, `pipecb`, and optional inotify/signal/timerfd callbacks.

Control flow: compile-time feature macros are derived from `config.h`, platform headers, and libev defaults. `loop_init` initializes clocks, wakeup pipe state, optional fd subsystems, selects the first requested backend in priority order, and installs backend function pointers. `ev_run` invokes already pending watchers, checks fork state, queues fork and prepare watchers, reifies fd changes into the active backend, computes a bounded wait time from active timers/periodics/backend minimums, calls `backend_poll`, updates time, queues expired timers/periodics/idle/check watchers, and invokes pending callbacks by priority. The loop exits when there are no active references, `ev_break` requests it, or one-shot/nonblocking flags are used.

State and persistence: in multiplicity mode, `struct ev_loop` stores all loop state through the declarations in `ev_vars.h`; otherwise those fields are static globals. Persistent runtime state includes fd watcher lists (`anfds`), pending queues by priority, timer and periodic heaps, backend fd and backend-private arrays, signal watcher tables, child watcher hash tables, async watcher arrays, and optional inotify/timerfd/signalfd descriptors. State is heap-allocated with a replaceable allocator and released in `ev_loop_destroy`. Kernel state is synchronized lazily through `fdchanges` and `backend_modify`.

Dependencies and integration: includes `ev.h`, `ev_vars.h`, `ev_wrap.h`, and backend implementation files such as `ev_epoll.c`, `ev_poll.c`, `ev_select.c`, and optionally `ev_linuxaio.c`. It uses POSIX time, signal, process, fd, inotify, eventfd, signalfd, timerfd, and syscall APIs depending on platform features. `event.c` adapts this native API for libevent-style callers.

Risks: the file is intentionally macro-heavy and backend code is included into the same translation unit, so compile-time feature changes can alter ABI, loop layout, and available watcher types. Correctness depends on watcher fields remaining stable while active; assertions catch some misuse but production builds may continue after undefined caller behavior. Signal and async wakeups rely on atomic flags, memory fences, and a pipe/eventfd protocol. Fork handling has backend-specific recreation paths. Timer behavior depends on monotonic clock availability and time-jump detection. The bundled copy intentionally disables linux AIO by default and drops io_uring in the `config.h` path, so backend expectations should be checked against audit-userspace configuration.

Test signals: build with the audit-userspace configuration and run event-loop tests that cover fd readiness, timer repeat and cancellation, `EVRUN_NOWAIT`/`EVRUN_ONCE`, `ev_break`, priorities, signal delivery, async wakeups, fork reinitialization, and backend fallback. Enable `EV_VERIFY >= 2` in targeted builds to catch corrupted watcher lists/heaps. Platform CI should cover at least epoll and poll/select configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev.h -->
# sources/security-integrity/audit-userspace/src/libev/ev.h

Purpose: declares the public native libev API and watcher data structures for the bundled event loop. It is the contract consumed by `ev.c`, `event.c`, and any audit-userspace code using native libev watchers.

Important APIs/types: defines feature flags (`EV_FEATURE_*`), watcher enable macros, timestamp type `ev_tstamp`, multiplicity macros (`EV_P`, `EV_A`, `EV_DEFAULT`), event masks (`EV_READ`, `EV_WRITE`, `EV_TIMER`, `EV_SIGNAL`, etc.), watcher base macros, watcher structs (`ev_io`, `ev_timer`, `ev_periodic`, `ev_signal`, `ev_child`, `ev_stat`, `ev_idle`, `ev_prepare`, `ev_check`, `ev_fork`, `ev_cleanup`, `ev_embed`, `ev_async`), `union ev_any_watcher`, loop flags, backend flags, and prototypes for loop lifecycle, run control, pending/event feeding, and watcher start/stop functions.

Control flow: this header does not execute runtime control flow, but it defines the initialization macros used by callers. `ev_init` clears active/pending state and stores a callback; `ev_TYPE_set` macros assign type-specific read-only fields; `ev_TYPE_init` macros combine both. Inline helpers expose default-loop access, activity/pending checks, priorities, callback storage, and compatibility names for pre-4.0 APIs.

State and persistence: watcher structs are caller-owned and persist as long as they may be active or pending in a loop. The `active` and `pending` fields are private loop-owned indexes; `data` is user-owned by default through `EV_COMMON`. The header supports changing `EV_COMMON`, priorities, multiplicity, and feature macros at compile time, which changes structure layout and binary compatibility.

Dependencies and integration: used directly by `ev.c` and by compatibility wrappers. It includes standard headers conditionally for atomics and stat support. The ABI version is declared as 4.33. `event.c` embeds libevent-compatible fields that wrap these native watchers.

Risks: applications must not move or free active/pending watchers and must not mutate read-only fields such as fd/signum while active. Feature macros can remove watcher types or alter `struct ev_loop` handling. The callback setter uses `memmove` to avoid strict-aliasing issues, and build flags should preserve that assumption. Child and signal watchers are restricted to the default loop.

Test signals: compile consumers in C and C++ modes with representative feature combinations, verify watcher struct layout assumptions through build tests, and exercise each init/start/stop pair through `ev.c` integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_epoll.c -->
# sources/security-integrity/audit-userspace/src/libev/ev_epoll.c

Purpose: implements the Linux epoll backend for libev fd readiness. It maps libev `EV_READ`/`EV_WRITE` interest to epoll interest, handles epoll-specific kernel quirks, and supplies backend hooks consumed by `ev.c`.

Important APIs/functions: internal hooks are `epoll_init`, `epoll_modify`, `epoll_poll`, `epoll_destroy`, and `epoll_fork`; helper `epoll_epoll_create` uses `epoll_create1(EPOLL_CLOEXEC)` when available or falls back to `epoll_create` plus `FD_CLOEXEC`. State uses `backend_fd`, `epoll_events`, `epoll_eventmax`, `epoll_eperms`, `epoll_epermcnt`, and `ANFD` fields `emask` and `egen`.

Control flow: `epoll_init` creates the epoll fd, installs `backend_modify`/`backend_poll`, and allocates an initial event array. `epoll_modify` ignores pure deletes optimistically, adds or modifies active fds, stores fd plus generation in `data.u64`, handles `ENOENT`/`EEXIST` races, treats `EPERM` as an always-ready fd by placing it in `epoll_eperms`, and kills invalid fds after hard errors. `epoll_poll` calls `epoll_wait`, validates generation counters, repairs interest masks for spurious events, feeds fd events, grows the receive array when full, and synthesizes events for `EPERM` fds.

State and persistence: the backend persists kernel registration in the epoll instance and mirrors it in `anfds[fd].emask`. Generation counters prevent stale events from closed/reused descriptors from being accepted. The `epoll_eperms` array persists fds epoll cannot monitor and is compacted when they no longer need synthetic events.

Dependencies and integration: requires `<sys/epoll.h>` and libev core helpers/macros from `ev.c`. It is included into `ev.c` under `EV_USE_EPOLL` and is also used by the linux AIO backend as its fallback and wakeup path.

Risks: delete elision improves common performance but requires spurious-event repair logic. Epoll behavior across `fork`, descriptor duplication, regular files, and older kernels is explicitly fragile. `EPERM` fds are treated as always ready, which can spin if callers keep unsupported fds active. Backend recreation after generation mismatch sets `postfork |= 2`, so fork/rearm paths must be tested.

Test signals: run fd readiness tests on pipes/sockets, close/reuse watched fds, watch unsupported fds that return `EPERM`, force event-array growth with many ready fds, and verify `ev_loop_fork` rebuilds registrations.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_linuxaio.c -->
# sources/security-integrity/audit-userspace/src/libev/ev_linuxaio.c

Purpose: implements the experimental Linux AIO `IOCB_CMD_POLL` backend for fd readiness, with epoll as a required fallback. In this bundled configuration it is present but normally disabled by `EV_USE_LINUXAIO 0`.

Important APIs/functions: syscall wrappers `evsys_io_setup`, `evsys_io_destroy`, `evsys_io_submit`, `evsys_io_cancel`, and `evsys_io_getevents` call raw Linux AIO syscalls. Backend hooks are `linuxaio_init`, `linuxaio_modify`, `linuxaio_poll`, `linuxaio_destroy`, and `linuxaio_fork`. Helpers include `linuxaio_nr_events`, `linuxaio_array_needsize_iocbp`, `linuxaio_free_iocbp`, `linuxaio_fd_rearm`, `linuxaio_parse_events`, `linuxaio_get_events_from_ring`, `linuxaio_ringbuf_valid`, `linuxaio_get_events`, and `linuxaio_io_setup`.

Control flow: `linuxaio_init` requires a new enough Linux kernel and a working epoll backend, creates an AIO context, starts an internal epoll watcher for fallback events, and replaces backend hooks with linux AIO handlers. `linuxaio_modify` allocates an iocb per fd, cancels active one-shot polls before resubmitting, switches fds previously handed to epoll back to AIO when possible, records fd/generation in `aio_data`, and queues submissions. `linuxaio_poll` submits queued iocbs, falls back individual unsupported fds to epoll on `EINVAL`, grows/recreates the AIO context on `EAGAIN`, can fall back completely to epoll if setup fails, then fetches completions via ring buffer or `io_getevents` and rearms one-shot polls.

State and persistence: persists the AIO context (`linuxaio_ctx`), sizing iteration, per-fd iocb array, queued submission array, and an internal epoll watcher. Each iocb stores the active poll mask in `aio_buf`, fd in `aio_fildes`, generation-tagged identity in `aio_data`, and uses negative `aio_reqprio` to mark epoll fallback ownership.

Dependencies and integration: requires Linux `<linux/aio_abi.h>`, raw syscall numbers, `<poll.h>`, and the epoll backend. It consumes the same `ANFD` generation and event feeding mechanisms as epoll. `ev_vars.h` and `ev_wrap.h` include its loop fields when enabled or when wrapper generation is requested.

Risks: depends on undocumented kernel ring-buffer layout and underdocumented `IOCB_CMD_POLL` behavior. AIO polls are one-shot, so missed rearming can lose readiness. Error handling is complex: `EINVAL`, `EAGAIN`, `EBADF`, and fork can all migrate state between AIO and epoll. Resource limits can force context recreation or complete backend downgrade. Since the audit-userspace config disables it by default, bitrot risk is higher than for epoll/poll/select.

Test signals: only meaningful when compiled with `EV_USE_LINUXAIO`. Test supported sockets/pipes, unsupported tty/file descriptors, many watchers to hit ring sizing, forced `io_submit` partial failures, ring-buffer and `io_getevents` paths, full epoll downgrade, and fork reinitialization.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_linuxaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_poll.c -->
# sources/security-integrity/audit-userspace/src/libev/ev_poll.c

Purpose: implements the portable POSIX `poll(2)` backend for libev fd readiness. It is simpler than epoll and serves as a fallback or selected backend on platforms where poll is reliable.

Important APIs/functions: backend hooks are `poll_init`, `poll_modify`, `poll_poll`, and `poll_destroy`; helper `array_needsize_pollidx` initializes fd-to-poll-array indexes to `-1`. State uses `polls`, `pollcnt`, `pollmax`, `pollidxs`, and `pollidxmax`.

Control flow: `poll_init` installs backend callbacks and clears arrays. `poll_modify` ensures an index entry for the fd, allocates or updates a `struct pollfd` when interest is nonzero, and removes entries by swapping the last active pollfd into the removed slot. `poll_poll` calls `poll`, maps `POLLIN`/`POLLOUT` plus `POLLERR`/`POLLHUP` to libev read/write events, kills invalid fds on `POLLNVAL`, and invokes recovery helpers for `EBADF` or `ENOMEM`.

State and persistence: keeps a dense `polls` array for kernel calls and a sparse `pollidxs[fd]` reverse map. State is fully in memory and freed by `poll_destroy`; there is no persistent kernel registration between calls beyond the watched fd numbers.

Dependencies and integration: requires `<poll.h>` and libev core helpers from `ev.c`. It is included under `EV_USE_POLL` and selected by `loop_init` after higher-priority backends fail or are disabled.

Risks: `poll` scales linearly with active fds and platform-specific bugs are called out elsewhere in backend recommendation logic. Correct reverse-index maintenance is critical when removing by swap. `POLLNVAL` leads to watcher kill and `EV_ERROR` delivery through core `fd_kill`.

Test signals: watch multiple fds, add/remove from the middle of the poll array, verify read/write/hup/error mapping, inject closed fds to trigger `POLLNVAL`/`EBADF`, and run with many descriptors to catch index growth issues.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_select.c -->
# sources/security-integrity/audit-userspace/src/libev/ev_select.c

Purpose: implements the `select(2)` backend for libev fd readiness. It is the broadest portability backend and supports either native `fd_set` storage or custom bit-vector storage depending on platform macros.

Important APIs/functions: backend hooks are `select_init`, `select_modify`, `select_poll`, and `select_destroy`. It manages input/output read and write vectors `vec_ri`, `vec_ro`, `vec_wi`, `vec_wo`, optional Windows exception vector `vec_eo`, and `vec_max` for custom bit vectors.

Control flow: `select_modify` updates the persistent interest sets for read and write events, allocating larger bit vectors when not using `fd_set`. `select_poll` copies interest sets to output sets, calls `select` with a computed timeout, handles Windows-specific error behavior, dispatches `EBADF`/`ENOMEM` recovery, and scans resulting sets to feed fd events. `select_init` allocates and zeroes vectors; `select_destroy` frees them.

State and persistence: the backend persists desired read/write sets in memory and creates per-poll copies because `select` mutates them. No kernel registration persists between calls. With custom vectors, `vec_max` grows to cover the highest watched fd word and is not shrunk.

Dependencies and integration: uses `<sys/select.h>`, `<inttypes.h>`, `<string.h>`, and Windows socket compatibility branches through macros supplied by `ev.c`. It is included under `EV_USE_SELECT` and selected last among standard backends.

Risks: fd-set mode is limited by `FD_SETSIZE` and asserts if callers exceed it. Windows requires special handling because `select` operates on sockets and reports some errors in the exception set or as `EINVAL`. Custom bit-vector mode depends on `NFDBITS`/`fd_mask` details. Linear scanning across `anfdmax` or vector words can be expensive for sparse high fds.

Test signals: build both `fd_set` and custom-vector modes where possible, watch fds near `FD_SETSIZE`, exercise read/write readiness and timeout behavior, close watched fds to trigger `EBADF`, and run Windows socket tests if that configuration is supported.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_select.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_vars.h -->
# sources/security-integrity/audit-userspace/src/libev/ev_vars.h

Purpose: declares the complete set of fields that make up libev loop state. It is included by `ev.c` with different `VAR` definitions to either populate `struct ev_loop` in multiplicity mode or define static globals in single-loop mode.

Important APIs/types: this is not a public API, but it enumerates critical loop members: clocks (`now_floor`, `mn_now`, `rtmn_diff`), reverse-feed and pending queues, backend identity/function pointers, fd watcher arrays, wakeup pipe state, backend-specific storage for select/poll/epoll/linuxaio/iouring/kqueue/port/iocp, fd-change queues, timer and periodic heaps, idle/prepare/check/fork/cleanup/async watcher arrays, inotify/signalfd/timerfd state, original flags, loop counters, userdata, and advanced callbacks.

Control flow: the file is macro-expanded by its includer. Each `VARx(type, name)` expands through `VAR(name, type name)`, while array declarations use `VAR` directly. Conditional blocks mirror feature macros so disabled watcher/backend fields do not exist unless `EV_GENWRAP` is generating wrappers.

State and persistence: every declaration here is persistent event-loop state owned by libev for the lifetime of a loop. The fields store heap allocations, kernel descriptor numbers, callback pointers, counters, atomic flags, and backend-private arrays that are initialized in `loop_init`, mutated throughout `ev_run` and watcher operations, and released in `ev_loop_destroy`.

Dependencies and integration: tightly coupled to `ev.c` internal typedefs (`W`, `ANFD`, `ANPENDING`, `ANHE`, `ANFS`) and platform/backend types such as `struct pollfd`, `struct epoll_event`, `aio_context_t`, `struct iocb`, `sigset_t`, and `HANDLE`. `ev_wrap.h` must stay synchronized with this file.

Risks: adding/removing/reordering fields changes `struct ev_loop` layout and can break binary compatibility for consumers compiled with different feature macros. Conditional fields must match backend code and destroy/fork logic exactly. Wrapper generation drift between this file and `ev_wrap.h` causes compile failures or incorrect macro access.

Test signals: compile with multiplicity on/off and a matrix of backend feature macros, verify `ev_wrap.h` regeneration is clean, and run loop lifecycle tests under each backend to catch missing initialization or cleanup for a declared field.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_vars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_wrap.h -->
# sources/security-integrity/audit-userspace/src/libev/ev_wrap.h

Purpose: provides generated preprocessor aliases that map loop member names to `((loop)->member)` in multiplicity builds, and undefines those aliases when included a second time. It allows backend and core code to use short field names while still compiling against a `struct ev_loop *`.

Important APIs/macros: the first include guard branch defines aliases for every loop field, including generic state (`activecnt`, `backend`, `anfds`, `timers`, `pendings`), backend-specific fields (`epoll_events`, `polls`, `vec_ri`, `linuxaio_ctx`, `iouring_*`, `kqueue_*`, `port_*`), watcher arrays, signal/timer/inotify fields, and advanced callbacks. The `#else` branch undefines `EV_WRAP_H` and all aliases.

Control flow: this header is included after `struct ev_loop` is declared in `ev.c` so subsequent implementation code can use unqualified field names. At the end of `ev.c`, it is included again to undefine the aliases and avoid leaking macros beyond the translation unit.

State and persistence: it owns no runtime state; it is a compile-time mapping layer over the fields declared by `ev_vars.h`. Correctness depends on each macro matching a real field in the active `struct ev_loop` configuration.

Dependencies and integration: generated by `update_ev_wrap` from loop variable declarations and tightly paired with `ev_vars.h`. Backend files included inside `ev.c` depend on these aliases for loop-state access.

Risks: manual edits are explicitly forbidden by the file header. If `ev_vars.h` changes without regenerating this file, builds can fail or backend code can refer to stale field names. Because the aliases are broad common identifiers, include order and the final undef pass matter.

Test signals: regenerate wrappers after `ev_vars.h` changes and check for a clean diff, compile with `EV_MULTIPLICITY=1`, and verify a preprocessed or compile test catches both define and undef include modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/ev_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.c -->
# sources/security-integrity/audit-userspace/src/libev/event.c

Purpose: implements a libevent-compatible API on top of libev. It lets code written for older libevent-style `struct event` and `event_base` calls run against the bundled libev core.

Important APIs/functions: exports `event_get_version`, `event_get_method`, `event_init`, `event_base_new`, `event_base_free`, `event_dispatch`, `event_loop`, `event_loopexit`, `event_set`, `event_add`, `event_del`, `event_active`, `event_pending`, `event_base_set`, `event_base_loop`, `event_base_dispatch`, `event_base_loopexit`, `event_once`, `event_base_once`, `event_priority_init`, `event_priority_set`, and `event_get_callback`. Internal callbacks `ev_x_cb_io`, `ev_x_cb_sig`, `ev_x_cb_to`, and `ev_x_once_cb` translate libev revents into libevent callback signatures.

Control flow: `event_init` initializes the current base as the default libev loop on first use or a new loop later when multiplicity is enabled. `event_set` initializes embedded libev io/signal and timer watchers inside `struct event`. `event_add` starts the signal or io watcher and optionally arms the timeout watcher. `event_del` stops all active embedded watchers. Read/write callbacks delete non-persistent events before invoking the user callback; timeout callbacks always delete first. Base loop and dispatch calls delegate to `ev_run`; loopexit schedules an `ev_once` timer that calls `ev_break`.

State and persistence: global `ev_x_cur` stores the current event base. `struct event_base` is an opaque dummy type cast to/from `struct ev_loop`. Each `struct event` persists callback metadata, flags, fd, requested events, priority, result bits, base pointer, and embedded libev watchers. `event_base_once` allocates a small heap wrapper and frees it after the callback.

Dependencies and integration: includes `event.h` or a configured `EV_EVENT_H`, plus `ev.h` through that compatibility header. It depends on libev multiplicity for multiple independent bases; without multiplicity it asserts on multiple base creation. It uses standard `malloc/free` for one-shot compatibility wrappers rather than libev's allocator hook.

Risks: `event_init` and `ev_x_cur` are not thread-safe. The compatibility layer only approximates libevent semantics: priority initialization is a no-op, `event_pending` reports timeout time as current loop time rather than remaining timeout, and only read/write/signal/timer behavior is mapped. Non-persistent io events are deleted before callback, so callback code must re-add if needed. One-shot allocation failure returns `-1`.

Test signals: run libevent-style tests for persistent and non-persistent fd events, signal events, timeout-only events, combined fd+timeout events, `event_once`, `event_base_once`, `event_loopexit`, and multiple bases when `EV_MULTIPLICITY` is enabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/libev/event.c -->
