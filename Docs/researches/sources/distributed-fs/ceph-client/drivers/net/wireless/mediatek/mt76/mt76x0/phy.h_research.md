# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.h

Purpose: this header defines MT76x0 RF/PHY constants and table element types used by `phy.c` and static init tables.

Important definitions: RF band masks include `RF_G_BAND`, `RF_A_BAND`, low/mid/high/11J 5 GHz masks, and bandwidth masks `RF_BW_20`, `RF_BW_40`, `RF_BW_10`, `RF_BW_80`. `MT_RF`, `MT_RF_BANK`, and `MT_RF_REG` encode/decode RF bank/register offsets. PLL, VCO, SDM, and clock bit masks define fields used while programming frequency plans.

Important types: `mt76x0_bbp_switch_item` maps a band/bandwidth mask to a BBP register pair. `mt76x0_rf_switch_item` maps RF bank/register plus band/bandwidth mask to an RF byte value. `mt76x0_freq_item` describes per-channel PLL/SDM fields. `mt76x0_rate_pwr_item` and `mt76x0_rate_pwr_tab` model rate power and PA mode for CCK/OFDM/HT/VHT/STBC/MCS32 classes.

Control flow and integration: the header is consumed by `initvals.h`, `initvals_init.h`, `initvals_phy.h`, and `phy.c`. Its masks drive table matching during init and channel changes; its structures determine table layout.

State and persistence behavior: no runtime state. It defines how immutable tables are interpreted and how RF register addresses are encoded for runtime writes.

Dependencies: expects mt76 register-pair definitions and Linux bit macros from includers. It intentionally contains no function prototypes beyond types/constants.

Risks: wrong RF address encoding or masks would corrupt unrelated RF registers. `mt76x0_freq_item` field meanings must match the PLL programming sequence in `phy.c`; adding/removing fields requires synchronized table updates.

Test signals: compile all table users, verify RF register bank/reg bounds in `phy.c` do not warn, and validate channel tuning across every table category.
