# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/isa-dma.h

Purpose: RiscPC ISA DMA channel definitions.

Important APIs/types/functions: defines DMA channel identifiers and platform-specific ISA DMA constraints used by `dma.c` and legacy drivers.

Control flow: no executable flow.

State and persistence: no state; constants describe available DMA resources.

Dependencies and integration points: required because `ARCH_RPC` selects `ISA_DMA_API`; integrates IOMD and virtual floppy/sound DMA channels with generic ISA DMA users.

Risks: channel numbering mismatch breaks driver DMA requests.

Test signals: ISA DMA registration logs and drivers requesting floppy, podule, or sound DMA channels.
