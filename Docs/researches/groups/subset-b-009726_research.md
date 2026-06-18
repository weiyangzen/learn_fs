# subset-b-009726 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/server_stats.c -->
## sources/user-network-fs/nfs-ganesha/src/support/server_stats.c

Purpose: `server_stats.c` is the central runtime statistics implementation for NFS-Ganesha. It records protocol operation counts, read/write transfer sizes, latency, duplicates, NFSv4 compound sizes, pNFS layout activity, 9P transport/op activity, delegation counters, and optional detailed per-op DBus/statistics views.

Important APIs, types, and functions: internal types include `struct proto_op`, `op_latency`, `xfer_op`, `layout_op`, protocol-specific stats structs, `transport_stats`, `global_stats`, and `deleg_stats`. External entry points include `server_stats_nfs_done`, `server_stats_nfsv4_op_done`, `server_stats_compound_done`, `server_stats_io_done`, `server_stats_9p_done`, `server_stats_transport_done`, delegation increment helpers, DBus marshalling helpers, reset helpers, and free helpers. `record_op`, `record_latency`, `record_io`, `record_nfsv4_op`, `record_stats`, and `record_clnt_all_stats` are the core update routines.

Control flow: request completion paths enter through protocol callbacks after handlers finish. Fast stats increment global per-procedure arrays and may return early. Full stats compute elapsed time from `op_ctx`, classify protocol/read/write/layout operations, update client and export stats, and emit `nfs_metrics` dynamic observations. DBus readers later walk lazily allocated client/export/global structures and marshal summaries, per-version totals, I/O stats, layout stats, full v3/v4 op stats, and nfsmon one-second deltas.

State and persistence: all counters are in-memory only. `global_st`, `v3_full_stats`, and `v4_full_stats` are static process-global state. Client/export stats live in owning client/export structures via `server_stats_private.h` and are allocated lazily under the owner lock. Updates use atomic integer operations for hot counters and intentionally avoid strict locking around min/max latency. Reset functions zero counters; free functions release lazily allocated substructures.

Dependencies and integration points: this file depends on protocol constants, `op_ctx`, client/export managers, DBus, 9P conditionals, NFSv3/NLM/RQUOTA build flags, `abstract_atomic`, `nfs_proto_functions`, `nfs_convert`, and `nfs_metrics`. It is integrated with RPC completion (`nfs_rpc_process_request`), NFSv4 compound processing, protocol read/write handlers, export/client DBus methods, and metrics exporters.

Risks: latency min/max updates are racy by design, so instantaneous min/max can be slightly inaccurate under concurrent updates. Several arrays are indexed by protocol op numbers and rely on upstream bounds; full stats log critically on overflow but some fast-stat increments assume valid op ids. `dec_grants` increments `curr_deleg_grants`, which looks suspicious for a decrement helper. DBus output shape depends on build flags and whether stats structs have been allocated. `server_dbus_nfsmon_iostats` sleeps for one second in the DBus path.

Test signals: coverage is mostly indirect through runtime protocol tests, DBus stat consumers, metrics validation, and NFSv3/v4 operation tests. Useful focused tests would exercise fast-stat early return, per-client all-op accounting, export latency averages, reset/free behavior, layout delay/error categorization, and delegation grant decrement behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/server_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/strlcpy.c -->
## sources/user-network-fs/nfs-ganesha/src/support/strlcpy.c

Purpose: compatibility implementation of BSD `strlcpy` when the platform lacks `HAVE_STRLCPY`.

Important APIs, types, and functions: exports `size_t strlcpy(char *dst, const char *src, size_t siz)` under the feature guard. It copies up to `siz - 1` bytes, NUL-terminates when `siz != 0`, and returns the full source length.

Control flow: it copies while space remains, stops early on source NUL, otherwise writes a terminating NUL and advances through the rest of `src` to compute the return value.

State and persistence: no persistent state; pure buffer utility.

Dependencies and integration points: depends only on `<sys/types.h>` and build-time feature detection. It provides the expected libc-like symbol for the rest of the tree.

Risks: like standard `strlcpy`, behavior is undefined for invalid pointers or overlapping buffers. Return value must be checked by callers to detect truncation.

Test signals: unit tests should cover `siz == 0`, exact fit, truncation, empty source, and return length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/strlcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/strnlen.c -->
## sources/user-network-fs/nfs-ganesha/src/support/strnlen.c

Purpose: compatibility implementation for bounded string length when the platform lacks `HAVE_STRNLEN`.

Important APIs, types, and functions: exports `size_t gsh_strnlen(const char *s, size_t max)`. The name is project-specific rather than overriding libc `strnlen`.

Control flow: iterates from `s` until NUL or until `max` characters have been consumed, then returns pointer distance.

State and persistence: no persistent state.

Dependencies and integration points: depends on `<sys/types.h>` and `<stdlib.h>`. Other code can use `gsh_strnlen` as a portable bounded string helper.

Risks: input must point to readable memory for at least `max` bytes or contain a prior NUL. The post-decrement loop is correct but easy to misread.

Test signals: tests should cover zero max, shorter-than-max strings, no-NUL-within-max buffers, and empty strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/strnlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/uid2grp.c -->
## sources/user-network-fs/nfs-ganesha/src/support/uid2grp.c

Purpose: resolves users, UIDs, and Kerberos principals to primary and supplementary group lists for request credential handling.

Important APIs, types, and functions: public entry points are `uname2grp`, `uid2grp`, `principal2grp`, `uid2grp_unref`, and refcount helpers. Internal allocation routines call `getpwnam_r`, `getpwuid_r`, `getgrouplist`, and optional `nfs4_gss_princ_to_grouplist`. `uid2grp_sem` throttles directory-service group list requests.

Control flow: lookup first checks `idmapping_enabled`, then the `uid2grp_cache` under read lock. Non-expired cache hits are refcounted and returned. Misses or expired entries allocate fresh `group_data`, fetch passwd and group data, add the new entry to cache under write lock, and remove expired stale entries on failure. UID failures also populate the negative UID cache.

State and persistence: returned `group_data` objects are heap-allocated with embedded user/principal name, group array, primary IDs, epoch, mutex, and refcount. Cache ownership and caller ownership share the same refcount. The data is in-memory and expires based on `manage_gids_expiration`.

Dependencies and integration points: integrates with `uid2grp_cache.c`, idmapper negative cache, pwnam wrappers, `nfs_param.directory_services_param.max_groups_membership`, auth/idmapper monitoring, LTTng tracepoints, optional libnfsidmap, and the global `idmapping_enabled` switch.

Risks: callers must always call `uid2grp_unref` after successful resolution. Directory-service calls can block and are only optionally throttled. `getpwnam_r`/`getpwuid_r` ERANGE paths return without freeing the last allocated buffer in this file's current structure. Cache insertion deliberately rechecks `idmapping_enabled` to avoid repopulating after idmapping disable. Principal lookup uses the principal string as cache uname, so principal and username namespace collisions are possible if upstream callers mix them.

Test signals: useful tests mock pwnam wrappers for success, ENOENT, ERANGE, and large group lists; verify cache hit/refcount behavior; verify stale removal; verify negative cache insertion; and exercise idmapping-disable races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/uid2grp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/uid2grp_cache.c -->
## sources/user-network-fs/nfs-ganesha/src/support/uid2grp_cache.c

Purpose: owns the in-memory user-to-group cache used by `uid2grp.c`, indexed by both username and UID with FIFO expiration/eviction order.

Important APIs, types, and functions: `struct cache_info` links UID, uname, `group_data`, two AVL nodes, and FIFO queue entry. Public functions initialize/cleanup/reap the cache, add users, look up by name or UID, detect expiration, remove by name/UID, clear all entries, and optionally expose a DBus `show_uid2grp` method.

Control flow: `uid2grp_cache_init` initializes the rwlock, optional semaphore, AVL trees, hash shortcut array, and FIFO queue. `uid2grp_add_user` inserts into name and UID trees, replaces collisions, updates the direct UID cache slot, appends to FIFO, and evicts the oldest entry if capacity is exceeded. Reaping walks FIFO from oldest until the first non-expired item. Lookups use AVL for names and a UID hash shortcut plus AVL fallback for UIDs.

State and persistence: cache state is process-memory only: `uname_tree`, `uid_tree`, `uid_grplist_cache[1009]`, `groups_fifo_queue`, and `uid2grp_user_lock`. Each cached entry holds one reference on `group_data` and releases it on removal.

Dependencies and integration points: uses Ganesha AVL, BSD tail queues, atomics for read-lock UID shortcut access, `nfs_param` directory-service cache sizing, cleanup registration, monitoring counters, and optional DBus.

Risks: all public lookup/remove calls depend on callers holding the documented lock mode. `uid_grplist_cache[uid % id_cache_size] = NULL` clears the entire slot on removal, which is safe but may drop a shortcut to a different collided UID. The DBus method uses `snprintf(..., "%s", info->uname.addr)` even though `gsh_buffdesc` names are length-bearing and not guaranteed NUL-terminated for all sources. The `show_uid2grp` method allocates with `gsh_malloc` and frees with `free`.

Test signals: tests should verify replacement by uname and UID, capacity eviction, FIFO reap stop condition, hash shortcut fallback on collision, clear-cache reference release, and DBus rendering with non-NUL-terminated names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/uid2grp_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/xprt_handler.c -->
## sources/user-network-fs/nfs-ganesha/src/support/xprt_handler.c

Purpose: manages `SVCXPRT` custom data used to track NFSv4.1 sessions associated with a transport and cleanly dissociate sessions during transport destruction.

Important APIs, types, and functions: entry points are `init_custom_data_for_xprt`, `add_nfs41_session_to_xprt`, `remove_nfs41_session_from_xprt`, `dissociate_custom_data_from_xprt`, and `destroy_custom_data_for_destroyed_xprt`. It uses `xprt_custom_data_t`, `nfs41_sessions_holder_t`, and `nfs41_session_list_entry_t`.

Control flow: initialization allocates `xp_u1`, initializes the session list/rwlock, and marks status associated. Add allocates a list entry and increments session ref before taking the lock, then denies association if the xprt is already dissociating. Remove scans the list, drops matching session refs, and updates the count. Dissociation splices the whole session list into a duplicate list under lock, marks the xprt data dissociated, then outside the lock destroys backchannels and removes session connections to avoid lock-order deadlocks. Final destroy asserts the xprt is destroyed and the list is empty, destroys the rwlock, frees custom data, and clears `xp_u1`.

State and persistence: all state is in-memory and attached to `SVCXPRT->xp_u1`. Status transitions are `ASSOCIATED_TO_XPRT`, `DISSOCIATED_FROM_XPRT`, and `DESTROYED`. Session refs are balanced on add/remove/dissociate.

Dependencies and integration points: integrates with SAL session functions, xprt tracepoints, display helpers, Ganesha list utilities, metrics, and RPC transport lifecycle.

Risks: correctness depends on all association paths checking dissociation status before adding sessions. Duplicate entries are possible if callers fail to verify non-association before `add_nfs41_session_to_xprt`. `num_sessions` is a `uint8_t`, so extreme numbers of sessions would wrap. The teardown path uses asserts heavily and assumes exact lifecycle ordering.

Test signals: valuable tests would simulate add/remove, add during dissociation denial, duplicate add behavior, dissociation lock ordering, refcount balance, and final destroy assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/xprt_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/test/CMakeLists.txt

Purpose: declares small support/unit test executables for AVL, hash/AVL, glist, URL regex, and CIDR behavior.

Important APIs, types, and functions: CMake targets are `test_avl`, `test_mh_avl`, `test_glist`, `test_url_regex`, and `test_cidr`. CUnit-based targets are guarded by `USE_CUNIT`.

Control flow: when `USE_CUNIT` is enabled, AVL tests are built `EXCLUDE_FROM_ALL` and linked with `ganesha_nfsd` and threads. Other tests are always declared `EXCLUDE_FROM_ALL`; CIDR links only `ganesha_nfsd`.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: depends on `ganesha_nfsd`, CUnit, thread libraries, and support sources such as `../support/murmur3.c`.

Risks: `EXCLUDE_FROM_ALL` means these tests will not build in default builds. Some test executables do not integrate with CTest here, so build declaration alone may not ensure automated execution.

Test signals: enables manual or CI-driven focused checks of foundational containers and parsers once explicit build/run steps include these targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/run_test_mode.sh -->
## sources/user-network-fs/nfs-ganesha/src/test/run_test_mode.sh

Purpose: launches a locally built `ganesha.nfsd` in a simple VFS export configuration suitable for presubmit protocol tests such as pynfs or cthon.

Important APIs, types, and functions: shell inputs are one `build_path`; derived paths include `ganesha.nfsd`, VFS plugin directory, temporary config/log/pid/export paths. It invokes `sudo "$GANESHA_EXE" -F -x -f ...`.

Control flow: validates argument count and executable presence, creates a temporary directory under `$HOME/ganesha-test-mode`, writes a minimal NFSv3/v4 VFS config, then runs ganesha in foreground with logging and pid file.

State and persistence: creates temporary directories and files under the user's home directory. It does not clean them up automatically because the server runs foreground and may be terminated externally.

Dependencies and integration points: depends on a completed build tree with `ganesha.nfsd` and VFS plugin, sudo privileges, VFS FSAL, and external test suites pointed at `/export`.

Risks: unquoted `mkdir --parents $EXPORT_PATH` can mis-handle spaces. It assumes plugin path layout under `FSAL/FSAL_VFS/vfs/`. Running under sudo changes permissions and environment expectations. The script uses `set -euo pipefail`, so any missing variable or command failure terminates immediately.

Test signals: useful as an integration harness rather than a unit test. Success is a running foreground server ready for external NFS test clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/run_test_mode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_avl.c -->
## sources/user-network-fs/nfs-ganesha/src/test/test_avl.c

Purpose: CUnit regression test for the project AVL tree implementation, covering insertion, lookup, traversal, deletion, minimum, supremum, and infimum behavior at several sizes.

Important APIs, types, and functions: defines `avl_unit_val_t` with `node_k`, key, and value. Uses `avltree_init`, `avltree_insert`, `avltree_lookup`, `avltree_remove`, `avltree_first`, `avltree_next`, `avltree_sup`, `avltree_inf`, and `avltree_size`. CUnit suites register tests for 1, 2, 100, 10000, random 100000 min, and supremum cases.

Control flow: each suite initializes a global tree, tests insert deterministic values, validate some lookups/traversals, delete values, and cleanup. Later tests rebuild `avl_tree_1` for delete/min scenarios and use random inserts to check tracked minimum.

State and persistence: global AVL trees store heap-allocated test nodes for each suite. Cleanup frees nodes in most cases.

Dependencies and integration points: links against `ganesha_nfsd`, `abstract_mem`, `avltree`, and CUnit via the test CMake file.

Risks: `avl_unit_clear_tree` removes nodes from `avl_tree_1` regardless of the tree argument, so it is only safe for the paths that actually use tree 1. Many "check" functions assert only `0 == 0`, so structural invariants are not deeply verified. Lookup paths dereference returned nodes without asserting non-NULL first. Random min uses `srand(time(0))`, making failures less reproducible.

Test signals: if run, it catches basic ordering/traversal/delete regressions, but it is weak for balancing invariants, duplicate insertion handling, and memory correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_cidr.c -->
## sources/user-network-fs/nfs-ganesha/src/test/test_cidr.c

Purpose: table-driven executable that exercises CIDR parsing, string formatting, and IPv4/IPv6 containment checks.

Important APIs, types, and functions: uses `cidr_from_str`, `cidr_to_str`, `cidr_contains_ip`, `cidr_free`, and `ip_str_to_sockaddr`. Test data includes invalid CIDR syntax, default masks, IPv4/IPv6 masks, IPv4-mapped IPv6, and zero masks.

Control flow: first loop parses CIDR strings and compares formatted output with expected values. Second loop parses a CIDR and an IP address, then checks containment return against expected boolean.

State and persistence: no persistent state; allocates/free CIDR objects and formatted strings per case.

Dependencies and integration points: depends on `ip_utils.h` and Ganesha memory wrappers.

Risks: failures only print messages and the program still exits with status 0, so CI will not fail unless output is inspected. The containment condition appears inverted: it prints "Failed" for `contains_ret && expected` and for `!contains_ret && !expected`, which may treat matching expected results as failures depending on `cidr_contains_ip` return convention. This test needs verification against the API contract.

Test signals: broad data coverage exists, especially for IPv6 mask edges, but executable exit semantics make the signal weak.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_cidr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_glist.c -->
## sources/user-network-fs/nfs-ganesha/src/test/test_glist.c

Purpose: manual smoke test for `gsh_list` intrusive list operations.

Important APIs, types, and functions: defines `struct myteststruct` with embedded `glist_head`. Uses `glist_init`, `glist_add`, `glist_add_tail`, `glist_del`, `glist_add_list_tail`, `glist_splice_tail`, `glist_for_each`, and `glist_entry`.

Control flow: `basic_test` adds nodes to a list, appends a tail node, deletes one, combines another list, and prints contents. `splice_tail_test` builds two 5-node lists, splices the second onto the first, and prints both. `main` runs both tests.

State and persistence: only stack-allocated nodes and two global list heads.

Dependencies and integration points: built as `test_glist` and linked with `ganesha_nfsd` and thread libraries.

Risks: there are no assertions or nonzero exits on wrong behavior; it is output-inspection based. Stack node lifetime is safe within each function but would be unsafe if retained beyond the function.

Test signals: useful for visual debugging of list order and splice behavior, not a strong automated regression test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_glist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_mh_avl.c -->
## sources/user-network-fs/nfs-ganesha/src/test/test_mh_avl.c

Purpose: CUnit test for using an AVL tree as a hash-key index with Murmur3-derived keys and probing.

Important APIs, types, and functions: `avl_unit_val_t` stores two AVL nodes, a `{k, p}` hash/probe key, a name, and an FSAL cookie. `qp_avl_insert` hashes names with `MurmurHash3_x64_128`, attempts quadratic probing, then linear probing. `qp_avl_lookup_s` repeats the probe sequence and compares names. Tests insert a fixed dir listing and then 100000 synthetic file names.

Control flow: the first phase inserts and looks up static file names. The second inserts `file0` through `file99999` and looks up `file0` through `file199999`, aborting on misses for the first half. Cleanup removes all nodes and frees duplicated names.

State and persistence: one global AVL tree contains heap nodes and duplicated strings during each suite run.

Dependencies and integration points: depends on CUnit, `avltree`, `murmur3`, and Ganesha memory wrappers. CMake includes `../support/murmur3.c` in this target.

Risks: `qp_avl_lookup_s` is called with `maxj == 1`, so it will not find entries that needed probing even though insert supports probing. Probe loops use `uint32_t j < UINT64_MAX`, which is effectively unbounded and type-mismatched. Lookup allocates many temporary `avl_unit_val_t` objects in a loop but only frees the last one, leaking test memory. `avl_unit_clear_tree` always removes from `avl_tree_1`.

Test signals: catches common no-collision lookup and large insert behavior, but collision/probing behavior is under-tested and memory usage is noisy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_mh_avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_url_regex.c -->
## sources/user-network-fs/nfs-ganesha/src/test/test_url_regex.c

Purpose: standalone regex experiment/test for decomposing RADOS object URLs and config URLs.

Important APIs, types, and functions: regexes are `RADOS_URL_REGEX` and `CONFIG_URL_REGEX`. Functions `match_dup`, `split_pool`, and `split_url` duplicate and print matched groups using POSIX regex APIs.

Control flow: `main` compiles the pool/object regex, tests four URL strings, compiles the config URL regex, and tests three quoted/unquoted `rados://` strings. Errors print and exit only on regex compilation failure.

State and persistence: two static `regex_t` objects; heap strings are freed after each match. There is no `regfree`.

Dependencies and integration points: built by test CMake and linked with `ganesha_nfsd`, though it mostly uses libc regex and malloc.

Risks: no assertions or expected-output comparison; it exits 0 even if matching behavior changes. The regexes are permissive and this file may diverge from production parser behavior if production patterns evolve.

Test signals: useful as a manual parser behavior probe. To become a regression test, it should assert captured groups and failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/test/test_url_regex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/tools/CMakeLists.txt

Purpose: top-level tools build entry point.

Important APIs, types, and functions: conditionally calls `add_subdirectory(multilock)` when `USE_TOOL_MULTILOCK` is enabled.

Control flow: there is no executable declaration in this file except the conditional subdirectory inclusion.

State and persistence: build graph only.

Dependencies and integration points: integrates with the `multilock` CMake subtree and the project option `USE_TOOL_MULTILOCK`.

Risks: tools present in this directory, such as scripts or RADOS utilities, may be built/installed elsewhere or not represented here. Enabling multilock depends entirely on the CMake option.

Test signals: build configuration can verify that toggling `USE_TOOL_MULTILOCK` includes or excludes the subdirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/findlog.sh -->
## sources/user-network-fs/nfs-ganesha/src/tools/findlog.sh

Purpose: shell utility to extract multiline function calls, primarily `Log...` calls, from C source and normalize each call onto one output line with file and line number.

Important APIs, types, and functions: configurable variables include `FUNC`, `PRINTF`, `FILES`, `TODO`, `CSCOPE`, `FINAL`, `LINESONLY`, and `DIR`. Functions include `find_funcs`, `debug_mode`, `no_xref`, `final_massage`, `final_lines_only`, `find_func_in_file`, and `find_files`.

Control flow: option parsing selects function regex, file list, cscope mode, printf mode, debug/no-xref/line-only modes, and search directory. Non-cscope mode reads file names either from a list, arguments, or `find $DIR -name '*.[ch]'`, then feeds each through sed logic that joins multiline calls until terminators. Cscope mode shells out to `cscope -d -L -0`.

State and persistence: no persistent state; output is stdout. It reads source files and optional file lists.

Dependencies and integration points: depends on POSIX shell, sed, grep, find, cat, and optionally cscope. `tools/test_findlog.c` is referenced as a behavior corpus.

Risks: many expansions are unquoted, so paths with spaces break. The sed parser is intentionally heuristic and can be confused by macros, comments, nested syntax, or function names without preceding blank/tab. Cscope mode hardcodes `Log.*` extraction in sed even when `FUNC` is changed.

Test signals: use `tools/test_findlog.c` plus representative source files to compare expected output, line-only output, no-xref output, and cscope parity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/findlog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/ganesha-rados-grace.c -->
## sources/user-network-fs/nfs-ganesha/src/tools/ganesha-rados-grace.c

Purpose: administrative CLI for inspecting and mutating the RADOS-backed grace-period database used for coordinated NFS grace handling.

Important APIs, types, and functions: `cluster_connect` creates a librados client, reads config, connects, optionally creates the pool, creates an ioctx, and sets namespace. `main` parses long options and dispatches commands to `rados_grace_dump`, `rados_grace_create`, `rados_grace_add`, `rados_grace_join_bulk`, `rados_grace_lift_bulk`, `rados_grace_enforcing_toggle`, and `rados_grace_member_bulk`.

Control flow: defaults to `dump`, with defaults for pool and oid from `rados_grace.h`. Node arguments are normalized: numeric node ids get a `node` prefix, non-numeric names are used as-is. `add` creates the pool/object if needed, then adds members. Other commands require at least one node except `dump`.

State and persistence: mutates persistent Ceph RADOS pool/object state. Local process state includes allocated node name strings and a RADOS ioctx; cleanup is minimal at process exit.

Dependencies and integration points: depends on librados, Ceph configuration, and the project's `rados_grace` support library. It is an operator-facing companion to server grace coordination.

Risks: `cluster_connect` returns early without destroying partially created RADOS handles on failure. `node_names` is not initialized when no nodes are supplied, though it is only used in node command paths. Allocation length for node names omits an explicit extra byte in the non-numeric case but uses `calloc(1, len)` and `snprintf(..., len, ...)`, truncating the final character if `len == strlen(arg)`. RADOS mutations are direct and should be used carefully.

Test signals: requires integration tests against a test Ceph cluster or mocked librados/rados_grace layer. CLI parsing can be unit-tested for node normalization and command dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/ganesha-rados-grace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/tools/multilock/CMakeLists.txt

Purpose: declares the multilock console and client tools used to drive file-locking scenarios across backends.

Important APIs, types, and functions: builds `ml_console`, `ml_posix_client`, optional `ml_cephfs_client`, and optional `ml_glusterfs_client`. Common sources are `ml_functions.c` and `multilock.h`.

Control flow: if `CEPH_FS_CEPH_STATX` is enabled, it sets `_FILE_OFFSET_BITS=64`, includes CephFS headers, builds `ml_cephfs_client`, and links CephFS libraries. If `USE_FSAL_GLUSTER AND USE_LKOWNER`, it includes GFAPI headers, builds `ml_glusterfs_client`, and links GFAPI libraries.

State and persistence: build graph only.

Dependencies and integration points: depends on math library, pthreads for clients, CephFS or GFAPI optional dependencies, and system libraries.

Risks: `add_definitions(-D_FILE_OFFSET_BITS=64)` applies directory-wide once CephFS statx is enabled. Optional client builds are tightly coupled to feature-detection variables and external library discovery.

Test signals: build matrix should cover base console/posix, CephFS-enabled, and Gluster/LKOWNER-enabled configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_cephfs_client.c -->
## sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_cephfs_client.c

Purpose: CephFS backend client for the multilock test framework. It reads commands from stdin, a script, or a console server and performs CephFS low-level file I/O and lock operations.

Important APIs, types, and functions: command handlers include `do_open`, `do_close`, `do_lock`, `do_unlock`, `do_test`, `do_list`, `do_hop`, `do_unhop`, `do_seek`, `do_read`, `do_write`, `do_alarm`, and `do_fork`. Work management uses `struct work_item`, `schedule_work`, `cancel_work`, `get_work`, and worker threads. CephFS APIs include `ceph_create`, `ceph_conf_read_file`, `ceph_mount`, `ceph_mount_perms`, `ceph_ll_walk`, `ceph_ll_create`, `ceph_ll_open`, `ceph_ll_read`, `ceph_ll_write`, `ceph_ll_lseek`, `ceph_ll_setlk`, `ceph_ll_getlk`, `ceph_ll_close`, and `ceph_ll_put`.

Control flow: `main` initializes per-file work queues, starts one polling thread and four worker threads, installs signal handlers, parses mode/options, connects to a console if requested, mounts CephFS, then loops reading and parsing multilock commands. Most commands complete synchronously. Blocking lock commands can be scheduled to worker/poll queues and later responded to when granted, denied, canceled, or interrupted.

State and persistence: global arrays map framework file positions to CephFS `Inode *`, `Fh *`, and lock mode. Global `cmount` and `cephperms` hold CephFS mount state. Work queues and per-fno lists are protected by `work_mutex` and `work_cond`. Lock state persists in the CephFS cluster and MDS lock manager, not just this process.

Dependencies and integration points: integrates with `multilock.h` parsing/responding helpers, Ganesha list macros, POSIX sockets/signals/threads, and libcephfs. It can run interactively, script-driven, or as a named client connected to `ml_console`.

Risks: worker threads are started before CephFS mount setup; they block on empty queues but share globals after initialization. `pthread_create` checks `rc == -1`, but pthread APIs return nonzero error codes rather than `-1`. `pthread_cond_timedwait` uses a relative-looking `timespec` as an absolute timeout, which is likely wrong. Many globals are unsynchronized outside work queues, relying on command sequencing. `do_read` truncates binary data by writing NUL and then using `strlen`. Fork mode with active threads and CephFS mount state is risky. Shutdown does not join threads or unmount CephFS.

Test signals: multilock sample scripts can validate POSIX/OFD lock behavior, blocking locks, cancel/unlock interactions, lock listing, hop/unhop range operations, forked clients, and CephFS-specific low-level I/O paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_cephfs_client.c -->
