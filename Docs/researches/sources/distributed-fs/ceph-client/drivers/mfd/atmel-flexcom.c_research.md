<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c

Purpose: configures an Atmel/Microchip Flexcom block into one selected serial function and populates its child devices from device tree. Flexcom can expose USART, SPI, or TWI functionality, but only the selected function is clocked and muxed.

Important APIs and functions: `atmel_flexcom_probe` reads `atmel,flexcom-mode`, maps the register block, enables the clock, writes the mode register, disables the clock, and calls `devm_of_platform_populate`. `atmel_flexcom_resume_noirq` rewrites the selected mode after low-level resume.

Control flow: probe validates that the mode is between `ATMEL_FLEXCOM_MODE_USART` and `ATMEL_FLEXCOM_MODE_TWI`, obtains MMIO and clock resources, temporarily enables the clock to write `FLEX_MR_OPMODE(opmode)` to `FLEX_MR`, then populates children declared below the node. Resume repeats the mode write before child resume paths run.

State and persistence: `struct atmel_flexcom` stores MMIO base, selected opmode, and clock pointer. Hardware mode register state may be lost across system suspend, so the noirq resume hook restores it.

Dependencies and integration points: depends on DT binding constants, platform resources, OF platform population, MMIO, and clock framework. Child nodes under the Flexcom DT node bind to the actual USART/SPI/TWI drivers after the wrapper selects mode.

Risks: the driver does not keep the clock enabled after configuration, assuming children manage their own clocks. An invalid or missing `atmel,flexcom-mode` fails probe. If resume mode restoration fails because the clock cannot enable, child drivers may access an unconfigured block.

Test signals: probe with USART/SPI/TWI modes, invalid mode rejection, clock enable/write/disable tracing, child OF population, system suspend/resume preserving mode, and register readback of `FLEX_MR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c -->
