# sources/distributed-fs/ceph-client/include/linux/kexec_handover.h

## Purpose
Declares Kexec Handover (KHO) helpers for preserving selected memory and device-tree subtrees across a kexec transition.

## Important APIs, Types, And Functions
`struct kho_scratch` records preserved scratch physical address and size, and `struct kho_vmalloc` is an opaque preservation descriptor. With `CONFIG_KEXEC_HANDOVER`, APIs include enable/boot detection, preserve/unpreserve for folios, pages, vmalloc, allocate-preserve/free helpers, restore helpers, subtree add/remove/retrieve, `kho_memory_init()`, and `kho_populate()`.

## Control Flow
Callers preserve memory objects before kexec, optionally attach named blobs/subtrees, and the next kernel detects a KHO boot and restores preserved objects by physical address or descriptor. Disabled builds return `false`, `-EOPNOTSUPP`, `ERR_PTR(-EOPNOTSUPP)`, `NULL`, or no-op stubs.

## State And Persistence
State is intentionally preserved across kexec in physical memory and metadata such as FDT subtree entries and scratch ranges. This differs from normal kernel-only in-memory state because the next kernel can consume it.

## Dependencies And Integration Points
Depends on error pointers, errno, physical address types, folios/pages, vmalloc descriptors, and kexec image fields. Integrates with kexec, boot memory initialization, and subsystems that want warm handover of selected state.

## Risks
Preserved memory must be excluded from normal freeing and from new image overwrite. Restore helpers must validate physical addresses and sizes. Disabled stubs use slightly different unsigned parameter types in declarations versus some prototypes, so callers should match the public signatures carefully.

## Test Signals
Signals include KHO enabled/disabled builds, preserve/restore folio and page ranges, vmalloc preservation, subtree round trips, kexec boot detection, scratch range validation, and memory leak/double-free checks.
