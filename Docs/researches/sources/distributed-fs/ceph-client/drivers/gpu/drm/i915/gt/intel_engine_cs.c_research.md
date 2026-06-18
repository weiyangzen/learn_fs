<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c

## Purpose
`intel_engine_cs.c` implements i915 engine discovery, setup, common initialization, teardown, idle/reset helpers, diagnostics, hung request discovery, busy-time access, and pinned kernel/bind context creation. It is the central implementation behind the `intel_engine.h` API.

## Important APIs, Types, and Functions
Important public functions include `intel_engine_context_size()`, `intel_engine_set_hwsp_writemask()`, `intel_engines_init_mmio()`, `intel_engine_init_execlists()`, `intel_engine_create_pinned_context()`, `intel_engine_destroy_pinned_context()`, `intel_engines_init()`, `intel_engine_cleanup_common()`, `intel_engine_resume()`, `intel_engine_get_active_head()`, `intel_engine_get_last_batch_head()`, `intel_engine_stop_cs()`, `intel_engine_cancel_stop_cs()`, `intel_engine_wait_for_pending_mi_fw()`, `intel_engine_get_instdone()`, `__intel_engine_flush_submission()`, `intel_engine_is_idle()`, `intel_engines_are_idle()`, `intel_engine_irq_enable()`, `intel_engine_irq_disable()`, `intel_engines_reset_default_submission()`, `intel_engine_can_store_dword()`, `intel_engine_dump_active_requests()`, `intel_engine_dump()`, `intel_engine_get_busy_time()`, `intel_engine_create_virtual()`, `intel_engine_get_hung_entity()`, and `xehp_enable_ccs_engines()`. Major internals include the `intel_engines[]` metadata table, fuse-pruning helpers, `intel_engine_setup()`, `init_status_page()`, `intel_engine_init_tlb_invalidation()`, `engine_setup_common()`, `measure_breadcrumb_dw()`, `engine_init_common()`, and diagnostic dump helpers.

## Control Flow
MMIO initialization starts with the platform engine mask, applies media/compute/GSC/DG2 fuses, assigns logical IDs, allocates each engine, computes reset domains/MMIO bases/GuC IDs/default properties/context size, sanitizes HWSP writes, and records engines in GT arrays. Full engine initialization chooses GuC, execlists, or ring submission setup, runs common setup, calls the backend setup, creates pinned kernel and optional GGTT bind contexts, measures final breadcrumb dword size, and registers the engine for userspace. Cleanup unwinds scheduler, breadcrumbs, retire/cmd parser, default state, pinned contexts, status page, and workaround lists. Idle/reset helpers flush submission tasklets, inspect scheduler queues and ring head/tail/mode, stop the command streamer with `STOP_RING`, wait for forcewake completion, and read instdone registers. Dump paths capture requests, ring buffers, LRC state, registers, HWSP, breadcrumbs, heartbeat, and properties.

## State and Persistence
Persistent engine state includes allocated `intel_engine_cs` objects in `gt->engine[]`, `gt->engine_class[][]`, engine masks/counts, status-page VMA and CPU map, scheduler engine, breadcrumbs, workarounds, TLB invalidation register metadata, pinned kernel/bind contexts, properties/defaults, latency stats, reset domains, and uABI registration. The status page and pinned contexts remain GPU-visible until cleanup.

## Dependencies and Integration Points
The file depends on GEM object/VMA allocation, GGTT pinning, GT/uncore/register helpers, GuC and execlists submission backends, command parser, workarounds, breadcrumbs, PM/retire/heartbeat, reset, MCR reads, scheduler engine, request dumping, and platform fuse registers. It is the integration hub for engine setup at driver load/resume and for error capture/hang recovery.

## Risks and Edge Cases
Engine masks must reflect fused-off hardware before forcewake pruning and engine allocation. TLB invalidation register selection intentionally avoids catch-all future platform matching; unsupported platforms return errors/warnings. Status pages must avoid unsafe high GGTT placement on non-LLC platforms. Cleanup assumes GPU access has stopped. Diagnostics read live hardware snapshots and may race with execution, so they use references/RCU where needed but are best-effort. Pinned context creation relies on perma-pinning and special lockdep classes to be safe inside engine PM barriers.

## Test Signals
High-value tests include engine discovery across platform masks/fuses, GuC/execlists/ring backend selection, status-page allocation and cleanup, command parser init failure unwinds, TLB invalidation on each engine class, heartbeat/breadcrumb measurement, idle checks after submission/reset, stop-ring timeout handling, error-state dumps, virtual engine creation, and selftests included at the bottom of the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c -->
