# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_general.h

Purpose: Defines the general WF200 HIF message header, common request/confirmation/indication IDs, status codes, rate indexes, startup capabilities, generic indications, error/exception payloads, and secure-link state values.

Important APIs and types: `struct wfx_hif_msg` is the common wire header with length, ID, interface, sequence number, encryption bits, and body. General IDs include configuration, GPIO control, secure-link commands, rollback/PTA commands, shutdown, startup/wakeup/generic/error/exception indications. Status macros encode firmware return values. `enum wfx_hif_api_rate_index` maps 802.11b/g/n rates. `struct wfx_hif_ind_startup` carries hardware ID, OPN/UID, input buffer count/size, link/interface counts, MAC addresses, API/firmware versions, secure-link mode, region/channel data, supported rates, and label. Generic indication payloads carry RX test stats and TX power loop info.

Control flow and integration: BH reads/writes messages using this header and sequence counters. Common probe waits for startup indication and copies it into `wdev->hw_caps`. HIF TX uses status values for command return handling. Debugfs and generic indication handlers expose stats/power-loop data. Probe rejects unsupported firmware API and enforced secure-link mode.

State and persistence: Startup capabilities persist in `wdev->hw_caps` and drive buffer credits, max frame size, API compatibility, MAC addresses, regulatory flags, TDLS availability, and operational mode decisions.

Dependencies: Depends on Linux types and Ethernet address length. Included by command and MIB ABI headers.

Risks and test signals: Risks include interpreting little-endian status constants, unsupported encrypted HIF messages, sequence mismatch, startup layout changes, and secure-link modes not implemented by this driver. Tests should cover startup parsing, API major/minor gating, buffer size/count use, firmware error/exception indications, generic stats update, shutdown no-reply behavior, and unknown status reporting.

Test signals: Source read size: 252 lines, 7617 bytes.
