# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-scmi.h

Purpose: defines Amlogic T7 SCMI firmware clock IDs.

Important APIs/types/functions: IDs cover DDR, audio, top, TCON, USB PLL0/1, MCLK, PCIe, Ethernet, PCIe refclk, EARC, SYS1, HDMI PLL oscillators, system/AXI clocks, fixed PLL and fixed divisors, FCLK 50M, CPU clock, A73 clock, and CPU/A73 div16 clocks.

Control flow: DTS references these IDs under an SCMI clock provider; the Linux SCMI clock driver asks firmware for rates/enables rather than touching MMIO directly.

State and persistence: IDs are firmware and DT ABI. Runtime clock state is owned by SCMI firmware.

Dependencies and integration: standalone T7 SCMI binding used by Amlogic firmware clock provider and device trees.

Risks and test signals: firmware/table mismatch can misreport CPU or bus clocks. Test SCMI enumeration, rate get/set where supported, CPU/A73 clocks, PLL oscillator availability, and firmware error propagation.
