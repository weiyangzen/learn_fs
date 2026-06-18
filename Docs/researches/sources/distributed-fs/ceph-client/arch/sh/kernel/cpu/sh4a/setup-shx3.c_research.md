# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-shx3.c

Purpose: supplies SH-X3 prototype CPU setup for SCIF, TMU, interrupt controllers, external IRQ/IRL pin modes, and extra memory nodes.

Important APIs, types, and functions: `shx3_devices_setup()` registers early devices as normal platform devices. `plat_early_device_setup()` adds SCIF0-2 and TMU0-1 for early use. `plat_irq_setup()` registers the main descriptor; `plat_irq_setup_pins()` configures GPIO-backed IRQ mode or IRL modes; `plat_mem_setup()` registers URAM/CSM bootmem nodes.

Control flow: static resources define SCIF0-2 with four IRQs each and TMU0-1. Interrupt tables cover TMU, SCIF, DMAC, CSM, H8EX, FE, HUDI, DMAC groups, and inter-CPU interrupt controller lines. `plat_irq_setup_pins()` requests GPIO function pins for IRQ mode before registering `intc_desc_irq`; IRL modes use mask registers and optional descriptors.

State and persistence: static platform data persists in devices. `plat_mem_setup()` registers CPU0 URAM `0x145f0000-0x14610000` and CSM `0x16000000-0x16020000`; additional CPU URAM nodes are present but disabled with `#if 0`. INTC distribution state uses `INT2DISTCR*` registers.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, PFC GPIO function requests, SH-X3 clock setup, SH-X3 SMP support, and SuperH INTC with SMP balancing.

Risks: prototype hardware and disabled CPU1-3 URAM nodes indicate incomplete SMP memory modeling. GPIO requests can fail, leaving IRQ mode unregistered. Early and normal registration use the same device list, requiring stable platform ordering.

Test signals: early console, TMU timekeeping, external IRQ mode GPIO requests, IRL modes, SMP IPI interrupts, `/proc/iomem` extra nodes, and interrupt balancing across CPUs.
