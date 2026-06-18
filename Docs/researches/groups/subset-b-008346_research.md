# Research Group subset-b-008346

This grouped report covers the SELinux `libselinux/src` files assigned to subset `subset-b-008346`. Each file section is bounded by reconciliation markers and titled with the exact source path.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/Makefile -->
# sources/security-integrity/selinux/libselinux/src/Makefile

Purpose: This makefile builds the libselinux C library, static archive, shared object, pkg-config file, and Python/Ruby language bindings. It discovers Python and Ruby build metadata through `python -m sysconfig`, `importlib.machinery`, `pkg-config`, and `RbConfig`, then compiles all non-generated C sources except `audit2why.c` into `libselinux.a` and `libselinux.so.1`.

Important targets and variables: `all`, `pywrap`, `rubywrap`, `install`, `install-pywrap`, `install-rubywrap`, `clean`, and `distclean` are the primary control points. `SRCS`, `OBJS`, and `LOBJS` select C inputs; `DISABLE_X11`, `DISABLE_SHARED`, `ANDROID_HOST`, and `LABEL_BACKEND_ANDROID` change backend coverage. `LD_SONAME_FLAGS` applies soname, version-script, `-z defs`, and RELRO flags on ELF builds. Feature probes add `HAVE_STRLCPY` and `HAVE_REALLOCARRAY`.

Control flow: variable setup detects toolchain, Python/Ruby ABI suffixes, warning flags, and optional backend source filtering. Build targets generate SWIG wrappers, compile PIC and non-PIC objects, link the archive/shared library, generate `libselinux.pc`, and install artifacts into `DESTDIR`-qualified library/include/runtime paths.

State and persistence: persistent outputs are `libselinux.a`, `libselinux.so.1`, `libselinux.so`, generated SWIG files, wheel contents, Ruby extension, and `libselinux.pc`. It never mutates runtime SELinux state.

Dependencies and integration: depends on compiler, archive tools, `pkg-config`, Python, Ruby, SWIG, PCRE flags, libsepol, FTS, `dl`, and public headers under `../include`. It integrates with downstream packagers through install paths and pkg-config substitution.

Risks and test signals: the broad `-Werror` profile makes compiler drift visible. Backend filtering must stay aligned with actual source availability. Install rules should be tested with `DESTDIR`, shared/static toggles, Python/Ruby wrapper builds, Android host mode, and Darwin linker behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/audit2why.c -->
# sources/security-integrity/selinux/libselinux/src/audit2why.c

Purpose: `audit2why.c` implements the Python C extension module `audit2why`, which explains why an AVC denial occurred by loading a binary SELinux policy with libsepol, translating contexts/classes/permissions into policy identifiers, and computing denial reasons.

Important APIs/types/functions: exported Python methods are `init`, `analyze`, and `finish`. Module constants include `ALLOW`, `DONTAUDIT`, `TERULE`, `BOOLEAN`, `CONSTRAINT`, `RBAC`, `BOUNDS`, and error codes like `BADSCON`. Internal state is held in global `struct avc_t *avc`, global `sidtab`, `boollist`, and `boolcnt`. `__policy_init()` reads policy, initializes `sepol_policydb_t`, `sepol_handle_t`, booleans, and sidtab. `analyze()` calls `sepol_compute_av_reason_buffer()`. `check_booleans()` temporarily toggles each policy boolean to find changes that would allow access.

Control flow: `init()` refuses repeated initialization, selects an explicit policy path or `selinux_current_policy_path()`, reads policydb, loads booleans, and sets libsepol globals. `analyze()` parses five Python arguments, converts source/target contexts and permissions, computes an access vector decision and reason mask, then returns either a reason constant plus `None`, a constraint string, or a boolean list. `finish()` releases all global policy state.

State and persistence: state is process-global and persists until `finish()` or module teardown. Boolean probing mutates the in-memory policydb and attempts to restore each boolean before continuing. No on-disk policy is modified.

Dependencies and integration: uses Python C API, libsepol policydb/services APIs, libselinux policy path helpers, and raw SELinux context strings. It is built as `audit2why.so` by the makefile and consumed by audit analysis tooling.

Risks and test signals: the extension is not reentrant because policy state is global. Boolean probing has many early exits where restoration and object cleanup matter. Tests should cover missing policy, invalid contexts/classes/perms, constraint/RBAC/bounds reasons, boolean-caused allow decisions, repeated init rejection, finish idempotence, and Python reference ownership.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/audit2why.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc.c -->
# sources/security-integrity/selinux/libselinux/src/avc.c

Purpose: `avc.c` implements the userspace SELinux Access Vector Cache. It interns security contexts as `security_id_t`, caches access vector decisions by `(ssid, tsid, class)`, audits decisions, and reacts to policy/enforcing changes through callbacks and status notifications.

Important APIs/types/functions: public APIs include `avc_open()`, `avc_init()`, `avc_destroy()`, `avc_context_to_sid[_raw]()`, `avc_sid_to_context[_raw]()`, `avc_get_initial_sid()`, `avc_has_perm[_noaudit]()`, `avc_compute_create()`, `avc_compute_member()`, callback registration, stats, and security-server update handlers `avc_ss_*`. Core types are `avc_entry`, `avc_node`, `avc_cache`, callback nodes, and the `sidtab`.

Control flow: initialization configures optional memory/log/thread/lock callbacks, allocates locks, initializes fixed cache slots and freelist nodes, sets enforcing state, initializes the SID table, allocates audit buffer, and opens SELinux status mapping. Permission checks first consult an entry reference, then cache, then `security_compute_av_flags_raw()`, inserting the decision if current. Denied bits are allowed in permissive mode or per-domain permissive decisions. Audited events are formatted with class/permission names and supplemental audit callbacks. Policy/enforcement updates reset or patch cache entries and notify registered callbacks.

State and persistence: state is entirely process-local: cache buckets, freelist, callback list, audit buffer, stats, SID table, latest notification sequence, enforcing flag, and running flag. It persists until `avc_destroy()` and is invalidated by status/netlink events.

Dependencies and integration: depends on `selinuxfs` compute APIs, class/permission mapping, `selinux_status_*`, `avc_internal` callbacks, and `avc_sidtab`. Object managers use it through libselinux AVC APIs.

Risks and test signals: cache correctness depends on locking, sequence-number checks, and policyload/setenforce invalidation. The empty `avc_cleanup()` means reclaim behavior is bounded by initial freelist plus reclaim scan. Tests should cover cache hit/miss/ref discard, permissive handling, unknown classes, callback retention for try-revoke, audit output, status-triggered reset, and destroy/reinit.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_internal.c -->
# sources/security-integrity/selinux/libselinux/src/avc_internal.c

Purpose: `avc_internal.c` provides AVC support glue for SELinux netlink/status events. It owns callback-function globals, enforcing/running state, netlink socket lifecycle, and translation of kernel setenforce/policyload notifications into AVC cache resets and user callbacks.

Important APIs/types/functions: global callback pointers include `avc_func_malloc`, `avc_func_log`, thread callbacks, and lock callbacks. Public internal functions include `avc_process_setenforce()`, `avc_process_policyload()`, `avc_netlink_open()`, `avc_netlink_close()`, `avc_netlink_check_nb()`, `avc_netlink_loop()`, `avc_netlink_acquire_fd()`, and `avc_netlink_release_fd()`.

Control flow: setenforce events log the transition, update `avc_enforcing` unless caller fixed it via `AVC_OPT_SETENFORCE`, reset the AVC when moving to enforcing, and call `selinux_netlink_setenforce()`. Policyload events reset cache with the sequence number, flush class cache, and call `selinux_netlink_policyload()`. Netlink open creates a `NETLINK_SELINUX` socket, optionally nonblocking, and binds `SELNL_GRP_AVC`. Receive uses `poll()` and `recvfrom()`, validates kernel origin, length, truncation, and message type, then dispatches supported notification records.

State and persistence: module state is the static netlink `fd`, AVC globals, thread/main-loop flags, and callback function pointers. The socket persists until close, thread exit, or destroy.

Dependencies and integration: uses Linux netlink headers, `selinux_netlink.h`, `selinux_status` consumers, AVC cache control functions from `avc.c`, and application main loops that can acquire the netlink fd.

Risks and test signals: spoofed/truncated netlink packets must be rejected. Nonblocking polling must return `EWOULDBLOCK` cleanly. Tests should simulate setenforce/policyload messages, malformed `nlmsg_len`, non-kernel `nl_pid`, app-main-loop fd acquisition, and callback failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_internal.h -->
# sources/security-integrity/selinux/libselinux/src/avc_internal.h

Purpose: This header defines AVC-internal callback plumbing, global state declarations, logging helpers, lock/memory/thread adapters, cache-stat macros, audit-buffer sizing, and internal cache-control prototypes.

Important APIs/types/functions: `set_callbacks()` installs optional user-supplied memory, log, audit, thread, and lock callbacks. Inline wrappers `avc_malloc()`, `avc_free()`, `avc_create_thread()`, `avc_alloc_lock()`, and lock operations fall back to libc/no-op behavior. `avc_log` and `avc_suppl_audit()` route messages through AVC-specific callbacks or libselinux defaults. Prototypes expose `avc_ss_grant`, revoke/reset, and audit mask updates.

Control flow: callers initialize function pointers once through `set_callbacks()`, then all AVC implementation code uses wrapper functions rather than direct malloc/free/log/lock calls. `AVC_CACHE_STATS` gates whether stat counters are incremented or compiled to no-ops.

State and persistence: declares external callback pointers, `avc_prefix`, `avc_running`, `avc_enforcing`, and `avc_setenforce`. The header itself has no persistent storage but centralizes access to process-global AVC state.

Dependencies and integration: includes public `selinux/avc.h`, `callbacks.h`, and libselinux logging. It is included by `avc.c`, `avc_internal.c`, and SID table code.

Risks and test signals: callback pointer combinations can produce partial customization, so tests should cover default operation and all supplied callback classes. Lock callbacks may be no-ops, making thread-safety application-dependent. Compile tests with and without `AVC_CACHE_STATS` are useful.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_sidtab.c -->
# sources/security-integrity/selinux/libselinux/src/avc_sidtab.c

Purpose: `avc_sidtab.c` implements the userspace AVC SID table: a hash table that interns raw security context strings and returns stable `security_id_t` pointers for cache keys and audit formatting.

Important APIs/types/functions: `sidtab_init()` allocates buckets, `sidtab_context_lookup()` finds an existing `security_id`, `sidtab_context_to_sid()` inserts if missing, `sidtab_sid_stats()` reports bucket utilization, and `sidtab_destroy()` frees contexts and nodes. `sidtab_hash()` is a djb2-style hash masked to 128 buckets.

Control flow: lookups hash a context and traverse a bucket chain by `strcmp`. Insertions allocate a node through `avc_malloc()`, duplicate the context with `strdup()`, assign a monotonically increasing integer ID, and prepend to the selected bucket.

State and persistence: each table owns allocated bucket array and nodes. Entries persist until `sidtab_destroy()`, and pointers are used by the AVC cache, so they must not be freed during live cache operation.

Dependencies and integration: uses `avc_internal` allocation wrappers, `freecon()` for duplicated contexts, and public AVC `struct security_id`.

Risks and test signals: failure paths must leave `*sid = NULL` on insert failure. The table stops at `UINT_MAX - 1` entries. Tests should cover duplicate lookup returning identical pointer, collision chains, stats formatting, allocation failure, and destroy with null/empty tables.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_sidtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_sidtab.h -->
# sources/security-integrity/selinux/libselinux/src/avc_sidtab.h

Purpose: This header declares the SID table data structures and operations used by the AVC implementation to map context strings to process-local security IDs.

Important APIs/types/functions: `struct sidtab_node` embeds `struct security_id` and a next pointer. `struct sidtab` owns a bucket array and entry count. Constants define a 7-bit, 128-bucket table. Function declarations cover init, lookup, context-to-SID insertion, stats, and destroy.

Control flow: there is no executable logic here, but the structure layout is directly consumed by `avc_sidtab.c` and by `avc.c` through opaque `security_id_t` pointers.

State and persistence: the header defines the shape of process-local persisted SID table state. Entries are not kernel SIDs; they are stable in-memory handles.

Dependencies and integration: includes public `selinux/selinux.h` and `selinux/avc.h`, so it is tied to libselinux public SID types.

Risks and test signals: ABI risk is internal, but pointer stability and bucket sizing affect AVC cache behavior. Tests should verify that consumers never treat the integer `id` as a kernel-visible SID.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/avc_sidtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/booleans.c -->
# sources/security-integrity/selinux/libselinux/src/booleans.c

Purpose: `booleans.c` implements SELinux boolean discovery, reading pending/active values, setting pending values, and committing them through `selinuxfs`. It also supports boolean-name substitutions through `booleans.subs_dist`.

Important APIs/types/functions: exported functions include `security_get_boolean_names()`, `security_get_boolean_pending()`, `security_get_boolean_active()`, `security_set_boolean()`, `security_commit_booleans()`, `security_set_boolean_list()`, deprecated `security_load_booleans()`, and `selinux_boolean_sub()`. `bool_open()` centralizes path construction and substitution fallback.

Control flow: names are read by `scandir(selinux_mnt/booleans)` with dot entries filtered. Boolean values are read as three-byte strings where the first byte is active and second is pending. Setting validates name/value, opens the boolean file, writes `"0\0"` or `"1\0"`, and commit writes to `/commit_pending_bools`. List setting applies each value then commits, rolling back earlier booleans to active values on set failure.

State and persistence: changes are persisted only after `security_commit_booleans()`. Pending writes live in kernel SELinux boolean state. The disabled build path compiles stubs returning `-1`.

Dependencies and integration: depends on `selinux_mnt`, path helpers, kernel `selinuxfs` boolean files, and `SELboolean` public API.

Risks and test signals: names with `/` are rejected to prevent path traversal. Rollback can itself fail silently. Permanent flag deliberately returns error after commit because it is no longer used. Tests should cover substitutions, ENOENT, disabled build stubs, active/pending parsing, list rollback, and commit failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/booleans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/callbacks.c -->
# sources/security-integrity/selinux/libselinux/src/callbacks.c

Purpose: `callbacks.c` stores global libselinux callback hooks for logging, supplemental audit, context validation, setenforce notification, and policyload notification, with default implementations.

Important APIs/types/functions: exported APIs are `selinux_set_callback()` and `selinux_get_callback()`. Global callback pointers are `selinux_log_direct`, `selinux_audit`, `selinux_validate`, `selinux_netlink_setenforce`, and `selinux_netlink_policyload`. `log_mutex` protects log output.

Control flow: defaults log to `stderr`, no-op audit/netlink callbacks, and validate contexts through `security_check_context()` unless building host tools. `selinux_set_callback()` switches by public callback type and replaces the matching pointer. `selinux_get_callback()` returns the current pointer or sets `EINVAL` for unknown types.

State and persistence: callback state is process-global and persists until replaced or process exit. No filesystem state is modified.

Dependencies and integration: used by label validation, AVC event forwarding, and logging across libselinux. The header macro `selinux_log()` wraps these pointers with mutex and errno preservation.

Risks and test signals: global callback mutation is not guarded by its own setter lock. Callback implementations can change library behavior broadly. Tests should cover default validation with and without `BUILD_HOST`, unknown callback type errno, logging errno preservation, and callback replacement.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/callbacks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/callbacks.h -->
# sources/security-integrity/selinux/libselinux/src/callbacks.h

Purpose: This header declares libselinux callback globals and defines the thread-safe `selinux_log()` macro used throughout the library.

Important APIs/types/functions: declarations cover log, audit, validation, setenforce, and policyload callback pointers plus `log_mutex`. The `selinux_log(type, ...)` macro saves `errno`, locks `log_mutex`, calls `selinux_log_direct`, unlocks, and restores `errno`.

Control flow: code using `selinux_log()` gets serialized output and avoids accidental errno clobbering from logging callbacks. Other callback pointers are consumed directly by label and AVC paths.

State and persistence: exposes process-global callback pointer state owned by `callbacks.c`.

Dependencies and integration: includes public libselinux headers and internal `selinux_internal.h`; used by most modules for diagnostics and validation.

Risks and test signals: callback direct calls outside `selinux_log()` will not get errno preservation. Tests should verify the macro is safe when callback writes to errno and that recursive logging does not deadlock under callback behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/callbacks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/canonicalize_context.c -->
# sources/security-integrity/selinux/libselinux/src/canonicalize_context.c

Purpose: Implements context canonicalization through the kernel SELinux `/context` interface, with public translated and raw variants.

Important APIs/types/functions: `security_canonicalize_context_raw()` writes a raw context to `selinux_mnt/context`, reads back the canonical value, and duplicates it. `security_canonicalize_context()` converts translated input to raw, calls raw canonicalization, then converts the output back to translated form.

Control flow: the raw path requires `selinux_mnt`, opens `context` read-write, allocates a page-sized buffer, copies input with overflow checking, writes NUL-terminated context, clears the buffer, and reads the response. If read fails with `EINVAL`, it falls back to the original context for kernels lacking the extended canonicalization interface.

State and persistence: no persistent state is changed; kernel policy is queried through a transient file descriptor.

Dependencies and integration: depends on `selinux_page_size`, `selinux_mnt`, raw/translated context conversion helpers, and `freecon()`.

Risks and test signals: page-size limits and `strlcpy` overflow are the primary input-size boundary. Tests should cover missing selinuxfs, long contexts, kernel `EINVAL` fallback, conversion failures, and successful raw/trans round trip.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/canonicalize_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/checkAccess.c -->
# sources/security-integrity/selinux/libselinux/src/checkAccess.c

Purpose: Provides high-level access checking APIs around the AVC and a compatibility password-access check.

Important APIs/types/functions: `selinux_check_access()` checks one permission by source/target context strings, class name, permission name, and auxiliary audit data. `selinux_check_passwd_access()` and `checkPasswdAccess()` delegate to `selinux_check_passwd_access_internal()`. A `pthread_once_t` initializes the AVC once.

Control flow: the first access check initializes SELinux state and opens the AVC if SELinux is enabled. If SELinux is disabled, access is allowed. Otherwise contexts are interned with `avc_context_to_sid()`, status updates are processed, class and permission strings are resolved, unknowns are allowed only when `security_deny_unknown() == 0`, and `avc_has_perm()` performs the decision and audit. Password access checks current previous context, computes access on the `passwd` class, and permits on permissive mode.

State and persistence: uses process-global once state, AVC cache, and current SELinux status. It does not persist policy changes.

Dependencies and integration: integrates public libselinux callers with AVC, status mapping, class/permission mapping, `getprevcon_raw()`, and enforcement-state reads.

Risks and test signals: unknown-class handling must preserve errno when denial is required. Tests should cover disabled SELinux, AVC init failure, unknown class/permission with deny_unknown both ways, permissive password access, and audit auxiliary data propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/checkAccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/check_context.c -->
# sources/security-integrity/selinux/libselinux/src/check_context.c

Purpose: Validates whether a context is accepted by the current kernel SELinux policy through `selinuxfs/context`.

Important APIs/types/functions: `security_check_context_raw()` writes a raw context to `selinux_mnt/context`. `security_check_context()` converts translated input to raw before validation.

Control flow: raw validation requires `selinux_mnt`, opens `/context` read-write, writes the NUL-terminated context, closes the descriptor, and returns success if the write succeeded. The translated wrapper handles conversion and freeing.

State and persistence: no persistent state is changed; the kernel validates input against loaded policy.

Dependencies and integration: used as the default validation callback for label lookups and context-list filtering.

Risks and test signals: write length includes the terminating NUL. Tests should cover missing mount, invalid contexts, conversion failure, and descriptor close on write failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/check_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/checkreqprot.c -->
# sources/security-integrity/selinux/libselinux/src/checkreqprot.c

Purpose: Reads the kernel SELinux `checkreqprot` setting.

Important APIs/types/functions: `security_get_checkreqprot()` opens `selinux_mnt/checkreqprot`, reads a small text integer, parses it with `sscanf`, and returns the value.

Control flow: missing `selinux_mnt`, open failures, read failures, and parse failures all return `-1`.

State and persistence: this is read-only kernel state.

Dependencies and integration: depends on `selinux_mnt` and the legacy `checkreqprot` selinuxfs node.

Risks and test signals: tests should cover absent node on newer systems, non-integer contents, and normal `0`/`1` values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/checkreqprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_av.c -->
# sources/security-integrity/selinux/libselinux/src/compute_av.c

Purpose: Computes SELinux access vector decisions by querying the kernel policy through `selinuxfs/access`.

Important APIs/types/functions: exports `security_compute_av_flags_raw()`, `security_compute_av_raw()`, `security_compute_av_flags()`, and `security_compute_av()`. The flags variants preserve `avd->flags`; compatibility variants omit flags from public result copying.

Control flow: raw computation opens `/access`, formats `scon tcon class requested` using `unmap_class()` and `unmap_perm()`, writes the request, reads a response containing allowed/decided/auditallow/auditdeny/seqno/optional flags, then maps returned decision permissions back to userspace if a kernel class mapping existed. Public wrappers translate contexts to raw before raw query and free conversions afterward.

State and persistence: read-only kernel policy query; no cache is maintained here.

Dependencies and integration: AVC calls `security_compute_av_flags_raw()` on cache misses. Class and permission mapping come from `mapping.h`.

Risks and test signals: page-buffer formatting can overflow, parse may return older five-field responses, and class mapping of unknown userspace classes is subtle. Tests should cover flags presence/absence, unknown class behavior, mapping round trips, long contexts, and kernel read/write failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_create.c -->
# sources/security-integrity/selinux/libselinux/src/compute_create.c

Purpose: Computes a default creation context for a source context, target context, object class, and optional object name by querying `selinuxfs/create`.

Important APIs/types/functions: exports `security_compute_create_name_raw()`, `security_compute_create_raw()`, `security_compute_create_name()`, and `security_compute_create()`. `object_name_encode()` percent-encodes object names for the kernel request format, preserving alnum and selected safe punctuation while mapping space to `+`.

Control flow: raw create computation formats `scon tcon class`, appends encoded object name if supplied, writes to `/create`, reads the resulting raw context, and duplicates it for the caller. Public wrappers translate contexts in and the returned context out.

State and persistence: no persistent state is modified.

Dependencies and integration: AVC `avc_compute_create()` can call the raw API and cache the resulting SID. Mapping uses `unmap_class()`.

Risks and test signals: object-name encoding is length-sensitive and byte-oriented. Tests should cover spaces, percent-encoded bytes, long names, null name, translation failures, and ENAMETOOLONG/EOVERFLOW behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_member.c -->
# sources/security-integrity/selinux/libselinux/src/compute_member.c

Purpose: Computes member contexts through `selinuxfs/member`.

Important APIs/types/functions: `security_compute_member_raw()` queries the kernel using raw contexts and class. `security_compute_member()` translates public contexts before and after the raw query.

Control flow: the raw function validates `selinux_mnt`, opens `/member`, creates a page-sized request of `scon tcon class`, writes it, reads a raw context response, duplicates it, then closes and frees buffers.

State and persistence: stateless kernel query.

Dependencies and integration: used by `avc_compute_member()` to produce a `security_id_t` through the AVC SID table.

Risks and test signals: tests should cover missing mount, context conversion errors, class unmapping, buffer overflow, and response duplication failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_member.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_relabel.c -->
# sources/security-integrity/selinux/libselinux/src/compute_relabel.c

Purpose: Computes relabel contexts through `selinuxfs/relabel`.

Important APIs/types/functions: `security_compute_relabel_raw()` is the raw kernel-query API; `security_compute_relabel()` is the translated public wrapper.

Control flow: raw relabel computation opens `/relabel`, formats `scon tcon class`, writes the request, reads the new raw context, and duplicates it. The public wrapper translates source/target contexts to raw and converts output back to translated form.

State and persistence: no persistent state is changed by this query.

Dependencies and integration: depends on `selinux_mnt`, `selinux_page_size`, `unmap_class()`, and raw/trans context conversion helpers.

Risks and test signals: same page-sized request constraints as other compute APIs. Tests should cover invalid contexts, unsupported class, long request, read/write failure, and output conversion failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_relabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_user.c -->
# sources/security-integrity/selinux/libselinux/src/compute_user.c

Purpose: Implements deprecated user-context computation through `selinuxfs/user`, returning a NULL-terminated array of possible contexts for a user and source context.

Important APIs/types/functions: `security_compute_user_raw()` performs the raw query. `security_compute_user()` translates the source context and each returned raw context. It logs a deprecation warning recommending `get_ordered_context_list()`.

Control flow: raw function formats `scon user`, writes to `/user`, reads a buffer whose first string encodes the count, then walks subsequent NUL-terminated context strings into a heap array. Public wrapper converts every returned element in place, freeing the raw entries.

State and persistence: no persistent state, but it allocates caller-owned arrays freed by `freeconary()`.

Dependencies and integration: uses callbacks logging, `freeconary()`, and SELinuxfs policy service.

Risks and test signals: response parsing assumes a count followed by contiguous NUL strings. Tests should cover malformed counts, short buffers, output conversion failure cleanup, zero contexts, and missing mount.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/compute_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/context.c -->
# sources/security-integrity/selinux/libselinux/src/context.c

Purpose: Provides the public `context_t` object implementation for parsing, inspecting, modifying, and rendering SELinux context strings.

Important APIs/types/functions: `context_new()`, `context_free()`, `context_str()`, `context_to_str()`, getters `context_user_get`, `context_role_get`, `context_type_get`, `context_range_get`, and setters for each component. Internal `context_private_t` stores a cached rendered string plus four components.

Control flow: `context_new()` validates separators and whitespace, requires three or four logical components while allowing MLS range to contain additional colons, duplicates components, and returns a wrapper. `context_str()` frees and rebuilds the cached string from current components. `context_to_str()` returns a fresh string. Setters reject tabs/newlines/carriage returns and reject colon or space except in range.

State and persistence: each context owns heap strings and a cached rendered form. Setters invalidate only the affected component; render functions recreate strings.

Dependencies and integration: included through `context_internal.h` and public `selinux/context.h`; used by login-context selection and customizable type checks.

Risks and test signals: `context_str()` returns an internal pointer invalidated by later mutations. Tests should cover MLS ranges with colons/spaces, invalid whitespace, missing components, setter validation, allocation failure cleanup, and repeated render calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/context_internal.h -->
# sources/security-integrity/selinux/libselinux/src/context_internal.h

Purpose: Internal include shim for the public SELinux context API.

Important APIs/types/functions: it includes `<selinux/context.h>` and introduces no additional declarations.

Control flow: none.

State and persistence: none.

Dependencies and integration: gives internal source files a local include path for `context_t` and context component APIs.

Risks and test signals: minimal risk; compile coverage verifies the include path and public header availability.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/context_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/deny_unknown.c -->
# sources/security-integrity/selinux/libselinux/src/deny_unknown.c

Purpose: Reads the kernel policy setting controlling whether unknown classes or permissions are denied.

Important APIs/types/functions: `security_deny_unknown()` opens `selinux_mnt/deny_unknown`, reads a small integer string, parses it, and returns the value.

Control flow: missing mount, open error, read error, or parse failure returns `-1`.

State and persistence: read-only kernel policy state.

Dependencies and integration: used by high-level access checking to decide whether unknown class/permission names should fail closed or be allowed.

Risks and test signals: tests should cover absent file, malformed content, and both deny/allow configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/deny_unknown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/disable.c -->
# sources/security-integrity/selinux/libselinux/src/disable.c

Purpose: Requests SELinux disablement by writing to `selinuxfs/disable`.

Important APIs/types/functions: `security_disable()` writes `"1"` to `selinux_mnt/disable`.

Control flow: requires `selinux_mnt`, opens the disable node write-only, writes a one-character string, closes, and returns success if write succeeded.

State and persistence: this is a persistent/security-critical kernel state change when supported by the kernel and policy mode.

Dependencies and integration: depends on `selinuxfs` exposing a writable `disable` node.

Risks and test signals: this API has high operational impact. Tests should mock or sandbox the filesystem node, cover missing mount, read-only/permission failure, partial writes, and descriptor close.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/disable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/enabled.c -->
# sources/security-integrity/selinux/libselinux/src/enabled.c

Purpose: Reports whether SELinux and MLS are enabled.

Important APIs/types/functions: `is_selinux_enabled()` checks discovered mount/config state, using Android-specific logic that only requires `selinux_mnt`. `is_selinux_mls_enabled()` reads `selinux_mnt/mls` and returns true only when content is exactly `"1"`.

Control flow: enablement is based on constructor-initialized globals from `init.c`. MLS read retries no EINTR loop around open but does loop read until not interrupted.

State and persistence: reads process-global mount/config discovery and kernel MLS state.

Dependencies and integration: used by high-level access checks and callers deciding whether to perform SELinux work.

Risks and test signals: non-Android builds require both mount and config presence, which can differ in containers. Tests should cover Android/non-Android behavior, missing mount, malformed MLS content, and read interruption.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/enabled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/exception.sh -->
# sources/security-integrity/selinux/libselinux/src/exception.sh

Purpose: Generates SWIG Python exception wrappers for public libselinux integer-returning APIs.

Important APIs/types/functions: shell function `except()` emits a `%exception` block for most functions, translating negative `result` into `PyErr_SetFromErrno(PyExc_OSError)` and `SWIG_fail`. `selinux_file_context_cmp` is explicitly ignored.

Control flow: the script concatenates selected public headers, compiles with `${CC:-gcc}` and `-aux-info` to extract extern int function names, falls back to `gcc` if the configured compiler cannot support `-aux-info`, emits exception wrappers for each extracted function, and removes temporary files.

State and persistence: generated output is `selinuxswig_python_exception.i`; temporary `temp.aux` and `temp.o` are deleted.

Dependencies and integration: invoked by the makefile before Python wrapper builds. Depends on compiler support, public headers, Python/SWIG conventions, and shell/awk.

Risks and test signals: compiler output format changes can break function extraction. Tests should run the target with GCC and Clang fallback, verify ignored functions, and ensure temp files are removed on failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/exception.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/fgetfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/fgetfilecon.c

Purpose: Reads the SELinux file context xattr from an open file descriptor.

Important APIs/types/functions: `fgetfilecon_raw()` reads `security.selinux` and returns a raw context string. `fgetfilecon()` translates it. `fgetxattr_wrapper()` emulates `O_PATH` support through `/proc/self/fd/<fd>` when `fgetxattr()` returns `EBADF`.

Control flow: raw function starts with `INITCONTEXTLEN + 1`, retries with exact xattr size on `ERANGE`, treats zero-length attributes as `ENOTSUP`, and returns the byte count on success. Public wrapper returns translated string length including NUL when translation succeeds.

State and persistence: read-only xattr access; caller owns returned memory.

Dependencies and integration: depends on Linux xattrs, `O_PATH`, `/proc/self/fd`, `XATTR_NAME_SELINUX`, and raw/trans conversion helpers.

Risks and test signals: tests should cover normal fd, O_PATH fd, ERANGE resize, empty xattr, ENOENT-to-EBADF mapping for proc fallback, and translation failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/fgetfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/file_path_suffixes.h -->
# sources/security-integrity/selinux/libselinux/src/file_path_suffixes.h

Purpose: Central macro list of SELinux policy/config file path suffixes.

Important APIs/types/functions: the file is intended for inclusion with an `S_(NAME, suffix)` macro defined by the includer. Entries cover policy binary, contexts directories, file/media/X/db context files, default/failsafe contexts, seusers, translations, secolor, subs files, and service-specific context paths.

Control flow: no logic; inclusion expands the table according to caller-defined macro.

State and persistence: defines canonical relative paths under the SELinux policy root.

Dependencies and integration: used by internal path helper generation in `selinux_internal` code outside this subset.

Risks and test signals: path changes affect many public helper APIs. Tests should cover generated helper strings and compatibility of deprecated aliases such as `BOOLEANS` and `USERS_DIR`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/file_path_suffixes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/freecon.c -->
# sources/security-integrity/selinux/libselinux/src/freecon.c

Purpose: Implements the public deallocator for SELinux context strings returned by libselinux APIs.

Important APIs/types/functions: `freecon(char *con)` simply calls `free(con)`.

Control flow: no special handling beyond libc `free`, so NULL is allowed by libc semantics.

State and persistence: releases caller-owned heap memory.

Dependencies and integration: all APIs returning context strings document `freecon()` as the release method, allowing ABI flexibility even though current implementation is `free`.

Risks and test signals: low risk. Tests should verify callers consistently use `freecon()` for returned contexts and no mismatched allocator is introduced.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/freecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/freeconary.c -->
# sources/security-integrity/selinux/libselinux/src/freeconary.c

Purpose: Frees NULL-terminated arrays of context strings returned by libselinux APIs.

Important APIs/types/functions: `freeconary(char **con)` iterates until a NULL sentinel, frees each element with `free()`, then frees the array.

Control flow: NULL array input returns immediately.

State and persistence: releases caller-owned arrays.

Dependencies and integration: used by user-context APIs and cleanup paths in compute/list functions.

Risks and test signals: arrays must be NULL-terminated. Tests should cover NULL input, empty array, multi-entry arrays, and cleanup after partially built arrays.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/freeconary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/fsetfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/fsetfilecon.c

Purpose: Sets the SELinux file context xattr on an open file descriptor.

Important APIs/types/functions: `fsetfilecon_raw()` sets raw `security.selinux`; `fsetfilecon()` translates input to raw. `fsetxattr_wrapper()` emulates `O_PATH` support via `/proc/self/fd/<fd>` after `EBADF`.

Control flow: raw setter writes `strlen(context) + 1` bytes. If `setxattr` reports `ENOTSUP`, it reads the current context and treats the operation as success if the requested context already matches, preserving the original error otherwise.

State and persistence: modifies file xattr state when supported.

Dependencies and integration: depends on xattr syscalls, `/proc/self/fd`, raw/trans conversion, and `fgetfilecon_raw()` for ENOTSUP equality fallback.

Risks and test signals: high impact because it relabels files. Tests should cover O_PATH fallback, ENOTSUP same-context success, ENOTSUP different-context failure, translation failure, and context string NUL-length write.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/fsetfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_context_list.c -->
# sources/security-integrity/selinux/libselinux/src/get_context_list.c

Purpose: Builds ordered login/default context lists for a user from per-user and global SELinux context configuration, with optional role and MLS level filtering.

Important APIs/types/functions: public APIs include `get_ordered_context_list()`, `get_ordered_context_list_with_level()`, `get_default_context()`, `get_default_context_with_level()`, `get_default_context_with_role()`, and `get_default_context_with_rolelevel()`. Helpers parse context config with `get_context_user()` and fall back through `get_failsafe_context()`.

Control flow: if no source context is supplied, current context is read with `getcon()`. The source context is parsed to role/type/range. Per-user config is tried first, then global default contexts. Each matching line maps partial contexts to full `user:partial` contexts, applies the source MLS range, removes duplicates, and validates candidates through `security_check_context()`. If no reachable contexts are found, the failsafe context file is prefixed with the user.

State and persistence: allocates caller-owned NULL-terminated arrays; reads policy configuration files but does not modify them.

Dependencies and integration: uses context parsing, path helpers, validation callbacks, `freeconary()`, and login/session consumers.

Risks and test signals: parsing accepts partial contexts and has many fallback paths. Tests should cover per-user precedence, global fallback, duplicate suppression, invalid candidate skip, explicit level override, role filtering, failsafe recovery, and malformed files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_context_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_context_list_internal.h -->
# sources/security-integrity/selinux/libselinux/src/get_context_list_internal.h

Purpose: Internal include shim for public get-context-list declarations.

Important APIs/types/functions: includes `<selinux/get_context_list.h>` with no extra declarations.

Control flow: none.

State and persistence: none.

Dependencies and integration: used by `get_context_list.c` to reference public prototypes while keeping local include style.

Risks and test signals: compile coverage is sufficient.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_context_list_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_default_type.c -->
# sources/security-integrity/selinux/libselinux/src/get_default_type.c

Purpose: Looks up a default SELinux type for a role from the default type configuration file.

Important APIs/types/functions: `get_default_type()` opens `selinux_default_type_path()` and calls `find_default_type()`. The helper searches for `role:` at the start of a nonblank trimmed line and duplicates the text after the colon.

Control flow: the parser reads fixed 250-byte lines with `fgets_unlocked()`, trims one trailing byte, skips leading whitespace and blank lines, and reports `EINVAL` if no matching role is found.

State and persistence: read-only configuration lookup; caller owns returned `type`.

Dependencies and integration: uses path helpers and public `selinux/get_default_type.h`.

Risks and test signals: fixed buffer length can truncate long lines; matching is prefix plus colon. Tests should cover comments/whitespace, missing role, long lines, roles that are prefixes of other roles, and allocation failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_default_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_default_type_internal.h -->
# sources/security-integrity/selinux/libselinux/src/get_default_type_internal.h

Purpose: Internal include shim for default-type API declarations.

Important APIs/types/functions: includes `<selinux/get_default_type.h>` only.

Control flow: none.

State and persistence: none.

Dependencies and integration: supports local compilation of `get_default_type.c`.

Risks and test signals: compile coverage is sufficient.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_default_type_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_initial_context.c -->
# sources/security-integrity/selinux/libselinux/src/get_initial_context.c

Purpose: Reads named initial security contexts from `selinuxfs/initial_contexts`.

Important APIs/types/functions: `security_get_initial_context_raw()` reads a raw context for a name. `security_get_initial_context()` translates the returned raw context.

Control flow: raw function rejects names containing `/`, builds `selinux_mnt/initial_contexts/<name>` with overflow checks, opens read-only, reads up to one page, duplicates the buffer, and returns it.

State and persistence: read-only kernel policy state.

Dependencies and integration: used by `avc_get_initial_sid()` and callers needing kernel initial SIDs.

Risks and test signals: path traversal prevention is important. Tests should cover slash rejection, long names, missing initial context, empty reads, and translation failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/get_initial_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getenforce.c -->
# sources/security-integrity/selinux/libselinux/src/getenforce.c

Purpose: Reads current SELinux enforcing mode from `selinuxfs/enforce`.

Important APIs/types/functions: `security_getenforce()` returns booleanized parsed integer value.

Control flow: opens the enforce file, reads up to 19 bytes, parses an integer with `sscanf`, and returns `!!enforce`.

State and persistence: read-only kernel state.

Dependencies and integration: AVC initialization and password-access checks use it to determine permissive behavior.

Risks and test signals: tests should cover missing mount, unreadable file, malformed content, and nonzero values mapping to `1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getenforce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/getfilecon.c

Purpose: Reads a path's SELinux file context xattr following symlinks.

Important APIs/types/functions: `getfilecon_raw()` calls `getxattr()` for `security.selinux`; `getfilecon()` translates the returned raw context.

Control flow: starts with `INITCONTEXTLEN + 1`, retries with exact size after `ERANGE`, treats zero-length attributes as `ENOTSUP`, returns raw byte count on success, and public wrapper returns translated string length plus NUL.

State and persistence: read-only xattr access.

Dependencies and integration: used by file-labeling and restorecon-style callers.

Risks and test signals: tests should cover ERANGE, empty xattr, missing xattr, symlink-following semantics, translation failure, and memory cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getpeercon.c -->
# sources/security-integrity/selinux/libselinux/src/getpeercon.c

Purpose: Retrieves the SELinux security context of a connected socket peer.

Important APIs/types/functions: `getpeercon_raw()` uses `getsockopt(SO_PEERSEC)`. `getpeercon()` translates the raw result.

Control flow: allocates an initial buffer, calls `getsockopt`, resizes to kernel-provided size on `ERANGE`, and returns 0 on success with caller-owned context.

State and persistence: read-only socket metadata.

Dependencies and integration: depends on `SO_PEERSEC` availability and raw/trans conversion.

Risks and test signals: tests should cover connected UNIX sockets, ERANGE resize, unsupported socket types, translation failure, and fallback constant definition for platforms lacking `SO_PEERSEC`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/getpeercon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/init.c -->
# sources/security-integrity/selinux/libselinux/src/init.c

Purpose: Initializes libselinux process-global mount discovery and page size.

Important APIs/types/functions: globals are `selinux_mnt`, `selinux_page_size`, and `has_selinux_config`. Functions include `selinuxfs_exists()`, `fini_selinuxmnt()`, `set_selinuxmnt()`, constructor `init_lib()`, destructor `fini_lib()`, and internal `verify_selinuxmnt()`/`init_selinuxmnt()`.

Control flow: constructor saves errno, records page size, tries default and old SELinux mount paths, checks `/proc/filesystems`, scans `/proc/mounts` for `selinuxfs`, and records only writable selinuxfs mounts. Non-Android builds also record whether SELinux config exists. Destructor frees `selinux_mnt`.

State and persistence: process-global mount string and configuration flag persist for library lifetime. `set_selinuxmnt()` can override the mount path.

Dependencies and integration: all SELinuxfs-backed APIs depend on these globals. Uses `statfs`, `statvfs`, `/proc/filesystems`, and `/proc/mounts`.

Risks and test signals: mount discovery must preserve errno and handle containers/read-only mounts. Tests should cover default mount, old mount, scan fallback, absent selinuxfs support, read-only mount rejection, override behavior, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/is_customizable_type.c -->
# sources/security-integrity/selinux/libselinux/src/is_customizable_type.c

Purpose: Determines whether a context's type appears in the policy's customizable types list.

Important APIs/types/functions: `is_context_customizable()` parses the input context and compares its type to a lazily loaded global `customizable_list`. `customizable_init()` loads `selinux_customizable_types_path()` once.

Control flow: one-time initialization counts lines, rewinds, allocates a NULL-terminated list, strips trailing newline from each line, and stores duplicates. Lookup parses the context, extracts type, scans the list, and returns `1`, `0`, or `-1`.

State and persistence: `customizable_list` is process-global and never freed in this file. It persists after first use.

Dependencies and integration: uses context parser, path helpers, page size, and `__selinux_once`.

Risks and test signals: line counting includes blank/comment lines without filtering. Tests should cover missing file, invalid context, type match/no match, long lines bounded by page size, and allocation failure during list build.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/is_customizable_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label.c -->
# sources/security-integrity/selinux/libselinux/src/label.c

Purpose: Implements the frontend for SELinux labeling backends. It opens backend handles, validates/translates lookup records lazily, exposes lookup, best-match, digest, compare, stats, and close APIs.

Important APIs/types/functions: public functions include `selabel_open()`, `selabel_lookup[_raw]()`, `selabel_lookup_best_match[_raw]()`, `selabel_partial_match()`, digest helpers, `selabel_cmp()`, `selabel_close()`, and `selabel_stats()`. Internal `selabel_handle` function pointers are defined in `label_internal.h`.

Control flow: `selabel_open()` validates backend ID and compiled backend availability, allocates a handle, records validation/digest options, and calls the backend init function. Lookup APIs call backend-specific lookup, then `selabel_fini()` validates raw contexts and optionally lazily translates them under per-record lock with atomics. Digest setup allocates SHA1 storage and specfile list when requested.

State and persistence: each handle owns backend data, spec file path, and optional digest state. Lookup records cache validation and translated context strings until close.

Dependencies and integration: dispatches to file, media, X, DB, Android property/service backends depending on compile flags. Uses global validation callback and raw/trans context conversion.

Risks and test signals: lazy validation/translation must be thread-safe. Tests should cover unsupported backends, disabled backend `ENOTSUP`, digest option, raw vs translated lookups, lookup best match, compare incompatible handles, and close cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_backends_android.c -->
# sources/security-integrity/selinux/libselinux/src/label_backends_android.c

Purpose: Implements Android property and service label backends for `selabel_open()`.

Important APIs/types/functions: `selabel_property_init()` and `selabel_service_init()` share parsing/init/close/stats code but install different lookup functions. `spec_t` pairs a property/service key with a lookup record. `cmp()` sorts wildcard entries after concrete entries and longer keys first.

Control flow: init requires `SELABEL_OPT_PATH`, opens a regular file, makes two passes to count then populate specs, validates contexts if requested, checks duplicate keys, sorts specs, records digest, and installs lookup callbacks. Property lookup performs prefix match or `*`; service lookup performs exact match or `*`.

State and persistence: backend handle owns a sorted spec array and raw/translated contexts. Digest state is stored in the parent handle.

Dependencies and integration: Android builds enable these backends through makefile flags; frontend validation and translation are handled by `label.c`.

Risks and test signals: wildcard and prefix ordering are security-sensitive. Duplicate different-context keys are errors. Tests should cover property longest-prefix behavior, service exact behavior, wildcard fallback, duplicate detection, invalid context validation, empty files, and digest generation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_backends_android.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_db.c -->
# sources/security-integrity/selinux/libselinux/src/label_db.c

Purpose: Implements the database-object labeling backend, primarily for SE-PostgreSQL-style object names.

Important APIs/types/functions: `selabel_db_init()` installs `db_close`, `db_lookup`, and `db_stats`. `spec_t` contains lookup record, wildcard key, database object type, and match count. `process_line()` maps strings like `db_table`, `db_column`, and `db_procedure` to `SELABEL_DB_*` constants.

Control flow: initialization parses `SELABEL_OPT_PATH` or default `selinux_sepgsql_context_path()`, verifies a regular file, grows a flexible `catalog_t` array while reading lines, ignores malformed/comment-only lines with warnings, records digest, and stores `rec->spec_file`. Lookup scans in file order for matching type and `fnmatch()` key.

State and persistence: per-handle catalog persists until close; match counts support stats. No config is modified.

Dependencies and integration: frontend handles validation/translation; backend depends on path helpers, `fnmatch`, and database label constants.

Risks and test signals: lookup order is first-match, so spec file ordering matters. Tests should cover every type string, wildcard matching, malformed lines, non-regular files, catalog growth, digest, and stats counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_file.c -->
# sources/security-integrity/selinux/libselinux/src/label_file.c

Purpose: Implements the file-context labeling backend. It loads text or compiled `file_contexts` data into a stem tree of literal and regex specs, supports substitutions, lookup, partial-match digesting, stats, and handle comparison.

Important APIs/types/functions: entrypoint `selabel_file_init()` installs close/stats/lookup/partial/digest/best-match/cmp callbacks. Major internals include `process_text_file()`, `load_mmap()`, `merge_mmap_spec_nodes()`, `process_file()`, substitution init/apply helpers, `lookup_all()`, `lookup_check_node()`, `lookup_best_match()`, `hash_all_partial_matches()`, `cmp()`, and `free_spec_node()`. Data structures are from `label_file.h`: `spec_node`, `literal_spec`, `regex_spec`, `saved_data`, and `mmap_area`.

Control flow: init parses `SELABEL_OPT_PATH`, `SUBSET`, and `BASEONLY`, loads substitution files, then loads base, optional homedirs, and local file contexts. Each source is opened as newest text/bin candidate, with fallback to oldest if processing fails. Text lines are parsed by `process_line()` into literal or regex specs and inserted into a bounded-depth stem tree. Compiled files are mmaped, validated for magic/version/regex version/architecture, loaded into tree nodes, and merged. Lookups normalize duplicate/trailing slashes, apply substitutions, find the deepest stem node, prefer literal matches, then regex matches in reverse input order and parent precedence, honoring file kind and `<<none>>`.

State and persistence: handle owns tree allocations, mmap areas, substitutions, digest, match flags, and lazily compiled regex data. It reads but does not modify spec files; partial-match digest compares with `security.sehash` xattr.

Dependencies and integration: depends on regex backend abstraction, SHA1, xattr, file context suffixes, label frontend, and validation callback.

Risks and test signals: high-risk areas are mmap binary parsing bounds, regex lazy compilation, spec priority, substitution order, duplicate detection, and partial-match digest compatibility. Tests should cover text/bin loading, version mismatch fallback, `file_contexts.local` priority, subset filtering, literal vs regex precedence, `<<none>>`, malformed compiled data, compare subset/superset, and restorecon digest behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_file.h -->
# sources/security-integrity/selinux/libselinux/src/label_file.h

Purpose: Defines the file-context backend's data model, compiled-file format constants, file-kind conversion helpers, regex simplification/compilation helpers, dynamic-array growth macro, spec insertion, and line/binary entry readers.

Important APIs/types/functions: key structures include `lookup_result`, `selabel_sub`, `regex_spec`, `literal_spec`, `spec_node`, `mmap_area`, and `saved_data`. Constants define compiled fcontext versions, `RESTORECON_PARTIAL_MATCH_DIGEST`, and `LABEL_FILE_KIND_*`. Helpers include `string_to_file_kind()`, `file_kind_to_string()`, `regex_has_meta_chars()`, `regex_simplify()`, `compare_literal_spec()`, `sort_specs()`, `compile_regex()`, `GROW_ARRAY`, `insert_spec()`, `next_entry()`, and `process_line()`.

Control flow: `process_line()` uses shared `read_spec_entries()` to parse regex, optional type, and context. `insert_spec()` determines literal vs regex, builds stem tree nodes up to `SPEC_NODE_MAX_DEPTH`, applies subset filtering, stores lookup records, validates contexts, and compiles regexes eagerly only in validating mode. `compile_regex()` anchors expressions, limits regex length to below 4096 bytes, and uses atomics plus mutex for once-only compilation.

State and persistence: the structures define all per-handle persistent state for file labeling, including mmap ownership and lazy caches.

Dependencies and integration: includes regex abstraction, callbacks, label internals, and SELinux internals; parts are exposed for fuzzing under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

Risks and test signals: input parsing rejects non-ASCII and oversized entries, but regex complexity remains important. Tests should cover file-kind parsing, escaped literal simplification, unsupported escapes, array growth overflow, prefix filtering, validation failures, lazy compile races, and fuzz-visible functions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_internal.h -->
# sources/security-integrity/selinux/libselinux/src/label_internal.h

Purpose: Defines the internal label-backend interface and shared data structures used by `label.c` and backend implementations.

Important APIs/types/functions: declares backend init functions, `struct selabel_digest`, `struct selabel_lookup_rec`, and `struct selabel_handle` with function pointers for lookup, close, stats, partial match, digest operations, best match, and compare. Declares `selabel_validate()`, `compat_validate()`, `read_spec_entries()`, and digest helpers.

Control flow: no implementation except `COMPAT_LOG` macro, which routes legacy compatibility output to `myprintf` when enabled or to `selinux_log()`.

State and persistence: describes per-handle persistent state: backend ID, validation flag, backend data pointer, spec file path, and optional digest.

Dependencies and integration: all label backends include this header to satisfy the frontend contract.

Risks and test signals: function-pointer optionality drives public API fallbacks. Tests should cover backends missing optional operations and digest structures with multiple spec files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_media.c -->
# sources/security-integrity/selinux/libselinux/src/label_media.c

Purpose: Implements a simple media-context labeling backend keyed by media names.

Important APIs/types/functions: `selabel_media_init()` installs close, lookup, and stats callbacks. `spec_t` stores key, lookup record, and match count. `process_line()` parses `<key> <context>` lines.

Control flow: init selects `SELABEL_OPT_PATH` or `selinux_media_context_path()`, verifies a regular file, performs two passes to count and populate specs, records digest, and generates the hash. Lookup scans for exact key match or `*` fallback and increments match count.

State and persistence: per-handle array of specs and match counters persists until close.

Dependencies and integration: frontend handles validation/translation. Backend uses path helpers, digest helpers, and logging.

Risks and test signals: first-match ordering and wildcard fallback determine security labels. Tests should cover empty file, malformed lines, wildcard fallback, regular-file validation, digest generation, and stats.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_media.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_support.c -->
# sources/security-integrity/selinux/libselinux/src/label_support.c

Purpose: Provides shared label backend helpers for spec-entry parsing and digest generation.

Important APIs/types/functions: `read_spec_entries()` parses whitespace-delimited ASCII entries from a line, returning item count and optional error text. `digest_add_specfile()` appends file or mmap bytes to a digest buffer and records the path. `digest_gen_hash()` computes SHA1 over accumulated bytes.

Control flow: parsing strips trailing newline, skips blank/comment lines, rejects non-ASCII and entries at or above `UINT16_MAX`, and uses varargs to populate caller-provided `char **` outputs. Digest accumulation reallocates a growing buffer, optionally rewinds and reads a `FILE`, or copies from memory, then stores up to `DIGEST_FILES_MAX` paths.

State and persistence: digest state lives in `struct selabel_digest` attached to a label handle. `digest_gen_hash()` frees the accumulated hash buffer after finalization.

Dependencies and integration: used by file, media, X, DB, and Android backends; uses SHA1 implementation from `label_internal.h`.

Risks and test signals: parser ownership on partial failure is caller-managed. Digest overflows and max file count must be tested. Test signals include comments, unterminated final lines, non-ASCII entries, long tokens, file rewind/read failures, and mmap digest input.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_x.c -->
# sources/security-integrity/selinux/libselinux/src/label_x.c

Purpose: Implements the X object labeling backend for properties, extensions, clients, events, selections, and poly variants.

Important APIs/types/functions: `selabel_x_init()` installs close, lookup, and stats callbacks. `process_line()` maps type strings such as `property`, `extension`, `client`, `event`, `selection`, `poly_property`, and `poly_selection` to `SELABEL_X_*` constants. Lookup uses `fnmatch()`.

Control flow: init selects `SELABEL_OPT_PATH` or default `selinux_x_context_path()`, verifies a regular file, performs two-pass count/populate parsing, records digest, and generates hash. Lookup scans specs for matching type and pattern, then returns the record and increments matches.

State and persistence: per-handle spec array and match counts persist until close.

Dependencies and integration: optional backend controlled by `NO_X_BACKEND`; frontend handles context validation and translation.

Risks and test signals: invalid type strings are skipped, not fatal. Tests should cover every supported type, wildcard matching, malformed lines, optional backend disablement, digest, and stats.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/label_x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lgetfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/lgetfilecon.c

Purpose: Reads a path's SELinux file context xattr without following symlinks.

Important APIs/types/functions: `lgetfilecon_raw()` uses `lgetxattr()` for `security.selinux`; `lgetfilecon()` translates the raw context.

Control flow: mirrors `getfilecon_raw()` with initial buffer, `ERANGE` resize, empty xattr mapped to `ENOTSUP`, and translated length return in the public wrapper.

State and persistence: read-only xattr access.

Dependencies and integration: used for symlink-aware labeling tools where the link's own label matters.

Risks and test signals: tests should cover symlink vs target behavior, ERANGE, empty xattr, missing xattr, and translation failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lgetfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/libselinux.pc.in -->
# sources/security-integrity/selinux/libselinux/src/libselinux.pc.in

Purpose: Template for the installed pkg-config metadata for libselinux.

Important APIs/types/functions: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package `Name`, `Description`, `Version`, project URL, private requirements, linker flags, and Cflags. Placeholders `@prefix@`, `@libdir@`, `@includedir@`, `@VERSION@`, and `@PCRE_MODULE@` are substituted by the makefile.

Control flow: no runtime logic. Makefile target `libselinux.pc` runs `sed` substitutions.

State and persistence: installed `.pc` file guides downstream builds.

Dependencies and integration: consumers use it via `pkg-config --cflags --libs libselinux`; `Requires.private` exposes static-link dependencies on libsepol and the regex module.

Risks and test signals: packaging tests should verify substituted paths, version, private requirements, and that shared vs static link consumers receive correct flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/libselinux.pc.in -->
