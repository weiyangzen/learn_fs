<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c

## Purpose
`dma-mask.c` supplies the PowerPC architecture hook called when a device DMA mask changes. It lets platform-specific machine descriptors react to mask updates.

## Important APIs, Types, And Functions
The only function is exported `arch_dma_set_mask(struct device *dev, u64 dma_mask)`. It checks `ppc_md.dma_set_mask` and delegates when the platform provides one.

## Control Flow
There is no local policy beyond optional callback dispatch. If the machine descriptor lacks a `dma_set_mask` hook, the function returns without side effects.

## State And Persistence
This file owns no state. Any state mutation occurs inside platform-provided `ppc_md.dma_set_mask`, typically in device or host bridge DMA metadata.

## Dependencies And Integration Points
It integrates with the generic DMA mapping layer, `asm/machdep.h`, and machine descriptor callbacks for pSeries, PowerNV, or embedded platforms.

## Risks
The hook is intentionally thin, so platform bugs are not contained here. Callers should not expect a return status or fallback validation from this function.

## Test Signals
Changing PCI DMA masks should trigger the platform hook when present. Build coverage should verify the exported symbol and no-op behavior on platforms without the callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-mask.c -->
