# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Kconfig

## Purpose
Defines configuration switches for AMDGPU Display Core and related display-engine options.

## Important APIs, Types, And Functions
`DRM_AMD_DC` enables the newer AMD display engine, defaults to yes, depends on DRM/AMDGPU and architecture/compiler constraints, and selects CEC, CEC notifier, optional HDA component support, and `DRM_AMD_DC_FP` when kernel FPU support is safe. `DRM_AMD_DC_FP` is an internal floating-point support symbol for DCN SoCs. `DRM_AMD_DC_SI` enables DC support for Southern Islands ASICs. `DEBUG_KERNEL_DC` enables kgdb break behavior in DC asserts. `DRM_AMD_SECURE_DISPLAY` enables secure display CRC/debugfs support when DC floating point and debugfs are available.

## Control Flow
Kconfig evaluates these symbols during kernel configuration. The selected values control which display Makefiles compile objects and which preprocessor paths are active.

## State And Persistence
Configuration state is stored in the kernel `.config`; there is no runtime state in this file.

## Dependencies And Integration Points
Integrates with DRM, AMDGPU, architecture FPU support, compiler constraints, CEC, sound HDA, KGDB, DEBUG_FS, and downstream display Kbuild files. The Clang architecture constraint protects against excessive stack use in bandwidth calculations.

## Risks
Dependency mistakes can expose unsupported DC builds or hide supported ones. The `DRM_AMD_DC_FP` selection is architecture and compiler sensitive; getting it wrong can create unsafe kernel FPU use or build/runtime failures. Secure display depends on debugfs and specific firmware behavior.

## Test Signals
Run config matrix builds across x86_64, ARM64, RISC-V, LoongArch, SPARC64, and Clang/GCC combinations; verify object inclusion for DC, DCN FP, SI, debug, and secure display options.
