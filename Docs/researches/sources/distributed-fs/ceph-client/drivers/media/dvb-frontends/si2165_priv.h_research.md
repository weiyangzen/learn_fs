# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2165_priv.h

Purpose: Private Si2165 configuration, firmware name, statistics constants, and register address map.

Important APIs/types/functions: `SI2165_FIRMWARE_REV_D` names firmware. `struct si2165_config` mirrors platform data plus I2C address. `STATISTICS_PERIOD_*` defines BER accumulation scale. `REG_*` constants cover chip mode, PLL, DSP control, AGC, DVB standard, firmware DCOM, counters, FEC lock, TS output, and RSSI registers.

Control flow: `si2165.c` uses these constants for probe, init, firmware upload, DVB-T/C setup, stats, and TS configuration.

State and persistence: constants only; no runtime state.

Dependencies/integration: private to SI2165 driver.

Risks: several registers are marked unknown and may be silicon/firmware sensitive; mismatch between register widths and helper choice would silently program wrong values.

Test signals: firmware upload, register-list execution, stats period behavior, TS output after init.
