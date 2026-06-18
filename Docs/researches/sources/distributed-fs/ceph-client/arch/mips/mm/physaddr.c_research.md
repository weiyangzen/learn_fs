<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c

### Purpose
`physaddr.c` wraps virtual-to-physical address conversion with debug validation for MIPS linear and kernel-symbol address ranges.

### Important APIs, Types, And Functions
`__virt_to_phys()` warns on invalid non-linear virtual addresses before calling `__virt_to_phys_nodebug()`. `__phys_addr_symbol()` checks that a symbol address lies between `_text` and `_end` before calling `__pa_symbol_nodebug()`. `__debug_virt_addr_valid()` encodes the accepted virtual ranges and special-cases `MAX_DMA_ADDRESS`.

### Control Flow
At conversion time, `__virt_to_phys()` evaluates the address against page offset, segment class, EVA, and highmem rules. Invalid conversions only warn, preserving legacy callers. Symbol conversion uses `VIRTUAL_BUG_ON()` to enforce that `__pa_symbol()` is only used for kernel image symbols.

### State, Persistence, And Dependencies
There is no retained state. Dependencies include address-space macros, kernel section boundaries, DMA constants, and MM debug helpers.

### Integration Points
The functions are exported and used by MIPS drivers, DMA setup, and core memory helpers that need physical addresses. The warning helps catch misuse of `virt_to_phys()` on vmalloc/highmem addresses.

### Risks
The compatibility exception for `MAX_DMA_ADDRESS` preserves old behavior but can mask weak callers. Range rules differ under EVA and highmem, so tests must cover those configurations. Symbol bounds bugs are fatal through `VIRTUAL_BUG_ON()`.

### Test Signals
Exercise `virt_to_phys()` for KSEG0/linear addresses, `MAX_DMA_ADDRESS`, vmalloc addresses, highmem mappings, EVA builds, and `__pa_symbol()` on valid and invalid kernel-image addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/physaddr.c -->
