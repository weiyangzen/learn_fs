# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Kconfig

## Purpose
This `Kconfig` file defines build-time configuration options for the AMD HSA/KFD driver: core HSA support, HMM-based shared virtual memory, and peer-to-peer GPU access.

## Important APIs, Types, And Functions
The configuration symbols are `HSA_AMD`, `HSA_AMD_SVM`, and `HSA_AMD_P2P`. `HSA_AMD` depends on `DRM_AMDGPU` and supported 64-bit architectures, and selects `HMM_MIRROR`, `MMU_NOTIFIER`, and `DRM_AMDGPU_USERPTR`. `HSA_AMD_SVM` depends on `HSA_AMD && DEVICE_PRIVATE`, defaults to `y`, and selects HMM/MMU notifier support. `HSA_AMD_P2P` depends on `HSA_AMD && PCI_P2PDMA`.

## Control Flow
There is no runtime control flow. Kernel configuration resolves these symbols before compilation, which determines which source files and code paths are built and which memory-management features are exposed.

## State And Persistence
The selected symbols persist in the kernel `.config` and influence compiled kernel/module contents. They indirectly control runtime availability of KFD char devices, SVM/HMM migration, and P2P paths.

## Dependencies And Integration Points
This file integrates KFD with DRM AMDGPU, Linux HMM, MMU notifier, DEVICE_PRIVATE memory, PCI P2PDMA, and architecture support. Its symbols are consumed by the AMDKFD Makefile and by `#if IS_ENABLED(CONFIG_HSA_AMD_SVM)` or `CONFIG_HSA_AMD_P2P` guards in KFD sources.

## Risks
Incorrect dependencies can allow unsupported builds or hide valid functionality. SVM depends on kernel memory-management features and module parameters such as `amdgpu.noretry=0` for page-fault mode on many GFXv9 GPUs. P2P help text notes runtime chipset, large BAR, and physical address constraints that are not fully represented by Kconfig dependencies.

## Test Signals
Signals include configuration matrix builds across supported architectures, builds with SVM and P2P both enabled/disabled, HIP managed-memory tests, page-fault/preemption SVM tests, and multi-GPU P2P topology/performance validation.
