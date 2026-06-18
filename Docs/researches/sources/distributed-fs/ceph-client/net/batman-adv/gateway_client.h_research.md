<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h research

Purpose: declares gateway client APIs for gateway election, gateway node lifecycle, DHCP parsing, netlink dumping, and out-of-range checks.

Important APIs and types: prototypes cover client stop/reselect/election, selected originator and gateway retrieval, node update/delete/free/release/get, `batadv_gw_dump()`, `batadv_gw_out_of_range()`, and `batadv_gw_dhcp_recipient_get()`. The inline `batadv_gw_node_put()` decrements a gateway node kref using `batadv_gw_node_release()`.

Control flow and state behavior: the header does not store state but defines reference ownership: any returned `batadv_gw_node` or selected originator must be released by the caller. The DHCP parser communicates both classification and, for server-to-client DHCP, the client hardware address.

Dependencies and integration: includes `main.h`, kref, netlink, skbuff, batman packet UAPI. It is used by TVLV code, routing paths, hard-interface teardown, and netlink command handlers.

Risks: mismatched get/put calls leak or prematurely free gateway nodes. Callers must invoke election only when routing algorithm gateway hooks are valid and must not assume DHCP parser leaves `header_len` unchanged.

Test signals: compile all gateway users, reference leak checks around selected gateway get/put, DHCP parser callers with malformed skbs, and gateway node removal while current gateway is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.h -->
