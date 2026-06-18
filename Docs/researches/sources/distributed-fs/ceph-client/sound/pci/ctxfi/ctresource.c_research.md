# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.c

## Purpose

This file implements generic bitmap resource allocation and base `struct rsc` lifecycle for ctxfi hardware resources.

## Important APIs, types, and functions

Public functions are `mgr_get_resource()`, `mgr_put_resource()`, `rsc_init()`, `rsc_uninit()`, `rsc_mgr_init()`, and `rsc_mgr_uninit()`. Internal helpers `get_resource()` and `put_resource()` manage contiguous bits. Generic `rsc_ops` expose `master`, `next_conj`, `index`, and `output_slot`.

## Control flow

Resource managers allocate a zeroed bitmap and ask the hardware backend for type-specific manager control blocks. `mgr_get_resource()` searches for contiguous free entries and decrements availability. `rsc_init()` initializes index/type/MSR/hardware pointers and obtains per-resource control blocks for SRC and AMIXER. `rsc_uninit()` returns those control blocks and clears fields. `next_conj()` advances by a rate-dependent audio-slot stride.

## State and persistence behavior

Manager state is the allocation bitmap, total/available counts, type, hardware pointer, and manager control block. Resource state is index, conjugate index, type, master sample-rate mask/count, control block, hardware pointer, and ops. Hardware programming remains in backend callbacks.

## Dependencies and integration points

It depends on `ctresource.h`, `cthardware.h`, Linux allocation, and backend vtables. SRC, SRCIMP, AMIXER, SUM, and DAIO managers build on this layer.

## Risks and test signals

Risks include bitmap bounds errors, lack of double-free detection, global assumptions about `NUM_RSCTYP`, invalid `msr` causing conjugate stride errors, and partial initialization cleanup. Tests should allocate/free contiguous blocks, exhaust resources, validate conjugate output slots by type/MSR, and run leak checks during manager failure injection.
