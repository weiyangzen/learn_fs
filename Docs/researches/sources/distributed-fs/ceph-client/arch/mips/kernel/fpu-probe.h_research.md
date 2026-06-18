<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h

### Purpose
`fpu-probe.h` is the local interface for MIPS FPU capability detection. It lets CPU probing code call the same names regardless of whether `CONFIG_MIPS_FP_SUPPORT` is enabled.

### Important APIs, Types, And Functions
With `CONFIG_MIPS_FP_SUPPORT`, it declares `mips_fpu_disabled`, `__cpu_has_fpu()`, `cpu_set_fpu_opts()`, and `cpu_set_nofpu_opts()`. Without FPU support, it defines `mips_fpu_disabled` as `1`, returns `FPIR_IMP_NONE` from a local `cpu_get_fpu_id()` stub, returns false from `__cpu_has_fpu()`, and makes the option setters no-ops.

### Control Flow
There is no runtime control flow beyond inline stubs. The preprocessor selects either the real declarations or the fallback implementation at build time.

### State, Persistence, And Dependencies
The header has no independent mutable state. It depends on `struct cpuinfo_mips`, `FPIR_IMP_NONE`, and `CONFIG_MIPS_FP_SUPPORT`. The stub value for `mips_fpu_disabled` becomes a compile-time constant for builds without FP support.

### Integration Points
The file is included by `fpu-probe.c` and MIPS CPU setup code that needs to probe or disable FPU behavior. It provides a stable local ABI between CPU feature detection and optional FP support.

### Risks
Because the !FP configuration uses stubs, callers must not expect side effects such as `cpuinfo_mips` fields being normalized. Any code added behind this header should preserve the same semantics for both configurations.

### Test Signals
Build coverage matters most: compile MIPS kernels with and without `CONFIG_MIPS_FP_SUPPORT`, then confirm no unresolved references to the real FPU probe functions remain in the no-FP build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h -->
