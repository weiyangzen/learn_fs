<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h

## Purpose
This header exposes the DSB command-buffer API to display commit code while keeping `struct intel_dsb` opaque.

## Important APIs, Types, and Functions
It defines `enum intel_dsb_id` with three engines and `I915_MAX_DSBS`. The declared API covers preparing/finishing/cleaning contexts, size/head queries, register writes, indexed writes, masked writes, NOPs, non-posted sections, interrupts, microsecond/vblank/scanline waits, delayed-vblank waits, vblank evasion, polling, GOSUB, chaining, commit/wait, and IRQ handling.

## Control Flow
There is no implementation flow here, but the API encodes the lifecycle: prepare, emit commands, finish or GOSUB-finish, commit, wait, and cleanup. The IRQ handler declaration connects hardware completion to display interrupt dispatch.

## State and Persistence Behavior
The opaque context carries transient command-buffer state. Callers receive and pass the pointer without knowing buffer layout, which protects the instruction encoding from broad coupling.

## Dependencies and Integration Points
The header depends on `i915_reg_defs.h` for `i915_reg_t` and forward declares display atomic/CRTC types. It is used by plane, watermark, PSR/VRR, and atomic commit code that emits display programming sequences.

## Risks
Callers must honor the lifecycle and must not emit after finish or cleanup. Scanline/wait helpers require matching atomic state and CRTC. Since masked writes are byte-enable based, callers need masks aligned to byte granularity.

## Test Signals
Compile coverage for all DSB users, atomic commit tests with each DSB id, chained/GOSUB command tests, and IRQ dispatch coverage for all pipes and DSB ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h -->
