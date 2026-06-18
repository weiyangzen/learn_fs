# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.h

Purpose: declares brcmsmac channel manager APIs and regulatory power flag constants.

Important APIs and constants: `BRCMS_TXPWR_DB_FACTOR` converts dB to quarter-dB units. Locale flags describe peak/EIRP/DFS/no-OFDM/no-40MHz/no-MIMO/radar policy. Exports channel manager attach/detach, chanspec validation, regulatory limit calculation, chanspec setting, and regulatory initialization.

Control flow: no implementation, but callers use attach during driver setup, call `brcms_c_regd_init()` after wiphy/channel tables exist, validate chanspecs before programming, and call set/reg-limits during channel changes.

State and persistence: hides `struct brcms_cm_info` implementation. Hardware and cfg80211 state are changed by the functions declared here.

Dependencies and integration: used by brcmsmac main and PHY/channel programming code; interacts with `struct txpwr_limits`.

Risks and test signals: unit conversion mistakes at call sites can over/under-limit transmit power. Tests should compare expected qdBm values and validate that callers handle false chanspec validation results.
