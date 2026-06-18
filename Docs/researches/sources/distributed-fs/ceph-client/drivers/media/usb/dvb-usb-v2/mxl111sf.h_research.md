# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf.h

Purpose: shared private header for the MxL111SF bridge, helper, tuner, and demod files. It centralizes endpoint constants, chip/mode enums, private state layout, register control structures, exported bridge register APIs, and debug macros.

Important APIs/types/functions: `struct mxl111sf_state` is the device-wide state carrier. `struct mxl111sf_adap_state` stores per-frontend alt mode, GPIO mode, device mode, EP6 clock phase, and saved frontend callbacks. `enum mxl111sf_gpio_port_expander`, `enum mxl111sf_pads`, chip revision constants, device mode constants, endpoint constants, `MXL_MAX_XFER_SIZE`, and `struct mxl111sf_reg_ctrl_info` define the local ABI. Prototypes expose `mxl111sf_read_reg()`, `mxl111sf_write_reg()`, `mxl111sf_write_reg_mask()`, `mxl111sf_ctrl_program_regs()`, and `mxl111sf_ctrl_msg()`.

Control flow: all MxL111SF sources include this header. The main driver fills and owns `mxl111sf_state`; helper modules receive it through config callbacks or direct calls and operate on shared USB buffers, chip revision, GPIO state, and debug flags.

State and persistence: the header describes all long-lived bridge state: USB pointer, GPIO expander type/address, chip ID/version/revision, current modes, EEPROM info, frontend lock, per-frontend state array, control message buffers, message mutex, and optional media-controller tuner entity/pads. No on-disk persistence exists.

Dependencies and integration: includes dvb-usbv2, TV EEPROM, and media entity definitions. Debug macros are shared across in-tree and separately built tuner/demod modules, with `mxl_fail()` conditionally using the external debug variable.

Risks: this header exposes internals broadly and couples helper modules tightly to the bridge state layout. `adap_state[3]` assumes at most three frontends. Debug macros are statement-like and not wrapped in `do { } while (0)`, which can be awkward in conditionals. Some historic conditional enum code is disabled, leaving parallel integer mode fields.

Test signals: compile all MxL111SF objects under module and built-in configs; check `MXL_MAX_XFER_SIZE` against all USB command callers; exercise three-frontend profiles; media-controller builds with tuner pads; debug flag paths in external tuner/demod modules.
