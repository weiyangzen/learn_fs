<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h

Purpose: Provides DT clock IDs for Mobileye EyeQ6L Plus clock domains.

Important APIs, types, and functions: Defines `EQ6LPC_PLL_*` roots, CPU, accelerator, DDR, peripheral, and VDI output clocks such as OSPI, I2C, UART, SPI, and PERIPH. No callable functions or data structures are included.

Control flow: No execution occurs. The EyeQ6L Plus clock provider maps these IDs from DT clock specifiers to registered clock objects.

State and persistence: Numeric IDs are stable DT ABI; runtime PLL/divider/gate state is external to the header.

Dependencies and integration points: Integrates Mobileye EyeQ6L Plus DTS files with the common clock framework and consumers in CPU, DDR, VDI, accelerator, OSPI, UART, I2C, SPI, and peripheral subsystems.

Risks and test signals: Risks include parent/child confusion among PLL and OCC outputs and off-by-one provider tables. Test with `dtbs_check`, provider probe logs, clk tree inspection, serial and SPI/I2C bring-up, OSPI storage access, accelerator/VDI consumers, and suspend/resume clock enable validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mobileye,eyeq6lplus-clk.h -->
