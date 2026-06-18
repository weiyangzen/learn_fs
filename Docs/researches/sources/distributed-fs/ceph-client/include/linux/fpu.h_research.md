# sources/distributed-fs/ceph-client/include/linux/fpu.h

## Purpose
This header is the generic gate for architecture FPU support in kernel code.

## APIs, types, and control flow
It deliberately rejects inclusion from a compilation unit that defines `_LINUX_FPU_COMPILATION_UNIT`, emitting an error that floating-point code must be compiled separately. Otherwise it includes `<asm/fpu.h>`, making architecture-specific FPU save/restore or kernel-mode FPU helpers available.

## State and dependencies
No state is defined here. All behavior and state live in architecture-specific `asm/fpu.h` code and the build-system discipline around isolated floating-point compilation units.

## Integration, risks, and tests
Kernel code generally avoids FPU use; consumers must follow `Documentation/core-api/floating-point.rst` and architecture rules. Risks include accidental FPU instructions in normal kernel objects, missing preemption/context handling, and architecture mismatch. Test signals are compile-time enforcement for marked FPU units, architecture build coverage, static checks for unintended floating-point code, and runtime tests around any subsystem that explicitly enters/leaves kernel FPU context.
