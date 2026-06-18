# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hydra.h

Purpose: Defines register offsets and bit masks for the Apple Hydra Mac I/O controller used by legacy PowerPC systems.

Important APIs, types, and functions: Constants describe feature-control, interrupt, DMA, SCC, SCSI, Ethernet, and power-management bits. The header does not expose functions.

Control flow: Platform feature code uses these constants to toggle clocks/resets, route interrupts, and enable controller subdevices.

State and persistence: State is held in Hydra hardware registers only.

Dependencies and integration points: Integrates with old PowerMac platform, MacIO-style device setup, and low-level feature control code.

Risks: The definitions are board-specific and lack type checking. Wrong masks can disable essential devices or misroute interrupts on old machines.

Test signals: Boot on Hydra-based hardware/emulators, SCC/SCSI/Ethernet initialization, interrupt routing, suspend/resume register restore, and device reset sequencing.
