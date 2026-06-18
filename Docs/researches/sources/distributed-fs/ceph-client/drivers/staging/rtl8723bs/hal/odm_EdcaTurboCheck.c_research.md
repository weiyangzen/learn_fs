# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_EdcaTurboCheck.c

## Purpose

`odm_EdcaTurboCheck.c` implements EDCA turbo tuning for best-effort traffic. It selects uplink or downlink BE EDCA parameters based on traffic direction, wireless mode, and AP vendor interoperability quirks. The source was read as a complete 158-line file.

## Important APIs, Types, and Functions

The public functions are `ODM_EdcaTurboInit`, `odm_EdcaTurboCheck`, and `odm_EdcaTurboCheckCE`. Static tables `edca_setting_DL_GMode`, `edca_setting_UL`, and `edca_setting_DL` provide vendor-specific EDCA values indexed by `HT_IOT_PEER_*`.

## Control Flow

Initialization clears current turbo state and non-BE packet tracking. The watchdog-facing `odm_EdcaTurboCheck` returns unless `ODM_MAC_EDCA_TURBO` is enabled, then calls the CE implementation. The CE implementation exits when unlinked, Wi-Fi spec mode is enabled, or AP vendor is invalid. If non-BE packets are absent, it compares current TX/RX byte counts to choose uplink or downlink, applies vendor/mode-specific EDCA overrides, writes `REG_EDCA_BE_PARAM`, and records turbo state. If conditions later require disabling turbo, it restores `hal_com_data->AcParam_BE`.

## State and Persistence Behavior

State lives in `dm_odm_t->DM_EDCA_Table`, `adapter->recvpriv.bIsAnyNonBEPkts`, `dvobj_priv->traffic_stat`, and the hardware EDCA BE register. The previous traffic index persists for diagnostics but is not heavily used in this snapshot.

## Dependencies and Integration Points

It depends on MLME association vendor detection, registry `wifi_spec`, traffic counters, recv non-BE tracking, `hal_com_data->AcParam_BE`, and MAC register writes. It is called from `ODM_DMWatchdog`.

## Risks and Edge Cases

`bbtchange` and `biasonrx` are local constants set false, reducing intended dynamic behavior. Turbo is skipped entirely in `wifi_spec` mode. Vendor table indices must match `HT_IOT_PEER_*`. If non-BE packet state is not maintained accurately elsewhere, BE EDCA may remain too aggressive or be restored too soon.

## Test Signals

Tests should cover unlinked and `wifi_spec` exits, invalid vendor exit, uplink/downlink traffic selection, Cisco/Airgo/Marvell/Atheros overrides, restore of `AcParam_BE`, and non-BE packet suppression.
