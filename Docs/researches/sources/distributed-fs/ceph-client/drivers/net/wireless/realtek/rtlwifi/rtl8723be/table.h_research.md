<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h

## Purpose
Declares the RTL8723BE vendor initialization table arrays and their length symbols for MAC, PHY, RF, AGC, and power-group programming.

## Important APIs, Types, And Functions
- Extern declarations for `RTL8723BEPHY_REG_1TARRAY`, `RTL8723BEPHY_REG_ARRAY_PG`, `RTL8723BE_RADIOA_1TARRAY`, `RTL8723BEMAC_1T_ARRAY`, and `RTL8723BEAGCTAB_1TARRAY`.
- Extern declarations for the matching `*_ARRAYLEN` symbols.
- Includes `<linux/types.h>` for `u32`.

## Control Flow
The header has no control flow. It exposes table data from `table.c` to chip initialization code.

## State And Persistence
The declarations reference static module arrays whose values are applied to hardware registers during initialization. The header itself stores no state.

## Dependencies And Integration Points
Included by `table.c`, `sw.c`, and PHY/hardware table-loading code. It is part of the boundary between opaque vendor register tables and the code that interprets them.

## Risks And Edge Cases
Signature or symbol-name changes break table loading at compile or link time. Missing length declarations can cause consumers to use stale sizes or hard-coded lengths. The arrays are mutable declarations, so accidental writes by future code would corrupt subsequent initialization.

## Test Signals
Compile/link success for RTL8723BE, successful PHY/RF/MAC initialization, and no unresolved symbols for table arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.h -->
