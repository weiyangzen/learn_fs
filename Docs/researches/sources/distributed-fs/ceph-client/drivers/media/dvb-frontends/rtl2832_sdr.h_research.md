# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_sdr.h

Purpose: Public platform-data contract for the RTL2832 SDR platform driver.

Important APIs/types/functions: `struct rtl2832_sdr_platform_data` supplies clock, tuner id, demod regmap, DVB frontend, optional tuner V4L2 subdev, and parent DVB USB device. Tuner ids mirror RTL2832 ids for SDR-supported tuners.

Control flow: the parent bridge creates the platform device after demod/tuner setup. `rtl2832_sdr_probe()` consumes this structure to bind SDR capture to the same hardware.

State and persistence: no state is stored by the header. It carries borrowed pointers whose lifetime must cover the SDR platform device.

Dependencies/integration: includes I2C, V4L2 subdev, and DVB frontend declarations. Integrates demod, tuner controls, and USB streaming.

Risks: no explicit ownership/refcounting in the struct; tuner id list excludes SI2157 despite demod support; missing `dvb_usb_device` or regmap is fatal in practice.

Test signals: platform data validation through successful SDR probe, tuner-specific control set creation, streaming with each supported tuner id.
