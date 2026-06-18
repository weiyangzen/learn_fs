# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_live_selftests.h

## Purpose
This header is the ordered live selftest registry for the i915 driver. It is included multiple times with different definitions of the `selftest(name, function)` macro to build enums, module parameters, and the runtime dispatch table in `i915_selftest.c`.

## Important APIs, Types, And Functions
It does not define callable functions itself. Its API is the macro list of `selftest()` entries, including live suites for uncore, workarounds, GT engines/timelines/contexts/LRC/MOCS/PM/heartbeat/TLB, requests, migrate, active objects, GEM object/mman/dmabuf/VMA/coherency/GTT/evict/hugepage/context/client/migrate tests, reset, memory regions, hangcheck, execlists, ring submission, perf, SLPC, GuC, and late GT PM.

## Control Flow
Consumers include this file after defining `selftest`. `i915_selftest.c` uses it to generate an enum, a `live_selftests[]` table, and per-test module parameters with line-numbered names. Execution order is exactly the textual order. `sanitycheck` is kept first as a self-check and `late_gt_pm` is kept last.

## State And Persistence
The header itself holds no mutable state. Its entries become mutable `enabled` flags in `live_selftests[]` and module parameters once expanded by `i915_selftest.c`.

## Dependencies And Integration Points
Every listed function must be linked into the i915 selftest build and match the live signature `int (*)(struct drm_i915_private *)`. It is tightly coupled to the selftest runner’s macro-inclusion pattern and module parameter naming.

## Risks
Ordering is behavior: moving entries can alter hardware state expectations. Names must remain unique C identifiers. Adding a function with the wrong signature or missing conditional compilation breaks the generated dispatch table.

## Test Signals
The signal is indirect: `i915_live_selftests()` prints and invokes entries from this registry, respecting module parameters and filters. A missing or misordered entry manifests as absent live coverage or a build/link failure.
