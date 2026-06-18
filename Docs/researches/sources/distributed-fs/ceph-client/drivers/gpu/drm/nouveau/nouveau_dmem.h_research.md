
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.h

## Purpose
Declares the public interface for Nouveau device-private memory support. It hides the HMM/DMEM implementation behind lifecycle, migration, and address helpers, and compiles to no-op stubs when `CONFIG_DRM_NOUVEAU_SVM` is disabled.

## Important APIs, Types, and Functions
The header forward-declares DRM and Nouveau structures and declares `nouveau_dmem_init()`, `nouveau_dmem_fini()`, `nouveau_dmem_suspend()`, `nouveau_dmem_resume()`, `nouveau_dmem_migrate_vma()`, and `nouveau_dmem_page_addr()`. `nouveau_dmem_migrate_vma()` accepts a `struct nouveau_drm`, `struct nouveau_svmm`, `struct vm_area_struct`, and address range for migration into GPU private memory.

## Control Flow
Consumers call lifecycle hooks from device init, suspend, resume, and fini without needing local `#ifdef` blocks. When SVM is disabled, the init/fini/suspend/resume hooks become empty inline functions; migration/address helpers are not exposed because no caller should perform DMEM migration without SVM.

## State and Persistence
The header owns no state. It defines the contract for the opaque `drm->dmem` pointer managed by `nouveau_dmem.c`.

## Dependencies and Integration Points
The header includes `nvif/os.h` for kernel/NVIF environment definitions and is included by `nouveau_drm.c`, SVM-related code, and the DMEM implementation. It forms the compile-time boundary between optional SVM memory migration support and the always-built DRM lifecycle.

## Risks and Test Signals
The main risk is feature gating: callers must not invoke migration helpers when SVM support is absent. Build coverage should include both `CONFIG_DRM_NOUVEAU_SVM=y/m` and disabled configurations. Runtime signals are that device init/fini and PM paths remain harmless on unsupported configurations and older GPUs.
