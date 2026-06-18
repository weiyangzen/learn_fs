## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/Makefile

### Purpose
Builds the ARM uprobes implementation when `CONFIG_UPROBES` is enabled by adding `core.o` and `actions-arm.o`.

### Important APIs, Types, And Functions
The only build API is `obj-$(CONFIG_UPROBES) += core.o actions-arm.o`, which binds generic uprobe support to ARM instruction analysis and action handling.

### Control Flow
Kbuild evaluates the config symbol, then compiles and links the two objects into the ARM architecture build. There is no runtime control flow in this file.

### State, Persistence, And Dependencies
State is build metadata only. It depends on Kbuild config selection and on both C files compiling against ARM probe decoding and generic uprobe headers.

### Integration Points
Integrates `arch/arm/probes/uprobes` into the kernel image so generic uprobes can trap, single-step, and emulate ARM user instructions.

### Risks
If the object list drifts from source exports, ARM uprobes may link without required decoders or fail at build time. Config-only coverage means disabled builds hide errors.

### Test Signals
Build ARM kernels with `CONFIG_UPROBES=y`, run uprobe/kprobe selftests on ARM, and verify both object files appear in build logs.
