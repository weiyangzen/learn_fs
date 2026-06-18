# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.h

## Purpose
This header declares the i915 GPU spinner helper and its owned state.

## Important APIs, Types, And Functions
`struct igt_spinner` stores GT, HWS object, batch object, context, VMAs, batch pointer, and seqno pointer. The API includes init, pin, fini, request creation, end, and wait functions.

## Control Flow
Callers initialize a spinner, create a spinner request for a context and arbitration command, wait for it to start, perform the test scenario, end the spinner, wait/cancel as needed, then finalize.

## State And Persistence
The struct is caller-owned but contains references and pinned mappings that must be released with `igt_spinner_fini()`.

## Dependencies And Integration Points
It includes GEM context, engine, request, and selftest headers. It is shared by request, scheduler, hangcheck, and reset-oriented tests.

## Risks
Improper lifecycle handling leaks pinned VMAs or leaves a looping batch active. The helper assumes the target GT matches the context VM GT.

## Test Signals
Callers use returned request pointers and `igt_wait_for_spinner()` booleans to decide whether the GPU reached the loop.
