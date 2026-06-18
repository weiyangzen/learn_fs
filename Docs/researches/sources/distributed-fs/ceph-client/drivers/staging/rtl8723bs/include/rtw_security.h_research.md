<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h` defines security algorithms, authentication modes, key storage, PMKID cache, IV/PN helpers, MIC state, and software crypto entry points for WEP, TKIP, AES/CCMP, and BIP verification. The source was reviewed as a complete 272-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct security_priv`, `struct rt_pmkid_list`, `struct mic_data`, `security_type_str`, `GET_ENCRY_ALGO`, `SET_ICE_IV_LEN`, `GET_TKIP_PN`, `omac1_aes_128`, `rtw_secmicsetkey`, `rtw_secgetmic`, `rtw_aes_encrypt`, `rtw_tkip_encrypt`, `rtw_wep_encrypt`, `rtw_aes_decrypt`, `rtw_tkip_decrypt`, `rtw_wep_decrypt`, `rtw_BIP_verify`, and `rtw_handle_tkip_countermeasure`.

## Control Flow

Configuration paths populate auth/cipher/key state; TX/RX paths choose the active algorithm, build/parse IVs, perform software crypto where needed, verify MIC/BIP, and handle TKIP countermeasures.

## State and Persistence Behavior

`security_priv` persists keys, key IDs, cipher/auth modes, PMKID cache, WPS/association IEs, TKIP PN counters, ARC4 contexts, and join-time security BSS data.

## Dependencies and Integration Points

Includes Linux `crypto/arc4.h`; integrates with MLME, ioctl/cfg80211, command key setting, transmit descriptors, and receive decrypt paths. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Security code is high risk: key bounds, PN/replay handling, MIC failure behavior, and IE lengths must be correct. Legacy WEP/TKIP support expands attack surface.

## Test Signals

WEP/TKIP/CCMP association, software encrypt/decrypt known vectors, replay/MIC failure handling, PMKID cache behavior, malformed security IE parsing, and BIP verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_security.h -->
