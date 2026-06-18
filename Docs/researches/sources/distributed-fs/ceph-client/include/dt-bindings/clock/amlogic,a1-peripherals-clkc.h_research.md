# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-peripherals-clkc.h

Purpose: defines Amlogic A1 peripheral clock controller IDs for DT consumers.

Important APIs/types/functions: IDs cover input roots, system/reset/analog/power/pad/sys controls, temperature sensor, AXI dividers, SPICC, measurement, audio/JTAG/SARADC/PWM/CEC/I2C/IR/ACODEC/OTP/SD/eMMC/USB, DSP, DMA, IRQ, NIC/GIC/UART/PSRAM/RSA/CoreSight, RAM/AXI gates, RTC/CEC 32K clocks, 24M/12M, generated clocks, SARADC/PWM/SPICC/TS/SPIFC/USB/SD/PSRAM/DMC mux/divider clocks, SYS/DSP mux/divider trees, and system PLL div16.

Control flow: DTS clock references map to A1 peripheral clock provider entries; the driver uses IDs to enable gates and configure mux/divider clocks.

State and persistence: IDs are stable DT ABI. Runtime rates/enables are held by the clock framework/provider.

Dependencies and integration: standalone Amlogic A1 clock binding.

Risks and test signals: numerous mux/divider/gate IDs must align with provider arrays. Test provider registration count, DTS reference lookup, clock enable for UART/I2C/PWM/USB/SD, and rate changes for generated clocks.
