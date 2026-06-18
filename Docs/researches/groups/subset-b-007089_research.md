# subset-b-007089 research

Grouped research for the GlusterFS bit-rot daemon/stub files and changelog library files listed in work item `subset-b-007089`. Each section is bounded for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.c

Purpose: this is the main bit-rot daemon xlator implementation. It runs in one of two modes, signer or scrubber, over child brick client xlators. In signer mode it subscribes to changelog release events from each brick, delays or queues signing work, reads object contents, calculates SHA256 checksums, and writes signatures back through bit-rot-stub controlled xattrs. In scrubber mode it delegates scanning and verification to the scrubber support code while sharing child connection, status, and monitor lifecycle logic.

Important APIs and functions: `init`, `fini`, `notify`, `reconfigure`, and `mem_acct_init` form the xlator entry points. `br_brick_connect` discovers a brick export path and stub boot time through `GLUSTERFS_GET_BR_STUB_INIT_TIME`, then calls `br_enact_signer` or `br_enact_scrubber`. Signer work flows through `br_brick_callback`, `br_initialize_object`, `br_initialize_timer`, `br_add_object_to_queue`, `br_process_object`, and `br_sign_object`. Object signing itself uses `br_object_lookup`, `br_object_open`, `br_calculate_obj_checksum`, `br_object_read_sign`, and `br_prepare_signature`. One-shot catch-up signing is implemented by `br_oneshot_signer` and `bitd_oneshot_crawl`. Scrub status and on-demand scrub commands are handled through `br_scrubber_status_get` and the `GF_EVENT_SCRUB_*` cases in `notify`.

Control flow: child up/down notifications are not processed inline. `notify` maps the child xlator to a `br_child_t`, updates `child_up` and `up_children`, queues a `br_child_event` in `priv->bricks`, and wakes `br_handle_events`. That event thread calls either `br_brick_connect` or `br_brick_disconnect`. In signer mode, a successful connect registers a `gf_brick_spec` with `gf_changelog_register_generic` for `CHANGELOG_OP_TYPE_BR_RELEASE`, then starts an initial crawler. Release events from bit-rot-stub call `br_brick_callback`; `BR_SIGN_REOPEN_WAIT` events are delayed in the timer wheel, while other events are quick-queued. Worker threads wait on `priv->object_cond`, pop `br_object_t` instances, and sign them.

State and persistence behavior: persistent object state is not owned by this file directly. It writes persistent signatures through `GLUSTERFS_SET_OBJECT_SIGNATURE`, which bit-rot-stub converts into `BITROT_SIGNING_VERSION_KEY` on disk. It also sends reopen/resign hints through `BR_REOPEN_SIGN_HINT_KEY` to drive stub state transitions. In-memory state includes child connection state, `priv->bricks` event queue, `priv->signing`, timer-wheel entries, signer object queue, token bucket throttling, scrub monitor state, and per-child inode tables. `br_object_sign_softerror` treats ENOENT, ESTALE, and ENODATA as expected races because files may disappear or lack xattrs while signing catches up.

Dependencies and integration points: the file depends on GlusterFS syncop APIs, inode/fd/lru infrastructure, changelog generic registration, timer wheel, token bucket filter, bit-rot common xattr formats, and scrubber state machine helpers from `bit-rot-scrub.*` and `bit-rot-ssm.*`. It relies on special client pids `GF_CLIENT_PID_BITD` and `GF_CLIENT_PID_SCRUB` so the stub can distinguish internal bitrot operations from ordinary clients. It also publishes status through GlusterFS events and dictionaries used by volume scrub status commands.

Risks: signature allocation uses flexible payload sizing and has a local TODO noting embedded NUL bytes can interact badly with consumers that treat hashes as strings. `br_object_read_block_and_sign` appears to call `TBF_THROTTLE_BEGIN` twice around `SHA256_Update`, which is worth reviewing against the intended throttle macro pairing. Most worker threads run infinite loops and are cancelled during cleanup, so lock ordering and cancellation points matter. The signer cleanup path is incomplete for per-child changelog registrations (`br_cleanup_signer` is a stub). Event and timer allocation failures can drop signing opportunities, relying on later modification or one-shot crawl for recovery.

Test signals: useful coverage includes child up/down races, changelog release events for normal and reopen-wait sign states, deleted-file soft errors, zero-byte and ENODATA one-shot crawl behavior, SHA256 signature xattr writes, signer thread count and expiry-time reconfiguration, scrubber status dictionary fields, on-demand scrub scheduling only from pending state, and shutdown cleanup with live timers and signer workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.h

Purpose: this header defines the shared daemon-side data structures and helper declarations used by bit-rot signer and scrubber code. It bridges GlusterFS logging, dict, syncop, changelog, timer wheel, throttle, common bitrot xattr formats, and scrub status/state-machine headers.

Important types and APIs: `scrub_throttle_t` and `scrub_freq_t` enumerate runtime scrub policy values. `br_child_t` stores per-brick state: connection status, child xlator, inode table, brick path, worker thread, timer pool, scanner queues, and active scrub flag. `br_private_t` is the top-level xlator private state containing child arrays, event queues, signer object queues, timer wheel, token bucket, scrub stats, `br_scrubber`, and `br_monitor`. `br_object_t` carries a GFID, signed version, sign state, and target child for queued signing. Exported helpers include `br_log_object`, `br_calculate_obj_checksum`, `br_prepare_loc`, `bitd_is_bad_file`, and `br_get_bad_objects_list`.

Control flow model: the types encode three cooperating loops: child connection event handling through `br_private.bricks`, signer object processing through `br_obj_n_workers.objects` plus `object_cond`, and scrub scanning through `br_scanfs` and `br_scrubber.scrublist`. Inline helpers define state transitions and checks for connected, failed, witnessed, and scrub-active children.

State and persistence behavior: this header does not persist state directly, but it defines the in-memory state that coordinates persistent xattr operations performed in the daemon and stub. `br_monitor` stores scrub scheduling state and timer pointer, while `br_private.expiry_time` and `signer_th_count` reflect volume options that shape when persistent signatures are written.

Dependencies and integration points: consumers must include the bit-rot common formats from the stub directory, scrub status, timer wheel, and changelog types. The header intentionally exposes enough daemon internals for scrub source files to update counters, build locs, detect bad objects, and drive scrub monitor events.

Risks: the header concentrates many mutexes and condition variables across nested structures, so implementation code must preserve documented lock order, especially around child locks and scrub monitor locks. Because `br_child_t.list` is reused in signer and scrubber lists, double insertion/removal bugs are a risk if mode checks regress.

Test signals: compile-time coverage should catch enum and function prototype drift. Runtime tests should exercise child state transitions, scrub pause/resume event derivation, status collection, and shared helper behavior when child inode tables or timer pools are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/Makefile.am

Purpose: this Automake file builds the `bitrot-stub` xlator when server support is enabled. It installs the module under the GlusterFS feature xlator directory and declares the C sources and private headers for the bit-rot stub.

Important build declarations: `xlator_LTLIBRARIES = bitrot-stub.la` is guarded by `WITH_SERVER`. `bitrot_stub_la_SOURCES` includes `bit-rot-stub-helpers.c` and `bit-rot-stub.c`. `noinst_HEADERS` lists `bit-rot-stub.h`, `bit-rot-common.h`, `bit-rot-stub-mem-types.h`, `bit-rot-object-version.h`, and `bit-rot-stub-messages.h`. The target links against `libglusterfs.la`.

Control flow and integration: the file has no runtime control flow, but it controls whether the stub xlator is part of the server-side translator set. Include paths cover libglusterfs, XDR generated headers, and RPC libraries, matching the stub's use of GlusterFS fop, xdr, and system wrappers.

State and persistence behavior: none directly. Its build output enables the runtime code that persists bitrot version and signature xattrs and maintains the quarantine directory.

Dependencies and risks: dependency risks are mostly build-time. Missing RPC/XDR include paths or a server-disabled build will prevent the stub from compiling or installing. Because `bit-rot-common.h` is shared with the daemon, this build file must stay in sync with any header split or rename.

Test signals: `make` with `WITH_SERVER` should produce `bitrot-stub.la`; distribution checks should include all noinst headers and avoid missing generated XDR include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-common.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-common.h

Purpose: this shared header defines bit-rot xattr state classification, in-memory signature payloads, stub initialization payloads, signature type constants, and helpers for converting daemon requests into on-disk version/signature records. It is included by both bit-rot daemon and stub code.

Important APIs and types: `br_vxattr_status_t` classifies xattr combinations as full, missing, unsigned, or invalid. `br_sign_state_t` describes release/signing state transitions: normal, reopen-wait, and quick sign. `br_version_xattr_state` examines a dict for `BITROT_OBJECT_BAD_KEY`, `BITROT_CURRENT_VERSION_KEY`, and `BITROT_SIGNING_VERSION_KEY`. `br_isignature_t` is the daemon-to-stub signing request format, and `br_isignature_out_t` is the stub-to-daemon/scrubber signature query format. `br_stub_init_t` carries stub boot time and brick export. Helpers set default versions, default signatures, ongoing versions, and packed signatures.

Control flow role: stub lookup/getxattr code uses `br_version_xattr_state` to decide whether an object is signed, unsigned, missing all bitrot metadata, or corruptly inconsistent. Daemon code constructs `br_isignature_t`, passes it under `GLUSTERFS_SET_OBJECT_SIGNATURE`, and the stub uses `br_set_signature` to persist it as `BITROT_SIGNING_VERSION_KEY`.

State and persistence behavior: the header defines names for the virtual stub init xattr and reopen hint xattr. It also defines the bad-object container GFID constant and the transient/persistent signature types. The on-disk persistence layout itself is declared in `bit-rot-object-version.h`, but this file provides the functions that populate it.

Dependencies and integration points: it depends on GlusterFS dict and bitrot key definitions supplied elsewhere, plus network byte order helpers used by the stub. It is a protocol boundary between daemon, scrubber, and stub, so additions must remain binary-compatible with existing xattr values.

Risks: `br_version_xattr_state` treats the mere presence of the bad-object key as enough to mark an object bad. Incorrect dict population can therefore cause EIO behavior for otherwise readable files. Signature length handling relies on caller-provided sizes and flexible arrays, so bounds and endian conversions are important.

Test signals: test all four xattr state combinations, bad-object detection with and without version/signature keys, signature type validation, default version/signature initialization, and daemon-stub round trips for SHA256 signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-object-version.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-object-version.h

Purpose: this header declares the compact on-disk xattr payload formats for bit-rot object versioning and signing.

Important types: `br_version_t` stores `ongoingversion` plus a two-word timestamp buffer. `br_signature_t` is packed and stores `signaturetype`, `signedversion`, and a flexible `signature[]` payload. These are the concrete values persisted under `BITROT_CURRENT_VERSION_KEY` and `BITROT_SIGNING_VERSION_KEY`.

Control flow role: bit-rot-stub initializes these records on lookup/create/mknod, updates `br_version_t` before modifying writes or truncates, and writes `br_signature_t` when bitd submits a validated signature. The scrubber and bitd later read them through virtual signature queries to determine staleness and verify content.

State and persistence behavior: this file is entirely about persistence layout. Any ABI change affects existing brick xattrs. The packed attribute on `br_signature_t` avoids compiler padding before the flexible signature payload.

Dependencies and integration points: included by `bit-rot-common.h`, which supplies helper functions for populating these records. It assumes standard integer and endian types are already available through surrounding GlusterFS headers.

Risks: the use of `unsigned long` in on-disk structures may be sensitive to architecture width and endian interpretation. Tests should guard mixed-version and mixed-architecture compatibility if the format is ever changed.

Test signals: validate xattr byte sizes for default signatures and SHA256 signatures, verify no padding is introduced in `br_signature_t`, and exercise upgrade/missing-xattr paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-object-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-helpers.c

Purpose: this helper file supports bit-rot-stub by managing fd contexts and the bad-object quarantine facade under the brick export. It also implements wrapper logic for lookup/readdir on the virtual bad-object container and path enrichment for scrub status output.

Important APIs and functions: fd context helpers are `br_stub_fd_new`, `__br_stub_fd_ctx_set`, `__br_stub_fd_ctx_get`, `br_stub_fd_ctx_get`, and `br_stub_fd_ctx_set`. Quarantine management functions are `br_stub_dir_create`, `br_stub_add`, `br_stub_del`, `br_stub_check_stub_directory`, and `br_stub_check_stub_file`. Worker queue helpers are `__br_stub_enqueue`, `__br_stub_dequeue`, `br_stub_worker_enqueue`, and `br_stub_worker`. Virtual directory operations are `br_stub_lookup_wrapper`, `br_stub_readdir_wrapper`, and `br_stub_fill_readdir`. Scrub status enrichment uses `br_stub_bad_objects_path`, `br_stub_get_path_of_gfid`, and `br_stub_entry_xattr_fill`.

Control flow: during stub initialization, `br_stub_dir_create` ensures `.glusterfs/quarantine` exists and creates the stable `stub-<container-gfid>` link target file. When the scrubber marks an object bad, `br_stub_add` hard-links that stable stub file to a file named by the object's GFID, creating an enumerable bad-object entry. Lookup or readdir of the special bad-object GFID is handled by queuing call stubs to `br_stub_worker`, which performs filesystem directory reads outside the main fop path.

State and persistence behavior: the quarantine directory is persistent under the brick export path. Each bad object is represented by a hard link named as its GFID, and stale `stub-<uuid>` entries are cleaned during readdir when they have only one link. Per-fd state stores either ordinary bitrot release callback context or an open `DIR *` for the quarantine directory plus EOF offset.

Dependencies and integration points: this file depends on GlusterFS syncop utilities, syscall wrappers, fd/inode context APIs, gf_dirent handling, and `syncop_gfid_to_path_hard`. It integrates with scrub status by attaching paths to the readdir xdata dict when available.

Risks: `br_stub_del` appears to treat `gf_unlink` return semantics differently from normal POSIX `unlink`; this should be checked against the wrapper. Hard-link based accounting can lose scrub status entries if link creation fails with ENOENT, EMLINK, or EEXIST, though object access is still blocked by the bad xattr. Readdir offset portability is guarded for non-Linux hosts, so directory seek/tell behavior needs platform testing. Path resolution is best effort and may fail without `gfid2path` or inode-table linkage.

Test signals: initialize both old misspelled quarantine path migration and fresh directory creation, mark and unmark bad GFIDs, enumerate quarantine directory with offsets and EOF, delete stale stub files, return path xdata when gfid2path is available, and verify bad-object directory lookup/readdir is handled asynchronously without leaking fd contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-mem-types.h

Purpose: this header reserves GlusterFS memory accounting type IDs for bit-rot-stub and bit-rot daemon allocations.

Important definitions: `enum br_mem_types` starts at `gf_common_mt_end + 1` and includes private state, version buffers, inode contexts, signatures, daemon children/objects/workers, scrubber entries, fd contexts, signature stubs, child events, and miscellaneous allocations. `gf_br_stub_mt_end` is passed to `xlator_mem_acct_init` by both daemon and stub memory accounting entry points.

Control flow and state: no runtime logic is present. The enum values are used by `GF_CALLOC`, `GF_MALLOC`, mem pools, and xlator memory accounting so allocations can be attributed in diagnostics.

Dependencies and integration points: depends on `<glusterfs/mem-types.h>`. It is included by both `bit-rot.c` and `bit-rot-stub.c`, so enum additions affect both components' accounting boundary.

Risks: removing or reordering memory IDs can confuse diagnostics and any tooling that expects stable type names. A shared enum for daemon and stub means new allocations in either component should be added before the end sentinel without collisions.

Test signals: build and run memory accounting initialization for both `bit-rot` and `bitrot-stub`, then exercise signer, scrubber, signature, fd context, and quarantine paths while checking allocation labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-messages.h

Purpose: this header defines structured GlusterFS message IDs and message strings for bit-rot-stub logging. It centralizes stable identifiers for allocation failures, internal xattr protection, bad-object handling, thread lifecycle, quarantine directory errors, and version/signature preparation errors.

Important APIs and definitions: `GLFS_MSGID(BITROT_STUB, ...)` declares all stub message IDs. The `BRS_MSG_*_STR` macros provide human-readable text for specific IDs. Message names include `BRS_MSG_BAD_OBJECT_ACCESS`, `BRS_MSG_NON_BITD_PID`, `BRS_MSG_NON_SCRUB_BAD_OBJ_MARK`, `BRS_MSG_SET_INTERNAL_XATTR`, `BRS_MSG_BAD_OBJECT_DIR_*`, and `BRS_MSG_VERSION_PREPARE_FAIL`.

Control flow role: implementation files use these IDs in `gf_smsg` calls at all critical failure and policy enforcement points. They do not alter behavior, but they make errors searchable and stable across releases.

State and persistence behavior: none directly. The header comments warn that IDs must not be removed to avoid reuse, which is a logging ABI constraint.

Dependencies and integration points: depends on `glfs-message-id.h` and the component name registry. Logs emitted with these IDs are integration points for support tooling, tests that inspect logs, and operational diagnostics.

Risks: adding IDs in the middle or deleting old IDs can break log interpretation. Some string macros are not necessarily used at every call site, so dead message strings can remain for compatibility.

Test signals: compile with all message IDs, run negative tests for internal xattr operations, bad-object access, non-bitd signature attempts, non-scrubber bad-object marks, and quarantine directory failures, then verify structured message IDs are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.c

Purpose: this is the server-side bitrot stub xlator. It protects internal bitrot xattrs from clients, maintains per-inode object version state, persists version changes before modifying writes/truncates, serializes daemon signature writes, tracks bad objects, exposes the bad-object quarantine directory, and emits changelog release IPC events that drive the bitrot daemon.

Important APIs and functions: xlator entry points are `init`, `reconfigure`, `notify`, `fini`, and `mem_acct_init`. Versioning helpers include `br_stub_init_inode_versions`, `br_stub_mod_inode_versions`, `br_stub_need_versioning`, `br_stub_versioning_prep`, `br_stub_perform_incversioning`, and `br_stub_fd_versioning`. Internal xattr handlers include `br_stub_fsetxattr`, `br_stub_handle_object_signature`, `br_stub_handle_object_reopen`, `br_stub_handle_bad_object_key`, `br_stub_getxattr_cbk`, and `br_stub_lookup_version`. FOP wrappers include lookup, stat, fstat, open, create, mknod, readv, writev, truncate, ftruncate, setxattr/fsetxattr, getxattr/fgetxattr, readdir/readdirp, opendir, unlink, removexattr/fremovexattr. Callback hooks include `br_stub_release`, `br_stub_forget`, and `br_stub_ictxmerge`.

Control flow: initialization reads `bitrot` and `export` options, records boot time in network byte order, initializes locks and the local mem pool, then starts a signature serialization thread and bad-object worker when versioning is enabled. Lookup/readdirp request bitrot version, signature, and bad-object xattrs from the child and initialize inode context. Open adds non-readonly fds to the inode fd list. Before writev/ftruncate/truncate, the stub checks whether the inode is dirty; if so, it persists a bumped ongoing version by issuing an internal durable fsetxattr before resuming the original operation. Successful modifying callbacks mark the inode modified. On last modifying release, `br_stub_release` transitions sign state and sends an IPC `CHANGELOG_OP_TYPE_BR_RELEASE` event to changelog.

State and persistence behavior: per-inode memory state is `br_stub_inode_ctx_t`, including dirty/modified flags, current version, signing state, fd list, and bad-object flag. Persistent state is held in `BITROT_CURRENT_VERSION_KEY`, `BITROT_SIGNING_VERSION_KEY`, `BITROT_SIGNING_XATTR_SIZE_KEY`, and `BITROT_OBJECT_BAD_KEY`. Signature requests from bitd use virtual `GLUSTERFS_SET_OBJECT_SIGNATURE`; stub validates the caller pid and version order, converts the request into persistent signing xattr data, and queues it ordered by version. Bad-object marks are allowed only from scrubber pid and are mirrored into inode context plus quarantine entries.

Dependencies and integration points: the file depends on GlusterFS fop stack macros, call stubs, inode/fd context APIs, changelog IPC event formats, special client pids, bitrot common on-disk formats, and helper functions from `bit-rot-stub-helpers.c`. It is the primary protocol peer for bitd: bitd gets stub init data, asks for object signatures, sends reopen hints, and receives release events through changelog.

Risks: this file has many async paths where `frame->local` is used as either a real local pointer or sentinel `0x1`; callback misuse can leak or corrupt local state. Versioning correctness depends on fd list maintenance and last-release detection across anonymous fds, parallel opens, inode merges, and error paths. Internal xattr checks must remain strict or clients could forge signatures or clear bad-object markers. The signature compare path can fake success when bitd signs an older version, which avoids regressing metadata but must be covered by tests. Reconfigure toggles threads and cleanup with cancellation, so locks and condition variables are sensitive.

Test signals: cover enabling/disabling `bitrot`, lookup with full/missing/unsigned/invalid xattrs, create/mknod initialization, parallel writes and opens, anonymous truncate versioning, last release IPC events for normal/reopen/quick states, bitd-only signature writes, scrubber-only bad marks, client denial of internal xattrs and removals, bad-object EIO on read/stat/open/write, quarantine readdir, inode forget and lookup ENOENT cleanup, and ictxmerge moving fd tracking across linked inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.h

Purpose: this header declares the bitrot stub's private structures, fop-local structures, fd context structures, guard macros, inline state helpers, and helper prototypes used by `bit-rot-stub.c` and `bit-rot-stub-helpers.c`.

Important types and APIs: `br_stub_inode_ctx_t` stores current version, dirty/modified flags, signing state, fd list, and bad-object state. `br_stub_fd_t` stores fd identity plus quarantine directory iterator state. `br_stub_local_t` carries delayed fop context across call stubs. `br_stub_private_t` stores the `bitrot` option, boot timestamp, export path, signature queue, bad-object worker container, local mem pool, quarantine base path, and bad-object directory GFID. Public helper prototypes cover fd context management, quarantine management, bad-object path lookup, readdir wrappers, and worker queueing.

Control flow helpers: `BR_STUB_VER_NOT_ACTIVE_THEN_GOTO`, `BR_STUB_VER_COND_GOTO`, `BR_STUB_VER_ENABLED_IN_CALLPATH`, and `BR_STUB_RESET_LOCAL_NULL` implement the sentinel-based mechanism used to remember whether versioning was enabled on the call path. Inline helpers mark inodes dirty/synced/modified, mark objects bad, read/set inode ctx, compute writeback version, determine release-trigger eligibility, filter internal xattrs, strip bitrot xattrs from outward dicts, and set bad inode markers.

State and persistence behavior: the header defines quarantine path constants, including migration support for the old misspelled `quanrantine` path. It does not write xattrs itself but names the state transitions used by the implementation before writing current-version, signing-version, and bad-object xattrs.

Dependencies and integration points: includes logging, dict, call-stub, syscall wrappers, common bitrot formats, structured messages, and XDR definitions. Its prototypes connect the main stub fop file to helper functions and to GlusterFS inode/fd context primitives.

Risks: `__br_stub_can_trigger_release` encodes the last-fd release rule and assumes modified implies not dirty before notification; regressions here directly affect missing or duplicate signing. Sentinel use in `frame->local` is compact but fragile. Inline xattr removal can accidentally hide or expose bad-object markers depending on the `remove_bad_marker` flag.

Test signals: unit-like tests should target inline state helpers through fop scenarios: dirty to synced to modified transitions, bad-object marking, release eligibility with multiple fds, internal xattr filtering, and outward dict scrubbing with and without bad marker retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/Makefile.am

Purpose: this Automake file declares the top-level changelog feature subdirectories.

Important declarations: `SUBDIRS = src lib` builds both the changelog xlator source and the changelog client library. `CLEANFILES` is empty.

Control flow and state: no runtime logic or persistent state is present. The file controls build traversal order and inclusion in distribution builds.

Dependencies and integration points: the `lib` subdirectory contains `libgfchangelog`, which bitrot daemon uses through `gf_changelog_register_generic`. The `src` subdirectory contains the changelog feature xlator implementation referenced by library includes.

Risks: omitting either subdirectory breaks either server changelog support or external/library consumers. Build-system tests should catch accidental subdirectory removal.

Test signals: run Automake/configure builds and verify both changelog xlator and `libgfchangelog` targets are visited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/Makefile.am

Purpose: this Automake file declares the changelog library subdirectory build.

Important declarations: `SUBDIRS = src` sends the build into the library source directory. `CLEANFILES` is empty.

Control flow and state: no runtime behavior. This is a thin build routing file.

Dependencies and integration points: it ensures `xlators/features/changelog/lib/src` participates in the build, producing `libgfchangelog.la` and related headers used by examples and by bitrot's changelog integration.

Risks: low, but accidental changes can silently exclude the library from builds while leaving the xlator itself intact.

Test signals: distribution and recursive make targets should confirm the `src` directory is entered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes-multi.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes-multi.c

Purpose: this C example demonstrates the generic multi-brick changelog callback API. It registers two bricks, filters for bitrot release events, and prints callback notifications.

Important functions: `brick_init`, `brick_fini`, and `brick_callback` satisfy the `gf_brick_spec` lifecycle/callback contract. `fill_brick_spec` populates brick path, event filter, and callback pointers. `main` allocates two specs, initializes changelog, and calls `gf_changelog_register_generic`.

Control flow: after registration, the example calls `select(0, NULL, NULL, NULL, NULL)` to sleep forever while the changelog library's callback machinery invokes `brick_callback`. It uses unordered events by passing `0` for the order flag.

State and persistence behavior: no changelog files are explicitly scanned or marked done by this example. State lives in the library connection and event callback machinery.

Dependencies and integration points: depends on `changelog.h` and `libgfchangelog`. It mirrors the same generic API style used by bitrot daemon, though bitrot passes one brick at a time and sets ordered events.

Risks: the example leaks `strdup` paths and the allocated brick array on failure, which is acceptable for a sample but not a service pattern. It hardcodes example brick paths and logs to `/tmp/multi-changes.log`.

Test signals: compile with pkg-config flags, register two test bricks, inject `CHANGELOG_OP_TYPE_BR_RELEASE`, and verify callbacks include the brick path and event type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes-multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes.c

Purpose: this C example demonstrates the simple polling changelog API for one brick. It scans every ten seconds, prints changelog file names, and marks each processed file done.

Important functions and APIs: `main` calls `gf_changelog_init`, `gf_changelog_register`, `gf_changelog_scan`, `gf_changelog_next_change`, and `gf_changelog_done`. The `handle_error` macro prints errno-backed failures.

Control flow: after registration, the loop scans the processing directory, reads entries from the tracker with `gf_changelog_next_change`, simulates processing with comments, and moves each file to processed via `gf_changelog_done`. A zero scan count sleeps and repeats.

State and persistence behavior: the library manages a scratch directory, tracker file, processing directory, and processed directory. This example demonstrates the intended contract that consumers call `done` after processing each changelog file.

Dependencies and integration points: includes `changelog.h` and links with `libgfchangelog`. It is a usage sample for changelog consumers outside the xlator stack.

Risks: the brick path, scratch path, and log path are hardcoded. It does not handle shutdown, retries, or partial processing beyond printing errors. The sample only prints file names and does not parse contents.

Test signals: compile via the documented pkg-config command, run against a brick with changelog enabled, create changes, observe scan count and file names, and confirm processed files are moved after `done`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-history.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-history.c

Purpose: this C example demonstrates the historical changelog API. It asks the user for start/end timestamps, requests history over a changelog directory, scans historical results, prints file names, and marks history changelogs done.

Important APIs: it calls `gf_changelog_init`, `gf_changelog_register`, `gf_history_changelog`, `gf_history_changelog_scan`, `gf_history_changelog_next_change`, and `gf_history_changelog_done`.

Control flow: after normal changelog registration, the program reads two integers with `scanf`, invokes `gf_history_changelog` with a hardcoded changelog directory and parallelism value `3`, then loops over historical scans until zero entries indicates completion.

State and persistence behavior: history APIs stage historical changelog files into library-managed directories and require `gf_history_changelog_done` after processing. `end_ts` reports the actual available end timestamp for the request.

Dependencies and integration points: includes `changelog.h` and links with `libgfchangelog`. It complements the live polling example by showing history recovery/backfill consumption.

Risks: the example uses `%d` printing for `unsigned long end_ts`, scans user input without validation, has hardcoded paths, and leaves some error handling commented. It is illustrative rather than production-safe.

Test signals: compile with pkg-config, run with a populated `.glusterfs/changelogs` directory, request valid and invalid timestamp ranges, confirm actual end timestamp behavior, and verify history done moves or cleans staged files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-history.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/changes.py -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/changes.py

Purpose: this Python example wraps the ctypes changelog binding in a polling loop. It initializes the library, registers one brick, repeatedly scans for changes, prints them, and marks each change done.

Important functions: `get_changes` accepts brick, scratch directory, log file, log level, and polling interval. It calls `Changes.cl_init`, `cl_register`, `cl_scan`, `cl_getchanges`, and `cl_done`.

Control flow: the program validates command-line arity, then enters an infinite loop inside `get_changes`. Each iteration scans, fetches all current changes from the wrapper, prints a list if non-empty, calls done for each file, and sleeps for the requested interval. `OSError` from the wrapper is caught and printed.

State and persistence behavior: persistent state is managed by `libgfchangelog`; this file only controls the poll cadence and calls `done` after printing each change. `cl_getchanges` in the wrapper also resets the tracker through `cl_startfresh`.

Dependencies and integration points: imports local `libgfchangelog.py`, plus `os`, `sys`, and `time`. It demonstrates a Python consumer path for the same C API used by native examples.

Risks: the usage string checks for six arguments but documents four user parameters, and the code uses `sys.argv[4]` as interval while passing a fixed log level, which suggests the usage text or arity is stale. It does not expose retry count. The global `cl` instance makes the sample single-client.

Test signals: run with valid brick/scratch/log/interval parameters, trigger changelog files, observe printed byte-string paths, verify `cl_done` moves files, and exercise errno propagation by using bad paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/changes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/libgfchangelog.py -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/libgfchangelog.py

Purpose: this Python module is a minimal ctypes wrapper around `libgfchangelog`. It exposes class methods for initialization, registration, scanning, tracker reset, fetching changes, and marking changes done.

Important APIs: `Changes.libgfc` loads `gfchangelog` with `RTLD_GLOBAL` and `use_errno=True`. `_get_api` fetches C symbols. `cl_init`, `cl_register`, `cl_scan`, `cl_startfresh`, `cl_getchanges`, and `cl_done` call the corresponding C functions and raise `OSError` on `-1`.

Control flow: `cl_getchanges` allocates a 4096-byte buffer, repeatedly calls `gf_changelog_next_change`, appends returned byte slices without the trailing NUL/newline, raises on `-1`, resets the tracker through `cl_startfresh`, and returns the sorted list using the suffix after the last dot as the key.

State and persistence behavior: wrapper state is process-global through the loaded C library and its `THIS`/API state. It does not manage files directly, but `cl_done` delegates persistent movement to `gf_changelog_done`.

Dependencies and integration points: uses `ctypes`, `ctypes.util.find_library`, and errno propagation from the C library. It is intended for the adjacent `changes.py` example.

Risks: `cl_init` calls `raise_changelog_err`, which is not defined in the class; this is a bug on init failure. Python 3 ctypes calls are passed Python strings unless callers encode them; depending on runtime, bytes may be required for C `char *` arguments. Return types and argument types are not declared, so ctypes defaults can be unsafe on platforms where sizes differ.

Test signals: import when `libgfchangelog` is installed, force init/register failure to validate error paths, pass bytes and string arguments under Python 3, scan and fetch more than one change, and verify tracker reset plus sorted order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/python/libgfchangelog.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/Makefile.am

Purpose: this Automake file builds `libgfchangelog.la`, the changelog client/library target used by examples and internal consumers such as bitrot.

Important declarations: it sets `AUTOMAKE_OPTIONS = subdir-objects`, declares `lib_LTLIBRARIES = libgfchangelog.la`, and lists sources including `gf-changelog.c`, journal handler, helpers, API, history support, RPC/reborp code, and changelog RPC common code from the xlator source tree. Headers are listed in `noinst_HEADERS`. It links against libglusterfs, XDR, and RPC libraries.

Control flow and state: no runtime control flow, but compile flags define `DATADIR`, file offset support, PIC, and include paths required by RPC, xlator, and changelog internals. The `version-info` setting controls the library ABI version.

Dependencies and integration points: this is the build bridge between changelog xlator internals and the standalone `libgfchangelog` API. It depends on generated XDR headers, rpc-lib, socket transport headers, and libglusterfs. It also includes a make rule to build `libglusterfs.la`.

Risks: missing generated XDR include paths or source-list drift can break library builds. ABI-sensitive changes need matching `LIBGFCHANGELOG_LT_VERSION` management. Since the library includes source from `xlators/features/changelog/src`, build ordering must remain correct.

Test signals: recursive make should produce `libgfchangelog.la`; pkg-config users should compile the C examples; symbol checks should show live, generic, and history changelog APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/changelog-lib-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/changelog-lib-messages.h

Purpose: this header defines structured log message IDs and message strings for `libgfchangelog` and related changelog library code.

Important definitions: `GLFS_MSGID(CHANGELOG_LIB, ...)` reserves IDs for open, rmdir, scratch directory setup, thread creation, opendir, rename, read, htime, write, mmap/munmap, parse, cleanup, notify registration, RPC invocation, event draining, XDR decoding, history failures, and final/requesting status messages. String macros provide stable text for many of these IDs.

Control flow role: changelog library source files use these IDs in `gf_msg` and `gf_smsg` calls to report operational failures and state transitions. The header itself contains no logic.

State and persistence behavior: no direct state. The comments establish a compatibility rule that IDs should be appended and never removed, because log ID reuse breaks diagnostics.

Dependencies and integration points: depends on `glfs-message-id.h` and the `CHANGELOG_LIB` component registration. Operational tooling and tests can key on these IDs.

Risks: editing the ID list incorrectly can break stable logging. Some message strings are broad and shared across multiple source files, so changing them may affect log-based tests.

Test signals: compile all changelog library sources, force failures in rename/open/stat/history/rpc paths, and verify emitted structured message IDs and strings match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/changelog-lib-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-api.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-api.c

Purpose: this file implements the simple live changelog consumer API layered over the changelog journal state. It lets consumers scan available changelog files, iterate their paths from a tracker file, reset iteration, and mark files processed.

Important APIs: `gf_changelog_done` validates a processed file path and renames it into the processed directory. `gf_changelog_start_fresh` truncates the tracker so iteration restarts. `gf_changelog_next_change` reads the next tracker line and returns it without the trailing newline. `gf_changelog_scan` scans the processing directory, writes changelog paths to the tracker, and rewinds the tracker for iteration.

Control flow: every API fetches `THIS`, then obtains the journal pointer through `GF_CHANGELOG_GET_API_PTR`. `scan` refuses work if the journal is API-disconnected, truncates the tracker, rewinds `jnl_dir`, iterates entries excluding `.` and `..`, writes full processing paths plus newline into the tracker, and seeks back to the start. `next_change` reads one line using the helper buffered reader. `done` resolves the input path and ensures it is within `jnl_working_dir` before renaming to `jnl_processed_dir`.

State and persistence behavior: persistent state consists of the journal working, processing, and processed directories plus the tracker file descriptor. `gf_changelog_done` is the state transition from processing to processed. `gf_changelog_scan` refreshes the tracker but does not consume files.

Dependencies and integration points: depends on GlusterFS globals, syscall wrappers, changelog journal structures, helper I/O functions, and changelog library messages. Public examples in C and Python call these APIs directly.

Risks: `gf_changelog_done` constructs `to_path` by concatenating `jnl_processed_dir` and `basename(buffer)` and assumes directory strings already carry separators. The realpath containment check is prefix-based; it relies on canonical paths and could be sensitive to similarly prefixed directories if not normalized with separator boundaries. `scan` writes entries one by one and breaks on write failure, returning `-1` unless it cleanly reaches end.

Test signals: scan empty and populated processing directories, iterate until zero, call done on valid and invalid paths, verify path traversal is rejected, simulate disconnected journals, write failures, and tracker truncation/reseek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.c

Purpose: this file provides small reusable helpers for changelog library I/O, path encoding, buffered line reading over file descriptors, seek/truncate state reset, and pthread cleanup.

Important APIs: `gf_changelog_write` loops until a buffer is fully written or write fails. `gf_rfc3986_encode_space_newline` percent-encodes bytes using an exception table. `gf_readline` reads one line with a thread-local `read_line_t` buffer. `gf_lseek` and `gf_ftruncate` wrap syscall operations and reset the thread-local line buffer. `gf_thread_cleanup` cancels and joins a thread, validating `PTHREAD_CANCELED`.

Control flow: `gf_readline` uses `my_read` to fill a per-thread buffer with `sys_read`, then returns on newline, EOF, max length, or error. Reset wrappers clear that buffer because tracker files are truncated and repositioned during scans. `gf_thread_cleanup` logs warning messages for cancel, join, or non-canceled termination failures.

State and persistence behavior: no persistent state is owned here, but file descriptor writes, truncates, and seeks affect changelog tracker files. Thread-local state is intentionally reset on seek/truncate to avoid stale buffered data.

Dependencies and integration points: depends on changelog mem types, helper declarations, message IDs, and GlusterFS syscall wrappers. It is used by live and history changelog APIs.

Risks: `gf_ftruncate` ignores its `length` parameter and always truncates to zero, which matches current callers but is surprising API behavior. `gf_rfc3986_encode_space_newline` uses `sprintf` while advancing through the output buffer; callers must provide sufficient space. `gf_readline` is thread-local but only supports one active fd buffer per thread.

Test signals: partial writes, EOF without newline, long-line truncation at `maxlen`, seek/truncate followed by reads, thread cleanup for cancellable and non-cancellable threads, and encoding of spaces/newlines versus reserved bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.h

Purpose: this header declares changelog library helper types, connection/event structures, constants for journal subdirectories, callback invocation macros, and helper function prototypes.

Important types and APIs: `read_line_t` backs buffered line reads. `gf_event_list` stores ordered event queue state with `next_seq`, a mutex/cond, invoker thread, and queued events. `gf_event` stores a sequence number and flexible iovec payload. `gf_changelog_conn_state_t` describes pending, accepted, and disconnected states. `gf_changelog_t` is the per-brick connection object, holding brick path, RPC handles, notify filter, lifecycle callbacks, owner private data, invoker xlator, ordering flag, queue/pick callbacks, and event list. `gf_private_t` stores global library private state with connection and cleanup lists.

Control flow helpers: `gf_changelog_filter_check` tests whether an event matches a brick's notification filter. `GF_NEED_ORDERED_EVENTS` checks the ordered flag. `GF_CHANGELOG_INVOKE_CBK` switches `THIS` to the consumer xlator before invoking callbacks, then restores it. `SAVE_THIS` and `RESTORE_THIS` support similar context management.

State and persistence behavior: constants define `.current`, `.processed`, `.processing`, `.history`, and tracker names used by journal management. The header does not persist state itself but names directories and structures that the API and journal handlers maintain.

Dependencies and integration points: includes locking, xlator, changelog RPC common, and changelog journal headers. It is a central internal contract for changelog processing, RPC connection handling, ordered event delivery, and API access.

Risks: the callback macro references `entry` implicitly, so call sites must have the expected variable in scope. Event allocation macros require correct count/length accounting to avoid iovec payload corruption. Ordered event logic depends on `next_seq` bootstrap and queue/pick callbacks being paired correctly.

Test signals: ordered and unordered event queue/pick behavior, callback invocation with `THIS` restoration, filter matching, connection state transitions, event allocation sizing, and API pointer retrieval from `gf_private_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.h -->
