# sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate-asm.S

Purpose: Provides low-level RISC-V hibernation resume and image-restore assembly.

Important APIs/types/functions: Defines `__hibernate_cpu_resume`, `hibernate_restore_image`, and `hibernate_core_restore_code`.

Control flow: Resume assembly restores saved CPU context, switches to resume page tables, jumps into relocated restore code, and copies saved image pages back to original locations before returning to restored kernel execution.

State and persistence: Consumes `suspend_context`, relocated restore code address, SATP/page-table state, and memory copy lists prepared by `hibernate.c`.

Dependencies and integration points: Tied to hibernation C code, suspend context layout, `asm-offsets`, cache/TLB ordering, and MMU page table setup.

Risks and test signals: Running while overwriting the old kernel image is extremely sensitive to relocation, register preservation, and executable mapping. Test hibernate/resume with KASLR, high memory pressure, multiple CPUs disabled, and post-resume register/state validation.
