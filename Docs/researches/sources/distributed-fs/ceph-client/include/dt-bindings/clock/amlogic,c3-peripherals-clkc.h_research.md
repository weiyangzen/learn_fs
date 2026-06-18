# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-peripherals-clkc.h

Purpose: defines Amlogic C3 peripheral clock controller IDs for system, AXI, media, display, storage, PWM, serial, and accelerator clocks.

Important APIs/types/functions: IDs cover RTC, reset/power/pad/sys controls, TS PLL, arbitration, MMC, CPU/JTAG/IR/IRQ/MSR/ROM/UART/RSA/SARADC/startup/secure/SPIFC/NNA/ETH/GIC/RAM/NIC/audio/PWM/USB/SD/SPICC/I2C/I2S/GE2D/ISP/MIPI/ETH PHY/ACODEC/DWAP/DOS/CVE/VOUT/VC9000E, AXI domains, 12/24M and FCLK clocks, generated clock, SARADC, PWM A-N selectors/dividers/outputs, SPICC, SPIFC, SD/eMMC A/B/C, TS, Ethernet, MIPI DSI, VOUT, codecs, VC9000E, CSI, DEWARPA, ISP, NNA, GE2D, and VAPB.

Control flow: clock consumers in DTS use these IDs; the C3 peripheral provider maps them to gates, muxes, dividers, and rate operations.

State and persistence: constants are DT ABI, while runtime state is clock-framework state.

Dependencies and integration: standalone Amlogic C3 peripheral clock binding.

Risks and test signals: large ID table alignment and media/display clock dependencies are risk areas. Test all DTS references, media/display probe, PWM outputs, Ethernet clocks, and provider count against max ID 200.
