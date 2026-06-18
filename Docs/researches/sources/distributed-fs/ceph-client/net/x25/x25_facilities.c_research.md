# sources/distributed-fs/ceph-client/net/x25/x25_facilities.c

Purpose: parses, creates, negotiates, and link-limits X.25 facilities, including reverse charging, throughput, packet/window size, and DTE address-extension facilities.

Important APIs/functions: `x25_parse_facilities()`, `x25_create_facilities()`, `x25_negotiate_facilities()`, and `x25_limit_facilities()` are used by call request/accept and connection setup.

Control flow: parsing validates the declared facilities length, walks class A/B/C/D encodings, updates regular and DTE facility structs, and records a VC facility mask. Creation emits a length-prefixed facility block based on a mask and current socket values, including DTE marker/service encodings. Negotiation copies local defaults, parses peer requests, rejects unacceptable reverse charging, negotiates throughput and packet/window values downward, then returns the consumed facility length.

State and persistence: functions mutate caller-provided `x25_facilities`, `x25_dte_facilities`, and VC mask fields. Per-socket accepted values persist in `x25_sock`; no global state is owned.

Dependencies and integration: used by `af_x25.c` for incoming calls, by `x25_in.c` for call accepted frames, and by `x25_subr.c` when generating call packets. It relies on X.25 constants and skb pull validation.

Risks and test signals: malformed length fields and variable class-D encodings are high-risk. Tests should cover empty facilities, all known classes, unknown facility logging, too-short class encodings, DTE AE length limits, reverse charging rejection, extended versus standard window clamping, and generated facility byte-for-byte round trips.
