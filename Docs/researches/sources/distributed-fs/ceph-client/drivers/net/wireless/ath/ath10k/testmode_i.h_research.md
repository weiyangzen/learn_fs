# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode_i.h

Purpose: Defines the internal/userspace ath10k testmode ABI constants, netlink attributes, command numbers, and payload size limits.

Important APIs and types: Exports testmode version `1.0`, `ATH10K_TM_DATA_MAX_LEN`, `ATH_FTM_EVENT_MAX_BUF_LENGTH`, `enum ath10k_tm_attr`, and `enum ath10k_tm_cmd` values for get-version, UTF start/stop, raw WMI, and legacy TLV command mode.

Control flow, state, and persistence: No executable flow. The enum values are userspace ABI, including the intentional alias where `ATH10K_TM_CMD_TLV` shares value zero with get-version and is distinguished by presence of data.

Dependencies and integration points: Consumed by `testmode.c` netlink policy and userspace test tools using nl80211 testmode.

Risks: Changing enum values or versioning rules breaks userspace. The shared command value is subtle and requires parser logic to remain compatible. Payload limits must align with segmentation and event buffer code.

Test signals: Userspace compatibility tests for version reporting, command IDs, max input length enforcement, legacy TLV dispatch, and segmented FTM event buffer limits.
