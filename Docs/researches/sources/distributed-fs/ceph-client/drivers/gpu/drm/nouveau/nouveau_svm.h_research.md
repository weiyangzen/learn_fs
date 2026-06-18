# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.h

## Purpose
This header defines the public SVM/SVMM interface and the `struct nouveau_svmm` state shared between Nouveau client VMM code, channel setup, migration, and SVM fault handling.

## Important APIs, Types, and Functions
`struct nouveau_svmm` contains an mmu notifier, active Nouveau VMM pointer, unmanaged address interval, and mutex. The header declares SVM driver lifecycle hooks, per-client SVMM init/fini, channel join/part, SVM bind/migration ioctl handling, GPU invalidation, and PFN-map allocation/free/map helpers. Disabled builds provide no-op or `-ENOSYS` stubs.

## Control Flow
The header has no executable flow. Its conditional compilation gate means callers can unconditionally call SVM hooks while feature availability is decided by `CONFIG_DRM_NOUVEAU_SVM`.

## State and Persistence Behavior
The declared state ties a process mm to a managed GPU VMM and tracks an unmanaged range that is excluded or partially clipped during invalidation and faults.

## Dependencies and Integration Points
It depends on NVIF OS types, Linux mmu notifier APIs, DRM device/file types, and Nouveau VMM/client code. It is included by `nouveau_svm.c`, `nouveau_vmm.c`, channel code, and migration helpers.

## Risks
Stub behavior must match caller expectations. The header forward-declares `struct mm_struct` only indirectly through included headers for `nouveau_pfns_map`, so include ordering matters.

## Test Signals
Build both with and without `CONFIG_DRM_NOUVEAU_SVM`; exercise ioctl paths, channel creation, VMM teardown, and migration helpers to catch signature or stub mismatches.
