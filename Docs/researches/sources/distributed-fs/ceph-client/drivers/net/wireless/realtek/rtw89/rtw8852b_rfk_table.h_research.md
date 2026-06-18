# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk_table.h

Purpose: Declares the external RFK table symbols exported by `rtw8852b_rfk_table.c` for RTL8852B calibration code. It is the linkage contract between table definitions and `rtw8852b_rfk.c`, allowing calibration helpers to select named `struct rtw89_rfk_tbl` sequences without exposing the private `struct rtw89_reg5_def` arrays.

Important APIs and types: The header includes `phy.h` for `struct rtw89_rfk_tbl` and declares `extern const struct rtw89_rfk_tbl` objects. The declarations cover AFE initialization, ADDC/DADC enable/disable checks, DACK stage tables for RF paths A and B, DPK AFE setup/restore and KIP setup, TSSI common system configuration, per-path 2 GHz/5 GHz system tables, TX power initialization, HE TB power initialization, TSSI DCK, DAC gain tables, path/band slope tables, channel-range alignment tables, and final TSSI slope enable tables.

Control flow: The header has no executable logic, but its declarations define the names available to the RFK control flow. `rtw8852b_rfk.c` binds these symbols into ordered calibration flows by passing addresses such as `&rtw8852b_tssi_align_a_5g2_all_defs_tbl` to `rtw89_rfk_parser()`. Conditional selection is done outside the header based on RF path, current band, channel range, and whether the full or partial alignment sequence is needed.

State and persistence: No mutable state is declared. The `const` table objects refer to immutable arrays in the C file, but parsing those objects produces persistent hardware register state. The header therefore participates in hardware state transitions indirectly through symbol exposure.

Dependencies and integration points: Depends on `phy.h`, which in turn provides the RFK table type and parser prototype. Included by `rtw8852b_rfk_table.c` for definition consistency and by `rtw8852b_rfk.c` for consumption. The symbol list must stay synchronized with every `RTW89_DECLARE_RFK_TBL()` in the C file and with every direct table reference in RTL8852B RFK logic.

Risks: Missing, misspelled, or stale declarations cause compile/link failures for consumers. More subtle risk comes from declaring a table that is no longer selected or failing to declare a new table, which can leave intended hardware programming unreachable. Because all declarations share the same opaque type, the compiler cannot detect semantic mixups such as using a path B table in a path A flow or a 5 GHz alignment table for 2 GHz operation.

Test signals: Normal kernel/module build catches symbol and type mismatches. Grep or static checks comparing `extern` declarations against `RTW89_DECLARE_RFK_TBL()` definitions catch dead or missing declarations. Runtime coverage should exercise each consumer path: AFE init, DACK on both paths, DPK setup/restore, and TSSI setup across path A/path B and 2 GHz/5 GHz channel groups.
