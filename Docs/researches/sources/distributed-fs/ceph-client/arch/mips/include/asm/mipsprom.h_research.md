# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsprom.h

Purpose: Numeric PROM service call identifiers for legacy MIPS firmware interfaces.

Important APIs/types/functions: Defines service numbers such as `PROM_RESET`, `PROM_EXEC`, `PROM_RESTART`, `PROM_REINIT`, `PROM_REBOOT`, `PROM_AUTOBOOT`, `PROM_OPEN`, `PROM_READ`, `PROM_WRITE`, `PROM_IOCTL`, `PROM_CLOSE`, character/string I/O, packet operations, and VME-style read-modify-write operations.

Control flow, state, and persistence: No functions or state. Firmware call wrappers use these constants to dispatch into PROM services; persistent effects are firmware/device dependent.

Dependencies and integration: Integrated with legacy PROM console, boot, device, network, and reset code on systems that still expose this service table.

Risks and test signals: The comments mark several services as unclear; wrong numbers can invoke destructive firmware operations. Test only under matching firmware or emulator by validating benign console and query services before reset/reboot paths.
