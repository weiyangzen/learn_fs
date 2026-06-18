<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h

Purpose: Defines SWARM, LittleSur, and CRhone board names and fixed board resources for LEDs, IDE, and PCMCIA on SiByte evaluation systems.

Important APIs/types/functions: `SIBYTE_BOARD_NAME`, feature constants `SIBYTE_HAVE_PCMCIA`, `SIBYTE_HAVE_IDE`, optional `SIBYTE_DEFAULT_CONSOLE`, physical chip-select constants `LEDS_*`, `IDE_*`, `PCMCIA_*`, and GPIO/interrupt mappings `K_GPIO_GB_IDE`, `K_INT_GB_IDE`, `K_GPIO_PC_READY`, `K_INT_PC_READY`.

Control flow: Board setup selects constants through preprocessor configuration and platform code uses them to register resources and route GPIO-backed interrupts.

State and persistence: The header exposes immutable board layout rather than allocating state. The mapped resources represent persistent device placement in the physical address space and GPIO interrupt wiring.

Dependencies and integration points: Includes SiByte core and interrupt headers. Integrated by `arch/mips/sibyte/swarm` platform setup, IDE, PCMCIA, LED, and early console paths.

Risks: Wrong `CONFIG_*` selection changes physical addresses and interrupt lines. Optional IDE/PCMCIA feature flags must match the actual board variant.

Test signals: SWARM-family defconfig builds, resource registration logs, IDE/PCMCIA probe tests, LED access, and console boot with LittleSur default console are relevant.

Source read size: 46 lines, 1140 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h -->
