# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_hdcp.h

Purpose: public HDCP module contract for AMD display code. It defines statuses, display/link/config structures, DDC/PSP callback interfaces, adjustment policy, event/output plumbing, query results, and lifecycle/process APIs.

Important APIs/types: `enum mod_hdcp_status` is generated from `MOD_HDCP_STATUS_LIST` and covers generic, topology, DDC, HDCP1, and HDCP2 failures. Core types include `mod_hdcp_display`, `mod_hdcp_link`, `mod_hdcp_config`, `mod_hdcp_output`, `mod_hdcp_trace`, `mod_hdcp_display_query`, and DDC atomic op structures. Public functions include `mod_hdcp_get_memory_size`, `mod_hdcp_setup`, `mod_hdcp_teardown`, `mod_hdcp_add_display`, `mod_hdcp_remove_display`, `mod_hdcp_update_display`, `mod_hdcp_query_display`, `mod_hdcp_reset_connection`, `mod_hdcp_process_event`, and string/signal helpers.

Control flow role: callers allocate one `mod_hdcp` per link, set up DDC/PSP callbacks, add/remove/update displays, and drive the module with callback/watchdog/CPIRQ events. The module returns timer requests through `mod_hdcp_output`.

State and persistence: display slots are bounded by `MAX_NUM_OF_DISPLAYS`. Link adjustments persist retry limits, disable flags, forced content type, stored-KM fallback, H' timeout increase, and locality-check mode. Trace state records error history and downstream counts.

Dependencies and integration: includes OS and signal types and references DC/DDC/PSP concepts without exposing internals. It is the main boundary between display manager policy and HDCP implementation files.

Risks: bitfield widths constrain policy values; exceeding display count or retry assumptions can silently truncate. Function-pointer DDC contracts must be valid for the lifetime of the HDCP object. Status list changes require logging/string updates.

Test signals: API lifecycle, display bounds, link mode conversion, callback/watchdog outputs, DDC callback failures, adjustment updates, query encryption status, and all status string conversions.
