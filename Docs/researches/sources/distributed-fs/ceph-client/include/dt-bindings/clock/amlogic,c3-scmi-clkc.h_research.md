# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-scmi-clkc.h

Purpose: defines Amlogic C3 SCMI clock IDs exposed through firmware.

Important APIs/types/functions: IDs cover DDR PLL/PHY, top/USB/MCLK/Ethernet/fixed/GP1 PLL oscillators, MIPIISP/VOUT, USB control, oscillator, system/AXI/CPU clocks, SYS PLL div16, and CPU div16.

Control flow: DTS consumers reference SCMI clock IDs; the SCMI clock protocol provider resolves them through firmware instead of direct MMIO clock control.

State and persistence: IDs are firmware/DT ABI. Runtime state is controlled by SCMI firmware.

Dependencies and integration: standalone C3 SCMI clock binding, integrated with SCMI clock drivers and Amlogic firmware.

Risks and test signals: firmware ID mismatch leads to unavailable or wrong clocks. Test SCMI discovery, DTS references, CPU/AXI/sys rate reporting, and firmware error handling.
