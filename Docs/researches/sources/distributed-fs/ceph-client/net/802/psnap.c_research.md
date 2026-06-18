<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/psnap.c -->
# sources/distributed-fs/ceph-client/net/802/psnap.c

This file implements SNAP demultiplexing over LLC. It lets protocols register a five-byte SNAP descriptor and receive matching frames.

State consists of `snap_list`, protected by `snap_lock` and traversed under RCU, plus the LLC SAP handle `snap_sap`. `register_snap_client()` allocates a `struct datalink_proto`, stores the descriptor, receive callback, header length, and request function, then adds it to the list. `unregister_snap_client()` removes it with RCU synchronization. `snap_init()` opens LLC SAP `0xAA`, and `snap_exit()` releases it.

Receive control flow enters `snap_rcv()` from LLC, pulls five descriptor bytes, looks up a client, pulls the SNAP header, resets the transport header, and calls the client's `rcvfunc`; unknown or malformed frames are freed. Transmit flow uses `snap_request()` to push the descriptor and send an LLC UI packet.

There is no persistence beyond module state. Dependencies include LLC SAP APIs, datalink protocol structures, skb bounds checks, RCU lists, and module lifecycle. Risks include duplicate descriptor registration, receive callback ownership of skb, SAP open failure, and concurrent unregister. Tests should register/unregister clients, receive matching/unknown/truncated frames, verify SNAP header insertion on transmit, and exercise module unload with active clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/psnap.c -->
