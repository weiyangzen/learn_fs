# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/compat_vdso.lds.S

Purpose: Provides the compat VDSO linker script by selecting the 32-bit VDSO symbol namespace and reusing the common RISC-V VDSO linker layout.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes the generic `vdso/vdso.lds.S`.

Control flow: The linker script controls ELF sections, dynamic symbols, versioning, and exported VDSO entry placement at build time; there is no runtime control flow.

State and persistence: Produces immutable layout metadata and sections inside `compat_vdso.so`.

Dependencies and integration points: Depends on common RISC-V VDSO linker script logic and the compat VDSO build.

Risks and test signals: Layout mistakes affect symbol versioning and user ABI. Test with `readelf` on `compat_vdso.so.dbg`, symbol version checks, and compat VDSO runtime calls.
