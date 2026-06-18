## sources/distributed-fs/ceph-client/drivers/accel/ivpu/Kconfig

### Purpose
`Kconfig` declares the Intel NPU/ivpu DRM accelerator driver and its optional debug mode.

### Important APIs, Types, And Functions
`DRM_ACCEL_IVPU` is a tristate depending on `DRM_ACCEL`, `X86_64 && !UML`, `PCI`, and `PCI_MSI`; it selects firmware loading, shmem GEM helpers, generic allocator, and device coredumps. `DRM_ACCEL_IVPU_DEBUG` enables extra debug behavior and unsafe module parameters.

### Control Flow
Kconfig controls whether the `intel_vpu` module is built and whether debug-only code paths are compiled. It also pulls in required subsystems through `select`.

### State, Persistence, And Dependencies
There is no runtime state. Build-time state determines module availability and debug feature exposure. The dependencies tie the driver to x86 PCI/MSI-capable systems.

### Integration Points
It integrates with the kernel DRM accel menu, firmware loader, GEM shmem infrastructure, generic allocator, devcoredump, debug module parameters, and the `drivers/accel/ivpu/Makefile`.

### Risks
Missing dependency selections would produce link/build failures or runtime feature gaps. Enabling debug mode exposes unsafe knobs such as firmware override and hardware fault injection paths.

### Test Signals
Build tests should cover built-in, module, disabled, and debug configurations; runtime tests should verify the module name `intel_vpu` and that firmware/debug/coredump features are present only when configured.
