# sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h` declares ARM EFI runtime mapping,
boot services, and memory map helpers. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `arch_efi_call_virt`,
`ARCH_EFI_IRQ_FLAGS_MASK`, `arm_efi_init`, `MAX_UNCOMP_KERNEL_SIZE`, `EFI_PHYS_ALIGN`; types:
`efi_arm_entry_state`; functions/prototypes: `efi_init`, `arm_efi_init`, `efi_create_mapping`,
`efi_set_mapping_permissions`, `check_and_switch_context`, `efi_virtmap_load`, `efi_virtmap_unload`,
`__cpuc_flush_dcache_area`. The file is 94 lines / 2678 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. MMU and mapping helpers are reached from
memory-management setup, page-table transitions, highmem/fixmap setup, or device mapping code rather
than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `efi_arm_entry_state`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `asm/cacheflush.h`, `asm/cachetype.h`,
`asm/early_ioremap.h`, `asm/fixmap.h`, `asm/highmem.h`, `asm/mach/map.h`, `asm/mmu_context.h`,
`asm/ptrace.h`, `asm/uaccess.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Mapping helpers depend on page-
table, vmalloc, highmem, or memory-type definitions supplied elsewhere under `arch/arm`. Interrupt-
related declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting
code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `efi.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; incorrect address alignment, memory type, or cache alias handling can
corrupt data or make executable mappings incoherent.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run MMU, highmem, ioremap, kexec, and
cache/TLB coherency tests; ensure all include users still build with sparse/objtool-style
diagnostics where available.
