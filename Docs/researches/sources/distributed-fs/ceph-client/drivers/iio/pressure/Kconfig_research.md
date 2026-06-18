<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig

Purpose: Kconfig menu for IIO pressure sensor drivers. It declares selectable symbols, bus dependencies, hidden common core symbols, and helper selections for pressure, barometer, altimeter, humidity-capable, and HID pressure devices.

Important APIs, types, and functions: this is build metadata rather than C code. Key symbols for this subset are `ABP060MG`, `ABP2030PA`, `ABP2030PA_I2C`, `ABP2030PA_SPI`, `BMP280`, `BMP280_I2C`, `BMP280_SPI`, `IIO_CROS_EC_BARO`, `DLHL60D`, `DPS310`, `HID_SENSOR_PRESS`, `HP03`, `HP206C`, `HSC030PA`, `HSC030PA_I2C`, `HSC030PA_SPI`, and `ADP810`.

Control flow: user-visible bus symbols select hidden common cores where needed. `BMP280` selects bus helper modules conditionally on `I2C` and `SPI_MASTER`; ABP2 and MPR use hidden common cores selected by bus-specific drivers; HSC selects hidden I2C/SPI helpers based on available buses.

State and persistence: Kconfig choices persist in the kernel `.config` and determine which objects become built-in or modules. No runtime state is defined here.

Dependencies and integration points: integrates with the kernel build system, IIO buffer/trigger selections, regmap bus helpers, CRC support, HID sensor hub, ChromeOS EC sensor core, and bus subsystems. It also communicates module names through help text.

Risks: hidden core symbols must stay aligned with Makefile object names and exported namespaces. Conditional `select` can build bus modules unintentionally when a common symbol is enabled with both buses available. Help text and module names can drift from source files. Alphabetical-order comments are partly strained by late additions such as `ADP810`.

Test signals: use `make olddefconfig` and `make menuconfig` visibility checks, verify module dependency closure for I2C-only, SPI-only, and both-bus configs, run `scripts/kconfig/conf` warnings, and confirm selected symbols produce the objects listed in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig -->
