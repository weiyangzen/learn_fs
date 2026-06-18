# sources/distributed-fs/ceph-client/include/net/gue.h

Purpose: defines Generic UDP Encapsulation header layout and validation helpers for standard and private option flags.

Important APIs/types: `struct guehdr` overlays the first word with version, control bit, header length, protocol/control type, and standard flags. `GUE_FLAG_PRIV` indicates a private flags extension. `GUE_PFLAG_REMCSUM` defines the remote-checksum private option. `guehdr_flags_len()` computes standard option length; `guehdr_priv_flags_len()` currently returns zero for known private flags; `validate_gue_flags()` checks unknown standard/private flags and ensures option lengths fit the header length.

Control flow and state: receive or transmit code reads `hlen`, derives option length, validates supported flags, and then parses optional private flags at the end of the standard option area. No persistent state is stored here.

Dependencies and integration: uses architecture byteorder and Linux types. It integrates with FOU/GUE tunnel headers, GRO remote checksum handling, and UDP tunnel offload.

Risks: bitfield layout is endian-dependent, and `validate_gue_flags()` performs pointer arithmetic into option data, so callers must ensure the base header and option area are present. Tests should include unknown standard/private flags, too-short options, remote checksum flag handling, control-vs-data headers, and both endian configurations where possible.
