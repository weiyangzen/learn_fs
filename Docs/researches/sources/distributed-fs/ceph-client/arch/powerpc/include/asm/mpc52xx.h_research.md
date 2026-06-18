# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx.h

Purpose: provides Freescale MPC5200/MPC52xx SoC constants, register maps, platform setup APIs, interrupt/timer helpers, PCI setup, and suspend hooks.

Important APIs/types/functions: defines SVR values for MPC5200 and MPC5200B; maps memory controller, SDRAM, SDMA, GPT, GPIO, wakeup GPIO, XLB, CDM, and interrupt controller registers. APIs include common device mapping/declaration, XLB arbiter setup, PSC AC97 GPIO reset, PSC clock divider setup, restart, GPT lookup/start/period/stop, IRQ init/get, optional PCI bridge setup, and PM hooks through `struct mpc52xx_suspend`.

Control flow: platform boot maps common devices, configures bus arbitration/clocks/GPIO, initializes IRQ controller and optional PCI, and later drivers use GPT and PSC helpers. PM code calls board-specific suspend prepare/resume finish callbacks.

State and persistence: SoC register values persist in MMIO hardware. GPT private objects, suspend callback table, and saved SRAM buffer persist in platform implementation.

Dependencies and integration points: depends on `mpc5xxx.h`, suspend definitions, device tree nodes, PCI, IRQ, timer, and platform device registration.

Risks: register structs are hardware ABI; padding and widths must be exact. PCI and PM hooks compile conditionally. Clock divider or GPIO misconfiguration can break serial/audio/AC97 devices.

Test signals: boot MPC5200 and MPC5200B boards, verify OF platform devices, GPT timers, IRQ routing, PCI bridge setup, PSC clocking, restart path, and suspend/resume where supported.
