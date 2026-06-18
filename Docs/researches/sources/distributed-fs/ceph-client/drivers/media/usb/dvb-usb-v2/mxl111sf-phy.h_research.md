# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-phy.h

Purpose: public prototype header for MxL111SF physical-layer and transport-port helpers.

Important APIs/types/functions: it declares reset, device-mode, top-master, USB output, 656 disable, tuner/demod init, MPEG input configuration, I2S init/config/disable, SPI mode, and IDAC configuration helpers. The prototypes expose transport parameters such as serial/parallel TS, bit order, clock phase, MPEG valid/sync polarity, I2S bit positions, and IDAC control/current/hysteresis fields.

Control flow: `mxl111sf.c` and `mxl111sf-tuner.c` call these helpers during frontend attach/init, stream control, tuner IF setup, antenna hunting, and product profile setup. The header is the compile-time contract between the board driver and lower-level register programming.

State and persistence: no state is defined here; all helpers accept `struct mxl111sf_state *` and modify its `device_mode` or chip registers. Parameter choices persist until reset or later reconfiguration.

Dependencies and integration: includes `mxl111sf.h` for shared state and debug conventions. It is paired with `mxl111sf-reg.h` constants in the implementation.

Risks: parameters are plain integers rather than enums, so invalid serial/parallel, clock phase, and polarity values compile and may produce unintended register values. Adding new transport modes requires changes in both the board driver and implementation.

Test signals: compile all MxL111SF users; exercise frontend init and stream control for EP4/EP5/EP6; verify IDAC antenna switching and SPI mode changes on v8 devices.
