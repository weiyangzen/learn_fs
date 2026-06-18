<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h

Purpose: version-adaptive helpers for Debug Host Command response packets.

Important APIs/functions: `iwl_dhc_resp_status()` returns the status field from either `struct iwl_dhc_cmd_resp` or legacy `struct iwl_dhc_cmd_resp_v1`; `iwl_dhc_resp_data()` returns a pointer to the response payload and stores its length. Both select the layout by checking the `DEBUG_HOST_COMMAND` notification version through `iwl_fw_lookup_notif_ver()`.

Control flow: each helper branches on notification version >= 2, validates `iwl_rx_packet_payload_len(pkt)` against the selected response header, then returns the status or payload. Short packets return `(u32)-1` or `ERR_PTR(-EINVAL)`.

State and persistence: stateless inline utilities; they only inspect firmware capability tables and packet bytes.

Dependencies/integration: depends on `fw/img.h` for command-version lookup, `api/commands.h`, `api/dhc.h`, and RX packet helpers. Callers using DHC can avoid duplicating version parsing.

Risks/test signals: packet length validation and version defaults are the main risks. Test both v1 and v2 notification layouts, empty/short responses, non-default firmware version tables, and callers that propagate `ERR_PTR()` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h -->
