# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/zd1301_demod.h

Purpose: Public platform-data and accessor header for the ZD1301 demodulator platform driver.

Important APIs/types/functions: `struct zd1301_demod_platform_data` supplies a private callback pointer plus `reg_read()` and `reg_write()` functions for 16-bit register addresses and 8-bit values. When `CONFIG_DVB_ZD1301_DEMOD` is reachable, the header declares `zd1301_demod_get_dvb_frontend()` and `zd1301_demod_get_i2c_adapter()`. Disabled stubs warn and return `NULL`.

Control flow: A parent bridge creates a platform device with this platform data, waits for probe, then calls the exported helpers to get the frontend and child I2C adapter used to attach a tuner. Disabled builds fail early through the stubs.

State and persistence: The header owns no state. Platform data callback lifetime is critical because every hardware register access in the implementation goes through these function pointers.

Dependencies/integration: Includes platform device, DVB frontend, and media DVB frontend headers. It is the coupling point between a parent hardware driver and the ZD1301 demod platform child.

Risks and test signals: Validate callback pointers before instantiation, Kconfig-disabled builds, helper calls before/after probe, and remove ordering so exported pointers are not used after the platform device is gone.
