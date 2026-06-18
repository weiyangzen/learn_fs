<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h

Purpose: provides netlink attribute IDs and a size helper for RPL source-routing IPv6 tunnel encapsulation.

Important APIs, types, and functions: the anonymous enum exports `RPL_IPTUNNEL_UNSPEC`, `RPL_IPTUNNEL_SRH`, and `RPL_IPTUNNEL_MAX`. `RPL_IPTUNNEL_SRH_SIZE(srh)` computes the byte size of an RPL SRH from `hdrlen`.

Control flow: userspace sends a tunnel attribute carrying an RPL SRH. Kernel tunnel code validates the attribute, uses the size macro to copy or compare the header length, and attaches it to the tunnel encap state.

State and persistence behavior: no state is held here. Tunnel state lives in route/lwtunnel configuration and includes the serialized SRH payload.

Dependencies and integration points: integrates with `rpl.h`, IPv6 lwtunnel netlink parsing, route encap attributes, and iproute2 tunnel configuration.

Risks and edge cases: `hdrlen` must be trusted only after the containing attribute length is checked. A malformed header can make the size macro exceed provided bytes.

Test signals: create RPL tunnel routes with valid and invalid SRH attributes, verify netlink policy rejects short payloads, and check that route dumps preserve the SRH bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpl_iptunnel.h -->
