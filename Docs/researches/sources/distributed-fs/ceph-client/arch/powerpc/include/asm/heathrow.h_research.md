# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/heathrow.h

Purpose: Defines register offsets and bit masks for the Apple Heathrow/Paddington I/O controller used on older PowerMac systems.

Important APIs, types, and functions: Constants cover feature control registers, media bay, floppy, SCC, SCSI, IDE, sound, Ethernet, PCI, and power-management bits. No functions or structs are declared.

Control flow: Platform and driver code uses these masks to set/clear controller feature bits during device enable, reset, suspend, and wake handling.

State and persistence: State is held in hardware feature-control registers. This header only names bit positions.

Dependencies and integration points: Integrates with old PowerMac feature drivers, MacIO/PMU paths, and platform power management.

Risks: Many bit names represent board-specific wiring. Incorrect masks can disable clocks, reset devices, or break wake behavior. There is no type safety around raw register access.

Test signals: Boot and suspend/resume on Heathrow/Paddington machines, device enable for IDE/SCSI/SCC/sound/Ethernet, media bay switching, and register readback after feature toggles.
