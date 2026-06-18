# Research: subset-b-005921

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stop_machine.h -->
# sources/distributed-fs/ceph-client/include/linux/stop_machine.h

Purpose: declares the kernel stop-machine and per-CPU stopper interfaces used when code must run with selected CPUs monopolized or the whole machine quiesced.

Important APIs and types: `cpu_stop_fn_t` is the non-sleeping callback signature. `struct cpu_stop_work` is either queued stopper work on SMP or a `work_struct` fallback on UP. Public entry points include `stop_one_cpu()`, `stop_two_cpus()`, `stop_one_cpu_nowait()`, `stop_machine()`, `stop_machine_cpuslocked()`, `stop_core_cpuslocked()`, and `stop_machine_from_inactive_cpu()`. SMP-only helpers park/unpark stoppers and print stopper diagnostics.

Control flow: callers submit a callback and argument for execution on target CPUs. SMP builds use preallocated per-CPU stopper resources and, for `stop_machine()`, schedule stopper threads that run with interrupts disabled while other CPUs are prevented from useful progress. UP/non-hotplug fallbacks run the function locally with preemption or interrupts disabled.

State and persistence: no persistent state is owned by the header. Runtime state lives in stopper work queues, CPU hotplug state, and preallocated per-CPU stopper resources.

Dependencies and integration points: integrates with CPU hotplug locking, cpumasks, SMP/preemption control, workqueues for UP fallback, and task diagnostics. It is used by high-risk kernel mutation paths such as CPU hotplug, text patching, and synchronization fallbacks.

Risks and test signals: risks are deadlock or latency spikes from sleeping callbacks, misuse outside `cpus_read_lock()` for the cpuslocked variants, offline CPU targeting, and assumptions that stop-machine calls serialize globally. Test signals include SMP/UP builds, CPU hotplug stress, lockdep with raw spinlocks, latency tracing, and fault injection around offline targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stop_machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string.h -->
# sources/distributed-fs/ceph-client/include/linux/string.h

Purpose: provides the kernel's central string and memory helper declarations, safer copy macros, user-memory duplication helpers, allocation wrappers, command-line parsers, fortify integration, and compile-time checked conversions between C strings and fixed byte arrays.

Important APIs and types: user-copy helpers include `strndup_user()`, `memdup_user()`, `vmemdup_user()`, `memdup_user_nul()`, and overflow-checked array wrappers. Core APIs cover libc-like `str*` and `mem*` operations, `strscpy()`/`strscpy_pad()`, `mem_is_zero()`, `kstrdup*()`, `kmemdup*()`, `argv_split()`, option parsing, `sysfs_streq()`, `match_string()`, binary printf helpers, `memory_read_from_buffer()`, `memzero_explicit()`, `kbasename()`, `memcpy_and_pad()`, `strtomem*()`, `memtostr*()`, `memset_after()`, `memset_startat()`, `str_has_prefix()`, `strstarts()`, and `strends()`.

Control flow: this is mostly declarative and inline/macro-driven. Callers select arch-optimized implementations through `asm/string.h`, then fall back to generic declarations when `__HAVE_ARCH_*` is absent. Safer macros use compile-time object-size, array, C-string, and non-string checks before dispatching to implementations.

State and persistence: no global state is stored here. Memory allocation helpers return kernel allocations owned by callers; `memzero_explicit()` intentionally creates a compiler-visible barrier so sensitive stack or heap data is actually cleared.

Dependencies and integration points: depends on compiler attributes, overflow checks, UAPI string definitions, fortify support, allocation hooks, sysfs semantics, command-line parsing, and arch string routines. It is used across nearly every kernel subsystem.

Risks and test signals: risks include incorrect buffer size inference, overlapping string copies, nonstring arrays treated as C strings, missed overflow checks, fortify false positives/negatives, and optimized-away security clears. Test signals include `CONFIG_FORTIFY_SOURCE`, KASAN/UBSAN, compile-time object-size diagnostics, string selftests, sysfs parser tests, and architecture build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string_choices.h -->
# sources/distributed-fs/ceph-client/include/linux/string_choices.h

Purpose: centralizes common boolean-to-literal string choices so diagnostics and status messages use consistent spelling and can share deduplicated string constants.

Important APIs and types: inline helpers include `str_assert_deassert()`, `str_enable_disable()`, `str_enabled_disabled()`, `str_hi_lo()`, `str_high_low()`, `str_input_output()`, `str_on_off()`, `str_read_write()`, `str_true_false()`, `str_up_down()`, and `str_yes_no()`. Each has an inverse macro such as `str_disable_enable()` or `str_no_yes()`. `str_plural(size_t num)` returns `""` for one and `"s"` otherwise.

Control flow: callers pass a boolean and receive a pointer to a static string literal. Inverse macros negate the boolean and reuse the forward helper.

State and persistence: there is no runtime state or allocation; all results point to string literals.

Dependencies and integration points: depends only on `linux/types.h`. It integrates with printk, sysfs, trace, and driver status formatting code.

Risks and test signals: risks are semantic mismatch when a subsystem's true/false sense differs from the helper name and English-only pluralization limits. Test signals are mostly compile coverage and review of log/sysfs output for expected wording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string_choices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string_helpers.h -->
# sources/distributed-fs/ceph-client/include/linux/string_helpers.h

Purpose: declares higher-level string formatting, parsing, escaping, unescaping, case conversion, and quotable duplication helpers used by drivers and core code.

Important APIs and types: `string_is_terminated()` checks bounded NUL termination. `enum string_size_units` selects SI or binary scaling and output modifiers. Public functions include `string_get_size()`, `parse_int_array()`, `parse_int_array_user()`, `string_unescape()`, `string_escape_mem()`, `kstrdup_quotable*()`, `kstrdup_and_replace()`, `kasprintf_strarray()`, `kfree_strarray()`, and `devm_kasprintf_strarray()`. Flag sets define escape and unescape policies such as `ESCAPE_SPACE`, `ESCAPE_NP`, `ESCAPE_HEX`, and `UNESCAPE_OCTAL`.

Control flow: callers select escape/unescape flags, then either write into a caller buffer or duplicate into newly allocated strings. Inline wrappers provide in-place unescape and common "any non-printable" escaping. `string_upper()` and `string_lower()` copy while converting until the source NUL is copied.

State and persistence: no module state is owned here. Allocation helpers return caller-owned or devm-managed arrays/strings.

Dependencies and integration points: depends on ctype, bit helpers, core string APIs, device management, task/file formatting, and user-copy parsing. It is widely used in sysfs/debug formatting and command parsers.

Risks and test signals: risks include output truncation, incorrect escape flag combinations, in-place unescape aliasing mistakes, user buffer faults, and ownership confusion for allocated arrays. Test with string helper selftests, sysfs/debugfs inputs, user-copy fault injection, and KASAN leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/string_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stringhash.h -->
# sources/distributed-fs/ceph-client/include/linux/stringhash.h

Purpose: defines non-cryptographic byte-string hashing helpers optimized for pathname components and dcache-style lookup.

Important APIs and types: `init_name_hash(salt)` seeds a hash, `partial_name_hash()` updates it one byte at a time, and `end_name_hash()` folds it to 32 bits with `hash_long()`. `full_name_hash()` hashes a byte range, and `hashlen_string()` returns a packed hash/length value. `hashlen_hash()`, `hashlen_len()`, and `hashlen_create()` manipulate the packed `u64`.

Control flow: simple callers may stream characters through `partial_name_hash()` and finalize with `end_name_hash()`. Faster implementations can use `full_name_hash()`/`hashlen_string()`, which may vary with architecture and configuration.

State and persistence: no state is kept here; callers supply salt and input. The file explicitly warns that hashes are not stable across versions, architectures, or boots and are not collision-resistant.

Dependencies and integration points: depends on `linux/hash.h` and compiler purity attributes. It integrates with VFS/dcache and server auth hashing through `svcauth.h`.

Risks and test signals: risks include treating values as persistent on-disk/network identifiers, using them for adversarial security boundaries, or mixing case/encoding incorrectly. Test signals include dcache/hash distribution tests, boot-to-boot non-persistence assumptions, and collision stress under long and short names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stringhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stringify.h -->
# sources/distributed-fs/ceph-client/include/linux/stringify.h

Purpose: provides two-level preprocessor stringification so macro arguments expand before being converted to string literals.

Important APIs and types: `__stringify_1(x...)` performs raw `#x` stringification. `__stringify(x...)` expands macro arguments first by calling `__stringify_1`. `FILE_LINE` concatenates `__FILE__`, a colon, and the current `__LINE__`.

Control flow: all behavior happens at preprocessing time. There is no generated runtime control flow beyond string literal use.

State and persistence: no runtime state or allocation.

Dependencies and integration points: consumed by assertions, section names, generated metadata, logging, and compile-time diagnostics.

Risks and test signals: risks are mostly macro-expansion surprises and accidental use where runtime formatting is needed. Test signals are compile-time checks that generated literals match expected macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stringify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sungem_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/sungem_phy.h

Purpose: declares the PHY abstraction used by the Sun GEM Ethernet driver family, including MDIO callbacks, PHY operation tables, probed PHY instance state, and model-specific MII register constants.

Important APIs and types: `struct mii_phy_ops` defines init, suspend, autonegotiation, forced setup, link polling, link readout, and fiber enable hooks. `struct mii_phy_def` describes supported PHY IDs, masks, ethtool feature bits, autonegotiation behavior, name, and ops. `struct mii_phy` stores current advertising/autoneg/speed/duplex/pause state plus host `net_device`, MDIO read/write callbacks, and platform data. `sungem_phy_probe()` fills a caller-provided instance. Register constants cover Broadcom BCM5201/5221/5241/5400 and Marvell 88E1011 details.

Control flow: the network driver initializes MDIO access in `struct mii_phy`, calls `sungem_phy_probe()`, then invokes ops to configure autonegotiation or forced speed and poll/read link state.

State and persistence: runtime link configuration is stored in `struct mii_phy`; persistent hardware state lives in PHY registers and is rewritten by driver operations.

Dependencies and integration points: integrates with `net_device`, ethtool feature definitions, MDIO register access, and legacy Sun GEM hardware support.

Risks and test signals: risks include stale register bit definitions, wrong PHY ID masks, MDIO callback lifetime, and mismatched pause/duplex reporting. Test with supported PHY models, autoneg and forced modes, suspend/resume, link flap handling, and ethtool reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sungem_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/addr.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/addr.h

Purpose: provides SUNRPC sockaddr presentation conversion declarations plus inline helpers for comparing, copying, and manipulating IPv4/IPv6 RPC peer addresses.

Important APIs and types: external conversion APIs are `rpc_ntop()`, `rpc_pton()`, `rpc_sockaddr2uaddr()`, and `rpc_uaddr2sockaddr()`. Inline helpers include `rpc_get_port()`, `rpc_set_port()`, `rpc_cmp_addr4()`, `rpc_cmp_addr6()`, `rpc_cmp_addr()`, `rpc_cmp_addr_port()`, `rpc_copy_addr()`, and `rpc_get_scope_id()`. Constants define IPv6 universal-address scope delimiters and scope ID string size.

Control flow: callers convert between socket addresses and RPC universal address strings, then use inline helpers to compare address-only or address-plus-port identity. IPv6 comparison accounts for link-local scope IDs when IPv6 is enabled.

State and persistence: no state is stored; helpers operate on caller-supplied `sockaddr` buffers.

Dependencies and integration points: depends on socket, IPv4/IPv6 address types, `struct net`, and optional IPv6 support. It is used by RPC client/server transport setup, rpcbind registration, and multipath address matching.

Risks and test signals: risks include ignoring ports when ports matter, missing IPv6 scope IDs, copying into undersized buffers, and IPv6-disabled fallbacks returning false. Test with IPv4, global IPv6, link-local IPv6, rpcbind universal address parsing, and namespace-aware parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/auth.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/auth.h

Purpose: declares the client-side SUNRPC authentication framework, credential cache objects, auth flavor operations, and transmit/receive wrapping hooks.

Important APIs and types: `struct auth_cred` describes kernel credentials plus optional machine principal. `struct rpc_cred` is refcounted, hash/LRU-linked, RCU-freed credential state with flags such as `RPCAUTH_CRED_UPTODATE` and `RPCAUTH_CRED_NEGATIVE`. `struct rpc_auth` represents an auth handle with slack sizes, flavor, operations, refcount, and credential cache. `struct rpc_authops` creates/destroys auth modules and maps GSS info/flavors. `struct rpc_credops` initializes, marshals, refreshes, validates, wraps, unwraps, and stringifies credentials.

Control flow: RPC client creation calls `rpcauth_create()`, tasks look up credentials via `rpcauth_lookupcred()` or the cache, marshal credentials into `xdr_stream`, refresh stale credentials, and validate reply verifiers. GSS/privacy flavors can wrap requests and unwrap responses.

State and persistence: state is in-memory and refcounted/RCU-managed: auth modules, auth handles, credential cache entries, flags, expiry times, and kernel `cred` references.

Dependencies and integration points: integrates with `rpc_task`, XDR streams, message protocol constants, modules, RCU, uid/gid credentials, UTS nodename sizing, and GSS flavor mapping.

Risks and test signals: risks include stale or negative credentials, refcount/RCU lifetime bugs, auth slack underestimation, async lookup failures, and reencode requirements after refresh. Test with AUTH_NULL, AUTH_UNIX, TLS auth, RPCSEC_GSS, credential expiry, cache pressure, and KASAN/RCU debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/auth_gss.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/auth_gss.h

Purpose: defines RPCSEC_GSS wire structures and client credential/context state shared by SUNRPC GSS authentication code.

Important APIs and types: constants include `RPC_GSS_VERSION` and `MAXSEQ`. `enum rpc_gss_proc` covers data, init, continue-init, and destroy control procedures; `enum rpc_gss_svc` covers none, integrity, and privacy services. Wire structs are `rpc_gss_wire_cred`, `rpc_gss_wire_verf`, and `rpc_gss_init_res`. `struct gss_cl_ctx` tracks refcount, procedure, sequence numbers, locking, local GSS context, wire context, acceptor, window, expiry, and RCU teardown. `struct gss_cred` embeds `rpc_cred` and references the active context or pending upcall.

Control flow: credentials marshal a GSS wire cred and verifier, use upcalls to establish `gss_cl_ctx`, then sequence, sign, encrypt, validate, or destroy contexts depending on procedure and service.

State and persistence: GSS client state is runtime-only but long-lived across RPC tasks until expiry: context handles, sequence counters, upcall timestamps, and principal pointers.

Dependencies and integration points: depends on `auth.h`, `svc.h`, and `gss_api.h`; integrates client RPCSEC_GSS with server request handling and the mechanism-independent GSS layer.

Risks and test signals: risks include sequence wrap/replay handling, context expiry, RCU context replacement, upcall races, and incorrect service selection. Test with krb5 `krb5`, `krb5i`, `krb5p`, context renewal, replay windows, and concurrent RPC load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/auth_gss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/bc_xprt.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/bc_xprt.h

Purpose: declares SUNRPC backchannel transport setup and request management used by protocols such as NFSv4.1 callbacks over an existing client connection.

Important APIs and types: when `CONFIG_SUNRPC_BACKCHANNEL` is enabled, APIs include `xprt_lookup_bc_request()`, `xprt_complete_bc_request()`, `xprt_init_bc_request()`, `xprt_free_bc_request()`, `xprt_setup_backchannel()`, `xprt_destroy_backchannel()`, `xprt_enqueue_bc_request()`, socket-specific `xprt_setup_bc()`, `xprt_destroy_bc()`, `xprt_free_bc_rqst()`, `xprt_bc_max_slots()`, and `xprt_svc_destroy_nullify_bc()`. Inline helpers check or set `sv_bc_enabled`.

Control flow: a transport allocates/prepares backchannel request slots, incoming callback replies are matched by XID, completed, and returned to the preallocation pool. Disabled builds compile to inert setup/destroy helpers.

State and persistence: state is held in `rpc_xprt`, `rpc_rqst`, and `svc_serv` backchannel fields; it is connection lifetime, not persistent.

Dependencies and integration points: integrates `xprt.h`, `sched.h`, `svcsock.h`, NFS callback services, and transport-specific backchannel methods.

Risks and test signals: risks include XID mismatches, preallocated slot leaks, disabled-config behavior drift, and service destruction while callbacks are active. Test with NFSv4.1 callback traffic, backchannel teardown, reconnects, and builds with and without `CONFIG_SUNRPC_BACKCHANNEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/bc_xprt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/cache.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/cache.h

Purpose: defines the generic SUNRPC cache framework used mainly for authentication, identity, and export-related upcall caches.

Important APIs and types: `struct cache_head` supplies hash linkage, expiry, refresh time, refcount, and flags `CACHE_VALID`, `CACHE_NEGATIVE`, `CACHE_PENDING`, and `CACHE_CLEANED`. `struct cache_detail` describes cache-specific operations, hash table, flush time, request/read queues, pipefs/procfs exposure, writer accounting, and network namespace. `struct cache_req` and `struct cache_deferred_req` support delaying requests until an upcall fills an entry. APIs include lookup/update, pipe upcalls, deferred cleanup, `cache_check*()`, purge/flush, per-net create/register/destroy, pipefs registration, sequence iteration, and qword parsing helpers.

Control flow: callers look up a key, check validity, possibly send an upcall over procfs/pipefs, defer the RPC request, then update or mark negative results when user space responds. Expiry uses seconds since boot and flush-time comparisons.

State and persistence: cache entries, queues, writer counts, and timestamps are in-memory and per-cache/per-net. User-space responses can refresh state but nothing here persists across reboot.

Dependencies and integration points: depends on kref, spinlocks, wait queues, procfs, pipefs, net namespaces, and string-to-integer parsing. It supports server auth domains, Unix group caches, and other SUNRPC identity caches.

Risks and test signals: risks include refcount races, expired-but-referenced entries, no-listener stalls, deferred request leaks, boot-time versus wall-clock conversion errors, and namespace unregister ordering. Test with cache upcall daemons, writer close/reopen, negative entries, flush/purge, RCU iteration, and request deferral under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/clnt.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/clnt.h

Purpose: declares the high-level SUNRPC client object, RPC program/procedure descriptors, client creation arguments, and synchronous/asynchronous call APIs.

Important APIs and types: `struct rpc_clnt` holds refs, IDs, task lists, transport pointers, procedure tables, auth/stats/metrics, retry and shutdown policy bits, transport security, RTT/timeout data, pipefs/sysfs/debugfs state, xprt iterator/work, credentials, and task counts. `struct rpc_program`, `rpc_version`, and `rpc_procinfo` describe program numbers, versions, procedure encode/decode callbacks, sizing, timers, stats indexes, and names. `struct rpc_create_args` configures network, address, protocol, auth, timeout, backchannel, credentials, nconnect, and transport security.

Control flow: callers create or clone a client, bind program/version/auth, submit `rpc_call_sync()` or `rpc_call_async()`, then tasks encode arguments, reserve a transport/request, transmit, decode replies, update stats, and release client/transport references. Multipath helpers add, remove, probe, and switch transports.

State and persistence: client state is in-memory and refcounted; metrics and RPC counters live for the client/mount lifetime but are not persistent. Pipefs/sysfs/debugfs objects mirror runtime state.

Dependencies and integration points: integrates RPC scheduler, transports, auth, stats, RTT timers, pipefs, paths, IPv6, and xprt multipathing. NFS and lock managers are primary consumers.

Risks and test signals: risks include client shutdown races, stale RCU transport pointers, retry policy mismatches, auth/transport security drift, multipath trunking mistakes, and wrong procedure sizing. Test with sync/async calls, soft/hard timeouts, rpcbind autobind, transport switching, nconnect, backchannel, and per-net cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/clnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/debug.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/debug.h

Purpose: provides SUNRPC debug masks, conditional debug printing macros, sysctl hooks, and debugfs registration APIs.

Important APIs and types: global masks are `rpc_debug`, `nfs_debug`, `nfsd_debug`, and `nlm_debug`. `dprintk()` and `dprintk_rcu()` expand through `dfprintk()` and `dfprintk_rcu()` using a local `FACILITY`. Debug-enabled builds use `ifdebug()` and either `trace_printk()` or `printk()`. APIs register sysctl, initialize/exit debugfs, and attach client/transport debugfs directories.

Control flow: when `CONFIG_SUNRPC_DEBUG` is enabled, debug masks gate printing and RCU-safe printing acquires an RCU read lock. Disabled builds compile calls to `no_printk()` for format checking without output.

State and persistence: debug masks and debugfs dentries are runtime diagnostic state. No persistent data is stored.

Dependencies and integration points: depends on UAPI debug bit definitions and optional debugfs/trace support. It is included by `sunrpc/types.h` and used throughout SUNRPC.

Risks and test signals: risks include format side effects hidden by disabled debug, trace_printk overhead, missing RCU protection around pointer formatting, and stale debugfs directories. Test with debug config matrices, dynamic mask changes, debugfs mount/unmount, and RCU debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_api.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_api.h

Purpose: defines the mechanism-independent GSS API used by SUNRPC RPCSEC_GSS and the registration interface for concrete mechanisms such as Kerberos.

Important APIs and types: `struct gss_ctx` binds a mechanism to an internal context plus slack/alignment. `struct rpcsec_gss_oid` and `rpcsec_gss_info` represent mechanism OID, QOP, and service. Main APIs import/delete contexts and perform MIC, verify, wrap, and unwrap operations over `xdr_buf`. `struct pf_desc` maps pseudoflavors to QOP/service/domain names. `struct gss_api_mech` describes a mechanism module, OID, name, ops, pseudoflavors, and upcall enctype string. `struct gss_api_ops` is the mechanism callback table.

Control flow: auth code looks up a mechanism by OID/name/pseudoflavor, imports a context token, then dispatches MIC/wrap/unwrap operations through mechanism callbacks. Mechanisms are registered/unregistered dynamically and refcounted via `gss_mech_get()`/`put()`.

State and persistence: mechanism registrations and context internals are in-memory. Imported contexts carry expiration time but are not persistent.

Dependencies and integration points: integrates XDR buffers, RPC message protocol constants, module ownership, auth domains, and crypto mechanisms.

Risks and test signals: risks include mechanism refcount leaks, OID lookup mismatches, wrong slack/alignment for privacy wrapping, and context deletion races. Test with Kerberos pseudoflavors, module unload, MIC verification failures, privacy wrapping, and token import error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_err.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_err.h

Purpose: provides GSS major status code constants and bitfield helpers adapted from the GSSAPI C bindings for SUNRPC security code.

Important APIs and types: `OM_uint32` is the status type. Constants define context flags, credential usage, status code types, indefinite lifetime, success, calling/routine/supplementary field offsets and masks, error testers such as `GSS_ERROR()`, concrete routine errors such as `GSS_S_BAD_MECH`, `GSS_S_NO_CRED`, `GSS_S_CONTEXT_EXPIRED`, and supplementary values such as `GSS_S_CONTINUE_NEEDED`.

Control flow: mechanism and RPCSEC_GSS code compose and test status words using macros. `GSS_ERROR()` checks calling and routine error fields without treating supplementary bits as fatal.

State and persistence: no state; this is a constants-only compatibility header.

Dependencies and integration points: consumed by GSS mechanism code and Kerberos definitions. It mirrors external GSSAPI semantics inside the kernel.

Risks and test signals: risks are numeric drift from GSSAPI expectations, treating supplementary status as fatal, and signed/unsigned misuse. Test with context continuation, expired credentials, bad token handling, and mechanism error translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_krb5.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_krb5.h

Purpose: defines Kerberos-specific constants, token identifiers, checksum/encryption type values, and key usage numbers used by the SUNRPC GSS Kerberos mechanism.

Important APIs and types: size constants include `GSS_KRB5_MAX_KEYLEN`, `GSS_KRB5_MAX_CKSUM_LEN`, `GSS_KRB5_MAX_BLOCKSIZE`, and `GSS_KRB5_TOK_HDR_LEN`. Token constants cover legacy and RFC 4121 MIC/WRAP/initial/response identifiers and flags. `enum sgn_alg` and `enum seal_alg` define older signing/sealing algorithms. Checksum types include HMAC SHA1/SHA2 AES, CMAC Camellia, and RC4-HMAC values. Encryption types include DES, 3DES, AES CTS HMAC SHA1/SHA2, ARCFOUR, Camellia, and unknown. Key usage constants distinguish seal/sign/sequence and initiator/acceptor directions.

Control flow: Kerberos mechanism code parses tokens, selects checksum and encryption algorithms, derives keys using usage constants, and validates/creates MIC or wrap tokens.

State and persistence: no state is stored here; keys and contexts live in mechanism implementation structures.

Dependencies and integration points: depends on kernel crypto skcipher APIs, RPCSEC_GSS client context definitions, and GSS status constants.

Risks and test signals: risks include wrong enctype/checksum mapping, deprecated algorithm handling, direction-specific key usage mistakes, and export-policy-sensitive crypto changes. Test with Kerberos krb5/krb5i/krb5p mounts, AES-SHA1/SHA2 enctypes, token replay, and bad checksum/wrap vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/metrics.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/metrics.h

Purpose: declares per-operation RPC client I/O metrics exposed mainly through procfs for monitoring tools.

Important APIs and types: `RPC_IOSTATS_VERS` is `"1.1"`. `struct rpc_iostats` contains a spinlock, operation/transmission/timeout counters, byte counters, queue/RTT/execution time accumulators, and error status counts, cacheline-aligned. Procfs-enabled APIs allocate/free metrics, count task I/O stats, count timing metrics, and show client stats.

Control flow: RPC tasks update the per-procedure metrics after transmission and completion under the metrics lock. Consumers sample the cumulative counters and compute rates or moving averages externally.

State and persistence: metrics are per-client runtime counters and are intentionally not reset during a mount/client lifetime. Disabled procfs builds compile to no-op stubs.

Dependencies and integration points: integrates with `rpc_task`, `rpc_clnt`, `seq_file`, locks, and ktime. Monitoring tools such as iostat-style consumers rely on stable field meaning.

Risks and test signals: risks include counter lock contention, overflow assumptions in long-lived clients, procfs-disabled behavior differences, and changing field semantics. Test with procfs enabled/disabled, high RPC rates, error paths, and stats output parsers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/msg_prot.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/msg_prot.h

Purpose: defines core ONC RPC protocol constants, auth flavors, reply status values, stream fragment header layout, header sizing, and rpcbind netid/universal-address limits.

Important APIs and types: `rpc_authflavor_t` is a `u32`. Auth flavors include AUTH_NULL, AUTH_UNIX, AUTH_GSS, AUTH_TLS, and GSS pseudoflavors for krb5/krb5i/krb5p and others. Enums cover call/reply types, accepted/denied replies, accept status, reject status, and auth status including RPCSEC_GSS credential/context problems. `rpc_fraghdr` and masks define record-marking for stream transports. Header size macros include `RPC_CALLHDRSIZE`, `RPC_MAX_HEADER_WITH_AUTH`, and reply equivalents. Netid constants cover UDP/TCP/RDMA/SCTP IPv4/IPv6/local.

Control flow: encode/decode code uses these constants to marshal RPC headers, interpret replies, size buffers, and format rpcbind registrations. Stream transports inspect the high fragment bit and 31-bit fragment length.

State and persistence: no state; constants define wire ABI and must remain stable.

Dependencies and integration points: depends on `linux/inet.h` for address length limits and is included by client, auth, transport, and XDR headers.

Risks and test signals: risks include wire incompatibility from numeric changes, fragment length mishandling, auth size underestimation, and rpcbind address truncation. Test with TCP/UDP/RDMA RPC, rpcbind registration, AUTH_GSS/TLS, and malformed fragment headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/msg_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rdma_rn.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/rdma_rn.h

Purpose: declares a small RPC/RDMA removal-notification API used to detect RDMA device/resource removal.

Important APIs and types: `struct rpcrdma_notification` stores an `rn_done` callback and provider index. APIs include `rpcrdma_rn_register()`, `rpcrdma_rn_unregister()`, `rpcrdma_ib_client_register()`, and `rpcrdma_ib_client_unregister()`.

Control flow: RPC/RDMA code registers a notification object against an `ib_device`; when the RDMA core reports removal, the callback is invoked so transports can tear down or mark resources unavailable.

State and persistence: notification registration state is runtime state associated with RDMA devices and RPC/RDMA transports.

Dependencies and integration points: depends on RDMA `ib_verbs.h` and is used by client/server RPC/RDMA transport code, including `svc_rdma.h`.

Risks and test signals: risks include callback after transport free, unregister races, missing device removal events, and index reuse confusion. Test with RDMA device hot-remove, module unload, failed registration, and active RPC/RDMA traffic during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rdma_rn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_pipe_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_pipe_fs.h

Purpose: declares the rpc_pipefs infrastructure used by SUNRPC to exchange upcalls/downcalls with user-space helpers such as GSS daemons and cache managers.

Important APIs and types: `struct rpc_pipe_dir_head`, `rpc_pipe_dir_object`, and ops manage dynamic pipefs directory objects. `struct rpc_pipe_msg` tracks queued message data, bytes copied, and errno. `struct rpc_pipe_ops` defines upcall/downcall/open/release/destroy callbacks. `struct rpc_pipe` owns upcall/downcall queues, reader/writer counts, timeout work, ops, lock, and dentry. `struct rpc_inode` embeds VFS inode state. APIs cover pipefs notifier registration, per-net superblock management, generic upcalls, message queueing, client/cache directories, pipe data/dentry creation, unlinking, registration, and `gssd_running()`.

Control flow: kernel code creates pipefs objects, queues an upcall message, user space reads and writes responses, then downcall handlers update kernel state. Mount/umount notifiers and per-net superblock helpers manage visibility.

State and persistence: all state is runtime VFS/pipefs state; messages are transient and tied to readers/writers and dentries.

Dependencies and integration points: integrates with VFS inodes/dentries, workqueues, net namespaces, cache details, RPC clients, and GSS user-space daemons.

Risks and test signals: risks include stuck upcalls without readers, message lifetime races, namespace mount teardown, in-flight message detection, and cache directory leaks. Test with rpc_pipefs mount/unmount, gssd restarts, cache upcalls, per-net cleanup, and concurrent readers/writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_pipe_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma.h

Purpose: defines common RPC-over-RDMA version-one wire constants, connection-private data, procedure/error values, and segment encode/decode helpers.

Important APIs and types: constants include `RPCRDMA_VERSION`, inline size defaults, header size limits, and max XDR quad sizes for fixed headers and chunks. `enum rpcrdma_errcode` and `enum rpcrdma_proc` define RDMA_ERROR causes and message procedures. Pre-XDR constants provide big-endian procedure/error values. `struct rpcrdma_connect_private` is the packed RDMA-CM private extension with magic, version, flags, and encoded send/recv sizes. Helpers encode/decode 1 KiB-based buffer sizes and XDR RDMA/read segments.

Control flow: connection setup exchanges private data; send/receive paths parse RDMA_MSG/NOMSG/MSGP/DONE/ERROR and encode or decode chunk segment descriptors with XDR helpers.

State and persistence: no state is stored; this is a wire ABI and helper header.

Dependencies and integration points: depends on integer and bit APIs and `xdr_encode_hyper()`/`xdr_decode_hyper()` from SUNRPC XDR. Shared by client and server RPC/RDMA.

Risks and test signals: risks include packed layout drift, endianness mistakes, unsupported chunk combinations, buffer-size encoding underflow, and version negotiation errors. Test with RPC/RDMA interoperability, RDMA-CM private data, malformed chunks, and big-endian/little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma_cid.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma_cid.h

Purpose: defines a shared completion identifier structure for client and server RPC/RDMA transports.

Important APIs and types: `struct rpc_rdma_cid` stores `ci_queue_id` and `ci_completion_id`, enough to correlate a completion event with a completion queue and a posted send/receive/work request.

Control flow: transport code initializes a CID before posting RDMA work and later uses it in completion handling, tracing, and error messages.

State and persistence: CID values are runtime diagnostics/correlation state; they are not persistent and are generally scoped to a transport's completion-id sequence.

Dependencies and integration points: included by RPC/RDMA client and server headers, especially `svc_rdma.h`.

Risks and test signals: risks include ID reuse ambiguity, uninitialized IDs on error completions, and queue ID mismatch after resource recreation. Test with RDMA send/recv completions, CQ teardown, error tracing, and reconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/rpc_rdma_cid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/sched.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/sched.h

Purpose: declares the SUNRPC task scheduler, wait queues, timeout strategy, call callback interface, and rpciod/xprtiod workqueue hooks.

Important APIs and types: `struct rpc_message` carries procedure, args, response, and credentials. `struct rpc_timeout` defines initial/max/increment/retry/exponential behavior. `struct rpc_task` is the central asynchronous/synchronous RPC state machine with refcount, status, callbacks/actions, runstate bits, wait/work union, message, client, transport, request, workqueue, owner, retry counters, flags, and priority. `struct rpc_call_ops` provides prepare/done/stats/release callbacks. `struct rpc_task_setup` configures new tasks. `struct rpc_wait_queue` implements priority wait queues and timer lists.

Control flow: callers create or run tasks, scheduler actions sleep tasks on wait queues, timers wake or fail them, transports set send/receive runstate bits, and completion invokes callbacks before releasing calldata.

State and persistence: tasks and wait queues are runtime state. Workqueues `rpciod_workqueue` and `xprtiod_workqueue` execute async work; no state persists beyond client/task lifetime.

Dependencies and integration points: integrates timers, ktime, wait-bit, workqueues, spinlocks, RPC XDR, client/transport/auth code, and optional swap-over-NFS support.

Risks and test signals: risks include task refcount leaks, wakeup races, priority starvation, timeout policy mismatches, cancellation status races, and workqueue shutdown ordering. Test with async/sync RPC, soft/hard timeouts, signal interruption, cancellation, high-priority tasks, swap activation, and debug task dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/stats.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/stats.h

Purpose: declares coarse SUNRPC client and server statistics structures and procfs registration helpers.

Important APIs and types: `struct rpc_stat` records program pointer plus network, UDP/TCP/connect/reconnect, RPC, retransmission, auth-refresh, and garbage counters. `struct svc_stat` records server program pointer plus network/TCP/UDP/connect, RPC, bad format, bad auth, and bad client counters. Procfs-enabled APIs initialize/exit per-net proc entries, register/unregister client/server stats, zero RPC program counters, and show service stats.

Control flow: RPC client/server paths increment counters, procfs registration exposes them under the network namespace, and proc readers render cumulative values. Without `CONFIG_PROC_FS`, all helpers become no-ops.

State and persistence: stats are in-memory cumulative counters for program/service lifetime; no persistent storage.

Dependencies and integration points: integrates with procfs, `seq_file`, RPC program descriptors, service descriptors, and net namespaces.

Risks and test signals: risks include counter drift, procfs-disabled blind spots, unregister ordering, and parsers depending on output format. Test with procfs enabled/disabled, per-net namespace teardown, client/server call counters, and stats reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc.h

Purpose: declares the SUNRPC server framework: service thread pools, request context, program/version/procedure descriptors, buffer sizing, request processing, and server-side XDR stream setup.

Important APIs and types: `struct svc_pool` tracks per-pool thread counts, pending transports, idle/all thread lists, counters, and flags for work/victim management. `struct svc_serv` holds program tables, stats, locks, thread counts, transport lists, temp-socket timer, pool array, thread function, and optional backchannel queue. `struct svc_rqst` is the per-thread/per-RPC context with transport, addresses, service/procedure/auth state, XDR arg/reply buffers/streams, page arrays, folio batching, RPC header fields, decoded args/results, auth slack, cache request handle, client domains, task pointer, and private data. `struct svc_program`, `svc_version`, and `svc_procedure` describe dispatch, auth, rpcbind, decode, encode, release, and size contracts.

Control flow: a service is created and bound, threads receive transport work, initialize decode streams, authenticate and dispatch to a procedure, encode replies into page-backed XDR buffers, reserve auth slack, send responses, release pages, and possibly stop when pool victim flags are set.

State and persistence: service, pool, request, temp socket, and page buffer state are in-memory and service-lifetime. RPC payload pages are dynamically refilled and released per request; no persistent storage is managed here.

Dependencies and integration points: depends on XDR, auth/svcauth, lwq, wait queues, mm/pages/folios, kthreads, net namespaces, rpcbind, service transports, and optional backchannel support. NFSd and lockd are principal users.

Risks and test signals: risks include page-array ownership bugs, auth slack underflow, thread stop races, temp socket accounting, request deferral loops, buffer length mismatches, and backchannel context confusion. Test with NFSd/lockd workloads, UDP/TCP/RDMA payload sizes, thread pool resizing, auth flavors, deferral caches, and KASAN on page release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma.h

Purpose: declares the server-side RPC/RDMA transport implementation state, context pools, statistics, and send/receive/read/write helper entry points.

Important APIs and types: module parameters/stats include `svcrdma_ord`, max request settings, `svcrdma_wq`, and percpu counters. `struct svcxprt_rdma` embeds `svc_xprt` and owns RDMA CM/QP/CQ/PD state, send queue accounting, credits, locks, wait queues, context freelists, receive/read completion queues, flags, and completion IDs. `struct svc_rdma_recv_ctxt` stores receive WR/CQE/SGE, receive buffer stream, invalidation key, read-pull state, saved arg buffer, parsed chunk lists, and request pages. `struct svc_rdma_send_ctxt`, `svc_rdma_write_info`, and `svc_rdma_chunk_ctxt` track send work, write/reply chunks, pages, SGE construction, and RDMA read/write completions.

Control flow: receives are posted, incoming RDMA messages are parsed into chunk lists, read chunks may be pulled into request pages, service code processes the RPC, then write/reply chunks are mapped and send WRs are posted. SQ wait/ticketing and completion IDs coordinate resource use and diagnostics.

State and persistence: transport state is connection-lifetime RDMA runtime state: credits, contexts, queues, counters, posted WRs, and pages. Nothing persists beyond the connection/service.

Dependencies and integration points: integrates SUNRPC service transport, XDR, socket service helpers, RPC/RDMA wire helpers, RDMA core verbs/CM, notification API, parsed chunk lists, workqueues, and percpu counters.

Risks and test signals: risks include SQ starvation, credit accounting bugs, DMA mapping leaks, page ownership mistakes, malformed chunk parsing, send-with-invalidate compatibility, and RDMA device removal races. Test with NFS/RDMA server workloads, read/write/reply chunks, backchannel, CQ errors, hot-unplug, and RDMA resource exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma_pcl.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma_pcl.h

Purpose: defines parsed RPC/RDMA chunk list structures and helpers used by the server receive path.

Important APIs and types: `struct svc_rdma_segment` stores handle, length, and offset. `struct svc_rdma_chunk` links a chunk, position, length, payload length, segment count, and flexible segment array. `struct svc_rdma_pcl` stores count and chunk list head. Helpers initialize lists, test emptiness, fetch first/next chunks, iterate chunks/segments, and compute aligned end offsets with `xdr_align_size()`. Allocation/process APIs include `pcl_free()`, `pcl_alloc_call()`, `pcl_alloc_read()`, `pcl_alloc_write()`, and `pcl_process_nonpayloads()`.

Control flow: the RDMA receive parser builds call/read/write/reply parsed chunk lists from incoming XDR, service RDMA code iterates chunks and segments to move payload or process non-payload data, then frees the parsed lists.

State and persistence: parsed chunk lists are per-receive-context runtime state.

Dependencies and integration points: depends on kernel lists and SUNRPC XDR alignment; integrates tightly with `svc_rdma_recv_ctxt` in `svc_rdma.h`.

Risks and test signals: risks include zero segment counts breaking iteration, malformed lengths/positions, alignment mistakes, allocation failure cleanup, and nonpayload processing gaps. Test with malformed chunk lists, multi-segment chunks, empty lists, read/write/reply chunk combinations, and KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma_pcl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_xprt.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_xprt.h

Purpose: declares the SUNRPC server transport abstraction used by socket, RDMA, and other service transports.

Important APIs and types: `struct svc_xprt_ops` defines create, accept, space check, receive, send, result-payload handling, context release, detach, free, temp-kill, and handshake hooks. `struct svc_xprt_class` registers a transport class with max payload and identifier. `struct svc_xpt_user` provides deletion callbacks. `struct svc_xprt` stores class/ops, kref, queue time, list/ready nodes, flags, service pointer, reservation/request counts, locks, auth cache, deferred list, local/remote addresses, users, net namespace, credentials, and optional backchannel client transport/switch.

Control flow: service code registers transport classes, creates/listens on transports, enqueues ready transports, receives into `svc_rqst`, sends replies, closes/deferred-closes, and tears down all transports during service destruction. Inline helpers manage peer-valid temp connection accounting and user callbacks.

State and persistence: transport state is runtime service/connection state with refcounts, flags, reservations, address buffers, deferred requests, and optional auth cache.

Dependencies and integration points: depends on `svc.h`, networking address types, krefs, lwq, net namespaces, credentials, and rpcbind unregister behavior.

Risks and test signals: risks include temp connection count leaks, close/user callback races, auth cache lifetime, address length assumptions, and transport class unregister while active. Test with TCP/UDP/RDMA listeners, temp connection aging, TLS handshake flags, deferred close, and service teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_xprt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth.h

Purpose: declares server-side SUNRPC authentication credentials, auth domains, flavor operations, Unix/GSS mapping helpers, and hash helpers.

Important APIs and types: `struct svc_cred` stores uid/gid/group info, pseudoflavor, raw/principal/target principal strings, and GSS mechanism reference. `init_svc_cred()` and `free_svc_cred()` initialize and release those fields. `struct auth_domain` is a refcounted, hashed, RCU-freed domain with name and flavor ops. `enum svc_auth_status` covers garbage, valid, negative, ok, drop, close, denied, pending, and complete. `struct auth_ops` accepts/releases requests, releases domains, sets clients, and returns pseudoflavors.

Control flow: server receive code calls flavor-specific `accept()`, possibly maps a client domain through caches, authorizes, dispatches, then calls `release()` to sign/encrypt or cleanup. Local client credentials can be mapped into service credentials for backchannel/local cases.

State and persistence: auth domains, Unix/GID caches, credential principal strings, and GSS mechanism refs are runtime state, often refreshed by upcall caches.

Dependencies and integration points: integrates string, cache, GSS API, RPC client, hashing, credentials, and `svc_xprt` auth cache. It supports NFS export/client identity authorization.

Risks and test signals: risks include group_info leaks, GSS mechanism ref leaks, domain RCU lifetime bugs, hash collision behavior, pending cache upcalls, and wrong status-to-RPC-error mapping. Test AUTH_NULL/UNIX/GSS, cache expiry, domain lookup races, local backchannel mapping, and KASAN/RCU debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth_gss.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth_gss.h

Purpose: declares server-side RPCSEC_GSS lifecycle and pseudoflavor registration helpers.

Important APIs and types: APIs include global `gss_svc_init()`/`gss_svc_shutdown()`, per-net `gss_svc_init_net()`/`gss_svc_shutdown_net()`, `svcauth_gss_register_pseudoflavor()`, and `svcauth_gss_flavor()`.

Control flow: SUNRPC server initialization registers GSS service support, per-net setup prepares namespace-local state, mechanisms register pseudoflavors as auth domains, and request authentication can recover the pseudoflavor from a domain.

State and persistence: GSS service and per-net state are runtime only; auth domains may be cached and refreshed by user-space GSS helpers.

Dependencies and integration points: depends on scheduler types, SUNRPC XDR, server auth, service sockets, and RPCSEC_GSS definitions. It bridges svcauth and GSS mechanism registration.

Risks and test signals: risks include per-net cleanup ordering, duplicate pseudoflavor registration, missing user-space helper state, and flavor/domain mismatch. Test with NFSd Kerberos exports, namespace creation/destruction, module init/shutdown, and GSS context expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth_gss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcsock.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcsock.h

Purpose: declares the socket-based SUNRPC server transport and helpers for receiving, sending, and creating service sockets.

Important APIs and types: `struct svc_sock` embeds `svc_xprt`, stores `socket`/`sock`, saved socket callbacks, send `bio_vec`, TCP record marker/length accounting, page fragment cache, handshake completion, max pages, and flexible page array. Inline helpers `svc_sock_reclen()` and `svc_sock_final_rec()` decode the RPC stream fragment header. APIs include `svc_recv()`, `svc_send()`, `svc_addsock()`, `svc_init_xprt_sock()`, and `svc_cleanup_xprt_sock()`. Socket creation flags include anonymous and temporary.

Control flow: socket callbacks mark transports ready, service threads receive request records/fragments into pages, process RPCs, and send replies. TCP receive state tracks record marker, received bytes, and data length across fragments.

State and persistence: socket transport state is per-connection runtime state: callbacks, fragment progress, page cache, handshake completion, and page arrays.

Dependencies and integration points: integrates with `svc.h`, `svc_xprt.h`, Berkeley sockets, INET sockets, bio vectors, and RPC record marking from `msg_prot.h`.

Risks and test signals: risks include fragment length parsing bugs, callback restoration races, send vector lifetime, handshake stalls, and page accounting errors. Test TCP fragmented RPCs, UDP service sockets, TLS handshake paths, temporary sockets, and service shutdown under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/svcsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/timer.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/timer.h

Purpose: declares the RPC round-trip-time estimator and timeout calculation helpers used by client transports.

Important APIs and types: `struct rpc_rtt` stores default timeout, five smoothed RTT values, five smoothed deviations, and per-timer timeout counts. APIs include `rpc_init_rtt()`, `rpc_update_rtt()`, and `rpc_calc_rto()`. Inline helpers `rpc_set_timeo()` and `rpc_ntimeo()` adjust/read bounded timeout counters for timer indexes.

Control flow: after successful replies, transports update RTT estimators; before retransmission/waiting, code calculates RTO. Timeout counters are capped at eight and can decay when observed timeout count decreases.

State and persistence: RTT state is per-client runtime estimator state and is not persistent.

Dependencies and integration points: used by `rpc_clnt`, `rpc_task`, and `rpc_xprt` timeout paths.

Risks and test signals: risks include wrong timer index handling, overly aggressive retransmission, timeout counter saturation, and poor behavior after network changes. Test with induced latency/loss, soft/hard mounts, multiple procedure timer classes, and reconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/types.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/types.h

Purpose: provides generic SUNRPC includes and a small signal-pending shorthand used by older SUNRPC code.

Important APIs and types: `signalled()` expands to `signal_pending(current)`.

Control flow: callers use `signalled()` to decide whether an RPC operation should abort or return restart/interruption status.

State and persistence: no state is owned here.

Dependencies and integration points: includes timers, signal-aware scheduler state, workqueues, SUNRPC debug support, and lists. It is a common foundational include for other SUNRPC headers.

Risks and test signals: risks are macro opacity around `current` and accidental use in contexts where signal state is irrelevant. Test via signal-interrupted RPC waits and compile coverage of SUNRPC headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdr.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdr.h

Purpose: declares the kernel SUNRPC XDR buffer model, stream encoder/decoder, common RPC pre-encoded constants, and helpers for scalar, opaque, string, array, page-backed, and scatter/gather XDR processing.

Important APIs and types: `XDR_UNIT` and `XDR_QUADLEN()` define 32-bit alignment. `struct xdr_netobj` represents counted opaque data. `struct xdr_buf` models head/tail kvecs plus page/bvec-backed payload with flags `XDRBUF_READ`, `XDRBUF_WRITE`, and `XDRBUF_SPARSE_PAGES`. Pre-XDR constants encode RPC auth/message/status values. `struct xdr_array2_desc` describes generic array encode/decode. `struct xdr_stream` tracks current pointer, buffer, end, iov, scratch buffer, page pointer/kaddr, remaining decode words, and request pointer. APIs reserve/commit/truncate/restrict streams, read/write pages, create subsegments, move/zero ranges, process buffers with scatterlists, encode/decode auth, strings, opaque values, booleans, u32/u64/be32, arrays, and optional item discriminators.

Control flow: callers initialize encode or decode streams over an `xdr_buf`, reserve contiguous space or inline-decode bytes, use scratch buffers when page-boundary data must be linearized, write/read page payloads, and return `-EMSGSIZE` or `-EBADMSG` on overflow.

State and persistence: XDR state is per-message runtime state in caller-provided buffers/pages. Duplicated netobjs allocate caller-owned memory.

Dependencies and integration points: depends on kvec/uio, byteorder, unaligned access, scatterlists, pages/folios, RPC message constants, and request objects. It is the shared wire-encoding layer for SUNRPC client, server, RDMA, NFS, and generated XDR code.

Risks and test signals: risks include alignment/padding mistakes, page boundary linearization bugs, buffer length under/over-accounting, max length validation after pointer exposure, sparse page handling, and endian mistakes. Test with XDR selftests, malformed/truncated RPCs, page-spanning opaque fields, large NFS READ/WRITE payloads, RDMA chunks, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_builtins.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_builtins.h

Purpose: provides inline encode/decode primitives used by generated in-kernel XDR code for RFC 4506 scalar, string, and opaque types.

Important APIs and types: helpers cover void, bool, signed/unsigned short, int, unsigned int, long, unsigned long, hyper, unsigned hyper, variable-length `string`, and variable-length `opaque`. They use `struct xdr_stream`, `xdr_inline_decode()`, `xdr_reserve_space()`, `xdr_stream_decode_u32()`, `xdr_encode_opaque()`, and alignment helpers.

Control flow: generated decoders inline-decode the needed XDR units and return `false` on missing data or max-length violation. Encoders reserve the aligned size and write big-endian wire values, returning `false` on overflow. Strings/opaque values expose pointers into the XDR stream rather than duplicating data.

State and persistence: no persistent state. Decoded string/opaque pointers are valid only as long as the backing XDR buffer remains valid.

Dependencies and integration points: depends on `xdr.h` and `_defs.h` type names. Used by generated protocol headers/implementations such as NFSv4.1 and NLMv4.

Risks and test signals: risks include pointer lifetime misuse, ignored `maxlen` in encode call sites, sign-extension assumptions for non-standard short types, and missing padding validation. Test generated XDR round trips, truncated inputs, max-length failures, and signed short vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_defs.h

Purpose: defines base C representations and fixed XDR word-size constants for generated SUNRPC XDR code.

Important APIs and types: `TRUE` and `FALSE` map to C booleans. `typedef struct { u32 len; unsigned char *data; } string;` represents XDR strings. `typedef struct { u32 len; u8 *data; } opaque;` represents XDR opaque data. Size macros define word counts for void, bool, int, unsigned int, long, unsigned long, hyper, and unsigned hyper.

Control flow: generated headers use these definitions to declare protocol structs and compute static maximum encoded sizes.

State and persistence: no state; decoded pointers point into separately managed XDR buffers.

Dependencies and integration points: included by generated XDR protocol headers and assumes kernel integer and bool types are available from the including context.

Risks and test signals: risks include confusing byte length with XDR word counts, pointer lifetime misuse, and generated-code ABI drift. Test by regenerating XDR headers, compiling protocol users, and validating max-size macros against encoded test vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nfs4_1.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nfs4_1.h

Purpose: generated XDR type and size definitions for selected NFSv4.1 protocol extensions, including delegation-time attributes, OPEN argument metadata, and POSIX ACL extension attributes.

Important APIs and types: defines aliases `int64_t`, `uint32_t`, `bitmap4`, UTF-8 string aliases, `struct nfstime4`, `fattr4_offline`, and `struct open_arguments4`. Enums define OPEN share access/deny/want, open claim, create mode, delegation types, ACL model/scope, and POSIX ACE tags. `struct posixace4` holds tag, permissions, and `who`; default/access ACL arrays hold `posixace4` elements. Attribute numbers include `FATTR4_OFFLINE`, `FATTR4_TIME_DELEG_ACCESS`, `FATTR4_TIME_DELEG_MODIFY`, `FATTR4_OPEN_ARGUMENTS`, and POSIX ACL attributes. Size macros compute XDR word counts for each generated type.

Control flow: generated encoder/decoder code and NFS protocol code include this header to allocate structs, validate enum values, and size XDR buffers for these attributes.

State and persistence: no runtime state; structures represent decoded or to-be-encoded protocol payloads.

Dependencies and integration points: depends on `_defs.h` and kernel types. It is generated from `Documentation/sunrpc/xdr/nfs4_1.x`, so manual edits would be overwritten.

Risks and test signals: risks include generated file/spec drift, incorrect array maximum assumptions, enum value mismatch with NFS protocol, and stale size macros. Test with xdrgen regeneration, NFSv4.1 OPEN/delegation/POSIX ACL vectors, and interoperability with NFS servers/clients advertising these attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nfs4_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nlm4.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nlm4.h

Purpose: generated XDR type, procedure, and maximum-size definitions for NLMv4 network lock manager protocol messages.

Important APIs and types: constants define maximum string/object sizes and `NLM4_PROG`. Types include `netobj`, share mode/access enums, scalar aliases, `nlm4_stats`, `nlm4_holder`, `nlm4_testrply`, `nlm4_stat`, `nlm4_res`, `nlm4_testres`, `nlm4_lock`, lock/cancel/test/unlock args, share/shareargs/shareres, notify/notifyargs, and procedure IDs from NULL through lock/share/free-all operations. Size macros compute XDR word counts and `NLM4_MAX_ARGS_SZ`.

Control flow: lock manager XDR code uses these declarations to marshal lock requests, test replies, callbacks, share operations, and status monitor notifications.

State and persistence: no state is owned; structs are transient decoded or encoded protocol messages. Actual lock state lives in NLM/lockd code.

Dependencies and integration points: depends on `_defs.h` and generated XDR primitive definitions. It is generated from `Documentation/sunrpc/xdr/nlm4.x`.

Risks and test signals: risks include generated spec drift, maximum string/object mismatch, lock range width errors, status endian handling because `nlm4_stats` is `__be32`, and procedure ID incompatibility. Test with lockd interoperability, lock/test/cancel/unlock/share RPC vectors, status monitor notify, and malformed oversized netobjs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xdrgen/nlm4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprt.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprt.h

Purpose: declares the SUNRPC client transport layer, request slot structure, transport operations, transport class registration, congestion/window state, connection state bits, and generic transport helpers.

Important APIs and types: `struct rpc_rqst` tracks send/receive XDR buffers, task/cred/XID, GSS sequence history, encryption scratch pages, slot/receive/send queue nodes, call/reply buffers, byte counts, timeout/retry/connect state, partial-send progress, timestamps, pins, and optional backchannel preallocation. `enum xprtsec_policies` and `struct xprtsec_parms` configure none/anonymous TLS/X.509 TLS. `struct rpc_xprt_ops` defines buffer sizing, slot reservation, rpcbind, connect, send, receive wait, timer, close, destroy, swap, disconnect injection, and backchannel hooks. `struct rpc_xprt` owns refcount, ops, address, protocol, congestion/cwnd, wait queues, slot table, state bits, connection timers, locks, XID generator, send/receive queues, stats, net namespace, display strings, debug/sysfs objects, class, and multipath flags.

Control flow: tasks reserve a slot and transport, bind/connect if needed, enqueue transmit/receive, send requests, wait for replies, update RTT/congestion, complete or retransmit, then release slots and transport references. State-bit helpers manage connected, connecting, bound, and binding transitions with memory barriers where needed.

State and persistence: transport state is runtime client/connection state: slots, queues, congestion windows, timers, stats, addresses, reconnect cookies, and optional backchannel pools. It does not persist beyond client/transport lifetime.

Dependencies and integration points: integrates RPC scheduler, XDR, message protocol constants, sockets/RDMA/local transport classes, net namespaces, sysfs/debugfs, TLS policy, NFS backchannel, and multipath.

Risks and test signals: risks include slot leaks, XID lookup races, congestion accounting errors, reconnect cookie misuse, state-bit memory ordering, send/receive queue races, and TLS/backchannel interactions. Test with TCP/UDP/RDMA/local transports, retransmits, disconnect/reconnect, congestion, high slot counts, GSS privacy, and multipath failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtmultipath.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtmultipath.h

Purpose: declares SUNRPC client transport-switch and iterator infrastructure for multipath/nconnect-style transport selection.

Important APIs and types: `struct rpc_xprt_switch` contains a lock, kref, ID, transport counts, active and unique-destination counts, queue length, xprt list, net namespace, iterator ops, sysfs object, and RCU head. `struct rpc_xprt_iter` stores an RCU switch pointer, cursor transport, and iterator ops. `struct rpc_xprt_iter_ops` provides rewind/current/next callbacks.

Control flow: clients allocate a switch around an initial transport, add/remove transports, select iterator policy such as round-robin, initialize iterators, exchange switches under RCU, and fetch current/next transports for RPC tasks.

State and persistence: multipath state is runtime client state with refcounts and RCU lifetime. Transport IDs can be cleaned up through `xprt_multipath_cleanup_ids()`.

Dependencies and integration points: integrates with `rpc_xprt`, net namespaces, sysfs transport switch objects, and client transport-management code in `clnt.h`.

Risks and test signals: risks include RCU cursor use-after-free, active count drift, duplicate address accounting errors, queue length mismatch, and offline removal races. Test nconnect/multipath mounts, round-robin selection, add/remove during I/O, offline transports, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtmultipath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtrdma.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtrdma.h

Purpose: exposes client RPC/RDMA transport constants and memory-registration strategy IDs, including values that form part of a kernel/user-space API.

Important APIs and types: slot table bounds are `RPCRDMA_MIN_SLOT_TABLE`, `RPCRDMA_DEF_SLOT_TABLE`, and `RPCRDMA_MAX_SLOT_TABLE`. Inline thresholds are `RPCRDMA_MIN_INLINE`, `RPCRDMA_DEF_INLINE`, and `RPCRDMA_MAX_INLINE`. `enum rpcrdma_memreg` lists registration strategies from bounce buffers through FRWR and physical mappings, ending at `RPCRDMA_LAST`.

Control flow: RPC/RDMA client setup and module parameters use these constants to size request slots, inline thresholds, and choose memory registration mode.

State and persistence: no state is stored here; selected values influence runtime transport state elsewhere.

Dependencies and integration points: included by RPC/RDMA client code and user-visible configuration paths; comments warn that memory registration strategy numbers must not be removed.

Risks and test signals: risks include breaking user-space ABI by renumbering strategies, invalid inline thresholds, and slot table values that exceed RDMA resources. Test RPC/RDMA mounts with each supported memreg mode, threshold boundary values, and module parameter compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtrdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtsock.h -->
# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtsock.h

Purpose: declares the socket-backed SUNRPC client transport provider and its private transport state.

Important APIs and types: lifecycle APIs are `init_socket_xprt()` and `cleanup_socket_xprt()`. Reserved port bounds/defaults define privileged source port selection. `struct sock_xprt` embeds `rpc_xprt` and stores socket, sock, backing file, TCP receive fragment/XID/calldir/offset/length/copied state, transmit offset, socket state bits, connect/error/recv workers, receive mutex, handshake completion, source address/port, last transport error, owning client, UDP buffer sizes, TCP timeout, and saved socket callbacks. State bits include connecting, data ready, timeout update, wake error/write/pending/disconnect, connect sent, no space, and ignore receive.

Control flow: socket transports initialize and register, connect asynchronously, receive stream fragments into the RPC receive state machine, transmit partial records using offsets, handle socket callbacks through workers, and restore callbacks during teardown.

State and persistence: socket transport state is per-transport runtime state tied to sockets, workers, callbacks, and connection progress.

Dependencies and integration points: integrates with `rpc_xprt`, socket layer callbacks, workqueues, handshake support, RPC client, and TCP/UDP timeout behavior.

Risks and test signals: risks include callback races, receive worker reentrancy, fragment header parsing, partial-send offset bugs, reserved-port exhaustion, and handshake completion deadlocks. Test TCP and UDP RPC, reconnects, socket errors, TLS handshake paths, partial sends, and cleanup under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunserialcore.h -->
# sources/distributed-fs/ceph-client/include/linux/sunserialcore.h

Purpose: declares shared Sun serial, keyboard, mouse, and console helper interfaces for SPARC/Sun UART drivers.

Important APIs and types: keyboard constants identify reset and L1-A key sequence values. APIs include `suncore_mouse_baud_cflag_next()`, `suncore_mouse_baud_detection()`, `sunserial_register_minors()`, `sunserial_unregister_minors()`, `sunserial_console_match()`, and `sunserial_console_termios()`.

Control flow: serial drivers register UART minors, detect mouse baud changes from received bytes, match Open Firmware console nodes, and derive console termios settings.

State and persistence: state lives in UART drivers, console objects, and device tree nodes; this header stores none.

Dependencies and integration points: depends on device, serial core, console, and device tree support. It integrates legacy Sun keyboard/mouse serial behavior with the generic UART layer.

Risks and test signals: risks include minor allocation mismatches, OF console matching mistakes, keyboard escape sequence handling, and baud detection false positives. Test on Sun/SPARC serial console hardware or emulation, console handoff, keyboard L1-A handling, and mouse baud changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunserialcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunxi-rsb.h -->
# sources/distributed-fs/ceph-client/include/linux/sunxi-rsb.h

Purpose: declares the Allwinner Reduced Serial Bus client device/driver model and managed regmap creation helper.

Important APIs and types: `struct sunxi_rsb_device` embeds `struct device`, points to the controller, stores IRQ, runtime address, and hardware address. `to_sunxi_rsb_device()`, `sunxi_rsb_device_get_drvdata()`, and `sunxi_rsb_device_set_drvdata()` bridge to driver core data. `struct sunxi_rsb_driver` wraps `device_driver` with probe/remove callbacks. APIs/macros include `sunxi_rsb_driver_register()`, `sunxi_rsb_driver_unregister()`, `module_sunxi_rsb_driver()`, `__devm_regmap_init_sunxi_rsb()`, and `devm_regmap_init_sunxi_rsb()`.

Control flow: an RSB client driver registers a `sunxi_rsb_driver`; matching devices call probe with a `sunxi_rsb_device`; drivers usually create a devm-managed regmap to access the slave registers and unregister through driver core on module exit.

State and persistence: device and driver binding state is managed by driver core; regmap state is devm-managed per device.

Dependencies and integration points: depends on device core, regmap, lockdep wrappers, module driver helpers, and Allwinner RSB controller code.

Risks and test signals: risks include wrong runtime/hardware address mapping, regmap lock class misuse, remove/probe lifetime issues, and IRQ ownership confusion. Test with Allwinner PMIC/peripheral RSB clients, deferred probe, module unload, regmap read/write, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sunxi-rsb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_acpi_notify.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_acpi_notify.h

Purpose: declares the Surface ACPI Notify client interface for receiving discrete-GPU ACPI events produced by the SAN driver.

Important APIs and types: `struct san_dgpu_event` carries category, target, command, instance, payload length, and payload pointer. APIs are `san_client_link()`, `san_dgpu_notifier_register()`, and `san_dgpu_notifier_unregister()`.

Control flow: a client links itself to the SAN provider device, registers a notifier block for dGPU events, receives event payloads via the notifier chain, and unregisters before teardown.

State and persistence: event data is transient; notifier registration state lives in the SAN driver and notifier chain. No persistent state is defined here.

Dependencies and integration points: depends on notifier blocks, device objects, and integer types. It integrates Microsoft Surface platform drivers that need SAN-mediated dGPU notifications.

Risks and test signals: risks include notifier lifetime races, payload pointer lifetime misuse, unregister ordering during device removal, and malformed ACPI event lengths. Test with Surface dGPU hotplug/power events, driver unload, ACPI notification storms, and bounds checks on payload consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_acpi_notify.h -->
