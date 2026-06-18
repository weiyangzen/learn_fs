# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.h

Purpose: `table.h` declares the static RTL8723AE register table arrays and their lengths.

Important APIs/data: length constants cover PHY 1T, PHY PG, Radio A 1T, MAC, and AGC tables. Extern declarations expose `RTL8723EPHY_REG_1TARRAY`, `RTL8723EPHY_REG_ARRAY_PG`, `RTL8723E_RADIOA_1TARRAY`, `RTL8723EMAC_ARRAY`, and `RTL8723EAGCTAB_1TARRAY`.

Control flow: no executable flow. The lengths drive loops in `phy.c` that step by 2 for address/value arrays and by 3 for PG address/mask/data arrays.

State and persistence: no state is stored in the header. The declared arrays represent immutable configuration data, though the declarations are not `const`.

Dependencies/integration: includes `<linux/types.h>` for `u32`. Consumed by `phy.c` and implemented by `table.c`.

Risks: length constants must exactly match initializer sizes. Wrong lengths can skip required programming or read past array bounds. Include guard spelling `__RTL8723E_TABLE__H_` is unusual but functional. Non-const externs allow accidental writes from any includer.

Test signals: compile/link success, KASAN/UBSAN array-bound cleanliness during table load, and hardware init stability.
