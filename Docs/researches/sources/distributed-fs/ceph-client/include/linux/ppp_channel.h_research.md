# sources/distributed-fs/ceph-client/include/linux/ppp_channel.h

Purpose: defines the interface between generic PPP code and lower transport channels.

Important APIs and types: `struct ppp_channel_ops` provides `start_xmit`, `ioctl`, and optional forwarding-path fill callbacks. `struct ppp_channel` stores channel private data, ops, MTU, header headroom, opaque generic PPP pointer, speed, and direct-xmit flag. APIs wake PPP output, deliver input packets/errors, register/unregister channels in a network namespace or default namespace, query channel/unit numbers, and get associated device name under RCU.

Control flow: a transport driver initializes `ppp_channel`, registers it with PPP, accepts `start_xmit()` calls for packets/fragments, calls `ppp_input()` for received packets, reports input errors when packet loss may have occurred, wakes output when TX capacity returns, and unregisters only after ensuring no channel callbacks are executing.

State and persistence: runtime state is split between transport-private data, opaque PPP binding, MTU/headroom/speed/direct-xmit metadata, and generic PPP unit associations. No persistence is defined.

Dependencies and integration points: integrates with sk_buffs, net namespaces, poll include dependency, net_device path offload/forwarding, PPP generic core, and RCU for device-name lookup.

Risks and test signals: risks include skb ownership mistakes, unregister races with input/output/ioctl callbacks, wrong MTU/headroom causing corruption, direct-xmit bypass issues, net namespace registration mistakes, and missing RCU when reading device names. Test channel register/unregister, TX backpressure and wakeups, RX packet/error paths, ioctl forwarding, multilink fragmentation, netns teardown, and RCU device-name access.
