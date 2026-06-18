## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.h

Purpose: declares the externally defined Realtek RTL8822C initialization and calibration tables used by the rtw88 chip description. The file does not own data; it is the typed link between `rtw8822c.c` and the generated/static table providers in the same driver family.

Important APIs/types: all symbols are `extern const struct rtw_table`: MAC, AGC, BB, BB power-by-rate, RF path A/B, two TX power limit variants, DPK AFE/non-DPK, DPK MAC/BB, and MP calibration initialization tables. These depend on `struct rtw_table` from the rtw88 table-loader infrastructure.

Control flow and state: no runtime control flow or persistent state exists here. The declarations are consumed during chip bring-up when common code calls `rtw_load_table()` through fields in the chip info structure.

Dependencies and integration: depends on the rtw88 chip-table model and the corresponding compiled table objects. Any declaration/name drift breaks link-time integration or chip initialization.

Risks and test signals: table names are hardware contract points, so the main risks are missing object files, wrong table assignment in chip info, or ABI drift in `struct rtw_table`. Build/link tests and successful RTL8822C power-on/table load logs are the practical signals.
