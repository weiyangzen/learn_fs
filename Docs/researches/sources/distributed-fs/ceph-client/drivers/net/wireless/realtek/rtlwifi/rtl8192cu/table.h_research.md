
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.h

Purpose: Declares the RTL8192CU static hardware table arrays and their expected lengths.

Important APIs/data: Provides length macros and `extern u32` declarations for 2T/1T PHY arrays, PHY power-group arrays, RadioA/RadioB arrays, MAC array, AGC arrays, and high-power 1T/PG/RadioA/AGC variants. Includes `<linux/types.h>` for `u32`.

Control flow: Header only. The length macros drive loops in `phy.c` and table assignment in `hw.c`.

State and persistence: No direct state. The declarations expose static calibration payload stored in `table.c` and later persisted into hardware registers by replay.

Dependencies/integration: Included by `hw.c`, `phy.c`, `rf.c`, and `table.c`. The `rtlphy->hwparam_tables` indexes are assigned using these length/data pairs.

Risks: Mismatched length macros versus actual array initializers can cause truncated configuration or out-of-bounds reads. The guard macro name has a double underscore style and unusual spelling (`__RTL92CU_TABLE__H_`) but is internally consistent.

Test signals: Compile-time symbol resolution, optional static assertions if added, and init trace confirming each length is consumed with the correct pair/triple stride.
