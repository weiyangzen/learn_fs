# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.h

Purpose: minimal public header for the MxL111SF I2C adapter implementation.

Important APIs/types/functions: it declares `mxl111sf_i2c_xfer(struct i2c_adapter *adap, struct i2c_msg msg[], int num)`, the only function consumed by the main driver's `struct i2c_algorithm`.

Control flow: `mxl111sf.c` assigns this function to `.master_xfer`; Linux I2C core calls it for all child device transactions after dvb-usbv2 registers the adapter.

State and persistence: no state is defined here. The function contract implies that caller-provided adapter data resolves to a `dvb_usb_device` whose private data is `struct mxl111sf_state`.

Dependencies and integration: includes `mxl111sf.h`, and through it the dvb-usbv2 and shared state definitions. It links `mxl111sf-i2c.c` to the main bridge file without exposing the many software/hardware helper internals.

Risks: the header does not declare functionality flags or helper types; maintainers must keep the `.functionality` implementation in `mxl111sf.c` synchronized manually. The broad include of `mxl111sf.h` may pull more dependencies than the one prototype needs.

Test signals: compile the MxL111SF driver; verify `mxl111sf_i2c_algo.master_xfer` resolves; run I2C attach/probe paths for EEPROM, demods, tuners, and GPIO expander.
