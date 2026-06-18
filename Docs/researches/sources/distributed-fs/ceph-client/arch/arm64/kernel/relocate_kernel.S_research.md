# sources/distributed-fs/ceph-client/arch/arm64/kernel/relocate_kernel.S

Purpose: this assembly routine performs the kexec relocation copy and jumps to the new kernel. It is placed in `.kexec_relocate.text` so `machine_kexec()` can copy it to safe memory before the old kernel image is overwritten.

Important symbols and macros: `arm64_relocate_new_kernel` is the exported routine. `turn_off_mmu` programs `INIT_SCTLR_EL1_MMU_OFF`, runs `pre_disable_mmu_workaround`, writes `sctlr_el1`, and issues an ISB. The routine consumes `struct kimage` offsets such as `KIMAGE_START`, `KIMAGE_HEAD`, `KIMAGE_ARCH_TTBR1`, `KIMAGE_ARCH_ZERO_PAGE`, `KIMAGE_ARCH_DTB_MEM`, `KIMAGE_ARCH_EL2_VECTORS`, and `KIMAGE_ARCH_PHYS_OFFSET`.

Control flow: it first loads every needed `kimage` field before memory may be clobbered. It switches the linear map copy with break-before-make support, walks the kexec indirection list, tracks source, destination, and indirection entries, copies pages, cleans/invalidates destination cache lines to PoC, and loops until `IND_DONE_BIT`. It then drains writes, invalidates I-cache, disables the MMU, and enters the new image either via HVC soft restart when EL2 vectors are provided or directly via `br x28` at EL1.

Dependencies and integration: depends on kexec data structures, page-copy assembler macros, cache maintenance helpers, MMU disable workarounds, virtualization state, and the machine_kexec setup code that supplies safe memory and populated `kimage` fields.

Risks: this code runs while destroying the old kernel memory map; all state must be in registers or safe copied text/data. Cache, TLB, and MMU ordering errors can boot a corrupted new kernel. EL2 versus EL1 entry register conventions must match the receiving image.

Test signals: kexec/kdump boot tests with and without EL2, varied memory layouts, and cache-coherency stress. Failures show as hangs after kexec, bad DTB handoff, or new kernel decompression/entry crashes.
