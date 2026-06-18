<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h` declares 802.11n HT capability state, AMPDU/AMSDU settings, bandwidth/channel offset helpers, and HT IE manipulation routines. The source was reviewed as a complete 83-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct ht_priv`, `struct ht_caps_element`, `rtw_set_ht_cap`, `rtw_ht_use_default_setting`, `rtw_restructure_ht_ie`, `rtw_update_ht_cap`, `rtw_issue_addbareq_cmd`, and bandwidth/short-GI related fields.

## Control Flow

During scan/join/AP setup, HT IEs are parsed or generated, adapter HT defaults are applied, and aggregation setup can issue ADDBA commands once a link supports HT.

## State and Persistence Behavior

`ht_priv` persists per adapter/station and records HT enablement, AMPDU density/factor, bandwidth mode, short GI, STBC/LDPC, and MCS capabilities.

## Dependencies and Integration Points

Used by `rtw_mlme.h`, `sta_info.h`, `rtw_recv.h`, `rtw_xmit.h`, and PHY bandwidth/rate-control code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

HT capability negotiation affects descriptor bandwidth/rate bits and reorder buffering; mismatched IEs can break interoperability or aggregation.

## Test Signals

Join APs with/without HT, 20/40 MHz operation, ADDBA setup/teardown, short-GI rates, and interoperability with legacy B/G clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_ht.h -->
