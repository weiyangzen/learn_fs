# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/note.S

Purpose: Emits the compat VDSO ELF note section by reusing the common RISC-V VDSO note source.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/note.S`.

Control flow: This is build-time data emission only. Runtime consumers inspect ELF notes for metadata such as Linux/VDSO identity.

State and persistence: The note section persists inside the compat VDSO ELF image.

Dependencies and integration points: Depends on common VDSO note definitions and ELF tooling.

Risks and test signals: Incorrect notes can confuse debuggers, loaders, or diagnostics. Test with `readelf -n` on the compat VDSO image and mapped process VDSO.
