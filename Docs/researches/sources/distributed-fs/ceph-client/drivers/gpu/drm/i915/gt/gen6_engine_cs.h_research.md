# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.h

## Purpose
Declares gen6/gen7/Haswell engine command-streamer operations used by i915 engine setup.

## APIs And Control Flow
Declares render/XCS/VCS flush functions, breadcrumb emitters, batch-buffer starts, and IRQ helpers: `gen6_emit_flush_rcs/xcs/vcs()`, `gen7_emit_flush_rcs()`, `gen6/gen7_emit_breadcrumb_*()`, `gen6_emit_bb_start()`, `hsw_emit_bb_start()`, and IRQ enable/disable functions. It has no executable flow.

## State, Dependencies, Integration, Risks, And Tests
It stores no state and depends on integer types, `intel_gpu_commands.h`, and forward declarations. Engine initialization includes it to bind gen6/gen7 ops. Risks are hardware-generation misbinding and prototype drift. Build coverage and engine submission/flush/interrupt tests validate it.
