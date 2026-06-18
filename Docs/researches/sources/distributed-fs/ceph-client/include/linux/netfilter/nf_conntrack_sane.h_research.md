# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sane.h

Purpose: Defines the SANE scanner protocol helper state for tracking control/data negotiation on TCP port 6566.

Important APIs, types, and functions: Exports `SANE_PORT`, `enum sane_state`, and `struct nf_ct_sane_master` with state and data port fields. Detected source surface: 18 lines; includes none; macros `SANE_PORT`, `_NF_CONNTRACK_SANE_H`; structs `nf_ct_sane_master`; enums `sane_state`; typedefs none; function-like declarations/helpers none.

Control flow: The helper watches the control stream, transitions through normal and start-request states, and records the negotiated data port for expectation creation.

State and persistence behavior: Per-master conntrack state records a compact protocol phase and port. No global state is defined here.

Dependencies and integration points: Consumed by the SANE conntrack helper and expectation code. It relies on the generic conntrack extension layout outside this header.

Risks and test signals: Risks are incomplete TCP stream parsing and accepting bogus data ports. Test normal scan setup, fragmented control commands, and teardown without a data channel.
