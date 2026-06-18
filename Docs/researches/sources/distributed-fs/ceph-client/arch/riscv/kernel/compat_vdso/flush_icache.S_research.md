# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/flush_icache.S

Purpose: Builds the compat VDSO `flush_icache` entry by reusing the common RISC-V VDSO implementation in 32-bit mode.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/flush_icache.S`.

Control flow: Runtime behavior is inherited from the common VDSO assembly: user code enters the VDSO symbol and issues the appropriate syscall or helper sequence for instruction-cache synchronization.

State and persistence: No private state; it is part of the mapped compat VDSO image.

Dependencies and integration points: Depends on common VDSO assembly, compat VDSO linking, and user-space cache flush ABI.

Risks and test signals: ABI register width and syscall number handling must match compat expectations. Test with compat JIT/self-modifying code paths that call `__riscv_flush_icache`.
