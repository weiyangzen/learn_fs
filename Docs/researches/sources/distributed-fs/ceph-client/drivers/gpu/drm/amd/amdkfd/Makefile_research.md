# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Makefile

## Purpose
The AMDKFD Makefile enumerates the KFD object files that are linked into the AMDGPU/KFD build. It centralizes the core module, queue, interrupt, topology, debug, SVM, migration, and per-generation manager objects.

## Important APIs, Types, And Functions
The key build variable is `AMDKFD_FILES`. It includes core objects such as `kfd_module.o`, `kfd_device.o`, `kfd_chardev.o`, `kfd_topology.o`, process/queue/device-queue managers, MQD managers for CIK/VI/v9/v10/v11/v12/v12_1, packet managers, interrupt/event handlers, SMI events, CRAT, and debug. Conditional additions include `kfd_debugfs.o` when `CONFIG_DEBUG_FS` is set and `kfd_svm.o` plus `kfd_migrate.o` when `CONFIG_HSA_AMD_SVM` is set.

## Control Flow
There is no runtime flow. During kernel build evaluation, the parent AMDGPU build uses `AMDKFD_FILES` to decide which KFD translation units become part of the module. Kconfig symbols control optional object inclusion.

## State And Persistence
The Makefile does not hold runtime state. It persists build composition: adding, removing, or reordering objects changes which code is linked and can affect initcall availability, symbol resolution, and feature coverage.

## Dependencies And Integration Points
It depends on `AMDKFD_PATH` being set by the including build system and on Kconfig symbols from `amdkfd/Kconfig`. It integrates all KFD generations with the broader `drivers/gpu/drm/amd` build.

## Risks
Missing an object can cause unresolved symbols or disabled runtime features. Including an object without the right Kconfig guard can break builds on configurations that lack supporting kernel APIs. Because multiple hardware generations are listed together, new generation support must update both source and build lists consistently.

## Test Signals
Build tests should cover baseline KFD, `CONFIG_DEBUG_FS`, `CONFIG_HSA_AMD_SVM`, and combinations across supported architectures. Linker errors, modpost warnings, missing debugfs entries, or absent SVM functionality are strong failure signals.
