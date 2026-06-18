# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_wifi.h

Purpose: Defines common Broadcom Wi-Fi channel, bandwidth, band, rate, MCS, security, and 802.11 constants plus channel helper macros.

Important APIs/constants: Includes 2G/5G channel ranges, channel spacing offsets, chanspec masks and testers, `CHSPEC_CTL_CHAN`, `CHSPEC2BAND`, sideband helpers, `ch20mhz_chspec()`, next-channel helpers, legacy rate constants in 500 kbps units, `MCSSET_LEN`, WEP/TKIP/AES/MFP/WPA/WPA2/WPA3 bit definitions, default RTS/fragment sizes, IV/header lengths, and HT RX STBC values.

Control flow and state: Header-only inline helpers compute lower/upper sidebands, band unit, 20 MHz chanspec, and next 20 MHz channel. It carries no state but standardizes encoded channel/rate/security values across modules.

Dependencies and integration: Includes Ethernet and IEEE80211 headers for address and PMKID/cipher context. Used by rate, channel, chanspec conversion, security, and driver configuration paths. Risks include legacy chanspec format divergence from D11AC-specific formats, `CHSPEC_CTL_CHAN` using lower/upper helpers even for no-sideband cases, fixed max channel assumptions, and stale security constants. Test signals include chanspec helper tests, rate table consumers, WPA/WPA2/WPA3 configuration mapping, and 2G/5G boundary behavior.
