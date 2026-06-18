# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,t7-peripherals-clkc.h

Purpose: defines Amlogic T7 peripheral clock IDs for dualdiv RTC/CEC, DSPs, generated clocks, CSI/ISP, GPU, Ethernet, storage, serial, PWM, and system gates.

Important APIs/types/functions: IDs include RTC/CECA/CECB dualdiv trees, smartcard, DSPA/DSPB mux/dividers, 24M/12M/25M, Anakin clocks, TS, MIPI CSI/ISP, Mali, Ethernet RMII/125M, SD/eMMC, SPICC0-5, SARADC, PWM main and AO channels, and system gates for DDR/DOS/MIPI/ETHPHY/MALI/AOCPU/AUCPU/CEC/GDC/DESWARP/NAND/ETH/AXI/SD/eMMC/smartcard/ACODEC/SPIFC/MSR/IR/audio/UART/AIFIFO/PCIE/USB/I2C/HDMITX/HDMIRX/MMC/RSA/APB/DSP/VPU/SAR/GIC/thermal/PWM groups.

Control flow: DTS consumers use IDs to request clocks from the T7 peripheral provider; provider maps IDs to gates, muxes, dividers, and parents.

State and persistence: constants are DT ABI. Runtime state is provider/clock-framework state.

Dependencies and integration: standalone T7 peripheral clock binding.

Risks and test signals: new T7 table is broad and includes AO/main PWM and many system gates; provider ordering and DTS references are key. Test all referenced clocks, PCIe/USB/Ethernet/CSI/ISP/GPU/audio probes, and clock rate changes.
