# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/piix4.h

Purpose: Intel PIIX4 southbridge PCI configuration and power-management register definitions used by MIPS boards such as Malta.

Important APIs/types/functions: Defines function 0 PIRQ route control, SERIRQ control, top-of-memory, deterministic latency, and general configuration bits. Function 1 IDE timing registers include primary/secondary decode enable bits. Function 3 PMBA and PMREGMISC define power-management enable. PM I/O offsets define power-button status and suspend control/type bits. `PIIX4_SUSPEND_MAGIC` supplies the special PCI-cycle data.

Control flow, state, and persistence: No code. State lives in PIIX4 PCI config space and PM I/O registers.

Dependencies and integration: Consumed by Malta southbridge, IRQ routing, IDE, and power-off/suspend code.

Risks and test signals: Register offsets are device-specific; incorrect values can disable IRQ routing or IDE decode. Test PCI config writes, PIRQ routing, SERIRQ, IDE detection, power button status, and suspend/poweroff flows.
