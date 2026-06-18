# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_common.c

Purpose: this file provides common iavf hardware/AdminQ helpers: status stringification, AdminQ debug dumps, ASQ liveness checks, queue shutdown command, RSS LUT/key AQ commands, VF-to-PF virtchnl message sending, and parsing PF-provided VF resources into the hardware struct.

Important APIs/functions: exported functions include `iavf_stat_str`, `iavf_debug_aq`, `iavf_check_asq_alive`, `iavf_aq_queue_shutdown`, `iavf_aq_set_rss_lut`, `iavf_aq_set_rss_key`, `iavf_aq_send_msg_to_pf`, and `iavf_vf_parse_hw_config`. Internal helpers implement get/set RSS LUT/key command preparation.

Control flow: RSS helpers build AQ descriptors for get/set RSS LUT or key, mark them as indirect buffer commands with read flags, encode VSI id and table type using bitfield macros, and send through `iavf_asq_send_command`. `iavf_aq_send_msg_to_pf` builds the virtualization mailbox command, stores virtchnl opcode/status in descriptor cookies, marks indirect buffer flags when a payload exists, defaults to async send, and relies on AdminQ completion/event handling later. Resource parsing copies PF-reported queue/vector counts, DCB flag, and default MAC addresses from SR-IOV VSI resources into `hw`.

State and persistence: the file reads and updates `hw->aq.asq_last_status`, uses `hw->debug_mask`, writes `hw->err_str` for unknown status strings, and populates `hw->dev_caps` and `hw->mac` from PF resource messages. RSS key/LUT data is supplied by callers and programmed through PF/FW rather than stored here.

Dependencies and integration: it depends on virtchnl, bitfield helpers, iavf type/AdminQ/prototype headers, AdminQ command definitions, and `libie_aq_desc`. It is used by VF initialization, RSS configuration, shutdown/remove, and all VF-to-PF messaging paths.

Risks and test signals: debug dumps can expose command buffers in logs when masks are enabled. Async mailbox send means callers must handle later completion and PF communication failures. Resource parsing assumes at least one VSI resource and that SR-IOV VSI carries the permanent/default MAC. Tests should cover status-string mapping, AQ debug gated by mask, RSS key/LUT AQ command encoding, queue shutdown on unload, mailbox send with empty/large payloads, and parsing resource messages with multiple VSIs.
