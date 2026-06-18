# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.h

## Purpose
`phy.h` declares the shared PHY API, rate-section tables, PHY table declaration macros, RFE validation helpers, TX power data structures, CCK packet-detection levels, register masks, RF read constants, and power-tracking helpers used by core, chip-specific PHY files, firmware/RX code, and debug paths.

## Important APIs, Types, and Functions
- Extern rate arrays and `rtw_rate_section[]`/`rtw_rate_size[]` used by TX power and rate-section logic.
- Initialization/runtime declarations: `rtw_phy_init()`, `rtw_phy_dynamic_mechanism()`, DIG helpers, EDCCA/adaptivity helpers, CFO parsing, and TX path diversity.
- RF access declarations for direct, SIPI, and mixed RF register operations.
- Table parser/config declarations for conditional PHY tables, BB power-group tables, TX power limit tables, and MAC/AGC/BB/RF config callbacks.
- TX power declarations: `rtw_phy_init_tx_power()`, `rtw_phy_load_tables()`, `rtw_phy_get_tx_power_index()`, `rtw_phy_set_tx_power_level()`, by-rate/limit config, `struct rtw_power_params`, and `rtw_get_tx_power_params()`.
- Power tracking declarations: swing table config, thermal average/change/delta helpers, power index helper, and LCK/IQK trigger predicates.
- Table macros: `RTW_DECL_TABLE_PHY_COND_CORE`, `RTW_DECL_TABLE_PHY_COND`, `RTW_DECL_TABLE_RF_RADIO`, `RTW_DECL_TABLE_BB_PG`, and `RTW_DECL_TABLE_TXPWR_LMT`.
- RFE helpers: `rtw_get_rfe_def()` and `rtw_check_supported_rfe()`.

## Control Flow
Chip-specific table files use the declaration macros to build `struct rtw_table` objects with parser and configuration callbacks. Core chip setup calls `rtw_check_supported_rfe()` before board setup, then loads PHY PG and TX power limit tables. MAC/PHY initialization later calls `rtw_phy_load_tables()` and `rtw_phy_init()`. Runtime watchdog and scan paths call the dynamic/DIG APIs declared here. RX code can call `rtw_phy_parsing_cfo()` after descriptor parsing.

## State and Persistence Behavior
The header itself stores no state, but its APIs operate on `struct rtw_dev` state from `main.h`: `rtw_hal` power arrays, `rtw_dm_info` dynamic mechanism fields, efuse power/thermal values, SAR config, and chip table pointers. The RFE inline helper logs and returns an RFE table pointer based on `efuse.rfe_option`; unsupported RFE detection is an early persistent device setup gate.

## Dependencies and Integration Points
`phy.h` includes `debug.h`, which brings in driver logging and the core types needed by declarations. It integrates with chip-specific generated table files, regulatory/SAR code, RX PHY status parsing, firmware adaptivity support, and core channel/power setup. Register mask constants are shared by low-level BB/RF configuration and chip-specific code.

## Risks
- Duplicate mask definitions must stay compatible with other register headers.
- Table declaration macros encode parser choice at compile time; using the wrong macro silently sends data to the wrong parser/config path.
- `rtw_get_rfe_def()` returns NULL when no RFE table exists or the efuse option is out of range; callers must validate before dereferencing.
- TX power helper prototypes expose many raw `u8` indexes, so callers must pass valid path/rate/bandwidth/channel/regulatory values.

## Test Signals
- Build coverage for all chip-specific table declaration macros.
- Unsupported RFE probe failure with clear error logs.
- Unit-style or trace validation of TX power helper inputs and outputs.
- Runtime scan/channel/rate/power-tracking paths invoking the declared APIs without NULL table or callback dereferences.
