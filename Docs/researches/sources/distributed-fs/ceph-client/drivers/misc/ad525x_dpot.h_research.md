# sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot.h

Purpose: defines the shared AD525x digital potentiometer device-id encoding, feature flags, register command constants, bus-operation contract, and shared probe/remove declarations.

Important APIs and types: `DPOT_CONF` packs feature flags, active wiper bits, maximum-position exponent, and a unique id into an `enum dpot_devid` value. `DPOT_UID`, `DPOT_MAX_POS`, `DPOT_WIPERS`, and `DPOT_FEAT` unpack that encoding. `enum dpot_devid` lists supported AD5258/AD5259, AD516x, AD52xx, ADN28xx, and OTP-capable parts. `struct ad_dpot_bus_ops` abstracts byte, register-byte, and register-word reads/writes. `struct ad_dpot_bus_data` passes a bus client plus ops into `ad_dpot_probe`.

Control flow: bus-specific drivers select an enum value from their device-id tables, fill bus ops, and call the shared core. The core uses feature bits such as `F_CMD_EEP`, `F_CMD_OTP`, `F_RDACS_WONLY`, `F_AD_APPDATA`, and `F_SPI_*` to choose register protocols and sysfs exposure.

State and persistence: this header owns no runtime state, but its encodings directly determine persistent hardware affordances such as EEPROM and one-time programmable support. Incorrect encodings change both ABI shape and hardware commands.

Dependencies and integration points: depends on Linux integer types and an including translation unit with `struct device`. It is included by the shared core and by I2C/SPI frontend drivers.

Risks: many constants encode hardware protocol details in compact bitfields, so table mistakes are hard to see in review. `DPOT_MAX_POS` is an exponent, not a literal maximum, which can be misused. Function declarations rely on transitive visibility for `struct device` rather than declaring it locally.

Test signals: compile all frontends, verify each device id creates the expected number of sysfs attributes and RDAC range, and cross-check encoded features against datasheets for EEPROM, OTP, tolerance, SPI width, and write-only behavior.
