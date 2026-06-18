## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/switchdev.h

### Purpose
`switchdev.h` provides a tiny compatibility hook for marking received skbs as hardware-forwarded when qtnfmac is built with switchdev support.

### Important APIs, Types, And Functions
The only helper is `qtnfmac_switch_mark_skb_flooded(struct sk_buff *skb)`. With `CONFIG_NET_SWITCHDEV`, it sets `skb->offload_fwd_mark = 1`; otherwise it compiles to a no-op.

### Control Flow
Callers can unconditionally invoke the helper on frames flooded by hardware switch/bridge logic. The compile-time configuration decides whether the skb mark is actually set.

### State, Persistence, And Dependencies
There is no state. The helper mutates only the skb metadata for the current packet. It depends on `linux/skbuff.h` and, conditionally, kernel switchdev semantics.

### Integration Points
The helper integrates qtnfmac hardware bridge capabilities with the Linux bridge/switchdev path to avoid duplicate forwarding decisions.

### Risks
Incorrect marking could suppress needed software forwarding or cause duplicated traffic if omitted. Builds without switchdev intentionally lose the metadata signal.

### Test Signals
Bridge offload tests should verify the mark on flooded frames with switchdev enabled and no behavioral regression when compiled without `CONFIG_NET_SWITCHDEV`.
