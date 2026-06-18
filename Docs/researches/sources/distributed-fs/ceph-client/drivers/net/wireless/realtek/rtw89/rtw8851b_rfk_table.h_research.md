# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk_table.h

Purpose: Declares the RTW8851B RFK table symbols exported by `rtw8851b_rfk_table.c`. It is the small ABI between chip-specific calibration logic and the data-only RFK table object.

Important APIs and types: The header includes `phy.h` so consumers see `struct rtw89_rfk_tbl`. It declares 27 `extern const struct rtw89_rfk_tbl` objects: DADCK setup/post, DACK step and manual-off tables, IQK RX clock/TXK/MACBB/AFE restore tables, TSSI system/init/DCK/DAC/slope/alignment/tracking/moving-average tables for path A and 2 GHz or 5 GHz variants, and the NCTL post table. There are no functions, inline helpers, enums, or local data definitions.

Control flow: The header has no executable control flow. It shapes caller control flow by making table symbols available for calls to `rtw89_rfk_parser()` and `rtw89_rfk_parser_by_cond()`. `rtw8851b_rfk.c` uses the declarations directly in DACK, IQK, and TSSI helper phases, while `rtw8851b.c` uses `rtw8851b_nctl_post_defs_tbl` in chip metadata.

State and persistence: The header declares immutable table descriptors only. It creates no state and performs no persistence itself. Persistent effects occur when callers parse the declared tables and write hardware registers.

Dependencies and integration points: Depends on `phy.h` for the RFK table type. Included by `rtw8851b_rfk_table.c`, `rtw8851b_rfk.c`, and `rtw8851b.c`. Its include guard is `__RTW89_8851B_RFK_TABLE_H__`. The declaration names must stay synchronized with `RTW89_DECLARE_RFK_TBL()` invocations in the C file and with all parser call sites.

Risks: This header is mechanically simple but sits on a link-time contract. Removing or renaming a declaration without updating callers breaks compilation or linking. Adding a declaration without a matching C definition creates an unresolved symbol if used. More subtle risk comes from exposing the wrong table to a caller: because every object has the same type, the compiler cannot distinguish DACK, IQK, TSSI, or NCTL phase requirements.

Test signals: Full RTW89 build coverage catches declaration/definition drift. Runtime coverage comes from exercising the calibration paths that include this header: initial RFK, channel RFK, band-change/scan TSSI handling, TSSI tracking, and common NCTL post initialization. Static review should confirm the header remains source-tree-aligned with the C file and does not introduce duplicate definitions.
