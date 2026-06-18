<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/stp.c -->
# sources/distributed-fs/ceph-client/net/802/stp.c

This file is the LLC SAP demultiplexer for STP and GARP-family protocols. It registers one LLC SAP for bridge spanning-tree traffic and dispatches either to the generic STP protocol or to GARP protocol slots based on the destination multicast address.

State includes RCU pointers for `stp_proto` and `garp_protos[]`, the shared LLC `sap`, a registration count, and a mutex for registration lifecycle. `stp_proto_register()` opens the LLC SAP on first user and installs the protocol pointer either as the zero-group STP handler or into the GARP address-indexed table. `stp_proto_unregister()` clears the pointer, waits for RCU readers, and releases the SAP when the last user leaves.

Receive control flow in `stp_pdu_rcv()` validates LLC SSAP/DSAP/control fields, selects GARP slots for destination addresses `01:80:c2:00:00:20` through `2f`, verifies exact group address if a GARP proto is found, and calls `proto->rcv()`. Invalid or unregistered frames are freed.

Dependencies are LLC PDU helpers, Ethernet headers, RCU, and `struct stp_proto` provided by STP/GARP users. Risks include out-of-range group-address indexing if callers register malformed GARP addresses, SAP registration reference imbalance, and packet drops from strict LLC validation. Tests should cover STP and GARP registration/unregistration, multicast dispatch, malformed LLC fields, exact-address mismatch, and concurrent receive during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/stp.c -->
