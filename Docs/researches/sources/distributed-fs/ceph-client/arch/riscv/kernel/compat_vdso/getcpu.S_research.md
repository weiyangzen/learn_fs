# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/getcpu.S

Purpose: Provides the compat VDSO `getcpu` entry by compiling the common RISC-V VDSO implementation for the 32-bit ABI.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/getcpu.S`.

Control flow: Runtime control flow is inherited from the common VDSO implementation and returns CPU/NUMA information according to the compat calling convention.

State and persistence: Uses VDSO/VVAR data mapped into the process; this wrapper has no independent mutable state.

Dependencies and integration points: Depends on common VDSO `getcpu`, compat VDSO layout, and generic scheduler/VVAR data provisioning.

Risks and test signals: Register size, pointer width, and VVAR layout must be compat-correct. Test with 32-bit `getcpu()` loops under migration and CPU hotplug.
