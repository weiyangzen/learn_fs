# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/pctype.h

Purpose: defines Intel packet classifier type identifiers used for RSS hash enable registers and virtchnl RSS hash configuration.

Important APIs and types: `enum libie_filter_pctype` assigns hardware packet-class values for non-fragmented IPv4/IPv6 UDP/TCP/SCTP/other, TCP SYN without ACK, fragmented IPv4/IPv6, FCoE classes, and L2 payload. Comments document reserved ranges and values unsupported on XL710/X710.

Control flow: drivers use these enum values when programming HENA/register bits or communicating RSS hash capabilities over virtchnl. The numeric values must match hardware/firmware definitions.

State and persistence: no state is kept. The constants configure hardware hashing/classification state elsewhere.

Dependencies and integration points: no external includes beyond the guard. Integrates Intel Ethernet hardware packet classification with driver and virtchnl control paths.

Risks and test signals: risks include changing numeric values, enabling unsupported PCTYPEs on older devices, and mismatching RSS hash fields with classifier type. Test RSS hash enable programming, virtchnl capability exchange, old XL710/X710 device behavior, and packet-flow classification for IPv4, IPv6, FCoE, fragments, and L2 payload.
