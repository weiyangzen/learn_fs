# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/Hal8723BReg.h

## Purpose
`Hal8723BReg.h` is a small register-address definition header for RTL8723B-specific MAC/protocol/EDCA/WMAC registers. It does not implement behavior by itself; it provides symbolic addresses consumed by HAL and coexistence code so register programming can refer to named constants rather than raw offsets.

## Important APIs, Types, And Functions
The header exports only preprocessor constants. Defined addresses include C2H event metadata registers (`REG_C2HEVT_CMD_SEQ_88XX`, `REG_C2HEVT_CMD_LEN_88XX`), beacon/TXDMA control (`REG_DWBCN1_CTRL_8723B`), protocol/rate/aggregation registers (`REG_FWHW_TXQ_CTRL_8723B`, `REG_ARFR0_8723B`, `REG_ARFR1_8723B`, `REG_CCK_CHECK_8723B`, `REG_AMPDU_MAX_TIME_8723B`, `REG_AMPDU_MAX_LENGTH_8723B`, `REG_DATA_SC_8723B`, `REG_MAX_AGGR_NUM_8723B`), EDCA timing (`REG_PIFS_8723B`), and WMAC receive/protocol controls (`REG_RX_PKT_LIMIT_8723B`, `REG_TRXPTCL_CTL_8723B`). There are no types, inline functions, or variables.

## Control Flow
There is no runtime control flow. The include guard `__INC_HAL8723BREG_H` prevents duplicate definitions. Build-time inclusion makes these constants available to C files that perform MMIO through Realtek HAL read/write helpers.

## State, Dependencies, And Integration
The header has no state. Its constants describe hardware state locations; persistence depends entirely on code that writes those registers. The header integrates with RTL8723B HAL implementation files and Bluetooth coexistence code that read or write protocol and aggregation registers. `HalBtc8723b1Ant.c` writes raw offsets such as `0x430`, `0x434`, and `0x456`; those correspond conceptually to rate fallback and AMPDU controls also named here.

## Risks And Test Signals
The main risk is drift between symbolic constants and raw offsets used elsewhere. Incorrect register addresses can cause silent hardware misconfiguration. Build coverage should confirm the header compiles wherever included. Hardware validation should confirm C2H event parsing, ARFR restore, AMPDU max time/length changes, EDCA PIFS, RX packet limit, and protocol control. Static analysis can flag raw constants matching these addresses and suggest replacing them with symbols.
