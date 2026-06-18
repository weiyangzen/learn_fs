# sources/distributed-fs/ceph-client/drivers/hwmon/occ/Kconfig

Purpose: Kconfig definitions for IBM On-Chip Controller hwmon support.

Important symbols: `SENSORS_OCC_P8_I2C` enables the POWER8 I2C BMC transport and depends on `I2C`; `SENSORS_OCC_P9_SBE` enables POWER9/P10 SBE/FSI transport and depends on `FSI_OCC`; both select hidden common symbol `SENSORS_OCC`.

Control flow: selecting either transport builds the common OCC hwmon core plus the selected bus frontend. Help text documents that these drivers run on a BMC connected to the POWER processor, not on the host processor itself.

State and persistence: no runtime state; it controls build-time inclusion and module names `occ-p8-hwmon` and `occ-p9-hwmon`.

Dependencies and integration: integrates OCC with the hwmon Kconfig tree, I2C, and FSI OCC infrastructure.

Risks: common code is hidden and selected only by frontends, so new transport symbols must also select `SENSORS_OCC`. Missing dependency updates would surface as build failures.

Test signals: `olddefconfig`, modular and built-in builds for each frontend, and dependency-disabled configs where symbols are unavailable.
