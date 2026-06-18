# Research: subset-b-007082

Grouped research for GlusterFS EC translator files under `sources/distributed-fs/glusterfs/xlators/cluster/ec/src`. Each section is delimited for reconciliation into the source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.h

Purpose: declares the portable C erasure-coding backend used when dynamic CPU-specific code is disabled or generation fails. It is the fallback ABI for computing linear and interleaved GF combinations.

Important APIs: `ec_code_c_prepare(ec_gf_t *gf, uint32_t *values, uint32_t count)` prepares static state for the portable routines; `ec_code_c_linear(void *dst, void *src, uint64_t offset, uint32_t *values, uint32_t count)` combines data from a linear source buffer; `ec_code_c_interleaved(void *dst, void **src, uint64_t offset, uint32_t *values, uint32_t count)` combines per-fragment source pointers. These prototypes depend on `ec-types.h` and the GF tables referenced through `ec_gf_t`.

Control flow and integration: `ec-code.c` calls `ec_code_c_prepare()` and returns one of these function symbols from `ec_code_build()` when no `ec_code_gen_t` is available. State is intentionally minimal at the header boundary; any persistent prepared state lives in the implementation, not in this header. Risks center on ABI compatibility with `ec_code_func_linear_t` and `ec_code_func_interleaved_t`, and on thread-safety of the portable implementation because the header exposes shared function symbols rather than per-build closures. Test signals should compare output parity/reconstruction against dynamic x64/SSE/AVX backends and force `cpu-extensions=none` or dynamic-generation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.c

Purpose: implements a small x86/x86-64 instruction encoder used by EC dynamic-code generators. It emits raw bytes for general-purpose, SSE, and AVX moves, XORs, arithmetic, tests, conditional branches, stack operations, and returns.

Important APIs and types: public emitters include `ec_code_intel_op_push_r`, `pop_r`, `ret`, `mov_r2r`, `mov_r2m`, `mov_m2r`, `xor_r2r`, `xor_m2r`, `add_i2r`, `test_i2r`, `jne`, SSE `mov/xor` variants, and AVX `mov/xor` variants. Internals build `ec_code_intel_t` with prefix/opcode/offset/immediate buffers plus REX, VEX, ModRM, and SIB state.

Control flow: each public helper initializes an encoder object, sets addressing/opcode/immediate fields, computes REX or VEX metadata, and calls `ec_code_intel_emit()`, which serializes prefixes, VEX/REX, opcodes, ModRM/SIB, displacement, and immediate bytes into a 15-byte local buffer before passing them to `ec_code_emit()`. `ec_code_intel_modrm_mem()` validates illegal addressing such as SP as an index and invalid scales, and marks the instruction invalid for `ec_code_error()`.

State and persistence: no disk persistence; emitted bytes are appended to the active `ec_code_builder_t`, which later writes into mmap-backed executable storage. Dependencies are `ec-code-intel.h`, `ec-code.h`, Gluster boolean/error conventions, and the builder error path. Risks include instruction-length overflow if a new encoding exceeds 15 bytes, incorrect VEX inverted-bit handling, branch displacement miscalculation in `jne`, and unsupported addressing combinations. Test signals are byte-level encoder tests, generated-function execution tests across low and high registers, SSE/AVX feature-gated tests, and fallback tests when invalid operands set builder errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.h

Purpose: defines the Intel instruction-emitter ABI shared by the x64, SSE, and AVX EC dynamic-code backends.

Important APIs/types: `ec_code_intel_reg_t` enumerates x86-64 registers with `REG_NULL` for no base/index; VEX prefix/opcode enums model two- and three-byte VEX forms. `ec_code_intel_buffer_t`, `ec_code_intel_sib_t`, `ec_code_intel_modrm_t`, `ec_code_intel_rex_t`, and `ec_code_intel_t` describe all encoded instruction fields. Exported functions emit push/pop/ret, GP register/memory moves and XORs, immediate add/test, `jne`, SSE moves/XORs, and AVX moves/XORs.

Control flow and integration: architecture-specific generators do not hand-encode bytes directly; they call this interface from their `ec_code_gen_t` callbacks. The header depends on `ec-code.h`, so every operation receives an `ec_code_builder_t` that owns output, current address, loop address, width, and error state.

State behavior: the structures are transient per instruction. Persistent generated code resides in `ec-code.c` chunks, while CPU feature selection is elsewhere. Risks include tight coupling to the System V register ABI assumed by `ec-code-x64.c`/`ec-code-sse.c`, enum value compatibility with REX/VEX bit construction, and absent prototypes for newer instructions if future backends are added. Test signals should compile all dynamic backends, verify declarations match definitions, and compare generated byte streams or execution output for each public emitter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.c

Purpose: implements the SSE2 dynamic backend for EC GF combination code. It emits vectorized loops that operate 16 bytes at a time using SSE registers.

Important APIs: the file exports `ec_code_gen_sse`, an `ec_code_gen_t` named `"sse"` requiring CPU flag `"sse2"`. Its callbacks are `ec_code_sse_prolog`, `epilog`, `load`, `store`, `copy`, `xor2`, and `xorm`; `xor3` is left `NULL`, causing the neutral builder to synthesize XOR3 through copy plus XOR2.

Control flow: `prolog` records the loop address. Each load chooses between linear addressing from `REG_SI + REG_DX` and interleaved addressing through a cached base pointer loaded from a source-pointer array. `store` writes to `REG_DI`, `copy` and `xor2` move/xor SSE registers, and `xorm` XORs memory into an SSE register. `epilog` advances source and destination offsets by 16, tests `REG_DX` against `width - 1`, branches back while more of the chunk remains, then returns.

State and integration: per-builder fields `linear`, `base`, `width`, `bits`, `loop`, and `address` drive emitted addressing. It depends on `ec-code-intel.c` for instruction bytes and on `ec-code.c` for scheduling GF operations. Risks include unaligned SSE memory assumptions, loop termination relying on power-of-two width, and stale `builder->base` for interleaved source arrays. Test signals should compare SSE output to C fallback over linear and interleaved layouts, run with misaligned buffers if supported, and verify CPU detection only selects this backend when `sse2` appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.h

Purpose: declares the SSE dynamic-code generator descriptor used by `ec-code.c` when `USE_EC_DYNAMIC_SSE` is compiled in.

Important API: `extern ec_code_gen_t ec_code_gen_sse;` exposes the backend descriptor. Consumers use it through the generic `ec_code_gen_t` vtable rather than calling SSE helpers directly.

Control flow and integration: `ec-code.c` places `&ec_code_gen_sse` in `ec_code_gen_table` behind AVX and before x64 depending on compile-time flags. `ec_code_detect()` validates CPU flags and returns this descriptor; `ec_code_build_dynamic()` then calls its callbacks to emit executable code.

State behavior: no mutable state is declared in the header. Runtime state lives in `ec_code_t`, `ec_code_builder_t`, and generated code chunks. Risks are mostly build-configuration risks: the header must only be included when the implementation is compiled, and the symbol must match the descriptor name. Test signals include builds with `USE_EC_DYNAMIC_SSE` toggled, CPU-detection tests for `"sse"`, and fallback checks when SSE generation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-sse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.c

Purpose: implements the scalar x86-64 dynamic backend for EC GF combination code, emitting 64-bit register operations as a baseline dynamic path when no vector backend is selected.

Important APIs: exports `ec_code_gen_x64` with no required CPU flags and width `sizeof(uint64_t)`. Internal callbacks implement prolog/epilog, load/store, register copy, register XOR, and memory XOR. `ec_code_x64_regmap` maps virtual GF registers onto x86-64 registers.

Control flow: the prolog saves `REG_BP`, optionally `REG_BX` for interleaved source base caching, verifies at most 11 mapped registers, saves extra callee-saved registers, and records the loop address. Load and xorm functions either address a linear source buffer or load a source pointer from an interleaved pointer array when the source index changes. Epilog increments `REG_DX` and `REG_DI` by 8, loops while masked offset bits remain, restores saved registers, and returns.

State and integration: this backend relies on the neutral builder to keep register pressure within `EC_GF_MAX_REGS` and on `ec-code-intel.c` for byte emission. It writes no persistent state beyond generated code chunks. Risks include register-save ABI mistakes, invalid register pressure for large GF tables, loop-width assumptions, and interleaved base caching across source indexes. Test signals should cover all GF widths that approach the 11-register limit, compare with C fallback, and run under sanitizers or valgrind-like tools to catch ABI clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.h

Purpose: declares the scalar x64 dynamic-code generator descriptor.

Important API: `extern ec_code_gen_t ec_code_gen_x64;` is consumed by `ec-code.c` when `USE_EC_DYNAMIC_X64` is enabled. The descriptor supplies generic callbacks for `ec_code_build_dynamic()`.

Control flow and integration: x64 is a fallback dynamic generator in `ec_code_gen_table`, generally after wider AVX/SSE backends. CPU detection can select it even without feature flags because its implementation requires only x86-64 baseline integer operations.

State behavior: this header declares no state. Generated functions are managed by `ec_code_t` and released through `ec_code_release()`. Risks are symbol/configuration mismatches and accidental inclusion on non-x64 builds if compile guards are wrong. Test signals include builds with only x64 dynamic support, explicit `cpu-extensions=x64`, and parity output comparison to the portable C backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.c

Purpose: owns EC dynamic code generation, executable memory management, portable fallback selection, and CPU-extension detection. It turns GF multiplication plans into linear or interleaved function pointers used by EC methods.

Important APIs: `ec_code_detect()`, `ec_code_create()`, `ec_code_destroy()`, `ec_code_build_linear()`, `ec_code_build_interleaved()`, `ec_code_release()`, `ec_code_error()`, and `ec_code_emit()`. Internal builder helpers emit neutral GF ops (`LOAD`, `STORE`, `COPY`, `XOR2`, optional `XOR3`, `XORM`), duplicate precomputed GF multiplication operations, and compile them through an `ec_code_gen_t`.

Control flow: `ec_code_build()` tries dynamic generation if a generator exists. `ec_code_build_dynamic()` walks nonzero coefficient values, loading the first input, multiplying by ratios between coefficients with `ec_gf_div()`, XORing later inputs, multiplying by the final coefficient, and storing the result; zero coefficients produce a clear. `ec_code_compile()` first dry-runs to calculate size, allocates an executable chunk, then emits bytes for real. On dynamic failure, it disables the generator and returns `ec_code_c_linear` or `ec_code_c_interleaved`.

State and persistence: code chunks live in mmap-backed temporary-file storage with separate writable and executable mappings to avoid W+X memory. `ec_code_space_t` and `ec_code_chunk_t` lists provide allocation, splitting, merging, and release under `code->lock`. CPU detection reads `/proc/cpuinfo` flags and chooses the first supported compiled backend or a named backend. Risks include executable mapping portability, chunk fragmentation or leaks, code release on fallback pointers, parser assumptions for `/proc/cpuinfo`, and dynamic code correctness for sparse coefficient arrays. Test signals include forced `none`, `auto`, and named CPU extensions, simulated unsupported features, repeated build/release cycles, SELinux/noexec scenarios, and output equivalence across C/dynamic backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.h

Purpose: public interface for EC code-generation selection, lifecycle, build, release, and byte emission.

Important APIs: `ec_code_detect(xlator_t *xl, const char *def)` selects an optional dynamic generator; `ec_code_create()` binds a GF table to a generator; `ec_code_build_linear()` and `ec_code_build_interleaved()` return executable combination callbacks; `ec_code_release()` frees dynamic functions; `ec_code_error()` and `ec_code_emit()` are backend-facing hooks for reporting generation failures and appending bytes.

Control flow and integration: higher EC method code calls the build functions with coefficient arrays. Architecture backends include this header to receive the builder type and emit bytes, while callers only see function pointers. The header depends on `ec-types.h`, `ec-galois.h`, and Gluster list support.

State behavior: `ec_code_t` owns backend selection, GF metadata, and generated-code spaces; the header hides structure details in `ec-types.h`. No persistent on-disk state is exposed. Risks include lifecycle misuse, especially releasing fallback C symbols or calling generated functions after `ec_code_destroy()`, and ABI mismatch between function pointer typedefs and backend calling conventions. Test signals should pair every successful build with release, exercise both linear and interleaved signatures, and run fallback paths after dynamic errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.c

Purpose: combines, compares, and normalizes callback answers received from multiple EC child bricks. It determines which answers are equivalent enough to form quorum and rebuilds aggregate metadata for the upper translator.

Important APIs: `ec_combine()`, `ec_combine_check()`, `ec_combine_write()`, `ec_iatt_combine()`, `ec_iatt_rebuild()`, `ec_dict_compare()`, `ec_dict_combine()`, `ec_vector_compare()`, `ec_flock_compare()`, and `ec_statvfs_combine()`. Specialized dictionary handlers merge pathinfo, clear-lock output, lockinfo dictionaries, link/fd/lock counts, quota metadata, node UUID lists, stime/xtime markers, and embedded iatt values.

Control flow: new callbacks are inserted into `fop->cbk_list` ordered by equivalent-answer count. `ec_combine_check()` first compares return values and errno, filters xdata through `ec_dict_compare()`, and delegates successful fop-specific iatt comparison to functions such as `ec_combine_write()`. If a new answer matches an existing answer, masks and counts are merged and the linked answer is chained through `next`. When all dispatched replies are received but the best answer is below minimum, `ec_combine()` dispatches another child.

State and persistence: state is in `ec_cbk_data_t` lists, masks, counts, and dictionaries; there is no direct persistence. Metadata scaling is EC-specific: `ec_iatt_rebuild()` adjusts block counts by fragments/answer count, quota size is multiplied by fragments, and regular-file sizes may be replaced by trusted EC size xattrs in other callers. Dependencies include Gluster dict/data APIs, quota helpers, marker/stime helpers, and EC lock context. Risks include treating benign xattr drift as mismatch, missing new fop-specific iatt counts, stack VLA size tied to `ec->nodes`, and subtle ordering errors in the answer list. Test signals should inject mixed successful/error callbacks, divergent xdata, quota/pathinfo/lockinfo xattrs, write fop iatt mismatches, and cases requiring extra dispatch to reach quorum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.h

Purpose: declares answer-combination helpers used by EC fop managers and callbacks.

Important APIs/types: `EC_COMBINE_DICT` and `EC_COMBINE_XDATA` select dictionary sources; `ec_combine_f` is the fop-specific comparator/merger callback. Exported functions cover iatt rebuild/combine, dictionary compare/combine, vector/flock/statvfs comparison or merge, generic callback combination, and write-fop combination.

Control flow and integration: callbacks allocate `ec_cbk_data_t`, populate fop-specific fields, then call `ec_combine(cbk, combine_func)`. Managers later call `ec_fop_prepare_answer()`, which uses `ec_dict_combine()` on the selected best callback. This header depends on EC callback/fop types from `ec-types.h` through includers.

State behavior: the interface mutates callback data in place, especially masks, counts, dictionaries, and iatt arrays. No persistent storage is owned here. Risks include passing the wrong `which` selector, using `NULL` combine functions for fops that need fop-specific validation, and header include-order assumptions because it does not include `ec-types.h` itself. Test signals include compile coverage for all includers and unit-style callback combination tests for every exported comparator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.c

Purpose: core EC operation engine. It manages child selection, dispatch, quorum completion, parent/child fop scheduling, lock acquisition/reuse/release, version/dirty/size xattr maintenance, healing triggers, fd reopen repair, and the generic fop state-machine loop.

Important APIs: `ec_update_fd_status()`, `ec_dispatch_one/inc/all/min()`, `ec_dispatch_one_retry()`, `ec_complete()`, `ec_update_good()`, `ec_fop_prepare_answer()`, `ec_sleep()`, `ec_resume()`, `ec_lock_prepare_inode/parent_inode/fd()`, `ec_lock()`, `ec_lock_reuse()`, `ec_unlock()`, `ec_flush_size_version()`, `ec_get/set_inode_size()`, `ec_clear_inode_info()`, `ec_lock_release()`, `ec_manager()`, and `ec_msg_str()`.

Control flow: managers call lock preparation, dispatch, answer preparation, reporting, lock reuse, and unlock states through `ec_manager()`. Dispatch selects available children from masks, read policy, parent restrictions, quorum rules, healing bits, and minimum semantics. Callbacks feed `ec_combine()`, then `ec_complete()` chooses an answer once enough matching replies exist. Locks are represented by inode-scoped `ec_lock_t` plus per-fop `ec_lock_link_t`; links move among pending, owner, waiting, frozen, and delayed-unlock states.

State and persistence: persistent consistency metadata is stored in trusted EC xattrs: `EC_XATTR_VERSION`, `EC_XATTR_DIRTY`, `EC_XATTR_SIZE`, and `EC_XATTR_CONFIG`. `ec_get_size_version()` uses xattrop/fxattrop to fetch and optionally dirty metadata before the main fop. `ec_update_info()` computes post/pre version and size deltas, clears dirty flags when all nodes are up and good, or leaves dirty markers for heal. In-memory state includes inode ctx size/version/config flags, bad-version counters, fd open status, good/healing masks, eager-lock timers, and stripe-cache contents.

Dependencies/integration: this file orchestrates most EC modules: fop wrappers in `ec-fops.h`, answer merging in `ec-combine`, xattr helpers in `ec-helpers`, GF methods, self-heal calls, Gluster locks, timers, dicts, inode/fd contexts, and child xlator fops. Risks are high: lock ordering deadlocks, use-after-free around sleep/resume, stale eager locks, incomplete dirty/version updates after partial failure, read-policy child selection with changing masks, fd reopen races, and incorrect handling while `ec->xl_up_count < fragments`. Test signals should stress parallel writes with range locking, eager-lock contention and timeout, partial brick failures, heal-trigger logging, fd reopen after disconnection, dirty xattr clearing/retention, version increments, state-machine error paths, and shutdown while delayed unlock timers exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.h

Purpose: central declaration header for EC common state-machine, dispatch, lock, inode-size, heal, and quorum helpers.

Important APIs/types/macros: defines transaction indexes `EC_DATA_TXN`/`EC_METADATA_TXN`, internal heal fop ids, config constants, lock flag `EC_FLAG_LOCK_SHARED`, quorum wrapper `QUORUM_CBK`, xattrop flag packing macros, state constants (`EC_STATE_INIT`, `LOCK`, `DISPATCH`, `PREPARE_ANSWER`, `REPORT`, `LOCK_REUSE`, `UNLOCK`, heal states), update/query flags, and `EC_RANGE_FULL`. Prototypes expose dispatch variants, completion, error handling, answer preparation, lock preparation/release, inode size cache access, manager/resume/sleep functions, heal info, fd status updates, and message formatting.

Control flow and integration: all concrete fop files include this header to build managers that move through the shared states. `QUORUM_CBK` enforces user-visible quorum by converting an otherwise successful callback to `EIO` when successful child count is below `ec->quorum_count` for normal client traffic.

State behavior: the macros encode the contract between fop managers and `ec-common.c`: flags indicate data/meta dirtying, minimum dispatch requirements, and whether parent errors propagate. The header itself stores no state. Risks include state-number collisions, incorrect bit packing if more than 16 xattrop flags are added, misusing `EC_FOP_MINIMUM()` with non-minimum flag bits, and forgetting to use `QUORUM_CBK` for mutating fops. Test signals should include compile coverage for every manager state, quorum-count behavior under insufficient good masks, and flag packing/unpacking tests around `EC_FLAG_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.c

Purpose: allocates, initializes, references, cleans up, and releases EC fop and callback data objects.

Important APIs: `ec_cbk_data_allocate()`, `ec_cbk_data_destroy()`, `ec_fop_data_allocate()`, `ec_fop_data_acquire()`, `ec_fop_cleanup()`, and `ec_fop_data_release()`. Allocation uses pools from `ec_t` (`cbk_pool`, `fop_pool`) and initializes list heads, locks, masks, callbacks, private frames, parent relationships, user/group ids, and pending-fop linkage.

Control flow: callbacks call `ec_cbk_data_allocate()` after validating frame/xlator/fop identity; the callback is appended to `fop->answer_list`. Fop wrappers call `ec_fop_data_allocate()` to create a private frame, set `frame->local`, sleep the parent if nested, and append to `ec->pending_fops`. Reference release destroys the private stack, unrefs dicts/inodes/fds/iobrefs, frees vectors/strings/locations/error strings, resumes the parent, destroys callback answers, removes pending-fop tracking, handles healer completion, and emits pending-complete notification when this was the last fop.

State and persistence: no disk persistence; this is in-memory lifecycle state. It protects refcount changes with `fop->lock` and pending list changes with `ec->lock`. Dependencies include Gluster memory pools, frames/stacks, dict/inode/fd/iobref reference APIs, EC common resume/pending/healer functions, and message IDs. Risks include mismatched frame or fop ids silently dropping callbacks, reference leaks on partial setup failure, parent resume error propagation, and list cleanup ordering. Test signals should cover allocation failure paths, nested fop parent sleep/resume, callback destruction with every optional field populated, and last-pending-fop notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.h

Purpose: declares the EC fop/callback data lifecycle interface.

Important APIs: `ec_cbk_data_allocate()` creates per-child callback records; `ec_fop_data_allocate()` creates a managed fop with wind/handler/callback union and caller data; `ec_fop_data_acquire()` and `ec_fop_data_release()` manage fop references; `ec_fop_cleanup()` clears accumulated answers; `ec_pending_fops_completed()` is the completion notification hook used when the pending list drains.

Control flow and integration: fop entry points allocate `ec_fop_data_t`, populate operation-specific fields, and start `ec_manager()`. Child callbacks allocate `ec_cbk_data_t`, combine answers, and call `ec_complete()`. Release interacts with `ec-common.c` for parent resume and pending-fop completion.

State behavior: the header exposes lifecycle ownership but not the full struct layout, which is defined through `ec-types.h`. Risks are ownership mismatches: callers must not release borrowed callback fields, and every acquire/sleep path must eventually release/resume. Test signals include compile checking all fop wrappers against the allocation signature and lifecycle tests that prove answer cleanup does not leak dicts, fds, inodes, iobuf refs, or vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-read.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-read.c

Purpose: implements EC directory read operations: `opendir`, `readdir`, and `readdirp`.

Important APIs: callbacks `ec_opendir_cbk()` and `ec_common_readdir_cbk()`, wind functions for each fop, managers `ec_manager_opendir()` and `ec_manager_readdir()`, entry points `ec_opendir()`, `ec_readdir()`, `ec_readdirp()`, plus helpers `ec_combine_opendir()`, `ec_deitransform()`, and `ec_adjust_readdirp()`.

Control flow: `opendir` copies location/fd/xdata, locks the directory inode for query info, dispatches to all selected children, combines only matching fd answers, records the opened-child mask in fd ctx, reports, then reuses/unlocks the lock. `readdir`/`readdirp` require fd ctx `open != 0`; at offset zero they lock/query the fd and dispatch to one child by read policy, retrying recoverable failures on another child. At nonzero offsets, `ec_deitransform()` decodes the client id embedded by Gluster directory offsets and pins dispatch to that child because offsets are not portable across bricks.

State and persistence: fd context `ctx->open` tracks children on which the directory fd is open. `readdirp` requests `EC_XATTR_SIZE` and `ec_adjust_readdirp()` rebuilds regular-file stats from EC size xattrs, dropping inode references when size data is absent. Dependencies include Gluster dirent lists, offset transform mapping `leaf_to_subvolid`, EC locks, combine/common helpers, and child fops. Risks include invalid offset-to-child mapping, readdirp returning unusable inode/stat data without EC size, stale fd open masks after brick failure, and missing callback validation for dict refs. Test signals should cover opendir partial success, readdir after unopened fd, nonzero offsets from invalid/valid children, recoverable retry on ENOTCONN/ESTALE/ENOENT/EBADFD/EIO, and readdirp entries with and without EC size xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-write.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-write.c

Purpose: implements EC directory-entry mutating fops: `create`, `link`, `mkdir`, `mknod`, `rename`, `rmdir`, `symlink`, and `unlink`.

Important APIs: common callback `ec_dir_write_cbk()` collects up to five iatt values and xdata, then calls `ec_combine_write()`. Each fop has a callback, wind function, manager, and public entry point. Managers use common states for lock, dispatch, answer preparation, report, lock reuse, and unlock.

Control flow: create/mknod regular-file creation inject EC config, zero version, and zero size xattrs into xdata before dispatch, and create strips `O_APPEND` because EC writes to explicit fragment offsets. Directory mutations lock parent inodes with data/meta updates; link and rename may pass a base inode for size lookup (`EC_INODE_SIZE`) so returned regular-file iatts can use true EC size. Rename prepares both old and new parent locks. Successful answers rebuild iatt block accounting with `ec_iatt_rebuild()`, update loc/inode cache for created/linked/mkdir/mknod/symlink objects, then report through `QUORUM_CBK` where appropriate.

State and persistence: persistent EC metadata is initialized through `EC_XATTR_CONFIG`, `EC_XATTR_VERSION`, and `EC_XATTR_SIZE` for regular files. Lock reuse/unlock in `ec-common.c` updates version/dirty xattrs for parent directory metadata. In-memory fop fields carry flags, modes, umask, rdev, linkname, xdata copies, and locs. Dependencies include `ec-method.h` for chunk/config constants, child xlator fops, common locks/dispatch, and combine logic. Risks include partial namespace mutation when quorum/reporting semantics diverge, missing EC metadata on regular-file creation, stale iatt sizes for link/rename, two-lock ordering in rename, xdata ownership differences between ref and copy, and callbacks assuming non-NULL user callback on allocation failure. Test signals should cover every fop under partial brick failure, quorum failure, same-directory rename, cross-directory rename, regular vs special mknod, create with O_APPEND, xdata allocation failures, and post-operation xattr version/dirty updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-dir-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-fops.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-fops.h

Purpose: declares the EC translator's full fop wrapper surface. These functions are the internal entry points used by Gluster fop tables, EC sub-operations, and common repair/dispatch code.

Important APIs: prototypes cover metadata, namespace, file data, xattr, lock, heal, seek, ipc, and directory operations: access/create/entrylk/fentrylk/flush/fsync/fsyncdir/getxattr/fgetxattr/heal/fheal/inodelk/finodelk/link/lk/lookup/mkdir/mknod/open/opendir/readdir/readdirp/readlink/readv/removexattr/fremovexattr/rename/rmdir/setattr/fsetattr/setxattr/fsetxattr/stat/fstat/statfs/symlink/fallocate/discard/truncate/ftruncate/unlink/writev/xattrop/fxattrop/seek/ipc.

Control flow and integration: every prototype follows the EC pattern: caller frame, translator, target mask, fop flags, typed callback, callback data, fop-specific arguments, and xdata. Implementations allocate `ec_fop_data_t`, populate fields, then call `ec_manager()` with fop-specific manager/wind callbacks. The header includes `ec-types.h` and `ec-common.h`, so it also imports shared fop flag/minimum semantics.

State behavior: this header stores no state but defines the ABI through which stateful managers receive loc/fd/dict/iovec/lock arguments. Risks are signature drift against Gluster fop table typedefs, callback union mismatches, and accidental omission when new fops are added to the translator. Test signals include full translator build with `-Werror` prototypes, fop-table initialization coverage, and smoke tests that exercise every declared wrapper through mounted EC volumes or targeted translator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-fops.h -->
