# sources/distributed-fs/ceph-client/arch/arm64/kernel/hibernate-asm.S

Purpose: Provides the copied-to-safe-page hibernation resume exit routine that restores memory contents and returns through the saved CPU resume path.

Important symbol: `swsusp_arch_suspend_exit` in `.hibernate_exit.text`. It receives temporary page table addresses, the restored kernel's swapper table, `cpu_resume`, the restore page list, optional hyp stub vector address, and a zero page for break-before-make TTBR switching.

Control flow: the routine switches TTBR1 to a temporary copied linear map, iterates `restore_pblist`, copies each saved page back to its original address with the assembly `copy_page` macro, cleans each restored page to PoU, waits for cache maintenance, switches TTBR1 to the restored kernel tables, invalidates instruction cache, optionally HVCs into the restored EL2 stub, and returns to `cpu_resume`.

Dependencies and integration: called from `hibernate.c` after being copied by `create_safe_exec_page()`. It depends on hibernation PBE offsets, break-before-make TTBR macros, cache maintenance alternatives, EL2 stub vectors from `hyp-stub.S`, and the invariant that it cannot call PC-relative external routines while memory is being overwritten.

Risks and test signals: risks include self-overwrite, stale I-cache after restoring text, missing EL2 reinitialization, wrong PBE traversal, and TTBR switch ordering. Test with hibernate/resume under KASLR, nVHE, VHE, 4K/16K/64K pages, modules loaded, and CPU hotplug around suspend.
