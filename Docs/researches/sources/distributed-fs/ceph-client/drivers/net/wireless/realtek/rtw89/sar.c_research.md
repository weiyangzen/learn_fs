# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.c

Purpose: implements rtw89 SAR and TAS power limiting. It accepts cfg80211 SAR limits, imports ACPI SAR tables, converts power units into MAC TX-power units, and dynamically adjusts SAR through TAS based on measured transmit duty/power.

Important APIs/functions: `rtw89_query_sar()` is the main exported query path used by TX-power programming. `rtw89_ops_set_sar_specs()` is the cfg80211 set-SAR hook. `rtw89_sar_init()` loads ACPI SAR and TAS policy. `rtw89_sar_track()` periodically refreshes dynamic ACPI table selection and TAS state. `rtw89_tas_reset()`, `rtw89_tas_scan()`, `rtw89_tas_chanctx_cb()`, and `rtw89_tas_fw_timer_enable()` integrate TAS with channel, scan, MCC, and firmware timer flows.

Control flow: common SAR maps center frequencies into 2/5/6 GHz SAR subbands, handles 6 GHz spanning channels through `rtw89_get_6ghz_span()`, and chooses the minimum configured limit for spanning ranges. ACPI SAR selects a table per RF path from ACPI indicators, chooses regulation-domain entries, optionally returns path-specific values, and downgrades 2TX. Query-time TAS may add or subtract offsets for DPR off/on before conversion to MAC units.

State and persistence: `rtwdev->sar` stores active source and config; common SAR has priority over ACPI. `rtwdev->tas` stores rolling power history, ratios, thresholds, current/backup state, pause/block flags, and ACPI country policy. State is in-memory only and protected by the wiphy lock after probe.

Dependencies/integration: depends on ACPI helpers, regulatory lookup, channel context, firmware H2C TAS trigger, environment monitor TX ratio, and `rtw89_core_set_chip_txpwr()`.

Risks: incorrect unit shifts or subband mapping can over/under-limit RF power. TAS disables itself for MLD, and dynamic ACPI failure resets table selection. Rolling-average division assumes a nonzero window after reset.

Test signals: SAR debug output, cfg80211 SAR setting paths, ACPI SAR table logs, TAS debug state transitions, TX-power recalculation after SAR/TAS changes, and regulatory/channel boundary tests around 6 GHz spans.
