# sources/distributed-fs/ceph-client/arch/arm64/mm/ioremap.c

## Purpose
This file implements ARM64 `ioremap` policy around the generic remapper. It rejects physical addresses outside `PHYS_MASK`, refuses to ioremap normal mapped RAM, allows a single architecture hook to adjust or reject the mapping protection, initializes early ioremap support, and declares when `memremap()` may remap RAM.

## Important APIs, Types, and Functions
The main APIs are `arm64_ioremap_prot_hook_register()`, `__ioremap_prot()`, `early_ioremap_init()`, and `arch_memremap_can_ram_remap()`. The file-local state is `static ioremap_prot_hook_t ioremap_prot_hook`, registered once and rejected with `-EBUSY` on duplicate registration.

## Control Flow
`__ioremap_prot()` computes `last_addr = phys_addr + size - 1`, checks the address stays within `PHYS_MASK`, rejects attempts to map RAM using `pfn_is_map_memory()`, calls the optional hook with `(phys_addr, size, &pgprot)` and rejects on non-zero return, then delegates to `generic_ioremap_prot()`. `early_ioremap_init()` simply calls `early_ioremap_setup()` after fixmap setup. `arch_memremap_can_ram_remap()` returns whether the offset PFN is mapped memory.

## State and Persistence
Only the hook pointer persists. It is intended for one-time registration, for example by confidential-computing code that needs to alter page attributes before MMIO mappings are installed.

## Dependencies and Integration Points
The file depends on `pfn_is_map_memory()` from ARM64 init code, generic ioremap APIs, fixmap-backed early ioremap setup, and optional confidential computing or platform code registering an `ioremap_prot_hook_t`.

## Risks
The `last_addr` calculation assumes caller-provided size is sane; overflow behavior matters for boundary checks. Incorrect hook behavior can map MMIO with inappropriate cacheability or sharing attributes. Rejecting RAM ioremap is intentional, but platform code that historically relied on it must use the correct RAM remap path instead.

## Test Signals
Boot and driver probes using MMIO should succeed without warnings. Attempts to ioremap RAM should trigger the `WARN_ONCE()` path. Confidential-computing platforms should test hook registration, hook rejection, and protection rewriting. `memremap()` users can validate RAM remapping through `arch_memremap_can_ram_remap()`.
