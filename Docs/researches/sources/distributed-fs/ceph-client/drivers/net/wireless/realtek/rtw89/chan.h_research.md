# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.h

## Purpose
Declares the channel-context, multi-role, pause/proceed, and MCC public interface for `rtw89`. It also centralizes MCC timing constants, role classification enums, and small entity-mode accessors used across core, firmware, PHY, SAR, coexistence, RFK, and mac80211 integration code.

## Important APIs, Types, and Functions
The header defines MCC timing constants such as prepare delay, MCC work delay, trigger times, early beacon margins, minimum role durations, switch-channel time, probe limits, group rotation, null-data lead time, and courtesy slot defaults. Multi-role classification types are `enum rtw89_mr_wtype`, `enum rtw89_mr_wmode`, and `enum rtw89_mr_ctxtype`, returned in `struct rtw89_mr_chanctx_info`. Pause and callback parameters are `struct rtw89_chanctx_pause_parm` and `struct rtw89_chanctx_cb_parm`; `struct rtw89_entity_weight` summarizes recalculation inputs; `struct rtw89_mcc_links_info` exposes MCC role links. Inline helpers read and write `hal->entity_active[]` and `hal->entity_mode` with `READ_ONCE`/`WRITE_ONCE`. Function declarations cover channel creation, entity assignment/iteration, chandef and ROC configuration, entity recalc, channel work queueing, management channel lookup, MCC helpers, and mac80211 chanctx operation wrappers.

## Control Flow
The header defines the callable stages implemented in `chan.c`: initialize entity state, add/configure chanctx definitions, assign links, recalculate entity mode, queue delayed channel-context work, pause MCC for scans/ROC/beacon recovery, proceed and optionally invoke a callback after `rtw89_set_channel()`, query multi-role topology, track MCC drift, and add/remove/change/reassign mac80211 chanctxs. The `RTW89_MCC_REQ_COURTESY()` macro is used during MCC pattern assignment to decide when firmware courtesy slots are required because a role has too little time before or after beacon reception.

## State and Persistence Behavior
No state is stored in the header, but it exposes accessors and interfaces for persistent `rtwdev->hal` and `rtwdev->mcc` state. The constants here shape persisted scheduling decisions such as role duration floors, beacon detection retries, group rotation, queue dwell times, and courtesy behavior. Inline state accessors deliberately use one-copy atomic reads/writes because entity mode and active flags are consulted from multiple paths.

## Dependencies and Integration Points
Includes `core.h` for all central driver types. Consumers include mac80211 callback wrappers, core channel setup, firmware C2H/H2C paths, PHY/RFK channel users, coexistence, SAR channel-context listeners, power-save code, hardware scan/ROC paths, and chip-specific channel listener tables. The exported `rtw89_mgnt_chan_get()` macro records the caller function name for debug fallback diagnostics.

## Risks
Timing constants are policy, not just documentation. Changing minimum durations, trigger times, or work delays can destabilize MCC beacon reception, queue wake timing, P2P NoA alignment, and BT coexistence. Role classification enums must stay aligned with diagnostic and firmware consumers. The pause/proceed callback contract is subtle: callbacks run after channel programming and before restarting entity scheduling when paused. Management channel fallback can hide invalid link indexes unless callers use the `_or_null` variant.

## Test Signals
Compile coverage across all rtw89 chips, channel-context add/remove/assign/reassign paths, MCC start/update/stop timing, hardware scan and ROC pause/proceed, multi-role classification queries for non-MLD and MLD topologies, BE MRC versus legacy MCC operation, BT coexistence slot changes, GC beacon-loss retries, and SAR/RFK listeners that consume channel-context state are the key signals.
