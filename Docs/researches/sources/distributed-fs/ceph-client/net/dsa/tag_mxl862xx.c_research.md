# sources/distributed-fs/ceph-client/net/dsa/tag_mxl862xx.c

Purpose: DSA special-tag driver for MaxLinear MxL862xx switches, using an 8-byte `ETH_P_MXLGSW` tag that carries CPU-port and sub-interface information.

Important APIs/functions: `mxl862_tag_xmit()` computes the target sub-interface relative to the CPU port and writes the ingress/egress fields. `mxl862_tag_rcv()` validates the marker, decodes source port from the IGP/EGP field, maps the user device, marks non-link-local forwarded frames, and strips the tag. `mxl862_netdev_ops` registers `DSA_TAG_PROTO_MXL862`.

Control flow: TX obtains `dp` and `cpu_dp`, pushes headroom, inserts an etype header, and fills four 16-bit words. RX performs bounded parsing, rate-limited diagnostics, DSA user lookup, optional offload mark, then removes the header.

State and persistence: no private state.

Dependencies and integration: uses DSA port relationships, `dsa_strip_etype_header()`, link-local detection, and bitfield helpers. Integrates with hardware bridge offload via `dsa_default_offload_fwd_mark()`.

Risks and test signals: the sub-interface calculation depends on CPU port numbering and should be tested on non-default CPU ports. RX should be tested for invalid markers, unknown ports, link-local frames, and normal bridge-forwarded data.
