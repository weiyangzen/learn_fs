# Research: sources/distributed-fs/ceph-client/net/llc/llc_pdu.c

## sources/distributed-fs/ceph-client/net/llc/llc_pdu.c

Purpose: Encapsulates LLC PDU control-field accessors and builders for I, S, and U frame types, including connection-management and station/SAP PDUs.

Important APIs/types/functions: Implements command/response bit setting, poll/final bit set/decode, builders for DISC, I, REJ, RNR, RR, SABME, DM, FRMR, UA, and response variants. It also builds FRMR info by copying rejected control bytes and encoding sequence/invalidity indicators.

Control flow: Builders write the control bytes directly through `llc_pdu_sn_hdr()` or `llc_pdu_un_hdr()`. I/S PDUs encode `N(S)` and `N(R)` shifted into even bits and store P/F in `ctrl_2`. U PDUs encode command/response values and P/F in `ctrl_1`. FRMR appends a `struct llc_frmr_info` payload with `skb_put()`.

State and persistence behavior: No module-level state. All behavior is skb-local, mutating headers and sometimes extending frame length. Correctness relies on callers allocating enough headroom/body for the selected PDU type.

Dependencies and integration points: Called by connection actions, SAP actions, station replies, and output helpers. It depends on layout and bit macros from `llc_pdu.h`; its encodings must match event classifiers in `llc_c_ev.c`, `llc_s_ev.c`, and `llc_input.c`.

Risks and test signals: Bit encoding errors directly break interoperability. The U-PDU P/F setter uses a compound OR expression that deserves regression coverage around clearing and setting the bit. Tests should validate raw header bytes for every builder, FRMR payload length/content, round-trip P/F decode, and sequence number modulo handling around 0/127.
