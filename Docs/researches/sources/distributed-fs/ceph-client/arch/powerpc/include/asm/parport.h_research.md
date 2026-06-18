<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h

## Purpose
This small header adapts generic parallel-port probing to PowerPC Open Firmware interrupt mapping.

## Important APIs, Types, And Functions
It includes `linux/of_irq.h` under `__KERNEL__`; the header otherwise acts as the architecture-specific parport include point expected by generic parport code.

## Control Flow
No runtime functions are defined here. Consumer code can use OF IRQ helpers made visible through this architecture header while probing parallel ports.

## State And Persistence Behavior
No state is stored. Device-tree interrupt mappings persist in OF data structures managed elsewhere.

## Dependencies And Integration Points
It integrates with generic parport drivers and PowerPC device-tree interrupt parsing.

## Risks And Edge Cases
The header is intentionally minimal. Removing the include can break platforms whose parport probing expects OF IRQ declarations via the arch header.

## Test Signals
Build PowerPC configs with parallel-port support, probe device-tree-described parport devices, and validate IRQ assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h -->
