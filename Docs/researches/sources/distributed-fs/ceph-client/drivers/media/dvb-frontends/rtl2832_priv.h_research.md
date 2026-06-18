# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/rtl2832_priv.h

Purpose: Private RTL2832 driver state, register bitfield identifiers, and tuner-specific initialization data.

Important APIs/types/functions: `struct rtl2832_dev` holds platform data, client, regmap, mux, frontend, status/stat counters, gate work, PID bitmap, and slave TS state. `struct rtl2832_reg_entry` maps symbolic bitfields to start address and bit positions. `struct rtl2832_reg_value` drives generic and tuner register scripts. `enum DVBT_REG_BIT_NAME` names demod fields consumed by `rtl2832.c`.

Control flow: `rtl2832_wr_demod_reg()` indexes the enum into `registers[]` in `rtl2832.c`; `rtl2832_init()` selects one tuner init array by platform tuner id and writes it sequentially.

State and persistence: runtime state lives in `rtl2832_dev`; static register tables are immutable driver data. No persistence beyond hardware register programming.

Dependencies/integration: depends on regmap, math64, bitops, DVB frontend, integer log, and public `rtl2832.h`.

Risks: enum/table alignment is critical because the table is indexed directly; several enum values have no entry in `registers[]` and must not be used with generic accessors unless added; init values are undocumented hardware magic and tuner sensitive.

Test signals: build warnings for missing enum entries are unlikely, so runtime coverage should include every supported tuner path and bitfield write used by init/tune/status.
