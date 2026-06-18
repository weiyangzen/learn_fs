# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.h

Purpose: public GPIO and pin-mux helper header for MxL111SF board support. It gives the main USB driver a compact API for GPIO writes, port-expander initialization, ATSC/MH/DVB-T mode switching, and transport pin mux selection.

Important APIs/types/functions: exported prototypes are `mxl111sf_set_gpio()`, `mxl111sf_init_port_expander()`, `mxl111sf_gpio_mode_switch()`, and `mxl111sf_config_pin_mux_modes()`. Mode constants are `MXL111SF_GPIO_MOD_DVBT`, `MXL111SF_GPIO_MOD_MH`, and `MXL111SF_GPIO_MOD_ATSC`. `enum mxl111sf_mux_config` names pin-mux targets including TS output serial/parallel, GPIO, serial/SPI/parallel input, BT656/I2S, and default mode.

Control flow: `mxl111sf.c` includes this header and calls these helpers during device init, frontend attach/init, and streaming setup depending on product profile, chip revision, endpoint, and `spi`/`isoc` module options.

State and persistence: no direct state is defined here; all operations mutate `struct mxl111sf_state` fields and hardware registers in the implementation. The enum values are persistent ABI within this driver directory because board profiles depend on their names and meanings.

Dependencies and integration: includes `mxl111sf.h`, so it inherits the shared state/debug contract. It bridges board-profile logic with low-level GPIO/pin-mux programming.

Risks: the enum is unscoped C state with a broad default case in implementation; adding values requires updating the large switch in `mxl111sf-gpio.c`. The mode constants are plain integers rather than enum members, so invalid mode values compile and fall into default behavior.

Test signals: compile all MxL111SF profiles; exercise each enum mode from board attach and streaming paths; validate DVB-T, ATSC, and MH mode switching on hardware variants with internal and external GPIO.
