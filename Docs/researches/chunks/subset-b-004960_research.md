# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 41892-49275

## Scope and Purpose

This chunk is a data-only section of the Realtek rtw89 RTL8852C PHY table source. It contributes regulatory transmit-power limits used by the 8852C default RFE parameters. The chunk contains no executable functions; its behavior comes from large `static const s8` designated-initializer tables that are later referenced through `rtw89_8852c_dflt_parms`.

Visible coverage in this chunk:

- Tail of `rtw89_8852c_txpwr_lmt_6g`, a 6 GHz non-RU transmit-power limit table declared earlier at line 36955.
- Entire `rtw89_8852c_txpwr_lmt_ru_2g`, declared at lines 46234-46235.
- Beginning and middle of `rtw89_8852c_txpwr_lmt_ru_5g`, declared at lines 47415-47416; this table continues past the assigned end line at 49275.

The data maps regulatory domains, channel indexes, transmit-chain count, bandwidth/RU category, rate section, beamforming flag, and 6 GHz power mode into signed RF-domain power-limit values. It is part of the default static regulatory baseline for 8852C unless firmware RFE data overrides the corresponding rule pointers.

## Important APIs, Types, and Data Contracts

- `rtw89_8852c_txpwr_lmt_6g` has shape `[RTW89_6G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER][RTW89_6G_CH_NUM]`. The visible tail writes 6 GHz regulatory entries for bandwidth/rate/beamforming combinations, including many `RTW89_REG_6GHZ_POWER_*` subindexes.
- `rtw89_8852c_txpwr_lmt_ru_2g` has shape `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`, where `RTW89_RU_NUM` includes `RTW89_RU26`, `RTW89_RU52`, `RTW89_RU106`, `RTW89_RU52_26`, and `RTW89_RU106_26`. The 2 GHz table covers channel indexes 0-13, matching the 14 2.4 GHz channels.
- `rtw89_8852c_txpwr_lmt_ru_5g` has shape `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`. The visible section covers RU indexes 0-2, both NTX indexes, and 5 GHz channel indexes through 35 at the chunk boundary; the remaining entries continue after this chunk.
- `enum rtw89_regulation_type` defines the regulatory indexes used here: `RTW89_WW`, `RTW89_ETSI`, `RTW89_FCC`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_MEXICO`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_CN`, `RTW89_QATAR`, `RTW89_UK`, and `RTW89_THAILAND`.
- `struct rtw89_txpwr_rule_2ghz`, `struct rtw89_txpwr_rule_5ghz`, and `struct rtw89_txpwr_rule_6ghz` in `core.h` define the pointer shapes consumed by the PHY code. `rtw89_8852c_dflt_parms` wires `.rule_2ghz.lmt_ru`, `.rule_5ghz.lmt_ru`, `.rule_6ghz.lmt`, and `.rule_6ghz.lmt_ru` to the 8852C tables.

## Control Flow and Runtime Use

There is no local control flow in this chunk. Runtime control flow is indirect:

1. The device selects `rtw89_8852c_dflt_parms` as the default RFE parameter set.
2. `rtw89_phy_read_txpwr_limit_ru()` receives band, RU size, NTX, and channel.
3. It derives the channel index with `rtw89_channel_to_idx()`, chooses the active regulatory domain with `rtw89_regd_get()`, and for 6 GHz also uses `rtwdev->regulatory.reg_6ghz_power`.
4. For 2 GHz and 5 GHz, it reads `(*rule_*ghz->lmt_ru)[ru][ntx][regd][ch_idx]`; for 6 GHz it reads `(*rule_6ghz->lmt_ru)[ru][ntx][regd][reg6][ch_idx]`.
5. If a regional RU limit is zero, the lookup falls back to the `RTW89_WW` default row. Nonzero values, including negative limits and `127`, bypass that fallback.
6. The selected RF-domain value is combined with optional dynamic antenna-gain RFE limits, converted with `rtw89_phy_txpwr_rf_to_mac()`, then bounded by SAR and TPE constraints.
7. `rtw89_phy_fill_txpwr_limit_ru_ax()` arranges those reads into a hardware page according to channel width, and `rtw89_phy_set_txpwr_limit_ru_ax()` writes the packed bytes to `R_AX_PWR_RU_LMT`.

The non-RU 6 GHz entries visible at the start of this chunk flow through the analogous `rtw89_phy_read_txpwr_limit()` path and are written by `rtw89_phy_set_txpwr_limit_ax()` to `R_AX_PWR_LMT`.

## State and Persistence Behavior

The data in this chunk is `static const` and has no runtime mutation or persistence of its own. It persists only as compiled kernel module image data. Runtime state that affects interpretation lives outside the table:

- `rtwdev->rfe_parms` selects either these defaults or firmware-loaded override tables.
- `rtwdev->regulatory` stores the current regulatory domain and 6 GHz power mode.
- SAR, TPE, and antenna-gain logic apply additional runtime caps after table lookup.

Because C designated initializers leave omitted elements as zero, zero is semantically important: in the lookup path, a zero regional value means "fall back to WW" for the default table. A deliberate zero power limit is therefore hard to represent in these static regional rows without being interpreted as missing.

## Data Characteristics in This Chunk

- The assigned span contains 7,376 designated assignments.
- Values range from `-30` to `127`. Common values include ordinary positive RF power limits such as 16, 20, 28, 30, 44, 52, 58, 70, and 74.
- `127` is heavily used as a sentinel-style permissive/invalid/no-specific-limit value in many regional/channel combinations. Since it is nonzero, it will not trigger WW fallback.
- Negative values such as `-30`, `-20`, `-6`, `-4`, and `-2` appear in edge or restricted combinations. These are still valid signed table entries and flow through the same RF-to-MAC conversion and final min caps.
- The 2 GHz RU table includes `RTW89_WW` defaults for all 14 channel indexes, then regional overrides for ETSI/FCC/MKK/IC/KCC/ACMA/CN/UK/MEXICO/UKRAINE/CHILE/QATAR/THAILAND where needed.
- The 5 GHz RU table visible here covers lower and middle channel-index ranges and regulatory domains including WW defaults plus FCC/ETSI/MKK/IC/KCC/ACMA/CN/UK/MEXICO/UKRAINE/CHILE/QATAR/THAILAND. The table continues after line 49275.

## Dependencies and Integration Points

- Depends on `core.h` constants for channel counts, RU indexes, regulatory-domain indexes, NTX count, 6 GHz power-mode count, and bandwidth counts. Reordering enum values would silently remap regulatory limits, which is why the regulation enum warns not to insert values in the middle.
- Integrated into 8852C default parameters at the bottom of `rtw8852c_table.c` through `rtw89_8852c_dflt_parms`.
- Consumed by common AX PHY power code in `phy.c`, especially `rtw89_phy_read_txpwr_limit()`, `rtw89_phy_read_txpwr_limit_ru()`, `rtw89_phy_fill_txpwr_limit_ru_ax()`, and `rtw89_phy_set_txpwr_limit_ru_ax()`.
- May be superseded by firmware RFE tables loaded in `fw.c` when firmware-provided `lmt_ru_*ghz`, `da_lmt_ru_*ghz`, or related configs validate. In that case the same pointer contract is used, but data comes from `struct rtw89_rfe_data`.
- Debug visibility is through the tx-power debug mappings in `debug.c`, which can expose the filled hardware-facing RU limit pages rather than these source initializers directly.

## Risks and Edge Cases

- Table-shape drift is high risk. Any mismatch between `RTW89_*_CH_NUM`, `RTW89_RU_NUM`, `RTW89_REGD_NUM`, or 6 GHz power-mode enum values and the generated initializer indexes can silently change effective transmit limits or fail compilation only for out-of-range indexes.
- `0` means fallback in the lookup code. If regulatory data needs an actual zero limit, this convention can encode the wrong behavior unless the lookup logic changes or another sentinel is used.
- `127` is nonzero and bypasses fallback. If treated as an ordinary high limit, later `min()` operations normally constrain it with SAR/TPE/other caps, but a misplaced `127` in a regulatory row can remove the intended regional restriction.
- Negative values are legal signed `s8` table entries. They should be reviewed carefully at band edges because they can materially reduce or alter programmed power and may interact with RF-to-MAC conversion behavior.
- The chunk boundary cuts through `rtw89_8852c_txpwr_lmt_ru_5g`; whole-file conclusions must merge the next chunk to understand all 5 GHz RU channel indexes and RU categories.
- Regulatory compliance risk is the main behavioral risk. These values directly influence the power limits written to hardware for OFDMA RU transmissions and, for the leading part of the chunk, 6 GHz non-RU transmissions.

## Test Signals

- Build-time signals: compile this driver with `W=1` or normal kernel build to catch out-of-range designated initializers and type-shape mismatches. Existing `BUILD_BUG_ON()` checks in the PHY write path validate hardware page struct sizes, not the regulatory correctness of this source data.
- Runtime debug signals: enable rtw89 TX power debug output and verify `set txpwr limit` / `set txpwr limit ru` messages for expected channel and bandwidth selections, then inspect the debugfs tx-power maps if available.
- Regulatory matrix tests should exercise multiple domains visible in this chunk: WW fallback, FCC/IC/CHILE restricted negative or low entries, ETSI/UK/QATAR low 5 GHz ranges, CN-specific 5 GHz rows, and KCC/MKK special cases.
- Boundary tests should cover 2.4 GHz channels 12-14, 5 GHz lower/mid channels around indexes 0, 15, 37, and 48 where many sentinel transitions appear, and 6 GHz channel indexes around 75-119 from the visible 6 GHz tail.
- Firmware override tests should confirm that valid RFE data replaces these defaults and invalid firmware entries are rejected by the `fw_txpwr_lmt_ru_*ghz_entry_valid()` validators before pointer reassignment.

## Cross-Chunk Notes

- This chunk starts inside `rtw89_8852c_txpwr_lmt_6g`, whose declaration and earlier bandwidth/regulatory data are in previous chunks.
- `rtw89_8852c_txpwr_lmt_ru_5g` continues beyond line 49275 and must be reconciled with later chunk research before producing the final per-file report.
- `rtw89_8852c_txpwr_lmt_ru_6g` begins later at line 49772 and is outside this chunk.
