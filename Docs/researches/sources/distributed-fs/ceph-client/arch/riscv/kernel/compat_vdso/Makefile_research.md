# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/Makefile

Purpose: Describes how the 32-bit compat VDSO image is assembled, linked, stripped, and converted into kernel objects.

Important APIs/types/functions: Defines compat VDSO object lists, linker script preprocessing, `compat_vdso.so.dbg`, generated `compat_vdso.so`, offset header generation with `gen_compat_vdso_offsets.sh`, and flags such as `-mabi=ilp32`, `-march=rv32g`, no relaxation, no stack protector, and hidden visibility.

Control flow: Kbuild compiles the compat VDSO assembly/C objects, links them with `compat_vdso.lds`, strips debug-only output into a deployable image, embeds the image through `compat_vdso.S`, and generates offsets for kernel mapping code.

State and persistence: Build artifacts persist in the object tree; runtime state is the mapped compat VDSO image in each process.

Dependencies and integration points: Integrates RISC-V VDSO sources, generated offsets, objcopy, linker support for rv32 ABI, and compat signal/syscall code that references VDSO symbols.

Risks and test signals: Toolchain flags are fragile: relaxation, wrong ABI, or wrong link script can make the image unmappable or ABI-incompatible. Test with rv64 kernels enabling compat, VDSO symbol inspection, `gettimeofday`/`getcpu`/`rt_sigreturn` compat tests, and build coverage across GCC/Clang.
