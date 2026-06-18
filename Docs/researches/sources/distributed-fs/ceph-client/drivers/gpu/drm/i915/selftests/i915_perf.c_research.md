# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_perf.c

## Purpose
This file tests the i915 perf/OA stream setup and NOA wait batch behavior. It verifies that a minimal OA metric configuration can be registered, opened as a perf stream, used to execute the NOA wait delay, and that the generated wait sequence preserves user GPR and scratch state.

## Important APIs, Types, And Functions
- `alloc_empty_config()`, `destroy_empty_config()`, and `get_empty_config()` manage a temporary `i915_oa_config` in `perf->metrics_idr`.
- `test_stream()` creates an `i915_perf_stream` using render engine OA properties and calls `i915_oa_stream_init()`.
- `stream_destroy()` tears the stream down under `gt->perf.lock`.
- `live_sanitycheck()` checks stream creation/destruction.
- `write_timestamp()` emits a `PIPE_CONTROL` timestamp write into the engine status page.
- `live_noa_delay()` measures timestamp deltas around `stream->noa_wait`.
- `live_noa_gpr()` poisons context scratch, loads GPR registers with `STACK_MAGIC`, executes the NOA wait batch, stores GPRs back, and verifies no clobbering.
- `i915_perf_live_selftests()` owns registration, execution, and cleanup of the temporary OA config.

## Control Flow
The live entry first skips if perf metrics are unavailable or the GT is wedged. It allocates the empty config, runs `live_sanitycheck`, `live_noa_delay`, and `live_noa_gpr`, then removes the config. The delay test constructs a kernel request, writes timestamps before and after dispatching the secure NOA wait batch, polls status-page slots from the CPU, and checks GPU clock-derived duration against the expected programming delay. The GPR test creates a user context request, initializes 32 GPR dwords, dispatches `noa_wait`, stores all GPR values into the global HWSP, waits for completion, and inspects both GPR storage and scratch-page poison.

## State And Persistence
The file temporarily mutates `perf->metrics_idr`, OA config references, stream state, engine status-page slots, GPR registers during a request, and context scratch memory. It restores by destroying the stream and unregistering the OA config. No persistent metric set survives a normal run.

## Dependencies And Integration Points
It depends on perf/OA internals, render engine lookup, OA format selection by graphics version, request/ring emission, status-page access, `i915_live_subtests()`, `igt_hexdump()`, and secure batch dispatch. It integrates with the live selftest registry through `perf` in `i915_live_selftests.h`.

## Risks
OA stream locking and config reference handling are important; failure paths must release configs and stream allocations. Timing thresholds can be sensitive to hardware clock conversion and polling latency. The GPR test intentionally touches low-level registers and scratch pages, so incorrect addressing can corrupt context state or produce difficult hardware failures.

## Test Signals
Failures include inability to create stream/config, delay outside the accepted threshold, request timeout that wedges the GT, GPR value mismatch, or scratch page poison corruption. Success confirms the OA stream can open and the NOA wait helper behaves as expected.
