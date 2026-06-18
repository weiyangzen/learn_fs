# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.h

Purpose: public attach/config header for the MxL111SF tuner module. It defines IF selection values, bridge callback requirements, optional antenna hunting hook, and a Kconfig-aware attach API.

Important APIs/types/functions: `enum mxl_if_freq` names supported IF outputs from 4.0 MHz through 44 MHz. `struct mxl111sf_tuner_config` carries IF frequency, invert-spectrum bit, register read/write/program callbacks, top-master callback, and `ant_hunt` callback. `mxl111sf_tuner_attach()` installs tuner ops into an existing DVB frontend when enabled; otherwise an inline stub warns and returns NULL.

Control flow: `mxl111sf.c` supplies a static config using IF 6 MHz and bridge register helpers, then calls `dvb_attach(mxl111sf_tuner_attach, fe, state, &mxl_tuner_config)` for each frontend. Runtime tuner ops call back into the bridge for register access and antenna path control.

State and persistence: no mutable state is stored in the header. The IF enum and config fields define how the tuner instance will persist its IF selection in runtime private state and chip registers.

Dependencies and integration: includes DVB frontend APIs and `mxl111sf.h`. The Kconfig guard matches the MxL111SF USB symbol and prevents unresolved symbols when the tuner module is unavailable.

Risks: config callbacks are optional only at runtime; missing callbacks cause `-EINVAL`. IF enum values are raw register encodings, so changing them would alter hardware programming. The attach stub warns but can still permit higher-level attach code to fail later if not checked.

Test signals: build enabled/disabled configs; attach tuner after demod for all product profiles; verify IF frequency getter values for each enum; exercise antenna hunt callback presence and absence.
