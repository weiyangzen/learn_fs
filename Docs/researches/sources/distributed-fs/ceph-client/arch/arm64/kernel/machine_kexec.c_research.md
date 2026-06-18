# sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec.c

Purpose: Implements arm64 machine-level kexec and crash-kexec preparation, relocation mapping, CPU shutdown, and hibernation crashkernel interaction.

Important APIs and state: functions include `machine_kexec_prepare()`, `machine_kexec_post_load()`, `machine_kexec()`, `machine_crash_shutdown()`, `crash_prepare_suspend()`, `crash_post_resume()`, `crash_is_nosave()`, and `crash_free_reserved_phys_range()`. The code fills `kimage->arch` fields such as `ttbr0`, `ttbr1`, `t0sz`, `kern_reloc`, `el2_vectors`, `zero_page`, and `phys_offset`.

Control flow: post-load flushes in-place images or builds temporary page tables, copies nVHE EL2 vectors, copies relocation code, idmaps it, records physical offset, and flushes caches. `machine_kexec()` masks interrupts, asserts CPU state, then either uses identity-mapped `cpu_soft_restart()` for in-place images or installs temporary vectors/TTBR0 and jumps to relocation code.

Dependencies and integration: integrates with generic kexec, crash dump, SMP CPU stop, trans_pgd, idmap/TTBR helpers, nVHE hyp stub, hibernation nosave filtering, and cache maintenance.

Risks and test signals: risks include executing stale relocation code, kexec with online/stuck CPUs, wrong EL2 vectors, crash kernel stale CPUs, and hibernation preserving crash memory incorrectly. Test normal kexec, kexec_file, crash kdump, CPU hotplug, nVHE KVM, hibernate plus crashkernel, and in-place `IND_DONE` path.
