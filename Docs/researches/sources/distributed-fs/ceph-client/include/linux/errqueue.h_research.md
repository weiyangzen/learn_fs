# sources/distributed-fs/ceph-client/include/linux/errqueue.h

Purpose: socket error-queue control block overlay for extended asynchronous errors.

Important APIs/types/functions: `SKB_EXT_ERR(skb)` and `struct sock_exterr_skb`, containing `sock_extended_err`, optional IPv6 address, original payload offset, and port.

Control flow: networking code records ICMP/PMTU/timestamping or protocol errors in skb control buffer; socket error queue consumers cast through `SKB_EXT_ERR()` to read metadata.

State/persistence: transient skb control block state until delivered/read from the socket error queue.

Dependencies/integration: `uapi/linux/errqueue.h`, skb `cb`, IPv6 config, socket error queues, ICMP/IPV6 and timestamping paths.

Risks/test signals: risks are skb control-buffer layout conflicts, missing IPv6 address field under config changes, stale origin/port values, and overrun of `skb->cb`. Test `IP_RECVERR`, IPv6 receive errors, PMTU discovery, timestamping error queue delivery, and cb-size assertions.
