
# sources/distributed-fs/ceph-client/lib/test_kho.c

## Purpose

This module tests KHO, kexec handover, by preserving randomly generated folio data plus metadata in an FDT subtree and verifying it after a handover-enabled boot.

## Important APIs, Types, And Functions

`struct kho_test_state` tracks allocated folios, physical metadata for those folios, preserved vmalloc metadata, count of preserved folios, the FDT folio, and checksum. The save path uses `kho_preserve_folio()`, `kho_preserve_vmalloc()`, `fdt_*()` builders, and `kho_add_subtree()`. The restore path uses `kho_retrieve_subtree()`, `kho_restore_vmalloc()`, `kho_restore_folio()`, and checksum recomputation.

## Control Flow And State

On init, the module exits quietly if KHO is disabled. If the `kho_test` subtree is present, it validates compatibility, magic, metadata shape, and checksum, then reports restore success or failure. If the subtree is absent, it allocates random folios up to `max_mem`, computes a checksum, preserves metadata and folios, builds an FDT subtree containing `nr_folios`, `folios_info`, and `csum`, and registers that subtree for handover. Exit removes the subtree and unpreserves/frees all state.

## State And Persistence

This file explicitly tests persistence across kexec handover. Folio physical addresses and orders are stored as `phys | order`; vmalloc metadata is preserved through `struct kho_vmalloc`; data integrity is represented by `csum_partial()`.

## Dependencies And Integration Points

It depends on KHO APIs, libfdt, kexec handover ABI, folio allocation, vmalloc, random bytes, and checksum helpers. The `max_mem` module parameter bounds test memory consumption.

## Risks And Test Signals

Risks include excessive allocation from `max_mem`, cleanup paths that unpreserve or free partially initialized state, and FDT property layout drift. Signals are `KHO restore succeeded`, `KHO restore failed`, checksum mismatch errors, and successful save registration when no subtree exists.
