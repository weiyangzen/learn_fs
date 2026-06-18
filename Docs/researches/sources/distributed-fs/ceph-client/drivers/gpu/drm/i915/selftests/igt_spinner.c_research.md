# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_spinner.c

## Purpose
This file implements a reusable GPU spinner for i915 selftests. A spinner is a tiny batch buffer that writes its request seqno to a status page, then loops on itself until the test patches the batch to end.

## Important APIs, Types, And Functions
- `igt_spinner_init()` allocates the status-page object and batch object.
- `igt_spinner_pin()` pins/maps both objects into a specific context VM, optionally under a ww context.
- `igt_spinner_create_request()` emits the spinner batch and returns an unsignaled request.
- `igt_spinner_end()` overwrites the batch start with `MI_BATCH_BUFFER_END`.
- `igt_spinner_fini()` ends, unpins, unmaps, and releases all objects.
- `igt_wait_for_spinner()` waits until the hardware status page records the request seqno.

## Control Flow
Initialization creates an LLC-coherent HWS object and a batch object. Pinning obtains VMAs and CPU maps, then pins both in the target VM. Request creation validates `store_dword` support, moves VMAs active, writes commands to store seqno and recursively jump to the batch start, flushes, emits optional breadcrumb initialization, and emits BB start. Waiting flushes submission if ready and polls the HWS seqno first in microseconds then jiffies.

## State And Persistence
`struct igt_spinner` owns GEM objects, VMAs, mapped CPU pointers, the target context pointer, and a seqno page. The spinner mutates GPU-visible batch memory; `igt_spinner_end()` changes execution from loop to termination. State is transient but must be finalized to unpin mappings.

## Dependencies And Integration Points
It depends on GEM internal objects, VMA pinning, context request creation, MI command encoding across graphics generations, chipset flush, and wait utilities. Request cancellation and parallel-engine tests use it to occupy engines.

## Risks
Incorrect MI command generation or address mode can hang engines. The helper is context-specific after pinning and warns on reuse with a different context. Failure after request creation must add the errored request to complete cleanup semantics.

## Test Signals
`igt_wait_for_spinner()` returning true signals that the request started on the GPU. Ending and waiting on the request should then complete. `-ENODEV` is expected on engines that cannot store dwords.
