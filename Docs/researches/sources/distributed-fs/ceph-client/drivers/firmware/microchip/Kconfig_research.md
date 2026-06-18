# sources/distributed-fs/ceph-client/drivers/firmware/microchip/Kconfig

Purpose: Defines the Microchip PolarFire SoC Auto Update firmware upload driver configuration.

Important APIs/types/functions: `POLARFIRE_SOC_AUTO_UPDATE` is a tristate depending on `POLARFIRE_SOC_SYS_CTRL` and selecting `FW_LOADER` plus `FW_UPLOAD`.

Control flow: No runtime flow. The option controls whether the Auto Update driver is compiled.

State and persistence behavior: No direct state, but enabling it allows Linux to write FPGA bitstreams to SPI flash through firmware upload.

Dependencies and integration points: Integrates the Microchip system controller, firmware loader/upload framework, and MTD flash access.

Risks and test signals: Because the feature can reprogram FPGA images, dependencies must ensure the system controller and upload framework are present. Test built-in/module builds and absence/presence of system controller support.
