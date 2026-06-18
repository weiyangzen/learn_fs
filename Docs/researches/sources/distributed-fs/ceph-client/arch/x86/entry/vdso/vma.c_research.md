## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vma.c

Purpose: kernel-side vDSO/VVAR mapping, fault, remap, and setup logic for x86 processes.

Important APIs/functions/state: `vclocks_used`, `vdso64_enabled`, `init_vdso_image()`, `vdso_fault()`, `vdso_mremap()`, `vvar_vclock_fault()`, `map_vdso()`, `map_vdso_once()`, `arch_setup_additional_pages()`, `compat_arch_setup_additional_pages()`, `arch_syscall_is_vdso_sigreturn()`, and `vdso_setup()`.

Control flow: init patches alternatives in image text. Mapping chooses an unmapped range for VVAR pages plus vDSO text, installs special mappings for `[vdso]`, main VVAR via helper, and `[vvar_vclock]`, then stores `mm->context.vdso` and `vdso_image`. Fault handlers map vDSO image pages or pvclock/hvclock PFNs if those clock modes are in use. Exec setup maps native, x32, or ia32 images depending on task ABI and enable flags.

State/persistence: per-mm `context.vdso` and `context.vdso_image` persist for the process lifetime or mremap. Global enable flags and `vclocks_used` guide mapping/fault behavior.

Integration points: exec, mm special mappings, VVAR/vclock pages, Hyper-V and pvclock, vDSO image symbols, compat vDSO setup, sigreturn detection, and boot parameter `vdso=`.

Risks: mapping order and VVAR offsets are ABI-sensitive; duplicate mapping prevention avoids abuse. Mremap must keep landing pads coherent. Test signals include vDSO mapping selftests, mremap tests, timekeeping with pvclock/hvclock, 32-bit/x32 exec, signal-return recognition, and boot `vdso=0/1`.
