# sources/distributed-fs/ceph-client/net/netfilter/xt_connlabel.c

Purpose: `connlabel` match tests and optionally sets conntrack label bits.

Important APIs/types/functions: `connlabel_mt()`, `connlabel_mt_check()`, `connlabel_mt_destroy()`, `nf_connlabels_get()`, and `nf_conntrack_event_cache()`.

Control flow: check accepts only INVERT and SET options, pins conntrack, and reserves label support for the requested bit. Runtime returns inverted result if conntrack or labels are absent, matches existing bits, or sets a missing bit and emits an event when SET is enabled.

State and persistence: label bits persist in conntrack; namespace label support and conntrack refs persist while rule exists. Dependencies include nf_conntrack_labels, event cache, x_tables, and conntrack. Risks: SET mutates state from a match, missing labels return invert, event only on first set, and unwind on label reservation failure. Test signals: absent/present bit, SET, INVERT, no conntrack, invalid options, and destroy puts.
