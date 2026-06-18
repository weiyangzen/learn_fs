# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/dm.h

## Purpose
This header defines the dynamic-management contract for the RTL8821AE/RTL8812AE driver. It provides register aliases, threshold constants, table sizes, mode enums, bit masks, and function prototypes used by `dm.c` and by neighboring PHY/FW/TX code that needs dynamic management services.

The header is mostly declarative, but it encodes important hardware policy: which RF/BB/MAC registers dynamic management may touch, what RSSI/false-alarm/thermal thresholds shape control loops, what power-tracking methods exist, and which exported functions other driver units may call.

## Important APIs, Types, And Functions
Register macros are grouped by RF, BB, and MAC pages. Examples include RF thermal/channel registers (`DM_REG_T_METER_11N`, `DM_REG_CHNBW_11N`), DIG/CCA registers (`DM_REG_IGI_A_11AC`, `DM_REG_IGI_B_11AC`, `DM_REG_CCK_CCA_11AC`), false-alarm counters and reset registers, TXAGC/TXIQK/RXIQK registers, EDCA registers, antenna selection registers, and RSSI monitor registers.

Control constants include table lengths (`TXSCALE_TABLE_SIZE`, `OFDM_TABLE_SIZE`, `CCK_TABLE_SIZE`), DIG false-alarm thresholds (`DM_DIG_FA_TH0/1/2`), rate-adaptation states (`DM_RATR_STA_*`), high-power and near-field thresholds, TX power tracking limits, dynamic ATC/CFO thresholds, thermal averaging sizes, and per-chip RF path counts (`MAX_PATH_NUM_8812A`, `MAX_PATH_NUM_8821A`).

Enums include dynamic initial gain operation types, CCA/RF save states, software antenna switch values, and `enum pwr_track_control_method` with `BBSWING`, `TXAGC`, and `MIX_MODE`. The public function prototypes expose DM init/watchdog, DIG/CCA writes, EDCA and RA init, thermal tracking, TX-power set/adjust helpers, rate conversion, C2H rate update support, and descriptor antenna selection.

## Control Flow
This file has no executable flow, but it defines the legal calls used by the runtime flow. Driver initialization can call `rtl8821ae_dm_init()`, EDCA/RA init helpers, and thermal-tracking initialization. Periodic work calls `rtl8821ae_dm_watchdog()` and thermal-meter checks. Firmware C2H rate reports can call `rtl8821ae_dm_update_init_rate()`. PHY or calibration code can call the chip-specific TX-power tracking callbacks and power-set helpers.

The register constants in this header let `dm.c` isolate chip-control logic from raw numeric addresses. They also preserve Realtek naming from older 11n/11ac code paths, which explains the mixed `11N` and `11AC` suffixes even in RTL8821AE code.

## State And Persistence
The header does not allocate state. It defines bit positions and constants that shape state stored elsewhere: `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, efuse fields, and hardware registers. Macros such as `GET_UNDECORATED_AVERAGE_RSSI()` select which RSSI state is authoritative depending on opmode.

Because the constants are compiled into the driver, changes here persist as driver behavior changes across all callers. Incorrect register aliases or threshold values would directly alter hardware programming at runtime.

## Dependencies And Integration Points
`dm.h` is included by `dm.c`, `fw.c`, and other RTL8821AE source files that need DM function prototypes or shared constants. It assumes kernel bit macros such as `BIT`, `GENMASK`, and `BIT_OFFSET_LEN_MASK_32`, mac80211 opmode definitions, and Realtek shared structures from included rtlwifi headers. The function declarations bind this header to `phy.c` calibration APIs, `fw.c` H2C/C2H interactions, and descriptor code in `trx.h`.

The constants also mirror hardware documentation and shared Realtek ODM code conventions. A maintenance change must consider both RTL8821AE one-path and RTL8812AE two-path behavior because one header serves both branches.

## Risks
Header risk is primarily semantic drift. Many register names carry `11N` suffixes while the code programs 11ac hardware paths; changing aliases without verifying call sites can misprogram BB/RF state. Threshold constants are magic hardware-policy values, so apparent cleanups can shift control-loop stability. `MAX_PATH_NUM_8821A` and `MAX_PATH_NUM_8812A` guard loops in `dm.c`; wrong values can cause missed path updates or out-of-bounds state access.

Macro APIs write through raw pointers and assume byte-array command buffers or valid `struct rtl_priv` pointers. `GET_UNDECORATED_AVERAGE_RSSI()` casts its argument and dereferences nested fields, so it is not type-safe. Duplicated constants and old naming also increase the chance that future chip support reuses an incompatible address or threshold.

## Test Signals
Compile coverage is the first signal because this header defines exported prototypes and macro dependencies. Runtime signals should focus on every feature using these constants: DIG register writes, false-alarm counter reads/resets, CCK CCA thresholds, EDCA BE programming, TX power tracking table bounds, thermal meter access, CFO crystal-cap adjustment, and antenna selection. Static analysis should flag unsafe macro use, path-count loops, and any mismatch between declared prototypes and `dm.c` implementations.
