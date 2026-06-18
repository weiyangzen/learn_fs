# sources/distributed-fs/ceph-client/include/net/dscp.h

Read `sources/distributed-fs/ceph-client/include/net/dscp.h` completely for this pass (76 lines, 3252 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dscp.h_research.md`.

Purpose: centralizes numeric Differentiated Services Code Point constants and pool documentation for IPv4/IPv6 DS field classification.

Important APIs/types/functions: defines standardized DSCP codepoints: class selectors `DSCP_CS0` through `CS7`, `DSCP_DF`, assured forwarding `DSCP_AF11` through `AF43`, expedited forwarding `DSCP_EF`, `DSCP_VOICE_ADMIT`, lower-effort `DSCP_LE`, and `DSCP_MAX` as 64. Comments document Pool 1, Pool 2, and Pool 3 assignment rules.

Control flow: no executable control flow. Classifiers, DCB, qdiscs, tunnels, and packet marking code include these constants to compare or assign the six-bit DSCP portion of a DS field.

State and persistence: no state. Constants are compile-time API.

Dependencies and integration points: self-contained aside from include guards. It integrates with DS field helpers, TC flower/u32/BPF classifiers, DCB DSCP priority mappings, qdisc CE-threshold selectors, and QoS policy code.

Risks: constants are six-bit DSCP values, not full 8-bit DS fields including ECN. Callers must shift/mask correctly when operating on IPv4 TOS or IPv6 traffic class bytes. IANA registry changes may add future constants.

Test signals: compile-time assertions for known values, DSCP-to-DS-field shift/mask tests, DCB DSCP mapping tests, TC/qdisc selector tests, and documentation checks against the IANA/RFC codepoint registry.
