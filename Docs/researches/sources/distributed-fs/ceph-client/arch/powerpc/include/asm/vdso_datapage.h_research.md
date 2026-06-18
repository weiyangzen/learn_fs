<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h

Purpose: Defines PowerPC access to the vDSO datapage for C and assembly users.

Important APIs/types/functions: Includes generic `vdso/datapage.h` for C and defines assembler macro `get_datapage ptr symbol` to compute a position-independent datapage address via link-register relative addressing.

Control flow: Assembly callers branch-and-link to a local label, read LR with `mflr`, then add high/low relocations from the local label to the requested symbol.

State and persistence: No storage is allocated here; it exposes access to the kernel-populated vDSO data page.

Dependencies and integration points: Kernel-only header depending on generic vDSO datapage layout and PowerPC assembler relocation syntax. Integrated by vDSO assembly and syscall veneers.

Risks: The macro is relocation- and instruction-sequence-sensitive. Incorrect symbol math breaks position-independent vDSO access.

Test signals: vDSO assembly build, objdump relocation inspection, and runtime validation of vDSO time/syscall data reads.

Source read size: 29 lines, 586 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso_datapage.h -->
