# sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate.c

Purpose: Implements arm64 architecture hibernation support, including image header invariants, nosave page filtering, temporary executable resume mapping, crashkernel preservation, MTE tag save/restore, and CPU selection for resume.

Important APIs and state: exports `arch_hibernation_header_save()` and `arch_hibernation_header_restore()`. Other entry points include `pfn_is_nosave()`, `swsusp_arch_suspend()`, `swsusp_arch_resume()`, and `hibernate_resume_nonboot_cpu_disable()`. Persistent image state is captured in `resume_hdr`, including `ttbr1_el1`, `reenter_kernel`, `__hyp_stub_vectors`, and `sleep_cpu_mpidr`; live local state includes `sleep_cpu` and optional MTE tag storage in `mte_pages`.

Control flow: suspend checks CPUs can be offlined, enters `__cpu_suspend_enter()`, prepares crash dump memory, saves MTE tags, records the suspend CPU, and calls `swsusp_save()`. On resume return, it cleans restored critical text, restores MTE tags, reprotects crash memory, clears `in_suspend`, exits CPU suspend, and restores mitigations. Resume builds a temporary linear map, allocates a zero page, optionally copies EL2 vectors, copies hibernate exit code to a safe executable page, installs temporary vectors, and jumps to `swsusp_arch_suspend_exit()`.

Dependencies and integration: integrated with generic swsusp, kexec crash resources, KVM/nVHE EL2 handling, trans_pgd temporary page tables, CPU hotplug, MTE, cache maintenance, and UTS version invariants.

Risks and test signals: key risks are resuming a different kernel, wrong CPU MPIDR, missing nosave/crash exclusions, losing MTE allocation failures, KASLR relocation mismatch, and EL2 vector handling. Test with hibernate image validation, crashkernel plus hibernate, MTE tagged memory, KASLR enabled/disabled, CPU hotplug, and nVHE KVM loaded.
