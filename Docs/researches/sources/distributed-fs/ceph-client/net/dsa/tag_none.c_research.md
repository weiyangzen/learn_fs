# sources/distributed-fs/ceph-client/net/dsa/tag_none.c

Purpose: no-op DSA tag driver for switches without hardware tagging support. The file explicitly warns new switch support should prefer tag_8021q where possible.

Important APIs/functions: `dsa_user_notag_xmit()` returns the original skb unchanged. `none_ops` registers `DSA_TAG_PROTO_NONE` with only an xmit callback and no RX parser.

Control flow: TX path passes packets directly to the conduit. RX source demultiplexing cannot be done by this tagger, so deployments rely on switch/hardware limitations that make no tag acceptable.

State and persistence: stateless.

Dependencies and integration: only depends on `tag.h` and the DSA tag driver framework.

Risks and test signals: no-tag mode cannot distinguish source ports in generic switched traffic and is unsuitable for new hardware. Tests should be limited to supported legacy configurations and should verify no unexpected multi-port ambiguity or bridge leakage occurs.
