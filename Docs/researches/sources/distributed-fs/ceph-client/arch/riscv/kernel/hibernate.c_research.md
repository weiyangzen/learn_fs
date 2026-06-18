# sources/distributed-fs/ceph-client/arch/riscv/kernel/hibernate.c

Purpose: Implements architecture hibernation save/resume support for RISC-V.

Important APIs/types/functions: Defines hibernation header structures, `pfn_is_nosave()`, `save_processor_state()`, `restore_processor_state()`, `arch_hibernation_header_save()`, `arch_hibernation_header_restore()`, `swsusp_arch_suspend()`, `swsusp_arch_resume()`, temporary page-table mapping helpers, `relocate_restore_code()`, `hibernate_resume_nonboot_cpu_disable()`, and `riscv_hibernate_init()`.

Control flow: Suspend saves invariants and CPU context, records the sleeping CPU, and returns through generic swsusp. Resume validates kernel version, SATP mode, and restore metadata, disables nonboot CPUs, allocates a temporary resume page directory, maps the restore code and saved image ranges, copies restore code to safe executable memory, switches to the resume path, and runs assembly restore code.

State and persistence: Maintains `sleep_cpu`, `resume_pg_dir`, `hibernate_cpu_context`, `relocated_restore_code`, and the architecture hibernation header embedded in the image. It mutates temporary page tables and page permissions.

Dependencies and integration points: Integrates with generic hibernation, memblock nosave ranges, RISC-V page table allocation, suspend assembly, cacheflush/TLB barriers, SMP CPU disable, and kernel version checks.

Risks and test signals: Header validation, page-table permissions, executable restore code, and CPU identity must be exact or resume corrupts memory. Test hibernate/resume across KASLR, SATP modes, SMP, module-loaded kernels, nosave PFNs, and failure cleanup paths.
