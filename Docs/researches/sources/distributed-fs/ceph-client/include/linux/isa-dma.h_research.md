# sources/distributed-fs/ceph-client/include/linux/isa-dma.h

## Purpose
`isa-dma.h` includes architecture ISA DMA definitions and exposes the x86 32-bit PCI/ISA DMA bridge bug indicator.

## Important APIs, types, and functions
It includes `<asm/dma.h>` and defines or declares `isa_dma_bridge_buggy`, depending on `CONFIG_PCI && CONFIG_X86_32`.

## Control flow
ISA DMA users can check `isa_dma_bridge_buggy` to decide whether DMA bridge quirks apply. Other builds compile the value as constant zero.

## State and persistence
The only state is the platform global quirk flag when present.

## Dependencies and integration points
It integrates legacy ISA DMA users with architecture DMA APIs and PCI bridge quirk detection.

## Risks and test signals
Risks include code not compiled on non-x86 due to arch DMA assumptions and missing quirk handling on old PCI/ISA systems. Tests should compile x86_32 PCI and non-x86 configs and exercise ISA DMA transfers on affected bridge hardware.
