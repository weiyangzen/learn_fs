<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h

Purpose: Defines DT clock specifier constants for Freescale/NXP MPC512x SoCs.

Important APIs, types, and functions: Exports `MPC512x_CLK_*` IDs for dummy/reference/system clocks, DIU/VIU, CSB, e300, IPS, FEC, SATA/PATA, NFC, LPC, MBX, USB, PSC, SPDIF, NAND, PCI, SDHC, CAN, OUT clocks, and `MPC512x_CLK_LAST_PUBLIC`. There are no functions or types.

Control flow: No runtime control flow exists. MPC512x clock providers use the IDs to return clock handles for DT consumers.

State and persistence: IDs persist as DT ABI. Runtime state is stored by platform clock code and hardware.

Dependencies and integration points: Used by PowerPC MPC512x DTS files and drivers for Ethernet, storage, display, USB, PSC serial/audio, CAN, PCI, SDHC, and peripheral buses.

Risks and test signals: Risks include public/private boundary drift around `MPC512x_CLK_LAST_PUBLIC`, legacy DTS compatibility breaks, and wrong PSC/SPDIF output mapping. Test with DT compilation, legacy board boot, clk lookup logs, Ethernet, storage, serial, display, PCI, USB, CAN, and audio-related PSC/SPDIF checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mpc512x-clock.h -->
