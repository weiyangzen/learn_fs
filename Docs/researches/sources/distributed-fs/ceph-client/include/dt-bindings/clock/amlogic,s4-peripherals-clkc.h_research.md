# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-peripherals-clkc.h

Purpose: defines Amlogic S4 peripheral clock controller IDs for RTC/CEC, system clocks, video/display, GPU/video decoders, storage, serial, PWM, security, audio, Ethernet, USB, and measurement clocks.

Important APIs/types/functions: IDs cover RTC and CEC 32K trees, sys clock A/B mux/dividers, smartcard, 12/24M, video PLL/VCLK trees, ENCI/ENCP/VDAC/HDMI, TS, Mali, VDEC/HEVC, VPU/VAPB/GE2D, VDIN, SD/eMMC, SPICC, PWM A-J, SARADC, generated clock, DDR/DOS/ETHPHY/MALI/AOCPU/AUCPU/CEC/NAND/smartcard/ACODEC/SPIFC/MSR/IR/audio/ETH/UART/I2C/HDMITX/HDCP22/MMC/RSA/GIC/demod/CDAC/ADC extclk and related selectors/dividers.

Control flow: DTS clock cells select S4 provider clocks for peripheral probe and media/display configuration.

State and persistence: constants are DT ABI.

Dependencies and integration: standalone Amlogic S4 peripheral binding.

Risks and test signals: media/display clock chains have many intermediate IDs, so provider ordering must match. Test HDMI/display modes, video decode, PWM, SD/eMMC, audio, Ethernet, HDCP22 clocks, and all DTS lookups.
