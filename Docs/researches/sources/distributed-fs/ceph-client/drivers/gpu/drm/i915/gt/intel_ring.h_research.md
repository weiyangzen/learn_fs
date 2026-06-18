# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.h

## Purpose
`intel_ring.h` declares the i915 ring-buffer allocation, pinning, space accounting, reset, and request command emission helpers used by legacy ringbuffer submission and context-owned rings.

## Important APIs, Types, And Functions
The exported helpers are `intel_engine_create_ring()`, `intel_ring_begin()`, `intel_ring_update_space()`, `intel_ring_pin()`, `intel_ring_unpin()`, `intel_ring_reset()`, and `intel_ring_free()`. Inline helpers manage krefs, validate and wrap ring offsets, advance command emission, compute available space, and set `ring->tail` after asserting hardware tail constraints.

## Control Flow
Request construction reserves dwords with `intel_ring_begin()`, writes commands into `ring->vaddr + ring->emit`, then calls the inline `intel_ring_advance()` as a consistency check. Submission paths eventually call `intel_ring_set_tail()` and program `RING_TAIL`. Wrap and direction calculations keep offsets within power-of-two ring size.

## State, Persistence, And Dependencies
State lives in `struct intel_ring` from `intel_ring_types.h`: VMA, CPU mapping, head/tail/emit, space, size, wrap bit, and pin/ref counts. It depends on GEM assertions, i915 requests, cacheline constants, and the hardware rule that head/tail sharing a cacheline cannot be programmed with head greater than tail.

## Integration Points
Legacy submission, execlists context rings, request retirement, and reset code use these helpers to keep software ring state aligned with hardware registers.

## Risks
Misaligned or out-of-range offsets can hang GPUs. The tail cacheline assertion is subtle because software `ring->head` is only a conservative last-known hardware head. `intel_ring_advance()` is a debug placeholder, so callers must still reserve the right number of dwords.

## Test Signals
Useful signals include ring selftests, wraparound request emission, tail/head cacheline boundary tests, reset-to-tail behavior, and GPU hang reports around invalid `RING_TAIL` updates.
