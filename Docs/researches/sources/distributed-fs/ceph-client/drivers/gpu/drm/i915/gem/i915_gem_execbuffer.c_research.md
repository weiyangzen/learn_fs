# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_execbuffer.c

## Purpose
Implements the GEM execbuffer2 ioctl: validates user GPU submission, resolves handles to VMAs, reserves GPU virtual addresses, applies relocations, optionally command-parses into shadow batches, wires sync fences, builds requests, marks objects active, and queues work to selected engines or parallel engine groups.

## Important APIs, Functions, and Types
`struct eb_vma` wraps each exec object with VMA, flags, relocation/bind list links, and handle lookup data. `struct eb_fence` tracks syncobj/dma-fence inputs and outputs. `struct i915_execbuffer` is the per-ioctl transaction state: device/file/args, object arrays, selected context/GT, request array, relocation cache, VMA lookup table, unbound/reloc lists, fences, batch metadata, and wakerefs.

Important functions include `i915_gem_execbuffer2_ioctl()`, `i915_gem_do_execbuffer()`, `eb_select_context()`, `eb_select_engine()`, `eb_lookup_vmas()`, `eb_validate_vmas()`, `eb_reserve()`, `eb_relocate_parse()`, `eb_relocate_parse_slow()`, `eb_parse()`, `eb_requests_create()`, `eb_move_to_gpu()`, `eb_request_submit()`, `eb_requests_add()`, `add_fence_array()`, and `add_timeline_fence_array()`.

## Control Flow
The ioctl validates buffer count and global flags, copies the exec object array, and initializes an `i915_execbuffer`. The transaction parses extensions and fence arrays, imports input fences, reserves an output fence fd if requested, builds a handle lookup structure, selects context/engine, and takes GT/VM references. VMA lookup resolves handles through the per-context LUT or file object IDR, checks protected-content keys, validates object flags/alignment/pinned offsets, records batch entries, rejects self-modifying batches, and initializes userptr submission.

Under a ww context, it pins engine timelines, locks objects, tries to reuse current VMA placements, reserves dma-resv fence slots, and retries binding with increasingly strong unbind/evict passes. Relocation first uses an atomic no-pagefault path over user relocation arrays; on faults or waits it releases state, prefaults or copies relocations, revalidates, and retries. Relocation writes use CPU kmap or temporary GGTT iomap depending on backing/coherency. The command parser may replace the batch with a read-only shadow object and optional GGTT trampoline.

Requests are created in parent-to-child order and added in reverse order for timeline lock ordering. The first relevant request awaits external fences, VMAs are moved active for all batches, batch-start commands are emitted, requests are queued, syncobjs/out fences are signaled, and all pins/references/fds/fences unwind through labeled cleanup.

## State and Persistence Behavior
Mutates per-context handle-to-VMA LUTs, object `lut_list`, VMA pin/fence/open state, user-visible exec-object offsets, object dirty/cache state during relocation, dma-resv fence reservations, request timelines, syncobj values, command-parser buffer-pool ownership, protected-content validation, and GT runtime PM wakerefs. Internal bits in `args->flags` track transaction state and are stripped from UAPI-visible flags before return.

## Dependencies and Integration Points
Integrates with GEM object lookup/locking, VMA/GGTT/PPGTT binding, eviction, userptr, command parser, GT buffer pool, engine/context/timeline/request code, syncobj/sync_file APIs, PXP protected content, clflush/domain helpers, runtime PM, and execbuffer UAPI structs.

## Risks
This is security- and deadlock-sensitive. Malformed userspace arrays, relocation races, stale VMA LUT entries, command parser bypasses, protected-content misuse, wrong VMA placement, incorrect fence ownership, and ww/timeline/VM lock ordering can cause use-after-free, stale GPU addresses, data corruption, or hangs. Parallel contexts and secure batches have additional constraints.

## Test Signals
IGT execbuffer relocation/no-reloc, fence-array, timeline-syncobj, context-engine, userptr, protected-content, command-parser, and parallel-submit tests are relevant. Debug GEM logs exact `EINVAL` sites, `drm_dbg()` reports validation failures, and request tracepoints show queue/add behavior.
