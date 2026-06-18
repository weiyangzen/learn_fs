<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h

Purpose: Defines the shared ath nl80211 testmode interface version, maximum payload sizes, attributes, and command IDs.

Important APIs/types/functions: Defines `ATH_TESTMODE_VERSION_MAJOR`, `ATH_TESTMODE_VERSION_MINOR`, `ATH_TM_DATA_MAX_LEN`, `ATH_FTM_EVENT_MAX_BUF_LENGTH`, `enum ath_tm_attr`, and `enum ath_tm_cmd`.

Control flow: No executable flow; driver testmode handlers parse attributes and commands according to these enums.

State and persistence: Constants only; version numbers are the compatibility contract with userspace tools.

Dependencies and integration points: Used by ath drivers with nl80211 testmode support for GET_VERSION, WMI command passthrough, UTF firmware start, and FTM WMI traffic.

Risks and test signals: Risks include incompatible interface changes without version bump, payload size mismatches, and command/attribute drift with userspace tooling. Test signals are nl80211 testmode GET_VERSION and WMI/FTM command round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/testmode_i.h -->
