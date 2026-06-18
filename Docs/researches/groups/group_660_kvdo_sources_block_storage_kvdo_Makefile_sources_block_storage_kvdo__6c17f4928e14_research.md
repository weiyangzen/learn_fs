# Group Research: group_660_kvdo_sources_block_storage_kvdo_Makefile_sources_block_storage_kvdo__6c17f4928e14

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/kvdo`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/Makefile -->
# File Research: sources/block-storage/kvdo/Makefile

## Purpose

Top-level Kbuild makefile for the kvdo source tree. It delegates all build participation to the `vdo/` subdirectory.

## Contents

- Adds `vdo/` to `obj-y`, causing Kbuild to descend into `sources/block-storage/kvdo/vdo`.

## Dependencies and Interactions

- Relies on `sources/block-storage/kvdo/vdo/Makefile` for actual module object definitions and compiler flags.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/Makefile -->
# File Research: sources/block-storage/kvdo/vdo/Makefile

## Purpose

Kbuild makefile for building the `kvdo` kernel module from all C sources in the `vdo` directory.

## Main Responsibilities

- Defines `VDO_VERSION = 8.2.7.4`.
- Discovers local C files with `$(wildcard $(src)/*.c)` and maps them to object files.
- Adds `-I$(src)` include path.
- Derives `RHEL_RELEASE_EXTRA` from `uname -r` unless supplied externally.
- Sets module compiler flags:
  - GNU11 mode,
  - no builtin `memset`,
  - `-Werror`,
  - optional stack-frame limit when KASAN is disabled,
  - `CURRENT_VERSION`,
  - `RHEL_RELEASE_EXTRA`.
- Builds `kvdo.o` as `obj-m` from all discovered objects.

## Notable Details

Every `.c` file in this directory becomes part of `kvdo-objs`, so adding a C file automatically links it into the module.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/action-manager.c -->
# File Research: sources/block-storage/kvdo/vdo/action-manager.c

## Purpose

Implements `struct action_manager`, a generic asynchronous coordinator for applying an operation across multiple VDO zones while preserving single-operation semantics for a shared context.

## Main Responsibilities

- Allocates and initializes action managers with:
  - zone count,
  - zone-to-thread resolver,
  - initiator thread,
  - shared context,
  - optional default scheduler,
  - embedded `VDO_ACTION_COMPLETION`,
  - embedded admin state.
- Maintains exactly two action slots:
  - one current action,
  - one pending action.
- Rejects a third concurrent schedule request with `VDO_COMPONENT_BUSY`.
- Runs each action as:
  - preamble on initiator thread,
  - optional zone action on each zone thread in order,
  - conclusion back on initiator thread,
  - parent completion notification.
- Integrates with `admin-state.c` using operation state codes.
- Supports default follow-up work via a scheduler called after each action if no pending explicit action exists.

## Key Structures

- `struct action`
  - `in_use`,
  - admin operation code,
  - preamble callback,
  - per-zone action callback,
  - conclusion callback,
  - parent completion,
  - action-specific context,
  - next slot pointer.
- `struct action_manager`
  - reusable completion,
  - admin state,
  - two `struct action` slots,
  - current slot pointer,
  - zone/thread metadata,
  - default scheduler,
  - shared context,
  - current acting zone.

## Important Functions

- `vdo_make_action_manager()` allocates and initializes the manager and circular two-slot action list.
- `vdo_get_current_manager_operation()` returns the manager’s current admin operation code.
- `vdo_get_current_action_context()` returns the active action-specific context if any.
- `vdo_schedule_default_action()` asks the default scheduler to schedule work only during normal operation.
- `vdo_schedule_action()` schedules a generic `VDO_ADMIN_STATE_OPERATING` action.
- `vdo_schedule_operation()` schedules a named admin operation without extra context.
- `vdo_schedule_operation_with_context()` is the core scheduler and optional action-context entry point.

## Behavior Details

`launch_current_action()` first starts the admin operation with `vdo_start_operation()`. If state transition fails, it stores the error in the parent and skips preamble/conclusion work. Otherwise, it prepares the reusable completion for either zone traversal or direct conclusion.

Zone traversal is serialized through one completion. `apply_to_zone()` runs on the current zone’s thread, increments `acting_zone`, prepares the same completion for the next zone or conclusion, and invokes the zone callback.

`finish_action_callback()` copies the current action locally before running conclusion or parent notification, avoiding use-after-free if callbacks destroy the manager. It clears the slot, advances to the next slot, possibly schedules default work, finishes the admin operation, completes the parent, then launches pending/default work.

## Dependencies and Interactions

- Uses `admin-state.c` to enforce valid operation transitions.
- Uses `completion.c` for requeueing callbacks across VDO worker threads.
- Used by multi-zone systems such as the block map and slab depot/block allocator paths.

## Notable Edge Cases

- At least one of preamble, zone action, or conclusion is expected by contract; NULL preamble/conclusion are replaced by no-op implementations.
- Scheduling is asserted to happen on the initiator thread.
- Preamble errors skip zone actions but still route to conclusion/finish logic.
- Only one pending action is supported.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/action-manager.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/action-manager.h -->
# File Research: sources/block-storage/kvdo/vdo/action-manager.h

## Purpose

Declares the action-manager API used to coordinate asynchronous operations across multiple zones.

## Contents

- Documents the action model:
  - optional preamble on initiator thread,
  - optional action per zone,
  - optional conclusion on initiator thread,
  - optional parent completion.
- Declares callback typedefs:
  - `vdo_zone_action`,
  - `vdo_action_preamble`,
  - `vdo_action_conclusion`,
  - `vdo_action_scheduler`,
  - `vdo_zone_thread_getter`.
- Declares construction, status, context, and scheduling functions.

## Dependencies and Role

The header forms the public internal contract for multi-zone components that need serialized operation execution, especially block map and slab/depot operations.

## Notable Details

The API distinguishes generic actions from named admin-state operations, and also provides a context-bearing scheduler variant for recovery or growth workflows that need temporary operation-specific state.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/action-manager.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-completion.c -->
# File Research: sources/block-storage/kvdo/vdo/admin-completion.c

## Purpose

Implements synchronous administrative operation orchestration on top of VDO’s asynchronous completion system.

## Main Responsibilities

- Initializes an embedded admin completion and sub-task completion for a `struct vdo`.
- Enforces one admin operation at a time using `atomic_t busy`.
- Provides helpers to:
  - assert expected admin operation type,
  - recover `struct admin_completion` from a sub-task completion,
  - recover `struct vdo` from an admin sub-task,
  - assert phase-specific thread affinity.
- Prepares admin sub-task completions to run on the current phase thread.
- Runs an admin operation by enqueueing a sub-task and waiting for completion.

## Important Functions

- `vdo_initialize_admin_completion()` initializes admin and sub-task completions plus the Linux completion used for synchronization.
- `vdo_reset_admin_sub_task()` resets a sub-task and assigns the current phase thread.
- `vdo_prepare_admin_sub_task()` prepares a sub-task on the same thread as the enclosing admin completion.
- `vdo_perform_admin_operation()` is the synchronous entry point for load, suspend, resume, and grow operations.

## Behavior Details

`vdo_perform_admin_operation()` uses `atomic_cmpxchg()` to reject concurrent admin operations. It prepares the outer admin completion to run on the admin thread, records operation type and phase thread resolver, prepares the sub-task, enqueues it, then waits on a Linux `struct completion`.

The wait uses `wait_for_completion_interruptible()` to avoid long kernel wait warnings, but ignores signals and sleeps briefly before retrying. Once the callback signals completion, the result is read, a write barrier is issued, and `busy` is cleared.

## Dependencies and Interactions

- Depends on `completion.c` for callback execution.
- Uses `thread-config.h` for admin thread selection.
- Used by higher-level VDO administrative workflows that need a blocking kernel-control path over async base-thread work.

## Notable Edge Cases

- A second admin operation returns/logs `VDO_COMPONENT_BUSY`.
- Signals during the wait do not abort the operation.
- Thread assertions are log-only assertions through `ASSERT_LOG_ONLY`.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-completion.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-completion.h -->
# File Research: sources/block-storage/kvdo/vdo/admin-completion.h

## Purpose

Declares the admin completion structure and helper API for synchronous administrative VDO operations.

## Contents

- Defines `enum admin_operation_type`:
  - unknown,
  - logical grow,
  - physical grow,
  - prepare physical grow,
  - load,
  - pre-load,
  - resume,
  - suspend.
- Defines `vdo_thread_id_getter_for_phase`.
- Defines `struct admin_completion` with:
  - owning `struct vdo`,
  - outer completion,
  - sub-task completion,
  - busy flag,
  - operation type,
  - phase thread resolver,
  - phase index,
  - Linux completion for synchronous callback wait.
- Declares helpers for assertions, sub-task preparation, initialization, and operation execution.

## Dependencies and Role

This header is the bridge between control-plane operations and the VDO base-thread completion model.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-completion.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-state.c -->
# File Research: sources/block-storage/kvdo/vdo/admin-state.c

## Purpose

Implements the administrative state machine used by VDO components to serialize and validate load, drain, suspend, resume, save, stop, recovery, rebuild, and generic operation transitions.

## Main Responsibilities

- Defines all exported `struct admin_state_code` instances.
- Tags each state code with semantic flags:
  - `normal`,
  - `draining`,
  - `loading`,
  - `quiescing`,
  - `quiescent`,
  - `operating`.
- Computes valid next states for requested operations.
- Starts operations with optional waiters and initiator callbacks.
- Finishes operations and notifies waiters.
- Provides typed start/finish helpers for:
  - draining,
  - loading,
  - resuming,
  - generic operations.
- Provides validation helpers for operation categories.

## State Model

States are represented as pointers to immutable state-code objects, not as a numeric enum. This lets callers compare identity for exact states while also querying categories through flags.

Examples:
- `VDO_ADMIN_STATE_NORMAL_OPERATION`: normal.
- `VDO_ADMIN_STATE_OPERATING`: normal and operating.
- `VDO_ADMIN_STATE_SAVING`: draining, quiescing, operating.
- `VDO_ADMIN_STATE_SAVED`: quiescent.
- `VDO_ADMIN_STATE_LOADING`: normal, operating, loading.
- `VDO_ADMIN_STATE_RECOVERING`: draining and operating.
- `VDO_ADMIN_STATE_SUSPENDED_OPERATION`: operating, with next state preserving suspended/saved state.

## Important Functions

- `get_next_state()` validates whether an operation can start from the current state and returns the state to install after completion.
- `begin_operation()` is the core transition routine.
- `vdo_finish_operation()` records result, installs `next_state`, and completes waiter when appropriate.
- `vdo_start_draining()` starts a drain only from normal state, or completes immediately if already quiescent.
- `vdo_finish_draining_with_result()` finishes a draining state.
- `vdo_start_loading()` and `vdo_finish_loading_with_result()` handle loading states.
- `vdo_start_resuming()` and `vdo_finish_resuming_with_result()` handle resume operations.
- `vdo_resume_if_quiescent()` directly returns quiescent states to normal operation.
- `vdo_start_operation()` and `vdo_start_operation_with_waiter()` handle generic operating states.

## Behavior Details

`begin_operation()` rejects starts if:
- the requested operation has no valid next state from the current state,
- another waiter is already registered,
- the current state is already operating.

If an initiator is provided, `begin_operation()` sets `starting = true`, calls the initiator, clears `starting`, then handles synchronous completion if the operation finished during initiator execution. This avoids completing the waiter while the initiator call stack is still active.

`vdo_finish_operation()` preserves operation result in the waiter before completing it. If called while `starting` is true, it records completion and defers final transition until initiator return.

## Dependencies and Interactions

- Used by `action-manager.c`, `block-map.c`, `block-allocator.c`, and other VDO subsystems.
- Uses `completion.c` to notify operation waiters.
- Uses VDO status codes for busy and invalid-state failures.

## Notable Edge Cases

- A drain request on an already quiescent state completes its waiter and returns false.
- Suspended operations preserve the current quiescent state as their next state.
- `VDO_ADMIN_STATE_PRE_LOADING` only starts from initialized and ends in pre-loaded.
- Exact-state helpers in the header coexist with category-based validation here.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-state.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-state.h -->
# File Research: sources/block-storage/kvdo/vdo/admin-state.h

## Purpose

Declares the VDO administrative state model and transition APIs.

## Contents

- Defines `struct admin_state_code` category flags and state name.
- Extern-declares all state-code pointers.
- Defines `struct admin_state`:
  - current state,
  - next state,
  - waiter completion,
  - `starting` flag,
  - `complete` flag.
- Provides inline state predicates:
  - normal,
  - suspending,
  - saving,
  - saved,
  - draining,
  - loading,
  - resuming,
  - clean load,
  - quiescing,
  - quiescent.
- Declares start/finish APIs for drain, load, resume, generic operations, and direct quiescent resume.

## Dependencies and Role

This header is central to administrative flow control across VDO components. Components use it to block incompatible work while preserving consistent completion behavior.

## Notable Details

`vdo_set_operation_result()` only updates a waiter if one exists, making it safe for components to preserve errors opportunistically during multi-step operations.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/admin-state.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/allocation-selector.c -->
# File Research: sources/block-storage/kvdo/vdo/allocation-selector.c

## Purpose

Implements round-robin physical-zone selection for zones that allocate data blocks.

## Main Responsibilities

- Allocates and initializes an `allocation_selector`.
- Chooses an initial physical zone from `thread_id % physical_zone_count`.
- Returns the current zone for allocation.
- Advances to the next zone after `ALLOCATIONS_PER_ZONE` allocations.

## Important Functions

- `vdo_make_allocation_selector()` allocates and initializes selector state.
- `vdo_get_next_allocation_zone()` increments allocation count and rotates zones.

## Behavior Details

Each selector uses 128 allocations per zone before rotating. If there is only one physical zone, the selector never rotates.

## Dependencies

- Uses VDO/UDS memory allocation helpers.
- Uses VDO zone and thread typedefs.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/allocation-selector.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/allocation-selector.h -->
# File Research: sources/block-storage/kvdo/vdo/allocation-selector.h

## Purpose

Declares the allocation selector used for round-robin physical-zone allocation.

## Contents

- Documents allocation selectors.
- Defines `struct allocation_selector`:
  - `allocation_count`,
  - `next_allocation_zone`,
  - `last_physical_zone`.
- Declares construction and next-zone selection APIs.

## Notable Details

The comment says “last_physical_cone” for the `last_physical_zone` field, which is a typo in documentation only.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/allocation-selector.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/atomic-stats.h -->
# File Research: sources/block-storage/kvdo/vdo/atomic-stats.h

## Purpose

Defines atomic statistics counters for VDO bio and metadata I/O accounting.

## Contents

- `struct atomic_bio_stats`
  - read,
  - write,
  - discard,
  - flush,
  - empty flush,
  - FUA.
- `struct atomic_statistics`
  - submitted/completed bio counts,
  - flush output,
  - invalid advice,
  - no-space errors,
  - read-only errors,
  - categorized atomic bio stat groups for incoming, outgoing, metadata, journal, and page-cache I/O.

## Dependencies and Role

Uses Linux `atomic64_t` because updates may come from arbitrary concurrent threads.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/atomic-stats.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/bio.c -->
# File Research: sources/block-storage/kvdo/vdo/bio.c

## Purpose

Implements VDO helpers for Linux `struct bio` data movement, allocation, initialization, completion, and statistics accounting.

## Main Responsibilities

- Copies data between bios and linear buffers.
- Allocates and frees VDO-owned bios.
- Counts bios by operation and flags.
- Completes VDO async bios by continuing their owning `vio`.
- Initializes bio fields for VDO I/O.
- Resets a VDO-owned bio around a 4 KiB-aligned buffer, including vmalloc-backed memory.

## Important Functions

- `vdo_bio_copy_data_in()` copies bio segment data into a buffer.
- `vdo_bio_copy_data_out()` copies a buffer into bio segments.
- `vdo_free_bio()` uninitializes and frees a VDO-owned bio.
- `vdo_count_bios()` increments atomic operation counters.
- `vdo_count_completed_bios()` increments completed counters by vio type.
- `vdo_complete_async_bio()` counts completion and continues the owning vio with the bio result.
- `vdo_set_bio_properties()` sets private data, endio callback, op flags, and sector.
- `vdo_reset_bio_with_buffer()` resets and populates bio vectors for a supplied buffer.
- `vdo_create_multi_block_bio()` allocates a bio with inline vec storage.

## Behavior Details

`vdo_count_bios()` treats an empty `REQ_PREFLUSH` bio as both `empty_flush` and `flush`, then returns. Other bios are classified as write, read, or discard and separately counted for preflush/FUA flags.

`vdo_set_bio_properties()` converts VDO physical block numbers to sectors and subtracts `geometry.bio_offset` for normal VIO-backed I/O. The geometry block location sentinel is exempt.

`vdo_reset_bio_with_buffer()` supports kernel API differences around `bio_reset()` through version/RHEL conditionals. It builds page vectors using `vmalloc_to_page()` for vmalloc memory or `virt_to_page()` otherwise.

## Dependencies and Interactions

- Depends on Linux block bio APIs.
- Interacts with `vio`, `vdo`, and `atomic-stats`.
- Used by metadata and data I/O paths to submit and complete work.

## Notable Edge Cases

- Data VIOs are asserted to be single-block.
- Metadata VIOs may span `vio->block_count`.
- If `bio_add_page()` cannot add the requested bytes, returns `VDO_BIO_CREATION_FAILED`.
- Unsupported bio operations assert/log because they should be filtered before this layer.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/bio.h -->
# File Research: sources/block-storage/kvdo/vdo/bio.h

## Purpose

Declares VDO bio helper APIs and small inline wrappers.

## Contents

- Data copy functions.
- Inline conversion/completion helpers:
  - `vdo_get_bio_result()`,
  - `vdo_complete_bio()`.
- Bio allocation/free APIs.
- Bio statistics APIs.
- Async bio completion callback.
- Bio property and buffer reset APIs.

## Dependencies and Role

Wraps Linux block-layer details so VDO code can work in VDO status/geometry terms while still submitting normal kernel bios.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-allocator.c -->
# File Research: sources/block-storage/kvdo/vdo/block-allocator.c

## Purpose

Implements a per-physical-zone block allocator for VDO slabs, including slab prioritization, allocation, load/drain/resume flows, slab scrubbing integration, metadata VIO pool ownership, and allocator statistics.

## Main Responsibilities

- Constructs and frees `struct block_allocator`.
- Registers read-only notification listeners.
- Owns:
  - slab summary zone,
  - priority table of allocatable slabs,
  - slab scrubber,
  - metadata VIO pool,
  - optional kcopyd eraser,
  - dirty slab journal list.
- Queues slabs for allocation or scrubbing.
- Allocates physical blocks from the current open slab.
- Releases unused provisional block references.
- Loads/rebuilds allocator-owned slabs and slab journals.
- Prepares slabs for allocation after load.
- Drains allocator I/O in ordered phases.
- Resumes allocator state in reverse drain order.
- Releases recovery-journal tail block locks held by dirty slab journals.
- Exposes allocator, slab journal, and refcount statistics.

## Key Allocation Behavior

Slabs are prioritized by approximate free block count. Full slabs get priority 0. Never-opened slabs get a reserved lower priority than high-free previously opened slabs, so VDO tends to reuse already-written physical space before opening fresh slabs, which is useful on thin-provisioned backing storage.

`vdo_allocate_block()` first tries the current `open_slab`. If it is exhausted, the slab is reprioritized, the highest-priority slab is dequeued/opened, and allocation is retried. Allocated blocks receive provisional references that must later be confirmed or released.

## Important Functions

- `vdo_make_block_allocator()` allocates the allocator and its components.
- `vdo_free_block_allocator()` tears down eraser, scrubber, VIO pool, priority table, and allocator memory.
- `vdo_register_slab_with_allocator()` records ownership.
- `vdo_queue_slab()` validates free count and routes slabs to scrubber or priority table.
- `vdo_adjust_free_block_count()` updates allocated-block count and reprioritizes non-open slabs.
- `vdo_allocate_block()` allocates from slabs.
- `vdo_release_block_reference()` decrements unused provisional references.
- `vdo_load_block_allocator()` starts per-zone allocator loading.
- `vdo_prepare_block_allocator_to_allocate()` loads/queues/scrubs slabs so allocation can begin.
- `vdo_register_new_slabs_for_allocator()` attaches grown slabs to the allocator.
- `vdo_drain_block_allocator()` starts phased drain.
- `vdo_resume_block_allocator()` starts reverse phased resume.
- `vdo_release_tail_block_locks()` asks dirty slab journals to release recovery-journal locks.
- `vdo_acquire_block_allocator_vio()` and `vdo_return_block_allocator_vio()` wrap the allocator’s VIO pool.
- `vdo_scrub_all_unrecovered_slabs_in_zone()` kicks scrub work.
- `vdo_dump_block_allocator()` logs allocator/slab state.

## Load, Drain, and Resume

Loading uses allocator admin state. For rebuild load, slab journals are erased with `dm_kcopyd_zero()` before finishing load. For recovery load, control passes to recovery journal replay into slab journals. Normal load applies a slab action to all slabs.

Draining runs these phases:
1. Stop slab scrubber.
2. Apply drain action to slabs.
3. Drain slab summary zone.
4. Assert VIO pool idle and finish drain.

Resume runs those phases in reverse:
1. Resume slab summary.
2. Apply resume action to slabs.
3. Resume slab scrubber.
4. Finish resume.

## Dependencies and Interactions

- Uses `admin-state.c` for allocator-local operation state.
- Uses `action-manager.c` as zone action callbacks from slab depot operations.
- Integrates with slabs, slab journals, refcounts, slab summaries, recovery journal, VIO pools, read-only notifier, and `dm-kcopyd`.

## Notable Edge Cases

- Invalid slab free-block counts force read-only mode.
- Unrecovered slabs are registered for scrubbing rather than allocation.
- Dirty slab journals are ordered by recovery-journal lock recency.
- kcopyd client destruction is requeued after callbacks to avoid same-stack deadlock.
- `vdo_release_block_reference()` ignores `VDO_ZERO_BLOCK`.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-allocator.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-allocator.h -->
# File Research: sources/block-storage/kvdo/vdo/block-allocator.h

## Purpose

Declares the per-zone block allocator structure and API.

## Contents

- Defines `VIO_POOL_SIZE = 128`.
- Defines allocator drain-step enum.
- Defines `struct slab_actor` for applying slab actions in parallel.
- Defines `struct block_allocator` with:
  - completion,
  - slab depot/summary,
  - read-only notifier,
  - nonce and zone/thread identity,
  - slab counts,
  - admin state,
  - open slab,
  - priority table,
  - slab scrubber,
  - statistics,
  - dirty slab journal list,
  - VIO pool,
  - kcopyd eraser,
  - slab iterator for erasure.
- Declares creation, allocation, load, drain, resume, grow, VIO pool, scrub, stats, and dump APIs.

## Dependencies and Role

The header exposes allocator internals because closely related slab, depot, and recovery code need direct coordination with allocator-owned state.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-allocator.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-entry.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map-entry.h

## Purpose

Defines the compact five-byte on-disk/in-memory block map entry format and conversion helpers.

## Data Format

A `struct block_map_entry` stores:
- 4 bits of mapping state,
- high 4 bits of a 36-bit physical block number,
- low 32 bits of the physical block number in little-endian order.

This addresses up to 256 TiB at 4 KiB block size while keeping each logical mapping entry at five bytes.

## Important Helpers

- `vdo_unpack_block_map_entry()` returns a `struct data_location`.
- `vdo_is_mapped_location()` checks for non-unmapped state.
- `vdo_is_valid_location()` validates zero-block and mapped-state combinations.
- `vdo_pack_pbn()` packs PBN and mapping state into an entry.

## Notable Details

Bitfield order is conditional on host byte order. Compressed states are invalid for `VDO_ZERO_BLOCK`, while non-zero PBNs must be mapped.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-entry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-format.c -->
# File Research: sources/block-storage/kvdo/vdo/block-map-format.c

## Purpose

Implements encode/decode and size calculations for the persisted VDO block map component state.

## Main Responsibilities

- Defines `VDO_BLOCK_MAP_HEADER_2_0`.
- Decodes block map state version 2.0 from a `struct buffer`.
- Encodes block map state version 2.0 into a `struct buffer`.
- Computes encoded block map component size.
- Computes number of block map leaf pages needed for a logical entry count.
- Computes additional forest pages needed when growing the block map.

## Important Functions

- `vdo_decode_block_map_state_2_0()` validates header, reads flat/root fields, asserts flat-page invariants, and fills state.
- `vdo_get_block_map_encoded_size()` returns encoded header plus state size.
- `vdo_encode_block_map_state_2_0()` writes header and state fields.
- `vdo_compute_block_map_page_count()` rounds logical entries to block map pages.
- `vdo_compute_new_forest_pages()` calculates per-level tree sizes and total new non-leaf pages.

## Behavior Details

The decoded flat-page origin must equal `VDO_BLOCK_MAP_FLAT_PAGE_ORIGIN`, and flat-page count must be zero. The code comments note the flat-page count has effectively always been zero.

Forest growth uses leaf page count, root count, and `VDO_BLOCK_MAP_ENTRIES_PER_PAGE` to compute page counts at each interior level, optionally subtracting old level sizes.

## Dependencies

Uses the generic `buffer` little-endian helpers, VDO headers, constants, and assertion/status helpers.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-format.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-format.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map-format.h

## Purpose

Declares persisted block-map component format structures and sizing helpers.

## Contents

- `struct block_map_state_2_0`
  - flat page origin,
  - flat page count,
  - root origin,
  - root count.
- `struct boundary`
  - level page counts for `VDO_BLOCK_MAP_TREE_HEIGHT`.
- Extern declaration for `VDO_BLOCK_MAP_HEADER_2_0`.
- Decode, encode, encoded-size, page-count, and growth page-count APIs.

## Role

This is the storage-format contract between VDO layout metadata and the runtime block map.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-format.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-page.c -->
# File Research: sources/block-storage/kvdo/vdo/block-map-page.c

## Purpose

Implements formatting and validation for individual block map pages.

## Main Responsibilities

- Defines block map page version 4.1.
- Formats a page buffer with version, nonce, PBN, initialized bit, and zeroed entries.
- Validates page version, initialized status, nonce, and expected PBN.

## Important Functions

- `vdo_format_block_map_page()` clears the block, writes version/header metadata, and returns the page overlay.
- `vdo_validate_block_map_page()` returns:
  - valid,
  - invalid,
  - bad page at wrong disk location.

## Behavior Details

A page with wrong version, uninitialized flag, or wrong nonce is treated as invalid and can be reformatted by callers. A page with matching metadata but unexpected PBN is treated as bad/corrupt.

## Notable Details

The `initialized` bit supports torn-write protection: new pages may need to be written more than once before being considered fully initialized on disk.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-page.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-page.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map-page.h

## Purpose

Defines the block map page layout and validation API.

## Contents

- `struct block_map_page_header`
  - nonce,
  - PBN,
  - unused fields,
  - initialized bit.
- `struct block_map_page`
  - packed version,
  - page header,
  - flexible array of block map entries.
- `enum block_map_page_validity`.
- Inline helpers:
  - check initialized bit,
  - set initialized bit,
  - get page PBN.
- Declarations for page formatting and validation.

## Role

This header defines the per-page storage unit used by both block map leaf pages and interior tree pages.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-page.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-recovery.c -->
# File Research: sources/block-storage/kvdo/vdo/block-map-recovery.c

## Purpose

Replays recovery-journal block mapping entries into the block map after recovery, batching work by block map page.

## Main Responsibilities

- Allocates a recovery completion containing a ring of page completions.
- Sorts/replays numbered journal entries by block map page and slot while preserving journal order for identical slots.
- Fetches block map pages concurrently up to a bounded count.
- Applies all entries for a page to that page.
- Requests page writeback after replay.
- Drains/flushes the block map after replay.
- Handles abort and cleanup.

## Key Structure

`struct block_map_recovery_completion` includes:
- main completion and sub-task completion,
- admin/logical thread IDs,
- target block map,
- abort/launch state,
- journal entry array,
- heap wrapper over entries,
- current entry cursors,
- outstanding page count,
- page completion array.

## Important Functions

- `vdo_make_recovery_completion()` allocates and initializes replay state and heap ordering.
- `compare_mappings()` orders mappings by page PBN, slot, then serial number, reversed for max-heap behavior.
- `find_entry_starting_next_page()` advances through entries until the next page boundary.
- `apply_journal_entries_to_page()` writes journal-provided entries into page slots.
- `fetch_page()` initializes and launches a writable page-cache fetch.
- `recover_ready_pages()` processes ready pages in sorted order, applies mappings, requests writes, releases completions, and launches more fetches.
- `vdo_recover_block_map()` is the public entry point.

## Behavior Details

The replay heap lets recovery iterate entries in sorted page/slot order without a separate full sort call. The serial `number` field preserves original journal order for multiple mappings to the same slot.

After all entries are applied, recovery launches a sub-task on the admin thread to drain the block map under `VDO_ADMIN_STATE_RECOVERING`, ensuring replayed changes are flushed.

## Dependencies and Interactions

- Uses block map page cache through page completions.
- Uses `heap` for sorted replay.
- Uses admin/completion mechanisms to switch between logical and admin threads.
- Uses `vdo_drain_block_map()` to flush changes before parent completion.

## Notable Edge Cases

- Page completions intentionally hold pages locked until recovery releases them.
- If recovery aborts, ready page completions are released before completing parent.
- Page fetch errors set the recovery result and abort further normal replay.
- Empty replay heap completes immediately.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-recovery.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map-recovery.h

## Purpose

Declares the recovery-journal replay representation for block map recovery.

## Contents

- `struct numbered_block_mapping`
  - target block map slot,
  - packed block map entry,
  - serial replay number.
- `vdo_recover_block_map()` public API.

## Role

The serial number lets recovery sort entries by logical location while preserving original order for repeated updates to the same mapping.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-tree.c -->
# File Research: sources/block-storage/kvdo/vdo/block-map-tree.c

## Purpose

Implements the interior tree machinery used to find, load, allocate, dirty, flush, and recover block map pages.

## Main Responsibilities

- Initializes and tears down per-zone block map tree state.
- Maintains dirty lists by recovery-journal era.
- Maintains a metadata VIO pool for interior tree I/O.
- Tracks pages currently being loaded/allocated using an integer-key lock map.
- Loads interior pages from disk and validates them.
- Allocates missing block map tree pages for writes.
- Journals block map page allocations through recovery and slab journals.
- Writes dirty tree pages with generation/flush ordering.
- Handles read-only transition on metadata I/O or invariant failures.
- Provides direct lookup of leaf block map page PBNs after tree pages are loaded.

## Key Concepts

- `struct page_descriptor` is packed into a 64-bit lock key identifying root, height, page index, and slot.
- `loading_pages` maps page keys to the active `tree_lock` so concurrent lookups can wait behind the first loader/allocator.
- Dirty pages have cyclic 8-bit generations. The zone tracks dirty counts per generation to know which pages are covered by flushes.
- `zone->flusher` identifies the page issuing or about to issue a flush.
- `VDO_INVALID_PBN` marks a loaded root-location pseudo page.

## Important Functions

- `vdo_initialize_tree_zone()` creates dirty lists, loading map, and VIO pool.
- `vdo_uninitialize_block_map_tree_zone()` frees tree-zone resources.
- `vdo_copy_valid_page()` validates and copies a disk page into an in-memory tree page.
- `vdo_is_tree_zone_active()` reports active lookups, waiters, or VIO use.
- `vdo_advance_zone_tree_period()` advances dirty-list era periods.
- `vdo_drain_zone_trees()` flushes dirty lists unless suspending.
- `vdo_lookup_block_map_pbn()` walks/loads/allocates the block-map tree to locate a leaf block map page.
- `vdo_find_block_map_page_pbn()` finds a leaf page PBN from already loaded tree pages.
- `vdo_write_tree_page()` schedules an interior page write during read-only rebuild corrections.

## Lookup and Allocation Flow

`vdo_lookup_block_map_pbn()` computes the root and tree slots for a logical page. If an in-memory tree page is present and initialized, it validates the next mapping. If the child page is mapped, it either finishes or loads the next level. If unmapped and the VIO is a write, it allocates missing pages; reads/trims simply finish as unmapped.

Allocation flow:
1. Acquire page lock in `loading_pages`.
2. Allocate a physical data block in the appropriate allocated zone.
3. Add a recovery journal entry.
4. Add a slab journal entry and set max reference count protection.
5. Release allocation lock.
6. Update parent tree page entry.
7. Format newly allocated child page in memory if needed.
8. Wake waiters sharing the page lock.

## Writeback Flow

Dirty-list expiration calls `write_dirty_pages_callback()`, which assigns the current generation and enqueues pages. `write_page()` copies the in-memory page into a VIO buffer, captures generation and recovery lock, clears the in-memory recovery lock, and submits metadata I/O.

On completion, recovery journal block references are released. If the page was dirtied again while writing, it is requeued. If a flush page completes, waiting pages may be written if not dirtied since the flush generation.

## Error Behavior

Metadata I/O errors call `record_metadata_io_error()` and transition the zone to read-only mode. Read-only mode drains flush waiters so the tree zone can close.

## Dependencies and Interactions

- Integrates with `block-map.c` for page updates and drain completion checks.
- Uses `forest` for in-memory tree pages.
- Uses `dirty-lists`, `int-map`, VIO pools, recovery journal, slab journal, and data VIO allocation callbacks.
- Relies on block map page validation/formatting helpers.

## Notable Edge Cases

- Reads waiting behind an allocation failure that is `VDO_NO_SPACE` may complete successfully because the mapping remains unmapped.
- Non-space allocation/load failures force read-only behavior for writers.
- Root pages are not checked as physical data blocks.
- Newly allocated block map pages are protected from deduplication by setting max references before writeout.
- Generation arithmetic is cyclic and guarded by assertions.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-tree.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map-tree.h

## Purpose

Declares block map tree page structures and tree-zone APIs.

## Contents

- `struct tree_page`
  - waiter,
  - dirty-list entry,
  - generation,
  - writing state/generation,
  - recovery lock and writing recovery lock,
  - page buffer.
- Extern `VDO_INVALID_PBN`.
- Inline `vdo_as_block_map_page()`.
- Declarations for:
  - page validation/copy,
  - tree-zone init/uninit,
  - period management,
  - active/drain checks,
  - PBN lookup,
  - page PBN lookup,
  - tree page write scheduling.

## Role

This header exposes interior tree management to the broader block map subsystem.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map.c -->
# File Research: sources/block-storage/kvdo/vdo/block-map.c

## Purpose

Implements the top-level VDO block map: zone setup, page-cache integration, logical-zone mapping, block map entry read/write, drain/resume, era advancement, and growth coordination.

## Main Responsibilities

- Allocates and initializes a multi-zone block map from persisted state.
- Creates per-zone page caches for leaf block map pages.
- Creates an action manager for zone-wide block map operations.
- Maintains block map eras tied to recovery journal sequence numbers.
- Validates and formats leaf pages on read.
- Handles leaf page write completion and recovery journal lock release.
- Computes logical zones for data VIOs.
- Finds leaf block map slots for data VIOs.
- Reads mapped block locations.
- Writes updated mappings and transfers recovery journal locks.
- Drains and resumes block map zones.
- Prepares and applies logical growth through forest replacement.
- Aggregates block map page cache statistics.

## Key Structures

`struct block_map_page_context` tracks the earliest recovery journal sequence number that dirtied a cached leaf page. This lock is acquired/released as entries change and when pages are written.

## Important Functions

- `vdo_decode_block_map()` builds a runtime block map from `block_map_state_2_0`.
- `vdo_free_block_map()` frees zones, forests, action manager, and map memory.
- `vdo_record_block_map()` converts runtime state back to persisted component state.
- `vdo_initialize_block_map_from_journal()` seeds era periods from recovery journal state.
- `vdo_compute_logical_zone()` maps an LBN to root index and logical zone.
- `vdo_find_block_map_slot()` prepares tree lock slot state and starts tree lookup.
- `vdo_advance_block_map_era()` records pending era and schedules default action.
- `vdo_drain_block_map()` schedules a draining operation across all zones.
- `vdo_resume_block_map()` schedules resume across zones.
- `vdo_prepare_to_grow_block_map()` allocates a future larger forest.
- `vdo_grow_block_map()` replaces the forest under suspended operation.
- `vdo_update_block_map_page()` updates a mapping entry and adjusts recovery journal locks.
- `vdo_get_mapped_block()` reads the current mapping.
- `vdo_put_mapped_block()` writes a new mapping.
- `vdo_get_block_map_statistics()` aggregates page-cache stats.

## Behavior Details

Block map eras classify dirty pages by journal sequence age. The current era is not proactively written except under cache pressure; older eras are progressively or immediately written. Era advancement is scheduled as a default action on the block map action manager and applied across page caches and tree zones.

Leaf page reads use `validate_page_on_read()`. Bad pages return `VDO_BAD_PAGE`; invalid pages are reformatted as empty pages.

`set_mapped_location()` validates unpacked entries. Bad mappings fail reads because returning zeros would hide known corruption, but writes treat bad old mappings as unmapped so the write can proceed.

`vdo_update_block_map_page()` packs the new mapping, acquires a lock on the newer recovery journal sequence if needed, releases the older lock, releases the per-entry lock transferred from the data VIO, and clears the VIO’s recovery sequence.

## Dependencies and Interactions

- Uses action manager for multi-zone operation dispatch.
- Uses admin state per block map zone.
- Uses block map tree code for interior lookup/allocation.
- Uses VDO page cache for leaf page caching.
- Uses recovery journal for consistency locks.
- Uses forest growth helpers for logical expansion.

## Notable Edge Cases

- Logical block numbers beyond `entry_count` complete with `VDO_OUT_OF_RANGE`.
- A zero block map page PBN means the mapping page is unallocated and the logical block is unmapped.
- Drain completes only when both tree zone and page cache are inactive.
- Read-only mode changes drain completion result to `VDO_READ_ONLY`.
- Growth to a smaller size is treated as no shrink; next entry count is capped at current count.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map.h -->
# File Research: sources/block-storage/kvdo/vdo/block-map.h

## Purpose

Defines the runtime block map structures and top-level block map API.

## Contents

- `struct block_map_tree_zone`
  - dirty lists,
  - active lookup count,
  - loading page lock map,
  - VIO pool,
  - flusher and flush waiters,
  - generation tracking.
- `struct block_map_zone`
  - zone/thread identity,
  - owning block map,
  - read-only notifier,
  - leaf page cache,
  - tree zone,
  - admin state.
- `struct block_map`
  - action manager,
  - root origin/count,
  - era points,
  - entry count,
  - nonce,
  - recovery journal,
  - current and next forests,
  - zone count and flexible zone array.
- Declares decode, drain, resume, grow, record, initialize, lookup, update, read/write mapping, and stats APIs.

## Role

This header is the central block-map contract for data VIO processing, recovery, layout metadata, and administrative control.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-map.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/block-mapping-state.h -->
# File Research: sources/block-storage/kvdo/vdo/block-mapping-state.h

## Purpose

Defines the four-bit mapping state values stored in each block map entry.

## Contents

- `VDO_MAPPING_STATE_UNMAPPED = 0`.
- `VDO_MAPPING_STATE_UNCOMPRESSED = 1`.
- `VDO_MAPPING_STATE_COMPRESSED_BASE = 2`.
- `VDO_MAPPING_STATE_COMPRESSED_MAX = 15`.
- `VDO_MAX_COMPRESSION_SLOTS`, derived from compressed state range.
- Inline conversion helpers:
  - slot to state,
  - state to slot,
  - compressed-state test.

## Role

This header defines how VDO distinguishes unmapped, normal, and compressed logical mappings inside compact block map entries.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/block-mapping-state.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffer.c -->
# File Research: sources/block-storage/kvdo/vdo/buffer.c

## Purpose

Implements a rolling byte buffer used for marshalling data to and from storage formats.

## Main Responsibilities

- Wraps existing byte arrays or allocates owned buffers.
- Tracks processed content with `start` and `end` indices.
- Compacts consumed data when more write space is needed.
- Supports skip, rewind, clear, end reset, and content comparison.
- Gets/puts raw bytes and typed little-endian integers.
- Copies content between buffers.
- Zero-fills buffer ranges.
- Encodes/decodes booleans.

## Important Functions

- `wrap_buffer()` creates a buffer over caller-provided bytes.
- `make_buffer()` allocates owned data and wraps it.
- `free_buffer()` frees owned data if not wrapped.
- `content_length()`, `available_space()`, `uncompacted_amount()`, `buffer_used()` expose buffer state.
- `ensure_available_space()` compacts if needed.
- `compact_buffer()` moves unread data to offset 0.
- `get_bytes_from_buffer()` and `put_bytes()` are raw copy primitives.
- `get_uint*_le_from_buffer()` and `put_uint*_le_into_buffer()` handle little-endian numeric fields.

## Behavior Details

Consumed data is not physically removed until compaction. This lets callers rewind within already-consumed content when needed.

## Notable Edge Cases

- `clear_buffer()` sets `end` to full buffer length, making the entire buffer content region available for reads; it does not zero memory.
- `wrap_buffer()` asserts `content_length <= length` but proceeds to allocate the wrapper object.
- `copy_bytes()` allocates before consuming bytes and frees on read failure.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffer.h -->
# File Research: sources/block-storage/kvdo/vdo/buffer.h

## Purpose

Declares the rolling buffer structure and marshalling helper API.

## Contents

- `struct buffer`
  - `start`,
  - `end`,
  - `length`,
  - `data`,
  - `wrapped`.
- Construction/destruction APIs.
- Space/content query APIs.
- Position manipulation APIs.
- Byte and buffer copy APIs.
- Boolean and little-endian integer get/put APIs.

## Role

Used by metadata format encoders/decoders such as block map state serialization.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffer.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-reader.c -->
# File Research: sources/block-storage/kvdo/vdo/buffered-reader.c

## Purpose

Implements a sequential buffered reader over a `dm_bufio_client` region.

## Main Responsibilities

- Owns references to an IO factory and dm-bufio client.
- Reads aligned blocks through `dm_bufio_read()`.
- Releases prior buffer when moving to a new block.
- Prefetches up to four blocks ahead.
- Copies arbitrary-length reads across block boundaries.
- Verifies expected byte sequences without consuming on failure.

## Important Functions

- `make_buffered_reader()` allocates a reader, stores block limit, prefetches block 0, and retains the IO factory.
- `free_buffered_reader()` releases active buffer, destroys client, releases factory, and frees reader.
- `position_reader()` positions to a block/offset and reads the block if necessary.
- `read_from_buffered_reader()` copies requested bytes, crossing blocks as needed.
- `verify_buffered_data()` compares expected data and rewinds to starting position on mismatch/error.

## Behavior Details

`reset_reader()` advances to the next block only when no bytes remain in the current buffer. Partial reads that hit out-of-range/EOF after reading some bytes return `UDS_SHORT_READ`.

## Dependencies

Uses Linux device-mapper bufio, `io-factory`, UDS memory/log/status helpers, and `UDS_BLOCK_SIZE`.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-reader.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-reader.h -->
# File Research: sources/block-storage/kvdo/vdo/buffered-reader.h

## Purpose

Declares the opaque buffered reader API.

## Contents

- Forward declarations for `buffered_reader`, `dm_bufio_client`, and `io_factory`.
- Construction/destruction functions.
- `read_from_buffered_reader()`.
- `verify_buffered_data()`.

## Role

Provides sequential region reads without exposing dm-bufio state to callers.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-reader.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-writer.c -->
# File Research: sources/block-storage/kvdo/vdo/buffered-writer.c

## Purpose

Implements a sequential buffered writer over a `dm_bufio_client` region.

## Main Responsibilities

- Owns references to an IO factory and dm-bufio client.
- Allocates writable bufio blocks with `dm_bufio_new()`.
- Appends arbitrary-length data across block boundaries.
- Writes zero bytes efficiently.
- Zero-fills unused tail space before releasing a dirty block.
- Flushes dirty buffers on destruction.
- Records sticky write errors.

## Important Functions

- `make_buffered_writer()` allocates and initializes writer state and retains the IO factory.
- `free_buffered_writer()` flushes current buffer, writes dirty buffers, destroys client/factory references, and frees writer.
- `prepare_next_buffer()` allocates the next block unless block limit is exceeded.
- `flush_previous_buffer()` zero-fills remaining bytes, marks dirty, releases the buffer, and advances block number.
- `write_to_buffered_writer()` appends caller data.
- `write_zeros_to_buffered_writer()` appends zeros.
- `flush_buffered_writer()` flushes current buffer if no sticky error exists.

## Behavior Details

Once an error is stored in `writer->error`, future write/flush attempts return it. Partial block writes are padded with zeros on flush.

## Dependencies

Uses device-mapper bufio, IO factory reference management, and UDS error/logging helpers.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-writer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-writer.h -->
# File Research: sources/block-storage/kvdo/vdo/buffered-writer.h

## Purpose

Declares the opaque buffered writer API.

## Contents

- Forward declarations for `buffered_writer`, `dm_bufio_client`, and `io_factory`.
- Construction/destruction functions.
- Data write, zero write, and explicit flush functions.

## Role

Provides sequential region writes while hiding block padding and dm-bufio lifecycle details.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/buffered-writer.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/chapter-index.c -->
# File Research: sources/block-storage/kvdo/vdo/chapter-index.c

## Purpose

Implements the open and packed chapter index used by UDS/VDO deduplication metadata to map chunk names to record pages within a chapter.

## Main Responsibilities

- Allocates an open chapter index backed by a delta index.
- Clears an open chapter index for a new virtual chapter.
- Adds chunk-name to record-page mappings.
- Packs delta lists into chapter index pages.
- Handles overflow by removing entries/lists when needed.
- Initializes packed chapter index pages.
- Validates packed chapter index pages during rebuild.
- Searches a packed chapter index page for a chunk name.

## Important Functions

- `make_open_chapter_index()` allocates `struct open_chapter_index` and initializes its delta index.
- `free_open_chapter_index()` uninitializes and frees it.
- `empty_open_chapter_index()` resets delta index contents for a new chapter.
- `put_open_chapter_index_record()` hashes a chunk name to delta address/list and inserts a record page number.
- `pack_open_chapter_index_page()` packs a range of delta lists into one page.
- `initialize_chapter_index_page()` initializes a packed delta index page.
- `validate_chapter_index_page()` walks all entries and verifies record page values are plausible.
- `search_chapter_index_page()` looks up a chunk name and returns a record page or `NO_CHAPTER_INDEX_ENTRY`.

## Behavior Details

The open chapter index gives the delta index one extra page because delta lists may rebalance under memory pressure.

`pack_open_chapter_index_page()` may remove entries if a delta list cannot fit, or if the final page must contain all remaining lists. It logs warnings when removals are needed to avoid page overflow.

`put_open_chapter_index_record()` asserts that duplicate collisions for the same chunk do not occur within a chapter.

## Dependencies and Interactions

- Uses `delta-index`, `geometry`, hash helpers, and UDS chunk names.
- Used by deduplication index chapter construction and rebuild/search paths.

## Notable Edge Cases

- Validation returns `UDS_CORRUPT_DATA` without logging an error when a record page field is implausible, because this can happen during rebuild before the whole volume has been written.
- Search converts the chapter-level delta list number to a sub-list number relative to the packed page’s lowest list number.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/chapter-index.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/chapter-index.h -->
# File Research: sources/block-storage/kvdo/vdo/chapter-index.h

## Purpose

Declares chapter index structures and APIs for UDS deduplication metadata.

## Contents

- `NO_CHAPTER_INDEX_ENTRY = -1`.
- `struct open_chapter_index`
  - geometry,
  - delta index,
  - virtual chapter number,
  - volume nonce,
  - memory allocation count.
- APIs to create/free/reset open chapter indexes.
- APIs to insert records, pack pages, initialize/validate packed pages, and search pages.

## Role

This header is the interface between chapter-building code and delta-index-backed chapter index storage.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/chapter-index.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/common.h -->
# File Research: sources/block-storage/kvdo/vdo/common.h

## Purpose

Defines small common UDS/VDO types and size constants.

## Contents

- Includes string utilities, type definitions, and `uds.h`.
- Defines:
  - `KILOBYTE`,
  - `MEGABYTE`,
  - `GIGABYTE`.
- Forward declares `struct uds_chunk_data`.
- Defines `struct uds_chunk_record` containing chunk name and chunk data.

## Role

Provides common definitions shared by UDS-related VDO code.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/compiler.h -->
# File Research: sources/block-storage/kvdo/vdo/compiler.h

## Purpose

Provides compiler convenience macros used by the kvdo source.

## Contents

- Includes Linux compiler and READ/WRITE-once support headers.
- Defines `const_container_of()` for deriving a const parent pointer from a const member pointer.
- Defines `INLINE` as `__attribute__((always_inline)) inline`.
- Defines `__STRING(x)` as a simple stringification macro.

## Notable Details

`INLINE` exists because plain `inline` depends on optimization settings.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/completion.c -->
# File Research: sources/block-storage/kvdo/vdo/completion.c

## Purpose

Implements VDO’s asynchronous completion primitive, including initialization, callback invocation, thread requeueing, error preservation, type assertions, and work-queue enqueueing.

## Main Responsibilities

- Maintains string names for completion types.
- Initializes and resets `struct vdo_completion`.
- Preserves first error result.
- Invokes callbacks immediately or enqueues them on the proper thread.
- Completes parent completions.
- Preserves child errors in parents while continuing processing.
- Asserts completion type.
- Enqueues completions into VDO thread work queues with priority.

## Important Functions

- `vdo_initialize_completion()` zeroes a completion, assigns VDO/type, and resets result state.
- `vdo_reset_completion()` resets result and complete flag.
- `vdo_set_completion_result()` records the first non-success result.
- `vdo_invoke_completion_callback_with_priority()` runs callback immediately if on target thread and not forced to requeue; otherwise enqueues.
- `vdo_continue_completion()` sets result and invokes callback.
- `vdo_complete_completion()` marks complete and invokes callback if set.
- `vdo_finish_completion_parent_callback()` finishes a parent completion.
- `vdo_preserve_completion_error_and_continue()` propagates error to parent, resets child, and continues.
- `vdo_assert_completion_type()` validates type and reports readable names.
- `vdo_enqueue_completion_with_priority()` places completion on the configured VDO work queue.

## Behavior Details

Completion results are sticky: once a non-success result is stored, later results do not mask it.

Thread affinity is enforced by `callback_thread_id`. If a completion is already on the right thread and `requeue` is false, callbacks run directly. Otherwise, completion is queued to the target VDO thread.

## Dependencies and Interactions

- Uses VDO thread configuration and work queues.
- Used throughout kvdo for admin operations, action managers, VIOs, page cache, block map, allocator, recovery, and flush flows.

## Notable Edge Cases

- Invalid target thread IDs trigger assertion and `BUG()`.
- Unknown completion type names are formatted into a static numeric buffer.
- `vdo_complete_completion()` asserts the completion was not already complete.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/completion.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/completion.h -->
# File Research: sources/block-storage/kvdo/vdo/completion.h

## Purpose

Defines VDO’s asynchronous completion object and helper API.

## Contents

- `enum vdo_completion_type` with sorted completion type IDs.
- `typedef vdo_action`.
- `struct vdo_completion`
  - type,
  - complete/requeue flags,
  - callback thread,
  - result,
  - owning VDO,
  - callback and error handler,
  - parent,
  - work queue link,
  - priority,
  - queue pointer,
  - enqueue time.
- Inline callback/run/finish/prepare helpers.
- Declarations for initialization, reset, invoke, continue, complete, preserve error, assert, and enqueue functions.

## Behavior Details

`vdo_run_completion_callback()` routes to `error_handler` when the result is non-success and an error handler exists; otherwise it calls the normal callback.

The prepare helpers reset completions and set callback, error handler, thread, parent, and optional forced requeue.

## Role

This is the core asynchronous control-flow type used across the kvdo module.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/completion.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/compressed-block.c -->
# File Research: sources/block-storage/kvdo/vdo/compressed-block.c

## Purpose

Implements compressed block header initialization, fragment lookup, and fragment insertion.

## Main Responsibilities

- Defines compressed block format version 1.0.
- Initializes a compressed block header and first fragment size.
- Validates and locates a compressed fragment by mapping state.
- Copies a fragment into a compressed block and records its size.

## Important Functions

- `vdo_initialize_compressed_block()` asserts header layout size, writes version, and sets slot 0 size.
- `vdo_get_compressed_block_fragment()` validates compressed state, version, slot number, accumulated offsets, and size bounds.
- `vdo_put_compressed_block_fragment()` records fragment size and copies data into the data area.

## Behavior Details

Fragment offsets are computed by summing sizes of earlier slots. If the computed offset or fragment extent exceeds the compressed block data area, lookup returns `VDO_INVALID_FRAGMENT`.

## Notable Edge Cases

- Non-compressed mapping states are invalid for fragment lookup.
- `vdo_put_compressed_block_fragment()` intentionally performs no bounds checking; callers must ensure the fragment fits.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/compressed-block.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/compressed-block.h -->
# File Research: sources/block-storage/kvdo/vdo/compressed-block.h

## Purpose

Defines the compressed block on-disk overlay and compressed-fragment API.

## Contents

- `struct compressed_block_header`
  - packed version,
  - little-endian fragment sizes for all compression slots.
- `VDO_COMPRESSED_BLOCK_DATA_SIZE`.
- `VDO_MAX_COMPRESSED_FRAGMENT_SIZE`.
- `struct compressed_block`
  - header,
  - data area.
- APIs for fragment lookup, initialization, clearing unused slots, and fragment insertion.

## Role

This header defines how multiple compressed logical fragments are packed into one VDO block.

## Notable Details

A compressed block is only worthwhile if at least two fragments fit, so a fragment that fills the entire data area is considered too large.

<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/compressed-block.h -->