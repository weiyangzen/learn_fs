# sources/distributed-fs/ceph-client/drivers/iio/humidity/Makefile

Purpose: Build recipe for IIO humidity drivers. It maps Kconfig symbols to object files and composes the multi-object HTS221 core module.

Important APIs/types/functions: Direct `obj-$(CONFIG_...)` rules build one object per humidity driver. `hts221-y := hts221_core.o hts221_buffer.o` composes the main HTS221 module, while `hts221_i2c.o` and `hts221_spi.o` build transport modules. `ccflags-y` adds `drivers/iio/common/hid-sensors` include path for the HID humidity driver.

Control flow: Build-time only; Kbuild includes objects based on configuration.

State and persistence: The only persisted outcome is built-in or module object selection. No runtime state.

Dependencies and integration points: Integrates with Kbuild, Kconfig, HID sensor common headers, and the HTS221 exported namespace split between core and bus drivers.

Risks: Object names must stay synchronized with module names and Kconfig help. The HID include path is global to this subdirectory, so header name conflicts could affect future files.

Test signals: `make M=drivers/iio/humidity` with representative configs, especially HTS221 I2C/SPI module combinations and HID humidity builds.
