# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.S

Purpose: Embeds the built compat VDSO shared object bytes into the kernel image.

Important APIs/types/functions: Defines linker-visible symbols around the included `compat_vdso.so` binary blob, normally consumed by VDSO mapping code.

Control flow: There is no runtime branching in this wrapper. The assembler emits a section containing the binary image; later kernel code maps those bytes into compat user processes.

State and persistence: The VDSO image is persistent read-only kernel data after boot and is mapped into user address spaces on demand.

Dependencies and integration points: Depends on the compat VDSO Makefile producing the binary, linker script symbols, and RISC-V VDSO loader code.

Risks and test signals: A missing or stale embedded blob breaks compat VDSO mappings. Test by checking exported blob symbols, VDSO ELF headers in compat processes, and fallback behavior when user code calls VDSO helpers.
