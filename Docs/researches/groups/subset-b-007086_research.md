# subset-b-007086 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-write.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-write.c

## Purpose
This file implements erasure-coded inode-changing FOPs for the GlusterFS disperse translator: metadata xattr updates, `setattr`, allocation and hole punching variants, truncation, and `writev`. It converts user byte ranges into EC fragment ranges, acquires EC locks, performs quorum dispatch to child bricks, combines callback answers, updates cached inode size/version state, and encodes user data into per-brick fragments before winding to children.

## Important APIs, Types, And Functions
The public entry points are `ec_removexattr`, `ec_fremovexattr`, `ec_setattr`, `ec_fsetattr`, `ec_setxattr`, `ec_fsetxattr`, `ec_fallocate`, `ec_discard`, `ec_truncate`, `ec_ftruncate`, and `ec_writev`. Each allocates an `ec_fop_data_t`, copies or references loc/fd/dict/iovec/xdata inputs, assigns a wind function, and enters `ec_manager()`. Shared callback handling is centralized by `ec_inode_write_cbk()`, with write-like answer combination through `ec_combine_write`. The major state-machine handlers are `ec_manager_xattr`, `ec_manager_setattr`, `ec_manager_fallocate`, `ec_manager_discard`, `ec_manager_truncate`, and `ec_manager_writev`.

The write path is the most complex API surface. `ec_writev_prepare_buffers()` normalizes unaligned or multi-iovec writes into an aligned data buffer plus a per-brick output buffer. `ec_writev_start()` performs partial-stripe head/tail reads or cache merges, adjusts append offsets, and temporarily uses root credentials for internal reads. `ec_writev_encode()` calls `ec_method_encode()` to fill one output block per node, and `ec_wind_writev()` sends each node its fragment at `offset / fragments`.

## Control Flow
Most operations follow `INIT/LOCK -> DISPATCH -> PREPARE_ANSWER -> REPORT -> LOCK_REUSE -> UNLOCK -> END`. Lock preparation marks whether the operation updates data, metadata, or only needs query information. Dispatch uses `ec_dispatch_all()` unless an operation needs a delayed internal action, such as write partial-stripe reads, discard zero-fill repair writes, or truncate tail cleanup writes. Answer preparation rebuilds `iatt` with `ec_iatt_rebuild()`, clamps return values to user-visible lengths, and updates inode size through `ec_get_inode_size()` / `ec_set_inode_size()` while the EC inode lock is held.

`discard` first rounds the range to EC fragment boundaries. Whole-fragment parts are dispatched as `discard`; uncovered head/tail bytes are rewritten as zeros with `ec_update_write()`. `truncate` rounds up the on-brick truncate offset, updates the logical inode size, and if a shrink lands inside a stripe, opens an anonymous fd if needed and writes zeros for the leftover encoded fragment tail. `fallocate` rejects unsupported range-transform modes and aligns the allocated range. `setxattr` has an integration-specific path for `SQUOTA_LIMIT_KEY`, dividing the aggregate quota limit by the number of data fragments before writing the xattr to bricks.

## State And Persistence Behavior
Persistent state is stored on child bricks as file data, metadata, and EC xattrs managed by helpers in other EC files. This file updates in-memory `ec_inode_t` size and lock-good masks to make later operations observe consistent logical size. The stripe cache stored under the inode context may retain recently completed full stripes; it is updated on write tail merges and used to avoid extra backend reads for partial-stripe writes. FOP state, callback groups, answer masks, and buffers are transient per `ec_fop_data_t`.

## Dependencies And Integration Points
The file depends on `ec-common`, `ec-helpers`, `ec-combine`, `ec-method`, and `ec-fops` for state machines, locks, quorum dispatch, iatt merging, EC encoding, fd/inode contexts, and child wind wrappers. It integrates with GlusterFS frame/callback conventions (`STACK_WIND_COOKIE`, `QUORUM_CBK`), iobuf/iobref memory management, inode/fd reference management, xdata dictionaries, and POSIX range semantics.

## Risks
The main correctness risks are off-by-one or overflow mistakes while converting user offsets into fragment offsets, stale inode size under concurrent writes, failure to restore root uid/gid after internal reads, partial-stripe corruption when head/tail reads fail, and callback answer mismatches that still reach quorum. Cache invalidation is subtle: stale stripe-cache data would corrupt future partial writes, so tests should stress truncates, discards, and overlapping writes. Error paths must preserve fop references and unwind exactly once.

## Test Signals
Useful signals include disperse write/read consistency across all alignments, append writes, shrinking and extending truncates, fallocate keep-size behavior, discard over sub-stripe and multi-stripe ranges, simple-quota xattr writes, brick failures during partial-stripe repair writes, and statedump stripe-cache counters for hits, misses, evicts, and errors. Quorum tests should verify that successful `op_ret` is converted from fragment bytes back to user bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-locks.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-locks.c

## Purpose
This file implements explicit lock FOP handling for the EC translator: entry locks, inode locks, fd inode locks, and POSIX byte-range `lk`. It fans lock requests out to child bricks, combines responses, converts blocking lock attempts into nonblocking parallel probes plus sequential fallback, and cleans up partially acquired locks when quorum cannot be reached.

## Important APIs, Types, And Functions
Public entry points are `ec_entrylk`, `ec_fentrylk`, `ec_inodelk`, `ec_finodelk`, and `ec_lk`. Callback/wind pairs include `ec_entrylk_cbk`/`ec_wind_entrylk`, `ec_inodelk_cbk`/`ec_wind_inodelk`, and `ec_lk_cbk`/`ec_wind_lk`. `ec_lock_check()` is the core quorum evaluator. It groups successful, `EAGAIN`, and `ESTALE` answers and returns success, retry, or a final error while producing the mask of bricks already locked. `ec_lock_unlocked()` and `ec_lock_lk_unlocked()` log failures from cleanup unlock requests.

## Control Flow
For blocking entry/inode/lk requests, the manager first converts the request to a nonblocking lock (`ENTRYLK_LOCK_NB` or `F_SETLK`) and sets mode `EC_LOCK_MODE_ALL`. After dispatch, `ec_lock_check()` decides whether enough bricks locked, whether `EAGAIN` contention requires retry, or whether partial locks must be released. If retry is needed, the manager changes the command back to blocking (`ENTRYLK_LOCK` or `F_SETLKW`) and uses `ec_dispatch_inc()` to acquire remaining locks incrementally. Unlock requests skip this special lock checking and use `ec_fop_prepare_answer()`.

For inode locks, the requested byte range is translated to EC fragment units by adjusting the start and length; partial cleanup unlocks translate back to user units when issuing a compensating unlock. `lk` uses `ec_combine_lk()` to reject mismatching flock answers from different bricks.

## State And Persistence Behavior
The file does not persist data directly. It coordinates backend lock state on child translators and uses transient `ec_fop_data_t` masks, callback groups, command fields, flock structures, and lock owner copies. Partially acquired backend locks are explicitly unwound by issuing child unlock FOPs against the mask returned by `ec_lock_check()`.

## Dependencies And Integration Points
It depends on `ec-common` dispatch/completion, `ec-combine` answer grouping, `ec-helpers` range and owner utilities, `ec-fops` recursive EC lock wrappers, and GlusterFS lock FOP contracts. It integrates with upstream `ec.c` wrappers, which choose `EC_MINIMUM_ALL` for acquiring locks and `EC_MINIMUM_ONE` for unlocks.

## Risks
The riskiest behavior is split-brain lock state if partial acquisitions are not cleaned up, if `EAGAIN` fallback is mishandled, or if range scaling does not match write/read range scaling. `ESTALE` is intentionally treated as quorum-relevant but not always fatal, which is subtle under concurrent unlink. The `ec_combine_lk()` mismatch path only logs and rejects grouping, so tests need to verify final answers under divergent brick lock state.

## Test Signals
Exercise blocking and nonblocking entry/inode/fd locks with one or more contended bricks, unlock failure logging, ESTALE during unlink, byte-range locks crossing EC fragment boundaries, and mixed child answers for `lk`. Failure injection should confirm that partial locks are released and that retries do not duplicate successful child locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-mem-types.h

## Purpose
This header declares memory accounting type IDs for the EC/disperse translator. The IDs let GlusterFS attribute allocations for EC private state, inode/fd contexts, self-heal structures, Galois-field/code-generation data, matrices, and stripe cache entries.

## Important APIs, Types, And Functions
The only exported symbol is enum `gf_ec_mem_types_`. Important members include `ec_mt_ec_t`, `ec_mt_xlator_t`, `ec_mt_ec_inode_t`, `ec_mt_ec_fd_t`, `ec_mt_subvol_healer_t`, `ec_mt_ec_gf_t`, `ec_mt_ec_code_t`, `ec_mt_ec_code_builder_t`, `ec_mt_ec_matrix_t`, and `ec_mt_ec_stripe_t`. `ec_mt_end` is passed to `xlator_mem_acct_init()` in `ec.c`.

## Control Flow
There is no runtime control flow. Allocation sites in EC source files pass these IDs to `GF_MALLOC`, `GF_CALLOC`, and related helpers; initialization in `mem_acct_init()` registers the enum range.

## State And Persistence Behavior
The header affects observability of heap state only. It does not persist data and does not hold mutable state.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and starts at `gf_common_mt_end + 1`, which is the standard GlusterFS convention for translator-local memory classes.

## Risks
Risks are mostly maintenance risks: adding a new allocation class out of order or before existing values could break accounting compatibility, while forgetting to add a type makes memory reports less useful. The enum must remain below `ec_mt_end` for `xlator_mem_acct_init()`.

## Test Signals
Build coverage and translator initialization are the primary checks. Memory-accounting/statedump tests can confirm EC allocations are tagged under expected names and do not fall into common unknown buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-messages.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-messages.h

## Purpose
This header registers stable message IDs for the EC/disperse translator. The IDs back structured `gf_msg()` logging across option parsing, FOP handling, locking, self-heal, matrix/code generation, xattr handling, and read-mask parsing.

## Important APIs, Types, And Functions
The file uses `GLFS_MSGID(EC, ...)` to define many `EC_MSG_*` identifiers, including invalid configuration, no memory, lock/unlock failures, matrix and dynamic codegen failures, xattr parse failures, heal events, fop mismatches, and `EC_MSG_INVALID_READMASK`.

## Control Flow
There is no executable control flow. The key rule is append-only maintenance: new IDs must be added at the end, never removed or reused, to preserve log compatibility.

## State And Persistence Behavior
No runtime state is held. The IDs become part of log/event ABI and should be treated as persistent identifiers across releases.

## Dependencies And Integration Points
It includes `<glusterfs/glfs-message-id.h>` and is included by most EC implementation files that call `gf_msg()`.

## Risks
The main risk is accidental ID reuse or removal, which can break log parsers, diagnostic tooling, and support workflows. Another risk is adding generic messages without enough specificity, reducing operational value.

## Test Signals
Compilation validates the macro expansion. Log-oriented tests and static review should confirm new EC logs use an existing appropriate ID or append a new one without reordering the list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.c

## Purpose
This file implements EC matrix management and encode/decode execution for the disperse translator. It prepares Vandermonde-like normal matrices for encoding, builds inverse matrices for available-fragment decode masks, caches those matrices, and invokes generated Galois-field code functions.

## Important APIs, Types, And Functions
Public APIs are `ec_method_init`, `ec_method_fini`, `ec_method_update`, `ec_method_encode`, and `ec_method_decode`. Internal helpers include `ec_method_matrix_normal()`, `ec_method_matrix_inverse()`, `ec_method_matrix_init()`, `ec_method_matrix_get()`, `ec_method_matrix_put()`, and sorted cache helpers for lookup/insert/remove. `ec_method_setup()` creates the encode matrix and the `ec_code_t` code generator context.

## Control Flow
Initialization creates a matrix mem-pool, object array, Galois-field tables via `ec_gf_prepare()`, code generation context via `ec_code_create()`, and the encode matrix. Encoding walks input in `list->stripe` chunks and calls each linear row function, advancing each child output pointer by `EC_METHOD_CHUNK_SIZE`. Decoding looks up or builds an inverse matrix keyed by the surviving-brick mask, runs interleaved decode functions over `EC_METHOD_CHUNK_SIZE` slices, then unreferences the cached matrix. Unreferenced matrices sit on an LRU list and are evicted when `count > max`.

## State And Persistence Behavior
All state is in-memory within `ec_matrix_list_t`: cached decode matrices, one encode matrix, generated executable code spaces, GF tables, mem-pool, and lock. Nothing is persisted to disk. The cache key is a bitmask of available fragments; correctness depends on matching the rows array to that mask.

## Dependencies And Integration Points
The file depends on `ec-galois`, `ec-code`, `ec-types`, `ec-mem-types`, and `ec-helpers`. It is initialized from `ec.c` with data fragments as columns and total nodes as rows; `ec-inode-write.c` calls `ec_method_encode()` before writing fragments. Read/heal paths use `ec_method_decode()` to reconstruct missing data.

## Risks
Matrix inversion and cache lifecycle are correctness-critical. Pointer arithmetic advances `void *` values, relying on compiler extensions common in this codebase. The decode cache uses a sorted object array plus LRU list; reference-count or removal mistakes could lead to stale function pointers or leaks. `ec_method_update()` is currently a stub, so changing CPU extension options at runtime does not rebuild generated code.

## Test Signals
Tests should cover encode/decode for every legal redundancy/data count, all surviving-fragment masks at quorum, repeated decode to hit cache reuse and eviction, memory cleanup during translator fini, and CPU-extension option combinations (`none`, `auto`, SIMD variants). Fault injection on allocation and code generation should return clean errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.h

## Purpose
This header defines the public EC coding-method interface and constants used by the disperse translator for Galois-field erasure coding.

## Important APIs, Types, And Functions
It defines GF parameters `EC_GF_BITS`, `EC_GF_MOD`, `EC_GF_SIZE`, capacity constants `EC_METHOD_MAX_FRAGMENTS` and `EC_METHOD_MAX_NODES`, and word/chunk constants `EC_METHOD_WORD_SIZE` and `EC_METHOD_CHUNK_SIZE`. It declares lifecycle APIs `ec_method_init()`, `ec_method_fini()`, `ec_method_update()`, and data APIs `ec_method_encode()` and `ec_method_decode()`.

## Control Flow
The header itself has no control flow. Callers initialize an `ec_matrix_list_t`, use encode/decode during FOP execution, optionally request an update for CPU extension changes, then finalize the method on translator teardown.

## State And Persistence Behavior
The state is owned by the `ec_matrix_list_t` passed to the functions. The header does not persist data.

## Dependencies And Integration Points
It includes `ec-types.h` and `ec-galois.h`, binding the coding API to EC type definitions and GF arithmetic support. `ec.h` derives maximum EC nodes from these constants.

## Risks
Changing constants changes on-disk/data-layout assumptions and maximum legal disperse volume shapes. Consumers expect chunk sizes to align with buffer preparation in write/read paths.

## Test Signals
Compile-time users should agree on constants. Runtime encode/decode tests should validate that `EC_METHOD_CHUNK_SIZE` matches fragment-size assumptions in `ec.c` and offset adjustment helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-types.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-types.h

## Purpose
This header is the central type model for the EC/disperse translator. It defines translator-private configuration, inode/fd contexts, lock structures, per-FOP state, callback aggregation records, coding/matrix structures, self-heal state, and statistics.

## Important APIs, Types, And Functions
Key structs are `ec_config_t` for on-disk EC layout fields, `ec_fd_t` for fd state and per-child open status, `ec_inode_t` for cached config/version/size/dirty state plus stripe cache and read mask, `ec_lock_t` and `ec_lock_link_t` for eager/inode lock ownership and dirty/update tracking, `ec_fop_data_t` for a full operation state machine, `ec_cbk_data_t` for grouped child answers, `ec_matrix_list_t` for coding matrices, `ec_heal_t` and `ec_self_heald_t` for healing, and `ec_t` for translator-wide state. The `ec_cbk_t` union stores callback types for every supported FOP.

## Control Flow
No functions are implemented here, but the fields define control flow elsewhere. `ec_fop_data_t` carries state numbers, quorum minimum, masks (`mask`, `remaining`, `received`, `good`, `healing`), wind/handler/resume callbacks, locks, fd/loc/iovec/xdata payloads, and fragment ranges. `ec_lock_t` owners/waiting/frozen lists drive eager lock reuse. `ec_t` masks and counters drive up/down notification and quorum.

## State And Persistence Behavior
Most structs are in-memory. Persistent EC state is represented indirectly by xattrs decoded into `ec_inode_t` fields: config, versions, dirty flags, and size. The translator private `ec_t` persists for the lifetime of the xlator instance and owns pools, child lists, matrix cache, self-heal threads, and statistics. `ec_fd_t` and `ec_inode_t` are attached to GlusterFS fd/inode contexts.

## Dependencies And Integration Points
The header includes GlusterFS timer, syncop, atomic, and libxlator headers. It is included by nearly every EC source file and acts as the ABI between method coding, helpers, locks, FOP managers, heal logic, and xlator entry points.

## Risks
Because `ec_fop_data_t` is shared by many state machines, field reuse is easy to misread: generic fields such as `int32`, `uint32`, `size`, `offset`, and `str[]` carry operation-specific meanings. Flexible arrays in `ec_fd_t`, `ec_code_builder_t`, and `ec_matrix_t` require exact allocation sizes. Lock flags, dirty flags, and masks must be updated atomically or under the expected locks.

## Test Signals
The best signals are broad FOP suites under failure injection, memory-pool accounting, statedumps for private state, lock contention tests, and ABI-aware compile checks after any struct field or enum change. Sanitizer or valgrind runs are valuable around flexible-array allocations and callback data lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.c

## Purpose
This is the main xlator implementation for GlusterFS disperse/EC. It initializes EC private state, parses volume options, manages child up/down notifications and self-heal triggering, registers FOP wrappers, protects internal EC xattrs, handles read-mask configuration, exposes statedump data, and publishes the `xlator_api_t`.

## Important APIs, Types, And Functions
Initialization flows through `mem_acct_init()`, `init()`, `ec_prepare_childs()`, `ec_parse_options()`, `ec_method_init()`, read-policy/read-mask assignment, self-heal daemon init, and subvolume-id dictionary construction. Teardown uses `fini()` and `__ec_destroy_private()`. Notification functions are `notify()`, `ec_notify()`, `ec_notify_cbk()`, `ec_up()`, `ec_down()`, and `ec_get_event_from_state()`. FOP wrappers named `ec_gf_*` adapt GlusterFS xlator FOP signatures to internal EC APIs. `ec_dump_private()` emits runtime state and stripe/heal statistics.

## Control Flow
At startup, the translator allocates `ec_t`, pools for FOP/callback/lock objects, child arrays, matrix coding state, inode table, self-heal state, and volume option values. `GF_EVENT_PARENT_UP` starts a ten-second delayed notification timer so initial child notifications can settle. Child up/down events update bitmasks under `ec->lock`; once enough bricks are up and all have notified, the translator propagates `GF_EVENT_CHILD_UP` and may launch root self-heal. If too many bricks are down, it propagates down. Upcalls are filtered: cache invalidation forces attr invalidation, while EC-domain inodelk contention releases eager locks on the affected inode.

The FOP wrapper table is mostly thin: it chooses quorum flags (`EC_MINIMUM_ONE`, `EC_MINIMUM_MIN`, or `EC_MINIMUM_ALL`) and calls the appropriate internal EC function. Xattr wrappers block direct access to `trusted.ec.*` internals except for the explicit heal/read-mask paths. Marker and heal-info getxattrs are intercepted before normal EC dispatch.

## State And Persistence Behavior
`ec_t` holds child topology, fragment/redundancy geometry, node masks, up/down state, option values, pending FOP lists, self-heal queues, matrix cache, pools, read mask, leaf-to-subvolid mapping, and counters. Persistent on-brick state is not written directly here, but this file defines internal xattr names and prevents users from mutating them. `ec->up`, child masks, timers, and self-heal thread state are runtime-only. `__ec_destroy_private()` includes a deliberate sleep after canceling a timer due to callback cancellation race concerns.

## Dependencies And Integration Points
The file integrates with GlusterFS xlator APIs, event APIs, statedump, upcall-utils, option macros, inode table creation, self-heal daemon (`ec-heald`), coding method (`ec-method`), and all internal EC FOP implementations. The final `xlator_api` identifies the translator as `"disperse"` and marks it maintained.

## Risks
Option parsing directly affects data layout: invalid redundancy or too many subvolumes must be rejected before serving I/O. Notification timing is race-prone because timer cancellation cannot guarantee the callback is not already scheduled. Direct xattr filtering must remain complete or users could corrupt EC metadata. Runtime `cpu-extensions` reconfiguration calls a stub method update, so expectations around live generator changes should be conservative.

## Test Signals
Tests should cover initialization with legal and illegal disperse counts, child notification orderings, delayed mount behavior, parent down while FOPs are pending, read-mask parsing and per-inode read-mask setxattr, internal xattr denial for get/set/remove, marker getxattr handling, self-heal launch on brick recovery, and statedump fields after workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.h

## Purpose
This small header defines EC translator-wide constants, internal xattr names, cache limits, and derived maximum node counts.

## Important APIs, Types, And Functions
Important macros include `EC_XATTR_PREFIX`, `EC_XATTR_CONFIG`, `EC_XATTR_SIZE`, `EC_XATTR_VERSION`, `EC_XATTR_HEAL`, `EC_XATTR_HEAL_NEW`, `EC_XATTR_DIRTY`, `EC_XATTR_READMASK`, `EC_STRIPE_CACHE_MAX_SIZE`, `EC_VERSION_SIZE`, `EC_SHD_INODE_LRU_LIMIT`, and `EC_DEFAULT_INODE_READ_MASK`. It also aliases `EC_MAX_FRAGMENTS` to `EC_METHOD_MAX_FRAGMENTS` and derives `EC_MAX_NODES`.

## Control Flow
There is no executable control flow. These macros are consumed by option parsing, xattr filtering, heal logic, and read-mask handling.

## State And Persistence Behavior
The xattr names define persistent metadata keys under `trusted.ec.*`; changing them would break compatibility with existing EC volumes. Cache and LRU constants affect in-memory behavior only.

## Dependencies And Integration Points
The header includes `ec-method.h` to derive coding limits. It is included by `ec.c` and other EC components that need common names.

## Risks
The main risk is compatibility: xattr names and maximum-node derivation are part of the translator contract. `EC_MAX_NODES` deliberately enforces redundancy less than fragment count; relaxing it would require broader layout review.

## Test Signals
Build tests catch macro availability. Functional tests should verify internal xattrs remain protected, heal xattrs are recognized, and invalid redundancy/node configurations are rejected consistently with these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/Makefile.am

## Purpose
This Automake file lists debug translators built under `xlators/debug`.

## Important APIs, Types, And Functions
It sets `SUBDIRS = error-gen io-stats sink trace delay-gen`, causing those child directories to participate in recursive builds, and declares an empty `CLEANFILES`.

## Control Flow
Automake recursively enters the listed subdirectories in order during build, install, clean, and related targets.

## State And Persistence Behavior
No runtime state is managed. The file affects build outputs installed for debug translators.

## Dependencies And Integration Points
It integrates with the top-level GlusterFS Automake build and the per-translator `Makefile.am` files in each debug child directory.

## Risks
Removing a subdirectory drops that translator from builds; ordering can matter if generated files or install paths have hidden assumptions. Empty `CLEANFILES` is benign.

## Test Signals
`make`, `make distcheck`, and packaging manifests should confirm all expected debug xlators are built and installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/Makefile.am

## Purpose
This Automake file delegates the delay-gen debug translator build to its `src` directory.

## Important APIs, Types, And Functions
It sets `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Recursive Automake targets enter `delay-gen/src`, where the actual module library and headers are declared.

## State And Persistence Behavior
No runtime or persistent state is managed.

## Dependencies And Integration Points
It is reached from `xlators/debug/Makefile.am` and points the build system at `delay-gen/src/Makefile.am`.

## Risks
The only meaningful risk is accidentally omitting `src`, which would stop building delay-gen.

## Test Signals
Recursive build and install tests should show `delay-gen.la` produced from the `src` directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/Makefile.am

## Purpose
This Automake file builds and installs the `delay-gen` debug translator module.

## Important APIs, Types, And Functions
It declares `xlator_LTLIBRARIES = delay-gen.la`, installs to `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/debug`, sets module linker flags, uses `delay-gen.c` as the source, links against `libglusterfs.la`, and marks `delay-gen.h`, `delay-gen-mem-types.h`, and `delay-gen-messages.h` as non-installed headers.

## Control Flow
Automake compiles `delay-gen.c` with `GF_CPPFLAGS`, RPC XDR include paths, `-Wall`, `-fno-strict-aliasing`, and `GF_CFLAGS`, then links the loadable xlator module.

## State And Persistence Behavior
No runtime state is held here. It controls produced build artifacts.

## Dependencies And Integration Points
The module depends on libglusterfs and GlusterFS build include variables. Install location matches the translator loader's debug xlator path.

## Risks
Incorrect install path, missing libglusterfs linkage, or missing include paths would produce a module that fails to build or load. Header list drift can break distribution builds.

## Test Signals
Build, install, and module-load tests should confirm `delay-gen` is compiled and discoverable by the GlusterFS xlator loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-mem-types.h

## Purpose
This header declares memory accounting IDs for the delay-gen debug translator.

## Important APIs, Types, And Functions
It defines enum `gf_delay_gen_mem_types_` with `gf_delay_gen_mt_dg_t` for the private `dg_t` allocation and `gf_delay_gen_mt_end` for registration.

## Control Flow
No executable control flow exists. `delay-gen.c` passes `gf_delay_gen_mt_end` to `xlator_mem_acct_init()` and uses `gf_delay_gen_mt_dg_t` when allocating private state.

## State And Persistence Behavior
It affects memory accounting labels only and persists no data.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and follows translator-local memory type numbering from `gf_common_mt_end + 1`.

## Risks
Adding allocations without corresponding types reduces diagnostic quality. Reordering is low risk for this small debug translator but still should be avoided.

## Test Signals
Translator initialization and memory-accounting dumps should show the delay-gen private allocation under this type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-messages.h -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-messages.h

## Purpose
This header reserves a message-ID header for delay-gen but currently declares no message IDs.

## Important APIs, Types, And Functions
It includes `<glusterfs/glfs-message-id.h>` and contains the standard append-only message-ID guidance, but no `GLFS_MSGID()` list.

## Control Flow
There is no control flow.

## State And Persistence Behavior
No state is held. If IDs are added later, they become stable log identifiers and should follow append-only rules.

## Dependencies And Integration Points
It is included by `delay-gen.h`, giving the translator a conventional place for structured logging IDs if it moves from `gf_log()` to `gf_msg()`.

## Risks
Current code logs with `gf_log()` and therefore lacks structured message IDs. Future additions must not reuse IDs or reorder an introduced list.

## Test Signals
Compilation is the main signal today. Static review should catch any future `gf_msg()` use without a corresponding ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.c -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.c

## Purpose
This debug translator probabilistically delays selected FOPs before forwarding them to the default child implementation. It is meant for timing, latency, and race-condition testing.

## Important APIs, Types, And Functions
`delay_gen()` checks whether a FOP is enabled and whether the configured probability hits; if so it sleeps for `delay_duration` microseconds using `gf_nanosleep()`. Macro `DG_FOP()` wraps each FOP implementation by calling `delay_gen()` and then `default_<fop>()`. The file defines wrappers for a broad set of FOPs including lookup, read, write, locks, xattrs, directory operations, allocation, discard, seek, lease, active-lock migration, and IPC. Lifecycle functions are `init()`, `fini()`, `mem_acct_init()`, `reconfigure()`, and `notify()`.

`delay_gen_parse_fill_fops()` parses the `enable` option. An empty string enables all FOPs from `GF_FOP_NULL + 1` to `GF_FOP_MAXVALUE - 1`; otherwise it treats the string as comma-separated FOP names and maps them through `gf_fop_int()`. `delay_gen_set_delay_ppm()` converts a user percentage into a threshold over `DELAY_GRANULARITY`.

## Control Flow
Initialization validates exactly one child translator, allocates `dg_t`, reads `delay-percentage`, `enable`, and `delay-duration`, computes the probability threshold, populates the enabled FOP bitmap, and stores `this->private`. Each FOP wrapper is synchronous: it may sleep in the caller's execution path, then forwards to the default stack implementation. `notify()` simply delegates to `default_notify()`. `reconfigure()` is a stub and does not update settings at runtime.

## State And Persistence Behavior
Runtime state is only `dg_t`: `delay_ppm`, `delay_duration`, and the `enable[]` bitmap. There is no persistent state and no per-inode/fd context. `rand()` is used without local seeding or locking in this file.

## Dependencies And Integration Points
The translator depends on GlusterFS defaults, FOP name mapping, option parsing, memory accounting, and the default pass-through xlator helpers. It is registered as a debug xlator with identifier `delay-gen` and tech-preview category.

## Risks
Because delay is injected synchronously before forwarding, it can block event or worker threads and amplify timing-sensitive deadlocks. `reconfigure()` doing nothing may surprise users who set options dynamically. The use of `rand()` gives process-global pseudo-random behavior and may not be thread-ideal. The wrapper list must track FOP table evolution or new FOPs will not be delayed.

## Test Signals
Tests should verify one-child validation, option parsing for empty and named FOP lists, invalid FOP names, probability extremes (`0%` and `100%`), approximate delay duration, pass-through correctness for representative FOPs, and that dynamic reconfigure currently has no effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.h -->
# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.h

## Purpose
This header defines the private state structure for the delay-gen debug translator.

## Important APIs, Types, And Functions
It includes delay-gen memory and message headers and defines `dg_t` with `uint32_t delay_ppm`, `uint32_t delay_duration`, and `bool enable[GF_FOP_MAXVALUE]`.

## Control Flow
No executable control flow exists. `delay-gen.c` reads and mutates the fields during initialization and FOP delay checks.

## State And Persistence Behavior
The `dg_t` instance is runtime-only and stored in `xlator_t->private`. It is allocated on `init()` and freed on `fini()`.

## Dependencies And Integration Points
The header relies on GlusterFS FOP enumeration size (`GF_FOP_MAXVALUE`) and the local mem/message headers. It is the shared contract between delay-gen implementation and any future helpers.

## Risks
If GlusterFS adds FOPs without increasing or correctly maintaining `GF_FOP_MAXVALUE`, the enable bitmap assumptions would break. `delay_ppm` is an integer threshold derived from a double percentage, so precision is bounded by `DELAY_GRANULARITY`.

## Test Signals
Build coverage is primary. Option parsing tests indirectly validate the bitmap length and state layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/error-gen/Makefile.am

## Purpose
This Automake file delegates the error-gen debug translator build to its `src` directory.

## Important APIs, Types, And Functions
It sets `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Recursive Automake targets enter `error-gen/src`, which declares the actual xlator module.

## State And Persistence Behavior
No runtime state is managed.

## Dependencies And Integration Points
It is listed by `xlators/debug/Makefile.am` and connects that parent build to `error-gen/src/Makefile.am`.

## Risks
Omitting `src` would remove error-gen from recursive builds and packages.

## Test Signals
Recursive build output should include `error-gen.la` from the child source directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/Makefile.am

## Purpose
This Automake file builds and installs the `error-gen` debug translator module.

## Important APIs, Types, And Functions
It declares `xlator_LTLIBRARIES = error-gen.la`, installs under the debug xlator directory, sets module linker flags, uses `error-gen.c`, links against `libglusterfs.la`, and includes `error-gen.h` and `error-gen-mem-types.h` as non-installed headers. It sets GlusterFS and RPC XDR include paths and builds with `-Wall`.

## Control Flow
Automake compiles the single source into a loadable xlator module and installs it where the GlusterFS translator loader expects debug modules.

## State And Persistence Behavior
No runtime state is held in this build file. It controls build artifacts only.

## Dependencies And Integration Points
It depends on libglusterfs and top-level GlusterFS build variables. It is reached from `xlators/debug/error-gen/Makefile.am`.

## Risks
Missing include paths or incorrect linker flags would break the module. Header list drift can cause distribution or clean builds to miss files.

## Test Signals
`make`, install/package tests, and module-load smoke tests should confirm `error-gen` is built and discoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen-mem-types.h

## Purpose
This header declares memory accounting IDs for the error-gen debug translator.

## Important APIs, Types, And Functions
It defines enum `gf_error_gen_mem_types_` with `gf_error_gen_mt_eg_t` for private error-gen state and `gf_error_gen_mt_end` as the registration limit.

## Control Flow
There is no runtime control flow. The implementation should use these IDs during memory-accounting initialization and private-state allocation.

## State And Persistence Behavior
It only labels heap allocations for diagnostics and persists no data.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and follows the translator-local numbering convention beginning at `gf_common_mt_end + 1`.

## Risks
Forgetting to use this type in allocations weakens memory diagnostics. Reordering enum values should be avoided for consistency with accounting output.

## Test Signals
Build coverage and memory-accounting dumps for error-gen should show allocations under the expected type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen-mem-types.h -->
