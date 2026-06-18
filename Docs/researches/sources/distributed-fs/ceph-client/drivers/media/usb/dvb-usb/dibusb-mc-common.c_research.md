# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dibusb-mc-common.c

Purpose: shared DiB3000MC/P frontend and tuner attachment code for DiBUSB MC devices. It provides AGC/config tables and exported attach helpers used by `dibusb-mc.c`.

Important APIs/functions: exports `dibusb_dib3000mc_frontend_attach()` and `dibusb_dib3000mc_tuner_attach()`. Static configs include `dib3000p_mt2060_agc_config`, `stk3000p_dib3000p_config`, `dib3000p_panasonic_agc_config`, `mod3000p_dib3000p_config`, and `stk3000p_mt2060_config`.

Control flow: frontend attach handles a Lite-On warm-device delay, tries `dib3000mc_attach()` first at `DEFAULT_DIB3000P_I2C_ADDRESS` then at `DEFAULT_DIB3000MC_I2C_ADDRESS`, and, on success, stores PID parse/control callbacks in `struct dibusb_state`. Tuner attach computes MT2060 first-IF calibration from EEPROM for Lite-On and MOD3001 variants, gets the demod tuner I2C master, tries `mt2060_attach()`, and falls back to Panasonic PLL parameters if MT2060 is absent.

State and persistence: adapter private state records whether MT2060 is present and exposes demod PID ops. EEPROM calibration bytes influence per-attach IF values but are not modified.

Dependencies and integration: depends on DiB3000MC demod APIs, MT2060, generic DVB PLL, `dibusb_read_eeprom_byte()`, and DiBUSB common I2C/power/streaming helpers.

Risks: EEPROM interpretation is vendor/product specific and tolerates odd values only with warnings. Fallback tuner attach returns `-ENOMEM` if PLL attach fails, which conflates memory and hardware absence. Correct PID filtering depends on ops being populated only after frontend attach succeeds.

Test signals: Lite-On and MOD3001 devices with calibration EEPROM data, DiB3000P versus DiB3000MC address fallback, MT2060 present and absent cases, PID parser enable/disable, and stream lock after retuning.
