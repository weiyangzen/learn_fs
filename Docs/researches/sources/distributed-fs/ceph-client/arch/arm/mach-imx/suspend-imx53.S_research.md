# sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx53.S

Purpose: i.MX53 OCRAM-resident low-level suspend routine that places DDR into M4IF self-refresh and changes/restores DDR pad drive settings.

Important APIs/types/functions: Defines `imx53_suspend` and `imx53_suspend_sz`; consumes `struct imx5_cpu_suspend_info` layout via hard-coded offsets.

Control flow: The routine saves r4-r7, saves each configured IOMUXC pad value, sets M4IF FDVFS and waits for FDVACK, applies low-power pad clear/set masks, executes WFI, restores pad values, clears FDVFS, waits for DDR self-refresh exit, restores registers, and returns.

State and persistence: State is the OCRAM pm-info block containing M4IF/IOMUXC bases, IO count, offsets, clear/set masks, and saved values. Hardware state includes M4IF MCR0 FDVFS/FDVACK and IOMUXC pad registers.

Dependencies and integration points: Depends on `pm-imx5.c` for OCRAM allocation and struct layout, ARM assembler/linkage, and i.MX53 memory-controller/IOMUXC register semantics.

Risks: Any C struct layout change without offset update breaks suspend. Infinite polling is possible if DDR self-refresh acknowledge never changes. Pad misconfiguration can prevent resume from DDR self-refresh.

Test signals: Suspend-to-RAM on i.MX53 with DDR retention, wake-source tests, and review offset consistency whenever `struct imx5_cpu_suspend_info` changes.
