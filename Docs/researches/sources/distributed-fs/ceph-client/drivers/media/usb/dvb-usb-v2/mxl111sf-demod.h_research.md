# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.h

Purpose: public attach/config header for the MxL111SF DVB-T demodulator module. It defines the bridge callback contract needed by `mxl111sf-demod.c` and provides a Kconfig-aware attach stub.

Important APIs/types/functions: `struct mxl111sf_demod_config` carries `read_reg`, `write_reg`, and `program_regs` callbacks accepting `struct mxl111sf_state`. `mxl111sf_demod_attach()` returns a configured `struct dvb_frontend *` when `CONFIG_DVB_USB_MXL111SF` is enabled; otherwise the inline stub warns and returns NULL.

Control flow: `mxl111sf.c` builds a static config pointing to its USB register helpers and calls `dvb_attach(mxl111sf_demod_attach, state, &mxl_demod_config)`. The demod module stores the callback table in private state and uses it for all runtime frontend operations.

State and persistence: this header has no runtime state. It defines which external state object owns the register transport (`mxl111sf_state`) and makes demod instances dependent on that object outliving the frontend.

Dependencies and integration: includes DVB frontend definitions and the MxL111SF shared header. Its Kconfig guard ties the demod attach helper to the USB driver symbol, so bridge builds without the symbol receive a visible warning rather than an unresolved function.

Risks: no callback is mandatory at compile time; missing callbacks fail at runtime with `-EINVAL`. The guard key is the bridge config symbol, so reuse outside the MxL111SF USB driver would need matching Kconfig wiring.

Test signals: build with `CONFIG_DVB_USB_MXL111SF=y/m/n`; verify `dvb_attach()` succeeds when enabled and returns NULL from the stub when disabled; probe a DVB-T MxL111SF profile and ensure demod operations call through the USB register callbacks.
