# subset-b-007105 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.c

## Purpose

`glusterd-mgmt.c` implements the originator-side and peer-RPC side of GlusterD management v3 transactions. It coordinates cluster-wide administrative operations through a fixed phase pipeline: acquire local and peer locks, build a request payload, pre-validate on all eligible nodes, optionally run brick-local work, commit, optionally run post-commit work, post-validate, and release locks. The file is the transaction coordinator for operations such as snapshot, add/remove/replace/reset brick, volume start/stop, rebalance/defrag, profile, and max-op-version discovery.

## Important APIs, types, and functions

The public entry points are declared in `glusterd-mgmt.h`: `glusterd_mgmt_v3_initiate_all_phases()`, `glusterd_mgmt_v3_initiate_all_phases_with_brickop_phase()`, `glusterd_mgmt_v3_initiate_snap_phases()`, `glusterd_mgmt_v3_initiate_lockdown()`, `glusterd_mgmt_v3_pre_validate()`, `glusterd_mgmt_v3_commit()`, `glusterd_mgmt_v3_release_peer_locks()`, `glusterd_mgmt_v3_build_payload()`, and `glusterd_set_barrier_value()`. The lower-level phase functions dispatch operation-specific behavior: `gd_mgmt_v3_pre_validate_fn()` calls snapshot, replace-brick, add-brick, start/stop, remove-brick, reset-brick, profile, and rebalance staging validators; `gd_mgmt_v3_brick_op_fn()` runs snapshot/profile/rebalance brick phases; `gd_mgmt_v3_commit_fn()` performs the actual operation commit and wraps the pre-commit hook; `gd_mgmt_v3_post_commit_fn()` handles add/replace-brick post-commit brick operations; and `gd_mgmt_v3_post_validate_fn()` runs snapshot postvalidate plus volume volfile/store updates for add/start/stop paths.

Every network phase has a submit helper and callback pair, such as `gd_mgmt_v3_lock()`/`gd_mgmt_v3_lock_cbk_fn()`, `gd_mgmt_v3_pre_validate_req()`/`gd_mgmt_v3_pre_validate_cbk_fn()`, `gd_mgmt_v3_brick_op_req()`/`gd_mgmt_v3_brick_op_cbk_fn()`, `gd_mgmt_v3_commit_req()`/`gd_mgmt_v3_commit_cbk_fn()`, `gd_mgmt_v3_post_commit_req()`/`gd_mgmt_v3_post_commit_cbk_fn()`, `gd_mgmt_v3_post_validate_req()`/`gd_mgmt_v3_post_validate_cbk_fn()`, and `gd_mgmt_v3_unlock()`/`gd_mgmt_v3_unlock_cbk_fn()`. These serialize `dict_t` payloads into XDR request structs, submit to `gd_mgmt_v3_prog` via `gd_syncop_submit_request()`, unserialize response dictionaries, aggregate response dictionaries where needed, collate errors, and wake the synchronous barrier.

## Control flow

The general all-phase entry points begin by snapshotting `conf->generation` into `txn_generation` and using a read memory barrier so the peer-list view cannot be reordered. They attach `originator_uuid` and `is_synctasked` to the input dictionary, clone the dictionary into `tmp_dict` for later local unlock, acquire local and peer mgmt v3 locks, then build a phase payload. `glusterd_mgmt_v3_build_payload()` copies the input dictionary for most operations, sets volume IDs for volume-scoped operations, and adds a commit hash for rebalance.

`glusterd_mgmt_v3_pre_validate()` first enforces server quorum for selected operations, runs local prevalidation, aggregates local response data into the request dictionary for most operations, then sends prevalidation requests to connected peers that were present before `txn_generation` and are befriended except for sync-volume. The same peer eligibility pattern is repeated by brick-op, commit, post-commit, post-validate, and unlock phases.

The standard `glusterd_mgmt_v3_initiate_all_phases()` path runs lock, payload, prevalidate, commit, post-commit, postvalidate, peer unlock, local unlock, and CLI response. `glusterd_mgmt_v3_initiate_all_phases_with_brickop_phase()` inserts a brick-op phase before commit and omits the post-commit phase, matching operations whose brick work is a first-class pre-commit phase. `glusterd_mgmt_v3_initiate_snap_phases()` has snapshot-specific flow: prevalidate, snapshot quorum check, pre brick-op with `operation-type=pre`, commit with `cleanup=1`, post brick-op with `operation-type=post` to unbarrier whether commit succeeded or failed, snapshot-volume quorum check after success, postvalidate with the final result, unlock, and CLI response.

## State and persistence behavior

The coordinator mutates `dict_t` state heavily. It adds transaction metadata (`originator_uuid`, `is_synctasked`), phase hints (`operation-type`, `cleanup`), volume IDs, commit hashes, rebalance/remove-brick IDs, aggregated response keys, and sometimes barrier options. `struct syncargs` carries cross-peer phase state: aggregate `op_ret`, `op_errno`, combined `errstr`, a response dictionary protected by `lock_dict`, and the peer UUID that last replied. Peer callbacks must copy `frame->local` and `frame->cookie` before error handling because even failed RPCs need to collate into the shared `syncargs`.

Persistent effects are delegated to operation-specific commit helpers and store helpers. Add-brick postvalidation can regenerate volfiles, notify services, and persist updated `glusterd_volinfo_t` with `GLUSTERD_VOLINFO_VER_AC_INCREMENT`. `glusterd_set_barrier_value()` mutates both the request dictionary and `vol->dict`, updates op-version metadata, regenerates volfiles, and stores the volume info. Snapshot flow deliberately marks snapshot objects incomplete during commit and relies on cleanup/postvalidate paths for failure repair.

## Dependencies and integration points

This file integrates with `glusterd-syncop` for synchronous RPC barriers, `glusterd-locks` for multiple-volume mgmt v3 locks, `glusterd-op-sm` for operation-specific staging and commit functions, `glusterd-server-quorum`, `glusterd-volgen`, `glusterd-store`, snapshot utilities, hooks, and message IDs. It depends on Gluster's `dict_t`, UUID helpers, RCU peer iteration, XDR serializers for `gd1_mgmt_v3_*` messages, and the global `gd_mgmt_v3_prog` RPC program. CLI completion is handed to `glusterd_op_send_cli_response()`, while peer response dictionaries are merged by operation-specific aggregators such as `glusterd_snap_pre_validate_use_rsp_dict()`, `glusterd_rb_use_rsp_dict()`, `glusterd_aggr_brick_mount_dirs()`, and `glusterd_syncop_aggr_rsp_dict()`.

## Risks and edge cases

Lock correctness is central: any path that acquires local or peer locks must reliably execute both peer unlock and local `glusterd_multiple_mgmt_v3_unlock()`. The code does that in shared `out:` blocks, but failures before `tmp_dict` creation or after dictionary mutation can still make unlock diagnostics hard to interpret. Peer filtering by `txn_generation` avoids sending phases to newly added peers, but disconnected or late-changing peers can leave partial cluster state if a commit phase has already mutated local storage. Snapshot comments explicitly acknowledge a crash window after LVM snapshot creation but before snapshot objects are marked complete.

Response aggregation assumes callback dictionaries are valid and that each operation's aggregator tolerates missing or empty dictionaries. Some callbacks set `rsp_dict->extra_stdfree` to XDR-allocated buffers, so ownership bugs would surface as leaks or double frees. `glusterd_pre_validate_aggr_rsp_dict()` falls through from `GD_OP_RESET_BRICK` into other no-op cases after aggregation; this is intentional-looking but should remain covered because an added case could change behavior. Error strings are repeatedly duplicated and replaced; failures in `gf_asprintf()` can degrade CLI diagnostics to generic internal errors.

## Test signals

Useful tests should cover all three orchestrator entry points, phase-failure cleanup, and peer eligibility. Signals include: local prevalidation failure returns a CLI response and releases any acquired locks; peer prevalidation/commit/brick-op callback errors aggregate peer hostnames into the final error; no RPC is sent to peers with `generation > txn_generation`, disconnected peers, or non-befriended peers for non-sync-volume operations; add-brick postvalidation regenerates volfiles and persists volume info; snapshot commit failure still runs post brick-op/unbarrier and postvalidate with failure; and barrier value changes update request dict, volume dict, volfiles, and store state. Fault injection around XDR unserialize, dictionary allocation, `gd_syncargs_init()`, and RPC status `-1` would exercise the fragile cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.h

## Purpose

`glusterd-mgmt.h` exposes the management v3 transaction coordinator API implemented by `glusterd-mgmt.c`. It is the include boundary used by other GlusterD modules that need to initiate or participate in mgmt v3 operations without knowing the RPC callback internals.

## Important APIs and contracts

The header declares the operation-specific local phase dispatchers (`gd_mgmt_v3_pre_validate_fn()`, `gd_mgmt_v3_brick_op_fn()`, `gd_mgmt_v3_commit_fn()`, `gd_mgmt_v3_post_commit_fn()`, `gd_mgmt_v3_post_validate_fn()`) and the public transaction drivers (`glusterd_mgmt_v3_initiate_all_phases()`, `glusterd_mgmt_v3_initiate_all_phases_with_brickop_phase()`, `glusterd_mgmt_v3_initiate_snap_phases()`). It also exposes phase helpers for lock acquisition, payload construction, prevalidation, commit, peer-lock release, and barrier changes. Several declarations refer to operation-specific helpers implemented elsewhere, including snapshot response aggregation, reset-brick prevalidation/commit, and post-commit brick operation handling.

## Control flow represented by the header

The API shape documents the phase model: callers can either invoke a full orchestration entry point or call individual phases in sequence. The function signatures consistently pass `glusterd_op_t`, `dict_t` operation context, `char **op_errstr`, optional `uint32_t *op_errno`, and a `txn_generation` for peer-list stability. This makes the management transaction boundary explicit: the dictionary is the mutable payload, `op_errstr` is the user-visible diagnostic channel, and `txn_generation` constrains which peers participate.

## State and persistence behavior

The header itself stores no state, but its signatures reveal ownership-sensitive behavior. `glusterd_mgmt_v3_build_payload()` returns a newly referenced `dict_t **req`; error strings may be allocated into `*op_errstr`; lock functions report acquisition through `gf_boolean_t *is_acquired`; and commit/post-commit helpers can update persistent volume and snapshot state through the operation-specific implementation behind the phase dispatchers.

## Dependencies and integration points

This header depends on GlusterD core types (`glusterd_op_t`, `dict_t`, `rpcsvc_request_t`, `gf_boolean_t`, `uuid_t`, `struct syncargs`) supplied by surrounding includes before the header is consumed. It is included by `glusterd-mgmt.c` and by modules that need mgmt v3 orchestration for CLI or peer-originated operations.

## Risks and test signals

The header has no include guard dependencies beyond `_GLUSTERD_MGMT_H_`, but it relies on consumers including the right type definitions first. There is a formatting oddity: a standalone `int` line appears before `glusterd_mgmt_v3_initiate_lockdown()`, which still forms a valid declaration with the following function but is easy to break during edits. Build coverage should compile all consumers with warnings enabled, and API tests should verify callers free returned dictionaries/error strings according to implementation ownership rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.c

## Purpose

`glusterd-mountbroker.c` implements GlusterD's mountbroker support. It parses configured mount specifications, checks a user's mount request against those specifications, creates a controlled mountpoint/cookie path under `mountbroker-root`, and launches `glusterfs` with the approved mount arguments. It is designed to let limited users obtain mounts, especially geo-replication mounts, without unrestricted command execution.

## Important APIs, types, and functions

The file operates on `gf_mount_spec_t` and `gf_mount_pattern_t` from `glusterd-mountbroker.h`. `parse_mount_pattern_desc()` parses the mount-spec language into an array of patterns. Supported set relations are `SUB`, `SUP`, `EQL`, `MEET`, and `SUB+`; a leading `-` negates a pattern. `make_georep_mountspec()` builds a geo-replication-oriented specification using `georep_mnt_desc_template`, `GF_CLIENT_PID_GSYNCD`, a root user map, log directory, and one or more volume names.

Request evaluation is split into helpers. `seq_dict_foreach()` walks dictionary keys named `0`, `1`, `2`, and so on in order. `match_comp()` compares requested argument components with pattern components, treating the suffix after `=` as fnmatch-capable. `relate_sets()` computes whether the request has private elements, the pattern has private elements, and whether they share common elements. `evaluate_mount_request()` applies every pattern and returns the mapped root UID parsed from `user-map-root=...`, or a negative errno. `glusterd_do_mount()` is the exported execution path.

## Control flow

Configuration parsing starts with a descriptor string such as `SUP(...)SUB+(...)MEET(...)`. `parse_mount_pattern_desc()` counts pattern groups by closing parentheses, allocates `mspec->patterns`, parses condition names and component lists, supports `SUB+` by copying the most recent `SUP` component set into the current pattern, and stores each component as a string. On syntax errors it logs an invalid-entry message and returns `-1`.

At request time, `glusterd_do_mount()` first reads `mountbroker-root` from translator options and validates the label. It finds the matching `gf_mount_spec_t` in `priv->mount_specs`, evaluates the argument dictionary against the configured patterns, extracts `volfile-id=...`, and requires that the named volume exists and is started. It then creates or verifies a per-UID directory under the root, creates a unique temporary mount directory with `mkdtemp()`, reserves a cookie name in `MB_HIVE` with `mkstemp()`, creates a private symlink from the cookie to the mountpoint, and invokes `SBIN_DIR "/glusterfs"` with each argument converted to `--<arg>` plus the mountpoint path.

## State and persistence behavior

Mount specs are held in memory on `glusterd_conf_t::mount_specs`. The mount operation creates filesystem state under `mountbroker-root`: per-user directories named `user<uid>`, temporary mountpoint directories, cookie entries under `mb_hive`, and symlinks from cookie paths to mountpoints. On success, ownership of the cookie path is returned via `*path`; on failure, the code attempts to unlink the temporary cookie symlink, remove the temporary mountpoint, and unlink the reserved cookie file. No Gluster volume metadata is persisted by this file, but it depends on live `glusterd_volinfo_t` state to reject mounts for missing or stopped volumes.

## Dependencies and integration points

The implementation uses Gluster utility APIs (`dict_t`, `runner_t`, `gf_asprintf`, `GF_CALLOC`, `gf_strdup`, logging and message IDs), POSIX account lookup (`getpwnam()`), filesystem syscalls through Gluster wrappers, and `fnmatch()` for wildcard matching. It integrates with GlusterD options (`this->options`), private config (`THIS->private`), volume lookup (`glusterd_volinfo_find()`), started-state checks (`glusterd_is_volume_started()`), and the `glusterfs` binary path from `SBIN_DIR`.

## Risks and edge cases

The parser mutates the descriptor string in place by replacing separators with NUL or spaces, so callers must pass mutable storage. Syntax and allocation failure cleanup is intentionally incomplete because comments assume termination on parse failure; that is a leak risk if parsing becomes recoverable. `make_georep_mountspec()` sets `ret = -1` if any of its temporary buffers are NULL during cleanup, which means a partially successful path with an optional NULL would be treated as failure; in the current flow all three are expected after success.

Mount execution is security-sensitive. Correctness depends on matching only approved `--` arguments, finding exactly one valid `user-map-root`, checking per-user directory mode/owner/group, and not following attacker-controlled paths. The code uses `mkdtemp()`, `mkstemp()`, `lstat()`, `chown()`, and strict mode checks, but failure cleanup manipulates `mtptemp` by toggling the hidden `/cookie` suffix and assumes `cookieswitch` was initialized. Tests should cover failures before and after `cookieswitch` assignment. `seq_dict_foreach()` stops at the first missing numeric key, so sparse argument dictionaries silently ignore later keys.

## Test signals

Focused tests should cover parsing of empty descriptors, valid `SUB`/`SUP`/`EQL`/`MEET`/negated/`SUB+` descriptors, malformed descriptors with `&`, missing parentheses, and wildcard matching after `=`. Request tests should verify label miss, missing `mountbroker-root`, empty label, missing `volfile-id`, stopped/missing volume, ambiguous or nonexistent `user-map-root`, sparse dict keys, and mismatched set relations. Filesystem integration tests should assert user directory attributes, cookie symlink layout under `mb_hive`, glusterfs runner arguments, and cleanup after failures at mkdir, mkdtemp, mkstemp, symlink/rename, and runner execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.h

## Purpose

`glusterd-mountbroker.h` defines the data model and public functions for GlusterD mountbroker support. It is the contract between mountbroker configuration parsing/evaluation and the rest of GlusterD.

## Important APIs and types

`MB_HIVE` names the cookie directory `mb_hive` under the configured mountbroker root. `gf_setrel_t` enumerates supported set relations: `SET_SUB`, `SET_SUPER`, `SET_EQUAL`, and `SET_INTERSECT`. `gf_mount_pattern_t` stores one parsed relation: a NULL-terminated component array, the relation condition, and a boolean negation flag. `gf_mount_spec_t` stores a list node, label, array of parsed patterns, and pattern count.

The public functions are `parse_mount_pattern_desc()`, which parses a mutable descriptor string into `gf_mount_spec_t`; `make_georep_mountspec()`, which constructs a geo-replication-safe spec; and `glusterd_do_mount()`, which evaluates a labeled request dictionary and returns a cookie path for the resulting mount.

## Control flow and state contract

Callers create or populate `gf_mount_spec_t` records, parse descriptor strings into their `patterns` arrays, link specs onto `glusterd_conf_t::mount_specs`, and later call `glusterd_do_mount()` with a label and ordered argument dictionary. The header makes the ownership model implicit: parsed components and pattern arrays are dynamically allocated by the parser, and `glusterd_do_mount()` returns a dynamically allocated `*path` on success.

## Dependencies and integration points

The structs depend on Gluster list and boolean types (`struct cds_list_head`, `gf_boolean_t`) and Gluster dictionaries for request arguments. The implementation integrates with GlusterD volume state, mountbroker translator options, filesystem syscalls, and the `glusterfs` runner.

## Risks and test signals

The header has no include guard, so repeated inclusion depends on the build's existing include ordering and should be treated carefully. The parser API requires mutable descriptor strings; passing string literals would be unsafe. Tests should compile multiple consumers, validate that parsed specs remain NULL-terminated, and assert that callers free mount spec allocations and returned cookie paths through the expected Gluster allocator conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.c

## Purpose

`glusterd-nfs-svc.c` wires the legacy Gluster NFS service into GlusterD's generic service-management framework. It is compiled only when `BUILD_GNFS` is defined. The file decides whether the NFS service should run, generates the NFS volfile, starts/stops the service, deregisters portmap entries when stopping, and reconfigures or restarts NFS when volume topology/options change.

## Important APIs and functions

`glusterd_nfssvc_build()` is the public builder that installs service callbacks into a `glusterd_svc_t`: manager, start, and stop. `glusterd_nfssvc_reconfigure()` is the public reconfiguration entry point. Internal helpers include `glusterd_nfssvc_need_start()`, which scans all volumes and returns true when at least one started volume has NFS enabled; `glusterd_nfssvc_create_volfile()`, which builds the service volfile path and calls `glusterd_create_global_volfile(build_nfs_graph, ...)`; `glusterd_nfssvc_manager()`, which initializes/stops/regenerates/starts/connects the service as needed; `glusterd_nfssvc_start()`, a thin wrapper over `glusterd_svc_start()`; and `glusterd_nfssvc_stop()`, which calls `glusterd_svc_stop()` and deregisters NFS pmap if the process had been running.

## Control flow

The manager lazily initializes the service with name `nfs`, kills any existing instance, treats missing `XLATORDIR "/nfs/server.so"` as a soft nonfatal condition, writes a fresh global NFS volfile, and starts/connects the service only if `glusterd_nfssvc_need_start()` finds an eligible started volume. Reconfiguration first validates private config and checks for the NFS xlator. It exits successfully if no volume is started. It then compares the generated NFS volfile with the active one by content. If identical, it does nothing. If only topology is identical but options differ, it rewrites the volfile and sends `glusterd_fetchspec_notify()` so the service can reconfigure. If topology differs, it calls the service manager with `PROC_START_NO_WAIT` to restart NFS.

## State and persistence behavior

The file mutates `glusterd_svc_t` callback fields and `svc->inited`, starts/stops `svc->proc`, connects `svc->conn`, and writes the generated NFS service volfile under the GlusterD workdir. It reads each `glusterd_volinfo_t` status and volume dictionary option `NFS_DISABLE_MAP_KEY`; the default value of `1` means volumes are treated as NFS-disabled unless the option is explicitly false. Stopping an active service deregisters NFS from pmap to avoid stale port mappings.

## Dependencies and integration points

The code depends on generic service management (`glusterd-svc-mgmt`, `glusterd-svc-helper`), volfile generation (`glusterd-volgen`, `build_nfs_graph`), process and connection helpers, event emission (`gf_event(EVENT_SVC_MANAGER_FAILED, ...)`), Gluster syscall wrappers, and the install path for the NFS server xlator. It is integrated from the GlusterD service initialization path through `glusterd_nfssvc_build()`.

## Risks and edge cases

Because the manager stops the existing service before checking whether `nfs/server.so` is installed or writing the new volfile, missing xlator or volfile-generation failure can leave NFS stopped. This is probably deliberate for clean reconfiguration but is operationally visible. `glusterd_nfssvc_need_start()` starts the service if any started volume has NFS enabled, so option defaults and volume dictionaries must be correct. Reconfigure relies on volfile equivalence and topology comparison helpers; false positives can skip needed restarts, while false negatives can restart unnecessarily.

## Test signals

Tests should cover build-time exclusion without `BUILD_GNFS`, manager initialization, missing xlator soft success/failure behavior, no eligible volumes, one started NFS-enabled volume, stop pmap deregistration only when process was running, identical volfile no-op, options-only reconfigure through fetchspec notify, topology-change restart, and failure event emission when manager operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.h

## Purpose

`glusterd-nfs-svc.h` exposes the legacy Gluster NFS service integration points. Its declarations are guarded by `BUILD_GNFS`, matching the conditional implementation in `glusterd-nfs-svc.c`.

## Important APIs

When `BUILD_GNFS` is enabled, the header declares `glusterd_nfssvc_build(glusterd_svc_t *svc)` to install NFS service callbacks and `glusterd_nfssvc_reconfigure(void)` to compare/regenerate/reconfigure or restart the running service. It includes `glusterd-svc-mgmt.h` for `glusterd_svc_t`.

## Control flow and state contract

Consumers call `glusterd_nfssvc_build()` during service setup, then invoke `glusterd_nfssvc_reconfigure()` after volume option or topology changes that may affect the NFS graph. The header makes NFS support a compile-time feature: callers must either be inside `#ifdef BUILD_GNFS` or tolerate the declarations being absent.

## Dependencies and integration points

The header depends on the generic GlusterD service-management type definitions. Its implementation integrates with volfile generation, service process lifecycle, pmap deregistration, and `nfs/server.so` availability.

## Risks and test signals

The main risk is build-configuration drift: code that calls these functions without the same `BUILD_GNFS` guard will fail in GNFS-disabled builds. Build matrix coverage should compile both GNFS-enabled and disabled configurations. Functional tests should verify that service callback wiring and reconfiguration behavior are reachable only in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-nfs-svc.h -->
