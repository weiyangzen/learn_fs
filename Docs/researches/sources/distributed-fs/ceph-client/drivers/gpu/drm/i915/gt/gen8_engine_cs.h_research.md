<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h

## Purpose
`gen8_engine_cs.h` declares the Gen8+ command emission API and provides small inline helpers for building PIPE_CONTROL, PIPE_CONTROL post-sync writes, and MI_FLUSH_DW GGTT writes.

## Important APIs, Types, and Functions
The header exposes generation-specific flush, batch start, init breadcrumb, final breadcrumb, and AUX table invalidation functions used by engine backends. Inline helpers include `__gen8_emit_pipe_control()`, `gen8_emit_pipe_control()`, `gen12_emit_pipe_control()`, `__gen8_emit_write_rcs()`, `gen8_emit_ggtt_write_rcs()`, `gen12_emit_ggtt_write_rcs()`, `__gen8_emit_flush_dw()`, and `gen8_emit_ggtt_write()`.

## Control Flow
Inline helpers advance a caller-provided dword pointer while writing fixed command packet layouts. PIPE_CONTROL helpers clear six dwords, set opcode and flag groups, and write the post-sync offset. RCS GGTT write helpers emit a qword PIPE_CONTROL write with global GTT selection. XCS GGTT write uses MI_FLUSH_DW with `MI_FLUSH_DW_USE_GTT` and stored-dword operation.

## State and Persistence
There is no owned state. The helpers persist GPU command state only by writing into the caller's ring or batch buffer. `GEM_BUG_ON()` guards enforce qword alignment and the MI_FLUSH_DW bit-5 workaround for GGTT addresses.

## Dependencies and Integration Points
The header depends on `intel_gpu_commands.h`, `intel_gt_regs.h`, and GEM debug assertions. It is included by Gen8+ engine emission code and by paths that need to assemble breadcrumb or flush packets without duplicating packet layout details.

## Risks and Edge Cases
Because these helpers encode hardware packet formats, any off-by-one in packet length, flag grouping, or address alignment can corrupt the ring stream. The Gen12 PIPE_CONTROL helper accepts two flag groups, so callers must keep generation-specific flags in the correct dword.

## Test Signals
Compile-time users catch signature drift. Runtime signals include ring parser validation, breadcrumb completion, cache flush correctness, and debug assertions on misaligned HWSP/GGTT addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h -->
