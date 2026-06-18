# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/hardware.h

Purpose: Defines XT2000 board hardware addresses and IRQ assignments.

Important APIs, types, and functions: `SONIC83934_INTNUM`, `SONIC83934_ADDR`, `IRQ_PCI_A/B/C`, and `XT2000_LED_ADDR`.

Control flow: Header-only constants used at compile time by platform setup and drivers.

State and persistence: No runtime state; maps physical board devices into `IOADDR()` virtual address space.

Dependencies and integration: `asm/core.h`, board setup, serial/SONIC devices, PCI interrupt wiring, and LED power/heartbeat code.

Risks: Hard-coded addresses/interrupts must match board memory map; `IOADDR()` assumptions depend on KIO mapping; incorrect IRQs break devices.

Test signals: XT2000 boot, LED writes, SONIC network interrupt, and PCI interrupt routing.
