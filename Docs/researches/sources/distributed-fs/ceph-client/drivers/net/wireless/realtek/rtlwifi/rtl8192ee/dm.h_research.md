# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.h

Purpose: Defines RTL8192EE dynamic-management register addresses, thresholds, states, RSSI dump registers, and exported DM functions.

Important APIs/definitions: Names RF/BB/MAC registers used by DM; defines DIG thresholds, primary CCA states, rate-adaptive states, ATC/CFO thresholds, TX power tracking constants, and RSSI/CFO dump registers. Declares DM init/watchdog, DIG/CCA writers, EDCA/rate-adaptive init, and ARFB selection.

Control flow/integration: Implemented by `dm.c`; `fw.c` calls ARFB selection from C2H RA reports; hardware setup and rtlwifi watchdog use init/watchdog.

State and persistence: Header is stateless; constants map to hardware registers and state fields mutated by `dm.c`.

Dependencies: Requires rtlwifi/mac80211 types and bit macros from including files.

Risks/test signals: Wrong register addresses or thresholds can destabilize gain, CCA, CFO, and rate adaptation. Build plus runtime DM traces/register observations validate behavior.
