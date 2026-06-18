# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.c

Purpose: implements MAX S4/S8 and MCI-based MAX frontend attachment plus LNB voltage/tone/DiSEqC routing policy. It adapts MXL5xx and SX8 frontends to ddbridge DVB inputs and board LNB hardware.

Important APIs/types/functions: exported `ddb_lnb_init_fmode()`, `ddb_fe_attach_mxl5xx()`, and `ddb_fe_attach_mci()`. Internal helpers send `LNB_CMD_*`, buffer DiSEqC messages, set satellite/tone/voltage, remap frontend input, read firmware from SPI flash, and override frontend SEC operations. Module parameters are `fmode`, `fmode_sat`, and `old_quattro`.

Control flow: during DVB input attach, the core calls either MXL5xx or MCI attach. Attach initializes demod/tuner mapping, LNB command channel for the first four inputs, fmode, frontend callbacks, and `sec_priv`. Runtime `set_voltage`, `set_tone`, and DiSEqC operations update shared link LNB state and write hardware commands.

State and persistence: mutable state lives in `dev->link[lnr].lnb`: lock, tone bitmap, voltage arrays, aggregate `voltages`, old voltage cache, and fmode. State is runtime-only but exposed through sysfs `fmode*`.

Dependencies/integration: depends on ddbridge registers/MMIO, MXL5xx frontend, MCI config from `ddbridge-sx8.c`, SPI flash read from core, and DVB frontend SEC APIs.

Risks and test signals: LNB state is shared by inputs and sensitive to fmode/quattro mapping; incorrect locking or voltage caching can leave wrong power on satellite inputs. Test by tuning multiple inputs, toggling 13/18V and tone, sending DiSEqC, reading firmware-backed MXL attach, changing fmode through sysfs, and validating old/new quattro behavior.
