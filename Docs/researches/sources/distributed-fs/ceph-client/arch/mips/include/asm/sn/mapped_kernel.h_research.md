<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h

Purpose: Provides address translation helpers for SGI SN mapped kernels, converting replicated/mapped read-only and read-write kernel addresses to physical or K0 addresses.

Important APIs/types/functions: `REP_BASE`, `MAPPED_ADDR_RO_TO_PHYS`, `MAPPED_ADDR_RW_TO_PHYS`, `MAPPED_KERN_RO_PHYSBASE`, `MAPPED_KERN_RW_PHYSBASE`, `MAPPED_KERN_RO_TO_PHYS`, `MAPPED_KERN_RW_TO_PHYS`, `MAPPED_KERN_RO_TO_K0`, and `MAPPED_KERN_RW_TO_K0`.

Control flow: Code subtracts the mapped kernel base and adds per-node kernel-var physical bases where mapped-kernel support is enabled; otherwise it performs direct `REP_BASE` subtraction. Results can be converted to K0 with `PHYS_TO_K0`.

State and persistence: The translation depends on per-node `hub_data(n)->kern_vars` populated from firmware handoff. The header does not store state itself.

Dependencies and integration points: Depends on `linux/mmzone.h`, MIPS address-space macros, hub data, and `klkernvars.h`-style state.

Risks: Incorrect node selection for an address yields wrong physical translation. The 16 MiB RW offset convention is ABI-like and must match linker/PROM layout.

Test signals: Mapped-kernel boot, symbol/address translation checks, module/debug memory access, and non-mapped build coverage are relevant.

Source read size: 55 lines, 1975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h -->
