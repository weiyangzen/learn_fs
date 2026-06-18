# subset-b-007864 Research

Grouped research for the requested OrangeFS protocol and server sources. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-req-proto.h -->
# sources/distributed-fs/orangefs/src/proto/pvfs2-req-proto.h

## Purpose
Defines the OrangeFS/PVFS2 server wire request protocol. The file assigns stable numeric server operation codes, protocol version numbers, request-size limits, per-operation request and response structures, encode/decode macros, extra-buffer sizing macros, and client-side fill macros for constructing `PVFS_server_req` messages. It is the central ABI contract shared by clients, servers, generated encoders, and server dispatch.

## Important APIs, Types, And Functions
The top-level protocol constants are `PVFS2_PROTO_MAJOR`, `PVFS2_PROTO_MINOR`, `PVFS2_PROTO_VERSION`, `PINT_SMALL_IO_MAXSIZE`, and many `PVFS_REQ_LIMIT_*` bounds for paths, layouts, key/value lists, handles, directory entries, security material, and management arrays. `enum PVFS_server_op` assigns operation numbers from `PVFS_SERV_CREATE` through `PVFS_SERV_MGMT_GET_USER_CERT_KEYREQ`; its order must match `PINT_server_req_table` in `pvfs2-server-req.c`.

The file declares per-op structs such as `PVFS_servreq_create`, `PVFS_servreq_io`, `PVFS_servreq_small_io`, `PVFS_servreq_mkdir`, `PVFS_servreq_tree_remove`, `PVFS_servreq_mgmt_split_dirent`, and matching `PVFS_servresp_*` payloads. Most are bound to generated-style `endecode_fields_*_struct` macros. Complex variable payloads, including mirror, normal I/O, small I/O, and certificate requests, provide explicit `encode_*` and `decode_*` macros under `__PINT_REQPROTO_ENCODE_FUNCS_C`. `PVFS_REQ_COPY_CAPABILITY` copies capabilities into outgoing requests, and `PINT_SERVREQ_*_FILL` macros initialize operation-specific request fields.

## Control Flow
This header does not run control flow itself; it defines how control moves over the network. A caller fills a `PVFS_server_req` by selecting an op code, copying a capability and hints, and assigning the union member matching the op. Encoding first emits the generic request header (`op`, padding, capability, hints), then the op-specific payload selected by `op`. Server-side decoding reconstructs the generic request and leaves dispatch to `pvfs2-server.c`/`pvfs2-server-req.c`.

For normal and small I/O, decode macros also unpack nested `PINT_Request` structures so later state machines can traverse the file-request tree. Small-write request decoding points `buffer` directly into the decoded message body instead of copying it, so state-machine lifetime must keep the decoded buffer alive. Management, tree, directory, key/value, and security requests all follow the same pattern: bounded variable-length arrays are represented by pointer/count pairs and sized by companion `extra_size_*` macros.

## State And Persistence
No persistent state is stored in this header. Its persistent effect is protocol compatibility: op values, struct fields, field order, alignment skips, extra-size bounds, and protocol version numbers become durable wire-format commitments. The generic `PVFS_server_req` and `PVFS_server_resp` unions define the in-memory decoded state carried by server operation state machines.

## Dependencies And Integration Points
The header integrates with `pvfs2-types.h`, `pvfs2-attr.h`, `pint-distribution.h`, `pvfs2-request.h`, `pint-request.h`, `pvfs2-mgmt.h`, `pint-hint.h`, UID/security headers, and the generated encoding system. Server dispatch in `pvfs2-server-req.c` must stay synchronized with `enum PVFS_server_op`. State machines and client system-interface code depend on the fill macros and specific union member names.

## Risks And Test Signals
The largest risk is ABI drift: changing an op number, field order, size limit, or encode/decode behavior without a coordinated protocol version bump can break mixed client/server deployments. Several fill macros mutate or copy caller-provided attribute structures, so callers must understand ownership and side effects. The small I/O decode path depends on decoded-message lifetime and correct `total_bytes` validation. The macro `PVFS_REQ_LIMIT_DFILE_COUNT_IS_VALID` rejects exactly `PVFS_REQ_LIMIT_DFILE_COUNT`, which is intentional only if the maximum is exclusive. Test signals include request encode/decode round trips for every op, mixed-endian key/value and ACL payloads, max-size boundary tests for variable arrays, small I/O read/write payload lifetime tests, and build checks that `PVFS_SERV_NUM_OPS` still matches the request table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/pvfs2-req-proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/check.c -->
# sources/distributed-fs/orangefs/src/server/check.c

## Purpose
Implements server-side permission utilities. It converts Unix mode bits and POSIX-style ACLs into OrangeFS capability masks, validates that an incoming capability covers the handle being operated on, and delegates the final operation-specific permission decision to the state-machine metadata registered for the request.

## Important APIs, Types, And Functions
`PINT_get_capabilities` computes `PINT_CAP_READ`, `PINT_CAP_WRITE`, `PINT_CAP_EXEC`, `PINT_CAP_SETATTR`, `PINT_CAP_CREATE`, and `PINT_CAP_REMOVE` for a user, group list, object attributes, and optional ACL buffer. `PINT_perm_check` is the main operation guard used by server state machines. Local helpers are `check_mode`, `check_acls`, and `check_seteattr_dir_hint`. `enum access_type` maps internal read/write/execute checks to mode-bit tests.

## Control Flow
`PINT_get_capabilities` grants UID 0 all capabilities, then removes directory-only capabilities for non-directory objects. For non-root users it first attempts ACL grants for read, write, and execute; then it validates that group data and object GID are present, selects the object's active group from the caller group list, evaluates Unix mode bits through `check_mode`, adds `SETATTR` for the owner, and adds create/remove when a directory has both write and execute capability.

`PINT_perm_check` looks up the request's permission function through `PINT_server_req_get_perm_fun`. If the request carries a non-null capability, it chooses the handle that must be covered: remove/tree-remove and I/O/small-I/O use the handle stored in hints, special directory-hint `seteattr` may use the parent hint, and most operations use `s_op->target_handle`. It then scans `cap->handle_array` for that handle and returns `-PVFS_EACCES` if missing. Finally it calls the op-specific permission function and returns that result.

`check_acls` validates the ACL buffer shape, byte-swaps ACL entries from LEBF/network order, scans user/group entries, applies an ACL mask where needed, and returns `0`, `-PVFS_EACCES`, or `-PVFS_EINVAL`. `check_mode` validates the attr mask and checks owner, group, or other bits for the requested access.

## State And Persistence
The file stores no persistent state. It reads request state (`PINT_server_op`, `PVFS_server_req`, hints, capabilities), object attributes, ACL buffers, and caller credential/group arrays. `PINT_get_capabilities` writes only the caller-supplied `op_mask`; `PINT_perm_check` logs diagnostic information and returns permission status.

## Dependencies And Integration Points
The implementation depends on `pvfs2-server.h`, `pvfs2-attr.h`, server configuration/Trove headers, `pint-perf-counter.h`, `bmi-byteswap.h`, `security-util.h`, capability helpers, hints, and request metadata from `pvfs2-server-req.c`. It is part of the authorization path for generated server state machines and relies on each operation's `PINT_server_req_params` to supply the correct permission function.

## Risks And Test Signals
Permission bugs here have direct security impact. `check_seteattr_dir_hint` appears suspicious: it returns false if a key differs from any one of the three accepted hint names, which means ordinary single-name strings cannot satisfy the "all keys are dir hints" intent. That may force `seteattr` to validate the target handle instead of the parent for directory hint attributes. ACL scanning assumes canonical ACL ordering and treats some orderings as invalid. Tests should cover root/non-root capability generation, owner/group/other mode bits, ACL user/group/mask/other combinations, missing attr mask fields, missing hint handles for remove/I/O/seteattr, capability handle-array rejection, and the special `user.pvfs2.num_dfiles`, `user.pvfs2.dist_name`, and `user.pvfs2.dist_params` seteattr path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/check.h -->
# sources/distributed-fs/orangefs/src/server/check.h

## Purpose
Declares the server permission-checking API implemented by `check.c`.

## Important APIs, Types, And Functions
The header exports `PINT_perm_check(struct PINT_server_op *s_op)` for operation-level authorization and `PINT_get_capabilities(...)` for deriving a capability mask from ACL/mode/credential inputs. It includes `pvfs2-types.h`, `pvfs2-attr.h`, and `pvfs2-server.h` so callers see the required OrangeFS object, attribute, and server-op types.

## Control Flow
No control flow is implemented in the header. Server state-machine code includes it to call `PINT_perm_check`, while capability-producing code calls `PINT_get_capabilities` after fetching object attributes and optional ACL data.

## State And Persistence
The header declares no state. Its API surfaces transient request state, object attributes, ACL buffers, group arrays, and output capability masks.

## Dependencies And Integration Points
This is the public boundary between generated/manual server state machines and the permission helper module. It must remain consistent with `check.c` and with struct definitions in `pvfs2-server.h` and `pvfs2-attr.h`.

## Risks And Test Signals
Risks are declaration drift and accidental inclusion cycles because the header includes broad server definitions. Compile coverage of server state machines and permission unit/integration tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/config-utils.c -->
# sources/distributed-fs/orangefs/src/server/config-utils.c

## Purpose
Provides a tiny global accessor layer for the active `server_configuration_s` pointer.

## Important APIs, Types, And Functions
`PINT_get_server_config` returns the static `server_config` pointer. `PINT_set_server_config` assigns it. The file includes `<stddef.h>` and `config-utils.h`.

## Control Flow
There is no complex control flow. Code that owns or initializes a server configuration calls `PINT_set_server_config`, and consumers call `PINT_get_server_config` to retrieve the currently installed pointer.

## State And Persistence
The only state is the process-global static pointer `server_config`. The file does not allocate, copy, retain, or free the pointed-to configuration. Lifetime remains the caller's responsibility, so stale pointers are possible if the original configuration is released or replaced without coordination.

## Dependencies And Integration Points
This module integrates with server configuration structures defined elsewhere and offers a lightweight alternative to passing the configuration pointer through every call path. It is listed in `module.mk.in` as part of `SERVERSRC`.

## Risks And Test Signals
The main risk is global mutable state with no locking or ownership semantics. Tests should ensure callers initialize the pointer before use and avoid dereferencing it after `PINT_config_release` or reload cleanup. Compile/link tests should catch signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/config-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/config-utils.h -->
# sources/distributed-fs/orangefs/src/server/config-utils.h

## Purpose
Declares the process-global server-configuration accessor functions implemented by `config-utils.c`.

## Important APIs, Types, And Functions
The header forward-declares `struct server_configuration_s` usage through the prototypes `PINT_get_server_config(void)` and `PINT_set_server_config(struct server_configuration_s *cfg_p)`.

## Control Flow
No control flow is implemented. Callers include this header when they need to publish or retrieve the active server configuration pointer.

## State And Persistence
The header stores no state; it exposes access to a global pointer managed by the implementation.

## Dependencies And Integration Points
It avoids including the full server-configuration definition, which keeps dependency weight low for consumers that only pass pointers. It must stay in sync with `config-utils.c` and the actual configuration type name.

## Risks And Test Signals
The risk is mostly API misuse: callers can retrieve NULL before initialization or keep using a pointer after owner cleanup. Build coverage and startup tests that initialize configuration before dependent modules run are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/config-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/module.mk.in -->
# sources/distributed-fs/orangefs/src/server/module.mk.in

## Purpose
Defines the Autotools make fragment for building OrangeFS server sources when `BUILD_SERVER` is enabled. It enumerates generated state-machine C files, manually maintained server support files, server binary sources, special include flags, and optional backtrace/security certificate additions.

## Important APIs, Types, And Functions
The fragment sets `DIR := src/server`, builds `SERVER_SMCGEN` with many generated `.c` files such as `create.c`, `lookup.c`, `io.c`, `small-io.c`, `mgmt-create-root-dir.c`, and `mgmt-split-dirent.c`, appends those files to `SERVERSRC`, adds `check.c` and `config-utils.c`, tracks generated files through `SMCGEN`, and adds `pvfs2-server.c` plus `pvfs2-server-req.c` to `SERVERBINSRC`. Conditional blocks use `BUILD_SERVER`, `ENABLE_SECURITY_CERT`, and `PVFS2_SEGV_BACKTRACE`.

## Control Flow
At configure/make time, the surrounding build system substitutes `@BUILD_SERVER@` and `@PVFS2_SEGV_BACKTRACE@`. If server builds are enabled, this fragment contributes generated state-machine files to the server library, links daemon-only files separately, optionally includes `mgmt-get-user-cert.c`, and applies `-D__PVFS2_SEGV_BACKTRACE__` to `pvfs2-server.c` when requested.

## State And Persistence
The file affects build state rather than runtime state. It records which generated artifacts are considered part of the server and which are cleaned during dist-clean via `SMCGEN`.

## Dependencies And Integration Points
It integrates the server directory with the top-level build system, the state-machine generator, optional certificate-security code, Trove handle-management include paths for `statfs.c`, and the backtrace code guarded in `pvfs2-server.c`. Its file list must match actual generated state machines and request-table entries.

## Risks And Test Signals
Risks include missing a generated state-machine source when a new protocol op is added, including a request-table entry whose state-machine object is not linked, stale conditional coverage for `ENABLE_SECURITY_CERT`, and dist-clean missing generated files. Test signals include full server builds with and without `BUILD_SERVER`, certificate support, and segv backtrace; clean/distclean runs; and link checks that all `pvfs2_*_params` references in `pvfs2-server-req.c` resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server-req.c -->
# sources/distributed-fs/orangefs/src/server/pvfs2-server-req.c

## Purpose
Maps decoded protocol operation numbers to server request parameters and exposes small accessor helpers used by dispatch, scheduling, permission checking, object lookup, credential extraction, and debugging.

## Important APIs, Types, And Functions
`PINT_server_req_table[]` is the central table, indexed directly by `enum PVFS_server_op`. Each entry stores the op type and a `PINT_server_req_params *` from the operation's state-machine module. Exported helpers are `PINT_server_req_readonly`, `PINT_server_req_modify`, `PINT_server_req_get_perm_fun`, `PINT_server_req_get_access_type`, `PINT_server_req_get_sched_policy`, `PINT_server_req_get_object_ref`, `PINT_server_req_get_credential`, and `PINT_map_server_op_to_string`. `CHECK_OP` asserts that the enum value matches the table slot.

## Control Flow
When a request is decoded, server code uses the request's `op` as an array index. Accessor functions assert table alignment, then read function pointers from `params`. If no access-type callback exists, access defaults to readonly. If no object-ref or credential callback exists, output references or credentials are set to zero/NULL and success is returned. `PINT_map_server_op_to_string` returns the static `string_name` stored in the params for logging.

## State And Persistence
The table is process-static runtime metadata, not persistent storage. It binds op numbers to state machines, scheduling policies, permission callbacks, object-reference extractors, credential extractors, and names. Some management operations intentionally have `NULL` params or optional certificate params depending on `ENABLE_SECURITY_CERT`.

## Dependencies And Integration Points
The file depends on `pvfs2-server.h`, `pvfs2-internal.h`, and every generated/manual server state-machine module that exports a `pvfs2_*_params` symbol. `pvfs2-server.c` uses this table via `server_op_state_get_machine`, permission code uses `PINT_server_req_get_perm_fun`, and request scheduling uses the access/schedule metadata.

## Risks And Test Signals
Because the table is indexed by protocol enum value, any mismatch with `pvfs2-req-proto.h` can dispatch a request to the wrong state machine. Helpers dereference `params` without guarding every NULL case, so ops with NULL params must not be passed to helpers that require them. `CHECK_OP` is an `assert`, so release builds may lose protection. Test signals include compile/link checks for every extern params symbol, startup dispatch tests for every implemented op, assertions under debug builds, certificate-enabled and certificate-disabled builds, and negative tests for unsupported/null-param operations such as write completion or disabled certificate management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server-req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server-stub -->
# sources/distributed-fs/orangefs/src/server/pvfs2-server-stub

## Purpose
Provides a shell wrapper that sets `LD_ASSUME_KERNEL=2.2.5` before launching the real server binary `pvfs2-server.bin` from the same directory.

## Important APIs, Types, And Functions
The script uses `/bin/bash`, exports `LD_ASSUME_KERNEL`, derives `SERVER_PATH` with ``dirname $0``, and executes `$SERVER_PATH/pvfs2-server.bin $@`.

## Control Flow
Invocation flows directly through the wrapper: set environment, find sibling binary directory, and call the binary with all original arguments.

## State And Persistence
No persistent state is written. The only runtime state change is the exported environment variable inherited by `pvfs2-server.bin`.

## Dependencies And Integration Points
It depends on Bash, a sibling `pvfs2-server.bin`, and historical Linux/glibc behavior controlled by `LD_ASSUME_KERNEL`. It integrates with packaging or launcher paths that invoke `pvfs2-server` through this wrapper instead of the raw binary.

## Risks And Test Signals
The wrapper does not quote `$SERVER_PATH` or `$@`, so paths or arguments containing whitespace can be split incorrectly. `LD_ASSUME_KERNEL=2.2.5` is obsolete on modern systems and may be ignored or harmful depending on libc. Test signals include launching with normal config arguments, install paths containing spaces, argument preservation tests, and validation on target runtime distributions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server-stub -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server.c -->
# sources/distributed-fs/orangefs/src/server/pvfs2-server.c

## Purpose
Implements the OrangeFS server daemon. It parses command-line/configuration input, optionally creates or removes storage space, initializes security, network, storage, flow, job, scheduler, performance, UID, cached-config, and precreate-pool subsystems, posts BMI unexpected receives, drives server state machines from the job loop, handles signals and limited live config reload, and shuts subsystems down in dependency order.

## Important APIs, Types, And Functions
The main entry is `main`. Initialization is split across `server_initialize`, `server_initialize_subsystems`, `server_setup_process_environment`, `server_setup_signal_handlers`, and `server_check_if_root_directory_created`. Runtime dispatch uses `server_post_unexpected_recv`, `server_state_machine_start`, `server_state_machine_alloc_noreq`, `server_state_machine_start_noreq`, `server_state_machine_complete`, `server_state_machine_complete_noreq`, `server_state_machine_terminate`, and `server_op_state_get_machine`. Shutdown/reload helpers include `server_shutdown`, `server_sig_handler`, `hup_sighandler`, `reload_config`, and optional `bt_sighandler`. Precreated handle support is implemented by `precreate_pool_initialize`, `precreate_pool_setup_server`, `precreate_pool_count`, `precreate_pool_launch_refiller`, and `precreate_pool_finalize`. Utility functions include pidfile management, `generate_shm_key_hint`, `server_perf_start_rollover`, `trove_coll_to_method_callback`, `PINT_server_access_debug`, `keep_keyval_buffers`, and `free_keyval_buffers`.

## Control Flow
`main` initializes logging, parses options, parses and validates configuration, handles `-r` and `-f` storage-space commands, allocates job result arrays, then calls `server_initialize`. After initialization it starts a no-request job timer state machine, checks/creates distributed root directory metadata, and enters an infinite `job_testcontext` loop. Completed jobs resume state machines through `PINT_state_machine_continue`; state-machine errors are logged and the loop continues unless the job layer itself fails.

`server_initialize` validates log output, daemonizes and redirects I/O when requested, initializes security/caches, calls `server_initialize_subsystems`, posts the configured number of unexpected BMI receive state machines, and installs signal handlers. `server_initialize_subsystems` initializes events, distributions, encoders, BMI, cached config, Trove collections/contexts and per-filesystem storage hints, flow, job time manager, job context, request scheduler, performance counters, UID management, and precreate pools. File-system initialization loads handle mappings, verifies stored collection IDs against configuration, registers handle ranges and cache/coalescing/sync settings, and passes data-sync settings to the flow layer.

Request dispatch starts with `server_post_unexpected_recv`, which allocates a BMI unexpected SMCB and adds its `PINT_server_op` to `posted_sop_list`. When a message arrives, `server_state_machine_start` decodes it into a `PVFS_server_req`, switches protocol errors to the protocol-error state machine, sets the operation on the SMCB, adds server-id/op-id hints, moves the op to `inprogress_sop_list`, starts tracing/perf timing, records address/tag, and invokes the selected state machine. Completion releases hints/decoded buffers, frees the BMI unexpected buffer, decrements the BMI address reference, removes the op from in-progress, and terminates/free the SMCB.

Signal handling sets `signal_recvd_flag` in the controlling process and cancels posted unexpected receives so shutdown drains only in-progress operations. `SIGHUP` is special: the main loop calls `reload_config`, which reparses the config and updates event logging, timeout bypass, squashing/read-only/trusted settings, and anonymous IDs in place, then reopens the log. Other signals trigger shutdown once `inprogress_sop_list` drains. `server_shutdown` uses `server_status_flag` bits to finalize only initialized subsystems in a mostly reverse order.

Precreate-pool initialization runs for metadata servers. It enumerates peer servers per filesystem, determines which object types each peer needs, ensures a persistent pool object exists by filesystem extended attribute key `precreate-pool-<host>-<type>`, counts handles already in the pool, registers the pool with the job layer, and launches no-request refiller state machines when configured batch sizes are nonzero.

## State And Persistence
Important process state includes `server_config`, `s_server_options`, `fs_conf`, `server_status_flag`, signal flags, global job arrays, `server_job_context`, posted/in-progress/no-request operation lists, `PINT_sm_event_id`, and Trove common/special key tables. Persistent storage is managed through Trove collections under configured data/meta paths. The daemon may create or remove storage spaces, validate collection IDs, create distributed root-directory metadata, create internal precreate-pool objects, and store pool handles as filesystem extended attributes. Pidfiles are created/deleted when requested. SIGHUP mutates selected configuration fields in memory but does not rewrite config files.

## Dependencies And Integration Points
This file is the integration hub for BMI networking, Trove storage, flow protocols, request scheduler, job layer, state-machine engine, generated request encoders (`__PINT_REQPROTO_ENCODE_FUNCS_C`), cached config, server config manager, security/capability/credential/certificate caches, UID management, performance counters, event tracing, distribution utilities, and generated server state machines. It depends on `PINT_server_req_table` from `pvfs2-server-req.c` for op-to-state-machine mapping and on config parsing/validation from server-config modules.

## Risks And Test Signals
High-risk areas include initialization ordering, partial-initialization cleanup, signal-time cancellation, no-request state-machine lifetime, decoded-buffer lifetime for in-place payloads, and precreate-pool persistence. `reload_config` has a likely traversal bug where the inner filesystem loop assigns `hup_filesystems = PINT_llist_head(hup_filesystems)` instead of advancing with `PINT_llist_next`, which can break matching beyond the first filesystem. `precreate_pool_initialize` has several error paths that return without freeing `addr_array`, and its debug log prints `pool_handle` before setup assigns it. The shell-like daemonization path also changes cwd to `/`, so relative paths must already be normalized.

Useful test signals include foreground/background startup, pidfile write/remove, `-f` and `-r` storage operations, invalid collection/config mismatch handling, full startup with multiple filesystems and mixed meta/IO roles, root-directory auto-creation, request decode/dispatch for representative ops, protocol-mismatch response, graceful SIGTERM drain, SIGHUP reload of logging/squash/read-only/trusted settings, precreate-pool creation/refill across peer servers, shutdown after partial initialization failures, and builds with/without security caches, cert support, perf counters, event tracing, and segv backtrace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/server/pvfs2-server.c -->
