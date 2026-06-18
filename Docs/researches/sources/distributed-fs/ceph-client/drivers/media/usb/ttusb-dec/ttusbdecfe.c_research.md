
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusbdecfe.c

## Purpose
`ttusbdecfe.c` implements lightweight DVB-T and DVB-S frontend wrappers for TTUSB DEC devices. It translates frontend operations into firmware commands sent through a callback supplied by `ttusb_dec.c`.

## Important APIs, Types, and Functions
`struct ttusbdecfe_state` stores the `ttusbdecfe_config`, embedded `dvb_frontend`, high-band flag, and LNB voltage. Important functions are `ttusbdecfe_dvbt_attach()`, `ttusbdecfe_dvbs_attach()`, `ttusbdecfe_release()`, `ttusbdecfe_dvbt_set_frontend()`, `ttusbdecfe_dvbt_read_status()`, `ttusbdecfe_dvbt_get_tune_settings()`, `ttusbdecfe_dvbs_set_frontend()`, `ttusbdecfe_dvbs_read_status()`, `ttusbdecfe_dvbs_diseqc_send_master_cmd()`, `ttusbdecfe_dvbs_set_tone()`, and `ttusbdecfe_dvbs_set_voltage()`. It exports both attach symbols.

## Control Flow
Attach allocates state, stores the config callback, copies the appropriate static `dvb_frontend_ops`, and returns the embedded frontend. DVB-T tuning sends command `0x71` with frequency in kHz and fixed parameters; status command `0x73` maps firmware status values to DVB frontend lock flags or timeout. DVB-S tuning adds LOF high/low offset based on tone state, sends frequency, symbol rate, band, and voltage with command `0x71`; DVB-S status currently reports lock unconditionally. DiSEqC sends command `0x72`, while tone and voltage setters update state used by the next tune command.

## State and Persistence
State is per frontend allocation: config pointer, high-band selection, and LNB voltage. No hardware state is cached beyond these fields, and no persistent storage exists.

## Dependencies and Integration Points
The file depends on DVB frontend core and `ttusbdecfe_config.send_command`, which is supplied by the parent USB driver. It defines frontend capability ranges for DVB-T and DVB-S.

## Risks and Edge Cases
DVB-S `read_status()` always reports full lock, so applications may not detect actual signal loss. Command return values from set-frontend paths are ignored, hiding firmware errors. DVB-T status requires an exact four-byte reply. DiSEqC validates maximum command length but otherwise trusts firmware delivery. State changes for tone/voltage do not immediately send hardware commands until tuning.

## Test Signals
Test DVB-T tuning/status values 1-4, DVB-S tuning with 13/18 V and tone on/off, DiSEqC length rejection and delivery, frontend release, and behavior when the parent send-command callback returns errors.
