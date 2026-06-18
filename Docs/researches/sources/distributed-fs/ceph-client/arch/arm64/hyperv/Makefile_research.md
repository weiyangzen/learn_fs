## sources/distributed-fs/ceph-client/arch/arm64/hyperv/Makefile

### Purpose
Builds the ARM64 Hyper-V architecture support objects.

### Important APIs, Types, And Functions
The only build rule is `obj-y := hv_core.o mshyperv.o`, making both objects built into the ARM64 kernel when this directory is selected by the parent build.

### Control Flow
There is no runtime control flow. At build time, Kbuild includes `hv_core.c` and `mshyperv.c` in the built-in object list.

### State, Persistence, And Dependencies
No runtime state. The dependency is Kbuild's object aggregation and the parent ARM64 Hyper-V configuration.

### Integration Points
Connects low-level SMCCC hypercall helpers and Hyper-V initialization to the ARM64 kernel image.

### Risks
The file is small but build-critical: omitting either object breaks exported Hyper-V helpers or initialization, while changing `obj-y` to conditional rules could alter built-in behavior.

### Test Signals
Cross-build ARM64 with `CONFIG_HYPERV`, confirm both objects are linked, boot under Hyper-V, and verify exported symbols from `hv_core.o` are available to dependent drivers.
