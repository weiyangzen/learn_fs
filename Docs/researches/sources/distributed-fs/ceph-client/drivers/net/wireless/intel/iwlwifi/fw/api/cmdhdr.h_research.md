# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/cmdhdr.h

Purpose: Defines host-command header formats, command ID packing helpers, sequence-number queue/index extraction, generic command response, and calibration PHY database payload structures.

Important APIs and types: `SEQ_TO_QUEUE()`, `QUEUE_TO_SEQ()`, `SEQ_TO_INDEX()`, and `INDEX_TO_SEQ()` encode/decode driver sequence values. `iwl_cmd_opcode()`, `iwl_cmd_groupid()`, `iwl_cmd_version()`, and `iwl_cmd_id()` pack/unpack wide command IDs. `struct iwl_cmd_header` is the short header; `struct iwl_cmd_header_wide` adds length and version. `struct iwl_calib_res_notif_phy_db`, `iwl_phy_db_cmd`, and `iwl_cmd_response` define common payloads.

Control flow: Inline helpers are used when building host commands, routing responses, and reclaiming TX frames from sequence fields.

State and persistence: Header owns no state. Sequence values carry transient TX queue/index and unsolicited notification bits across firmware responses.

Dependencies and integration points: Central to transport, DVM TX completion, firmware notification dispatch, calibration PHY database setup, and all command group APIs.

Risks: Bitfield macros assume queue IDs fit five bits and TFD indices fit eight bits. Short vs wide command headers must match firmware group/version negotiation. `SEQ_RX_FRAME` bit distinguishes unsolicited notifications and direct responses.

Test signals: Command ID round trips, queue/index sequence round trips, unsolicited notification dispatch, wide-header command submission, calibration PHY DB variable-length payloads, and generic response status parsing.
